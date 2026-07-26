#!/usr/bin/env python3
"""Export C3.6.2 blind packets from curated EN/RU eval natives (no live EN required).

Eval-only. Strips analyzer / mutation leakage. Does **not** invent human labels.

Usage (from backend/):
  PYTHONPATH=src .venv/bin/python evals/day_scenario_quality/export_curated_human_golden_c362.py \\
    --en 20 --batch-id c362_en_expansion_20260726
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT / "src"))

from todayflow_backend.services.day_scenario_eval_fixtures_c351 import (  # noqa: E402
    apply_mutation,
)
from todayflow_backend.services.day_scenario_eval_pack_c35 import (  # noqa: E402
    CONTROL_PROFILE_IDS,
    PROFILE_IDS,
    build_synthetic_eval_matrix_c351,
)
from todayflow_backend.services.day_scenario_human_golden_c362 import (  # noqa: E402
    build_human_case_shell,
    detect_duplicate_scenario_hashes,
    export_blind_review_packet,
    new_neutral_case_id,
    version_bundle,
)
from todayflow_backend.services.day_scenario_native_llm_c1 import (  # noqa: E402
    normalize_native_scenario_llm_c1,
)


def _normalize_keep_closure(raw: dict[str, Any]) -> dict[str, Any]:
    """Match eval-pack scoring: normalize drops day_closure — reattach for human review."""
    from copy import deepcopy

    n = normalize_native_scenario_llm_c1(deepcopy(raw if isinstance(raw, dict) else {}))
    if raw.get("day_closure") and not n.get("day_closure"):
        n["day_closure"] = deepcopy(raw["day_closure"])
    elif raw.get("closure") and not n.get("day_closure"):
        n["day_closure"] = deepcopy(raw["closure"])
    return n

# Operator-only mix plan — never written into blind packets.
_EN_SLOT_PLAN: list[dict[str, Any]] = [
    # pass-leaning curated good scenes (diverse profiles / days)
    {"kind": "good", "day_i": 0, "profile": "smooth_conflict"},
    {"kind": "good", "day_i": 1, "profile": "demand_clarity"},
    {"kind": "good", "day_i": 2, "profile": "analyze_first"},
    {"kind": "good", "day_i": 3, "profile": "act_first"},
    {"kind": "good", "day_i": 4, "profile": "over_responsible"},
    {"kind": "good", "day_i": 5, "profile": "rejection_sensitive"},
    {"kind": "good", "day_i": 6, "profile": "autonomy_oriented"},
    {"kind": "good", "day_i": 7, "profile": "no_birth_time"},
    {"kind": "good", "day_i": 8, "profile": "birth_date_only"},
    {"kind": "good", "day_i": 9, "profile": "no_profile"},
    # reject / hotspot coverage (mutations applied; mutation_id never exported)
    {"kind": "mut", "day_i": 10, "profile": "smooth_conflict", "mutation": "clone_scene_into_second"},
    {"kind": "mut", "day_i": 11, "profile": "demand_clarity", "mutation": "universal_advice_example"},
    {"kind": "mut", "day_i": 12, "profile": "analyze_first", "mutation": "drop_day_closure"},
    {"kind": "mut", "day_i": 13, "profile": "act_first", "mutation": "mush_closure"},
    {"kind": "mut", "day_i": 14, "profile": "over_responsible", "mutation": "soft_generic_action"},
    {"kind": "mut", "day_i": 15, "profile": "rejection_sensitive", "mutation": "clone_scene_into_second"},
    {"kind": "mut", "day_i": 16, "profile": "autonomy_oriented", "mutation": "universal_advice_example"},
    {"kind": "good", "day_i": 17, "profile": "incomplete_evidence"},
    {"kind": "good", "day_i": 18, "profile": "smooth_conflict"},
    {"kind": "mut", "day_i": 19, "profile": "demand_clarity", "mutation": "drop_evidence_refs"},
]


def _map_profile_type(profile_id: str) -> str:
    if profile_id in CONTROL_PROFILE_IDS:
        return f"curated_control_{profile_id}"
    return f"curated_{profile_id}"


def _map_evidence_depth(profile_id: str) -> str:
    if profile_id in {"no_profile", "incomplete_evidence"}:
        return "general"
    if profile_id in {"no_birth_time", "birth_date_only"}:
        return "general_personalized"
    return "deep_personalized"


def _cell_for(matrix: list[dict[str, Any]], *, day_i: int, profile: str, locale: str) -> dict[str, Any]:
    by_day: dict[str, dict[str, Any]] = {}
    for c in matrix:
        if c.get("locale") != locale or c.get("profile_id") != profile:
            continue
        by_day[str(c.get("date"))] = c
    dates = sorted(by_day.keys())
    if not dates:
        raise SystemExit(f"no matrix cell for {locale}/{profile}")
    return by_day[dates[day_i % len(dates)]]


def _write_review_sheet(blind: dict[str, Any], path: Path) -> None:
    sc = blind.get("scenario") if isinstance(blind.get("scenario"), dict) else {}
    conflict = sc.get("conflict") if isinstance(sc.get("conflict"), dict) else {}
    scenes = sc.get("scenes") if isinstance(sc.get("scenes"), list) else []
    lines = [
        f"# Review sheet — `{blind.get('case_id')}`",
        "",
        f"- scenario_hash: `{blind.get('scenario_hash')}`",
        f"- locale: {blind.get('locale')}",
        f"- Fill: `reviewer_templates/{blind.get('case_id')}.reviewer_*.json`",
        "- Rubric: `docs/audits/DAY_SCENARIO_HUMAN_REVIEW_RUBRIC_C362.md`",
        "- **Blind:** do not open `cases/` or the other reviewer's template",
        "",
        "## Conflict",
        f"- short_name: {conflict.get('title') or conflict.get('short_name') or ''}",
        f"- thesis: {conflict.get('thesis') or ''}",
        "",
        "## Scenes",
    ]
    for i, raw in enumerate(scenes, start=1):
        if not isinstance(raw, dict):
            continue
        lines.extend(
            [
                f"### Scene {i}: {raw.get('scene_id')} / {raw.get('sphere')}",
                f"- **setup:** {raw.get('setup') or ''}",
                f"- **everyday_example:** {raw.get('everyday_example') or ''}",
                f"- **opportunity:** {raw.get('opportunity') or ''}",
                f"- **trap:** {raw.get('trap') or ''}",
                f"- **recommended_action:** {raw.get('recommended_action') or ''}",
                f"- **avoid_action:** {raw.get('avoid_action') or ''}",
                "",
            ]
        )
    chorus = sc.get("interpretive_chorus") if isinstance(sc.get("interpretive_chorus"), dict) else {}
    if chorus:
        lines.append("## Chorus (skim)")
        for key in ("astrology", "day_card", "day_number", "natal"):
            row = chorus.get(key)
            if isinstance(row, list) and row and isinstance(row[0], dict):
                lines.append(f"- **{key}:** {row[0].get('human_meaning') or row[0].get('named_factor') or ''}")
            elif isinstance(row, dict):
                lines.append(
                    f"- **{key}:** {row.get('human_meaning') or row.get('archetype_role') or row.get('tempo') or row.get('named_factor') or ''}"
                )
        lines.append("")
    closure = sc.get("day_closure") if isinstance(sc.get("day_closure"), dict) else {}
    if closure:
        lines.append("## Closure")
        for k, v in closure.items():
            lines.append(f"- **{k}:** {v}")
        lines.append("")
    lines.extend(
        [
            "## Your labels",
            "",
            "- overall_band: `pass` | `acceptable_with_issues` | `reject` | `cannot_assess`",
            "- Priority: SCENE_ABSTRACT, SCENE_CLONE, SCENE_MISSING_EVERYDAY, SCENE_UNIVERSAL_ADVICE, ASTRO_JARGON_BARE, PERSONALIZATION_PROFILE_FACT_LEAK",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def export_curated_en_batch(
    *,
    out_dir: Path,
    en_count: int,
    batch_id: str,
) -> dict[str, Any]:
    matrix = build_synthetic_eval_matrix_c351(start=date(2026, 7, 1), days=28, profile_ids=PROFILE_IDS)
    plan = _EN_SLOT_PLAN[: max(1, min(en_count, len(_EN_SLOT_PLAN)))]

    root = out_dir / batch_id
    cases_dir = root / "cases"
    blind_dir = root / "blind"
    templates_dir = root / "reviewer_templates"
    sheets_dir = root / "review_sheets"
    for d in (cases_dir, blind_dir, templates_dir, sheets_dir):
        d.mkdir(parents=True, exist_ok=True)

    index_cases: list[dict[str, Any]] = []
    case_shells: list[dict[str, Any]] = []
    operator_mix: list[dict[str, Any]] = []

    for slot_i, slot in enumerate(plan):
        cell = _cell_for(matrix, day_i=int(slot["day_i"]), profile=str(slot["profile"]), locale="en")
        native_raw = cell.get("native") if isinstance(cell.get("native"), dict) else {}
        mut = slot.get("mutation")
        if mut:
            native_raw = apply_mutation(native_raw, str(mut))
        native = _normalize_keep_closure(native_raw)
        seed = f"curated-en-{batch_id}-{slot_i}-{slot['profile']}-{slot['day_i']}"
        case_id = new_neutral_case_id(seed=seed)
        profile_id = str(slot["profile"])
        case = build_human_case_shell(
            case_id=case_id,
            scenario=native,
            locale="en",
            profile_type=_map_profile_type(profile_id),
            evidence_depth=_map_evidence_depth(profile_id),
            source_type="curated",
            generator_version="eval_matrix_c351_curated_en",
            generation_seed=seed,
            scenario_id=case_id,
            evidence_pack_ref=f"curated_en_slot:{slot_i}",
            contract_valid=True,
            hard_gate_result="accept",
        )
        case["review_status"] = "exported_blind"
        # Operator meta only on cases/ — never in blind/
        case["curated_meta"] = {
            "slot": slot_i,
            "profile_id": profile_id,
            "day_type": cell.get("day_type"),
            "kind": slot.get("kind"),
            # mutation kept operator-side only (stripped from blind by protocol)
            "operator_mutation": mut,
        }
        blind = export_blind_review_packet(case)
        (cases_dir / f"{case_id}.json").write_text(
            json.dumps(case, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (blind_dir / f"{case_id}.blind.json").write_text(
            json.dumps(blind, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        _write_review_sheet(blind, sheets_dir / f"{case_id}.md")
        for rid in ("reviewer_a", "reviewer_b"):
            tmpl = {
                "case_id": case_id,
                "scenario_hash": case["scenario_hash"],
                "reviewer_id": rid,
                "overall_band": None,
                "defects": {
                    code: {
                        "presence": None,
                        "severity": None,
                        "evidence_location": None,
                        "rationale": None,
                        "affects_overall_band": None,
                    }
                    for code in blind["defect_codes_for_labeling"]
                },
                "notes": None,
                **version_bundle(),
            }
            (templates_dir / f"{case_id}.{rid}.json").write_text(
                json.dumps(tmpl, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        case_shells.append(case)
        index_cases.append(
            {
                "case_id": case_id,
                "locale": "en",
                "source_type": "curated",
                "profile_type": case["profile_type"],
                "evidence_depth": case["evidence_depth"],
                "scenario_hash": case["scenario_hash"],
                "blind_path": f"blind/{case_id}.blind.json",
                "sheet_path": f"review_sheets/{case_id}.md",
                "case_path": f"cases/{case_id}.json",
            }
        )
        operator_mix.append(
            {
                "case_id": case_id,
                "slot": slot_i,
                "kind": slot.get("kind"),
                "profile_id": profile_id,
                "operator_mutation": mut,
            }
        )

    dups = detect_duplicate_scenario_hashes(case_shells)
    manifest = {
        "batch_id": batch_id,
        "export_kind": "c362_human_golden_curated_en_batch",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "versions": version_bundle(),
        "case_count": len(index_cases),
        "locale_counts": {"en": len(index_cases)},
        "duplicate_scenario_hashes": dups,
        "inventory_note": (
            "Curated EN expansion toward 20 EN / 40 total. "
            "Live EN native_llm_c1 inventory was empty at export time. "
            "Do not treat operator_mix.json as reviewer input."
        ),
        "instructions": {
            "quorum": 2,
            "rubric": "docs/audits/DAY_SCENARIO_HUMAN_REVIEW_RUBRIC_C362.md",
            "protocol": "docs/audits/DAY_SCENARIO_HUMAN_GOLDEN_C362.md",
            "blind_dir": "blind/",
            "review_sheets": "review_sheets/",
            "do_not_open_cases_dir_as_reviewer": True,
            "do_not_open_operator_mix": True,
        },
        "cases": index_cases,
    }
    (root / "index.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / "operator_mix.json").write_text(
        json.dumps({"batch_id": batch_id, "slots": operator_mix}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        f"""# Human golden curated EN batch `{batch_id}`

