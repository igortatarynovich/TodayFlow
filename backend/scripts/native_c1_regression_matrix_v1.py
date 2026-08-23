"""Native C1 editorial gate calibration regression matrix (ops / 1.3.117).

Runs force day_story rebuild for fixed user/date cases and prints outcome rollup.
Does not weaken gates — measures whether c5.1 + retry feedback yields PASS on prod inputs.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from time import perf_counter
from typing import Any

from todayflow_backend.db import models
from todayflow_backend.db.session import SessionLocal
from todayflow_backend.services.core_profile import get_core_profile_service
from todayflow_backend.services.day_lifecycle_jobs_c5 import (
    _build_prewarm_celestial,
    _fusion_dump_for_user,
    _minimal_morning,
)
from todayflow_backend.services.day_story_refresh_v1 import refresh_day_story_for_user
from todayflow_backend.services.day_story_wire_v1 import build_day_story_record_for_refresh

DEFAULT_CASES: list[dict[str, Any]] = [
    {"user_id": 26, "label": "prior_astro_jargon_gate"},
    {"user_id": 2, "label": "prior_force_ok"},
    {"user_id": 5, "label": "prior_scene_everyday_gate"},
    {"user_id": 11, "label": "p0_today_account"},
    {"user_id": 6, "label": "p0_v2_account"},
]

TZ = "Europe/Berlin"
LOCALE = "ru"


def _summarize_result(
    db: Any,
    result: dict[str, Any],
    elapsed_ms: int,
    label: str,
) -> dict[str, Any]:
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
    native_meta = payload.get("native_llm_c1_meta") or {}
    i0 = editorial.get("i0_split") or native_meta.get("i0_split") or {}
    pers_pack = payload.get("personalization_pack") or {}
    story_text = str(story.get("story") or "").strip()
    interp = story.get("interpretation_status") or scen.get("interpretation_status")
    return {
        "label": label,
        "rebuilt": result.get("rebuilt"),
        "story_status": result.get("story_status"),
        "interpretation_status": interp,
        "has_story_text": bool(story_text),
        "story_chars": len(story_text),
        "gen_id": gen_id,
        "elapsed_ms": elapsed_ms,
        "used_fallback": getattr(log, "used_fallback", None),
        "generation_source": payload.get("generation_source"),
        "failure_class": native_meta.get("failure_class"),
        "reject_reason": (native_meta.get("reject_reason") or log.error_message or "")[:200],
        "prompt_version": editorial.get("prompt_version") or payload.get("prompt_version"),
        "evidence_depth": pers_pack.get("evidence_depth"),
        "i0_split": bool(i0.get("i0_split")),
        "personal_degraded": i0.get("personal_degraded"),
        "attempt_stages": [
            a.get("stage") for a in (native_meta.get("attempts") or []) if isinstance(a, dict)
        ],
        "scenes": len(scen.get("scenes") or []) if isinstance(scen, dict) else None,
    }


def run_case(
    db: Any,
    user_id: int,
    local_date: date,
    label: str,
) -> dict[str, Any]:
    user = db.get(models.User, user_id)
    if user is None:
        return {"label": label, "user_id": user_id, "error": "user_missing"}
    t0 = perf_counter()
    print(f"--- matrix case label={label} user={user_id} date={local_date} ---", flush=True)
    celestial = _build_prewarm_celestial(local_date, LOCALE)
    morning = _minimal_morning(local_date, celestial_events=celestial)
    core_profile = get_core_profile_service().build_cached_or_baseline(db, user)
    fusion_dump = _fusion_dump_for_user(db, user=user, local_date=local_date)

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
        local_date=local_date,
        timezone_name=TZ,
        locale=LOCALE,
        build_fn=_build,
        force=True,
    )
    elapsed = int((perf_counter() - t0) * 1000)
    summary = _summarize_result(db, result, elapsed, label)
    summary["user_id"] = user_id
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Native C1 regression matrix (force rebuild)")
    parser.add_argument("--date", default="2026-08-23", help="Local date YYYY-MM-DD")
    parser.add_argument("--user-id", type=int, default=0, help="Single user only (0 = all cases)")
    parser.add_argument("--label", default="", help="Override label when --user-id set")
    args = parser.parse_args()
    local_date = date.fromisoformat(args.date)
    db = SessionLocal()
    summaries: list[dict[str, Any]] = []
    try:
        if args.user_id:
            summaries.append(
                run_case(
                    db,
                    args.user_id,
                    local_date,
                    args.label or f"user_{args.user_id}",
                )
            )
        else:
            for case in DEFAULT_CASES:
                summaries.append(
                    run_case(
                        db,
                        int(case["user_id"]),
                        local_date,
                        str(case["label"]),
                    )
                )
        ok = sum(
            1
            for s in summaries
            if s.get("interpretation_status") == "ok"
            and s.get("has_story_text")
            and not s.get("used_fallback")
        )
        print(
            json.dumps(
                {
                    "matrix_date": local_date.isoformat(),
                    "cases": len(summaries),
                    "pass_count": ok,
                    "summaries": summaries,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
