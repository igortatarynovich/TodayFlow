"""Force-rebuild day_story for primary accounts (force=True → native LLM attempt)."""
from __future__ import annotations

from datetime import date
from time import perf_counter

from todayflow_backend.db.session import SessionLocal
from todayflow_backend.db import models
from todayflow_backend.services.core_profile import get_core_profile_service
from todayflow_backend.services.day_lifecycle_jobs_c5 import (
    _build_prewarm_celestial,
    _fusion_dump_for_user,
    _minimal_morning,
)
from todayflow_backend.services.day_story_refresh_v1 import refresh_day_story_for_user
from todayflow_backend.services.day_story_wire_v1 import build_day_story_record_for_refresh

USER_IDS = [1, 2]
LOCAL_DATE = date(2026, 8, 4)
TZ = "Europe/Berlin"
LOCALE = "ru"


def main() -> None:
    db = SessionLocal()
    try:
        for uid in USER_IDS:
            user = db.get(models.User, uid)
            if user is None:
                print(f"user {uid}: MISSING", flush=True)
                continue
            t0 = perf_counter()
            print(f"--- rebuild user={uid} email={user.email} date={LOCAL_DATE} ---", flush=True)
            celestial = _build_prewarm_celestial(LOCAL_DATE, LOCALE)
            morning = _minimal_morning(LOCAL_DATE, celestial_events=celestial)
            core_profile = get_core_profile_service().build_cached_or_baseline(db, user)
            fusion_dump = _fusion_dump_for_user(db, user=user, local_date=LOCAL_DATE)

            def _build(db_sess, **kwargs):
                return build_day_story_record_for_refresh(
                    db_sess,
                    user=kwargs["user"],
                    target_date=kwargs["target_date"],
                    locale=kwargs["locale"],
                    morning=morning,
                    fusion_dump=fusion_dump,
                    core_profile=core_profile if isinstance(core_profile, dict) else {},
                    force_rebuild=True,
                    expected_fingerprint=kwargs.get("expected_fingerprint"),
                    fingerprint_payload=kwargs.get("fingerprint_payload"),
                    timezone_name=TZ,
                )

            result = refresh_day_story_for_user(
                db,
                user=user,
                local_date=LOCAL_DATE,
                timezone_name=TZ,
                locale=LOCALE,
                build_fn=_build,
                force=True,
            )
            elapsed = int((perf_counter() - t0) * 1000)
            story = result.get("story") or {}
            scen = (story.get("day_scenario") or {}) if isinstance(story, dict) else {}
            editorial = (scen.get("editorial_meta") or {}) if isinstance(scen, dict) else {}
            gen_id = result.get("generation_id")
            log = None
            try:
                log = db.get(models.GenerationLog, int(gen_id)) if gen_id else None
            except Exception:
                log = None
            payload = (log.input_payload or {}) if log else {}
            print(
                {
                    "rebuilt": result.get("rebuilt"),
                    "status": result.get("story_status"),
                    "gen_id": gen_id,
                    "elapsed_ms": elapsed,
                    "used_fallback": getattr(log, "used_fallback", None),
                    "generation_source": payload.get("generation_source"),
                    "failure_class": (payload.get("native_llm_c1_meta") or {}).get("failure_class"),
                    "model": getattr(log, "model", None),
                    "prompt_version": editorial.get("prompt_version") or payload.get("prompt_version"),
                    "scenes": len(scen.get("scenes") or []) if isinstance(scen, dict) else None,
                },
                flush=True,
            )
    finally:
        db.close()
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
