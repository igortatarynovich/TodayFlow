"""C3.6.1 — Gate calibration harness (eval-only)."""

from __future__ import annotations

import copy
import json

from todayflow_backend.services.day_scenario_gate_calibration_c361 import (
    CALIBRATION_VERSION,
    LABEL_SOURCE_SYNTHETIC,
    MIN_SUPPORT_NEGATIVE,
    MIN_SUPPORT_POSITIVE,
    bootstrap_golden_cases_c361,
    calibration_report_markdown,
    compute_code_metrics,
    observe_case,
    resolve_case_native,
    run_gate_calibration_c361,
    slim_report_for_baseline,
)
from todayflow_backend.services.day_scenario_gate_maturity_c36 import (
    FAMILY_QUALITY,
    GATE_RULES,
    MATURITY_BLOCKING,
)


def _toy_obs(*, case_id: str, locale: str, expected: list[str], observed: list[str], band: str):
    return {
        "case_id": case_id,
        "locale": locale,
        "expected_defects": expected,
        "observed_defects": observed,
        "consensus_band": band,
        "annotated_defects": [
            {
                "code": c,
                "gate_family": FAMILY_QUALITY,
                "gate_maturity": "experimental",
                "runtime_action": "score_only",
            }
            for c in observed
        ],
    }


def test_tp_fp_tn_fn_counts_correctly():
    obs = [
        _toy_obs(case_id="p1", locale="ru", expected=["A"], observed=["A"], band="reject"),
        _toy_obs(case_id="p2", locale="ru", expected=["A"], observed=[], band="reject"),
        _toy_obs(case_id="n1", locale="ru", expected=[], observed=["A"], band="pass"),
        _toy_obs(case_id="n2", locale="ru", expected=[], observed=[], band="pass"),
        _toy_obs(case_id="n3", locale="en", expected=[], observed=[], band="pass"),
    ]
    row = compute_code_metrics(obs, "A")
    assert row["true_positives"] == 1
    assert row["false_negatives"] == 1
    assert row["false_positives"] == 1
    assert row["true_negatives"] == 2
    assert row["support_positive"] == 2
    assert row["support_negative"] == 3


def test_precision_null_when_zero_denominator():
    obs = [
        _toy_obs(case_id="p1", locale="ru", expected=["A"], observed=[], band="reject"),
        _toy_obs(case_id="p2", locale="ru", expected=["A"], observed=[], band="reject"),
        _toy_obs(case_id="n1", locale="ru", expected=[], observed=[], band="pass"),
        _toy_obs(case_id="n2", locale="en", expected=[], observed=[], band="pass"),
    ]
    row = compute_code_metrics(obs, "A")
    assert row["support_positive"] >= MIN_SUPPORT_POSITIVE
    assert row["support_negative"] >= MIN_SUPPORT_NEGATIVE
    assert row["precision"] is None
    assert row["recall"] == 0.0
    assert row["false_positive_rate"] == 0.0


def test_recall_null_without_positive_support():
    obs = [
        _toy_obs(case_id="n1", locale="ru", expected=[], observed=["A"], band="pass"),
        _toy_obs(case_id="n2", locale="ru", expected=[], observed=[], band="pass"),
        _toy_obs(case_id="n3", locale="en", expected=[], observed=[], band="pass"),
    ]
    row = compute_code_metrics(obs, "A")
    assert row["support_positive"] == 0
    assert row["metric_status"] == "insufficient_support"
    assert row["recall"] is None
    assert row["precision"] is None
    assert row["false_positive_rate"] is None


def test_fpr_null_without_negative_support():
    obs = [
        _toy_obs(case_id="p1", locale="ru", expected=["A"], observed=["A"], band="reject"),
        _toy_obs(case_id="p2", locale="en", expected=["A"], observed=["A"], band="reject"),
    ]
    row = compute_code_metrics(obs, "A")
    assert row["support_negative"] == 0
    assert row["metric_status"] == "insufficient_support"
    assert row["false_positive_rate"] is None
    assert row["precision"] is None
    assert row["recall"] is None


def test_ru_en_counted_separately_and_aggregate_does_not_hide_locale_fp():
    obs = [
        _toy_obs(case_id="p-ru", locale="ru", expected=["A"], observed=["A"], band="reject"),
        _toy_obs(case_id="p-en", locale="en", expected=["A"], observed=["A"], band="reject"),
        _toy_obs(case_id="n-ru", locale="ru", expected=[], observed=[], band="pass"),
        _toy_obs(case_id="n-en", locale="en", expected=[], observed=["A"], band="pass"),
        _toy_obs(case_id="n-en2", locale="en", expected=[], observed=[], band="pass"),
        _toy_obs(case_id="n-ru2", locale="ru", expected=[], observed=[], band="pass"),
    ]
    row = compute_code_metrics(obs, "A")
    assert row["by_locale"]["en"]["false_positives"] == 1
    assert row["by_locale"]["ru"]["false_positives"] == 0
    assert row["false_positives"] == 1


