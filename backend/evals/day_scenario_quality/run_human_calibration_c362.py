#!/usr/bin/env python3
"""Run C3.6.2 human-consensus calibration over sealed golden batches (eval-only).

Loads sealed/*.json from the three inventory batches, attaches analyzer codes,
writes baseline JSON + markdown. Does **not** promote maturity or change runtime.

Usage (from backend/):
  PYTHONPATH=src .venv/bin/python evals/day_scenario_quality/run_human_calibration_c362.py
"""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT / "src"))

from todayflow_backend.services.day_scenario_editorial_gate_c31 import (  # noqa: E402
    run_editorial_quality_gate_c31,
)
from todayflow_backend.services.day_scenario_eval_editorial_en_c351 import (  # noqa: E402
    run_editorial_quality_gate_en_c351,
)
from todayflow_backend.services.day_scenario_gate_maturity_c36 import (  # noqa: E402
    MATURITY_BLOCKING,
    MATURITY_CANDIDATE_BLOCKING,
    annotate_defects_with_maturity,
    get_rule,
)
from todayflow_backend.services.day_scenario_human_calibration_c362 import (  # noqa: E402
    run_human_consensus_calibration_c362,
)

BATCHES = (
    "c362_blind_pilot_20260726",
    "c362_en_expansion_20260726",
    "c362_ru_live_expansion_20260727",
)
BATCH_ROOT = REPO / "docs" / "audits" / "day_scenario_human_golden" / "batches"
OUT_JSON = REPO / "docs" / "audits" / "DAY_SCENARIO_HUMAN_CALIBRATION_BASELINE_C362.json"
OUT_MD = REPO / "docs" / "audits" / "DAY_SCENARIO_HUMAN_CALIBRATION_BASELINE_C362.md"


def _projected_to_gate_native(scenario: dict[str, Any]) -> dict[str, Any]:
    """Map day_scenario_v1 projection fields onto native-shaped inputs for editorial gates."""
    sc = deepcopy(scenario if isinstance(scenario, dict) else {})
    if sc.get("schema_version") and sc.get("interpretive_chorus") is not None:
        return sc  # already native
    scenes_out: list[dict[str, Any]] = []
    for raw in sc.get("scenes") or []:
        if not isinstance(raw, dict):
            continue
        row = dict(raw)
        row.setdefault("setup", row.get("what_happens") or "")
        row.setdefault("everyday_example", row.get("domestic_example") or "")
        row.setdefault("avoid_action", row.get("do_not") or "")
        scenes_out.append(row)
    chorus_src = sc.get("chorus") if isinstance(sc.get("chorus"), dict) else {}
    interpretive = sc.get("interpretive_chorus")
    if not isinstance(interpretive, dict):
        interpretive = {
            "astrology": list(chorus_src.get("astrology") or []),
            "day_card": chorus_src.get("day_card") if isinstance(chorus_src.get("day_card"), dict) else {},
            "day_number": chorus_src.get("day_number") if isinstance(chorus_src.get("day_number"), dict) else {},
            "natal": list(chorus_src.get("natal") or []),
        }
    conflict = sc.get("conflict") if isinstance(sc.get("conflict"), dict) else {}
    # Projected conflict may use short_name
    if conflict and not conflict.get("title") and conflict.get("short_name"):
        conflict = {**conflict, "title": conflict.get("short_name")}
    return {
        "schema_version": sc.get("schema_version") or "day_scenario_projected_for_gate",
        "conflict": conflict,
        "scenes": scenes_out,
        "interpretive_chorus": interpretive,
        "prop_material": sc.get("prop_material") or sc.get("props") or {},
        "day_closure": sc.get("day_closure") or {},
    }


def _analyze(case: dict[str, Any]) -> list[str]:
    native = _projected_to_gate_native(case.get("scenario") or {})
    locale = str(case.get("locale") or "ru").lower()
    if locale.startswith("en"):
        defects = run_editorial_quality_gate_en_c351(native)
    else:
        defects = run_editorial_quality_gate_c31(native, has_natal_evidence=False)
    annotated = annotate_defects_with_maturity(defects)
    return sorted({str(d.get("code") or "") for d in annotated if d.get("code")})


def _load_sealed() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for bid in BATCHES:
        sealed = BATCH_ROOT / bid / "sealed"
        for path in sorted(sealed.glob("*.sealed.json")):
            case = json.loads(path.read_text(encoding="utf-8"))
            if case.get("review_status") != "sealed" or not case.get("final_consensus"):
                continue
            codes = _analyze(case)
            case["analyzer_attachment"] = {
                "attached_at": datetime.now(timezone.utc).isoformat(),
                "output": {"defect_codes": codes, "source": "editorial_gate_post_seal"},
            }
            cases.append(case)
    return cases


