"""E1.1 — Calendar Day Record contract (canonical user × date archive atom)."""

from __future__ import annotations

import re
from datetime import UTC, date, datetime
from typing import Any
from uuid import uuid4

CALENDAR_DAY_RECORD_V1_CONTRACT = "calendar_day_record_v1"
CALENDAR_DAY_RECORD_V1_VERSION = "1.0.0"

ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

ALLOWED_DAY_TYPE_LABELS = frozenset(
    {
        "focus",
        "action",
        "recovery",
        "overload",
        "waiting",
        "completion",
        "neutral",
    }
)

COMPLETION_MARK_REF_V1_KEYS = frozenset(
    {
        "entity_ref",
        "progression_signal_id",
        "verified_at",
    }
)

CALENDAR_DAY_RECORD_V1_KEYS = frozenset(
    {
        "contract_version",
        "record_id",
        "user_id",
        "date",
        "day_model_snapshot_id",
        "interpretation_id",
        "content_package_id",
        "tarot_entity_code",
        "numerology_entity_code",
        "astrology_snapshot_ref",
        "completed_practices",
        "completed_habits",
        "completed_rituals",
        "completed_cycles",
        "completed_goals",
        "progression_signal_ids",
        "evolution_score_snapshot_id",
        "energy_score",
        "mood_score",
        "day_type_labels",
        "created_at",
        "updated_at",
        "source_versions",
        "version",
    }
)

FORBIDDEN_CALENDAR_DAY_RECORD_FIELDS = frozenset(
    {
        "rhythm_pattern",
        "rhythm_pattern_id",
        "pattern_candidate",
        "pattern_confirmation",
        "monthly_summary",
        "month_map",
        "recommendation",
        "recommendation_id",
        "commerce",
        "commerce_hook",
        "prompt",
        "llm_output",
        "llm_call",
        "insight",
        "insight_text",
        "evolution_stage",
        "current_stage",
        "promoted_stage",
        "stage_update",
        "profile",
        "profile_data",
        "core_profile",
        "memory",
        "memory_write",
        "knowledge_candidates",
        "knowledge_candidate",
        "day_model",
        "interpretation",
        "content_package",
        "tarot_entity",
        "numerology_entity",
        "astrology_snapshot",
    }
)

FORBIDDEN_MARK_REF_FIELDS = frozenset(
    {
        "recommendation",
        "insight",
        "llm_output",
        "commerce",
        "evolution_stage",
        "profile",
        "memory",
    }
)


class CalendarDayRecordError(ValueError):
    """Raised when calendar day record inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_calendar_day_record_id() -> str:
    return f"cdr-{uuid4()}"


def _normalize_iso_date(value: str) -> str:
    if not isinstance(value, str) or not ISO_DATE_PATTERN.match(value):
        raise CalendarDayRecordError("date must be ISO calendar date YYYY-MM-DD")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise CalendarDayRecordError("date must be a valid ISO calendar date") from exc
    return value


def _validate_score(value: Any, field_name: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return [f"{field_name} must be a number between 0 and 10"]
    if value < 0 or value > 10:
        return [f"{field_name} must be between 0 and 10"]
    return []


def _validate_completion_mark_refs(
    marks: Any,
    *,
    field_name: str,
) -> list[str]:
    errors: list[str] = []
    if marks is None:
        return [f"{field_name} must be array"]
    if not isinstance(marks, list):
        return [f"{field_name} must be array"]

    for index, mark in enumerate(marks):
        if not isinstance(mark, dict):
            errors.append(f"{field_name}[{index}] must be object")
            continue
        if not mark.get("entity_ref"):
            errors.append(f"{field_name}[{index}] missing entity_ref")
        forbidden = set(mark.keys()) & FORBIDDEN_MARK_REF_FIELDS
        if forbidden:
            errors.append(f"{field_name}[{index}] forbidden fields: {sorted(forbidden)}")
        extra = set(mark.keys()) - COMPLETION_MARK_REF_V1_KEYS
        if extra:
            errors.append(f"{field_name}[{index}] unknown fields: {sorted(extra)}")
    return errors


def build_completion_mark_ref_v1(
    *,
    entity_ref: str,
    progression_signal_id: str | None = None,
    verified_at: str | None = None,
) -> dict[str, Any]:
    """Build a confirmed daily completion mark reference (not a runtime event)."""
    if not entity_ref:
        raise CalendarDayRecordError("entity_ref required")

    mark = {
        "entity_ref": entity_ref,
        "progression_signal_id": progression_signal_id,
        "verified_at": verified_at,
    }
    errors = _validate_completion_mark_refs([mark], field_name="mark")
    if errors:
        raise CalendarDayRecordError("; ".join(errors))
    return mark


def build_calendar_day_record_v1(
    *,
    user_id: str,
    date: str,
    record_id: str | None = None,
    day_model_snapshot_id: str | None = None,
    interpretation_id: str | None = None,
    content_package_id: str | None = None,
    tarot_entity_code: str | None = None,
    numerology_entity_code: str | None = None,
    astrology_snapshot_ref: str | None = None,
    completed_practices: list[dict[str, Any]] | None = None,
    completed_habits: list[dict[str, Any]] | None = None,
    completed_rituals: list[dict[str, Any]] | None = None,
    completed_cycles: list[dict[str, Any]] | None = None,
    completed_goals: list[dict[str, Any]] | None = None,
    progression_signal_ids: list[str] | None = None,
    evolution_score_snapshot_id: str | None = None,
    energy_score: int | float | None = None,
    mood_score: int | float | None = None,
    day_type_labels: list[str] | None = None,
    created_at: str | None = None,
    updated_at: str | None = None,
    source_versions: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Build canonical calendar day archive record: user × date.

    Stores facts and references only — no rhythm patterns, summaries, or LLM output.
    """
    if not user_id:
        raise CalendarDayRecordError("user_id required")

    normalized_date = _normalize_iso_date(date)
    now = _utc_now_iso()

    record = {
        "contract_version": CALENDAR_DAY_RECORD_V1_CONTRACT,
        "record_id": record_id or generate_calendar_day_record_id(),
        "user_id": user_id,
        "date": normalized_date,
        "day_model_snapshot_id": day_model_snapshot_id,
        "interpretation_id": interpretation_id,
        "content_package_id": content_package_id,
        "tarot_entity_code": tarot_entity_code,
        "numerology_entity_code": numerology_entity_code,
        "astrology_snapshot_ref": astrology_snapshot_ref,
        "completed_practices": list(completed_practices or []),
        "completed_habits": list(completed_habits or []),
        "completed_rituals": list(completed_rituals or []),
        "completed_cycles": list(completed_cycles or []),
        "completed_goals": list(completed_goals or []),
        "progression_signal_ids": list(progression_signal_ids or []),
        "evolution_score_snapshot_id": evolution_score_snapshot_id,
        "energy_score": energy_score,
        "mood_score": mood_score,
        "day_type_labels": list(day_type_labels or []),
        "created_at": created_at or now,
        "updated_at": updated_at or now,
        "source_versions": dict(source_versions or {}),
        "version": CALENDAR_DAY_RECORD_V1_VERSION,
    }

    errors = validate_calendar_day_record_v1(record)
    if errors:
        raise CalendarDayRecordError("; ".join(errors))

    return record