def test_quality_rules_do_not_change_runtime_and_no_auto_promote():
    report = run_gate_calibration_c361()
    assert report["runtime_unchanged"] is True
    assert report["maturity_promotion_performed"] is False
    assert report["public_contract_unchanged"] is True
    # Sealed C3.6.2 pilot evidence promoted three scene-quality rules to
    # blocking/retry (commit "Promote scene quality gates"). Calibration
    # itself still never auto-promotes; all other quality rules stay observe-only.
    promoted = {"SCENE_ABSTRACT", "SCENE_CLONE", "SCENE_MISSING_EVERYDAY"}
    for row in report["per_code"]:
        assert row["promotion_allowed_from_this_report"] is False
        if row["family"] == FAMILY_QUALITY:
            if row["code"] in promoted:
                assert row["runtime_action"] in {"retry", "reject_story"}
            else:
                assert row["runtime_action"] == "score_only"


def test_calibration_does_not_mutate_maturity_registry():
    before = {k: (v.maturity, v.family) for k, v in GATE_RULES.items()}
    _ = run_gate_calibration_c361()
    after = {k: (v.maturity, v.family) for k, v in GATE_RULES.items()}
    assert before == after


def test_synthetic_labels_cannot_auto_promote():
    report = run_gate_calibration_c361()
    assert LABEL_SOURCE_SYNTHETIC in report["label_sources"]
    assert report["promotion_criteria"]["synthetic_bootstrap_may_promote"] is False
    assert all(r["promotion_allowed_from_this_report"] is False for r in report["per_code"])


def test_json_and_markdown_same_source_of_truth():
    report = run_gate_calibration_c361()
    md = calibration_report_markdown(report)
    slim = slim_report_for_baseline(report)
    assert report["calibration_version"] in md
    assert str(report["shadow"]["false_blocks_against_labels"]) in md
    assert slim["case_count"] == report["case_count"]
    assert slim["shadow"] == report["shadow"]
    blob = json.dumps(slim, sort_keys=True)
    assert "false_blocks_against_labels" in blob


def test_deterministic_rerun():
    a = slim_report_for_baseline(run_gate_calibration_c361())
    b = slim_report_for_baseline(run_gate_calibration_c361())
    assert a["case_count"] == b["case_count"]
    assert a["insufficient_support_codes"] == b["insufficient_support_codes"]
    assert a["shadow"]["false_blocks_against_labels"] == b["shadow"]["false_blocks_against_labels"]
    assert [r["code"] for r in a["per_code"]] == [r["code"] for r in b["per_code"]]
    for ra, rb in zip(a["per_code"], b["per_code"]):
        assert ra["true_positives"] == rb["true_positives"]
        assert ra["false_positives"] == rb["false_positives"]
        assert ra["metric_status"] == rb["metric_status"]


def test_unknown_defect_code_in_report_but_not_blocking():
    obs = [
        _toy_obs(case_id="p1", locale="ru", expected=["BRAND_NEW_X"], observed=["BRAND_NEW_X"], band="reject"),
        _toy_obs(case_id="p2", locale="en", expected=["BRAND_NEW_X"], observed=["BRAND_NEW_X"], band="reject"),
        _toy_obs(case_id="n1", locale="ru", expected=[], observed=[], band="pass"),
        _toy_obs(case_id="n2", locale="en", expected=[], observed=[], band="pass"),
    ]
    row = compute_code_metrics(obs, "BRAND_NEW_X")
    assert row["is_unknown_code"] is True
    assert row["runtime_action"] == "score_only"
    assert row["promotion_allowed_from_this_report"] is False


def test_shadow_semantics_distinguish_policy_from_quality():
    report = run_gate_calibration_c361()
    shadow = report["shadow"]
    assert "actual_runtime_blocked" in shadow
    assert "would_block_if_quality_promoted" in shadow
    assert "would_retry_if_quality_promoted" in shadow
    assert "false_blocks_against_labels" in shadow
    assert "true_blocks_against_labels" in shadow
    # Post-promotion (sealed C3.6.2): the three scene-quality rules are
    # blocking at runtime, so 12 of the 14 synthetic golden cases with those
    # defects count as actually blocked — this is the promotion working as
    # intended, not shadow drift.
    assert shadow["actual_runtime_blocked"] == 12


def test_bootstrap_inventory():
    cases = bootstrap_golden_cases_c361()
    assert len(cases) == 14
    assert sum(1 for c in cases if c["locale"] == "ru") >= 1
    assert sum(1 for c in cases if c["locale"] == "en") >= 1
    assert all(c["label_source"] == LABEL_SOURCE_SYNTHETIC for c in cases)
    report = run_gate_calibration_c361()
    assert report["calibration_version"] == CALIBRATION_VERSION
    assert report["insufficient_support_codes"]


def test_resolve_and_observe_smoke():
    cases = {c["case_id"]: c for c in bootstrap_golden_cases_c361()}
    assert resolve_case_native(cases["gs-c361-good-ru"]).get("scenes")
    obs = observe_case(cases["gs-c361-neg-closure-missing-ru"])
    assert "CLOSURE_MISSING" in obs["observed_defects"]
