"""C3.6.2 — Human golden review protocol tests (eval-only)."""

from __future__ import annotations

import copy
import json

from todayflow_backend.services.day_scenario_gate_maturity_c36 import (
    FAMILY_QUALITY,
    GATE_RULES,
    MATURITY_BLOCKING,
    runtime_action_for_rule,
)
from todayflow_backend.services.day_scenario_human_calibration_c362 import (
    compute_human_code_metrics,
    filter_human_consensus_cases,
    run_human_consensus_calibration_c362,
)
from todayflow_backend.services.day_scenario_human_golden_c362 import (
    GOLDEN_CONTRACT_VERSION,
    LABEL_SOURCE_HUMAN,
    LABEL_SOURCE_SYNTHETIC,
    RUBRIC_VERSION,
    append_reviewer_submission,
    apply_adjudication,
    attach_analyzer_after_seal,
    build_consensus,
    build_human_case_shell,
    consensus_to_calibration_case,
    detect_duplicate_scenario_hashes,
    example_review_cycle_fixture,
    export_blind_review_packet,
    new_neutral_case_id,
    scenario_hash,
    validate_reviewer_submission,
    verify_case_integrity,
    version_bundle,
)
from todayflow_backend.services.day_scenario_review_agreement_c362 import (
    agreement_report_for_case,
    reviews_require_adjudication,
)


def _mini_scenario(**overrides):
    base = {
        "conflict": {"title": "T", "force_a": "a", "force_b": "b"},
        "scenes": [{"scene_id": "s1", "setup": "Concrete chat reply at 21:40."}],
    }
    base.update(overrides)
    return base


def _case(**kw):
    return build_human_case_shell(
        case_id=kw.pop("case_id", new_neutral_case_id(seed="t")),
        scenario=kw.pop("scenario", _mini_scenario()),
        locale=kw.pop("locale", "en"),
        profile_type=kw.pop("profile_type", "smooth_conflict"),
        evidence_depth=kw.pop("evidence_depth", "general"),
        source_type=kw.pop("source_type", "curated"),
        **kw,
    )


def _submission(case, reviewer_id, band="pass", defects=None, **ver_overrides):
    defs = defects or {
        "SCENE_ABSTRACT": {"presence": "absent", "severity": None, "rationale": "ok"},
    }
    body = {
        "case_id": case["case_id"],
        "scenario_hash": case["scenario_hash"],
        "reviewer_id": reviewer_id,
        "overall_band": band,
        "defects": defs,
        **version_bundle(),
    }
    body.update(ver_overrides)
    return body


def test_blind_export_hides_analyzer_and_synthetic_expected():
    dirty = _mini_scenario()
    dirty["editorial_meta"] = {
        "editorial_defects": [{"code": "SCENE_ABSTRACT"}],
        "editorial_score": 0.2,
        "gate_maturity": {"policy": "blocking"},
    }
    case = _case(scenario=dirty)
    case["expected"] = {"primary_defects": ["SCENE_ABSTRACT"]}
    case["mutation_id"] = "clone_scene_into_second"
    case["negative_id"] = "abstract_scenes"
    packet = export_blind_review_packet(case)
    blob = json.dumps(packet)
    assert "editorial_defects" not in blob
    assert "gate_maturity" not in blob
    assert "editorial_score" not in blob
    assert "mutation_id" not in packet
    assert "negative_id" not in packet
    assert "expected" not in packet
    assert "primary_defects" not in blob
    assert packet["instructions"]["blind"] is True


def test_blind_export_redacts_private_profile_facts():
    scen = _mini_scenario(
        leak={"birth_date": "1990-03-15", "latitude": 55.75, "email": "a@b.com"}
    )
    case = _case(scenario=scen)
    packet = export_blind_review_packet(case)
    blob = json.dumps(packet)
    assert "1990-03-15" not in blob
    assert "55.75" not in blob
    assert "a@b.com" not in blob
    assert "[redacted]" in blob


def test_two_reviewers_independent_and_history_immutable():
    case = _case()
    case = append_reviewer_submission(case, _submission(case, "a"))
    hist1 = copy.deepcopy(case["review_history"])
    case = append_reviewer_submission(case, _submission(case, "b"))
    assert len(case["reviewers"]) == 2
    assert case["review_history"][: len(hist1)] == hist1
    assert case["review_history"][0]["event"] == "reviewer_submission"


