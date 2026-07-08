"""B1.2 — Evolution user state contract tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache, load_evolution_cd_v1
from todayflow_backend.services.evolution_user_state_v1 import (
    EVOLUTION_USER_STATE_V1_CONTRACT,
    EVOLUTION_USER_STATE_V1_KEYS,
    PROGRESS_SNAPSHOT_V1_KEYS,
    STAGE_GATE_ELIGIBILITY_V1_KEYS,
    build_evolution_user_state_v1,
    build_stage_gate_eligibility_snapshot_v1,
    validate_evolution_user_state_v1,
)


@pytest.fixture(autouse=True)
def _clear_cd_cache() -> None:
    clear_evolution_cd_cache()
    yield
    clear_evolution_cd_cache()


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
def valid_state(cd: dict, full_progress: dict) -> dict:
    return build_evolution_user_state_v1(
        user_id="user-123",
        current_stage="seeker",
        stage_started_at="2026-05-01T00:00:00Z",
        active_path_themes=["discipline", "energy"],
        completed_path_themes=[],
        progress_snapshot=full_progress,
        evolution_score_snapshot=120,
        last_evaluated_at="2026-05-31T12:00:00Z",
        cd=cd,
    )


def test_valid_user_state_passes(valid_state: dict) -> None:
    assert validate_evolution_user_state_v1(valid_state) == []
    assert valid_state["contract_version"] == EVOLUTION_USER_STATE_V1_CONTRACT
    assert valid_state["stage_gate_eligibility"]["promotion_allowed"] is False


def test_unknown_stage_invalid(valid_state: dict) -> None:
    broken = copy.deepcopy(valid_state)
    broken["current_stage"] = "novice"
    errors = validate_evolution_user_state_v1(broken)
    assert any("unknown current_stage" in e for e in errors)


def test_unknown_path_theme_invalid(valid_state: dict) -> None:
    broken = copy.deepcopy(valid_state)
    broken["active_path_themes"] = ["discipline", "unknown_theme"]
    errors = validate_evolution_user_state_v1(broken)
    assert any("unknown active_path_theme" in e for e in errors)


def test_non_sequential_gate_target_invalid(valid_state: dict) -> None:
    broken = copy.deepcopy(valid_state)
    broken["current_stage_gate_target"]["to_stage"] = "practitioner"
    errors = validate_evolution_user_state_v1(broken)
    assert any("sequential" in e for e in errors)


def test_eligibility_cannot_promote(valid_state: dict) -> None:
    eligibility = valid_state["stage_gate_eligibility"]
    assert eligibility["promotion_allowed"] is False
    assert "promoted_stage" not in valid_state
    broken = copy.deepcopy(valid_state)
    broken["stage_gate_eligibility"]["promotion_allowed"] = True
    errors = validate_evolution_user_state_v1(broken)
    assert any("promotion_allowed must be false" in e for e in errors)


def test_promotion_allowed_always_false_in_builder(cd: dict, full_progress: dict) -> None:
    state = build_evolution_user_state_v1(
        user_id="user-456",
        current_stage="seeker",
        stage_started_at="2026-05-01T00:00:00Z",
        active_path_themes=["discipline"],
        completed_path_themes=[],
        progress_snapshot=full_progress,
        evolution_score_snapshot=200,
        last_evaluated_at="2026-05-31T12:00:00Z",
        cd=cd,
    )
    assert state["stage_gate_eligibility"]["promotion_allowed"] is False


def test_achievement_commerce_fields_forbidden(valid_state: dict) -> None:
    broken = copy.deepcopy(valid_state)
    broken["achievement_unlocked"] = True
    errors = validate_evolution_user_state_v1(broken)
    assert any("forbidden field" in e for e in errors)

    broken2 = copy.deepcopy(valid_state)
    broken2["stage_gate_eligibility"]["progress_snapshot"]["commerce_purchase"] = 1
    errors2 = validate_evolution_user_state_v1(broken2)
    assert any("forbidden" in e for e in errors2)


def test_active_completed_path_themes_no_overlap(valid_state: dict) -> None:
    broken = copy.deepcopy(valid_state)
    broken["completed_path_themes"] = ["discipline"]
    errors = validate_evolution_user_state_v1(broken)
    assert any("overlap" in e for e in errors)


def test_status_valid(valid_state: dict) -> None:
    broken = copy.deepcopy(valid_state)
    broken["status"] = "deleted"
    errors = validate_evolution_user_state_v1(broken)
    assert any("invalid status" in e for e in errors)


def test_output_shape_stable(valid_state: dict) -> None:
    assert set(valid_state.keys()) == set(EVOLUTION_USER_STATE_V1_KEYS)
    eligibility = valid_state["stage_gate_eligibility"]
    assert set(eligibility.keys()) == set(STAGE_GATE_ELIGIBILITY_V1_KEYS)
    progress = eligibility["progress_snapshot"]
    assert set(progress.keys()) == set(PROGRESS_SNAPSHOT_V1_KEYS)


def test_eligibility_snapshot_marks_ineligible_when_progress_low(cd: dict) -> None:
    eligibility = build_stage_gate_eligibility_snapshot_v1(
        current_stage="seeker",
        progress_snapshot={
            "confirmed_patterns": 0,
            "completed_cycles": 0,
            "reflection_events": 0,
            "active_days": 0,
            "signal_counts": {},
            "confidence": 0.1,
        },
        cd=cd,
    )
    assert eligibility is not None
    assert eligibility["eligible"] is False
    assert eligibility["promotion_allowed"] is False
    assert len(eligibility["missing_requirements"]) > 0


def test_eligibility_snapshot_marks_eligible_without_promotion(cd: dict, full_progress: dict) -> None:
    eligibility = build_stage_gate_eligibility_snapshot_v1(
        current_stage="seeker",
        progress_snapshot=full_progress,
        cd=cd,
    )
    assert eligibility is not None
    assert eligibility["eligible"] is True
    assert eligibility["promotion_allowed"] is False
