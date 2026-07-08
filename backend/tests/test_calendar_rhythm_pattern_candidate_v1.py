"""E1.4 — Calendar rhythm pattern candidate tests."""

from __future__ import annotations

import copy
from datetime import date as date_cls

from todayflow_backend.services.calendar_day_record_v1 import (
    build_calendar_day_record_v1,
    build_completion_mark_ref_v1,
)
from todayflow_backend.services.calendar_month_map_v1 import build_calendar_month_map_v1
from todayflow_backend.services.calendar_rhythm_pattern_candidate_v1 import (
    CALENDAR_RHYTHM_PATTERN_CANDIDATE_V1_CONTRACT,
    CALENDAR_RHYTHM_PATTERN_CANDIDATE_V1_KEYS,
    CANDIDATE_TYPE_COMPLETION_WEEKDAY,
    CANDIDATE_TYPE_ENERGY_WEEKDAY,
    CANDIDATE_TYPE_PRACTICE_CONSISTENCY,
    build_calendar_rhythm_pattern_candidate_v1,
    detect_calendar_rhythm_pattern_candidates_v1,
    validate_calendar_rhythm_pattern_candidate_v1,
)


def _day_record(date: str, **overrides):
    base = build_calendar_day_record_v1(user_id="user-1", date=date)
    base.update(overrides)
    return base


def _practice_mark(entity: str = "practice:breath:1"):
    return build_completion_mark_ref_v1(
        entity_ref=entity,
        progression_signal_id=f"psig-{entity}",
    )


def _detect(records):
    return detect_calendar_rhythm_pattern_candidates_v1(
        user_id="user-1",
        day_records=records,
    )


def _candidate_by_type(candidates, candidate_type: str):
    matches = [item for item in candidates if item["candidate_type"] == candidate_type]
    return matches[0] if matches else None


def test_empty_month_no_candidate() -> None:
    month_map = build_calendar_month_map_v1(
        user_id="user-1",
        year_month="2026-06",
        day_records=[],
    )
    assert detect_calendar_rhythm_pattern_candidates_v1(
        user_id="user-1",
        month_maps=[month_map],
    ) == []
    assert _detect([]) == []


def test_too_few_observations_no_candidate() -> None:
    records = [
        _day_record("2026-06-01", energy_score=8),
        _day_record("2026-06-02", energy_score=8),
        _day_record("2026-06-03", energy_score=8),
    ]
    assert _detect(records) == []


def test_energy_weekday_pattern_candidate() -> None:
    records = []
    for day in range(1, 29):
        date = f"2026-06-{day:02d}"
        is_tuesday = date_cls.fromisoformat(date).weekday() == 1
        records.append(_day_record(date, energy_score=9 if is_tuesday else 4))

    candidates = _detect(records)
    candidate = _candidate_by_type(candidates, CANDIDATE_TYPE_ENERGY_WEEKDAY)
    assert candidate is not None
    assert candidate["dominant_value"] == "tuesday"
    assert candidate["evidence_count"] >= 4
    assert candidate["evidence_window_days"] >= 14
    assert candidate["strength"] >= 0.25
    assert candidate["confidence"] >= 0.4


def test_completion_weekday_pattern_candidate() -> None:
    records = []
    for day in range(1, 29):
        date = f"2026-06-{day:02d}"
        is_weekday = date_cls.fromisoformat(date).weekday() < 5
        records.append(
            _day_record(
                date,
                completed_practices=[_practice_mark(f"p-{date}")] if is_weekday else [],
            )
        )

    candidates = _detect(records)
    candidate = _candidate_by_type(candidates, CANDIDATE_TYPE_COMPLETION_WEEKDAY)
    assert candidate is not None
    assert candidate["dominant_value"] in {
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
    }
    assert candidate["evidence_count"] >= 4


