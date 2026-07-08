"""P1.18 — Pattern confirmation gate tests."""

from __future__ import annotations

from todayflow_backend.services.day_model_v1_confirmed_pattern import (
    CONFIRMATION_RESULT_CONFLICTED,
    CONFIRMATION_RESULT_CONFIRMED,
    CONFIRMATION_RESULT_NOT_READY,
    CONFIRMATION_RESULT_REJECTED,
    DAY_CONFIRMED_PATTERN_V1_CONTRACT,
    DAY_CONFIRMED_PATTERN_V1_KEYS,
    try_confirm_pattern_from_candidate_v1,
    validate_day_confirmed_pattern_v1,
)
from todayflow_backend.services.day_model_v1_pattern_candidate import (
    CANDIDATE_TYPE_SURFACE_PREFERENCE,
    DAY_PATTERN_CANDIDATE_V1_CONTRACT,
    try_aggregate_pattern_candidate_v1,
)
from todayflow_backend.services.day_model_v1_surface_learning_signal import (
    DAY_SURFACE_LEARNING_SIGNAL_V1_CONTRACT,
    SIGNAL_DIRECTION_POSITIVE,
)

AGG_KEY = "today_hero"
LONG_WINDOW_DATES = [
    "2026-05-01T12:00:00Z",
    "2026-05-05T12:00:00Z",
    "2026-05-10T12:00:00Z",
    "2026-05-15T12:00:00Z",
    "2026-05-16T12:00:00Z",
]


