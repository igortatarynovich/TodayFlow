"""E1.1 — Calendar Day Record contract tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.services.calendar_day_record_v1 import (
    ALLOWED_DAY_TYPE_LABELS,
    CALENDAR_DAY_RECORD_V1_CONTRACT,
    CALENDAR_DAY_RECORD_V1_KEYS,
    build_calendar_day_record_v1,
    build_completion_mark_ref_v1,
    validate_calendar_day_record_v1,
)


def _minimal_record(**overrides):
    base = build_calendar_day_record_v1(
        user_id="user-1",
        date="2026-06-01",
    )
    base.update(overrides)
    return base


def test_minimal_record_builds_and_validates() -> None:
    record = build_calendar_day_record_v1(user_id="user-1", date="2026-06-01")

    assert record["contract_version"] == CALENDAR_DAY_RECORD_V1_CONTRACT
    assert record["user_id"] == "user-1"
    assert record["date"] == "2026-06-01"
    assert validate_calendar_day_record_v1(record) == []


def test_record_stores_refs_not_embedded_objects() -> None:
    record = build_calendar_day_record_v1(
        user_id="user-1",
        date="2026-06-01",
        day_model_snapshot_id="dmsnap-abc",
        interpretation_id="interp-abc",
        content_package_id="pkg-abc",
        tarot_entity_code="tarot.major.06",
        numerology_entity_code="num.personal_day.3",
        astrology_snapshot_ref="astro:snap:2026-06-01",
    )

    assert record["day_model_snapshot_id"] == "dmsnap-abc"
    assert "day_model" not in record
    assert "interpretation" not in record
    assert "tarot_entity" not in record


def test_completion_marks_are_confirmed_refs_only() -> None:
    practice_mark = build_completion_mark_ref_v1(
        entity_ref="practice:breathing:instance-1",
        progression_signal_id="psig-1",
        verified_at="2026-06-01T08:00:00Z",
    )
    record = build_calendar_day_record_v1(
        user_id="user-1",
        date="2026-06-01",
        completed_practices=[practice_mark],
        completed_habits=[
            build_completion_mark_ref_v1(entity_ref="habit:daily_breathing:instance-1")
        ],
    )

    assert len(record["completed_practices"]) == 1
    assert record["completed_practices"][0]["entity_ref"].startswith("practice:")
    assert validate_calendar_day_record_v1(record) == []


def test_evolution_marks_are_ids_not_state() -> None:
    record = build_calendar_day_record_v1(
        user_id="user-1",
        date="2026-06-01",
        progression_signal_ids=["psig-1", "psig-2"],
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01",
    )

    assert "evolution_stage" not in record
    assert "current_stage" not in record
    assert record["progression_signal_ids"] == ["psig-1", "psig-2"]


def test_personal_tracking_scores_bounded() -> None:
    record = build_calendar_day_record_v1(
        user_id="user-1",
        date="2026-06-01",
        energy_score=7,
        mood_score=4,
    )

    assert record["energy_score"] == 7
    assert record["mood_score"] == 4

    bad = copy.deepcopy(record)
    bad["energy_score"] = 11
    assert any("energy_score" in err for err in validate_calendar_day_record_v1(bad))


def test_day_type_labels_only_no_explanation() -> None:
    record = build_calendar_day_record_v1(
        user_id="user-1",
        date="2026-06-01",
        day_type_labels=["focus", "action"],
    )

    assert set(record["day_type_labels"]).issubset(ALLOWED_DAY_TYPE_LABELS)
    assert "day_type_explanation" not in record

    bad = copy.deepcopy(record)
    bad["day_type_labels"] = ["focus", "recommend_more"]
    assert any("invalid day_type_label" in err for err in validate_calendar_day_record_v1(bad))


def test_forbidden_fields_rejected() -> None:
    record = _minimal_record()
    for forbidden in (
        "rhythm_pattern",
        "recommendation",
        "llm_output",
        "evolution_stage",
        "knowledge_candidates",
        "month_map",
    ):
        bad = copy.deepcopy(record)
        bad[forbidden] = "leak"
        errors = validate_calendar_day_record_v1(bad)
        assert any("forbidden fields" in err for err in errors)


def test_invalid_date_rejected() -> None:
    with pytest.raises(Exception):
        build_calendar_day_record_v1(user_id="user-1", date="2026-13-40")


def test_completion_mark_forbidden_fields_rejected() -> None:
    with pytest.raises(Exception):
        build_calendar_day_record_v1(
            user_id="user-1",
            date="2026-06-01",
            completed_practices=[
                {
                    "entity_ref": "practice:breathing:1",
                    "recommendation": "buy stone",
                }
            ],
        )


def test_output_shape_stable() -> None:
    record = build_calendar_day_record_v1(
        user_id="user-1",
        date="2026-06-01",
        source_versions={"day_model": "1.0.0", "ingestion": "e1.2-draft"},
    )

    assert set(record.keys()) == CALENDAR_DAY_RECORD_V1_KEYS
    assert validate_calendar_day_record_v1(record) == []
