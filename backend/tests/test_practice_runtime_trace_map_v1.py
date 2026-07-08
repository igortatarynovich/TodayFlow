"""C2.3 — Practice runtime trace map tests."""

from __future__ import annotations

import copy
import uuid

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
from todayflow_backend.services.evolution_score_v1 import build_evolution_state_with_ecc_v1
from todayflow_backend.services.practice_runtime_event_emission_bridge_v1 import (
    try_materialize_progression_signal_from_runtime_event_v1,
)
from todayflow_backend.services.practice_runtime_event_v1 import (
    build_ascetic_compliance_event_v1,
    build_habit_streak_event_v1,
    build_practice_completed_event_v1,
)
from todayflow_backend.services.practice_runtime_trace_map_v1 import (
    PRACTICE_RUNTIME_TRACE_MAP_V1_CONTRACT,
    PRACTICE_RUNTIME_TRACE_MAP_V1_KEYS,
    TRACE_STATUS_COMPLETE,
    TRACE_STATUS_FAILED,
    TRACE_STATUS_PARTIAL,
    build_practice_runtime_trace_map_v1,
    resolve_eligibility_snapshot_id_from_user_state_v1,
    resolve_evolution_score_snapshot_id_from_calculation_v1,
    validate_practice_runtime_trace_map_v1,
)
from todayflow_backend.services.progression_signal_v1 import VERIFICATION_STATUS_PENDING, VERIFICATION_STATUS_REJECTED, VERIFICATION_STATUS_VERIFIED


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


def _verified_practice_event(event_id: str | None = None) -> dict:
    return build_practice_completed_event_v1(
        user_id="user-1",
        definition_code="breathing",
        occurred_at="2026-06-01T08:00:00Z",
        source="user_action",
        verification_status=VERIFICATION_STATUS_VERIFIED,
        confidence=0.7,
        duration_minutes=5,
        completion_quality="complete",
        source_surface="today_engine",
        event_id=event_id or str(uuid.uuid4()),
    )


def test_full_chain_complete() -> None:
    event_id = "evt-trace-full-1"
    event = _verified_practice_event(event_id=event_id)
    materialized = try_materialize_progression_signal_from_runtime_event_v1(
        event,
        path_theme_code="discipline",
    )
    signal = materialized["progression_signal"]
    assert signal is not None

    score_calc, user_state = build_evolution_state_with_ecc_v1(
        user_id="user-1",
        current_stage="seeker",
        stage_started_at="2026-05-01T00:00:00Z",
        active_path_themes=["discipline"],
        completed_path_themes=[],
        signals=[signal],
        previous_evolution_score=0,
    )
    eligibility_id = resolve_eligibility_snapshot_id_from_user_state_v1(user_state)
    score_id = resolve_evolution_score_snapshot_id_from_calculation_v1(score_calc)
    assert eligibility_id is not None
    assert score_id is not None

    trace_map = build_practice_runtime_trace_map_v1(
        event=event,
        emission=materialized["emission"],
        progression_signal=signal,
        eligibility_snapshot_id=eligibility_id,
        evolution_score_snapshot_id=score_id,
    )

    assert trace_map["contract_version"] == PRACTICE_RUNTIME_TRACE_MAP_V1_CONTRACT
    assert set(trace_map.keys()) == PRACTICE_RUNTIME_TRACE_MAP_V1_KEYS
    assert trace_map["trace_status"] == TRACE_STATUS_COMPLETE
    assert trace_map["missing_links"] == []
    assert trace_map["mutation_allowed"] is False
    assert trace_map["runtime_event_id"] == event_id
    assert trace_map["emission_id"] == materialized["emission"]["emission_id"]
    assert trace_map["progression_signal_id"] == signal["progression_signal_id"]
    assert trace_map["signal_type"] == "practice_completed"
    assert validate_practice_runtime_trace_map_v1(
        trace_map,
        event=event,
        emission=materialized["emission"],
        progression_signal=signal,
    ) == []


def test_pending_emission_partial() -> None:
    event = build_practice_completed_event_v1(
        user_id="user-1",
        definition_code="breathing",
        occurred_at="2026-06-01T08:00:00Z",
        source="user_action",
        verification_status=VERIFICATION_STATUS_PENDING,
        confidence=0.4,
        duration_minutes=5,
        completion_quality="complete",
        source_surface="today_engine",
    )

    materialized = try_materialize_progression_signal_from_runtime_event_v1(event)
    assert materialized["progression_signal"] is None

    trace_map = build_practice_runtime_trace_map_v1(
        event=event,
        emission=materialized["emission"],
    )

    assert trace_map["trace_status"] == TRACE_STATUS_PARTIAL
    assert "progression_signal" in trace_map["missing_links"]
    assert "eligibility_snapshot" in trace_map["missing_links"]
    assert "evolution_score_snapshot" in trace_map["missing_links"]
    assert trace_map["emission_id"] is not None