def _shadow(cases: list[dict[str, Any]]) -> dict[str, Any]:
    """Counterfactual blocks vs human overall bands."""
    actual_blocked = 0
    would_block_quality = 0
    would_block_if_universal_promoted = 0
    false_blocks = 0
    true_blocks = 0
    false_if_universal = 0
    true_if_universal = 0
    false_block_rows: list[dict[str, Any]] = []

    for case in cases:
        band = str((case.get("final_consensus") or {}).get("overall_band") or "")
        codes = set((case.get("analyzer_attachment") or {}).get("output", {}).get("defect_codes") or [])
        blocking_hits = sorted(c for c in codes if get_rule(c).maturity == MATURITY_BLOCKING)
        any_quality = [c for c in codes if get_rule(c).family == "quality"]
        universal = "SCENE_UNIVERSAL_ADVICE" in codes

        if blocking_hits:
            actual_blocked += 1
            if band in {"pass", "acceptable_with_issues"}:
                false_blocks += 1
                false_block_rows.append(
                    {
                        "case_id": case.get("case_id"),
                        "locale": case.get("locale"),
                        "overall_band": band,
                        "blocking_codes": blocking_hits,
                        "batch_id": case.get("batch_id"),
                    }
                )
            elif band == "reject":
                true_blocks += 1
        if any_quality:
            would_block_quality += 1
        if blocking_hits or universal:
            would_block_if_universal_promoted += 1
            if band in {"pass", "acceptable_with_issues"}:
                false_if_universal += 1
            elif band == "reject":
                true_if_universal += 1

    return {
        "case_count": len(cases),
        "actual_runtime_blocked": actual_blocked,
        "false_blocks_against_labels": false_blocks,
        "true_blocks_against_labels": true_blocks,
        "false_block_cases": false_block_rows,
        "would_block_if_any_quality_promoted": would_block_quality,
        "would_block_if_SCENE_UNIVERSAL_ADVICE_promoted": would_block_if_universal_promoted,
        "false_blocks_if_SCENE_UNIVERSAL_ADVICE_promoted": false_if_universal,
        "true_blocks_if_SCENE_UNIVERSAL_ADVICE_promoted": true_if_universal,
        "note": (
            "actual_runtime_blocked uses maturity=blocking fires from analyzer on sealed cases. "
            "false_blocks = pass/acceptable wrongly blocked."
        ),
    }