def test_consensus_requires_quorum():
    case = _case()
    case = append_reviewer_submission(case, _submission(case, "a"))
    try:
        build_consensus(case)
        assert False, "expected quorum error"
    except ValueError as e:
        assert "quorum" in str(e)


def test_disagreement_requires_adjudication():
    case = _case()
    case = append_reviewer_submission(case, _submission(case, "a", band="pass"))
    case = append_reviewer_submission(case, _submission(case, "b", band="reject"))
    assert case["review_status"] == "needs_adjudication"
    assert reviews_require_adjudication(case["reviewers"]) is True
    try:
        build_consensus(case)
        assert False
    except ValueError as e:
        assert "adjudication" in str(e)
    case = apply_adjudication(
        case,
        adjudicator_id="adj1",
        overall_band="acceptable_with_issues",
        defects={"SCENE_ABSTRACT": {"presence": "present", "severity": "minor"}},
        rationale="Borderline but shippable",
        overrides=[{"field": "overall_band", "from": "split", "to": "acceptable_with_issues"}],
    )
    sealed = build_consensus(case)
    assert sealed["final_consensus"]["source"] == "adjudication"
    assert sealed["review_status"] == "sealed"


def test_uncertain_not_auto_absent_and_na_not_negative_support():
    rows = [
        {
            "locale": "en",
            "profile_type": "deep",
            "expected": {
                "primary_defects": [],
                "absent_defects": [],
                "uncertain_defects": ["SCENE_ABSTRACT"],
                "not_applicable_defects": ["CHORUS_ROLE_DRIFT"],
            },
            "_observed_analyzer": ["SCENE_ABSTRACT"],
        },
        {
            "locale": "en",
            "profile_type": "deep",
            "expected": {
                "primary_defects": ["SCENE_ABSTRACT"],
                "absent_defects": ["CHORUS_ROLE_DRIFT"],
                "uncertain_defects": [],
                "not_applicable_defects": [],
            },
            "_observed_analyzer": ["SCENE_ABSTRACT"],
        },
        {
            "locale": "ru",
            "profile_type": "general",
            "expected": {
                "primary_defects": [],
                "absent_defects": ["SCENE_ABSTRACT"],
                "uncertain_defects": [],
                "not_applicable_defects": [],
            },
            "_observed_analyzer": [],
        },
        {
            "locale": "ru",
            "profile_type": "general",
            "expected": {
                "primary_defects": [],
                "absent_defects": ["SCENE_ABSTRACT"],
                "uncertain_defects": [],
                "not_applicable_defects": [],
            },
            "_observed_analyzer": [],
        },
    ]
    m = compute_human_code_metrics(rows, "SCENE_ABSTRACT")
    # first row excluded (uncertain) — not counted as FP
    assert m["false_positives"] == 0
    assert m["true_positives"] == 1
    assert m["true_negatives"] == 2
    na = compute_human_code_metrics(rows, "CHORUS_ROLE_DRIFT")
    # N/A excluded; one absent → support_negative may be 1 only from second row's absent... 
    # second has absent CHORUS; first N/A excluded; others unlabeled for CHORUS → excluded
    assert na["excluded_uncertain_or_na_or_unlabeled"] >= 1


def test_cannot_assess_excluded_from_calibration():
    case = _case()
    case = append_reviewer_submission(case, _submission(case, "a", band="cannot_assess"))
    case = append_reviewer_submission(case, _submission(case, "b", band="cannot_assess"))
    # agreement → consensus without adj
    sealed = build_consensus(case)
    assert consensus_to_calibration_case(sealed) is None
    assert filter_human_consensus_cases([sealed]) == []


def test_calibration_uses_consensus_not_single_review():
    case = _case()
    case = append_reviewer_submission(case, _submission(case, "a", band="pass"))
    case = append_reviewer_submission(
        case,
        _submission(
            case,
            "b",
            band="reject",
            defects={"SCENE_ABSTRACT": {"presence": "present", "severity": "severe"}},
        ),
    )
    case = apply_adjudication(
        case,
        adjudicator_id="adj",
        overall_band="pass",
        defects={"SCENE_ABSTRACT": {"presence": "absent"}},
        rationale="B over-called abstract",
    )
    sealed = build_consensus(case)
    row = consensus_to_calibration_case(sealed)
    assert row is not None
    assert row["expected"]["primary_defects"] == []
    assert "SCENE_ABSTRACT" in row["expected"]["absent_defects"]
    # Single reviewer B would have disagreed — consensus wins


