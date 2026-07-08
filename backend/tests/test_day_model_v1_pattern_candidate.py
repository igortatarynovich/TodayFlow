"""P1.17 — Pattern candidate aggregation tests."""

from __future__ import annotations

import pytest

from todayflow_backend.services.day_model_v1_pattern_candidate import (
    CANDIDATE_TYPE_SURFACE_PREFERENCE,
    DAY_PATTERN_CANDIDATE_V1_CONTRACT,
    DAY_PATTERN_CANDIDATE_V1_KEYS,
    MIN_SIGNALS_FOR_PROMOTION,
    evaluate_promotion_eligible,
    try_aggregate_pattern_candidate_v1,
    validate_day_pattern_candidate_v1,
)
from todayflow_backend.services.day_model_v1_surface_learning_signal import (
    DAY_SURFACE_LEARNING_SIGNAL_V1_CONTRACT,
    SIGNAL_DIRECTION_NEGATIVE,
    SIGNAL_DIRECTION_NEUTRAL,
    SIGNAL_DIRECTION_POSITIVE,
)

SURFACE = "today_hero"
AGG_KEY = "today_hero"


def _signal(
    signal_id: str,
    *,
    direction: str = SIGNAL_DIRECTION_POSITIVE,
    created_at: str = "2026-05-01T12:00:00Z",
    surface: str = SURFACE,
) -> dict:
    return {
        "contract_version": DAY_SURFACE_LEARNING_SIGNAL_V1_CONTRACT,
        "learning_signal_id": signal_id,
        "reaction_id": f"react-{signal_id}",
        "exposure_id": f"exp-{signal_id}",
        "audit_id": f"audit-{signal_id}",
        "surface": surface,
        "signal_type": "useful",
        "signal_strength": 0.7,
        "signal_direction": direction,
        "evidence_type": "behavioral",
        "confidence": "medium-high",
        "source_keys": ["day.guidance.headline"],
        "selected_source": "deterministic",
        "used_llm": False,
        "dataset_candidate_effect": "keep_candidate",
        "created_at": created_at,
        "memory_update_allowed": False,
        "ranking_update_allowed": False,
    }


def _aggregate(signals, **kwargs):
    return try_aggregate_pattern_candidate_v1(
        signals,
        candidate_type=CANDIDATE_TYPE_SURFACE_PREFERENCE,
        aggregation_key=AGG_KEY,
        **kwargs,
    )


def test_one_signal_does_not_create_candidate():
    assert _aggregate([_signal("lsig-1")]) is None


def test_two_contradictory_signals_do_not_create_candidate():
    signals = [
        _signal("lsig-pos", direction=SIGNAL_DIRECTION_POSITIVE),
        _signal("lsig-neg", direction=SIGNAL_DIRECTION_NEGATIVE),
    ]
    assert _aggregate(signals) is None


def test_coherent_signals_create_candidate():
    signals = [
        _signal("lsig-1", direction=SIGNAL_DIRECTION_POSITIVE),
        _signal("lsig-2", direction=SIGNAL_DIRECTION_POSITIVE),
        _signal("lsig-3", direction=SIGNAL_DIRECTION_POSITIVE),
    ]
    candidate = _aggregate(signals)
    assert candidate is not None
    assert candidate["status"] == "formed"
    assert candidate["signal_count"] == 3
    assert len(candidate["source_signals"]) == 3


def test_positive_negative_counted_separately():
    signals = [
        _signal("lsig-1", direction=SIGNAL_DIRECTION_POSITIVE),
        _signal("lsig-2", direction=SIGNAL_DIRECTION_POSITIVE),
        _signal("lsig-3", direction=SIGNAL_DIRECTION_NEUTRAL),
    ]
    candidate = _aggregate(signals)
    assert candidate is not None
    assert candidate["positive_count"] == 2
    assert candidate["negative_count"] == 0
    assert candidate["neutral_count"] == 1


