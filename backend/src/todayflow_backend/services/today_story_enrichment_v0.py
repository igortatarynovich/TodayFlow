"""Background day_story enrichment — never blocks GET /today/contract."""

from __future__ import annotations

import logging
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.core.llm_openai_compatible import llm_operation
from todayflow_backend.services.generation_jobs_v0 import (
    claim_job,
    complete_job_if_fresh,
    enqueue_or_reuse,
    get_job,
    mark_job_failed,
    run_with_db,
    schedule_job_runner,
)

logger = logging.getLogger("todayflow.today.enrichment")


def run_today_story_enrichment_job(job_id: int) -> None:
    def _run(db: Session) -> None:
        job = claim_job(db, job_id)
        if job is None:
            return
        payload = job.request_payload if isinstance(job.request_payload, dict) else {}
        fingerprint = job.fingerprint
        try:
            from todayflow_backend.db import models as db_models
            from todayflow_backend.services.core_profile import get_core_profile_service
            from todayflow_backend.services.day_story_v1 import day_story_to_today_contract_v1
            from todayflow_backend.services.day_story_wire_v1 import _build_day_story_record

            user_id = int(payload.get("user_id") or job.user_id or 0)
            user = db.query(db_models.User).filter(db_models.User.id == user_id).first()
            if user is None:
                mark_job_failed(db, job, "user_missing")
                return

            target = date.fromisoformat(str(payload["local_date"]))
            locale = str(payload.get("locale") or "ru")
            timezone_name = str(payload.get("timezone") or "UTC")
            fusion_dump = payload.get("fusion_dump") if isinstance(payload.get("fusion_dump"), dict) else {}
            ritual_norm = payload.get("ritual_norm") if isinstance(payload.get("ritual_norm"), dict) else {}
            color = str(payload.get("color") or "")
            stone = str(payload.get("stone") or "")
            core_profile = get_core_profile_service().build_cached_or_baseline(db, user)

            with llm_operation("background"):
                story, gen_id, used_fallback = _build_day_story_record(
                    db,
                    user=user,
                    target_date=target,
                    locale=locale,
                    fusion_dump=fusion_dump,
                    core_profile=core_profile,
                    ritual_norm=ritual_norm,
                    color=color,
                    stone=stone,
                    force_rebuild=True,
                    expected_fingerprint=fingerprint,
                    timezone_name=timezone_name,
                )

            fresh = get_job(db, job_id)
            if fresh is None or fresh.fingerprint != fingerprint:
                if fresh is not None:
                    fresh.status = "stale"
                    db.add(fresh)
                    db.commit()
                return

            if used_fallback or not isinstance(story, dict):
                mark_job_failed(db, job, "day_story_llm_fallback")
                return

            contract = day_story_to_today_contract_v1(
                story,
                generation_id=str(gen_id or ""),
                progress={
                    "story_status": "enriched",
                    "story_refresh_required": False,
                    "story_fingerprint": fingerprint,
                    "generation_lifecycle": {
                        "status": "enriched",
                        "job_id": job_id,
                        "fingerprint": fingerprint,
                        "source": "llm",
                        "is_fully_personal": True,
                    },
                },
            )
            complete_job_if_fresh(
                db,
                job,
                expected_fingerprint=fingerprint,
                result_payload={
                    "contract": contract,
                    "generation_log_id": gen_id,
                    "generation_source": "llm",
                    "day_story": story,
                },
                generation_log_id=int(gen_id) if gen_id else None,
            )
        except Exception as exc:
            logger.exception("today_story_enrichment_failed job_id=%s", job_id)
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


def enqueue_today_story_enrichment(
    db: Session,
    *,
    user_id: int,
    local_date: date,
    fingerprint: str,
    locale: str,
    timezone_name: str,
    ritual_norm: dict[str, Any] | None,
    fusion_dump: dict[str, Any] | None,
    color: str = "",
    stone: str = "",
) -> Any:
    idem = f"today_story:{user_id}:{local_date.isoformat()}:{fingerprint}"
    job, created = enqueue_or_reuse(
        db,
        idempotency_key=idem,
        fingerprint=fingerprint,
        module="today",
        surface="day_story",
        user_id=user_id,
        request_payload={
            "user_id": user_id,
            "local_date": local_date.isoformat(),
            "locale": locale,
            "timezone": timezone_name,
            "ritual_norm": ritual_norm or {},
            "fusion_dump": fusion_dump or {},
            "color": color,
            "stone": stone,
        },
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
        schedule_job_runner(job.id, run_today_story_enrichment_job)
    return job
