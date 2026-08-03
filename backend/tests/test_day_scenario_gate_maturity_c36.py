"""C3.6 / C3.6.3 — Gate maturity: analysis vs runtime policy."""

from __future__ import annotations

from todayflow_backend.services.day_scenario_editorial_gate_c31 import (
    CRITICAL_DEFECTS,
    DEFECT_SCENE_ABSTRACT,
    DEFECT_SCENE_CLONE,
    DEFECT_SCENE_MISSING_EVERYDAY,
    DEFECT_SCENE_UNIVERSAL_ADVICE,
)
from todayflow_backend.services.day_scenario_gate_maturity_c36 import (
    FAMILY_HARD,
    FAMILY_QUALITY,
    MATURITY_ADVISORY,
    MATURITY_BLOCKING,
    MATURITY_CANDIDATE_BLOCKING,
    MATURITY_EXPERIMENTAL,
    annotate_defects_with_maturity,
    get_rule,
    is_hard_native_validate_error,
    is_hard_scenario_validate_error,
    should_downgrade_general,
    should_reject_story,
    should_retry_defects,
)
from todayflow_backend.services.day_scenario_personalization_c33 import (
    DEFECT_CLAIM_WITHOUT_EVIDENCE,
    DEFECT_EVIDENCE_ORPHAN,
    DEFECT_PROFILE_FACT_LEAK,
)

# C3.6.3 sealed-pilot promotions (quality family, blocking maturity).
PROMOTED_QUALITY_BLOCKING = frozenset(
    {
        DEFECT_SCENE_ABSTRACT,
        DEFECT_SCENE_CLONE,
        DEFECT_SCENE_MISSING_EVERYDAY,
        "ASTRO_JARGON_BARE",
    }
)


def test_unpromoted_editorial_critical_codes_remain_observe_only():
    for code in CRITICAL_DEFECTS:
        if code in PROMOTED_QUALITY_BLOCKING:
            continue
        if code == DEFECT_SCENE_UNIVERSAL_ADVICE:
            rule = get_rule(code)
            assert rule.maturity == MATURITY_CANDIDATE_BLOCKING
            assert not should_retry_defects([{"code": code}])
            continue
        rule = get_rule(code)
        assert rule.family == FAMILY_QUALITY
        assert rule.maturity in {MATURITY_EXPERIMENTAL, MATURITY_ADVISORY, MATURITY_CANDIDATE_BLOCKING}
        assert not should_retry_defects([{"code": code}])
        assert not should_reject_story([{"code": code}])
        assert not should_downgrade_general([{"code": code}])


def test_promoted_scene_quality_codes_retry_via_maturity():
    for code in PROMOTED_QUALITY_BLOCKING:
        rule = get_rule(code)
        assert rule.family == FAMILY_QUALITY
        assert rule.maturity == MATURITY_BLOCKING
        assert should_retry_defects([{"code": code}])
        # Prefer retry while attempts remain; reject_story action only when no retry flag.
        assert not should_reject_story([{"code": code}])
        assert not should_downgrade_general([{"code": code}])


def test_chorus_semantic_duplication_is_candidate_blocking_observe_only():
    rule = get_rule("CHORUS_SEMANTIC_DUPLICATION")
    assert rule.family == FAMILY_QUALITY
    assert rule.maturity == MATURITY_CANDIDATE_BLOCKING
    assert not should_retry_defects([{"code": "CHORUS_SEMANTIC_DUPLICATION"}])
    assert not should_reject_story([{"code": "CHORUS_SEMANTIC_DUPLICATION"}])


def test_soft_personalization_is_advisory_no_runtime_control():
    d = annotate_defects_with_maturity(
        [{"code": DEFECT_CLAIM_WITHOUT_EVIDENCE, "field": "x", "message": "m"}]
    )[0]
    assert d["gate_family"] == FAMILY_QUALITY
    assert d["gate_maturity"] == MATURITY_ADVISORY
    assert d["runtime_action"] == "score_only"
    assert not should_retry_defects([d])
    assert not should_downgrade_general([d])


