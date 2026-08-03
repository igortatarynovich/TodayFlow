"""Day Lifecycle C5 — background prewarm job (no LLM on GET).

Enqueued when GET /today/contract returns assembling, or by cron catch-up.
Uses generation_jobs_v0 daemon threads; request path only schedules.

Concurrency: at most MAX_CONCURRENT_PREWARMS LLM assemblies hold a DB session.
"""

from __future__ import annotations

import logging
import threading
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.services.generation_jobs_v0 import (
    claim_job,
    complete_job_if_fresh,
    enqueue_or_reuse,
    get_job,
    make_fingerprint,
    mark_job_failed,
    run_with_db,
    schedule_job_runner,
)

logger = logging.getLogger("todayflow.day_prewarm")

# Cap concurrent LLM+DB prewarms so QueuePool is not exhausted.
MAX_CONCURRENT_PREWARMS = 2
_PREWARM_SEM = threading.Semaphore(MAX_CONCURRENT_PREWARMS)


def run_day_prewarm_job(job_id: int) -> None:
    acquired = _PREWARM_SEM.acquire(timeout=120)
    if not acquired:
        logger.warning("day_prewarm semaphore timeout job_id=%s — leaving pending", job_id)

        def _release_claim(db: Session) -> None:
            job = get_job(db, job_id)
            if job is None:
                return
            if job.status == "enrichment_pending" and job.locked_at is not None:
                job.locked_at = None
                job.attempt_count = max(0, int(job.attempt_count or 1) - 1)
                db.add(job)
                db.commit()

        run_with_db(_release_claim)
        return

    try:

        def _run(db: Session) -> None:
            job = claim_job(db, job_id)
            if job is None:
                return
            payload = job.request_payload if isinstance(job.request_payload, dict) else {}
            fingerprint = job.fingerprint
            try:
                from todayflow_backend.db import models as db_models
                from todayflow_backend.services.day_lifecycle_jobs_c5 import prewarm_assemble_user_day

                user_id = int(payload.get("user_id") or job.user_id or 0)
                user = db.query(db_models.User).filter(db_models.User.id == user_id).first()
                if user is None:
                    mark_job_failed(db, job, "user_missing")
                    return

                local_date = date.fromisoformat(str(payload["local_date"]))
                locale = str(payload.get("locale") or "ru")
                timezone_name = str(payload.get("timezone") or "UTC")

                outcome = prewarm_assemble_user_day(
                    db,
                    user=user,
                    local_date=local_date,
                    timezone_name=timezone_name,
                    locale=locale,
                )

                fresh = get_job(db, job_id)
                if fresh is None or fresh.fingerprint != fingerprint:
                    if fresh is not None:
                        fresh.status = "stale"
                        db.add(fresh)
                        db.commit()
                    return

                if outcome == "error":
                    mark_job_failed(db, job, "prewarm_error")
                    return

                complete_job_if_fresh(
                    db,
                    job,
                    expected_fingerprint=fingerprint,
                    result_payload={
                        "outcome": outcome,
                        "local_date": local_date.isoformat(),
                        "user_id": user_id,
                    },
                )
            except Exception as exc:
                logger.exception("day_prewarm_failed job_id=%s", job_id)
                job2 = get_job(db, job_id)
                if job2 is not None:
                    if job2.attempt_count >= job2.max_attempts:
                        mark_job_failed(db, job2, str(exc)[:500])
                    else:
                        job2.status = "enrichment_pending"
                        job2.locked_at = None
                        job2.error_message = str(exc)[:500]
                        db.add(job2)
                        db.commit()

        run_with_db(_run)
    finally:
        _PREWARM_SEM.release()


def enqueue_day_prewarm(
    db: Session,
    *,
    user_id: int,
    local_date: date,
    locale: str = "ru",
    timezone_name: str = "UTC",
) -> Any:
    """Idempotent background assemble for one user/day. Safe to call from GET."""
    day_iso = local_date.isoformat()
    idem = f"day_prewarm:{int(user_id)}:{day_iso}"
    fingerprint = make_fingerprint("day_prewarm_c5", user_id, day_iso)
    job, created = enqueue_or_reuse(
        db,
        idempotency_key=idem,
        fingerprint=fingerprint,
        module="day_lifecycle",
        surface="prewarm",
        user_id=int(user_id),
        request_payload={
            "user_id": int(user_id),
            "local_date": day_iso,
            "locale": locale,
            "timezone": timezone_name,
        },
        max_attempts=2,
    )
    if job.status != "enriched" and (
        created or job.status in ("enrichment_pending", "enrichment_failed")
    ):
        if job.status == "enrichment_failed":
            job.status = "enrichment_pending"
            job.error_message = None
            job.locked_at = None
            db.add(job)
            db.commit()
            db.refresh(job)
        schedule_job_runner(job.id, run_day_prewarm_job)
    return job
