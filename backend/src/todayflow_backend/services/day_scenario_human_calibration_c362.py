"""C3.6.2 — Adapt sealed human consensus into calibration observations (eval-only).

Reads **only** human consensus. Never mixes synthetic_bootstrap.
Does not promote maturity or change runtime.
"""

from __future__ import annotations

from typing import Any

from todayflow_backend.services.day_scenario_gate_calibration_c361 import (
    CALIBRATION_VERSION,
    LABEL_SOURCE_HUMAN,
    MIN_SUPPORT_NEGATIVE,
    MIN_SUPPORT_POSITIVE,
    _metric_or_none,
    _support_status,
)
from todayflow_backend.services.day_scenario_gate_maturity_c36 import (
    FAMILY_QUALITY,
    GATE_RULES,
    get_rule,
    runtime_action_for_rule,
)
from todayflow_backend.services.day_scenario_human_golden_c362 import (
    LABEL_SOURCE_SYNTHETIC,
    consensus_to_calibration_case,
    version_bundle,
)


def filter_human_consensus_cases(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for c in cases:
        if str(c.get("label_source") or "") == LABEL_SOURCE_SYNTHETIC:
            continue
        row = consensus_to_calibration_case(c)
        if row is None:
            continue
        # Attach observed_defects placeholder — human calibration uses labeled present/absent
        # Analyzer may be attached post-seal but is not required for label metrics.
        observed = []
        if isinstance(c.get("analyzer_attachment"), dict):
            output = c["analyzer_attachment"].get("output") or {}
            observed = list(output.get("defect_codes") or [])
        row["_observed_analyzer"] = observed
        row["_raw_case"] = c
        out.append(row)
    return out


def compute_human_code_metrics(
    calib_rows: list[dict[str, Any]],
    code: str,
) -> dict[str, Any]:
    """Confusion using human present/absent only.

    - present → positive label
    - absent → negative label
    - uncertain / not_applicable → excluded from support (not automatic absent)
    - cannot_assess cases already filtered out
    """
    tp = fp = fn = tn = 0
    by_loc = {
        "ru": {"tp": 0, "fp": 0, "fn": 0, "tn": 0, "support_positive": 0, "support_negative": 0},
        "en": {"tp": 0, "fp": 0, "fn": 0, "tn": 0, "support_positive": 0, "support_negative": 0},
    }
    excluded = 0

    for row in calib_rows:
        exp = row.get("expected") or {}
        present = set(exp.get("primary_defects") or [])
        absent = set(exp.get("absent_defects") or [])
        uncertain = set(exp.get("uncertain_defects") or [])
        na = set(exp.get("not_applicable_defects") or [])
        locale = str(row.get("locale") or "ru")
        if locale not in by_loc:
            locale = "ru"
        observed = set(row.get("_observed_analyzer") or [])

        if code in uncertain or code in na:
            excluded += 1
            continue
        if code in present:
            label_pos = True
        elif code in absent:
            label_pos = False
        else:
            # Not labeled for this code — exclude
            excluded += 1
            continue

        hit = code in observed
        if label_pos and hit:
            tp += 1
            by_loc[locale]["tp"] += 1
            by_loc[locale]["support_positive"] += 1
        elif (not label_pos) and hit:
            fp += 1
            by_loc[locale]["fp"] += 1
            by_loc[locale]["support_negative"] += 1
        elif label_pos and not hit:
            fn += 1
            by_loc[locale]["fn"] += 1
            by_loc[locale]["support_positive"] += 1
        else:
            tn += 1
            by_loc[locale]["tn"] += 1
            by_loc[locale]["support_negative"] += 1

    support_positive = tp + fn
    support_negative = fp + tn
    status = _support_status(
        support_positive=support_positive,
        support_negative=support_negative,
    )
    precision = _metric_or_none(tp, tp + fp)
    recall = _metric_or_none(tp, tp + fn)
    fpr = _metric_or_none(fp, fp + tn)
    if status == "insufficient_support":
        precision = recall = fpr = None

    locale_out: dict[str, Any] = {}
    for loc, s in by_loc.items():
        loc_status = _support_status(
            support_positive=s["support_positive"],
            support_negative=s["support_negative"],
        )
        if s["support_positive"] < 1 or s["support_negative"] < 1:
            loc_status = "insufficient_support"
        lp = _metric_or_none(s["tp"], s["tp"] + s["fp"])
        lr = _metric_or_none(s["tp"], s["tp"] + s["fn"])
        lf = _metric_or_none(s["fp"], s["fp"] + s["tn"])
        if loc_status == "insufficient_support":
            lp = lr = lf = None
        locale_out[loc] = {
            **s,
            "true_positives": s["tp"],
            "false_positives": s["fp"],
            "true_negatives": s["tn"],
            "false_negatives": s["fn"],
            "precision": lp,
            "recall": lr,
            "false_positive_rate": lf,
            "metric_status": loc_status,
        }

    rule = get_rule(code)
    return {
        "code": code,
        "family": rule.family,
        "maturity": rule.maturity,
        "runtime_action": runtime_action_for_rule(rule),
        "support_positive": support_positive,
        "support_negative": support_negative,
        "true_positives": tp,
        "false_positives": fp,
        "true_negatives": tn,
        "false_negatives": fn,
        "excluded_uncertain_or_na_or_unlabeled": excluded,
        "precision": precision,
        "recall": recall,
        "false_positive_rate": fpr,
        "metric_status": status,
        "by_locale": locale_out,
        "promotion_allowed_from_this_report": False,
        "label_source": LABEL_SOURCE_HUMAN,
        "min_support": {"positive": MIN_SUPPORT_POSITIVE, "negative": MIN_SUPPORT_NEGATIVE},
    }


def run_human_consensus_calibration_c362(
    cases: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = filter_human_consensus_cases(cases)
    codes: set[str] = set()
    for row in rows:
        exp = row.get("expected") or {}
        codes.update(exp.get("primary_defects") or [])
        codes.update(exp.get("absent_defects") or [])
        codes.update(row.get("_observed_analyzer") or [])
    # Always include known quality catalog for inventory visibility when labeled
    for c in GATE_RULES:
        if GATE_RULES[c].family == FAMILY_QUALITY:
            pass
    per_code = [compute_human_code_metrics(rows, code) for code in sorted(codes)]
    by_profile: dict[str, int] = {}
    by_locale: dict[str, int] = {}
    for row in rows:
        pt = str(row.get("profile_type") or row.get("profile_id") or "?")
        by_profile[pt] = by_profile.get(pt, 0) + 1
        loc = str(row.get("locale") or "?")
        by_locale[loc] = by_locale.get(loc, 0) + 1

    return {
        "calibration_version": f"{CALIBRATION_VERSION}+human_c362",
        "label_source": LABEL_SOURCE_HUMAN,
        "synthetic_mixed": False,
        "case_count": len(rows),
        "by_locale": by_locale,
        "by_profile_type": by_profile,
        "per_code": per_code,
        "insufficient_support_codes": [
            r["code"] for r in per_code if r["metric_status"] == "insufficient_support"
        ],
        "maturity_promotion_performed": False,
        "runtime_unchanged": True,
        "versions": version_bundle(),
        "note": (
            "Uses sealed human consensus only. uncertain/not_applicable excluded from "
            "support. acceptable_with_issues is not auto-reject. No promotions."
        ),
    }
