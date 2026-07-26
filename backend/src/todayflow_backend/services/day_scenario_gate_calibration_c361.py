"""Phase C3.6.1 — Gate calibration harness (eval/capture only).

Synthetic bootstrap for harness verification and obvious FP discovery.
Does **not** change runtime maturity, promote rules, or touch generation.

Canon: docs/audits/DAY_SCENARIO_GATE_CALIBRATION_C361.md
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Literal

from todayflow_backend.services.day_scenario_eval_editorial_en_c351 import score_editorial_en_c351
from todayflow_backend.services.day_scenario_eval_fixtures_c351 import (
    NEGATIVE_FIXTURES,
    apply_mutation,
    good_native_en,
    good_native_ru,
)
from todayflow_backend.services.day_scenario_eval_pack_c35 import score_cell
from todayflow_backend.services.day_scenario_gate_maturity_c36 import (
    FAMILY_QUALITY,
    GATE_RULES,
    MATURITY_BLOCKING,
    annotate_defects_with_maturity,
    get_rule,
    maturity_summary,
    runtime_action_for_rule,
)

CALIBRATION_VERSION = "c36.1"
LABEL_SOURCE_SYNTHETIC = "synthetic_bootstrap"
LABEL_SOURCE_HUMAN = "human"

MetricStatus = Literal["measured", "insufficient_support"]

# Bootstrap is intentionally small — metrics below this stay insufficient.
MIN_SUPPORT_POSITIVE = 2
MIN_SUPPORT_NEGATIVE = 2


def _empty_pack(*, evidence_depth: str = "general") -> dict[str, Any]:
    return {
        "evidence_depth": evidence_depth,
        "confidence": 0.4 if evidence_depth == "general" else 0.85,
        "evidence_refs": [],
        "behavioral_tendencies": [],
        "sphere_selection": {},
    }


def _pack_for_case(case: dict[str, Any]) -> dict[str, Any]:
    depth = str(case.get("pack_depth") or "general")
    if depth == "deep":
        return {
            "evidence_depth": "deep_personalized",
            "confidence": 0.9,
            "evidence_refs": ["moon-pisces", "claim.personal.moon7.smooth"],
            "behavioral_tendencies": [{"id": "smooth_conflict"}],
            "sphere_selection": {"primary": "relationships"},
        }
    return _empty_pack(evidence_depth="general")


def bootstrap_golden_cases_c361() -> list[dict[str, Any]]:
    """Curated synthetic cases with provisional expected defects.

    `label_source=synthetic_bootstrap` — NOT human/editor consensus.
    Must not authorize maturity promotion.
    """
    return [
        {
            "case_id": "gs-c361-good-ru",
            "locale": "ru",
            "profile_id": "smooth_conflict",
            "source": "synthetic",
            "label_source": LABEL_SOURCE_SYNTHETIC,
            "native_factory": "good_native_ru",
            "pack_depth": "deep",
            "expected": {"band": "pass", "primary_defects": []},
            "consensus_band": "pass",
        },
        {
            "case_id": "gs-c361-good-en",
            "locale": "en",
            "profile_id": "smooth_conflict",
            "source": "synthetic",
            "label_source": LABEL_SOURCE_SYNTHETIC,
            "native_factory": "good_native_en",
            "pack_depth": "deep",
            "expected": {"band": "pass", "primary_defects": []},
            "consensus_band": "pass",
        },
        {
            "case_id": "gs-c361-neg-abstract-ru",
            "locale": "ru",
            "profile_id": "smooth_conflict",
            "source": "synthetic",
            "label_source": LABEL_SOURCE_SYNTHETIC,
            "negative_id": "abstract_scenes",
            "pack_depth": "general",
            "expected": {
                "band": "reject",
                "primary_defects": ["SCENE_ABSTRACT", "SCENE_UNIVERSAL_ADVICE"],
            },
            "consensus_band": "reject",
        },
        {
            "case_id": "gs-c361-neg-clone-ru",
            "locale": "ru",
            "profile_id": "smooth_conflict",
            "source": "synthetic",
            "label_source": LABEL_SOURCE_SYNTHETIC,
            "negative_id": "clone_scenes",
            "pack_depth": "general",
            "expected": {"band": "reject", "primary_defects": ["SCENE_CLONE"]},
            "consensus_band": "reject",
        },
        {
            "case_id": "gs-c361-neg-parallel-ru",
            "locale": "ru",
            "profile_id": "smooth_conflict",
            "source": "synthetic",
            "label_source": LABEL_SOURCE_SYNTHETIC,
            "negative_id": "parallel_chorus",
            "pack_depth": "general",
            "expected": {"band": "reject", "primary_defects": ["CHORUS_PARALLEL_FORECAST"]},
            "consensus_band": "reject",
        },
        {
            "case_id": "gs-c361-neg-closure-missing-ru",
            "locale": "ru",
            "profile_id": "smooth_conflict",
            "source": "synthetic",
            "label_source": LABEL_SOURCE_SYNTHETIC,
            "negative_id": "missing_day_closure",
            "pack_depth": "general",
            "expected": {"band": "reject", "primary_defects": ["CLOSURE_MISSING"]},
            "consensus_band": "reject",
        },
        {
            "case_id": "gs-c361-neg-closure-mush-ru",
            "locale": "ru",
            "profile_id": "smooth_conflict",
            "source": "synthetic",
            "label_source": LABEL_SOURCE_SYNTHETIC,
            "negative_id": "wellness_closure",
            "pack_depth": "general",
            "expected": {"band": "reject", "primary_defects": ["CLOSURE_WELLNESS_MUSH"]},
            "consensus_band": "reject",
        },
        {
            "case_id": "gs-c361-neg-conflict-ru",
            "locale": "ru",
            "profile_id": "smooth_conflict",
            "source": "synthetic",
            "label_source": LABEL_SOURCE_SYNTHETIC,
            "negative_id": "conflict_no_opposition",
            "pack_depth": "general",
            "expected": {"band": "reject", "primary_defects": ["CONFLICT_NO_OPPOSITION"]},
            "consensus_band": "reject",
        },
        {
            "case_id": "gs-c361-neg-provenance-ru",
            "locale": "ru",
            "profile_id": "smooth_conflict",
            "source": "synthetic",
            "label_source": LABEL_SOURCE_SYNTHETIC,
            "negative_id": "recommendation_without_evidence",
            "pack_depth": "deep",
            "expected": {"band": "reject", "primary_defects": ["PROVENANCE_REF_MISSING"]},
            "consensus_band": "reject",
        },
        {
            "case_id": "gs-c361-neg-locale-en",
            "locale": "en",
            "profile_id": "smooth_conflict",
            "source": "synthetic",
            "label_source": LABEL_SOURCE_SYNTHETIC,
            "negative_id": "locale_mismatch_en_cyrillic",
            "pack_depth": "general",
            "expected": {"band": "reject", "primary_defects": ["LOCALE_LANGUAGE_MISMATCH"]},
            "consensus_band": "reject",
        },
        {
            "case_id": "gs-c361-neg-locale-ru",
            "locale": "ru",
            "profile_id": "smooth_conflict",
            "source": "synthetic",
            "label_source": LABEL_SOURCE_SYNTHETIC,
            "negative_id": "locale_mismatch_ru_latin",
            "pack_depth": "general",
            "expected": {"band": "reject", "primary_defects": ["LOCALE_LANGUAGE_MISMATCH"]},
            "consensus_band": "reject",
        },
        {
            "case_id": "gs-c361-mut-universal-en",
            "locale": "en",
            "profile_id": "smooth_conflict",
            "source": "synthetic",
            "label_source": LABEL_SOURCE_SYNTHETIC,
            "native_factory": "good_native_en",
            "mutation_id": "universal_advice_example",
            "pack_depth": "deep",
            "expected": {
                "band": "reject",
                "primary_defects": ["SCENE_UNIVERSAL_ADVICE", "SCENE_ABSTRACT"],
            },
            "consensus_band": "reject",
        },
        {
            "case_id": "gs-c361-mut-clone-ru",
            "locale": "ru",
            "profile_id": "smooth_conflict",
            "source": "synthetic",
            "label_source": LABEL_SOURCE_SYNTHETIC,
            "native_factory": "good_native_ru",
            "mutation_id": "clone_scene_into_second",
            "pack_depth": "deep",
            "expected": {"band": "reject", "primary_defects": ["SCENE_CLONE"]},
            "consensus_band": "reject",
        },
        {
            "case_id": "gs-c361-mut-drop-closure-en",
            "locale": "en",
            "profile_id": "smooth_conflict",
            "source": "synthetic",
            "label_source": LABEL_SOURCE_SYNTHETIC,
            "native_factory": "good_native_en",
            "mutation_id": "drop_day_closure",
            "pack_depth": "deep",
            "expected": {"band": "reject", "primary_defects": ["CLOSURE_MISSING"]},
            "consensus_band": "reject",
        },
    ]


def resolve_case_native(case: dict[str, Any]) -> dict[str, Any]:
    if case.get("negative_id"):
        nid = str(case["negative_id"])
        if nid not in NEGATIVE_FIXTURES:
            raise KeyError(f"unknown negative_id: {nid}")
        return deepcopy(NEGATIVE_FIXTURES[nid])
    factory = str(case.get("native_factory") or "good_native_ru")
    native = good_native_en() if factory == "good_native_en" else good_native_ru()
    mut = case.get("mutation_id")
    if mut:
        native = apply_mutation(native, str(mut))
    return native


def observe_case(case: dict[str, Any]) -> dict[str, Any]:
    native = resolve_case_native(case)
    locale = str(case.get("locale") or "ru")
    profile_id = str(case.get("profile_id") or "smooth_conflict")
    pack = _pack_for_case(case)
    cell = score_cell(native=native, pack=pack, locale=locale, profile_id=profile_id)
    codes: set[str] = {str(c) for c in (cell.get("defect_codes") or []) if c}
    for c in cell.get("details", {}).get("pers_defect_codes") or []:
        if c:
            codes.add(str(c))
    en_scored = score_editorial_en_c351(native, locale=locale)
    for c in en_scored.get("defect_codes") or []:
        if c:
            codes.add(str(c))
    sorted_codes = sorted(codes)
    defects = annotate_defects_with_maturity(
        [{"code": c, "field": "cell", "message": "observed"} for c in sorted_codes]
    )
    expected = list((case.get("expected") or {}).get("primary_defects") or [])
    return {
        "case_id": case.get("case_id"),
        "locale": locale,
        "profile_id": profile_id,
        "label_source": case.get("label_source"),
        "consensus_band": case.get("consensus_band"),
        "expected_band": (case.get("expected") or {}).get("band"),
        "expected_defects": expected,
        "observed_defects": sorted_codes,
        "annotated_defects": defects,
        "gate_maturity": maturity_summary(defects),
        "cell_score": cell.get("score"),
        "contract_score": cell.get("contract_score"),
        "editorial_score": cell.get("editorial_score"),
        "cell_band": cell.get("band"),
    }


def _blank_confusion() -> dict[str, int]:
    return {"tp": 0, "fp": 0, "fn": 0, "tn": 0}


def _metric_or_none(numer: int, denom: int) -> float | None:
    if denom <= 0:
        return None
    return numer / denom


def _support_status(*, support_positive: int, support_negative: int) -> MetricStatus:
    if support_positive < MIN_SUPPORT_POSITIVE or support_negative < MIN_SUPPORT_NEGATIVE:
        return "insufficient_support"
    return "measured"


def compute_code_metrics(
    observations: list[dict[str, Any]],
    code: str,
) -> dict[str, Any]:
    """Classic confusion matrix for one defect code vs labeled expectations."""
    conf = _blank_confusion()
    by_loc = {
        "ru": {**_blank_confusion(), "support_positive": 0, "support_negative": 0},
        "en": {**_blank_confusion(), "support_positive": 0, "support_negative": 0},
    }
    false_blocks_pass = 0
    true_blocks_reject = 0

    for obs in observations:
        expected = set(obs.get("expected_defects") or [])
        observed = set(obs.get("observed_defects") or [])
        locale = str(obs.get("locale") or "ru")
        if locale not in by_loc:
            locale = "ru"
        exp = code in expected
        hit = code in observed
        band = str(obs.get("consensus_band") or "")

        if exp and hit:
            conf["tp"] += 1
            by_loc[locale]["tp"] += 1
        elif (not exp) and hit:
            conf["fp"] += 1
            by_loc[locale]["fp"] += 1
        elif exp and not hit:
            conf["fn"] += 1
            by_loc[locale]["fn"] += 1
        else:
            conf["tn"] += 1
            by_loc[locale]["tn"] += 1

        if exp:
            by_loc[locale]["support_positive"] += 1
        else:
            by_loc[locale]["support_negative"] += 1

        if hit and band == "pass" and not expected:
            false_blocks_pass += 1
        if hit and exp and band == "reject":
            true_blocks_reject += 1

    support_positive = conf["tp"] + conf["fn"]
    support_negative = conf["fp"] + conf["tn"]
    status = _support_status(
        support_positive=support_positive,
        support_negative=support_negative,
    )

    precision = _metric_or_none(conf["tp"], conf["tp"] + conf["fp"])
    recall = _metric_or_none(conf["tp"], conf["tp"] + conf["fn"])
    fpr = _metric_or_none(conf["fp"], conf["fp"] + conf["tn"])
    if status == "insufficient_support":
        precision = None
        recall = None
        fpr = None

    locale_out: dict[str, Any] = {}
    for loc, s in by_loc.items():
        loc_status: MetricStatus = _support_status(
            support_positive=s["support_positive"],
            support_negative=s["support_negative"],
        )
        if s["support_positive"] < 1 or s["support_negative"] < 1:
            loc_status = "insufficient_support"
        loc_p = _metric_or_none(s["tp"], s["tp"] + s["fp"])
        loc_r = _metric_or_none(s["tp"], s["tp"] + s["fn"])
        loc_fpr = _metric_or_none(s["fp"], s["fp"] + s["tn"])
        if loc_status == "insufficient_support":
            loc_p = loc_r = loc_fpr = None
        locale_out[loc] = {
            "support_positive": s["support_positive"],
            "support_negative": s["support_negative"],
            "true_positives": s["tp"],
            "false_positives": s["fp"],
            "true_negatives": s["tn"],
            "false_negatives": s["fn"],
            "precision": loc_p,
            "recall": loc_r,
            "false_positive_rate": loc_fpr,
            "metric_status": loc_status,
        }

    rule = get_rule(code)
    action = runtime_action_for_rule(rule)
    return {
        "code": code,
        "family": rule.family,
        "maturity": rule.maturity,
        "runtime_action": action,
        "is_unknown_code": code not in GATE_RULES,
        "support_positive": support_positive,
        "support_negative": support_negative,
        "true_positives": conf["tp"],
        "false_positives": conf["fp"],
        "true_negatives": conf["tn"],
        "false_negatives": conf["fn"],
        "precision": precision,
        "recall": recall,
        "false_positive_rate": fpr,
        "metric_status": status,
        "by_locale": locale_out,
        "shadow": {
            "would_block_if_quality_promoted": (
                false_blocks_pass + true_blocks_reject if rule.family == FAMILY_QUALITY else 0
            ),
            "would_retry_if_quality_promoted": 0,
            "false_blocks_against_labels": false_blocks_pass,
            "true_blocks_against_labels": true_blocks_reject,
        },
        "promotion_allowed_from_this_report": False,
    }


def _build_shadow(
    observations: list[dict[str, Any]], per_code: list[dict[str, Any]]
) -> dict[str, Any]:
    actual_runtime_blocked = 0
    would_block_if_any_quality = 0
    false_blocks_pass_any = 0
    true_blocks_reject_any = 0

    for obs in observations:
        annotated = obs.get("annotated_defects") or []
        expected = set(obs.get("expected_defects") or [])
        band = str(obs.get("consensus_band") or "")
        quality_hits = [d for d in annotated if d.get("gate_family") == FAMILY_QUALITY]
        blocking_hits = [d for d in annotated if d.get("gate_maturity") == MATURITY_BLOCKING]
        if blocking_hits:
            actual_runtime_blocked += 1
        if quality_hits:
            would_block_if_any_quality += 1
            if band == "pass" and not expected:
                false_blocks_pass_any += 1
            q_codes = {str(d.get("code")) for d in quality_hits}
            if band == "reject" and expected & q_codes:
                true_blocks_reject_any += 1

    worst_fp = sorted(
        (
            {
                "code": r["code"],
                "false_blocks_against_labels": r["shadow"]["false_blocks_against_labels"],
                "false_positives": r["false_positives"],
                "metric_status": r["metric_status"],
            }
            for r in per_code
            if r.get("family") == FAMILY_QUALITY
        ),
        key=lambda x: (
            -int(x["false_blocks_against_labels"]),
            -int(x["false_positives"]),
            x["code"],
        ),
    )

    return {
        "actual_runtime_blocked": actual_runtime_blocked,
        "would_block_if_quality_promoted": would_block_if_any_quality,
        "would_retry_if_quality_promoted": 0,
        "false_blocks_against_labels": false_blocks_pass_any,
        "true_blocks_against_labels": true_blocks_reject_any,
        "note": (
            "actual_runtime_blocked==0 is expected under C3.6 quality=observe policy; "
            "it is not a quality score. Primary shadow KPI: false_blocks_against_labels "
            "(pass/good cases that would be wrongly blocked if quality codes became blocking)."
        ),
        "worst_false_block_codes": worst_fp[:12],
        "per_code_false_blocks": {
            r["code"]: r["shadow"]["false_blocks_against_labels"] for r in per_code
        },
    }


def run_gate_calibration_c361(
    cases: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Evaluate golden cases → per-code calibration report (JSON SoT)."""
    cases = list(cases or bootstrap_golden_cases_c361())
    observations = [observe_case(c) for c in cases]

    all_codes: set[str] = set()
    for obs in observations:
        all_codes.update(obs["expected_defects"])
        all_codes.update(obs["observed_defects"])

    per_code = [compute_code_metrics(observations, code) for code in sorted(all_codes)]
    shadow = _build_shadow(observations, per_code)

    ru_n = sum(1 for c in cases if c.get("locale") == "ru")
    en_n = sum(1 for c in cases if c.get("locale") == "en")
    pos_labels = sum(1 for c in cases if (c.get("expected") or {}).get("primary_defects"))
    neg_labels = sum(1 for c in cases if not (c.get("expected") or {}).get("primary_defects"))
    insufficient = [r["code"] for r in per_code if r["metric_status"] == "insufficient_support"]

    human_ready = bool(cases) and all(
        str(c.get("label_source") or "") == LABEL_SOURCE_HUMAN for c in cases
    )

    return {
        "calibration_version": CALIBRATION_VERSION,
        "case_count": len(cases),
        "locale_counts": {"ru": ru_n, "en": en_n},
        "label_counts": {
            "positive_primary_defect_cases": pos_labels,
            "negative_clean_cases": neg_labels,
        },
        "locales_present": sorted({str(c.get("locale")) for c in cases}),
        "label_sources": sorted({str(c.get("label_source")) for c in cases}),
        "label_source_note": (
            "synthetic_bootstrap only — not human/editor consensus; "
            "not authorization for maturity promotion"
        ),
        "human_labels_complete": human_ready,
        "maturity_promotion_performed": False,
        "runtime_unchanged": True,
        "public_contract_unchanged": True,
        "insufficient_support_codes": insufficient,
        "min_support": {
            "positive": MIN_SUPPORT_POSITIVE,
            "negative": MIN_SUPPORT_NEGATIVE,
        },
        "observations": observations,
        "per_code": per_code,
        "shadow": shadow,
        "promotion_criteria": {
            "precision_min": 0.85,
            "recall_min": 0.70,
            "false_positive_rate_max": 0.10,
            "requires_human_labels": True,
            "requires_ru_and_en_comparable_support": True,
            "requires_review_protocol": "C3.6.2 Human Golden Set and Review Protocol",
            "synthetic_bootstrap_may_promote": False,
            "note": (
                "This report never sets promotion_allowed_from_this_report=true. "
                "Next: C3.6.2 human labeling + disagreement protocol, then live shadow."
            ),
        },
        "limitations": [
            "Labels are synthetic_bootstrap, not human/editor consensus.",
            "Baseline does not authorize maturity promotion.",
            "Results verify harness wiring and surface obvious false positives only.",
            "Thresholds and maturity remain provisional.",
            "Many codes have insufficient_support on a 14-case bootstrap.",
            "RU/EN metrics are not comparable without adequate support on both locales.",
            "actual_runtime_blocked≈0 is expected under observe-only quality policy.",
        ],
    }