def test_version_mismatch_detected():
    case = _case()
    bad = _submission(case, "a", rubric_version="old-rubric")
    errs = validate_reviewer_submission(bad, case=case)
    assert any("version_mismatch:rubric_version" == e for e in errs)


def test_duplicate_scenario_hash_detected():
    s = _mini_scenario()
    a = _case(case_id="hg-1", scenario=s)
    b = _case(case_id="hg-2", scenario=copy.deepcopy(s))
    assert a["scenario_hash"] == b["scenario_hash"]
    dups = detect_duplicate_scenario_hashes([a, b])
    assert dups


def test_scenario_change_after_review_detected():
    case = _case()
    case = append_reviewer_submission(case, _submission(case, "a"))
    case["scenario"]["scenes"][0]["setup"] = "CHANGED AFTER REVIEW"
    errs = verify_case_integrity(case)
    assert "scenario_hash_drift" in errs


def test_no_maturity_or_runtime_change_and_no_auto_promote():
    before = {k: (v.maturity, v.family, runtime_action_for_rule(v)) for k, v in GATE_RULES.items()}
    _ = example_review_cycle_fixture()
    after = {k: (v.maturity, v.family, runtime_action_for_rule(v)) for k, v in GATE_RULES.items()}
    assert before == after
    # Unpromoted quality stays observe-only; C3.6.3+ may mark selected quality as blocking.
    for code, rule in GATE_RULES.items():
        if rule.family != FAMILY_QUALITY:
            continue
        if rule.maturity == MATURITY_BLOCKING:
            assert runtime_action_for_rule(rule) in {"retry", "reject_story"}
        else:
            assert runtime_action_for_rule(rule) == "score_only"


def test_analyzer_only_after_seal():
    case = _case()
    case = append_reviewer_submission(case, _submission(case, "a"))
    case = append_reviewer_submission(case, _submission(case, "b"))
    try:
        attach_analyzer_after_seal(case, {"defect_codes": ["SCENE_ABSTRACT"]})
        assert False
    except ValueError as e:
        assert "sealed" in str(e)
    sealed = build_consensus(case)
    sealed = attach_analyzer_after_seal(sealed, {"defect_codes": []})
    assert sealed["analyzer_attachment"] is not None


def test_synthetic_never_mixed_into_human_calibration():
    syn = {
        "label_source": LABEL_SOURCE_SYNTHETIC,
        "final_consensus": {"overall_band": "reject", "defects": {}},
    }
    assert consensus_to_calibration_case(syn) is None
    assert filter_human_consensus_cases([syn]) == []


def test_locale_and_profile_splits_in_human_calibration():
    fixture = example_review_cycle_fixture()
    case_en = fixture["case"]
    case_ru = _case(case_id=new_neutral_case_id(seed="ru"), locale="ru", profile_type="no_birth_time")
    case_ru = append_reviewer_submission(case_ru, _submission(case_ru, "a"))
    case_ru = append_reviewer_submission(case_ru, _submission(case_ru, "b"))
    case_ru = build_consensus(case_ru)
    report = run_human_consensus_calibration_c362([case_en, case_ru])
    assert report["by_locale"].get("en", 0) >= 1
    assert report["by_locale"].get("ru", 0) >= 1
    assert report["by_profile_type"]
    assert report["synthetic_mixed"] is False
    assert report["maturity_promotion_performed"] is False


def test_deterministic_example_cycle_and_versions():
    a = example_review_cycle_fixture()
    b = example_review_cycle_fixture()
    assert a["case"]["scenario_hash"] == b["case"]["scenario_hash"]
    assert a["case"]["final_consensus"]["overall_band"] == b["case"]["final_consensus"]["overall_band"]
    assert a["case"]["golden_contract_version"] == GOLDEN_CONTRACT_VERSION
    assert a["blind_packet"]["rubric_version"] == RUBRIC_VERSION
    assert a["calibration_row"]["label_source"] == LABEL_SOURCE_HUMAN


def test_agreement_report_fields():
    case = _case()
    case = append_reviewer_submission(case, _submission(case, "a"))
    case = append_reviewer_submission(case, _submission(case, "b"))
    rep = agreement_report_for_case(case)
    assert rep["exact_overall_agreement"] is True
    assert rep["requires_adjudication"] is False
    assert "cohens_kappa_defect_presence" in rep
