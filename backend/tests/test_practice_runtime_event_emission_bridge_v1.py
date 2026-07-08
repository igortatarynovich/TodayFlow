"""C2.2 — Runtime event → emission bridge tests."""

from __future__ import annotations

import copy
import uuid

import pytest

from todayflow_backend.data.ascetic_definition_registry_loader import clear_ascetic_definition_registry_cache
from todayflow_backend.data.cycle_definition_registry_loader import clear_cycle_definition_registry_cache
from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache
from todayflow_backend.data.goal_definition_registry_loader import clear_goal_definition_registry_cache
from todayflow_backend.data.habit_definition_registry_loader import clear_habit_definition_registry_cache
from todayflow_backend.data.practice_definition_registry_loader import clear_practice_definition_registry_cache
from todayflow_backend.data.progression_signal_registry_loader import clear_progression_signal_registry_cache
from todayflow_backend.data.ritual_definition_registry_loader import clear_ritual_definition_registry_cache
from todayflow_backend.services.practice_runtime_event_emission_bridge_v1 import (
    BRIDGE_RESULT_EMISSION_CREATED,
    BRIDGE_RESULT_REJECTED,
    MATERIALIZATION_RESULT_EMISSION_PENDING,
    MATERIALIZATION_RESULT_MATERIALIZED,
    MATERIALIZATION_RESULT_REJECTED,
    try_build_emission_from_runtime_event_v1,
    try_materialize_progression_signal_from_runtime_event_v1,
    validate_bridge_output_has_no_mutation_fields,
)
from todayflow_backend.services.practice_runtime_event_v1 import (
    build_ascetic_compliance_event_v1,
    build_cycle_completion_event_v1,
    build_goal_progress_event_v1,
    build_habit_streak_event_v1,
    build_practice_completed_event_v1,
    build_practice_runtime_event_v1,
    build_ritual_streak_event_v1,
)
from todayflow_backend.services.progression_signal_v1 import (
    PROGRESSION_SIGNAL_V1_CONTRACT,
    VERIFICATION_STATUS_PENDING,
    VERIFICATION_STATUS_REJECTED,
    VERIFICATION_STATUS_VERIFIED,
)


@pytest.fixture(autouse=True)
def _clear_caches() -> None:
    clear_evolution_cd_cache()
    clear_practice_definition_registry_cache()
    clear_habit_definition_registry_cache()
    clear_goal_definition_registry_cache()
    clear_ascetic_definition_registry_cache()
    clear_ritual_definition_registry_cache()
    clear_cycle_definition_registry_cache()
    clear_progression_signal_registry_cache()
    yield
    clear_evolution_cd_cache()
    clear_practice_definition_registry_cache()
    clear_habit_definition_registry_cache()
    clear_goal_definition_registry_cache()
    clear_ascetic_definition_registry_cache()
    clear_ritual_definition_registry_cache()
    clear_cycle_definition_registry_cache()
    clear_progression_signal_registry_cache()


def _practice_event(*, verification_status: str, event_id: str | None = None) -> dict:
    return build_practice_completed_event_v1(
        user_id="user-1",
        definition_code="breathing",
        occurred_at="2026-06-01T08:00:00Z",
        source="user_action",
        verification_status=verification_status,
        confidence=0.7 if verification_status == VERIFICATION_STATUS_VERIFIED else 0.4,
        duration_minutes=5,
        completion_quality="complete",
        source_surface="today_engine",
        event_id=event_id or str(uuid.uuid4()),
    )


