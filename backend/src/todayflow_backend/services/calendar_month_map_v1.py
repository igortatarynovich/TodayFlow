"""E1.3 — Calendar Month Map contract (aggregate calendar_day_record_v1, no inference)."""

from __future__ import annotations

import calendar as py_calendar
import re
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.calendar_day_record_v1 import (
    CALENDAR_DAY_RECORD_V1_CONTRACT,
    validate_calendar_day_record_v1,
)

CALENDAR_MONTH_MAP_V1_CONTRACT = "calendar_month_map_v1"
CALENDAR_MONTH_MAP_V1_VERSION = "1.0.0"

YEAR_MONTH_PATTERN = re.compile(r"^\d{4}-\d{2}$")

DAY_COMPACT_FACT_V1_KEYS = frozenset(
    {
        "date",
        "record_id",
        "has_daymodel",
        "has_cosmic_refs",
        "completion_counts",
        "energy_score",
        "mood_score",
        "day_type_labels",
        "progression_signal_count",
    }
)

COMPLETION_COUNT_KEYS = frozenset(
    {
        "practice",
        "habit",
        "ritual",
        "cycle",
        "goal",
    }
)

CYCLE_OVERLAY_REF_V1_KEYS = frozenset(
    {
        "cycle_overlay_id",
        "cycle_length_days",
        "start_date",
        "end_date",
        "path_theme_code",
        "phase",
    }
)

CALENDAR_MONTH_MAP_V1_KEYS = frozenset(
    {
        "contract_version",
        "month_map_id",
        "user_id",
        "year_month",
        "day_records",
        "coverage",
        "completion_density",
        "tracking_density",
        "day_type_distribution",
        "cosmic_ref_coverage",
        "evolution_signal_density",
        "cycle_overlays",
        "created_at",
        "read_only",
        "rhythm_inference_allowed",
        "recommendation_allowed",
        "version",
    }
)

FORBIDDEN_MONTH_MAP_FIELDS = frozenset(
    {
        "rhythm_pattern",
        "rhythm_pattern_id",
        "rhythm_candidate",
        "pattern_candidate",
        "pattern_confirmation",
        "insight",
        "insight_text",
        "recommendation",
        "recommendation_id",
        "best_day",
        "worst_day",
        "burnout",
        "overload_inference",
        "commerce",
        "llm_output",
        "llm_call",
        "profile",
        "profile_update",
        "evolution_stage",
        "current_stage",
        "promoted_stage",
        "monthly_summary",
    }
)