def test_rejected_event_failed() -> None:
    event = build_practice_completed_event_v1(
        user_id="user-1",
        definition_code="breathing",
        occurred_at="2026-06-01T08:00:00Z",
        source="user_action",
        verification_status=VERIFICATION_STATUS_REJECTED,
        confidence=0.2,
        duration_minutes=5,
        completion_quality="complete",
        source_surface="today_engine",
    )

    trace_map = build_practice_runtime_trace_map_v1(event=event)

    assert trace_map["trace_status"] == TRACE_STATUS_FAILED
    assert trace_map["emission_id"] is None
    assert "emission" in trace_map["missing_links"]


def test_ascetic_blocked_failed() -> None:
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

    trace_map = build_practice_runtime_trace_map_v1(event=event)

    assert trace_map["trace_status"] == TRACE_STATUS_FAILED
    assert trace_map["runtime_entity_type"] == "ascetic"
    assert trace_map["signal_type"] is None


def test_missing_score_snapshot_partial() -> None:
    event = _verified_practice_event()
    materialized = try_materialize_progression_signal_from_runtime_event_v1(event)
    signal = materialized["progression_signal"]
    assert signal is not None

    _, user_state = build_evolution_state_with_ecc_v1(
        user_id="user-1",
        current_stage="seeker",
        stage_started_at="2026-05-01T00:00:00Z",
        active_path_themes=["discipline"],
        completed_path_themes=[],
        signals=[signal],
    )

    trace_map = build_practice_runtime_trace_map_v1(
        event=event,
        emission=materialized["emission"],
        progression_signal=signal,
        eligibility_snapshot_id=resolve_eligibility_snapshot_id_from_user_state_v1(user_state),
    )

    assert trace_map["trace_status"] == TRACE_STATUS_PARTIAL
    assert trace_map["missing_links"] == ["evolution_score_snapshot"]


def test_missing_eligibility_snapshot_partial() -> None:
    event = _verified_practice_event()
    materialized = try_materialize_progression_signal_from_runtime_event_v1(event)
    signal = materialized["progression_signal"]
    assert signal is not None

    score_calc, _ = build_evolution_state_with_ecc_v1(
        user_id="user-1",
        current_stage="seeker",
        stage_started_at="2026-05-01T00:00:00Z",
        active_path_themes=["discipline"],
        completed_path_themes=[],
        signals=[signal],
    )

    trace_map = build_practice_runtime_trace_map_v1(
        event=event,
        emission=materialized["emission"],
        progression_signal=signal,
        evolution_score_snapshot_id=resolve_evolution_score_snapshot_id_from_calculation_v1(score_calc),
    )

    assert trace_map["trace_status"] == TRACE_STATUS_PARTIAL
    assert trace_map["missing_links"] == ["eligibility_snapshot"]


def test_trace_preserves_ids() -> None:
    event_id = "evt-trace-ids-1"
    event = _verified_practice_event(event_id=event_id)
    materialized = try_materialize_progression_signal_from_runtime_event_v1(event)
    signal = materialized["progression_signal"]
    assert signal is not None

    trace_map = build_practice_runtime_trace_map_v1(
        event=event,
        emission=materialized["emission"],
        progression_signal=signal,
    )

    assert trace_map["runtime_event_id"] == event_id
    assert trace_map["emission_id"] == materialized["emission"]["emission_id"]
    assert trace_map["progression_signal_id"] == signal["progression_signal_id"]
    assert signal["source_event_id"] == event_id
    assert materialized["emission"]["runtime_event_id"] == event_id


def test_mutation_allowed_false() -> None:
    trace_map = build_practice_runtime_trace_map_v1(event=_verified_practice_event())
    assert trace_map["mutation_allowed"] is False


def test_no_profile_memory_stage_fields() -> None:
    trace_map = build_practice_runtime_trace_map_v1(event=_verified_practice_event())
    bad = copy.deepcopy(trace_map)
    bad["profile_update"] = True
    errors = validate_practice_runtime_trace_map_v1(bad)
    assert any("forbidden field" in e for e in errors)


def test_output_shape_stable() -> None:
    trace_map = build_practice_runtime_trace_map_v1(event=_verified_practice_event())
    assert set(trace_map.keys()) == PRACTICE_RUNTIME_TRACE_MAP_V1_KEYS


def test_emission_blocked_failed() -> None:
    event = build_habit_streak_event_v1(
        user_id="user-1",
        definition_code="daily_breathing",
        occurred_at="2026-06-01T08:00:00Z",
        source="scheduled_check",
        verification_status=VERIFICATION_STATUS_VERIFIED,
        confidence=0.6,
        streak_length=2,
        period_days=7,
        missed_days=3,
        threshold_met=False,
    )

    trace_map = build_practice_runtime_trace_map_v1(event=event)

    assert trace_map["trace_status"] == TRACE_STATUS_FAILED
    assert "emission" in trace_map["missing_links"]
