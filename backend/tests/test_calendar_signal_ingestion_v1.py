"""E1.2 — Calendar signal ingestion tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache
from todayflow_backend.data.progression_signal_registry_loader import clear_progression_signal_registry_cache
from todayflow_backend.services.calendar_day_record_v1 import build_calendar_day_record_v1
from todayflow_backend.services.calendar_signal_ingestion_v1 import (
    CALENDAR_SIGNAL_INGESTION_RESULT_V1_CONTRACT,
    CALENDAR_SIGNAL_INGESTION_RESULT_V1_KEYS,
    MARK_CYCLE,
    MARK_GOAL,
    MARK_HABIT,
    MARK_PRACTICE,
    MARK_RITUAL,
    OPERATION_APPEND,
    OPERATION_IGNORE,
    OPERATION_REJECT,
    OPERATION_UPSERT,
    SOURCE_COSMIC,
    SOURCE_DAYMODEL,
    SOURCE_EVOLUTION_SCORE,
    SOURCE_PROGRESSION_SIGNAL,
    SOURCE_TRACKING,
    ingest_calendar_signal_v1,
    validate_calendar_signal_ingestion_result_v1,
)
from todayflow_backend.services.progression_signal_v1 import (
    VERIFICATION_STATUS_VERIFIED,
    build_progression_signal_v1,
)


@pytest.fixture(autouse=True)
def _clear_caches() -> None:
    clear_evolution_cd_cache()
    clear_progression_signal_registry_cache()
    yield
    clear_evolution_cd_cache()
    clear_progression_signal_registry_cache()


@pytest.fixture
def day_record() -> dict:
    return build_calendar_day_record_v1(user_id="user-1", date="2026-06-01")


def _verified_signal(signal_type: str, source_engine: str, event_id: str, **overrides):
    base = build_progression_signal_v1(
        user_id="user-1",
        signal_type=signal_type,
        source_engine=source_engine,
        source_event_id=event_id,
        observed_at="2026-06-01T08:00:00Z",
        verification_status=VERIFICATION_STATUS_VERIFIED,
        confidence=0.8,
        evidence_count=3,
        evidence_window_days=7,
    )
    base.update(overrides)
    return base


def _ingest(record: dict, artifact: dict, source_type: str):
    return ingest_calendar_signal_v1(
        record,
        source_artifact=artifact,
        source_artifact_type=source_type,
        created_at="2026-06-01T12:00:00Z",
    )


def test_practice_completed_to_completed_practices(day_record: dict) -> None:
    signal = _verified_signal("practice_completed", "practice", "evt-practice-1")
    updated, result = _ingest(day_record, signal, SOURCE_PROGRESSION_SIGNAL)

    assert result["operation"] == OPERATION_APPEND
    assert result["mark_type"] == MARK_PRACTICE
    assert "completed_practices" in result["written_paths"]
    assert len(updated["completed_practices"]) == 1
    assert updated["completed_practices"][0]["progression_signal_id"] == signal["progression_signal_id"]


def test_habit_streak_confirmed_to_completed_habits(day_record: dict) -> None:
    updated, result = _ingest(
        day_record,
        _verified_signal("habit_streak_confirmed", "practice", "evt-habit-1"),
        SOURCE_PROGRESSION_SIGNAL,
    )

    assert result["mark_type"] == MARK_HABIT
    assert len(updated["completed_habits"]) == 1


def test_ritual_streak_confirmed_to_completed_rituals(day_record: dict) -> None:
    updated, result = _ingest(
        day_record,
        _verified_signal("ritual_streak_confirmed", "ritual", "evt-ritual-1"),
        SOURCE_PROGRESSION_SIGNAL,
    )

    assert result["mark_type"] == MARK_RITUAL
    assert len(updated["completed_rituals"]) == 1


def test_cycle_completed_to_completed_cycles(day_record: dict) -> None:
    updated, result = _ingest(
        day_record,
        _verified_signal("cycle_completed", "calendar", "evt-cycle-1"),
        SOURCE_PROGRESSION_SIGNAL,
    )

    assert result["mark_type"] == MARK_CYCLE
    assert len(updated["completed_cycles"]) == 1


def test_goal_signals_to_completed_goals(day_record: dict) -> None:
    updated, result = _ingest(
        day_record,
        _verified_signal("weekly_goal_completed", "goal", "evt-goal-1"),
        SOURCE_PROGRESSION_SIGNAL,
    )

    assert result["mark_type"] == MARK_GOAL
    assert len(updated["completed_goals"]) == 1


def test_duplicate_signal_not_duplicated(day_record: dict) -> None:
    signal = _verified_signal("practice_completed", "practice", "evt-practice-1")
    first_record, first_result = _ingest(day_record, signal, SOURCE_PROGRESSION_SIGNAL)
    second_record, second_result = _ingest(first_record, signal, SOURCE_PROGRESSION_SIGNAL)

    assert first_result["operation"] == OPERATION_APPEND
    assert second_result["operation"] == OPERATION_IGNORE
    assert second_result["ignored_reason"] == "duplicate_progression_signal_id"
    assert len(second_record["completed_practices"]) == 1


def test_daymodel_refs_upsert(day_record: dict) -> None:
    artifact = {
        "day_model_snapshot_id": "dmsnap-1",
        "interpretation_id": "interp-1",
        "content_package_id": "pkg-1",
    }
    updated, result = _ingest(day_record, artifact, SOURCE_DAYMODEL)

    assert result["operation"] == OPERATION_UPSERT
    assert updated["day_model_snapshot_id"] == "dmsnap-1"
    assert updated["interpretation_id"] == "interp-1"

    updated2, result2 = _ingest(
        updated,
        {"day_model_snapshot_id": "dmsnap-2"},
        SOURCE_DAYMODEL,
    )
    assert result2["operation"] == OPERATION_UPSERT
    assert updated2["day_model_snapshot_id"] == "dmsnap-2"


def test_cosmic_refs_upsert(day_record: dict) -> None:
    artifact = {
        "tarot_entity_code": "tarot.major.06",
        "numerology_entity_code": "num.personal_day.3",
        "astrology_snapshot_ref": "astro:snap:2026-06-01",
    }
    updated, result = _ingest(day_record, artifact, SOURCE_COSMIC)

    assert result["operation"] == OPERATION_UPSERT
    assert updated["tarot_entity_code"] == "tarot.major.06"
    assert updated["numerology_entity_code"] == "num.personal_day.3"


def test_tracking_scores_validated(day_record: dict) -> None:
    updated, result = _ingest(
        day_record,
        {"energy_score": 7, "mood_score": 4, "day_type_labels": ["focus"]},
        SOURCE_TRACKING,
    )

    assert result["operation"] == OPERATION_UPSERT
    assert updated["energy_score"] == 7
    assert updated["mood_score"] == 4
    assert updated["day_type_labels"] == ["focus"]

    unchanged, reject_result = _ingest(
        day_record,
        {"energy_score": 12},
        SOURCE_TRACKING,
    )
    assert reject_result["operation"] == OPERATION_REJECT
    assert unchanged["energy_score"] is None


def test_forbidden_insight_fields_rejected(day_record: dict) -> None:
    signal = _verified_signal("practice_completed", "practice", "evt-practice-1")
    bad = copy.deepcopy(signal)
    bad["recommendation"] = "buy this stone"

    with pytest.raises(Exception):
        _ingest(day_record, bad, SOURCE_PROGRESSION_SIGNAL)


def test_before_after_hashes_present(day_record: dict) -> None:
    _, result = _ingest(
        day_record,
        _verified_signal("practice_completed", "practice", "evt-practice-1"),
        SOURCE_PROGRESSION_SIGNAL,
    )

    assert result["record_before_hash"].startswith("snap-")
    assert result["record_after_hash"].startswith("snap-")
    assert result["record_before_hash"] != result["record_after_hash"]


def test_output_shape_stable(day_record: dict) -> None:
    updated, result = _ingest(
        day_record,
        {
            "evolution_score_snapshot_id": "evolution_score_snapshot_v1:user-1:2026-06-01",
            "user_id": "user-1",
        },
        SOURCE_EVOLUTION_SCORE,
    )

    assert updated["evolution_score_snapshot_id"] == "evolution_score_snapshot_v1:user-1:2026-06-01"
    assert result["contract_version"] == CALENDAR_SIGNAL_INGESTION_RESULT_V1_CONTRACT
    assert set(result.keys()) == CALENDAR_SIGNAL_INGESTION_RESULT_V1_KEYS
    assert result["mutation_scope"] == "calendar_day_record_only"
    assert validate_calendar_signal_ingestion_result_v1(result) == []
