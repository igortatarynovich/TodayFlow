"""E1.7 — Calendar Intelligence consumer policy tests."""

from __future__ import annotations

import copy

import pytest
from datetime import date

from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache, load_evolution_cd_v1
from todayflow_backend.data.evolution_product_effects_loader import clear_evolution_product_effects_cache
from todayflow_backend.services.calendar_day_record_v1 import build_calendar_day_record_v1
from todayflow_backend.services.calendar_intelligence_consumer_policy_v1 import (
    ARTIFACT_DAY_RECORD,
    ARTIFACT_MONTH_MAP,
    ARTIFACT_RHYTHM_PATTERN,
    BLOCK_CYCLE_VISIBILITY_NOT_ALLOWED,
    BLOCK_HISTORY_WINDOW_EXCEEDED,
    BLOCK_INVALID_CALENDAR_RUNTIME_POLICY,
    BLOCK_MONTH_MAP_NOT_ALLOWED,
    BLOCK_RHYTHM_VISIBILITY_NOT_ALLOWED,
    CALENDAR_INTELLIGENCE_CONSUMER_POLICY_V1_CONTRACT,
    CALENDAR_INTELLIGENCE_CONSUMER_POLICY_V1_KEYS,
    VISIBILITY_BLOCKED,
    VISIBILITY_REDACTED,
    VISIBILITY_VISIBLE,
    apply_calendar_consumer_policy_v1,
    build_calendar_intelligence_consumer_policy_v1,
    evaluate_calendar_artifact_visibility_v1,
    validate_calendar_intelligence_consumer_policy_v1,
)
from todayflow_backend.services.calendar_month_map_v1 import build_calendar_month_map_v1
from todayflow_backend.services.evolution_calendar_runtime_policy_v1 import (
    build_evolution_calendar_runtime_policy_v1,
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


def _calendar_runtime_policy(cd: dict, stage: str, **policy_kwargs):
    progress_by_stage = {
        "seeker": {
            "confirmed_patterns": 0,
            "completed_cycles": 0,
            "reflection_events": 3,
            "active_days": 7,
            "signal_counts": {},
            "confidence": 0.4,
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
        evolution_score_snapshot=420,
        last_evaluated_at="2026-06-01T09:00:00Z",
        cd=cd,
    )
    runtime = build_evolution_effect_runtime_policy_v1(
        evolution_user_state=state,
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
        source_systems_ready={"calendar_intelligence": True, "share_features": True},
        **policy_kwargs,
    )
    calendar_slice = extract_evolution_effect_consumer_slice_v1(runtime, CONSUMER_CALENDAR)
    return build_evolution_calendar_runtime_policy_v1(
        calendar_slice,
        calendar_readiness={"calendar_intelligence": True},
    )


def _consumer_policy(cd: dict, stage: str, **kwargs):
    return build_calendar_intelligence_consumer_policy_v1(
        _calendar_runtime_policy(cd, stage, **kwargs)
    )


def test_architect_full_rhythm_visibility(cd: dict) -> None:
    policy = _consumer_policy(cd, "architect")

    assert policy["day_record_visibility_allowed"] is True
    assert policy["month_map_visibility_allowed"] is True
    assert policy["cycle_overlay_visibility_allowed"] is True
    assert policy["rhythm_pattern_visibility_allowed"] is True
    assert policy["bridge_output_visibility_allowed"] is True
    assert evaluate_calendar_artifact_visibility_v1(policy, ARTIFACT_RHYTHM_PATTERN) == (
        VISIBILITY_VISIBLE,
        [],
    )


def test_seeker_day_only_month_blocked(cd: dict) -> None:
    policy = _consumer_policy(cd, "seeker")

    assert policy["day_record_visibility_allowed"] is True
    assert policy["month_map_visibility_allowed"] is False
    assert policy["rhythm_pattern_visibility_allowed"] is False

    visibility, reasons = evaluate_calendar_artifact_visibility_v1(policy, ARTIFACT_MONTH_MAP)
    assert visibility == VISIBILITY_BLOCKED
    assert BLOCK_MONTH_MAP_NOT_ALLOWED in reasons


def test_practitioner_month_allowed_rhythm_blocked(cd: dict) -> None:
    policy = _consumer_policy(cd, "practitioner")

    assert policy["month_map_visibility_allowed"] is True
    assert policy["rhythm_pattern_visibility_allowed"] is False

    visibility, reasons = evaluate_calendar_artifact_visibility_v1(policy, ARTIFACT_RHYTHM_PATTERN)
    assert visibility == VISIBILITY_BLOCKED
    assert BLOCK_RHYTHM_VISIBILITY_NOT_ALLOWED in reasons


def test_explorer_cycle_visibility_reflected(cd: dict) -> None:
    policy = _consumer_policy(cd, "explorer")

    assert policy["cycle_overlay_visibility_allowed"] is True
    assert policy["rhythm_pattern_visibility_allowed"] is False


def test_invalid_runtime_policy_idle_consumer() -> None:
    policy = build_calendar_intelligence_consumer_policy_v1(None)

    assert policy["calendar_depth"] == "none"
    assert policy["day_record_visibility_allowed"] is False
    assert BLOCK_INVALID_CALENDAR_RUNTIME_POLICY in policy["blocked_artifact_effects"]


def test_month_map_cycle_overlays_redacted(cd: dict) -> None:
    record = build_calendar_day_record_v1(user_id="user-1", date="2026-06-01")
    month_map = build_calendar_month_map_v1(
        user_id="user-1",
        year_month="2026-06",
        day_records=[record],
        cycle_overlays=[
            {
                "cycle_overlay_id": "co-1",
                "start_date": "2026-06-01",
                "end_date": "2026-06-07",
            }
        ],
    )

    runtime = _calendar_runtime_policy(cd, "practitioner")
    runtime = copy.deepcopy(runtime)
    runtime["cycle_visibility_allowed"] = False
    policy = build_calendar_intelligence_consumer_policy_v1(runtime)

    outcome = apply_calendar_consumer_policy_v1(policy, ARTIFACT_MONTH_MAP, month_map)

    assert outcome["result"] == VISIBILITY_REDACTED
    assert outcome["artifact"] is not None
    assert outcome["artifact"]["cycle_overlays"] == []
    assert BLOCK_CYCLE_VISIBILITY_NOT_ALLOWED in outcome["reasons"]


def test_day_record_history_window_blocks_old_record(cd: dict) -> None:
    policy = _consumer_policy(cd, "seeker")
    old_record = build_calendar_day_record_v1(user_id="user-1", date="2026-01-01")

    outcome = apply_calendar_consumer_policy_v1(
        policy,
        ARTIFACT_DAY_RECORD,
        old_record,
        reference_date=date(2026, 6, 1),
    )

    assert outcome["result"] == VISIBILITY_BLOCKED
    assert BLOCK_HISTORY_WINDOW_EXCEEDED in outcome["reasons"]


def test_month_map_history_window_redacts_old_days(cd: dict) -> None:
    records = [
        build_calendar_day_record_v1(user_id="user-1", date="2026-06-01"),
        build_calendar_day_record_v1(user_id="user-1", date="2026-06-10"),
    ]
    month_map = build_calendar_month_map_v1(
        user_id="user-1",
        year_month="2026-06",
        day_records=records,
    )
    runtime = _calendar_runtime_policy(cd, "practitioner")
    runtime = copy.deepcopy(runtime)
    runtime["history_window_days"] = 7
    policy = build_calendar_intelligence_consumer_policy_v1(runtime)

    outcome = apply_calendar_consumer_policy_v1(
        policy,
        ARTIFACT_MONTH_MAP,
        month_map,
        reference_date=date(2026, 6, 15),
    )

    assert outcome["result"] == VISIBILITY_REDACTED
    assert outcome["artifact"] is not None
    assert len(outcome["artifact"]["day_records"]) == 1
    assert BLOCK_HISTORY_WINDOW_EXCEEDED in outcome["reasons"]


def test_mutation_and_insight_flags_false(cd: dict) -> None:
    policy = _consumer_policy(cd, "architect")

    assert policy["calendar_mutation_allowed"] is False
    assert policy["insight_generation_allowed"] is False
    assert policy["recommendation_allowed"] is False
    assert policy["profile_update_allowed"] is False
    assert policy["memory_update_allowed"] is False


def test_forbidden_fields_rejected_on_validate(cd: dict) -> None:
    policy = _consumer_policy(cd, "architect")
    bad = copy.deepcopy(policy)
    bad["insight"] = "weekly overload"
    assert validate_calendar_intelligence_consumer_policy_v1(bad)


def test_output_shape_stable(cd: dict) -> None:
    policy = _consumer_policy(cd, "architect")

    assert policy["contract_version"] == CALENDAR_INTELLIGENCE_CONSUMER_POLICY_V1_CONTRACT
    assert set(policy.keys()) == CALENDAR_INTELLIGENCE_CONSUMER_POLICY_V1_KEYS
    assert validate_calendar_intelligence_consumer_policy_v1(policy) == []