def test_verified_practice_event_full_materialization() -> None:
    event_id = "evt-practice-bridge-1"
    event = _practice_event(verification_status=VERIFICATION_STATUS_VERIFIED, event_id=event_id)

    emission_outcome = try_build_emission_from_runtime_event_v1(event)
    assert emission_outcome["result"] == BRIDGE_RESULT_EMISSION_CREATED
    emission = emission_outcome["emission"]
    assert emission is not None
    assert emission["runtime_event_id"] == event_id
    assert emission["emitted_signal_type"] == "practice_completed"
    assert emission["verification_status"] == VERIFICATION_STATUS_VERIFIED

    materialized = try_materialize_progression_signal_from_runtime_event_v1(
        event,
        path_theme_code="discipline",
    )
    assert materialized["result"] == MATERIALIZATION_RESULT_MATERIALIZED
    signal = materialized["progression_signal"]
    assert signal is not None
    assert signal["contract_version"] == PROGRESSION_SIGNAL_V1_CONTRACT
    assert signal["signal_type"] == "practice_completed"
    assert signal["source_event_id"] == event_id
    assert signal["promotion_allowed"] is False

    trace = materialized["trace"]
    assert trace["event_id"] == event_id
    assert trace["emission_id"] == materialized["emission"]["emission_id"]
    assert trace["progression_signal_id"] == signal["progression_signal_id"]
    assert materialized["emission"]["progression_signal_id"] == signal["progression_signal_id"]


def test_pending_event_emission_without_progression_signal() -> None:
    event = _practice_event(verification_status=VERIFICATION_STATUS_PENDING)

    outcome = try_materialize_progression_signal_from_runtime_event_v1(event)
    assert outcome["result"] == MATERIALIZATION_RESULT_EMISSION_PENDING
    assert outcome["emission"]["verification_status"] == VERIFICATION_STATUS_PENDING
    assert outcome["progression_signal"] is None
    assert outcome["trace"]["emission_id"] is not None
    assert outcome["trace"]["progression_signal_id"] is None


def test_rejected_event_no_emission() -> None:
    event = _practice_event(verification_status=VERIFICATION_STATUS_REJECTED)

    outcome = try_build_emission_from_runtime_event_v1(event)
    assert outcome["result"] == BRIDGE_RESULT_REJECTED
    assert outcome["emission"] is None


def test_habit_threshold_false_no_signal() -> None:
    event = build_habit_streak_event_v1(
        user_id="user-1",
        definition_code="daily_breathing",
        occurred_at="2026-06-01T08:00:00Z",
        source="scheduled_check",
        verification_status=VERIFICATION_STATUS_VERIFIED,
        confidence=0.6,
        streak_length=3,
        period_days=7,
        missed_days=2,
        threshold_met=False,
    )

    outcome = try_build_emission_from_runtime_event_v1(event)
    assert outcome["result"] == BRIDGE_RESULT_REJECTED


def test_goal_weekly_resolves_weekly_goal_completed() -> None:
    event = build_goal_progress_event_v1(
        user_id="user-1",
        definition_code="weekly_clarity_theme",
        occurred_at="2026-06-07T18:00:00Z",
        source="system_detection",
        verification_status=VERIFICATION_STATUS_VERIFIED,
        confidence=0.65,
        progress_value=1,
        target_value=1,
        milestone_code=None,
        period_type="weekly",
    )

    outcome = try_materialize_progression_signal_from_runtime_event_v1(event)
    assert outcome["result"] == MATERIALIZATION_RESULT_MATERIALIZED
    assert outcome["progression_signal"]["signal_type"] == "weekly_goal_completed"


def test_goal_milestone_resolves_goal_milestone_reached() -> None:
    event = build_goal_progress_event_v1(
        user_id="user-1",
        definition_code="habit_consistency_milestone",
        occurred_at="2026-06-15T12:00:00Z",
        source="system_detection",
        verification_status=VERIFICATION_STATUS_VERIFIED,
        confidence=0.65,
        progress_value=21,
        target_value=21,
        milestone_code="habit_21_day",
        period_type="milestone",
    )

    outcome = try_materialize_progression_signal_from_runtime_event_v1(event)
    assert outcome["result"] == MATERIALIZATION_RESULT_MATERIALIZED
    assert outcome["progression_signal"]["signal_type"] == "goal_milestone_reached"