def _promotion_candidates(report: dict[str, Any], shadow: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in report.get("per_code") or []:
        code = row["code"]
        rule = get_rule(code)
        if rule.maturity not in {MATURITY_CANDIDATE_BLOCKING, "experimental", "advisory"}:
            continue
        if row.get("metric_status") != "measured":
            continue
        prec = row.get("precision")
        rec = row.get("recall")
        fpr = row.get("false_positive_rate")
        recommend = False
        reason = "measured but not yet recommended"
        if code == "SCENE_UNIVERSAL_ADVICE":
            # Promote only if precision high and shadow false blocks stay low relative to true.
            fb = shadow.get("false_blocks_if_SCENE_UNIVERSAL_ADVICE_promoted") or 0
            tb = shadow.get("true_blocks_if_SCENE_UNIVERSAL_ADVICE_promoted") or 0
            if prec is not None and prec >= 0.75 and rec is not None and rec >= 0.6 and fb <= max(1, tb // 2):
                recommend = True
                reason = "measured P/R + shadow false-block budget ok → candidate for blocking"
            else:
                reason = f"keep candidate_blocking (P={prec}, R={rec}, shadow_false={fb}, shadow_true={tb})"
        elif code == "CHORUS_SEMANTIC_DUPLICATION":
            if prec == 1.0 and rec == 1.0 and (row.get("support_positive") or 0) >= 4:
                recommend = True
                reason = "perfect measured P/R on n≥4 → promote to candidate_blocking (observe)"
            else:
                reason = "measured but below chorus promotion bar"
        out.append(
            {
                "code": code,
                "maturity_now": rule.maturity,
                "precision": prec,
                "recall": rec,
                "false_positive_rate": fpr,
                "support_positive": row.get("support_positive"),
                "support_negative": row.get("support_negative"),
                "recommend_promote_to_blocking": recommend,
                "reason": reason,
            }
        )
    return out


def _write_md(report: dict[str, Any], shadow: dict[str, Any], candidates: list[dict[str, Any]]) -> str:
    measured = [r for r in report["per_code"] if r["metric_status"] == "measured"]
    lines = [
        "# Day Scenario Human Calibration Baseline C3.6.2",
        "",
        "**Status:** LANDED (human consensus calibration · eval-only · one observe promotion)",
        f"**Date:** {datetime.now(timezone.utc).date().isoformat()}",
        f"**Cases:** {report['case_count']} sealed human (`label_source=human`)",
        f"**Locales:** {report.get('by_locale')}",
        "",
        "## Architecture impact",
        "",
        "```markdown",
        "## Architecture impact",
        "- **SoT before:** C3.6.1 synthetic_bootstrap calibration only; human pilot used for C3.6.3 promotions",
        "- **SoT after:** human consensus calibration over 40 sealed cases; analyzer P/R vs human labels;",
        "  shadow false-block KPI; CHORUS_SEMANTIC_DUPLICATION → candidate_blocking (observe);",
        "  SCENE_UNIVERSAL_ADVICE stays candidate_blocking (low recall)",
        "- **Public contract changed?** no",
        "- **Migration required?** no",
        "- **Canon updated?** yes — this baseline + tracker + DAY_SCENARIO_V1 + HUMAN_CALIBRATION_C362",
        "- **Backward compatible?** yes — candidate_blocking remains observe-only (no retry/reject)",
        "```",
        "",
        "## Shadow KPI",
        "",
        f"- `actual_runtime_blocked`: **{shadow['actual_runtime_blocked']}**",
        f"- `false_blocks_against_labels`: **{shadow['false_blocks_against_labels']}**",
        f"- `true_blocks_against_labels`: **{shadow['true_blocks_against_labels']}**",
        f"- `would_block_if_SCENE_UNIVERSAL_ADVICE_promoted`: **{shadow['would_block_if_SCENE_UNIVERSAL_ADVICE_promoted']}**",
        f"- `false_blocks_if_SCENE_UNIVERSAL_ADVICE_promoted`: **{shadow['false_blocks_if_SCENE_UNIVERSAL_ADVICE_promoted']}**",
        f"- `true_blocks_if_SCENE_UNIVERSAL_ADVICE_promoted`: **{shadow['true_blocks_if_SCENE_UNIVERSAL_ADVICE_promoted']}**",
        "",
        "### False-block cases (pass/acceptable hit by blocking analyzer)",
        "",
    ]
    fb_rows = shadow.get("false_block_cases") or []
    if fb_rows:
        lines.append("| case_id | locale | band | blocking_codes |")
        lines.append("|---------|--------|------|----------------|")
        for row in fb_rows:
            codes = ", ".join(f"`{c}`" for c in (row.get("blocking_codes") or []))
            lines.append(
                f"| `{row.get('case_id')}` | {row.get('locale')} | {row.get('overall_band')} | {codes} |"
            )
    else:
        lines.append("_none_")
    lines.extend(
        [
            "",
            "## Measured codes",
            "",
            "| Code | maturity | P | R | FPR | +sup | −sup |",
            "|------|----------|---|---|-----|------|------|",
        ]
    )
    for r in measured:
        lines.append(
            f"| `{r['code']}` | {r['maturity']} | {r['precision']} | {r['recall']} | "
            f"{r['false_positive_rate']} | {r['support_positive']} | {r['support_negative']} |"
        )
    lines.extend(
        [
            "",
            f"Insufficient support codes: **{len(report.get('insufficient_support_codes') or [])}**",
            "",
            "## Promotion candidates (decision table)",
            "",
            "| Code | now | recommend blocking? | reason |",
            "|------|-----|---------------------|--------|",
        ]
    )
    for c in candidates:
        lines.append(
            f"| `{c['code']}` | {c['maturity_now']} | "
            f"{'yes' if c['recommend_promote_to_blocking'] else 'no'} | {c['reason']} |"
        )
    if not candidates:
        lines.append("| — | — | — | no measured experimental/candidate codes |")
    lines.extend(
        [
            "",
            "## Explicit limits",
            "",
            "- Dual agent blind labels (not full human panel).",
            "- EN cases are curated matrix + mutations; RU are live_capture.",
            "- Analyzer attached post-seal via editorial gates (projected→native field map).",
            "- Decision table may recommend observe promotions (`candidate_blocking`); "
            "full `blocking` only with separate product acceptance.",
            "- Accepted observe promotion from this baseline: `CHORUS_SEMANTIC_DUPLICATION` → candidate_blocking.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    cases = _load_sealed()
    if len(cases) < 40:
        raise SystemExit(f"expected 40 sealed cases, got {len(cases)}")
    report = run_human_consensus_calibration_c362(cases)
    shadow = _shadow(cases)
    candidates = _promotion_candidates(report, shadow)
    payload = {
        **report,
        "shadow": shadow,
        "promotion_candidates": candidates,
        "batches": list(BATCHES),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(_write_md(report, shadow, candidates), encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": True,
                "case_count": report["case_count"],
                "measured": sum(1 for r in report["per_code"] if r["metric_status"] == "measured"),
                "insufficient": len(report.get("insufficient_support_codes") or []),
                "shadow_false_blocks": shadow["false_blocks_against_labels"],
                "promote_recommendations": [
                    c["code"] for c in candidates if c["recommend_promote_to_blocking"]
                ],
                "out_json": str(OUT_JSON.relative_to(REPO)),
                "out_md": str(OUT_MD.relative_to(REPO)),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
