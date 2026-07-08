"""B1.7 — Evolution effect consumer map tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache, load_evolution_cd_v1
from todayflow_backend.data.evolution_product_effects_loader import clear_evolution_product_effects_cache
from todayflow_backend.services.evolution_effect_consumer_map_v1 import (
    CONSUMER_CALENDAR,
    CONSUMER_COMMERCE_VISIBILITY,
    CONSUMER_CONTEXT_SELECTOR,
    CONSUMER_DAY_ENGINE,
    CONSUMER_LLM_GATE,
    CONSUMER_PRACTICE_SELECTOR,
    EVOLUTION_EFFECT_CONSUMER_MAP_V1_CONTRACT,
    EVOLUTION_EFFECT_CONSUMER_SLICE_V1_CONTRACT,
    EVOLUTION_EFFECT_CONSUMER_SLICE_V1_KEYS,
    SLICE_RESULT_CREATED,
    SLICE_RESULT_REJECTED,
    build_evolution_effect_consumer_map_v1,
    extract_evolution_effect_consumer_slice_v1,
    list_registered_consumers_v1,
    try_extract_evolution_effect_consumer_slice_v1,
    validate_evolution_effect_consumer_map_v1,
    validate_evolution_effect_consumer_slice_v1,
)
from todayflow_backend.services.evolution_effect_runtime_policy_v1 import build_evolution_effect_runtime_policy_v1
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
def architect_policy(cd: dict) -> dict:
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
    return build_evolution_effect_runtime_policy_v1(
        evolution_user_state=state,
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
        source_systems_ready={
            "calendar_intelligence": True,
            "share_features": True,
        },
    )


@pytest.fixture
def seeker_policy(cd: dict) -> dict:
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
    return build_evolution_effect_runtime_policy_v1(
        evolution_user_state=state,
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
    )


def test_consumer_map_registry_valid() -> None:
    assert validate_evolution_effect_consumer_map_v1() == []
    registry = build_evolution_effect_consumer_map_v1()
    assert registry["contract_version"] == EVOLUTION_EFFECT_CONSUMER_MAP_V1_CONTRACT
    assert set(registry["consumers"].keys()) == set(list_registered_consumers_v1())


def test_each_consumer_gets_only_allowed_slice(architect_policy: dict) -> None:
    for consumer_id in list_registered_consumers_v1():
        outcome = try_extract_evolution_effect_consumer_slice_v1(architect_policy, consumer_id)
        assert outcome["result"] == SLICE_RESULT_CREATED
        slice_payload = outcome["slice"]
        assert slice_payload is not None
        assert slice_payload["consumer_id"] == consumer_id
        assert "blocked_effects" not in slice_payload
        assert "stage_effects_ref" not in slice_payload
        assert "evolution_score_snapshot_id" not in slice_payload
        assert validate_evolution_effect_consumer_slice_v1(
            slice_payload,
            policy=architect_policy,
            consumer_id=consumer_id,
        ) == []


def test_context_selector_intelligence_only(architect_policy: dict) -> None:
    slice_payload = extract_evolution_effect_consumer_slice_v1(
        architect_policy,
        CONSUMER_CONTEXT_SELECTOR,
    )

    assert set(slice_payload["allowed_effects"].keys()) == {"intelligence_effects"}
    assert "engine_effects" not in slice_payload["allowed_effects"]
    assert slice_payload["allowed_effects"]["intelligence_effects"]["memory_window_days"] == 90
    assert slice_payload["effect_limits"]["active_knowledge_cap"] == 4


def test_llm_gate_engine_only(architect_policy: dict) -> None:
    slice_payload = extract_evolution_effect_consumer_slice_v1(architect_policy, CONSUMER_LLM_GATE)

    assert set(slice_payload["allowed_effects"].keys()) == {"engine_effects"}
    assert slice_payload["effect_limits"]["llm_budget_tier"] == "medium"
    assert slice_payload["effect_limits"]["max_tokens_cap"] == "high"


def test_practice_selector_unlock_subset(architect_policy: dict) -> None:
    slice_payload = extract_evolution_effect_consumer_slice_v1(
        architect_policy,
        CONSUMER_PRACTICE_SELECTOR,
    )

    assert set(slice_payload["allowed_effects"].keys()) == {"unlock_effects"}
    assert slice_payload["allowed_effects"]["unlock_effects"]["practice_pack_tier"] == "advanced"
    assert "commerce_effects" not in slice_payload["allowed_effects"]


def test_commerce_visibility_no_unlock_or_intelligence(architect_policy: dict) -> None:
    slice_payload = extract_evolution_effect_consumer_slice_v1(
        architect_policy,
        CONSUMER_COMMERCE_VISIBILITY,
    )

    assert set(slice_payload["allowed_effects"].keys()) == {"commerce_effects"}
    assert "unlock_effects" not in slice_payload["allowed_effects"]
    assert "intelligence_effects" not in slice_payload["allowed_effects"]
    assert slice_payload["allowed_effects"]["commerce_effects"]["commerce_visibility"] == "soft"


def test_day_engine_subset(seeker_policy: dict) -> None:
    slice_payload = extract_evolution_effect_consumer_slice_v1(seeker_policy, CONSUMER_DAY_ENGINE)

    assert slice_payload["allowed_effects"]["engine_effects"]["llm_budget_tier"] == "none"
    assert slice_payload["effect_limits"]["max_context_lines"] == 0
    assert "intelligence_effects" not in slice_payload["allowed_effects"]


def test_unknown_consumer_rejected(architect_policy: dict) -> None:
    outcome = try_extract_evolution_effect_consumer_slice_v1(architect_policy, "unknown_consumer")
    assert outcome["result"] == SLICE_RESULT_REJECTED


def test_invalid_policy_rejected(architect_policy: dict) -> None:
    bad = copy.deepcopy(architect_policy)
    bad["contract_version"] = "invalid"
    outcome = try_extract_evolution_effect_consumer_slice_v1(bad, CONSUMER_LLM_GATE)
    assert outcome["result"] == SLICE_RESULT_REJECTED


def test_mutation_flags_false_on_slices(architect_policy: dict) -> None:
    slice_payload = extract_evolution_effect_consumer_slice_v1(architect_policy, CONSUMER_LLM_GATE)

    assert slice_payload["read_only"] is True
    assert slice_payload["mutation_allowed"] is False
    assert slice_payload["profile_update_allowed"] is False
    assert slice_payload["memory_update_allowed"] is False
    assert slice_payload["commerce_activation_allowed"] is False


def test_output_shape_stable(architect_policy: dict) -> None:
    slice_payload = extract_evolution_effect_consumer_slice_v1(
        architect_policy,
        CONSUMER_CALENDAR,
    )

    assert slice_payload["contract_version"] == EVOLUTION_EFFECT_CONSUMER_SLICE_V1_CONTRACT
    assert set(slice_payload.keys()) == EVOLUTION_EFFECT_CONSUMER_SLICE_V1_KEYS


def test_slices_do_not_contain_full_policy_fields(architect_policy: dict) -> None:
    forbidden_on_slice = {
        "blocked_effects",
        "stage_effects_ref",
        "evolution_score_snapshot_id",
        "requires_gate",
    }
    for consumer_id in list_registered_consumers_v1():
        slice_payload = extract_evolution_effect_consumer_slice_v1(architect_policy, consumer_id)
        leaked = set(slice_payload.keys()) & forbidden_on_slice
        assert leaked == set()
