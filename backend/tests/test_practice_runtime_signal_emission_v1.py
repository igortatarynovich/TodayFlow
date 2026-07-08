"""C2.0 — Practice runtime signal emission contract tests."""

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
from todayflow_backend.services.practice_runtime_signal_emission_v1 import (
    PRACTICE_RUNTIME_SIGNAL_EMISSION_V1_CONTRACT,
    PRACTICE_RUNTIME_SIGNAL_EMISSION_V1_KEYS,
    PracticeRuntimeSignalEmissionError,
    build_practice_runtime_signal_emission_v1,
    list_cd_allowed_signal_types,
    materialize_progression_signal_from_emission_v1,
    validate_practice_runtime_signal_emission_v1,
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


def test_practice_completion_emission_and_materialization() -> None:
    emission = build_practice_runtime_signal_emission_v1(
        user_id="user-1",
        runtime_event_id="evt-practice-1",
        runtime_entity_type="practice",
        definition_code="breathing",
        emitted_signal_type="practice_completed",
        verification_status=VERIFICATION_STATUS_VERIFIED,
        confidence=0.7,
        occurred_at="2026-06-01T08:00:00Z",
    )
    assert emission["contract_version"] == PRACTICE_RUNTIME_SIGNAL_EMISSION_V1_CONTRACT
    assert set(emission.keys()) == PRACTICE_RUNTIME_SIGNAL_EMISSION_V1_KEYS
    assert emission["progression_signal_id"] is None

    updated, signal = materialize_progression_signal_from_emission_v1(
        emission,
        path_theme_code="discipline",
    )
    assert updated["progression_signal_id"] == signal["progression_signal_id"]
    assert signal["contract_version"] == PROGRESSION_SIGNAL_V1_CONTRACT
    assert signal["signal_type"] == "practice_completed"
    assert signal["source_engine"] == "practice"
    assert signal["promotion_allowed"] is False


def test_habit_streak_emission() -> None:
    allowed = list_cd_allowed_signal_types("habit", "daily_breathing")
    assert "habit_streak_confirmed" in allowed

    emission = build_practice_runtime_signal_emission_v1(
        user_id="user-1",
        runtime_event_id="evt-habit-1",
        runtime_entity_type="habit",
        definition_code="daily_breathing",
        emitted_signal_type="habit_streak_confirmed",
        verification_status=VERIFICATION_STATUS_VERIFIED,
        confidence=0.6,
        occurred_at="2026-06-01T08:00:00Z",
    )
    _, signal = materialize_progression_signal_from_emission_v1(emission)
    assert signal["signal_type"] == "habit_streak_confirmed"


def test_ritual_streak_emission() -> None:
    emission = build_practice_runtime_signal_emission_v1(
        user_id="user-1",
        runtime_event_id="evt-ritual-1",
        runtime_entity_type="ritual",
        definition_code="evening_reflection_ritual",
        emitted_signal_type="ritual_streak_confirmed",
        verification_status=VERIFICATION_STATUS_VERIFIED,
        confidence=0.55,
        occurred_at="2026-06-01T21:00:00Z",
    )
    _, signal = materialize_progression_signal_from_emission_v1(emission)
    assert signal["signal_type"] == "ritual_streak_confirmed"
    assert signal["source_engine"] == "ritual"


def test_cycle_completed_emission() -> None:
    emission = build_practice_runtime_signal_emission_v1(
        user_id="user-1",
        runtime_event_id="evt-cycle-1",
        runtime_entity_type="cycle",
        definition_code="twenty_one_day_discipline_cycle",
        emitted_signal_type="cycle_completed",
        verification_status=VERIFICATION_STATUS_VERIFIED,
        confidence=0.65,
        occurred_at="2026-06-22T12:00:00Z",
    )
    _, signal = materialize_progression_signal_from_emission_v1(
        emission,
        path_theme_code="discipline",
    )
    assert signal["signal_type"] == "cycle_completed"
    assert signal["source_engine"] == "calendar"


def test_goal_weekly_emission() -> None:
    emission = build_practice_runtime_signal_emission_v1(
        user_id="user-1",
        runtime_event_id="evt-goal-1",
        runtime_entity_type="goal",
        definition_code="weekly_clarity_theme",
        emitted_signal_type="weekly_goal_completed",
        verification_status=VERIFICATION_STATUS_VERIFIED,
        confidence=0.6,
        occurred_at="2026-06-07T18:00:00Z",
    )
    _, signal = materialize_progression_signal_from_emission_v1(emission)
    assert signal["signal_type"] == "weekly_goal_completed"
    assert signal["source_engine"] == "goal"


def test_ascetic_direct_emission_rejected() -> None:
    with pytest.raises(PracticeRuntimeSignalEmissionError, match="ascetic"):
        build_practice_runtime_signal_emission_v1(
            user_id="user-1",
            runtime_event_id="evt-ascetic-1",
            runtime_entity_type="ascetic",
            definition_code="no_sugar",
            emitted_signal_type="practice_completed",
            verification_status=VERIFICATION_STATUS_VERIFIED,
            confidence=0.5,
            occurred_at="2026-06-01T08:00:00Z",
        )


def test_pending_emission_has_no_progression_signal() -> None:
    emission = build_practice_runtime_signal_emission_v1(
        user_id="user-1",
        runtime_event_id="evt-pending-1",
        runtime_entity_type="practice",
        definition_code="meditation",
        emitted_signal_type="practice_completed",
        verification_status=VERIFICATION_STATUS_PENDING,
        confidence=0.4,
        occurred_at="2026-06-01T08:00:00Z",
    )
    updated, signal = materialize_progression_signal_from_emission_v1(emission)
    assert signal is None
    assert updated["progression_signal_id"] is None


def test_rejected_emission_has_no_progression_signal() -> None:
    emission = build_practice_runtime_signal_emission_v1(
        user_id="user-1",
        runtime_event_id="evt-reject-1",
        runtime_entity_type="practice",
        definition_code="meditation",
        emitted_signal_type="practice_completed",
        verification_status=VERIFICATION_STATUS_REJECTED,
        confidence=0.2,
        occurred_at="2026-06-01T08:00:00Z",
    )
    _, signal = materialize_progression_signal_from_emission_v1(emission)
    assert signal is None


def test_cd_disallowed_signal_type_rejected() -> None:
    with pytest.raises(PracticeRuntimeSignalEmissionError, match="not allowed"):
        build_practice_runtime_signal_emission_v1(
            user_id="user-1",
            runtime_event_id="evt-bad-1",
            runtime_entity_type="practice",
            definition_code="breathing",
            emitted_signal_type="cycle_completed",
            verification_status=VERIFICATION_STATUS_VERIFIED,
            confidence=0.8,
            occurred_at="2026-06-01T08:00:00Z",
        )


def test_validator_rejects_forbidden_promotion_field() -> None:
    emission = build_practice_runtime_signal_emission_v1(
        user_id="user-1",
        runtime_event_id="evt-1",
        runtime_entity_type="practice",
        definition_code="breathing",
        emitted_signal_type="practice_completed",
        verification_status=VERIFICATION_STATUS_PENDING,
        confidence=0.5,
        occurred_at="2026-06-01T08:00:00Z",
    )
    bad = copy.deepcopy(emission)
    bad["promotion_allowed"] = True
    errors = validate_practice_runtime_signal_emission_v1(bad)
    assert any("forbidden field" in e for e in errors)
