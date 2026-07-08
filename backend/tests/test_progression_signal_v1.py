"""B1.3 — Progression signal contract tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache
from todayflow_backend.data.progression_signal_registry_loader import (
    PROGRESSION_SIGNAL_REGISTRY_V1_CONTRACT,
    clear_progression_signal_registry_cache,
    load_progression_signal_registry_v1,
    validate_progression_signal_registry_v1,
)
from todayflow_backend.services.evolution_user_state_v1 import PROGRESS_SNAPSHOT_V1_KEYS
from todayflow_backend.services.progression_signal_v1 import (
    PROGRESSION_SIGNAL_V1_CONTRACT,
    PROGRESSION_SIGNAL_V1_KEYS,
    VERIFICATION_STATUS_PENDING,
    VERIFICATION_STATUS_VERIFIED,
    aggregate_eligibility_progress_from_signals_v1,
    build_progression_signal_v1,
    validate_progression_signal_v1,
)


@pytest.fixture(autouse=True)
def _clear_caches() -> None:
    clear_evolution_cd_cache()
    clear_progression_signal_registry_cache()
    yield
    clear_evolution_cd_cache()
    clear_progression_signal_registry_cache()


@pytest.fixture
def registry() -> dict:
    return load_progression_signal_registry_v1()


@pytest.fixture
def verified_signal(registry: dict) -> dict:
    return build_progression_signal_v1(
        user_id="user-123",
        signal_type="evening_reflection_confirmed",
        source_engine="ritual",
        source_event_id="evt-1",
        observed_at="2026-05-30T20:00:00Z",
        verification_status=VERIFICATION_STATUS_VERIFIED,
        confidence=0.7,
        evidence_count=3,
        evidence_window_days=7,
        path_theme_code="clarity",
        registry=registry,
    )


def test_registry_loads_and_matches_b1_1_types(registry: dict) -> None:
    assert registry["contract_version"] == PROGRESSION_SIGNAL_REGISTRY_V1_CONTRACT
    assert validate_progression_signal_registry_v1(registry) == []
    assert set(registry["signal_types"].keys()) == {
        "practice_completed",
        "habit_streak_confirmed",
        "goal_milestone_reached",
        "evening_reflection_confirmed",
        "cycle_completed",
        "confirmed_pattern",
        "ritual_streak_confirmed",
        "weekly_goal_completed",
    }


def test_valid_verified_signal_passes(verified_signal: dict) -> None:
    assert validate_progression_signal_v1(verified_signal) == []
    assert verified_signal["contributes_to_gate_eligibility"] is True
    assert verified_signal["promotion_allowed"] is False


def test_unknown_signal_type_invalid(verified_signal: dict) -> None:
    broken = copy.deepcopy(verified_signal)
    broken["signal_type"] = "login_count"
    errors = validate_progression_signal_v1(broken)
    assert any("unknown signal_type" in e for e in errors)


def test_unverified_signal_cannot_contribute(registry: dict) -> None:
    pending = build_progression_signal_v1(
        user_id="user-123",
        signal_type="practice_completed",
        source_engine="practice",
        source_event_id="evt-2",
        observed_at="2026-05-29T08:00:00Z",
        verification_status=VERIFICATION_STATUS_PENDING,
        confidence=0.9,
        evidence_count=1,
        evidence_window_days=1,
        registry=registry,
    )
    assert pending["contributes_to_gate_eligibility"] is False
    assert validate_progression_signal_v1(pending) == []


def test_promotion_allowed_always_false(registry: dict) -> None:
    signal = build_progression_signal_v1(
        user_id="user-123",
        signal_type="confirmed_pattern",
        source_engine="pattern",
        source_event_id="evt-3",
        observed_at="2026-05-28T12:00:00Z",
        verification_status=VERIFICATION_STATUS_VERIFIED,
        confidence=0.8,
        evidence_count=5,
        evidence_window_days=21,
        registry=registry,
    )
    assert signal["promotion_allowed"] is False

    broken = copy.deepcopy(signal)
    broken["promotion_allowed"] = True
    errors = validate_progression_signal_v1(broken)
    assert any("promotion_allowed must be false" in e for e in errors)


def test_achievement_commerce_fields_forbidden(verified_signal: dict) -> None:
    broken = copy.deepcopy(verified_signal)
    broken["achievement_unlocked"] = True
    errors = validate_progression_signal_v1(broken)
    assert any("forbidden field" in e for e in errors)


def test_source_engine_must_match_registry(registry: dict) -> None:
    with pytest.raises(Exception) as exc:
        build_progression_signal_v1(
            user_id="user-123",
            signal_type="practice_completed",
            source_engine="commerce",
            source_event_id="evt-4",
            observed_at="2026-05-27T12:00:00Z",
            verification_status=VERIFICATION_STATUS_VERIFIED,
            confidence=0.8,
            evidence_count=1,
            evidence_window_days=1,
            registry=registry,
        )
    assert "source_engine" in str(exc.value)


def test_unknown_path_theme_invalid(verified_signal: dict) -> None:
    broken = copy.deepcopy(verified_signal)
    broken["path_theme_code"] = "unknown_theme"
    errors = validate_progression_signal_v1(broken)
    assert any("unknown path_theme_code" in e for e in errors)


def test_signal_type_must_be_allowed_for_path_theme(registry: dict, verified_signal: dict) -> None:
    broken = copy.deepcopy(verified_signal)
    broken["signal_type"] = "goal_milestone_reached"
    broken["source_engine"] = "goal"
    broken["path_theme_code"] = "body"
    errors = validate_progression_signal_v1(broken)
    assert any("not allowed for path theme" in e for e in errors)


def test_output_shape_stable(verified_signal: dict) -> None:
    assert verified_signal["contract_version"] == PROGRESSION_SIGNAL_V1_CONTRACT
    assert set(verified_signal.keys()) == set(PROGRESSION_SIGNAL_V1_KEYS)


def test_aggregation_produces_progress_snapshot_shape(registry: dict) -> None:
    signals = [
        build_progression_signal_v1(
            user_id="user-123",
            signal_type="ritual_streak_confirmed",
            source_engine="ritual",
            source_event_id="evt-a",
            observed_at="2026-05-20T07:00:00Z",
            verification_status=VERIFICATION_STATUS_VERIFIED,
            confidence=0.6,
            evidence_count=3,
            evidence_window_days=7,
            registry=registry,
        ),
        build_progression_signal_v1(
            user_id="user-123",
            signal_type="evening_reflection_confirmed",
            source_engine="ritual",
            source_event_id="evt-b",
            observed_at="2026-05-21T21:00:00Z",
            verification_status=VERIFICATION_STATUS_VERIFIED,
            confidence=0.65,
            evidence_count=2,
            evidence_window_days=7,
            registry=registry,
        ),
        build_progression_signal_v1(
            user_id="user-123",
            signal_type="practice_completed",
            source_engine="practice",
            source_event_id="evt-c",
            observed_at="2026-05-21T09:00:00Z",
            verification_status=VERIFICATION_STATUS_PENDING,
            confidence=0.95,
            evidence_count=1,
            evidence_window_days=1,
            registry=registry,
        ),
    ]

    progress = aggregate_eligibility_progress_from_signals_v1(signals, registry=registry)
    assert set(progress.keys()) == set(PROGRESS_SNAPSHOT_V1_KEYS)
    assert progress["signal_counts"]["ritual_streak_confirmed"] == 1
    assert progress["signal_counts"]["evening_reflection_confirmed"] == 1
    assert "practice_completed" not in progress["signal_counts"]
    assert progress["reflection_events"] == 1
    assert progress["active_days"] == 2