def _signal(signal_id: str, *, direction=SIGNAL_DIRECTION_POSITIVE, created_at: str):
    return {
        "contract_version": DAY_SURFACE_LEARNING_SIGNAL_V1_CONTRACT,
        "learning_signal_id": signal_id,
        "reaction_id": f"react-{signal_id}",
        "exposure_id": f"exp-{signal_id}",
        "audit_id": f"audit-{signal_id}",
        "surface": "today_hero",
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


def _eligible_candidate():
    signals = [
        _signal(f"lsig-{i}", created_at=created_at)
        for i, created_at in enumerate(LONG_WINDOW_DATES)
    ]
    candidate = try_aggregate_pattern_candidate_v1(
        signals,
        candidate_type=CANDIDATE_TYPE_SURFACE_PREFERENCE,
        aggregation_key=AGG_KEY,
    )
    assert candidate is not None
    assert candidate["promotion_eligible"] is True
    return candidate


def _manual_candidate(**overrides):
    base = {
        "contract_version": DAY_PATTERN_CANDIDATE_V1_CONTRACT,
        "pattern_candidate_id": "pcand-test-001",
        "candidate_type": CANDIDATE_TYPE_SURFACE_PREFERENCE,
        "aggregation_key": AGG_KEY,
        "source_signals": [f"lsig-{i}" for i in range(5)],
        "signal_count": 5,
        "positive_count": 5,
        "negative_count": 0,
        "neutral_count": 0,
        "confidence": 0.72,
        "evidence_window": {
            "start_at": "2026-05-01T12:00:00Z",
            "end_at": "2026-05-16T12:00:00Z",
            "days": 15,
        },
        "status": "formed",
        "promotion_eligible": True,
        "memory_update_allowed": False,
        "profile_update_allowed": False,
        "ranking_update_allowed": False,
        "created_at": "2026-05-16T12:00:00Z",
    }
    base.update(overrides)
    return base


def test_eligible_candidate_confirms_pattern():
    candidate = _eligible_candidate()
    outcome = try_confirm_pattern_from_candidate_v1(candidate)
    assert outcome["result"] == CONFIRMATION_RESULT_CONFIRMED
    pattern = outcome["pattern"]
    assert pattern is not None
    assert pattern["status"] == "confirmed"
    assert pattern["source_pattern_candidate_id"] == candidate["pattern_candidate_id"]


def test_non_eligible_candidate_not_ready():
    signals = [
        _signal(f"lsig-{i}", created_at="2026-05-01T12:00:00Z")
        for i in range(3)
    ]
    candidate = try_aggregate_pattern_candidate_v1(
        signals,
        candidate_type=CANDIDATE_TYPE_SURFACE_PREFERENCE,
        aggregation_key=AGG_KEY,
    )
    assert candidate is not None
    assert candidate["promotion_eligible"] is False
    outcome = try_confirm_pattern_from_candidate_v1(candidate)
    assert outcome["result"] == CONFIRMATION_RESULT_NOT_READY
    assert outcome["pattern"] is None


def test_low_confidence_not_ready():
    candidate = _manual_candidate(confidence=0.5, promotion_eligible=False)
    outcome = try_confirm_pattern_from_candidate_v1(candidate)
    assert outcome["result"] == CONFIRMATION_RESULT_NOT_READY
    assert "confidence" in " ".join(outcome["reasons"])


def test_short_evidence_window_not_ready():
    candidate = _manual_candidate(
        evidence_window={
            "start_at": "2026-05-01T12:00:00Z",
            "end_at": "2026-05-05T12:00:00Z",
            "days": 4,
        },
        promotion_eligible=False,
    )
    outcome = try_confirm_pattern_from_candidate_v1(candidate)
    assert outcome["result"] == CONFIRMATION_RESULT_NOT_READY
    assert "evidence_window_days" in " ".join(outcome["reasons"])


def test_too_many_conflicts_conflicted():
    candidate = _manual_candidate(
        positive_count=3,
        negative_count=2,
        neutral_count=0,
        promotion_eligible=True,
    )
    outcome = try_confirm_pattern_from_candidate_v1(candidate)
    assert outcome["result"] == CONFIRMATION_RESULT_CONFLICTED
    assert outcome["pattern"] is None


def test_invalid_candidate_type_rejected():
    candidate = _manual_candidate(candidate_type="personality_trait")
    outcome = try_confirm_pattern_from_candidate_v1(candidate)
    assert outcome["result"] == CONFIRMATION_RESULT_REJECTED
    assert outcome["pattern"] is None


def test_confirmed_pattern_keeps_source_evidence():
    candidate = _eligible_candidate()
    outcome = try_confirm_pattern_from_candidate_v1(candidate)
    pattern = outcome["pattern"]
    assert pattern is not None
    assert pattern["evidence_signal_ids"] == candidate["source_signals"]
    assert pattern["evidence_count"] == candidate["signal_count"]
    assert pattern["evidence_window_days"] == candidate["evidence_window"]["days"]


def test_mutation_flags_always_false():
    outcome = try_confirm_pattern_from_candidate_v1(_eligible_candidate())
    pattern = outcome["pattern"]
    assert pattern is not None
    assert pattern["memory_update_allowed"] is False
    assert pattern["profile_update_allowed"] is False
    assert pattern["ranking_update_allowed"] is False


def test_no_knowledge_or_profile_fields():
    candidate = _eligible_candidate()
    outcome = try_confirm_pattern_from_candidate_v1(candidate)
    pattern = outcome["pattern"]
    assert pattern is not None
    forbidden = {
        "knowledge_atom",
        "ukm_atom_id",
        "behavior_knowledge",
        "profile_update",
        "recommendation",
        "knowledge_candidate_id",
    }
    assert forbidden.isdisjoint(pattern.keys())
    assert validate_day_confirmed_pattern_v1(pattern, pattern_candidate=candidate) == []


def test_output_shape_stable():
    candidate = _eligible_candidate()
    outcome = try_confirm_pattern_from_candidate_v1(candidate)
    pattern = outcome["pattern"]
    assert pattern is not None
    assert pattern["contract_version"] == DAY_CONFIRMED_PATTERN_V1_CONTRACT
    assert set(pattern.keys()) == set(DAY_CONFIRMED_PATTERN_V1_KEYS)
    assert outcome["result"] in {
        CONFIRMATION_RESULT_CONFIRMED,
        CONFIRMATION_RESULT_NOT_READY,
        CONFIRMATION_RESULT_CONFLICTED,
        CONFIRMATION_RESULT_REJECTED,
    }


def test_cannot_confirm_without_candidate():
    broken = {"contract_version": DAY_PATTERN_CANDIDATE_V1_CONTRACT}
    outcome = try_confirm_pattern_from_candidate_v1(broken)
    assert outcome["result"] == CONFIRMATION_RESULT_REJECTED
