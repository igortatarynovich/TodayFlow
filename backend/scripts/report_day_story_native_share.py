#!/usr/bin/env python3
"""Product metric: day_story native LLM success share (ongoing, not one-off).

Reports generation_source / used_fallback / failure_class for module=day_story_v1.

``failure_class`` buckets include coarse families (timeout, empty, parse, other)
and gate primary rules as ``gate:<rule>`` (e.g. gate:day_card_missing_conflict_link)
so taxonomy (a) can separate provider timeout from schema/quality rejects.

Usage:
  DATABASE_URL=postgresql+psycopg://... PYTHONPATH=backend/src \\
    backend/.venv/bin/python backend/scripts/report_day_story_native_share.py --days 7

  ... report_day_story_native_share.py --days 3 --json

Alert heuristic (ops): among rows with llm_attempted=true, native success share
below --alert-below (default 0.30) exits 2.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, text

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _payload(row: Any) -> dict[str, Any]:
    raw = row.get("input_payload") if hasattr(row, "get") else row[0] if False else None
    return raw if isinstance(raw, dict) else {}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--json", action="store_true")
    ap.add_argument(
        "--alert-below",
        type=float,
        default=0.30,
        help="Exit 2 if native share among llm_attempted rows is below this",
    )
    ap.add_argument("--no-alert", action="store_true")
    args = ap.parse_args()

    url = os.environ.get("DATABASE_URL") or os.environ.get("SQLALCHEMY_DATABASE_URI")
    if not url:
        print("DATABASE_URL required", file=sys.stderr)
        return 1

    since = datetime.now(timezone.utc) - timedelta(days=max(1, args.days))
    engine = create_engine(url)
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT created_at, used_fallback, status, model, error_message, duration_ms,
                       input_payload
                FROM generation_logs
                WHERE module = 'day_story_v1'
                  AND created_at >= :since
                ORDER BY created_at DESC
                """
            ),
            {"since": since},
        ).mappings().all()

    source_c: Counter[str] = Counter()
    failure_c: Counter[str] = Counter()
    llm_attempted_n = 0
    native_ok_n = 0
    fallback_n = 0

    for r in rows:
        payload = r["input_payload"] if isinstance(r["input_payload"], dict) else {}
        src = payload.get("generation_source")
        if not src:
            # Pre-instrumentation rows: infer.
            if payload.get("native_scenario_c1") is True:
                src = "native_llm_c1"
            elif r["used_fallback"]:
                src = "legacy_fallback_unknown"
            else:
                src = "legacy_success_unknown"
        source_c[str(src)] += 1
        if r["used_fallback"]:
            fallback_n += 1

        meta = payload.get("native_llm_c1_meta") if isinstance(payload.get("native_llm_c1_meta"), dict) else {}
        attempted = payload.get("llm_attempted")
        if attempted is None:
            attempted = bool(meta) or src in {
                "native_llm_c1",
                "deterministic_fallback_after_llm",
            }
        if attempted:
            llm_attempted_n += 1
            if src == "native_llm_c1" or payload.get("native_scenario_c1") is True:
                native_ok_n += 1
            fc = meta.get("failure_class") or (
                (r["error_message"] or "").split("|", 1)[0].strip() or "unknown"
            )
            if src != "native_llm_c1":
                failure_c[str(fc)] += 1

    share = (native_ok_n / llm_attempted_n) if llm_attempted_n else None
    report = {
        "window_days": args.days,
        "since": since.isoformat(),
        "n_total": len(rows),
        "n_fallback": fallback_n,
        "fallback_share": (fallback_n / len(rows)) if rows else None,
        "n_llm_attempted": llm_attempted_n,
        "n_native_ok": native_ok_n,
        "native_success_share_among_attempted": share,
        "generation_source": dict(source_c),
        "failure_class_among_attempted_fails": dict(failure_c),
        "alert_below": args.alert_below,
        "alert": bool(share is not None and share < args.alert_below),
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"day_story_v1 last {args.days}d · n={len(rows)}")
        print(f"  fallback_share={report['fallback_share']!s}")
        print(
            f"  native_success_among_llm_attempted="
            f"{native_ok_n}/{llm_attempted_n}"
            + (f" ({share:.1%})" if share is not None else "")
        )
        print("  generation_source:", dict(source_c))
        print("  failure_class (attempted fails):", dict(failure_c))
        if report["alert"] and not args.no_alert:
            print(
                f"ALERT: native share {share:.1%} < {args.alert_below:.0%}",
                file=sys.stderr,
            )

    if report["alert"] and not args.no_alert:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
