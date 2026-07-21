#!/usr/bin/env python3
"""Offline structural checks for guest baseline + scenario coverage (no LLM)."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from todayflow_backend.services.compatibility_content_v1.guest_baseline_v1 import (  # noqa: E402
    build_guest_content_v1,
)
from todayflow_backend.services.compatibility_content_v1.quality_checks import (  # noqa: E402
    check_template_diversity,
    run_quality_suite,
    sense_fingerprint,
)


def main() -> int:
    scenarios_path = Path(__file__).parent / "scenarios_v1.json"
    doc = json.loads(scenarios_path.read_text(encoding="utf-8"))
    scenarios = doc["scenarios"]
    assert len(scenarios) >= 80

    groups = Counter(s["group"] for s in scenarios)
    print("groups", dict(groups))

    guest_outputs = []
    failures = []
    fps = []
    for sc in scenarios:
        content = build_guest_content_v1(
            from_sign=sc["from_sign"],
            to_sign=sc["to_sign"],
            relationship_context=sc.get("relationship_context"),
            locale=sc.get("locale") or "ru",
            source_depth=sc.get("source_depth"),
            has_birth_dates=bool(sc.get("birth_date_1") and sc.get("birth_date_2")),
        )
        data = content.model_dump()
        guest_outputs.append(data)
        q = run_quality_suite(tier="guest", content=data)
        if not q["ok"]:
            failures.append({"id": sc["id"], "errors": q["errors"]})
        fps.append(sense_fingerprint(data))

        # Stability: same input → same fingerprint
        again = build_guest_content_v1(
            from_sign=sc["from_sign"],
            to_sign=sc["to_sign"],
            relationship_context=sc.get("relationship_context"),
            locale=sc.get("locale") or "ru",
            source_depth=sc.get("source_depth"),
            has_birth_dates=bool(sc.get("birth_date_1") and sc.get("birth_date_2")),
        )
        if sense_fingerprint(again.model_dump()) != q["fingerprint"]:
            failures.append({"id": sc["id"], "errors": ["stability:fingerprint_drift"]})

    divers = check_template_diversity(guest_outputs, field="summary", min_unique_ratio=0.55)
    divers += check_template_diversity(guest_outputs, field="headline", min_unique_ratio=0.4)

    print("guest_ok", len(scenarios) - len(failures), "/", len(scenarios))
    print("unique_fps", len(set(fps)), "/", len(fps))
    if divers:
        print("diversity_warnings", divers)
    if failures:
        print("FAILURES", json.dumps(failures[:15], ensure_ascii=False, indent=2))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
