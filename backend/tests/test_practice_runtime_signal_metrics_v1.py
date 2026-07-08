"""C2.4 — Practice runtime signal metrics tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.ascetic_definition_registry_loader import clear_ascetic_definition_registry_cache
from todayflow_backend.data.cycle_definition_registry_loader import clear_cycle_definition_registry_cache
from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache
from todayflow_backend.data.evolution_score_contract_loader import clear_evolution_score_contract_cache
from todayflow_backend.data.goal_definition_registry_loader import clear_goal_definition_registry_cache
from todayflow_backend.data.habit_definition_registry_loader import clear_habit_definition_registry_cache
from todayflow_backend.data.practice_definition_registry_loader import clear_practice_definition_registry_cache
from todayflow_backend.data.progression_signal_registry_loader import clear_progression_signal_registry_cache
from todayflow_backend.data.ritual_definition_registry_loader import clear_ritual_definition_registry_cache
from todayflow_backend.services.practice_runtime_event_emission_bridge_v1 import (
    BRIDGE_RESULT_REJECTED,
    try_build_emission_from_runtime_event_v1,
    try_materialize_progression_signal_from_runtime_event_v1,
)
from todayflow_backend.services.practice_runtime_event_v1 import (
    build_ascetic_compliance_event_v1,
    build_habit_streak_event_v1,
    build_practice_completed_event_v1,
)
from todayflow_backend.services.practice_runtime_signal_metrics_v1 import (
    PRACTICE_RUNTIME_SIGNAL_METRICS_V1_CONTRACT,
    PRACTICE_RUNTIME_SIGNAL_METRICS_V1_KEYS,
    build_practice_runtime_signal_metrics_v1,
    validate_practice_runtime_signal_metrics_v1,
)
from todayflow_backend.services.practice_runtime_trace_map_v1 import (
    TRACE_STATUS_COMPLETE,
    TRACE_STATUS_FAILED,
    TRACE_STATUS_PARTIAL,
    build_practice_runtime_trace_map_v1,
)
from todayflow_backend.services.progression_signal_v1 import VERIFICATION_STATUS_PENDING, VERIFICATION_STATUS_REJECTED, VERIFICATION_STATUS_VERIFIED

WINDOW_START = "2026-06-01T00:00:00Z"
WINDOW_END = "2026-06-30T23:59:59Z"


@pytest.fixture(autouse=True)
def _clear_caches() -> None:
    clear_evolution_cd_cache()
    clear_evolution_score_contract_cache()
    clear_practice_definition_registry_cache()
    clear_habit_definition_registry_cache()
    clear_goal_definition_registry_cache()
    clear_ascetic_definition_registry_cache()
    clear_ritual_definition_registry_cache()
    clear_cycle_definition_registry_cache()
    clear_progression_signal_registry_cache()
    yield
    clear_evolution_cd_cache()
    clear_evolution_score_contract_cache()
    clear_practice_definition_registry_cache()
    clear_habit_definition_registry_cache()
    clear_goal_definition_registry_cache()
    clear_ascetic_definition_registry_cache()
    clear_ritual_definition_registry_cache()
    clear_cycle_definition_registry_cache()
    clear_progression_signal_registry_cache()


def _build_metrics(**kwargs):
    return build_practice_runtime_signal_metrics_v1(
        window_start=WINDOW_START,
        window_end=WINDOW_END,
        **kwargs,
    )


def test_empty_input_zero_metrics() -> None:
    metrics = _build_metrics()

    assert metrics["contract_version"] == PRACTICE_RUNTIME_SIGNAL_METRICS_V1_CONTRACT
    assert metrics["event_metrics"]["event_count"] == 0
    assert metrics["emission_metrics"]["emission_count"] == 0
    assert metrics["signal_metrics"]["materialized_signal_count"] == 0
    assert metrics["trace_metrics"]["complete_trace_count"] == 0
    assert metrics["distributions"]["signal_type_distribution"] == {}


def test_mixed_event_counts() -> None:
    events = [
        build_practice_completed_event_v1(
            user_id="user-1",
            definition_code="breathing",
            occurred_at="2026-06-01T08:00:00Z",
            source="user_action",
            verification_status=VERIFICATION_STATUS_VERIFIED,
            confidence=0.7,
            duration_minutes=5,
            completion_quality="complete",
            source_surface="today_engine",
        ),
        build_practice_completed_event_v1(
            user_id="user-1",
            definition_code="meditation",
            occurred_at="2026-06-02T08:00:00Z",
            source="user_action",
            verification_status=VERIFICATION_STATUS_PENDING,
            confidence=0.4,
            duration_minutes=10,
            completion_quality="complete",
            source_surface="today_engine",
        ),
        build_practice_completed_event_v1(
            user_id="user-1",
            definition_code="breathing",
            occurred_at="2026-06-03T08:00:00Z",
            source="user_action",
            verification_status=VERIFICATION_STATUS_REJECTED,
            confidence=0.2,
            duration_minutes=5,
            completion_quality="partial",
            source_surface="today_engine",
        ),
    ]

    metrics = _build_metrics(events=events)

    assert metrics["event_metrics"]["event_count"] == 3
    assert metrics["event_metrics"]["verified_event_count"] == 1
    assert metrics["event_metrics"]["pending_event_count"] == 1
    assert metrics["event_metrics"]["rejected_event_count"] == 1


def test_mixed_emission_counts() -> None:
    verified_event = build_practice_completed_event_v1(
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
    pending_event = build_practice_completed_event_v1(
        user_id="user-1",
        definition_code="meditation",
        occurred_at="2026-06-02T08:00:00Z",
        source="user_action",
        verification_status=VERIFICATION_STATUS_PENDING,
        confidence=0.4,
        duration_minutes=10,
        completion_quality="complete",
        source_surface="today_engine",
    )

    verified_outcome = try_build_emission_from_runtime_event_v1(verified_event)
    pending_outcome = try_build_emission_from_runtime_event_v1(pending_event)
    emissions = [verified_outcome["emission"], pending_outcome["emission"]]

    metrics = _build_metrics(events=[verified_event, pending_event], emissions=emissions)

    assert metrics["emission_metrics"]["emission_count"] == 2
    assert metrics["emission_metrics"]["verified_emission_count"] == 1
    assert metrics["emission_metrics"]["pending_emission_count"] == 1
    assert metrics["emission_metrics"]["blocked_emission_count"] == 0


def test_materialized_signal_count() -> None:
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
    materialized = try_materialize_progression_signal_from_runtime_event_v1(event)
    signal = materialized["progression_signal"]
    assert signal is not None

    metrics = _build_metrics(
        events=[event],
        emissions=[materialized["emission"]],
        progression_signals=[signal],
    )

    assert metrics["signal_metrics"]["materialized_signal_count"] == 1
    assert metrics["distributions"]["signal_type_distribution"]["practice_completed"] == 1


def test_trace_status_counts() -> None:
    verified_event = build_practice_completed_event_v1(
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
    pending_event = build_practice_completed_event_v1(
        user_id="user-1",
        definition_code="meditation",
        occurred_at="2026-06-02T08:00:00Z",
        source="user_action",
        verification_status=VERIFICATION_STATUS_PENDING,
        confidence=0.4,
        duration_minutes=10,
        completion_quality="complete",
        source_surface="today_engine",
    )
    rejected_event = build_practice_completed_event_v1(
        user_id="user-1",
        definition_code="breathing",
        occurred_at="2026-06-03T08:00:00Z",
        source="user_action",
        verification_status=VERIFICATION_STATUS_REJECTED,
        confidence=0.2,
        duration_minutes=5,
        completion_quality="partial",
        source_surface="today_engine",
    )

    materialized = try_materialize_progression_signal_from_runtime_event_v1(verified_event)
    pending_emission = try_build_emission_from_runtime_event_v1(pending_event)

    complete_trace = build_practice_runtime_trace_map_v1(
        event=verified_event,
        emission=materialized["emission"],
        progression_signal=materialized["progression_signal"],
        eligibility_snapshot_id="eligibility_snapshot_v1:user-1:2026-06-01T09:00:00Z",
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
        created_at="2026-06-01T09:00:00Z",
    )
    partial_trace = build_practice_runtime_trace_map_v1(
        event=pending_event,
        emission=pending_emission["emission"],
        created_at="2026-06-02T09:00:00Z",
    )
    failed_trace = build_practice_runtime_trace_map_v1(
        event=rejected_event,
        created_at="2026-06-03T09:00:00Z",
    )

    metrics = _build_metrics(trace_maps=[complete_trace, partial_trace, failed_trace])

    assert metrics["trace_metrics"]["complete_trace_count"] == 1
    assert metrics["trace_metrics"]["partial_trace_count"] == 1
    assert metrics["trace_metrics"]["failed_trace_count"] == 1


def test_runtime_entity_distribution() -> None:
    practice = build_practice_completed_event_v1(
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
    ascetic = build_ascetic_compliance_event_v1(
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

    metrics = _build_metrics(events=[practice, ascetic])

    assert metrics["distributions"]["runtime_entity_distribution"]["practice"] == 1
    assert metrics["distributions"]["runtime_entity_distribution"]["ascetic"] == 1
    assert metrics["distributions"]["definition_code_distribution"]["breathing"] == 1
    assert metrics["distributions"]["definition_code_distribution"]["no_sugar"] == 1


def test_blocked_reason_distribution() -> None:
    rejected_event = build_practice_completed_event_v1(
        user_id="user-1",
        definition_code="breathing",
        occurred_at="2026-06-03T08:00:00Z",
        source="user_action",
        verification_status=VERIFICATION_STATUS_REJECTED,
        confidence=0.2,
        duration_minutes=5,
        completion_quality="partial",
        source_surface="today_engine",
    )
    ascetic = build_ascetic_compliance_event_v1(
        user_id="user-1",
        definition_code="no_sugar",
        occurred_at="2026-06-04T20:00:00Z",
        source="user_action",
        verification_status=VERIFICATION_STATUS_PENDING,
        confidence=0.4,
        compliance_status="kept",
        compliance_days=5,
        safety_flag=True,
    )
    habit_fail = build_habit_streak_event_v1(
        user_id="user-1",
        definition_code="daily_breathing",
        occurred_at="2026-06-05T08:00:00Z",
        source="scheduled_check",
        verification_status=VERIFICATION_STATUS_VERIFIED,
        confidence=0.6,
        streak_length=2,
        period_days=7,
        missed_days=3,
        threshold_met=False,
    )

    bridge_outcomes = [
        try_build_emission_from_runtime_event_v1(rejected_event),
        try_build_emission_from_runtime_event_v1(ascetic),
        try_build_emission_from_runtime_event_v1(habit_fail),
    ]
    assert all(outcome["result"] == BRIDGE_RESULT_REJECTED for outcome in bridge_outcomes)

    failed_trace = build_practice_runtime_trace_map_v1(
        event=rejected_event,
        created_at="2026-06-03T09:00:00Z",
    )

    metrics = _build_metrics(
        events=[rejected_event, ascetic, habit_fail],
        trace_maps=[failed_trace],
        bridge_outcomes=bridge_outcomes,
    )

    blocked = metrics["distributions"]["blocked_reason_distribution"]
    assert blocked["rejected_event"] >= 1
    assert blocked["ascetic_blocked"] >= 1
    assert blocked["emission_blocked"] >= 1
    assert metrics["emission_metrics"]["blocked_emission_count"] == 3


def test_read_only_mutation_flags_false() -> None:
    metrics = _build_metrics()

    assert metrics["read_only"] is True
    assert metrics["promotion_allowed"] is False
    assert metrics["profile_update_allowed"] is False
    assert metrics["memory_update_allowed"] is False


def test_output_shape_stable() -> None:
    metrics = _build_metrics()
    assert set(metrics.keys()) == PRACTICE_RUNTIME_SIGNAL_METRICS_V1_KEYS
    assert validate_practice_runtime_signal_metrics_v1(metrics) == []


def test_forbidden_field_rejected_by_validator() -> None:
    metrics = _build_metrics()
    bad = copy.deepcopy(metrics)
    bad["evolution_score"] = 100
    errors = validate_practice_runtime_signal_metrics_v1(bad)
    assert any("forbidden field" in e for e in errors)


def test_window_filters_out_of_range_artifacts() -> None:
    in_window = build_practice_completed_event_v1(
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
    out_window = build_practice_completed_event_v1(
        user_id="user-1",
        definition_code="breathing",
        occurred_at="2026-07-01T08:00:00Z",
        source="user_action",
        verification_status=VERIFICATION_STATUS_VERIFIED,
        confidence=0.7,
        duration_minutes=5,
        completion_quality="complete",
        source_surface="today_engine",
    )

    metrics = _build_metrics(events=[in_window, out_window])
    assert metrics["event_metrics"]["event_count"] == 1
