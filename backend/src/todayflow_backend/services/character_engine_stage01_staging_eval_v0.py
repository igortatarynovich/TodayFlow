"""Stage 0–1 staging evaluation — fixed profiles, breadth/authority gates.

Run:
  PYTHONPATH=src .venv/bin/python -m todayflow_backend.services.character_engine_stage01_staging_eval_v0

Or via pytest (asserts gate).
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from todayflow_backend.services.character_engine_stage01_shadow_v0 import (
    run_character_engine_stage01_shadow_v0,
)

FIXTURE_PATH = (
    Path(__file__).resolve().parents[3]
    / "tests"
    / "fixtures"
    / "character_engine_stage01_staging_profiles_v0.json"
)
# When imported from installed package, parents differ — also try repo-relative.
_REPO_FIXTURE = Path(__file__).resolve().parents[4] / "backend/tests/fixtures/character_engine_stage01_staging_profiles_v0.json"


def _load_profiles() -> list[dict[str, Any]]:
    path = FIXTURE_PATH if FIXTURE_PATH.is_file() else _REPO_FIXTURE
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("profiles") or [])


def _summarize_case(profile: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    stage0 = artifact.get("stage0") or {}
    stage1 = artifact.get("stage1") or {}
    facts = stage0.get("raw_facts") or []
    claims = stage1.get("claims") or []
    excluded = stage1.get("excluded_candidates") or []
    edges = stage1.get("edges") or []
    dedupe = (stage0.get("diagnostics") or {}).get("dedupe") or []
    fact_types = [f.get("fact_type") for f in facts]
    claim_theses = [c.get("thesis_key") for c in claims]
    authorities = Counter(str(f.get("authority")) for f in facts)
    edge_types = Counter(str(e.get("edge_type")) for e in edges)
    return {
        "id": profile.get("id"),
        "label": profile.get("label"),
        "ok": bool(artifact.get("ok")),
        "fact_count": len(facts),
        "fact_types": fact_types,
        "authorities": dict(authorities),
        "dedupe": dedupe,
        "claim_count": len(claims),
        "thesis_keys": claim_theses,
        "claim_kinds": [c.get("claim_kind") for c in claims],
        "excluded": excluded,
        "edge_types": dict(edge_types),
        "has_asc": any(t == "angle_sign:ascendant" for t in fact_types),
        "has_houses": any(str(t).startswith("house_cusp_sign:") for t in fact_types),
        "bridge_in_pack": any(f.get("authority") == "bridge_natal_facts_llm" for f in facts),
        "swiss_sun": next(
            (
                f.get("value")
                for f in facts
                if f.get("fact_type") == "planet_sign:sun" and f.get("authority") == "swiss"
            ),
            None,
        ),
        "validation": (stage1.get("diagnostics") or {}).get("validation"),
        "input_fact_set_version": stage0.get("input_fact_set_version"),
        "claim_ids": [c.get("claim_id") for c in claims],
        "fact_ids": [f.get("fact_id") for f in facts],
    }


def evaluate_stage01_staging_v0() -> dict[str, Any]:
    profiles = _load_profiles()
    cases: list[dict[str, Any]] = []
    for profile in profiles:
        art = run_character_engine_stage01_shadow_v0(
            profile_fingerprint=str(profile["profile_fingerprint"]),
            swiss_chart=profile.get("swiss_chart"),
            numerology=profile.get("numerology"),
            natal_facts_bridge=profile.get("natal_facts_bridge"),
            capability=profile.get("capability"),
            birth_date=profile.get("birth_date"),
            input_fingerprint=str(profile["profile_fingerprint"]),
        )
        # Repeatability
        art2 = run_character_engine_stage01_shadow_v0(
            profile_fingerprint=str(profile["profile_fingerprint"]),
            swiss_chart=profile.get("swiss_chart"),
            numerology=profile.get("numerology"),
            natal_facts_bridge=profile.get("natal_facts_bridge"),
            capability=profile.get("capability"),
            birth_date=profile.get("birth_date"),
            input_fingerprint=str(profile["profile_fingerprint"]),
        )
        summary = _summarize_case(profile, art)
        summary["repeatable_fact_ids"] = summary["fact_ids"] == [
            f.get("fact_id") for f in (art2.get("stage0") or {}).get("raw_facts") or []
        ]
        summary["repeatable_claim_ids"] = summary["claim_ids"] == [
            c.get("claim_id") for c in (art2.get("stage1") or {}).get("claims") or []
        ]
        cases.append(summary)

    thesis_freq = Counter()
    for c in cases:
        for t in c.get("thesis_keys") or []:
            thesis_freq[str(t)] += 1
    n = max(len(cases), 1)
    majority_threshold = max(2, (n + 1) // 2)
    majority_theses = sorted(t for t, k in thesis_freq.items() if k >= majority_threshold)

    gates = {
        "all_cases_ok": all(c.get("ok") for c in cases),
        "all_repeatable": all(c.get("repeatable_fact_ids") and c.get("repeatable_claim_ids") for c in cases),
        "date_only_excludes_full_natal_facts": all(
            (not c.get("has_asc") and not c.get("has_houses"))
            for c in cases
            if c.get("id") != "full_natal_air_asc"
        ),
        "full_natal_can_include_asc": any(
            c.get("id") == "full_natal_air_asc" and c.get("has_asc") for c in cases
        ),
        "swiss_beats_bridge": any(
            c.get("id") == "bridge_diverges_swiss"
            and c.get("swiss_sun") is not None
            and not c.get("bridge_in_pack")
            and any(
                d.get("dropped_authority") == "bridge_natal_facts_llm" for d in (c.get("dedupe") or [])
            )
            for c in cases
        ),
        "no_majority_identical_claim_set": len({tuple(c.get("thesis_keys") or []) for c in cases}) >= 3,
        "no_single_thesis_on_most_profiles": all(
            (thesis_freq[t] / n) <= 0.5 for t in thesis_freq
        ),
        "negative_controls_clean": all(
            (
                c.get("id") != "date_only"
                or c.get("thesis_keys") == []
            )
            and (
                c.get("id") != "water_emotional"
                or "autonomy_high" not in (c.get("thesis_keys") or [])
            )
            and (
                c.get("id") != "earth_analysis"
                or "autonomy_high" not in (c.get("thesis_keys") or [])
            )
            for c in cases
        ),
        "claim_sets_differ_across_distinct_charts": len(
            {
                tuple(c.get("thesis_keys") or [])
                for c in cases
                if c.get("id") in {"earth_analysis", "water_emotional", "fire_direct", "date_only"}
            }
        )
        >= 3,
    }

    return {
        "eval_version": "character_engine_stage01_staging_eval_v0",
        "profile_count": len(cases),
        "cases": cases,
        "thesis_frequency": dict(thesis_freq),
        "majority_theses": majority_theses,
        "gates": gates,
        "gate_pass": all(gates.values()),
        "publish_semantics_unchanged": True,
        "note": "Diagnostics-only; CHARACTER_ENGINE_STAGE01_SHADOW does not alter active Snapshot SoT.",
    }


def main() -> int:
    report = evaluate_stage01_staging_v0()
    print(json.dumps({k: report[k] for k in ("eval_version", "profile_count", "thesis_frequency", "gates", "gate_pass")}, indent=2))
    for case in report["cases"]:
        print(
            f"- {case['id']}: claims={case['thesis_keys']} facts={len(case['fact_types'])} "
            f"asc={case['has_asc']} ok={case['ok']}"
        )
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
