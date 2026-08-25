"""Roll up native C1 editorial gate rejects from generation_logs (ops / calibration)."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timedelta

from todayflow_backend.db.session import SessionLocal
from todayflow_backend.db import models


def _meta_from_log(log: models.GenerationLog) -> dict:
    inp = log.input_payload if isinstance(log.input_payload, dict) else {}
    for key in ("native_llm_c1_meta", "editorial_meta"):
        raw = inp.get(key)
        if isinstance(raw, dict):
            return raw
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect native C1 gate reject reasons")
    parser.add_argument("--days", type=int, default=7, help="Look back N days")
    parser.add_argument("--limit", type=int, default=200, help="Max logs to scan")
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
        code_counts: Counter[str] = Counter()
        failure_counts: Counter[str] = Counter()
        samples: list[dict] = []

        for log in rows:
            meta = _meta_from_log(log)
            if not meta and not log.error_message:
                continue
            fc = str(meta.get("failure_class") or log.status or "")
            rr = str(meta.get("reject_reason") or log.error_message or "")
            if fc:
                failure_counts[fc] += 1
            for part in rr.replace("gate | ", "").split(";"):
                code = part.strip()
                if code and code.isascii() and "_" in code:
                    code_counts[code] += 1
            if meta.get("success") is False or log.used_fallback:
                attempts = meta.get("attempts") or []
                samples.append(
                    {
                        "id": log.id,
                        "user_id": log.user_id,
                        "status": log.status,
                        "failure_class": fc,
                        "reject_reason": rr[:240],
                        "attempt_stages": [a.get("stage") for a in attempts if isinstance(a, dict)],
                    }
                )

        print(f"since={since.isoformat()} scanned={len(rows)}")
        print("failure_class:", dict(failure_counts.most_common()))
        print("gate_codes:", dict(code_counts.most_common(12)))
        print("recent_samples:")
        for s in samples[:15]:
            print(json.dumps(s, ensure_ascii=False))
    finally:
        db.close()


if __name__ == "__main__":
    main()
