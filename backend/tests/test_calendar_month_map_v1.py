"""E1.3 — Calendar Month Map contract tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.services.calendar_day_record_v1 import build_calendar_day_record_v1
from todayflow_backend.services.calendar_month_map_v1 import (
    CALENDAR_MONTH_MAP_V1_CONTRACT,
    CALENDAR_MONTH_MAP_V1_KEYS,
    build_calendar_month_map_v1,
    validate_calendar_month_map_v1,
)
from todayflow_backend.services.calendar_signal_ingestion_v1 import (
    SOURCE_PROGRESSION_SIGNAL,
    SOURCE_TRACKING,
    ingest_calendar_signal_v1,
)
from todayflow_backend.services.progression_signal_v1 import (
    VERIFICATION_STATUS_VERIFIED,
    build_progression_signal_v1,
)


def _day_record(date: str, **overrides):
    base = build_calendar_day_record_v1(user_id="user-1", date=date)
    base.update(overrides)
    return base


def _verified_signal(signal_type: str, source_engine: str, event_id: str, observed_at: str):
    return build_progression_signal_v1(
        user_id="user-1",
        signal_type=signal_type,
        source_engine=source_engine,
        source_event_id=event_id,
        observed_at=observed_at,
        verification_status=VERIFICATION_STATUS_VERIFIED,
        confidence=0.8,
        evidence_count=3,
        evidence_window_days=7,
    )


def _ingested_day(date: str, signal_type: str, source_engine: str, event_id: str):
    record = _day_record(date)
    signal = _verified_signal(signal_type, source_engine, event_id, f"{date}T08:00:00Z")
    updated, _ = ingest_calendar_signal_v1(
        record,
        source_artifact=signal,
        source_artifact_type=SOURCE_PROGRESSION_SIGNAL,
    )
    return updated


def test_empty_month_valid_zero_map() -> None:
    month_map = build_calendar_month_map_v1(
        user_id="user-1",
        year_month="2026-06",
        day_records=[],
    )

    assert month_map["coverage"]["days_with_records"] == 0
    assert month_map["coverage"]["days_in_month"] == 30
    assert month_map["completion_density"]["total_completion_marks"] == 0
    assert month_map["day_records"] == []
    assert validate_calendar_month_map_v1(month_map) == []


def test_day_records_aggregate_by_month_only() -> None:
    june = _ingested_day("2026-06-01", "practice_completed", "practice", "evt-1")
    july = _ingested_day("2026-07-01", "practice_completed", "practice", "evt-2")

    month_map = build_calendar_month_map_v1(
        user_id="user-1",
        year_month="2026-06",
        day_records=[june, july],
    )

    assert len(month_map["day_records"]) == 1
    assert month_map["day_records"][0]["date"] == "2026-06-01"


def test_completion_density_correct() -> None:
    day_one = _ingested_day("2026-06-01", "practice_completed", "practice", "evt-1")
    day_two = _ingested_day("2026-06-02", "habit_streak_confirmed", "practice", "evt-2")
    day_three = _ingested_day("2026-06-03", "cycle_completed", "calendar", "evt-3")

    month_map = build_calendar_month_map_v1(
        user_id="user-1",
        year_month="2026-06",
        day_records=[day_one, day_two, day_three],
    )

    density = month_map["completion_density"]
    assert density["practice_marks"] == 1
    assert density["habit_marks"] == 1
    assert density["cycle_marks"] == 1
    assert density["total_completion_marks"] == 3
    assert month_map["coverage"]["days_with_completion_marks"] == 3


def test_tracking_density_correct() -> None:
    record = _day_record("2026-06-01")
    updated, _ = ingest_calendar_signal_v1(
        record,
        source_artifact={"energy_score": 6, "mood_score": 4},
        source_artifact_type=SOURCE_TRACKING,
    )
    record2 = _day_record("2026-06-02")
    updated2, _ = ingest_calendar_signal_v1(
        record2,
        source_artifact={"energy_score": 8},
        source_artifact_type=SOURCE_TRACKING,
    )

    month_map = build_calendar_month_map_v1(
        user_id="user-1",
        year_month="2026-06",
        day_records=[updated, updated2],
    )

    tracking = month_map["tracking_density"]
    assert tracking["energy_entries"] == 2
    assert tracking["mood_entries"] == 1
    assert tracking["days_with_any_tracking"] == 2


def test_day_type_distribution_correct() -> None:
    record = _day_record("2026-06-01", day_type_labels=["focus", "action"])
    record2 = _day_record("2026-06-02", day_type_labels=["focus"])

    month_map = build_calendar_month_map_v1(
        user_id="user-1",
        year_month="2026-06",
        day_records=[record, record2],
    )

    assert month_map["day_type_distribution"] == {"action": 1, "focus": 2}


def test_cosmic_coverage_correct() -> None:
    record = _day_record(
        "2026-06-01",
        day_model_snapshot_id="dmsnap-1",
        tarot_entity_code="tarot.major.06",
        numerology_entity_code="num.personal_day.3",
        astrology_snapshot_ref="astro:snap:1",
    )

    month_map = build_calendar_month_map_v1(
        user_id="user-1",
        year_month="2026-06",
        day_records=[record],
    )

    cosmic = month_map["cosmic_ref_coverage"]
    assert cosmic["days_with_tarot"] == 1
    assert cosmic["days_with_numerology"] == 1
    assert cosmic["days_with_astrology"] == 1
    assert cosmic["days_with_daymodel"] == 1
    assert cosmic["days_with_any_cosmic"] == 1


def test_evolution_signal_density_correct() -> None:
    record = _ingested_day("2026-06-01", "practice_completed", "practice", "evt-1")
    record2 = _ingested_day("2026-06-02", "habit_streak_confirmed", "practice", "evt-2")

    month_map = build_calendar_month_map_v1(
        user_id="user-1",
        year_month="2026-06",
        day_records=[record, record2],
    )

    assert month_map["evolution_signal_density"]["total_progression_signal_ids"] == 2
    assert month_map["evolution_signal_density"]["days_with_signals"] == 2


def test_cycle_overlays_refs_only() -> None:
    month_map = build_calendar_month_map_v1(
        user_id="user-1",
        year_month="2026-06",
        day_records=[],
        cycle_overlays=[
            {
                "cycle_overlay_id": "co-1",
                "cycle_length_days": 21,
                "start_date": "2026-06-01",
                "end_date": "2026-06-21",
                "path_theme_code": "discipline",
                "phase": "active",
            }
        ],
    )

    assert len(month_map["cycle_overlays"]) == 1
    assert month_map["cycle_overlays"][0]["cycle_overlay_id"] == "co-1"
    assert "rhythm_pattern" not in month_map["cycle_overlays"][0]


def test_forbidden_inference_fields_rejected() -> None:
    month_map = build_calendar_month_map_v1(
        user_id="user-1",
        year_month="2026-06",
        day_records=[],
    )
    bad = copy.deepcopy(month_map)
    bad["best_day"] = "2026-06-01"
    errors = validate_calendar_month_map_v1(bad)
    assert any("forbidden fields" in err for err in errors)


def test_read_only_flags_correct() -> None:
    month_map = build_calendar_month_map_v1(
        user_id="user-1",
        year_month="2026-06",
        day_records=[],
    )

    assert month_map["read_only"] is True
    assert month_map["rhythm_inference_allowed"] is False
    assert month_map["recommendation_allowed"] is False


def test_output_shape_stable() -> None:
    month_map = build_calendar_month_map_v1(
        user_id="user-1",
        year_month="2026-06",
        day_records=[_ingested_day("2026-06-01", "practice_completed", "practice", "evt-1")],
    )

    assert month_map["contract_version"] == CALENDAR_MONTH_MAP_V1_CONTRACT
    assert set(month_map.keys()) == CALENDAR_MONTH_MAP_V1_KEYS
    assert validate_calendar_month_map_v1(month_map) == []