def test_profile_fact_leak_rejects_without_quality_retry():
    d = annotate_defects_with_maturity(
        [{"code": DEFECT_PROFILE_FACT_LEAK, "field": "setup", "message": "leak"}]
    )[0]
    assert d["gate_family"] == FAMILY_HARD
    assert d["gate_maturity"] == MATURITY_BLOCKING
    assert d["runtime_action"] == "reject_story"
    assert not should_retry_defects([d])
    assert should_reject_story([d])


def test_evidence_orphan_is_hard_blocking():
    assert should_retry_defects([{"code": DEFECT_EVIDENCE_ORPHAN}])


def test_scene_abstract_retries_when_promoted():
    defects = [
        {
            "code": DEFECT_SCENE_ABSTRACT,
            "severity": "critical",
            "field": "scenes[0].setup",
            "message": "abstract",
        }
    ]
    annotated = annotate_defects_with_maturity(defects)
    assert annotated[0]["runtime_action"] == "retry"
    assert should_retry_defects(annotated)


def test_hard_scenario_validate_markers():
    assert is_hard_scenario_validate_error("scenes_empty")
    assert not is_hard_scenario_validate_error("prop_color_origin_not_in_scenes")
    assert not is_hard_scenario_validate_error("conflict_opposing_forces_incomplete")
    assert not is_hard_scenario_validate_error("prop_color_without_origin_scene")
    assert is_hard_scenario_validate_error("conflict_opposing_forces_not_dict")
    # v3.1 seed-kill — must hard-block LLM accept / trigger retry
    assert is_hard_scenario_validate_error("conflict.short_name:invented_bank_binary")
    assert is_hard_scenario_validate_error("chorus:seed_paste_bridge")
    assert is_hard_scenario_validate_error("conflict_short_name_is_sky_fact")
    assert is_hard_scenario_validate_error(
        "verbatim_seed_leak:'тащить старое или отпустить'@conflict.short_name+chorus.day_number.voice"
    )
    assert is_hard_scenario_validate_error("scene_serves_conflict_not_opaque:scene.relationships")


def test_seed_kill_codes_are_hard_retry():
    from todayflow_backend.services.day_scenario_editorial_gate_c31 import (
        DEFECT_SEED_BANK_BINARY_SHORT_NAME,
        DEFECT_SEED_CHORUS_PASTE,
    )

    for code in (DEFECT_SEED_BANK_BINARY_SHORT_NAME, DEFECT_SEED_CHORUS_PASTE):
        annotated = annotate_defects_with_maturity([{"code": code, "field": "x", "message": "m"}])
        assert annotated[0]["gate_family"] == "hard"
        assert annotated[0]["gate_maturity"] == MATURITY_BLOCKING
        assert annotated[0]["runtime_action"] == "retry"
        assert should_retry_defects(annotated)
        assert not should_reject_story(annotated)  # reject only after retries exhausted

def test_hard_native_validate_markers():
    assert is_hard_native_validate_error("unknown_evidence:foo")
    assert is_hard_native_validate_error("legacy_keys:expect")
    assert is_hard_native_validate_error("orphan_prop_goal:scene_x")
    assert is_hard_native_validate_error("scenes_too_few")
    assert is_hard_native_validate_error("scene_missing_setup:s1")
    assert not is_hard_native_validate_error("scenes_too_many")
    assert not is_hard_native_validate_error("day_card_missing_conflict_link")
    assert not is_hard_native_validate_error("scene_missing_conflict_link:s1")
    assert not is_hard_native_validate_error("unrelated_soft_check")
    # Subjective chorus check must not hard-block (quality analyzer owns it).
    assert not is_hard_native_validate_error("parallel_forecast:day_card")


def test_unknown_code_defaults_to_experimental_observe():
    d = annotate_defects_with_maturity([{"code": "BRAND_NEW_HEURISTIC"}])[0]
    assert d["gate_maturity"] == MATURITY_EXPERIMENTAL
    assert d["runtime_action"] == "score_only"
