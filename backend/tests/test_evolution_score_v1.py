"""B1.4 — Evolution Score / ECC integration path tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache
from todayflow_backend.data.evolution_score_contract_loader import (
    EVOLUTION_SCORE_CONTRACT_V1,
    clear_evolution_score_contract_cache,
    load_evolution_score_contract_v1,
    validate_evolution_score_contract_v1,
)
from todayflow_backend.data.progression_signal_registry_loader import (
    clear_progression_signal_registry_cache,
)
from todayflow_backend.services.evolution_score_v1 import (
    EVOLUTION_SCORE_CALCULATION_V1_CONTRACT,
    EVOLUTION_SCORE_CALCULATION_V1_KEYS,
    ECC_COMPONENT_SCORE_KEYS,
    build_evolution_state_with_ecc_v1,
    calculate_evolution_score_v1,
    validate_evolution_score_calculation_v1,
)
from todayflow_backend.services.progression_signal_v1 import (
    VERIFICATION_STATUS_VERIFIED,
    build_progression_signal_v1,
)
from todayflow_backend.services.evolution_user_state_v1 import validate_evolution_user_state_v1


@pytest.fixture(autouse=True)
def _clear_caches() -> None:
    clear_evolution_cd_cache()
    clear_progression_signal_registry_cache()
    clear_evolution_score_contract_cache()
    yield
    clear_evolution_cd_cache()
    clear_progression_signal_registry_cache()
    clear_evolution_score_contract_cache()


@pytest.fixture
def contract() -> dict:
    return load_evolution_score_contract_v1()


@pytest.fixture
def verified_signals() -> list[dict]:
    common = {
        "verification_status": VERIFICATION_STATUS_VERIFIED,
        "evidence_count": 3,
        "evidence_window_days": 7,
    }
    return [
        build_progression_signal_v1(
            user_id="user-123",
            signal_type="practice_completed",
            source_engine="practice",
            source_event_id="evt-1",
            observed_at="2026-05-20T08:00:00Z",
            confidence=0.7,
            **common,
        ),
        build_progression_signal_v1(
            user_id="user-123",
            signal_type="evening_reflection_confirmed",
            source_engine="ritual",
            source_event_id="evt-2",
            observed_at="2026-05-21T21:00:00Z",
            confidence=0.65,
            **common,
        ),
        build_progression_signal_v1(
            user_id="user-123",
            signal_type="ritual_streak_confirmed",
            source_engine="ritual",
            source_event_id="evt-3",
            observed_at="2026-05-22T07:00:00Z",
            confidence=0.6,
            **common,
        ),
    ]


def test_ecc_contract_loads(contract: dict) -> None:
    assert contract["contract_version"] == EVOLUTION_SCORE_CONTRACT_V1
    assert validate_evolution_score_contract_v1(contract) == []
    assert abs(sum(contract["weights"].values()) - 1.0) < 0.001


def test_valid_calculation_passes(verified_signals: list[dict]) -> None:
    result = calculate_evolution_score_v1(
        user_id="user-123",
        signals=verified_signals,
        previous_evolution_score=100,
    )
    assert validate_evolution_score_calculation_v1(result) == []
    assert result["evolution_score"] >= 100
    assert result["verified_signal_count"] == 3


def test_evolution_score_bounded_0_1000(verified_signals: list[dict]) -> None:
    result = calculate_evolution_score_v1(
        user_id="user-123",
        signals=verified_signals,
        previous_evolution_score=990,
    )
    assert 0 <= result["evolution_score"] <= 1000


def test_promotion_and_api_exposure_always_false(verified_signals: list[dict]) -> None:
    result = calculate_evolution_score_v1(user_id="user-123", signals=verified_signals)
    assert result["promotion_allowed"] is False
    assert result["api_exposure_allowed"] is False

    broken = copy.deepcopy(result)
    broken["api_exposure_allowed"] = True
    errors = validate_evolution_score_calculation_v1(broken)
    assert any("api_exposure_allowed must be false" in e for e in errors)


def test_unverified_signals_excluded(contract: dict) -> None:
    pending = build_progression_signal_v1(
        user_id="user-123",
        signal_type="practice_completed",
        source_engine="practice",
        source_event_id="evt-p",
        observed_at="2026-05-20T08:00:00Z",
        verification_status="pending",
        confidence=0.9,
        evidence_count=1,
        evidence_window_days=1,
    )
    result = calculate_evolution_score_v1(user_id="user-123", signals=[pending])
    assert result["verified_signal_count"] == 0
    assert any("not eligible" in e for e in result["excluded_inputs"])


def test_forbidden_achievement_field_rejected_by_validator(verified_signals: list[dict]) -> None:
    result = calculate_evolution_score_v1(user_id="user-123", signals=verified_signals)
    broken = copy.deepcopy(result)
    broken["achievement_id"] = "ach-1"
    errors = validate_evolution_score_calculation_v1(broken)
    assert any("forbidden field" in e for e in errors)


def test_weights_snapshot_matches_contract(
    verified_signals: list[dict],
    contract: dict,
) -> None:
    result = calculate_evolution_score_v1(
        user_id="user-123",
        signals=verified_signals,
        contract=contract,
    )
    assert result["weights_snapshot"] == contract["weights"]


def test_output_shape_stable(verified_signals: list[dict]) -> None:
    result = calculate_evolution_score_v1(user_id="user-123", signals=verified_signals)
    assert result["contract_version"] == EVOLUTION_SCORE_CALCULATION_V1_CONTRACT
    assert set(result.keys()) == set(EVOLUTION_SCORE_CALCULATION_V1_KEYS)
    assert set(result["component_scores"].keys()) == set(ECC_COMPONENT_SCORE_KEYS)


def test_integration_builds_user_state(verified_signals: list[dict]) -> None:
    score_calc, state = build_evolution_state_with_ecc_v1(
        user_id="user-123",
        current_stage="seeker",
        stage_started_at="2026-05-01T00:00:00Z",
        active_path_themes=["discipline"],
        completed_path_themes=[],
        signals=verified_signals,
        previous_evolution_score=50,
    )
    assert validate_evolution_score_calculation_v1(score_calc) == []
    assert validate_evolution_user_state_v1(state) == []
    assert state["evolution_score_snapshot"] == score_calc["evolution_score"]
    assert state["stage_gate_eligibility"]["promotion_allowed"] is False


def test_cum_confidence_affects_profile_quality_component(verified_signals: list[dict]) -> None:
    high = calculate_evolution_score_v1(
        user_id="user-123",
        signals=verified_signals,
        cum_confidence_snapshot=1.0,
    )
    low = calculate_evolution_score_v1(
        user_id="user-123",
        signals=verified_signals,
        cum_confidence_snapshot=0.2,
    )
    assert (
        low["component_scores"]["profile_quality"]
        <= high["component_scores"]["profile_quality"]
    )