def calibration_report_markdown(report: dict[str, Any]) -> str:
    """Render the same report dict used for JSON (single source of truth)."""
    shadow = report.get("shadow") or {}
    lines = [
        f"# Gate Calibration Report ({report.get('calibration_version')})",
        "",
        f"- Cases: **{report.get('case_count')}** "
        f"(RU={report.get('locale_counts', {}).get('ru')}, "
        f"EN={report.get('locale_counts', {}).get('en')})",
        f"- Label sources: `{', '.join(report.get('label_sources') or [])}`",
        f"- Positive / negative labeled cases: "
        f"{report.get('label_counts', {}).get('positive_primary_defect_cases')} / "
        f"{report.get('label_counts', {}).get('negative_clean_cases')}",
        f"- Human labels complete: **{report.get('human_labels_complete')}**",
        f"- Maturity promotion performed: **{report.get('maturity_promotion_performed')}**",
        f"- Runtime unchanged: **{report.get('runtime_unchanged')}**",
        f"- Public contract unchanged: **{report.get('public_contract_unchanged')}**",
        "",
        "## Limitations",
        "",
    ]
    for lim in report.get("limitations") or []:
        lines.append(f"- {lim}")
    lines.extend(
        [
            "",
            "## Shadow (counterfactual vs policy)",
            "",
            f"- `actual_runtime_blocked`: **{shadow.get('actual_runtime_blocked')}** "
            "(expected ~0 while quality is observe-only)",
            f"- `would_block_if_quality_promoted`: **{shadow.get('would_block_if_quality_promoted')}**",
            f"- `would_retry_if_quality_promoted`: **{shadow.get('would_retry_if_quality_promoted')}**",
            f"- `false_blocks_against_labels` (good/pass wrongly blocked): "
            f"**{shadow.get('false_blocks_against_labels')}** ← primary shadow KPI",
            f"- `true_blocks_against_labels`: **{shadow.get('true_blocks_against_labels')}**",
            "",
            f"_{shadow.get('note')}_",
            "",
            "### Worst false-block codes (pass labels)",
            "",
            "| Code | False blocks on pass | FP (all) | Metric status |",
            "|------|---------------------:|---------:|---------------|",
        ]
    )
    for row in shadow.get("worst_false_block_codes") or []:
        lines.append(
            f"| `{row['code']}` | {row['false_blocks_against_labels']} | "
            f"{row['false_positives']} | {row['metric_status']} |"
        )

    lines.extend(
        [
            "",
            "## Per-code metrics",
            "",
            "| Code | Status | +/− support | TP | FP | TN | FN | P | R | FPR | "
            "RU status | EN status | False blocks on pass |",
            "|------|--------|------------:|---:|---:|---:|---:|---|---|-----|"
            "-----------|-----------|---------------------:|",
        ]
    )

    def _fmt(x: float | None) -> str:
        return "N/A" if x is None else f"{x:.2f}"

    for row in report.get("per_code") or []:
        ru = (row.get("by_locale") or {}).get("ru") or {}
        en = (row.get("by_locale") or {}).get("en") or {}
        lines.append(
            "| `{code}` | {st} | {sp}/{sn} | {tp} | {fp} | {tn} | {fn} | {p} | {r} | {fpr} | "
            "{ru_st} | {en_st} | {fb} |".format(
                code=row.get("code"),
                st=row.get("metric_status"),
                sp=row.get("support_positive"),
                sn=row.get("support_negative"),
                tp=row.get("true_positives"),
                fp=row.get("false_positives"),
                tn=row.get("true_negatives"),
                fn=row.get("false_negatives"),
                p=_fmt(row.get("precision")),
                r=_fmt(row.get("recall")),
                fpr=_fmt(row.get("false_positive_rate")),
                ru_st=ru.get("metric_status"),
                en_st=en.get("metric_status"),
                fb=(row.get("shadow") or {}).get("false_blocks_against_labels"),
            )
        )

    insuff = report.get("insufficient_support_codes") or []
    lines.extend(
        [
            "",
            f"### Insufficient support ({len(insuff)})",
            "",
            ", ".join(f"`{c}`" for c in insuff) if insuff else "_none_",
            "",
            "## Next",
            "",
            "**C3.6.2 — Human Golden Set and Review Protocol** "
            "(manual labeling + disagreement resolution before any promotion).",
            "",
        ]
    )
    return "\n".join(lines)


def slim_report_for_baseline(report: dict[str, Any]) -> dict[str, Any]:
    """Drop bulky annotated blobs for durable baseline JSON."""
    slim = {k: v for k, v in report.items() if k != "observations"}
    slim["observations"] = [
        {
            "case_id": o.get("case_id"),
            "locale": o.get("locale"),
            "consensus_band": o.get("consensus_band"),
            "label_source": o.get("label_source"),
            "expected_defects": o.get("expected_defects"),
            "observed_defects": o.get("observed_defects"),
            "cell_score": o.get("cell_score"),
            "cell_band": o.get("cell_band"),
        }
        for o in report.get("observations") or []
    ]
    return slim
