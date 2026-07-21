"""C1 — Non-blocking generation jobs: baseline first, enrichment async.

Status canon (product):
  baseline_ready | enrichment_pending | enriched | enrichment_failed | stale

Rules:
- Read endpoints never wait on Nebius.
- Max one active job per idempotency_key.
- Stale fingerprint writes are discarded.
- SDK retries stay off; job-level attempts are limited (max_attempts).
"""

from __future__ import annotations

import hashlib
import logging
import threading
from datetime import timedelta
from typing import Any, Callable, Literal, Optional

from sqlalchemy.orm import Session

from todayflow_backend.db.models import GenerationJob, utc_naive_now
from todayflow_backend.db.session import SessionLocal

logger = logging.getLogger("todayflow.generation_jobs")

GenerationStatus = Literal[
    "baseline_ready",
    "enrichment_pending",
    "enriched",
    "enrichment_failed",
    "stale",
]

JOB_CONTRACT = "generation_jobs_v0"
DEFAULT_MAX_ATTEMPTS = 2
DEFAULT_TTL_HOURS = 24
LOCK_STALE_SECONDS = 180

# In-process dedupe of runners (multi-worker needs DB lock only).
_runners_lock = threading.Lock()
_active_runners: set[int] = set()


def lifecycle_payload(
    *,
    status: GenerationStatus,
    job_id: int | None = None,
    fingerprint: str | None = None,
    source: str = "template",
    is_fully_personal: bool = False,
    error: str | None = None,
) -> dict[str, Any]:
    return {
        "contract_version": JOB_CONTRACT,
        "status": status,
        "job_id": job_id,
        "fingerprint": fingerprint,
        "source": source,
        # Baseline must not be marketed as a full personal LLM reading.
        "is_fully_personal": bool(is_fully_personal),
        "error": error,
    }


