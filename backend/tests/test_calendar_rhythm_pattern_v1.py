"""E1.5 — Calendar rhythm pattern confirmation gate tests."""

from __future__ import annotations

import copy

from todayflow_backend.services.calendar_rhythm_pattern_candidate_v1 import (
    CALENDAR_RHYTHM_PATTERN_CANDIDATE_V1_CONTRACT,
    CALENDAR_RHYTHM_PATTERN_CANDIDATE_V1_VERSION,
    CANDIDATE_TYPE_ENERGY_WEEKDAY,
)
from todayflow_backend.services.calendar_rhythm_pattern_v1 import (
    CALENDAR_RHYTHM_PATTERN_V1_CONTRACT,
    CALENDAR_RHYTHM_PATTERN_V1_KEYS,
    CONFIRMATION_RESULT_CONFIRMED,
    CONFIRMATION_RESULT_NOT_READY,
    CONFIRMATION_RESULT_REJECTED,
    try_confirm_rhythm_pattern_from_candidate_v1,
    validate_calendar_rhythm_pattern_v1,
)


def _strong_candidate(**overrides):
    base = {
        "contract_version": CALENDAR_RHYTHM_PATTERN_CANDIDATE_V1_CONTRACT,
        "candidate_id": "crpc-test-strong",
        "user_id": "user-1",
        "candidate_type": CANDIDATE_TYPE_ENERGY_WEEKDAY,
        "source_month_map_ids": ["cmm-test-1"],
        "source_day_record_ids": [f"cdr-{index}" for index in range(6)],
        "evidence_window_days": 28,
        "evidence_count": 6,
        "supporting_dates": [
            "2026-06-03",
            "2026-06-10",
            "2026-06-17",
            "2026-06-24",
            "2026-07-01",
            "2026-07-08",
        ],
        "dominant_value": "tuesday",
        "baseline_value": 5.0,
        "strength": 0.5,
        "confidence": 0.65,
        "status": "candidate",
        "created_at": "2026-06-01T12:00:00Z",
        "confirmation_allowed": False,
        "recommendation_allowed": False,
        "version": CALENDAR_RHYTHM_PATTERN_CANDIDATE_V1_VERSION,
    }
    base.update(overrides)
    return base


def test_strong_candidate_confirms_pattern() -> None:
    outcome = try_confirm_rhythm_pattern_from_candidate_v1(_strong_candidate())

    assert outcome["result"] == CONFIRMATION_RESULT_CONFIRMED
    assert outcome["reasons"] == []
    pattern = outcome["pattern"]
    assert pattern is not None
    assert pattern["contract_version"] == CALENDAR_RHYTHM_PATTERN_V1_CONTRACT
    assert pattern["status"] == "confirmed"
    assert pattern["source_candidate_id"] == "crpc-test-strong"
    assert pattern["pattern_type"] == CANDIDATE_TYPE_ENERGY_WEEKDAY


def test_low_evidence_not_ready() -> None:
    outcome = try_confirm_rhythm_pattern_from_candidate_v1(
        _strong_candidate(evidence_window_days=20, evidence_count=5)
    )

    assert outcome["result"] == CONFIRMATION_RESULT_NOT_READY
    assert outcome["pattern"] is None
    assert any("evidence_window_days" in reason for reason in outcome["reasons"])
    assert any("evidence_count" in reason for reason in outcome["reasons"])


def test_low_strength_not_ready() -> None:
    outcome = try_confirm_rhythm_pattern_from_candidate_v1(
        _strong_candidate(strength=0.3)
    )

    assert outcome["result"] == CONFIRMATION_RESULT_NOT_READY
    assert outcome["pattern"] is None
    assert any("strength" in reason for reason in outcome["reasons"])


def test_low_confidence_not_ready() -> None:
    outcome = try_confirm_rhythm_pattern_from_candidate_v1(
        _strong_candidate(confidence=0.5)
    )

    assert outcome["result"] == CONFIRMATION_RESULT_NOT_READY
    assert outcome["pattern"] is None
    assert any("confidence" in reason for reason in outcome["reasons"])


def test_invalid_candidate_rejected() -> None:
    bad = _strong_candidate(contract_version="wrong_contract", status="formed")
    outcome = try_confirm_rhythm_pattern_from_candidate_v1(bad)

    assert outcome["result"] == CONFIRMATION_RESULT_REJECTED
    assert outcome["pattern"] is None
    assert outcome["reasons"]


def test_forbidden_fields_rejected_on_validate() -> None:
    outcome = try_confirm_rhythm_pattern_from_candidate_v1(_strong_candidate())
    pattern = outcome["pattern"]
    assert pattern is not None

    bad = copy.deepcopy(pattern)
    bad["insight"] = "rest more on sundays"
    assert validate_calendar_rhythm_pattern_v1(bad)


def test_confirmed_pattern_preserves_evidence_refs() -> None:
    candidate = _strong_candidate()
    outcome = try_confirm_rhythm_pattern_from_candidate_v1(candidate)
    pattern = outcome["pattern"]
    assert pattern is not None

    assert pattern["source_month_map_ids"] == candidate["source_month_map_ids"]
    assert pattern["source_day_record_ids"] == candidate["source_day_record_ids"]
    assert pattern["supporting_dates"] == sorted(set(candidate["supporting_dates"]))
    assert pattern["evidence_count"] == candidate["evidence_count"]
    assert pattern["evidence_window_days"] == candidate["evidence_window_days"]


def test_insight_allowed_false() -> None:
    pattern = try_confirm_rhythm_pattern_from_candidate_v1(_strong_candidate())["pattern"]
    assert pattern is not None
    assert pattern["insight_allowed"] is False


def test_recommendation_allowed_false() -> None:
    pattern = try_confirm_rhythm_pattern_from_candidate_v1(_strong_candidate())["pattern"]
    assert pattern is not None
    assert pattern["recommendation_allowed"] is False


def test_mutation_flags_false() -> None:
    pattern = try_confirm_rhythm_pattern_from_candidate_v1(_strong_candidate())["pattern"]
    assert pattern is not None
    assert pattern["profile_update_allowed"] is False
    assert pattern["memory_update_allowed"] is False


def test_output_shape_stable() -> None:
    pattern = try_confirm_rhythm_pattern_from_candidate_v1(_strong_candidate())["pattern"]
    assert pattern is not None
    assert set(pattern.keys()) == CALENDAR_RHYTHM_PATTERN_V1_KEYS
    assert validate_calendar_rhythm_pattern_v1(pattern, candidate=_strong_candidate()) == []