def test_practice_consistency_streak_candidate() -> None:
    streak_dates = [
        "2026-06-01",
        "2026-06-02",
        "2026-06-03",
        "2026-06-04",
        "2026-06-08",
        "2026-06-09",
        "2026-06-10",
        "2026-06-11",
        "2026-06-15",
        "2026-06-16",
        "2026-06-17",
        "2026-06-18",
    ]
    records = [
        _day_record(
            date,
            completed_practices=[_practice_mark(f"p-{date}")],
        )
        for date in streak_dates
    ]

    candidates = _detect(records)
    candidate = _candidate_by_type(candidates, CANDIDATE_TYPE_PRACTICE_CONSISTENCY)
    assert candidate is not None
    assert candidate["dominant_value"].startswith("streak_length_")
    assert len(candidate["supporting_dates"]) >= 4


def test_weak_strength_no_candidate() -> None:
    records = [_day_record(f"2026-06-{day:02d}", energy_score=5) for day in range(1, 29)]
    candidates = _detect(records)
    assert _candidate_by_type(candidates, CANDIDATE_TYPE_ENERGY_WEEKDAY) is None


def test_candidate_keeps_evidence_dates() -> None:
    records = []
    for day in range(1, 29):
        date = f"2026-06-{day:02d}"
        is_tuesday = date_cls.fromisoformat(date).weekday() == 1
        records.append(_day_record(date, energy_score=9 if is_tuesday else 4))

    candidate = _candidate_by_type(_detect(records), CANDIDATE_TYPE_ENERGY_WEEKDAY)
    assert candidate is not None
    assert candidate["supporting_dates"]
    assert all(item.startswith("2026-06-") for item in candidate["supporting_dates"])


def test_no_recommendation_or_insight_fields() -> None:
    records = []
    for day in range(1, 29):
        date = f"2026-06-{day:02d}"
        is_tuesday = date_cls.fromisoformat(date).weekday() == 1
        records.append(_day_record(date, energy_score=9 if is_tuesday else 4))

    for candidate in _detect(records):
        assert "recommendation" not in candidate
        assert "insight" not in candidate
        assert "confirmed_pattern" not in candidate
        assert validate_calendar_rhythm_pattern_candidate_v1(candidate) == []


def test_confirmation_allowed_false() -> None:
    records = []
    for day in range(1, 29):
        date = f"2026-06-{day:02d}"
        is_tuesday = date_cls.fromisoformat(date).weekday() == 1
        records.append(_day_record(date, energy_score=9 if is_tuesday else 4))

    for candidate in _detect(records):
        assert candidate["confirmation_allowed"] is False
        assert candidate["recommendation_allowed"] is False
        assert candidate["status"] == "candidate"


def test_output_shape_stable() -> None:
    records = []
    for day in range(1, 29):
        date = f"2026-06-{day:02d}"
        is_weekday = date_cls.fromisoformat(date).weekday() < 5
        records.append(
            _day_record(
                date,
                energy_score=8 if is_weekday else 4,
                completed_practices=[_practice_mark(f"p-{date}")] if is_weekday else [],
            )
        )

    candidates = _detect(records)
    assert candidates
    for candidate in candidates:
        assert candidate["contract_version"] == CALENDAR_RHYTHM_PATTERN_CANDIDATE_V1_CONTRACT
        assert set(candidate.keys()) == CALENDAR_RHYTHM_PATTERN_CANDIDATE_V1_KEYS


def test_forbidden_fields_rejected_on_validate() -> None:
    candidate = build_calendar_rhythm_pattern_candidate_v1(
        user_id="user-1",
        candidate_type=CANDIDATE_TYPE_ENERGY_WEEKDAY,
        source_month_map_ids=[],
        source_day_record_ids=["cdr-1"],
        evidence_window_days=14,
        evidence_count=4,
        supporting_dates=["2026-06-03"],
        dominant_value="tuesday",
        baseline_value=5.0,
        strength=0.5,
        confidence=0.5,
    )
    assert candidate is not None
    bad = copy.deepcopy(candidate)
    bad["insight"] = "overload week"
    assert validate_calendar_rhythm_pattern_candidate_v1(bad)