def make_fingerprint(*parts: Any) -> str:
    raw = "|".join("" if p is None else str(p) for p in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def get_job(db: Session, job_id: int) -> GenerationJob | None:
    return db.query(GenerationJob).filter(GenerationJob.id == job_id).first()


def get_job_by_key(db: Session, idempotency_key: str) -> GenerationJob | None:
    return (
        db.query(GenerationJob)
        .filter(GenerationJob.idempotency_key == idempotency_key)
        .first()
    )


def enqueue_or_reuse(
    db: Session,
    *,
    idempotency_key: str,
    fingerprint: str,
    module: str,
    surface: str,
    user_id: int | None,
    request_payload: dict[str, Any] | None,
    baseline_payload: dict[str, Any] | None = None,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
) -> tuple[GenerationJob, bool]:
    """Return (job, created). Reuses enriched/pending jobs with same key+fingerprint."""
    existing = get_job_by_key(db, idempotency_key)
    now = utc_naive_now()

    if existing is not None:
        if existing.fingerprint == fingerprint and existing.status == "enriched" and existing.result_payload:
            return existing, False
        if existing.fingerprint == fingerprint and existing.status == "enrichment_pending":
            # Re-kick if lock looks abandoned.
            if existing.locked_at and (now - existing.locked_at).total_seconds() > LOCK_STALE_SECONDS:
                existing.locked_at = None
                existing.updated_at = now
                db.add(existing)
                db.commit()
                db.refresh(existing)
            return existing, False
        if existing.fingerprint == fingerprint and existing.status == "enrichment_failed":
            return existing, False
        # Fingerprint changed → reset the same idempotency row for the new generation.
        if existing.fingerprint != fingerprint:
            existing.fingerprint = fingerprint
            existing.status = "enrichment_pending"
            existing.attempt_count = 0
            existing.result_payload = None
            existing.error_message = None
            existing.request_payload = request_payload
            existing.baseline_payload = baseline_payload
            existing.locked_at = None
            existing.started_at = None
            existing.finished_at = None
            existing.expires_at = now + timedelta(hours=DEFAULT_TTL_HOURS)
            existing.updated_at = now
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing, True

    job = GenerationJob(
        idempotency_key=idempotency_key,
        fingerprint=fingerprint,
        module=module,
        surface=surface,
        user_id=user_id,
        status="enrichment_pending",
        attempt_count=0,
        max_attempts=max(1, int(max_attempts)),
        request_payload=request_payload,
        baseline_payload=baseline_payload,
        expires_at=now + timedelta(hours=DEFAULT_TTL_HOURS),
    )
    try:
        db.add(job)
        db.commit()
        db.refresh(job)
        return job, True
    except Exception:
        db.rollback()
        # Race on unique idempotency_key
        again = get_job_by_key(db, idempotency_key)
        if again is not None:
            return again, False
        raise


def mark_job_failed(db: Session, job: GenerationJob, error: str) -> GenerationJob:
    job.status = "enrichment_failed"
    job.error_message = (error or "enrichment_failed")[:2000]
    job.finished_at = utc_naive_now()
    job.locked_at = None
    job.updated_at = utc_naive_now()
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def complete_job_if_fresh(
    db: Session,
    job: GenerationJob,
    *,
    expected_fingerprint: str,
    result_payload: dict[str, Any],
    generation_log_id: int | None = None,
) -> GenerationJob:
    """Atomic complete with stale-write protection."""
    db.refresh(job)
    if job.fingerprint != expected_fingerprint:
        job.status = "stale"
        job.error_message = "fingerprint_mismatch_on_complete"
        job.finished_at = utc_naive_now()
        job.locked_at = None
        job.updated_at = utc_naive_now()
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    job.status = "enriched"
    job.result_payload = result_payload
    job.generation_log_id = generation_log_id
    job.error_message = None
    job.finished_at = utc_naive_now()
    job.locked_at = None
    job.updated_at = utc_naive_now()
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def claim_job(db: Session, job_id: int) -> GenerationJob | None:
    job = get_job(db, job_id)
    if job is None:
        return None
    if job.status not in ("enrichment_pending", "enrichment_failed"):
        return None
    if job.attempt_count >= job.max_attempts and job.status == "enrichment_failed":
        return None
    now = utc_naive_now()
    if job.locked_at and (now - job.locked_at).total_seconds() < LOCK_STALE_SECONDS:
        return None
    job.locked_at = now
    job.started_at = job.started_at or now
    job.attempt_count = int(job.attempt_count or 0) + 1
    job.status = "enrichment_pending"
    job.updated_at = now
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def schedule_job_runner(job_id: int, runner: Callable[[int], None]) -> None:
    """Fire-and-forget daemon thread; never blocks the request path."""
    with _runners_lock:
        if job_id in _active_runners:
            return
        _active_runners.add(job_id)

    def _wrap() -> None:
        try:
            runner(job_id)
        except Exception:
            logger.exception("generation_job_runner_crashed job_id=%s", job_id)
        finally:
            with _runners_lock:
                _active_runners.discard(job_id)

    t = threading.Thread(target=_wrap, name=f"gen-job-{job_id}", daemon=True)
    t.start()


def job_to_public(job: GenerationJob) -> dict[str, Any]:
    status: GenerationStatus
    if job.status in (
        "baseline_ready",
        "enrichment_pending",
        "enriched",
        "enrichment_failed",
        "stale",
    ):
        status = job.status  # type: ignore[assignment]
    else:
        status = "enrichment_pending"

    source = "llm" if status == "enriched" else "template"
    return {
        **lifecycle_payload(
            status=status,
            job_id=job.id,
            fingerprint=job.fingerprint,
            source=source,
            is_fully_personal=status == "enriched",
            error=job.error_message if status == "enrichment_failed" else None,
        ),
        "module": job.module,
        "surface": job.surface,
        "attempt_count": job.attempt_count,
        "max_attempts": job.max_attempts,
        "result": job.result_payload if status == "enriched" else None,
        "baseline": job.baseline_payload,
    }


def run_with_db(fn: Callable[[Session], Any]) -> Any:
    db = SessionLocal()
    try:
        return fn(db)
    finally:
        db.close()
