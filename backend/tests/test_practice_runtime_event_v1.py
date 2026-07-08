"""C2.1 — Practice runtime event contract tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.ascetic_definition_registry_loader import clear_ascetic_definition_registry_cache
from todayflow_backend.data.cycle_definition_registry_loader import clear_cycle_definition_registry_cache
from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache
from todayflow_backend.data.goal_definition_registry_loader import clear_goal_definition_registry_cache
from todayflow_backend.data.habit_definition_registry_loader import clear_habit_definition_registry_cache
from todayflow_backend.data.practice_definition_registry_loader import clear_practice_definition_registry_cache
from todayflow_backend.data.progression_signal_registry_loader import clear_progression_signal_registry_cache
from todayflow_backend.data.ritual_definition_registry_loader import clear_ritual_definition_registry_cache
from todayflow_backend.services.practice_runtime_event_v1 import (
    PRACTICE_RUNTIME_EVENT_V1_CONTRACT,
    PRACTICE_RUNTIME_EVENT_V1_KEYS,
    PracticeRuntimeEventError,
    build_ascetic_compliance_event_v1,
    build_cycle_completion_event_v1,
    build_goal_progress_event_v1,
    build_habit_streak_event_v1,
    build_practice_completed_event_v1,
    build_ritual_streak_event_v1,
    resolve_emitted_signal_type_from_event,
    validate_event_emission_path_v1,
    validate_practice_runtime_event_v1,
)
from todayflow_backend.services.progression_signal_v1 import VERIFICATION_STATUS_PENDING, VERIFICATION_STATUS_VERIFIED


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


def test_practice_completed_event_schema() -> None:
    event = build_practice_completed_event_v1(
        user_id="user-1",
        definition_code="breathing",
        occurred_at="2026-06-01T08:00:00Z",
        source="user_action",
        verification_status=VERIFICATION_STATUS_VERIFIED,
        confidence=0.7,
        duration_minutes=5,
        completion_quality="complete",
        source_surface="today_engine",
    )
    assert event["contract_version"] == PRACTICE_RUNTIME_EVENT_V1_CONTRACT
    assert set(event.keys()) == PRACTICE_RUNTIME_EVENT_V1_KEYS
    assert event["event_kind"] == "practice_completed_event"
    assert resolve_emitted_signal_type_from_event(event) == "practice_completed"
    assert validate_event_emission_path_v1(event) == []


def test_habit_streak_event_resolves_when_threshold_met() -> None:
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
    )
    assert resolve_emitted_signal_type_from_event(event) == "habit_streak_confirmed"
    assert validate_event_emission_path_v1(event) == []


def test_habit_streak_no_signal_when_threshold_not_met() -> None:
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
    assert resolve_emitted_signal_type_from_event(event) is None
    assert any("does not resolve" in e for e in validate_event_emission_path_v1(event))


def test_goal_weekly_progress_event() -> None:
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
    assert resolve_emitted_signal_type_from_event(event) == "weekly_goal_completed"
    assert validate_event_emission_path_v1(event) == []


def test_ritual_streak_event() -> None:
    event = build_ritual_streak_event_v1(
        user_id="user-1",
        definition_code="evening_reflection_ritual",
        occurred_at="2026-06-01T21:00:00Z",
        source="user_action",
        verification_status=VERIFICATION_STATUS_VERIFIED,
        confidence=0.55,
        streak_length=3,
        completed_components_count=2,
        required_components_count=2,
        threshold_met=True,
    )
    assert resolve_emitted_signal_type_from_event(event) == "ritual_streak_confirmed"


def test_cycle_completion_event() -> None:
    event = build_cycle_completion_event_v1(
        user_id="user-1",
        definition_code="twenty_one_day_discipline_cycle",
        occurred_at="2026-06-22T12:00:00Z",
        source="scheduled_check",
        verification_status=VERIFICATION_STATUS_VERIFIED,
        confidence=0.7,
        duration_days=21,
        completion_rate=0.85,
        required_threshold=0.7,
        completed_components_count=3,
    )
    assert resolve_emitted_signal_type_from_event(event) == "cycle_completed"
    assert validate_event_emission_path_v1(event) == []


def test_ascetic_compliance_pending_only() -> None:
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
    assert event["metadata"]["emits_signal"] is False
    assert resolve_emitted_signal_type_from_event(event) is None
    assert validate_event_emission_path_v1(event) == []


def test_ascetic_verified_rejected() -> None:
    with pytest.raises(PracticeRuntimeEventError, match="cannot be verified"):
        build_ascetic_compliance_event_v1(
            user_id="user-1",
            definition_code="no_sugar",
            occurred_at="2026-06-01T20:00:00Z",
            source="user_action",
            verification_status=VERIFICATION_STATUS_VERIFIED,
            confidence=0.8,
            compliance_status="kept",
            compliance_days=5,
            safety_flag=True,
        )


def test_verified_requires_confidence_threshold() -> None:
    with pytest.raises(PracticeRuntimeEventError, match="below verified threshold"):
        build_practice_completed_event_v1(
            user_id="user-1",
            definition_code="breathing",
            occurred_at="2026-06-01T08:00:00Z",
            source="user_action",
            verification_status=VERIFICATION_STATUS_VERIFIED,
            confidence=0.3,
            duration_minutes=5,
            completion_quality="complete",
            source_surface="today_engine",
        )


def test_unknown_definition_code_rejected() -> None:
    with pytest.raises(PracticeRuntimeEventError):
        build_practice_completed_event_v1(
            user_id="user-1",
            definition_code="nonexistent_practice",
            occurred_at="2026-06-01T08:00:00Z",
            source="user_action",
            verification_status=VERIFICATION_STATUS_PENDING,
            confidence=0.5,
            duration_minutes=5,
            completion_quality="complete",
            source_surface="today_engine",
        )


def test_forbidden_promotion_field() -> None:
    event = build_practice_completed_event_v1(
        user_id="user-1",
        definition_code="breathing",
        occurred_at="2026-06-01T08:00:00Z",
        source="user_action",
        verification_status=VERIFICATION_STATUS_PENDING,
        confidence=0.5,
        duration_minutes=5,
        completion_quality="complete",
        source_surface="today_engine",
    )
    bad = copy.deepcopy(event)
    bad["promoted_stage"] = "practitioner"
    errors = validate_practice_runtime_event_v1(bad)
    assert any("forbidden field" in e for e in errors)
