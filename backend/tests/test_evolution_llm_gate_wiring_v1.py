"""B1.8 — Evolution → LLM Gate wiring tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.day_content_registry_loader import clear_day_content_registry_cache
from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache, load_evolution_cd_v1
from todayflow_backend.data.evolution_product_effects_loader import clear_evolution_product_effects_cache
from todayflow_backend.data.reference_machine_loader import clear_reference_machine_cache
from todayflow_backend.services.day_model_v1_aggregator import aggregate_day_model_v1
from todayflow_backend.services.day_model_v1_content_assembler import assemble_day_content_package_v1
from todayflow_backend.services.day_model_v1_content_evaluator import (
    RECOMMENDATION_USE_WITH_CAUTION,
    evaluate_day_content_package_v1,
)
from todayflow_backend.services.day_model_v1_content_mapper import (
    map_day_model_interpretation_to_content_keys,
)
from todayflow_backend.services.day_model_v1_content_renderer import render_day_content_package_v1
from todayflow_backend.services.day_model_v1_content_resolver import (
    resolve_content_entries_from_mapping,
)
from todayflow_backend.services.day_model_v1_interpreter import interpret_day_model_v1
from todayflow_backend.services.day_model_v1_llm_call_gate import (
    CONTEXT_DEPTH_STANDARD,
    DAY_CONTENT_LLM_GATE_V1_CONTRACT,
    DAY_CONTENT_LLM_GATE_V1_KEYS,
    DECISION_CALL_LLM,
    DECISION_NO_CALL,
    MODEL_TIER_STANDARD,
    decide_day_content_llm_call_v1,
)
from todayflow_backend.services.evolution_effect_consumer_map_v1 import (
    CONSUMER_LLM_GATE,
    extract_evolution_effect_consumer_slice_v1,
)
from todayflow_backend.services.evolution_effect_runtime_policy_v1 import (
    build_evolution_effect_runtime_policy_v1,
)
from todayflow_backend.services.evolution_llm_gate_wiring_v1 import (
    DAY_CONTENT_LLM_GATE_V1_WITH_EVOLUTION_KEYS,
    EVOLUTION_LLM_GATE_TRACE_KEYS,
    apply_evolution_caps_to_llm_gate_decision_v1,
    decide_day_content_llm_call_with_evolution_v1,
    validate_evolution_llm_gate_wiring_v1,
)
from todayflow_backend.services.evolution_user_state_v1 import build_evolution_user_state_v1
from tests.test_cross_domain_machine_validation import (
    ANCHOR_NUMEROLOGY,
    ANCHOR_PLANET,
    ANCHOR_SIGN,
    ANCHOR_TAROT,
)


@pytest.fixture(autouse=True)
def _clear_caches() -> None:
    clear_reference_machine_cache()
    clear_day_content_registry_cache()
    clear_evolution_cd_cache()
    clear_evolution_product_effects_cache()
    yield
    clear_reference_machine_cache()
    clear_day_content_registry_cache()
    clear_evolution_cd_cache()
    clear_evolution_product_effects_cache()


@pytest.fixture
def cd() -> dict:
    return load_evolution_cd_v1()


@pytest.fixture
def seeker_llm_slice(cd: dict) -> dict:
    progress = {
        "confirmed_patterns": 0,
        "completed_cycles": 0,
        "reflection_events": 3,
        "active_days": 7,
        "signal_counts": {},
        "confidence": 0.4,
    }
    state = build_evolution_user_state_v1(
        user_id="user-1",
        current_stage="seeker",
        stage_started_at="2026-05-01T00:00:00Z",
        active_path_themes=["discipline"],
        completed_path_themes=[],
        progress_snapshot=progress,
        evolution_score_snapshot=50,
        last_evaluated_at="2026-06-01T09:00:00Z",
        cd=cd,
    )
    policy = build_evolution_effect_runtime_policy_v1(
        evolution_user_state=state,
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
    )
    return extract_evolution_effect_consumer_slice_v1(policy, CONSUMER_LLM_GATE)


@pytest.fixture
def architect_llm_slice(cd: dict) -> dict:
    progress = {
        "confirmed_patterns": 5,
        "completed_cycles": 3,
        "reflection_events": 21,
        "active_days": 120,
        "signal_counts": {
            "confirmed_pattern": 2,
            "weekly_goal_completed": 1,
        },
        "confidence": 0.75,
    }
    state = build_evolution_user_state_v1(
        user_id="user-1",
        current_stage="architect",
        stage_started_at="2026-05-01T00:00:00Z",
        active_path_themes=["discipline"],
        completed_path_themes=[],
        progress_snapshot=progress,
        evolution_score_snapshot=420,
        last_evaluated_at="2026-06-01T09:00:00Z",
        cd=cd,
    )
    policy = build_evolution_effect_runtime_policy_v1(
        evolution_user_state=state,
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
        source_systems_ready={
            "calendar_intelligence": True,
            "share_features": True,
        },
    )
    return extract_evolution_effect_consumer_slice_v1(policy, CONSUMER_LLM_GATE)


def _pipeline(tarot: str, numerology: str, planet: str, sign: str):
    dm = aggregate_day_model_v1(
        tarot_entity_code=tarot,
        numerology_entity_code=numerology,
        astrology_planet_code=planet,
        astrology_sign_code=sign,
    )
    interpretation = interpret_day_model_v1(dm)
    mapping = map_day_model_interpretation_to_content_keys(interpretation)
    resolution = resolve_content_entries_from_mapping(mapping)
    package = assemble_day_content_package_v1(interpretation, mapping, resolution)
    evaluation = evaluate_day_content_package_v1(package)
    render = render_day_content_package_v1(package, evaluation)
    return evaluation, render


def _call_llm_gate(evaluation: dict, render: dict) -> dict:
    evaluation = copy.deepcopy(evaluation)
    evaluation["recommendation"] = RECOMMENDATION_USE_WITH_CAUTION
    evaluation["degraded"] = True
    evaluation["issues"] = list(evaluation.get("issues") or []) + [
        "E-CONFLICT:strategy_action+tempo_slow_down"
    ]
    return decide_day_content_llm_call_v1(render, evaluation, surface="day_guidance_card")


def test_no_slice_legacy_gate_unchanged() -> None:
    evaluation, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    base = decide_day_content_llm_call_v1(render, evaluation, surface="today_hero")
    wired = decide_day_content_llm_call_with_evolution_v1(
        render,
        evaluation,
        surface="today_hero",
        evolution_slice=None,
    )

    for key in DAY_CONTENT_LLM_GATE_V1_KEYS:
        assert wired[key] == base[key]
    assert wired["evolution_slice_applied"] is False
    assert wired["cap_reason"] == "no_evolution_slice"


def test_seeker_caps_context_depth(seeker_llm_slice: dict) -> None:
    evaluation, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    base = _call_llm_gate(evaluation, render)
    assert base["decision"] == DECISION_CALL_LLM

    wired = apply_evolution_caps_to_llm_gate_decision_v1(base, seeker_llm_slice)
    assert wired["decision"] == DECISION_NO_CALL
    assert wired["evolution_slice_applied"] is True
    assert wired["evolution_context_depth_cap"] == "none"
    assert wired["allowed_context_depth"] == "none"
    assert "decision:call_llm->no_call" in wired["blocked_escalations"]


def test_seeker_blocks_or_downgrades_model_tier(seeker_llm_slice: dict) -> None:
    evaluation, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    base = _call_llm_gate(evaluation, render)
    base["allowed_model_tier"] = MODEL_TIER_STANDARD

    wired = apply_evolution_caps_to_llm_gate_decision_v1(base, seeker_llm_slice)
    assert wired["decision"] == DECISION_NO_CALL
    assert wired["evolution_model_tier_cap"] == "none"
    assert wired["allowed_model_tier"] == "none"


def test_architect_allows_larger_caps_but_does_not_force_call(
    architect_llm_slice: dict,
) -> None:
    evaluation, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    base = decide_day_content_llm_call_v1(render, evaluation, surface="today_hero")
    assert base["decision"] == DECISION_NO_CALL

    wired = apply_evolution_caps_to_llm_gate_decision_v1(base, architect_llm_slice)
    assert wired["decision"] == DECISION_NO_CALL
    assert wired["evolution_slice_applied"] is True
    assert wired["evolution_context_depth_cap"] == CONTEXT_DEPTH_STANDARD
    assert wired["evolution_model_tier_cap"] == MODEL_TIER_STANDARD
    assert wired["blocked_escalations"] == []


def test_requested_tokens_capped(architect_llm_slice: dict) -> None:
    evaluation, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    base = _call_llm_gate(evaluation, render)
    base["max_tokens"] = 999

    wired = apply_evolution_caps_to_llm_gate_decision_v1(base, architect_llm_slice)
    assert wired["decision"] == DECISION_CALL_LLM
    assert wired["max_tokens"] == wired["evolution_token_cap"]
    assert wired["max_tokens"] < 999
    assert any(entry.startswith("max_tokens:") for entry in wired["blocked_escalations"])


def test_invalid_slice_ignored_with_trace(seeker_llm_slice: dict) -> None:
    evaluation, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    base = _call_llm_gate(evaluation, render)
    invalid = copy.deepcopy(seeker_llm_slice)
    invalid["effect_limits"] = "not-an-object"

    wired = apply_evolution_caps_to_llm_gate_decision_v1(base, invalid)
    assert wired["decision"] == base["decision"]
    assert wired["allowed_context_depth"] == base["allowed_context_depth"]
    assert wired["allowed_model_tier"] == base["allowed_model_tier"]
    assert wired["max_tokens"] == base["max_tokens"]
    assert wired["evolution_slice_applied"] is False
    assert wired["cap_reason"] == "ignored:invalid_slice_payload"


def test_full_policy_rejected_not_accepted(cd: dict) -> None:
    evaluation, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    base = _call_llm_gate(evaluation, render)
    state = build_evolution_user_state_v1(
        user_id="user-1",
        current_stage="seeker",
        stage_started_at="2026-05-01T00:00:00Z",
        active_path_themes=["discipline"],
        completed_path_themes=[],
        progress_snapshot={
            "confirmed_patterns": 0,
            "completed_cycles": 0,
            "reflection_events": 3,
            "active_days": 7,
            "signal_counts": {},
            "confidence": 0.4,
        },
        evolution_score_snapshot=50,
        last_evaluated_at="2026-06-01T09:00:00Z",
        cd=cd,
    )
    full_policy = build_evolution_effect_runtime_policy_v1(
        evolution_user_state=state,
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
    )

    wired = apply_evolution_caps_to_llm_gate_decision_v1(base, full_policy)
    assert wired == {**base, **_evolution_trace_defaults(applied=False, cap_reason="ignored:full_policy_not_accepted")}


def test_evolution_cannot_turn_no_call_into_call_llm(architect_llm_slice: dict) -> None:
    evaluation, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    base = decide_day_content_llm_call_v1(render, evaluation, surface="today_hero")
    assert base["decision"] == DECISION_NO_CALL

    wired = apply_evolution_caps_to_llm_gate_decision_v1(base, architect_llm_slice)
    assert wired["decision"] == DECISION_NO_CALL


def test_trace_fields_present(seeker_llm_slice: dict) -> None:
    evaluation, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    base = _call_llm_gate(evaluation, render)
    wired = apply_evolution_caps_to_llm_gate_decision_v1(base, seeker_llm_slice)

    for key in EVOLUTION_LLM_GATE_TRACE_KEYS:
        assert key in wired
    assert validate_evolution_llm_gate_wiring_v1(wired) == []


def test_output_shape_stable_with_evolution_trace(seeker_llm_slice: dict) -> None:
    evaluation, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    wired = decide_day_content_llm_call_with_evolution_v1(
        render,
        evaluation,
        surface="today_hero",
        evolution_slice=seeker_llm_slice,
    )

    assert set(wired.keys()) == DAY_CONTENT_LLM_GATE_V1_WITH_EVOLUTION_KEYS
    assert wired["contract_version"] == DAY_CONTENT_LLM_GATE_V1_CONTRACT
    assert validate_evolution_llm_gate_wiring_v1(wired) == []


def _evolution_trace_defaults(*, applied: bool, cap_reason: str) -> dict:
    return {
        "evolution_slice_applied": applied,
        "evolution_context_depth_cap": None,
        "evolution_model_tier_cap": None,
        "evolution_token_cap": None,
        "cap_reason": cap_reason,
        "blocked_escalations": [],
    }