def test_confidence_grows_with_evidence_volume():
    small = _aggregate(
        [
            _signal("lsig-1", direction=SIGNAL_DIRECTION_POSITIVE),
            _signal("lsig-2", direction=SIGNAL_DIRECTION_POSITIVE),
            _signal("lsig-3", direction=SIGNAL_DIRECTION_POSITIVE),
        ]
    )
    large = _aggregate(
        [
            _signal(f"lsig-{i}", direction=SIGNAL_DIRECTION_POSITIVE)
            for i in range(MIN_SIGNALS_FOR_PROMOTION)
        ]
    )
    assert small is not None and large is not None
    assert large["confidence"] > small["confidence"]


def test_promotion_gate():
    short_window = _aggregate(
        [
            _signal(f"lsig-{i}", direction=SIGNAL_DIRECTION_POSITIVE, created_at="2026-05-01T12:00:00Z")
            for i in range(MIN_SIGNALS_FOR_PROMOTION)
        ]
    )
    assert short_window is not None
    assert short_window["promotion_eligible"] is False

    long_window = _aggregate(
        [
            _signal(
                f"lsig-{i}",
                direction=SIGNAL_DIRECTION_POSITIVE,
                created_at=created_at,
            )
            for i, created_at in enumerate(
                [
                    "2026-05-01T12:00:00Z",
                    "2026-05-05T12:00:00Z",
                    "2026-05-10T12:00:00Z",
                    "2026-05-15T12:00:00Z",
                    "2026-05-16T12:00:00Z",
                ]
            )
        ]
    )
    assert long_window is not None
    assert long_window["evidence_window"]["days"] >= 14
    assert long_window["promotion_eligible"] is True

    assert evaluate_promotion_eligible(signal_count=3, evidence_days=20, confidence=0.9) is False
    assert evaluate_promotion_eligible(signal_count=5, evidence_days=10, confidence=0.9) is False
    assert evaluate_promotion_eligible(signal_count=5, evidence_days=14, confidence=0.5) is False
    assert evaluate_promotion_eligible(signal_count=5, evidence_days=14, confidence=0.7) is True


def test_candidate_does_not_contain_profile_or_pattern_fields():
    candidate = _aggregate(
        [
            _signal("lsig-1", direction=SIGNAL_DIRECTION_POSITIVE),
            _signal("lsig-2", direction=SIGNAL_DIRECTION_POSITIVE),
            _signal("lsig-3", direction=SIGNAL_DIRECTION_POSITIVE),
        ]
    )
    assert candidate is not None
    forbidden = {
        "pattern_confirmed",
        "pattern_id",
        "behavior_pattern",
        "behavior_knowledge",
        "knowledge_atom",
        "profile_update",
        "recommendation",
    }
    assert forbidden.isdisjoint(candidate.keys())
    assert validate_day_pattern_candidate_v1(candidate) == []


def test_candidate_does_not_allow_memory_or_profile_updates():
    candidate = _aggregate(
        [
            _signal("lsig-1", direction=SIGNAL_DIRECTION_POSITIVE),
            _signal("lsig-2", direction=SIGNAL_DIRECTION_POSITIVE),
            _signal("lsig-3", direction=SIGNAL_DIRECTION_POSITIVE),
        ]
    )
    assert candidate is not None
    assert candidate["memory_update_allowed"] is False
    assert candidate["profile_update_allowed"] is False
    assert candidate["ranking_update_allowed"] is False


def test_candidate_does_not_create_recommendation():
    candidate = _aggregate(
        [
            _signal("lsig-1", direction=SIGNAL_DIRECTION_POSITIVE),
            _signal("lsig-2", direction=SIGNAL_DIRECTION_POSITIVE),
            _signal("lsig-3", direction=SIGNAL_DIRECTION_POSITIVE),
        ]
    )
    assert candidate is not None
    assert "recommendation" not in candidate
    assert "recommendation_id" not in candidate


def test_output_shape_stable():
    candidate = _aggregate(
        [
            _signal("lsig-1", direction=SIGNAL_DIRECTION_POSITIVE),
            _signal("lsig-2", direction=SIGNAL_DIRECTION_POSITIVE),
            _signal("lsig-3", direction=SIGNAL_DIRECTION_POSITIVE),
        ]
    )
    assert candidate is not None
    assert candidate["contract_version"] == DAY_PATTERN_CANDIDATE_V1_CONTRACT
    assert set(candidate.keys()) == set(DAY_PATTERN_CANDIDATE_V1_KEYS)