def test_ritual_threshold_false_no_signal() -> None:
    event = build_ritual_streak_event_v1(
        user_id="user-1",
        definition_code="evening_reflection_ritual",
        occurred_at="2026-06-01T21:00:00Z",
        source="user_action",
        verification_status=VERIFICATION_STATUS_VERIFIED,
        confidence=0.55,
        streak_length=1,
        completed_components_count=1,
        required_components_count=2,
        threshold_met=False,
    )

    outcome = try_build_emission_from_runtime_event_v1(event)
    assert outcome["result"] == BRIDGE_RESULT_REJECTED


def test_cycle_below_threshold_no_signal() -> None:
    event = build_cycle_completion_event_v1(
        user_id="user-1",
        definition_code="twenty_one_day_discipline_cycle",
        occurred_at="2026-06-22T12:00:00Z",
        source="scheduled_check",
        verification_status=VERIFICATION_STATUS_VERIFIED,
        confidence=0.7,
        duration_days=21,
        completion_rate=0.5,
        required_threshold=0.7,
        completed_components_count=2,
    )

    outcome = try_build_emission_from_runtime_event_v1(event)
    assert outcome["result"] == BRIDGE_RESULT_REJECTED


def test_ascetic_event_blocked() -> None:
    event = build_ascetic_compliance_event_v1(
        user_id="user-1",
        definition_code="no_sugar",
        occurred_at="2026-06-01T20:00:00Z",
        source="user_action",
        verification_status=VERIFICATION_STATUS_PENDING,
        confidence=0.4,
        compliance_status="kept",
        compliance_days=5,
        safety_flag=True,
    )

    outcome = try_build_emission_from_runtime_event_v1(event)
    assert outcome["result"] == BRIDGE_RESULT_REJECTED
    assert any("ascetic" in reason for reason in outcome["reasons"])

    materialized = try_materialize_progression_signal_from_runtime_event_v1(event)
    assert materialized["result"] == MATERIALIZATION_RESULT_REJECTED
    assert materialized["progression_signal"] is None


def test_trace_ids_preserved_on_habit_streak() -> None:
    event_id = "evt-habit-bridge-1"
    event = build_habit_streak_event_v1(
        user_id="user-1",
        definition_code="daily_breathing",
        occurred_at="2026-06-01T08:00:00Z",
        source="scheduled_check",
        verification_status=VERIFICATION_STATUS_VERIFIED,
        confidence=0.6,
        streak_length=7,
        period_days=7,
        missed_days=0,
        threshold_met=True,
        event_id=event_id,
    )

    outcome = try_materialize_progression_signal_from_runtime_event_v1(event)
    assert outcome["trace"]["event_id"] == event_id
    assert outcome["trace"]["emission_id"] == outcome["emission"]["emission_id"]
    assert outcome["trace"]["progression_signal_id"] == outcome["progression_signal"]["progression_signal_id"]
    assert outcome["emission"]["runtime_event_id"] == event_id


def test_no_mutation_fields_on_bridge_outputs() -> None:
    event = _practice_event(verification_status=VERIFICATION_STATUS_VERIFIED)
    outcome = try_materialize_progression_signal_from_runtime_event_v1(event)
    assert validate_bridge_output_has_no_mutation_fields(
        outcome["emission"],
        outcome["progression_signal"],
    ) == []

    bad_emission = copy.deepcopy(outcome["emission"])
    bad_emission["evolution_score"] = 10
    assert validate_bridge_output_has_no_mutation_fields(bad_emission, None)


def test_rejected_runtime_event_via_raw_builder() -> None:
    event = build_practice_runtime_event_v1(
        user_id="user-1",
        runtime_entity_type="practice",
        definition_code="meditation",
        event_kind="practice_completed_event",
        occurred_at="2026-06-01T08:00:00Z",
        source="user_action",
        verification_status=VERIFICATION_STATUS_REJECTED,
        confidence=0.2,
        metadata={
            "duration_minutes": 10,
            "completion_quality": "complete",
            "source_surface": "today_engine",
        },
    )

    outcome = try_materialize_progression_signal_from_runtime_event_v1(event)
    assert outcome["result"] == MATERIALIZATION_RESULT_REJECTED