def validate_calendar_day_record_v1(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if record.get("contract_version") != CALENDAR_DAY_RECORD_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in CALENDAR_DAY_RECORD_V1_KEYS:
        if key not in record:
            errors.append(f"missing field: {key}")

    forbidden = set(record.keys()) & FORBIDDEN_CALENDAR_DAY_RECORD_FIELDS
    if forbidden:
        errors.append(f"forbidden fields: {sorted(forbidden)}")

    if record.get("user_id") in (None, ""):
        errors.append("user_id required")

    date_value = record.get("date")
    if not isinstance(date_value, str) or not ISO_DATE_PATTERN.match(date_value):
        errors.append("date must be ISO calendar date YYYY-MM-DD")
    else:
        try:
            date.fromisoformat(date_value)
        except ValueError:
            errors.append("date must be a valid ISO calendar date")

    for field_name in (
        "completed_practices",
        "completed_habits",
        "completed_rituals",
        "completed_cycles",
        "completed_goals",
    ):
        errors.extend(_validate_completion_mark_refs(record.get(field_name), field_name=field_name))

    signal_ids = record.get("progression_signal_ids")
    if not isinstance(signal_ids, list):
        errors.append("progression_signal_ids must be array")
    elif any(not isinstance(item, str) or not item for item in signal_ids):
        errors.append("progression_signal_ids entries must be non-empty strings")

    errors.extend(_validate_score(record.get("energy_score"), "energy_score"))
    errors.extend(_validate_score(record.get("mood_score"), "mood_score"))

    labels = record.get("day_type_labels")
    if not isinstance(labels, list):
        errors.append("day_type_labels must be array")
    else:
        for label in labels:
            if label not in ALLOWED_DAY_TYPE_LABELS:
                errors.append(f"invalid day_type_label: {label!r}")

    source_versions = record.get("source_versions")
    if not isinstance(source_versions, dict):
        errors.append("source_versions must be object")
    else:
        for key, value in source_versions.items():
            if not isinstance(key, str) or not isinstance(value, str):
                errors.append("source_versions keys and values must be strings")

    ref_fields = (
        "day_model_snapshot_id",
        "interpretation_id",
        "content_package_id",
        "tarot_entity_code",
        "numerology_entity_code",
        "astrology_snapshot_ref",
        "evolution_score_snapshot_id",
    )
    for field_name in ref_fields:
        value = record.get(field_name)
        if value is not None and (not isinstance(value, str) or not value):
            errors.append(f"{field_name} must be a non-empty string when set")

    return errors