class CalendarMonthMapError(ValueError):
    """Raised when calendar month map inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_calendar_month_map_id() -> str:
    return f"cmm-{uuid4()}"


def _normalize_year_month(value: str) -> str:
    if not isinstance(value, str) or not YEAR_MONTH_PATTERN.match(value):
        raise CalendarMonthMapError("year_month must be YYYY-MM")
    year_str, month_str = value.split("-", 1)
    year = int(year_str)
    month = int(month_str)
    if month < 1 or month > 12:
        raise CalendarMonthMapError("year_month must be a valid calendar month")
    return value


def _days_in_month(year_month: str) -> int:
    year_str, month_str = year_month.split("-", 1)
    return py_calendar.monthrange(int(year_str), int(month_str))[1]


def _record_in_month(record: dict[str, Any], year_month: str) -> bool:
    date_value = record.get("date")
    return isinstance(date_value, str) and date_value.startswith(f"{year_month}-")


def _has_daymodel(record: dict[str, Any]) -> bool:
    return bool(
        record.get("day_model_snapshot_id")
        or record.get("interpretation_id")
        or record.get("content_package_id")
    )


def _has_cosmic_refs(record: dict[str, Any]) -> bool:
    return bool(
        record.get("tarot_entity_code")
        or record.get("numerology_entity_code")
        or record.get("astrology_snapshot_ref")
    )


def _completion_counts(record: dict[str, Any]) -> dict[str, int]:
    return {
        "practice": len(record.get("completed_practices") or []),
        "habit": len(record.get("completed_habits") or []),
        "ritual": len(record.get("completed_rituals") or []),
        "cycle": len(record.get("completed_cycles") or []),
        "goal": len(record.get("completed_goals") or []),
    }


def _total_completion_marks(counts: dict[str, int]) -> int:
    return sum(counts.values())


def build_day_compact_fact_v1(record: dict[str, Any]) -> dict[str, Any]:
    """Compact factual summary for one calendar day record."""
    if record.get("contract_version") != CALENDAR_DAY_RECORD_V1_CONTRACT:
        raise CalendarMonthMapError("invalid calendar_day_record contract_version")

    counts = _completion_counts(record)
    fact = {
        "date": record.get("date"),
        "record_id": record.get("record_id"),
        "has_daymodel": _has_daymodel(record),
        "has_cosmic_refs": _has_cosmic_refs(record),
        "completion_counts": counts,
        "energy_score": record.get("energy_score"),
        "mood_score": record.get("mood_score"),
        "day_type_labels": list(record.get("day_type_labels") or []),
        "progression_signal_count": len(record.get("progression_signal_ids") or []),
    }
    errors = validate_day_compact_fact_v1(fact)
    if errors:
        raise CalendarMonthMapError("; ".join(errors))
    return fact


def validate_day_compact_fact_v1(fact: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in DAY_COMPACT_FACT_V1_KEYS:
        if key not in fact:
            errors.append(f"missing day compact fact field: {key}")

    counts = fact.get("completion_counts")
    if not isinstance(counts, dict):
        errors.append("completion_counts must be object")
    else:
        for key in COMPLETION_COUNT_KEYS:
            if key not in counts:
                errors.append(f"completion_counts missing {key}")
            elif not isinstance(counts[key], int) or counts[key] < 0:
                errors.append(f"completion_counts.{key} must be non-negative integer")

    if not isinstance(fact.get("day_type_labels"), list):
        errors.append("day_type_labels must be array")

    for field in ("has_daymodel", "has_cosmic_refs"):
        if not isinstance(fact.get(field), bool):
            errors.append(f"{field} must be boolean")

    signal_count = fact.get("progression_signal_count")
    if not isinstance(signal_count, int) or signal_count < 0:
        errors.append("progression_signal_count must be non-negative integer")

    return errors


def validate_cycle_overlay_ref_v1(overlay: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not overlay.get("cycle_overlay_id"):
        errors.append("cycle_overlay_id required")
    for key in ("start_date", "end_date"):
        value = overlay.get(key)
        if not isinstance(value, str) or len(value) < 10:
            errors.append(f"{key} must be ISO date string")
    extra = set(overlay.keys()) - CYCLE_OVERLAY_REF_V1_KEYS
    if extra:
        errors.append(f"unknown cycle overlay fields: {sorted(extra)}")
    return errors


def build_calendar_month_map_v1(
    *,
    user_id: str,
    year_month: str,
    day_records: list[dict[str, Any]] | None = None,
    cycle_overlays: list[dict[str, Any]] | None = None,
    month_map_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """
    Aggregate calendar_day_record_v1 rows into a read-only month structure.

    Month Map aggregates facts, not meanings — no rhythm inference.
    """
    if not user_id:
        raise CalendarMonthMapError("user_id required")

    normalized_month = _normalize_year_month(year_month)
    days_in_month = _days_in_month(normalized_month)

    included_records: list[dict[str, Any]] = []
    for record in day_records or []:
        if not isinstance(record, dict):
            continue
        if record.get("user_id") != user_id:
            continue
        if record.get("contract_version") != CALENDAR_DAY_RECORD_V1_CONTRACT:
            continue
        if not _record_in_month(record, normalized_month):
            continue
        record_errors = validate_calendar_day_record_v1(record)
        if record_errors:
            raise CalendarMonthMapError("; ".join(record_errors[:4]))
        included_records.append(record)

    included_records.sort(key=lambda item: str(item.get("date")))

    day_facts = [build_day_compact_fact_v1(record) for record in included_records]

    completion_density = {
        "practice_marks": 0,
        "habit_marks": 0,
        "ritual_marks": 0,
        "cycle_marks": 0,
        "goal_marks": 0,
        "total_completion_marks": 0,
    }
    tracking_density = {
        "energy_entries": 0,
        "mood_entries": 0,
        "days_with_any_tracking": 0,
    }
    day_type_distribution: dict[str, int] = {}
    cosmic_ref_coverage = {
        "days_with_tarot": 0,
        "days_with_numerology": 0,
        "days_with_astrology": 0,
        "days_with_daymodel": 0,
        "days_with_any_cosmic": 0,
    }
    evolution_signal_density = {
        "total_progression_signal_ids": 0,
        "days_with_signals": 0,
    }

    days_with_completion_marks = 0
    days_with_tracking = 0

    for record, fact in zip(included_records, day_facts, strict=True):
        counts = fact["completion_counts"]
        completion_density["practice_marks"] += counts["practice"]
        completion_density["habit_marks"] += counts["habit"]
        completion_density["ritual_marks"] += counts["ritual"]
        completion_density["cycle_marks"] += counts["cycle"]
        completion_density["goal_marks"] += counts["goal"]

        if _total_completion_marks(counts) > 0:
            days_with_completion_marks += 1

        has_energy = record.get("energy_score") is not None
        has_mood = record.get("mood_score") is not None
        if has_energy:
            tracking_density["energy_entries"] += 1
        if has_mood:
            tracking_density["mood_entries"] += 1
        if has_energy or has_mood:
            tracking_density["days_with_any_tracking"] += 1
            days_with_tracking += 1

        for label in fact["day_type_labels"]:
            day_type_distribution[label] = day_type_distribution.get(label, 0) + 1

        if record.get("tarot_entity_code"):
            cosmic_ref_coverage["days_with_tarot"] += 1
        if record.get("numerology_entity_code"):
            cosmic_ref_coverage["days_with_numerology"] += 1
        if record.get("astrology_snapshot_ref"):
            cosmic_ref_coverage["days_with_astrology"] += 1
        if fact["has_daymodel"]:
            cosmic_ref_coverage["days_with_daymodel"] += 1
        if fact["has_cosmic_refs"] or fact["has_daymodel"]:
            cosmic_ref_coverage["days_with_any_cosmic"] += 1

        signal_count = fact["progression_signal_count"]
        evolution_signal_density["total_progression_signal_ids"] += signal_count
        if signal_count > 0:
            evolution_signal_density["days_with_signals"] += 1

    completion_density["total_completion_marks"] = (
        completion_density["practice_marks"]
        + completion_density["habit_marks"]
        + completion_density["ritual_marks"]
        + completion_density["cycle_marks"]
        + completion_density["goal_marks"]
    )

    days_with_records = len(day_facts)
    coverage = {
        "days_in_month": days_in_month,
        "days_with_records": days_with_records,
        "days_with_tracking": days_with_tracking,
        "days_with_completion_marks": days_with_completion_marks,
        "record_coverage_ratio": round(days_with_records / days_in_month, 4)
        if days_in_month
        else 0.0,
    }

    overlay_refs: list[dict[str, Any]] = []
    for overlay in cycle_overlays or []:
        if not isinstance(overlay, dict):
            continue
        overlay_errors = validate_cycle_overlay_ref_v1(overlay)
        if overlay_errors:
            raise CalendarMonthMapError("; ".join(overlay_errors))
        overlay_refs.append({key: overlay.get(key) for key in CYCLE_OVERLAY_REF_V1_KEYS if key in overlay})

    month_map = {
        "contract_version": CALENDAR_MONTH_MAP_V1_CONTRACT,
        "month_map_id": month_map_id or generate_calendar_month_map_id(),
        "user_id": user_id,
        "year_month": normalized_month,
        "day_records": day_facts,
        "coverage": coverage,
        "completion_density": completion_density,
        "tracking_density": tracking_density,
        "day_type_distribution": dict(sorted(day_type_distribution.items())),
        "cosmic_ref_coverage": cosmic_ref_coverage,
        "evolution_signal_density": evolution_signal_density,
        "cycle_overlays": overlay_refs,
        "created_at": created_at or _utc_now_iso(),
        "read_only": True,
        "rhythm_inference_allowed": False,
        "recommendation_allowed": False,
        "version": CALENDAR_MONTH_MAP_V1_VERSION,
    }

    errors = validate_calendar_month_map_v1(month_map)
    if errors:
        raise CalendarMonthMapError("; ".join(errors))

    return month_map


def validate_calendar_month_map_v1(month_map: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if month_map.get("contract_version") != CALENDAR_MONTH_MAP_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in CALENDAR_MONTH_MAP_V1_KEYS:
        if key not in month_map:
            errors.append(f"missing field: {key}")

    forbidden = set(month_map.keys()) & FORBIDDEN_MONTH_MAP_FIELDS
    if forbidden:
        errors.append(f"forbidden fields: {sorted(forbidden)}")

    if month_map.get("read_only") is not True:
        errors.append("read_only must be true")
    if month_map.get("rhythm_inference_allowed") is not False:
        errors.append("rhythm_inference_allowed must be false")
    if month_map.get("recommendation_allowed") is not False:
        errors.append("recommendation_allowed must be false")

    year_month = month_map.get("year_month")
    if not isinstance(year_month, str) or not YEAR_MONTH_PATTERN.match(year_month):
        errors.append("invalid year_month")

    if not isinstance(month_map.get("day_records"), list):
        errors.append("day_records must be array")
    else:
        for index, fact in enumerate(month_map["day_records"]):
            fact_errors = validate_day_compact_fact_v1(fact)
            for err in fact_errors:
                errors.append(f"day_records[{index}]: {err}")

    for section in (
        "coverage",
        "completion_density",
        "tracking_density",
        "day_type_distribution",
        "cosmic_ref_coverage",
        "evolution_signal_density",
    ):
        if not isinstance(month_map.get(section), dict):
            errors.append(f"{section} must be object")

    if not isinstance(month_map.get("cycle_overlays"), list):
        errors.append("cycle_overlays must be array")
    else:
        for index, overlay in enumerate(month_map["cycle_overlays"]):
            overlay_errors = validate_cycle_overlay_ref_v1(overlay)
            for err in overlay_errors:
                errors.append(f"cycle_overlays[{index}]: {err}")

    return errors