Curated EN natives from C3.5.1 eval matrix (+ selective mutations) for C3.6.2 blind review.

## Why curated

Live DB had **0** `native_llm_c1` EN day_scenario rows at export. Protocol allows `source_type=curated`
toward the 20 EN / 40 total inventory target. Labels still require dual blind review — no auto-seal.

## For reviewers

1. Open only `review_sheets/` or `blind/` + rubric.
2. Do **not** open `cases/`, `operator_mix.json`, or the other reviewer's templates.
3. Fill `reviewer_templates/<case_id>.reviewer_a.json` / `.reviewer_b.json`.

## Inventory

- Cases: **{len(index_cases)}** EN curated
- Prior sealed RU pilot: `c362_blind_pilot_20260726` (7) — combined path toward 40
""",
        encoding="utf-8",
    )
    (root / "REVIEWER_B_INSTRUCTIONS.md").write_text(
        f"""# Reviewer B — `{batch_id}`

1. Open only `review_sheets/*.md` (or `blind/*.json`) + the rubric.
2. Do **not** open `cases/`, `operator_mix.json`, or any `*.reviewer_a.json`.
3. Fill each `reviewer_templates/<case_id>.reviewer_b.json`.
4. When filled, operator runs `import_human_reviews_seal_c362.py --batch <this dir>`.
""",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO / "docs" / "audits" / "day_scenario_human_golden" / "batches",
    )
    ap.add_argument("--en", type=int, default=20)
    ap.add_argument("--batch-id", default="c362_en_expansion_20260726")
    args = ap.parse_args()
    manifest = export_curated_en_batch(out_dir=args.out, en_count=args.en, batch_id=args.batch_id)
    print(
        json.dumps(
            {"ok": True, "batch_id": manifest["batch_id"], "case_count": manifest["case_count"]},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
