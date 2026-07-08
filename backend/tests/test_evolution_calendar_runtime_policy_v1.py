"""B1.12 — Evolution → Calendar consumer runtime policy tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache, load_evolution_cd_v1
from todayflow_backend.data.evolution_product_effects_loader import clear_evolution_product_effects_cache
from todayflow_backend.services.evolution_calendar_runtime_policy_v1 import (
    BLOCK_CALENDAR_SYSTEM_NOT_READY,
    BLOCK_FULL_POLICY_PASSED,
    BLOCK_INVALID_EVOLUTION_SLICE,
    CALENDAR_DEPTH_BASIC,
    CALENDAR_DEPTH_FULL,
    CALENDAR_DEPTH_NONE,
    CALENDAR_DEPTH_STANDARD,
    EVOLUTION_CALENDAR_RUNTIME_POLICY_V1_CONTRACT,
    EVOLUTION_CALENDAR_RUNTIME_POLICY_V1_KEYS,
    VIEW_CYCLE,
    VIEW_DAY,
    VIEW_MONTH,
    VIEW_RHYTHM,
    VIEW_WEEK,
    build_evolution_calendar_runtime_policy_v1,
    validate_evolution_calendar_runtime_policy_v1,
)
from todayflow_backend.services.evolution_effect_consumer_map_v1 import (
    CONSUMER_CALENDAR,
    extract_evolution_effect_consumer_slice_v1,
)
from todayflow_backend.services.evolution_effect_runtime_policy_v1 import (
    build_evolution_effect_runtime_policy_v1,
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


def _policy_for_stage(cd: dict, stage: str, **policy_kwargs):
    progress_by_stage = {
        "seeker": {
            "confirmed_patterns": 0,
            "completed_cycles": 0,
            "reflection_events": 3,
            "active_days": 7,
            "signal_counts": {},
            "confidence": 0.4,
        },
        "observer": {
            "confirmed_patterns": 1,
            "completed_cycles": 0,
            "reflection_events": 8,
            "active_days": 14,
            "signal_counts": {},
            "confidence": 0.5,
        },
        "practitioner": {
            "confirmed_patterns": 2,
            "completed_cycles": 1,
            "reflection_events": 12,
            "active_days": 30,
            "signal_counts": {"practice_completed": 5},
            "confidence": 0.6,
        },
        "explorer": {
            "confirmed_patterns": 3,
            "completed_cycles": 2,
            "reflection_events": 15,
            "active_days": 45,
            "signal_counts": {"practice_completed": 10},
            "confidence": 0.65,
        },
        "architect": {
            "confirmed_patterns": 5,
            "completed_cycles": 3,
            "reflection_events": 21,
            "active_days": 120,
            "signal_counts": {"confirmed_pattern": 2},
            "confidence": 0.75,
        },
    }
    state = build_evolution_user_state_v1(
        user_id="user-1",
        current_stage=stage,
        stage_started_at="2026-05-01T00:00:00Z",
        active_path_themes=["discipline"],
        completed_path_themes=[],
        progress_snapshot=progress_by_stage[stage],
        evolution_score_snapshot=100 if stage == "seeker" else 420,
        last_evaluated_at="2026-06-01T09:00:00Z",
        cd=cd,
    )
    return build_evolution_effect_runtime_policy_v1(
        evolution_user_state=state,
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
        **policy_kwargs,
    )


def _calendar_slice(cd: dict, stage: str, **policy_kwargs) -> dict:
    policy = _policy_for_stage(cd, stage, **policy_kwargs)
    return extract_evolution_effect_consumer_slice_v1(policy, CONSUMER_CALENDAR)


def _ready(**overrides):
    base = {"calendar_intelligence": True}
    base.update(overrides)
    return base


def test_seeker_basic_day_only(cd: dict) -> None:
    policy = build_evolution_calendar_runtime_policy_v1(
        _calendar_slice(cd, "seeker"),
        calendar_readiness=_ready(),
    )

    assert policy["evolution_stage"] == "seeker"
    assert policy["allowed_views"] == [VIEW_DAY]
    assert VIEW_WEEK not in policy["allowed_views"]
    assert VIEW_MONTH not in policy["allowed_views"]
    assert policy["calendar_depth"] in {CALENDAR_DEPTH_NONE, CALENDAR_DEPTH_BASIC}


def test_practitioner_month_basic_allowed(cd: dict) -> None:
    policy = build_evolution_calendar_runtime_policy_v1(
        _calendar_slice(
            cd,
            "practitioner",
            source_systems_ready={"calendar_intelligence": True, "share_features": True},
        ),
        calendar_readiness=_ready(),
    )

    assert VIEW_MONTH in policy["allowed_views"]
    assert policy["calendar_depth"] == CALENDAR_DEPTH_BASIC
    assert policy["monthly_map_allowed"] is True


def test_explorer_cycle_visibility_allowed(cd: dict) -> None:
    policy = build_evolution_calendar_runtime_policy_v1(
        _calendar_slice(
            cd,
            "explorer",
            source_systems_ready={"calendar_intelligence": True, "share_features": True},
        ),
        calendar_readiness=_ready(),
    )

    assert policy["cycle_visibility_allowed"] is True
    assert VIEW_CYCLE in policy["allowed_views"]
    assert policy["calendar_depth"] == CALENDAR_DEPTH_STANDARD


def test_architect_rhythm_insights_allowed(cd: dict) -> None:
    policy = build_evolution_calendar_runtime_policy_v1(
        _calendar_slice(
            cd,
            "architect",
            source_systems_ready={"calendar_intelligence": True, "share_features": True},
        ),
        calendar_readiness=_ready(),
    )

    assert policy["rhythm_insights_allowed"] is True
    assert VIEW_RHYTHM in policy["allowed_views"]
    assert policy["calendar_depth"] == CALENDAR_DEPTH_FULL


def test_system_not_ready_blocked_effects(cd: dict) -> None:
    policy = build_evolution_calendar_runtime_policy_v1(
        _calendar_slice(
            cd,
            "architect",
            source_systems_ready={"calendar_intelligence": False, "share_features": False},
        ),
        calendar_readiness={"calendar_intelligence": False},
    )

    assert BLOCK_CALENDAR_SYSTEM_NOT_READY in policy["blocked_calendar_effects"]
    assert policy["cycle_visibility_allowed"] is False
    assert policy["rhythm_insights_allowed"] is False
    assert policy["monthly_map_allowed"] is False
    assert policy["calendar_depth"] == CALENDAR_DEPTH_NONE


def test_invalid_slice_ignored_with_trace(cd: dict) -> None:
    valid_slice = _calendar_slice(
        cd,
        "seeker",
        source_systems_ready={"calendar_intelligence": True, "share_features": True},
    )
    invalid = copy.deepcopy(valid_slice)
    invalid["consumer_id"] = "not_calendar"

    policy = build_evolution_calendar_runtime_policy_v1(
        invalid,
        calendar_readiness=_ready(),
    )

    assert policy["source_evolution_slice_id"] is None
    assert BLOCK_INVALID_EVOLUTION_SLICE in policy["blocked_calendar_effects"]
    assert policy["allowed_views"] == []


def test_full_policy_rejected_or_ignored(cd: dict) -> None:
    full_policy = build_evolution_effect_runtime_policy_v1(
        evolution_user_state=build_evolution_user_state_v1(
            user_id="user-1",
            current_stage="architect",
            stage_started_at="2026-05-01T00:00:00Z",
            active_path_themes=["discipline"],
            completed_path_themes=[],
            progress_snapshot={
                "confirmed_patterns": 5,
                "completed_cycles": 3,
                "reflection_events": 21,
                "active_days": 120,
                "signal_counts": {},
                "confidence": 0.75,
            },
            evolution_score_snapshot=420,
            last_evaluated_at="2026-06-01T09:00:00Z",
            cd=cd,
        ),
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
    )

    policy = build_evolution_calendar_runtime_policy_v1(
        full_policy,
        calendar_readiness=_ready(),
    )

    assert BLOCK_FULL_POLICY_PASSED in policy["blocked_calendar_effects"]
    assert policy["source_evolution_slice_id"] is None


def test_read_only_flags_and_no_mutation(cd: dict) -> None:
    policy = build_evolution_calendar_runtime_policy_v1(
        _calendar_slice(
            cd,
            "practitioner",
            source_systems_ready={"calendar_intelligence": True, "share_features": True},
        ),
        calendar_readiness=_ready(),
    )

    assert policy["read_only"] is True
    assert policy["calendar_mutation_allowed"] is False
    assert policy["profile_update_allowed"] is False
    assert policy["memory_update_allowed"] is False


def test_no_insight_or_recommendation_fields(cd: dict) -> None:
    policy = build_evolution_calendar_runtime_policy_v1(
        _calendar_slice(
            cd,
            "architect",
            source_systems_ready={"calendar_intelligence": True, "share_features": True},
        ),
        calendar_readiness=_ready(),
    )

    forbidden = {
        "insight",
        "calendar_insight",
        "insight_text",
        "recommendation",
        "llm_call",
        "commerce",
        "calendar_event",
        "events",
        "score",
        "stage_update",
    }
    assert forbidden.isdisjoint(set(policy.keys()))
    assert validate_evolution_calendar_runtime_policy_v1(policy) == []


def test_output_shape_stable(cd: dict) -> None:
    policy = build_evolution_calendar_runtime_policy_v1(
        _calendar_slice(
            cd,
            "explorer",
            source_systems_ready={"calendar_intelligence": True, "share_features": True},
        ),
        calendar_readiness=_ready(),
    )

    assert policy["contract_version"] == EVOLUTION_CALENDAR_RUNTIME_POLICY_V1_CONTRACT
    assert set(policy.keys()) == EVOLUTION_CALENDAR_RUNTIME_POLICY_V1_KEYS
