#!/usr/bin/env python3
"""Sample LLM run for content v1 (registered/premium) — opt-in, costs tokens.

Usage:
  COMPAT_EVAL_LLM=1 PYTHONPATH=src python evals/compatibility_quality/run_llm_sample_v1.py --limit 5

Does not switch production. Writes JSONL under runs/.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from todayflow_backend.services.compatibility_content_v1.generate_v1 import (  # noqa: E402
    build_generation_input,
    generate_content_v1,
)
from todayflow_backend.services.compatibility_content_v1.guest_baseline_v1 import (  # noqa: E402
    build_guest_content_v1,
)
from todayflow_backend.services.compatibility_content_v1.quality_checks import (  # noqa: E402
    run_quality_suite,
)


def main() -> int:
    if os.getenv("COMPAT_EVAL_LLM") != "1":
        print("Set COMPAT_EVAL_LLM=1 to spend tokens on sample generation.")
        return 2
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--tier", choices=["registered", "premium", "both"], default="both")
    args = ap.parse_args()

    scenarios = json.loads((Path(__file__).parent / "scenarios_v1.json").read_text(encoding="utf-8"))[
        "scenarios"
    ]
    out_dir = Path(__file__).parent / "runs"
    out_dir.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = out_dir / f"content_v1_sample_{stamp}.jsonl"

    n = 0
    with out_path.open("w", encoding="utf-8") as fh:
        for sc in scenarios[: max(1, args.limit)]:
            guest = build_guest_content_v1(
                from_sign=sc["from_sign"],
                to_sign=sc["to_sign"],
                relationship_context=sc.get("relationship_context"),
                locale=sc.get("locale") or "ru",
                source_depth=sc.get("source_depth"),
                has_birth_dates=bool(sc.get("birth_date_1") and sc.get("birth_date_2")),
            ).model_dump()
            payload = build_generation_input(
                from_sign=sc["from_sign"],
                to_sign=sc["to_sign"],
                locale=sc.get("locale") or "ru",
                relationship_context=sc.get("relationship_context"),
                birth_date_1=sc.get("birth_date_1"),
                birth_date_2=sc.get("birth_date_2"),
                profile_a=sc.get("profile_a"),
                profile_b=sc.get("profile_b"),
                user_question=sc.get("user_question"),
            )
            row: dict = {"id": sc["id"], "guest_ok": run_quality_suite(tier="guest", content=guest)["ok"]}
            tiers = ["registered", "premium"] if args.tier == "both" else [args.tier]
            for tier in tiers:
                if tier == "premium" and "premium" not in (sc.get("tiers_to_score") or []):
                    continue
                result = generate_content_v1(tier=tier, input_payload=payload)  # type: ignore[arg-type]
                if result.get("ok") and tier == "registered":
                    result = {
                        **result,
                        **run_quality_suite(
                            tier="registered",
                            content=result["content"],
                            peer_guest=guest,
                        ),
                    }
                row[tier] = {
                    "ok": result.get("ok"),
                    "errors": result.get("errors"),
                    "content": result.get("content"),
                }
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1
            print(sc["id"], {k: row[k].get("ok") for k in tiers if k in row})
    print("wrote", out_path, "rows", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
