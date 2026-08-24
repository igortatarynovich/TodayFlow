"""List cached native C1 unavailable shells (ops / 1.3.118).

GET /today/contract does not rebuild these (allow_rebuild_on_miss=False).
Recovery: POST /today/story/refresh force=true, or regression matrix / prewarm.
Never invent story text on GET.
"""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta

from todayflow_backend.db import models
from todayflow_backend.db.session import SessionLocal


def main() -> None:
    parser = argparse.ArgumentParser(description="List unavailable_after_llm day_story shells")
    parser.add_argument("--days", type=int, default=2, help="Look back N days of generation_logs")
    parser.add_argument("--limit", type=int, default=80)
    args = parser.parse_args()

    since = datetime.utcnow() - timedelta(days=max(1, args.days))
    db = SessionLocal()
    try:
        rows = (
            db.query(models.GenerationLog)
            .filter(
                models.GenerationLog.module == "day_story_v1",
                models.GenerationLog.created_at >= since,
            )
            .order_by(models.GenerationLog.id.desc())
            .limit(args.limit)
            .all()
        )
        latest_by_user: dict[int, models.GenerationLog] = {}
        for log in rows:
            uid = int(log.user_id or 0)
            if uid and uid not in latest_by_user:
                latest_by_user[uid] = log

        print(f"since={since.isoformat()} scanned={len(rows)} latest_users={len(latest_by_user)}")
        print("GET /today/contract will keep serving these until POST /today/story/refresh force=true")
        for uid, log in sorted(latest_by_user.items()):
            inp = log.input_payload if isinstance(log.input_payload, dict) else {}
            src = str(inp.get("generation_source") or "")
            interp = ""
            story = inp.get("contract") if isinstance(inp.get("contract"), dict) else {}
            if isinstance(story, dict):
                interp = str(story.get("interpretation_status") or "")
            unavailable = src == "unavailable_after_llm" or interp == "unavailable" or bool(log.used_fallback)
            if not unavailable:
                continue
            meta = inp.get("native_llm_c1_meta") if isinstance(inp.get("native_llm_c1_meta"), dict) else {}
            print(
                json.dumps(
                    {
                        "user_id": uid,
                        "gen_id": log.id,
                        "date": (log.created_at.date().isoformat() if log.created_at else None),
                        "generation_source": src,
                        "prompt_version": inp.get("prompt_version"),
                        "reject_reason": str(meta.get("reject_reason") or log.error_message or "")[:160],
                    },
                    ensure_ascii=False,
                )
            )
    finally:
        db.close()


if __name__ == "__main__":
    main()
