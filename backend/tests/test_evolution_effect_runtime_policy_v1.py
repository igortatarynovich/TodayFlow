"""B1.6 — Evolution effect runtime policy tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache, load_evolution_cd_v1
from todayflow_backend.data.evolution_product_effects_loader import (
    clear_evolution_product_effects_cache,
    get_stage_product_effects,
)
from todayflow_backend.services.evolution_effect_runtime_policy_v1 import (
    EVOLUTION_EFFECT_RUNTIME_POLICY_V1_CONTRACT,
    EVOLUTION_EFFECT_RUNTIME_POLICY_V1_KEYS,
    POLICY_RESULT_CREATED,
    POLICY_RESULT_REJECTED,
    build_evolution_effect_runtime_policy_v1,
    try_build_evolution_effect_runtime_policy_v1,
    validate_evolution_effect_runtime_policy_v1,
)
from todayflow_backend.services.evolution_user_state_v1 import build_evolution_user_state_v1


@pytest.fixture(autouse=True)
def _clear_caches() -> None:
    clear_evolution_cd_cache()
    clear_evolution_product_effects_cache()
    yield
    clear_evolution_cd_cache()
    clear_evolution_product_effects_cache()


@pytest.fixture
def cd() -> dict:
    return load_evolution_cd_v1()


@pytest.fixture
def full_progress() -> dict:
    return {
        "confirmed_patterns": 5,
        "completed_cycles": 2,
        "reflection_events": 10,
        "active_days": 30,
        "signal_counts": {
            "ritual_streak_confirmed": 3,
            "evening_reflection_confirmed": 5,
        },
        "confidence": 0.8,
    }


@pytest.fixture
def low_progress() -> dict:
    return {
        "confirmed_patterns": 0,
        "completed_cycles": 0,
        "reflection_events": 0,
        "active_days": 1,
        "signal_counts": {},
        "confidence": 0.2,
    }


def _state(
    *,
    stage: str,
    progress: dict,
    cd: dict,
    score_snapshot_id: str = "evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
) -> dict:
    return build_evolution_user_state_v1(
        user_id="user-1",
        current_stage=stage,
        stage_started_at="2026-05-01T00:00:00Z",
        active_path_themes=["discipline"],
        completed_path_themes=[],
        progress_snapshot=progress,
        evolution_score_snapshot=120,
        last_evaluated_at="2026-06-01T09:00:00Z",
        cd=cd,
    )


def test_seeker_low_minimal_effects(cd: dict, full_progress: dict) -> None:
    state = _state(stage="seeker", progress=full_progress, cd=cd)
    outcome = try_build_evolution_effect_runtime_policy_v1(
        evolution_user_state=state,
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
    )

    assert outcome["result"] == POLICY_RESULT_CREATED
    policy = outcome["policy"]
    assert policy is not None
    assert policy["current_stage"] == "seeker"
    assert policy["allowed_effects"]["engine_effects"]["llm_budget_tier"] == "none"
    assert policy["allowed_effects"]["intelligence_effects"]["memory_window_days"] == 7
    assert policy["allowed_effects"]["intelligence_effects"]["active_knowledge_cap"] == 0
    assert policy["effect_limits"]["llm_budget_tier"] == "none"


def test_architect_deeper_effects_within_caps(cd: dict, full_progress: dict) -> None:
    state = _state(stage="architect", progress=full_progress, cd=cd)
    stage_effects = get_stage_product_effects("architect")

    outcome = try_build_evolution_effect_runtime_policy_v1(
        evolution_user_state=state,
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
    )

    assert outcome["result"] == POLICY_RESULT_CREATED
    policy = outcome["policy"]
    assert policy is not None
    assert policy["allowed_effects"]["intelligence_effects"]["memory_window_days"] == 90
    assert policy["allowed_effects"]["engine_effects"]["max_context_lines"] == 4
    assert policy["effect_limits"]["memory_window_days"] == 90
    assert policy["effect_limits"]["llm_budget_tier"] == "medium"
    assert validate_evolution_effect_runtime_policy_v1(policy, stage_effects=stage_effects) == []


def test_architect_unlock_when_gate_eligible(cd: dict) -> None:
    gate_progress = {
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
    state = _state(stage="architect", progress=gate_progress, cd=cd)
    assert state["stage_gate_eligibility"]["eligible"] is True

    policy = build_evolution_effect_runtime_policy_v1(
        evolution_user_state=state,
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
        source_systems_ready={
            "calendar_intelligence": True,
            "share_features": True,
        },
    )

    assert policy["allowed_effects"]["unlock_effects"]["share_features"] is True
    assert policy["allowed_effects"]["unlock_effects"]["calendar_insight_tier"] == "full"


def test_unknown_stage_rejected(cd: dict, full_progress: dict) -> None:
    state = _state(stage="seeker", progress=full_progress, cd=cd)
    state["current_stage"] = "novice"

    outcome = try_build_evolution_effect_runtime_policy_v1(
        evolution_user_state=state,
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
    )

    assert outcome["result"] == POLICY_RESULT_REJECTED


def test_missing_es_snapshot_blocked(cd: dict, full_progress: dict) -> None:
    state = _state(stage="seeker", progress=full_progress, cd=cd)

    outcome = try_build_evolution_effect_runtime_policy_v1(
        evolution_user_state=state,
        evolution_score_snapshot_id=None,
    )

    assert outcome["result"] == POLICY_RESULT_REJECTED
    assert any("evolution_score_snapshot_id" in reason for reason in outcome["reasons"])


def test_commerce_activation_blocked(cd: dict, full_progress: dict) -> None:
    policy = build_evolution_effect_runtime_policy_v1(
        evolution_user_state=_state(stage="practitioner", progress=full_progress, cd=cd),
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
    )

    assert policy["commerce_activation_allowed"] is False
    assert "commerce_activation" in policy["blocked_effects"]
    assert "commerce_targeting" in policy["blocked_effects"]
    assert "commerce_visibility" in policy["allowed_effects"]["commerce_effects"]


def test_unlock_effect_requires_gate(cd: dict, low_progress: dict) -> None:
    state = _state(stage="architect", progress=low_progress, cd=cd)
    assert state["stage_gate_eligibility"]["eligible"] is False

    policy = build_evolution_effect_runtime_policy_v1(
        evolution_user_state=state,
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
    )

    assert policy["allowed_effects"]["unlock_effects"] == {}
    assert "unlock_without_gate" in policy["blocked_effects"]


def test_llm_budget_cannot_exceed_cap(cd: dict, full_progress: dict) -> None:
    policy = build_evolution_effect_runtime_policy_v1(
        evolution_user_state=_state(stage="seeker", progress=full_progress, cd=cd),
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
        requested_llm_budget_tier="high",
    )

    assert "llm_budget_escalation" in policy["blocked_effects"]
    assert policy["effect_limits"]["llm_budget_tier"] == "none"


def test_mutation_flags_false(cd: dict, full_progress: dict) -> None:
    policy = build_evolution_effect_runtime_policy_v1(
        evolution_user_state=_state(stage="seeker", progress=full_progress, cd=cd),
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
    )

    assert policy["promotion_allowed"] is False
    assert policy["profile_update_allowed"] is False
    assert policy["memory_update_allowed"] is False
    assert policy["requires_gate"] is True


def test_effect_limits_mirror_registry(cd: dict, full_progress: dict) -> None:
    state = _state(stage="practitioner", progress=full_progress, cd=cd)
    stage_effects = get_stage_product_effects("practitioner")
    policy = build_evolution_effect_runtime_policy_v1(
        evolution_user_state=state,
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
    )

    assert validate_evolution_effect_runtime_policy_v1(policy, stage_effects=stage_effects) == []
    assert policy["stage_effects_ref"].startswith("evolution_product_effects_registry_v1:practitioner:")


def test_output_shape_stable(cd: dict, full_progress: dict) -> None:
    policy = build_evolution_effect_runtime_policy_v1(
        evolution_user_state=_state(stage="seeker", progress=full_progress, cd=cd),
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
    )

    assert policy["contract_version"] == EVOLUTION_EFFECT_RUNTIME_POLICY_V1_CONTRACT
    assert set(policy.keys()) == EVOLUTION_EFFECT_RUNTIME_POLICY_V1_KEYS


def test_forbidden_promotion_field_rejected(cd: dict, full_progress: dict) -> None:
    policy = build_evolution_effect_runtime_policy_v1(
        evolution_user_state=_state(stage="seeker", progress=full_progress, cd=cd),
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
    )
    bad = copy.deepcopy(policy)
    bad["promoted_stage"] = "observer"
    errors = validate_evolution_effect_runtime_policy_v1(bad)
    assert any("forbidden field" in e for e in errors)


def test_calendar_unlock_blocked_when_source_not_ready(cd: dict, full_progress: dict) -> None:
    policy = build_evolution_effect_runtime_policy_v1(
        evolution_user_state=_state(stage="architect", progress=full_progress, cd=cd),
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
        source_systems_ready={"calendar_intelligence": False, "share_features": False},
    )

    assert "unlock_effects.calendar_insight_tier" in policy["blocked_effects"]
    assert "calendar_insight_tier" not in policy["allowed_effects"]["unlock_effects"]
