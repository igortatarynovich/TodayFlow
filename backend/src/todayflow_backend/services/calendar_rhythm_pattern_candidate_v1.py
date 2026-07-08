"""E1.4 — Calendar rhythm pattern candidate (detect repetition signals, not confirmed patterns)."""

from __future__ import annotations

from datetime import date, timedelta
from statistics import mean
from typing import Any, Callable
from uuid import uuid4

from todayflow_backend.services.calendar_day_record_v1 import (
    CALENDAR_DAY_RECORD_V1_CONTRACT,
    validate_calendar_day_record_v1,
)
from todayflow_backend.services.calendar_month_map_v1 import (
    CALENDAR_MONTH_MAP_V1_CONTRACT,
    validate_calendar_month_map_v1,
)

CALENDAR_RHYTHM_PATTERN_CANDIDATE_V1_CONTRACT = "calendar_rhythm_pattern_candidate_v1"
CALENDAR_RHYTHM_PATTERN_CANDIDATE_V1_VERSION = "1.0.0"

CANDIDATE_STATUS = "candidate"

CANDIDATE_TYPE_ENERGY_WEEKDAY = "energy_weekday_pattern"
CANDIDATE_TYPE_MOOD_WEEKDAY = "mood_weekday_pattern"
CANDIDATE_TYPE_COMPLETION_WEEKDAY = "completion_weekday_pattern"
CANDIDATE_TYPE_RECOVERY_DAY = "recovery_day_pattern"
CANDIDATE_TYPE_OVERLOAD_DENSITY = "overload_density_pattern"
CANDIDATE_TYPE_CYCLE_COMPLETION = "cycle_completion_pattern"
CANDIDATE_TYPE_PRACTICE_CONSISTENCY = "practice_consistency_pattern"
CANDIDATE_TYPE_REFLECTION_TIMING = "reflection_timing_pattern"

ALLOWED_CANDIDATE_TYPES = frozenset(
    {
        CANDIDATE_TYPE_ENERGY_WEEKDAY,
        CANDIDATE_TYPE_MOOD_WEEKDAY,
        CANDIDATE_TYPE_COMPLETION_WEEKDAY,
        CANDIDATE_TYPE_RECOVERY_DAY,
        CANDIDATE_TYPE_OVERLOAD_DENSITY,
        CANDIDATE_TYPE_CYCLE_COMPLETION,
        CANDIDATE_TYPE_PRACTICE_CONSISTENCY,
        CANDIDATE_TYPE_REFLECTION_TIMING,
    }
)

MIN_EVIDENCE_WINDOW_DAYS = 14
MIN_EVIDENCE_COUNT = 4
MIN_STRENGTH = 0.25
MIN_CONFIDENCE = 0.4

WEEKDAY_NAMES = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)

CALENDAR_RHYTHM_PATTERN_CANDIDATE_V1_KEYS = frozenset(
    {
        "contract_version",
        "candidate_id",
        "user_id",
        "candidate_type",
        "source_month_map_ids",
        "source_day_record_ids",
        "evidence_window_days",
        "evidence_count",
        "supporting_dates",
        "dominant_value",
        "baseline_value",
        "strength",
        "confidence",
        "status",
        "created_at",
        "confirmation_allowed",
        "recommendation_allowed",
        "version",
    }
)

FORBIDDEN_CANDIDATE_FIELDS = frozenset(
    {
        "confirmed_pattern",
        "pattern_confirmed",
        "rhythm_pattern",
        "rhythm_pattern_id",
        "insight",
        "insight_text",
        "recommendation",
        "recommendation_id",
        "best_day",
        "worst_day",
        "diagnosis",
        "burnout",
        "burnout_claim",
        "profile",
        "profile_update",
        "memory",
        "memory_write",
        "evolution_stage",
        "evolution_update",
        "current_stage",
        "promoted_stage",
        "commerce",
        "llm_output",
        "llm_call",
    }
)


class CalendarRhythmPatternCandidateError(ValueError):
    """Raised when rhythm pattern candidate inputs or payload are invalid."""


def _utc_now_iso() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_calendar_rhythm_pattern_candidate_id() -> str:
    return f"crpc-{uuid4()}"


def passes_candidate_thresholds_v1(
    *,
    evidence_window_days: int,
    evidence_count: int,
    strength: float,
    confidence: float,
) -> bool:
    return (
        evidence_window_days >= MIN_EVIDENCE_WINDOW_DAYS
        and evidence_count >= MIN_EVIDENCE_COUNT
        and strength >= MIN_STRENGTH
        and confidence >= MIN_CONFIDENCE
    )


def validate_calendar_rhythm_pattern_candidate_v1(candidate: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if candidate.get("contract_version") != CALENDAR_RHYTHM_PATTERN_CANDIDATE_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in CALENDAR_RHYTHM_PATTERN_CANDIDATE_V1_KEYS:
        if key not in candidate:
            errors.append(f"missing field: {key}")

    forbidden = set(candidate.keys()) & FORBIDDEN_CANDIDATE_FIELDS
    if forbidden:
        errors.append(f"forbidden fields: {sorted(forbidden)}")

    if candidate.get("status") != CANDIDATE_STATUS:
        errors.append("status must be candidate")

    if candidate.get("confirmation_allowed") is not False:
        errors.append("confirmation_allowed must be false")
    if candidate.get("recommendation_allowed") is not False:
        errors.append("recommendation_allowed must be false")

    candidate_type = candidate.get("candidate_type")
    if candidate_type not in ALLOWED_CANDIDATE_TYPES:
        errors.append("invalid candidate_type")

    for field in ("source_month_map_ids", "source_day_record_ids", "supporting_dates"):
        value = candidate.get(field)
        if not isinstance(value, list):
            errors.append(f"{field} must be array")
        elif field != "supporting_dates" and any(not isinstance(item, str) or not item for item in value):
            errors.append(f"{field} entries must be non-empty strings")
        elif field == "supporting_dates" and any(
            not isinstance(item, str) or len(item) < 10 for item in value
        ):
            errors.append("supporting_dates entries must be ISO date strings")

    for field in ("evidence_window_days", "evidence_count"):
        value = candidate.get(field)
        if not isinstance(value, int) or value < 0:
            errors.append(f"{field} must be non-negative integer")

    for field in ("strength", "confidence", "baseline_value"):
        value = candidate.get(field)
        if not isinstance(value, (int, float)):
            errors.append(f"{field} must be number")
        elif field in ("strength", "confidence") and (value < 0 or value > 1):
            errors.append(f"{field} must be between 0 and 1")

    dominant = candidate.get("dominant_value")
    if not isinstance(dominant, str) or not dominant:
        errors.append("dominant_value must be non-empty string")

    return errors


def build_calendar_rhythm_pattern_candidate_v1(
    *,
    user_id: str,
    candidate_type: str,
    source_month_map_ids: list[str],
    source_day_record_ids: list[str],
    evidence_window_days: int,
    evidence_count: int,
    supporting_dates: list[str],
    dominant_value: str,
    baseline_value: float,
    strength: float,
    confidence: float,
    candidate_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any] | None:
    """
    Build one rhythm pattern candidate when thresholds pass.

    Rhythm Candidate ≠ Rhythm Pattern — returns None when evidence is too weak.
    """
    if not user_id:
        raise CalendarRhythmPatternCandidateError("user_id required")
    if candidate_type not in ALLOWED_CANDIDATE_TYPES:
        raise CalendarRhythmPatternCandidateError("invalid candidate_type")

    if not passes_candidate_thresholds_v1(
        evidence_window_days=evidence_window_days,
        evidence_count=evidence_count,
        strength=strength,
        confidence=confidence,
    ):
        return None

    candidate = {
        "contract_version": CALENDAR_RHYTHM_PATTERN_CANDIDATE_V1_CONTRACT,
        "candidate_id": candidate_id or generate_calendar_rhythm_pattern_candidate_id(),
        "user_id": user_id,
        "candidate_type": candidate_type,
        "source_month_map_ids": list(source_month_map_ids),
        "source_day_record_ids": sorted(set(source_day_record_ids)),
        "evidence_window_days": evidence_window_days,
        "evidence_count": evidence_count,
        "supporting_dates": sorted(supporting_dates),
        "dominant_value": dominant_value,
        "baseline_value": round(float(baseline_value), 4),
        "strength": round(float(strength), 4),
        "confidence": round(float(confidence), 4),
        "status": CANDIDATE_STATUS,
        "created_at": created_at or _utc_now_iso(),
        "confirmation_allowed": False,
        "recommendation_allowed": False,
        "version": CALENDAR_RHYTHM_PATTERN_CANDIDATE_V1_VERSION,
    }

    errors = validate_calendar_rhythm_pattern_candidate_v1(candidate)
    if errors:
        raise CalendarRhythmPatternCandidateError("; ".join(errors))

    return candidate


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _observation_span_days(observations: list[dict[str, Any]]) -> int:
    if not observations:
        return 0
    dates = [_parse_date(item["date"]) for item in observations]
    return (max(dates) - min(dates)).days + 1


def _weekday_name(value: date) -> str:
    return WEEKDAY_NAMES[value.weekday()]


def _observation_from_day_record(record: dict[str, Any]) -> dict[str, Any]:
    day = _parse_date(str(record["date"]))
    practice_count = len(record.get("completed_practices") or [])
    ritual_count = len(record.get("completed_rituals") or [])
    cycle_count = len(record.get("completed_cycles") or [])
    completion_total = (
        practice_count
        + len(record.get("completed_habits") or [])
        + ritual_count
        + cycle_count
        + len(record.get("completed_goals") or [])
    )
    return {
        "date": record["date"],
        "record_id": record["record_id"],
        "weekday": day.weekday(),
        "weekday_name": _weekday_name(day),
        "day_of_month": day.day,
        "days_in_month": _days_in_month(day),
        "energy_score": record.get("energy_score"),
        "mood_score": record.get("mood_score"),
        "completion_total": completion_total,
        "practice_count": practice_count,
        "ritual_count": ritual_count,
        "cycle_count": cycle_count,
        "day_type_labels": list(record.get("day_type_labels") or []),
    }


def _observation_from_compact_fact(fact: dict[str, Any]) -> dict[str, Any]:
    day = _parse_date(str(fact["date"]))
    counts = fact.get("completion_counts") or {}
    practice_count = int(counts.get("practice") or 0)
    ritual_count = int(counts.get("ritual") or 0)
    cycle_count = int(counts.get("cycle") or 0)
    completion_total = sum(int(counts.get(key) or 0) for key in ("practice", "habit", "ritual", "cycle", "goal"))
    return {
        "date": fact["date"],
        "record_id": fact["record_id"],
        "weekday": day.weekday(),
        "weekday_name": _weekday_name(day),
        "day_of_month": day.day,
        "days_in_month": _days_in_month(day),
        "energy_score": fact.get("energy_score"),
        "mood_score": fact.get("mood_score"),
        "completion_total": completion_total,
        "practice_count": practice_count,
        "ritual_count": ritual_count,
        "cycle_count": cycle_count,
        "day_type_labels": list(fact.get("day_type_labels") or []),
    }


def _days_in_month(day: date) -> int:
    import calendar as py_calendar

    return py_calendar.monthrange(day.year, day.month)[1]


def _collect_observations(
    *,
    user_id: str,
    day_records: list[dict[str, Any]] | None,
    month_maps: list[dict[str, Any]] | None,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    observations: dict[str, dict[str, Any]] = {}
    month_map_ids: list[str] = []
    record_ids: list[str] = []

    for record in day_records or []:
        if not isinstance(record, dict):
            continue
        if record.get("user_id") != user_id:
            continue
        if record.get("contract_version") != CALENDAR_DAY_RECORD_V1_CONTRACT:
            continue
        record_errors = validate_calendar_day_record_v1(record)
        if record_errors:
            raise CalendarRhythmPatternCandidateError("; ".join(record_errors[:4]))
        obs = _observation_from_day_record(record)
        observations[obs["date"]] = obs
        record_ids.append(str(record["record_id"]))

    for month_map in month_maps or []:
        if not isinstance(month_map, dict):
            continue
        if month_map.get("user_id") != user_id:
            continue
        if month_map.get("contract_version") != CALENDAR_MONTH_MAP_V1_CONTRACT:
            continue
        map_errors = validate_calendar_month_map_v1(month_map)
        if map_errors:
            raise CalendarRhythmPatternCandidateError("; ".join(map_errors[:4]))
        month_map_id = month_map.get("month_map_id")
        if isinstance(month_map_id, str) and month_map_id:
            month_map_ids.append(month_map_id)
        for fact in month_map.get("day_records") or []:
            if not isinstance(fact, dict):
                continue
            obs = _observation_from_compact_fact(fact)
            observations[obs["date"]] = obs
            record_ids.append(str(fact["record_id"]))

    ordered = sorted(observations.values(), key=lambda item: item["date"])
    return ordered, month_map_ids, record_ids


def _confidence_from_alignment(
    *,
    aligned_count: int,
    sample_count: int,
    evidence_window_days: int,
    evidence_count: int,
) -> float:
    alignment = aligned_count / max(sample_count, 1)
    volume = min(evidence_count / MIN_EVIDENCE_COUNT, 1.0)
    window = min(evidence_window_days / MIN_EVIDENCE_WINDOW_DAYS, 1.0)
    return min(max(alignment * 0.5 + volume * 0.25 + window * 0.25, 0.0), 1.0)


def _detect_weekday_numeric_pattern(
    observations: list[dict[str, Any]],
    *,
    candidate_type: str,
    value_getter: Callable[[dict[str, Any]], float | None],
    prefer_higher: bool,
) -> dict[str, Any] | None:
    samples = [obs for obs in observations if value_getter(obs) is not None]
    if not samples:
        return None

    evidence_window_days = _observation_span_days(samples)
    by_weekday: dict[int, list[float]] = {index: [] for index in range(7)}
    for obs in samples:
        value = value_getter(obs)
        if value is None:
            continue
        by_weekday[obs["weekday"]].append(float(value))

    weekday_means = {
        weekday: mean(values)
        for weekday, values in by_weekday.items()
        if values
    }
    if len(weekday_means) < 2:
        return None

    baseline_value = mean(value_getter(obs) for obs in samples)  # type: ignore[arg-type]
    if prefer_higher:
        dominant_weekday = max(weekday_means, key=weekday_means.get)
        dominant_mean = weekday_means[dominant_weekday]
        strength = min((dominant_mean - baseline_value) / 10.0, 1.0)
        aligned = [
            obs
            for obs in samples
            if obs["weekday"] == dominant_weekday and float(value_getter(obs) or 0) >= baseline_value
        ]
    else:
        dominant_weekday = min(weekday_means, key=weekday_means.get)
        dominant_mean = weekday_means[dominant_weekday]
        strength = min((baseline_value - dominant_mean) / 10.0, 1.0)
        aligned = [
            obs
            for obs in samples
            if obs["weekday"] == dominant_weekday and float(value_getter(obs) or 0) <= baseline_value
        ]

    dominant_dates = [obs["date"] for obs in samples if obs["weekday"] == dominant_weekday]
    evidence_count = len(dominant_dates)
    confidence = _confidence_from_alignment(
        aligned_count=len(aligned),
        sample_count=evidence_count,
        evidence_window_days=evidence_window_days,
        evidence_count=evidence_count,
    )

    return {
        "candidate_type": candidate_type,
        "evidence_window_days": evidence_window_days,
        "evidence_count": evidence_count,
        "supporting_dates": dominant_dates,
        "dominant_value": WEEKDAY_NAMES[dominant_weekday],
        "baseline_value": baseline_value,
        "strength": max(strength, 0.0),
        "confidence": confidence,
        "source_day_record_ids": [obs["record_id"] for obs in aligned],
    }


def _detect_completion_weekday_pattern(observations: list[dict[str, Any]]) -> dict[str, Any] | None:
    samples = [obs for obs in observations if obs["completion_total"] > 0]
    if not samples:
        return None

    evidence_window_days = _observation_span_days(samples)
    weekday_hits = {index: 0 for index in range(7)}
    weekday_totals = {index: 0 for index in range(7)}
    for obs in observations:
        weekday_totals[obs["weekday"]] += 1
        if obs["completion_total"] > 0:
            weekday_hits[obs["weekday"]] += 1

    rates = {
        weekday: weekday_hits[weekday] / max(weekday_totals[weekday], 1)
        for weekday in range(7)
        if weekday_totals[weekday] > 0
    }
    if len(rates) < 2:
        return None

    baseline_value = len(samples) / max(len(observations), 1)
    dominant_weekday = max(rates, key=rates.get)
    dominant_rate = rates[dominant_weekday]
    strength = min(max(dominant_rate - baseline_value, 0.0), 1.0)

    supporting = [obs for obs in samples if obs["weekday"] == dominant_weekday]
    evidence_count = len(supporting)
    confidence = _confidence_from_alignment(
        aligned_count=evidence_count,
        sample_count=evidence_count,
        evidence_window_days=evidence_window_days,
        evidence_count=evidence_count,
    )

    return {
        "candidate_type": CANDIDATE_TYPE_COMPLETION_WEEKDAY,
        "evidence_window_days": evidence_window_days,
        "evidence_count": evidence_count,
        "supporting_dates": [obs["date"] for obs in supporting],
        "dominant_value": WEEKDAY_NAMES[dominant_weekday],
        "baseline_value": baseline_value,
        "strength": strength,
        "confidence": confidence,
        "source_day_record_ids": [obs["record_id"] for obs in supporting],
    }


def _detect_practice_consistency_pattern(observations: list[dict[str, Any]]) -> dict[str, Any] | None:
    practice_days = sorted(
        [obs for obs in observations if obs["practice_count"] > 0],
        key=lambda item: item["date"],
    )
    if len(practice_days) < MIN_EVIDENCE_COUNT:
        return None

    streaks: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    for obs in practice_days:
        if not current:
            current = [obs]
            continue
        prev_day = _parse_date(current[-1]["date"])
        this_day = _parse_date(obs["date"])
        if (this_day - prev_day).days == 1:
            current.append(obs)
        else:
            if len(current) >= 2:
                streaks.append(current)
            current = [obs]
    if len(current) >= 2:
        streaks.append(current)

    qualifying = [day for streak in streaks for day in streak]
    if len(qualifying) < MIN_EVIDENCE_COUNT:
        return None

    evidence_window_days = _observation_span_days(practice_days)
    longest = max(len(streak) for streak in streaks)
    baseline_value = len(practice_days) / max(_observation_span_days(observations), 1)
    strength = min(longest / 7.0, 1.0)
    confidence = _confidence_from_alignment(
        aligned_count=len(qualifying),
        sample_count=len(practice_days),
        evidence_window_days=evidence_window_days,
        evidence_count=len(qualifying),
    )

    return {
        "candidate_type": CANDIDATE_TYPE_PRACTICE_CONSISTENCY,
        "evidence_window_days": evidence_window_days,
        "evidence_count": len(qualifying),
        "supporting_dates": [obs["date"] for obs in qualifying],
        "dominant_value": f"streak_length_{longest}",
        "baseline_value": baseline_value,
        "strength": strength,
        "confidence": confidence,
        "source_day_record_ids": [obs["record_id"] for obs in qualifying],
    }


def _detect_recovery_day_pattern(observations: list[dict[str, Any]]) -> dict[str, Any] | None:
    by_date = {obs["date"]: obs for obs in observations}
    pairs: list[dict[str, Any]] = []
    for obs in observations:
        if "recovery" not in obs["day_type_labels"]:
            continue
        prev = _parse_date(obs["date"]) - timedelta(days=1)
        prev_obs = by_date.get(prev.isoformat())
        if prev_obs and "overload" in prev_obs["day_type_labels"]:
            pairs.append(obs)

    if not pairs:
        return None

    evidence_window_days = _observation_span_days(pairs)
    evidence_count = len(pairs)
    baseline_value = evidence_count / max(len(observations), 1)
    strength = min(evidence_count / max(len(observations), 1), 1.0)
    confidence = _confidence_from_alignment(
        aligned_count=evidence_count,
        sample_count=evidence_count,
        evidence_window_days=evidence_window_days,
        evidence_count=evidence_count,
    )

    return {
        "candidate_type": CANDIDATE_TYPE_RECOVERY_DAY,
        "evidence_window_days": evidence_window_days,
        "evidence_count": evidence_count,
        "supporting_dates": [obs["date"] for obs in pairs],
        "dominant_value": "recovery_after_overload",
        "baseline_value": baseline_value,
        "strength": strength,
        "confidence": confidence,
        "source_day_record_ids": [obs["record_id"] for obs in pairs],
    }


def _detect_overload_density_pattern(observations: list[dict[str, Any]]) -> dict[str, Any] | None:
    overload_days = sorted(
        [obs for obs in observations if "overload" in obs["day_type_labels"]],
        key=lambda item: item["date"],
    )
    if len(overload_days) < MIN_EVIDENCE_COUNT:
        return None

    clusters: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    for obs in overload_days:
        if not current:
            current = [obs]
            continue
        prev_day = _parse_date(current[-1]["date"])
        this_day = _parse_date(obs["date"])
        if (this_day - prev_day).days <= 2:
            current.append(obs)
        else:
            if len(current) >= 2:
                clusters.append(current)
            current = [obs]
    if len(current) >= 2:
        clusters.append(current)

    clustered = [day for cluster in clusters for day in cluster]
    if len(clustered) < MIN_EVIDENCE_COUNT:
        return None

    evidence_window_days = _observation_span_days(overload_days)
    baseline_value = len(overload_days) / max(len(observations), 1)
    strength = min(len(clustered) / max(len(overload_days), 1), 1.0)
    confidence = _confidence_from_alignment(
        aligned_count=len(clustered),
        sample_count=len(overload_days),
        evidence_window_days=evidence_window_days,
        evidence_count=len(clustered),
    )

    return {
        "candidate_type": CANDIDATE_TYPE_OVERLOAD_DENSITY,
        "evidence_window_days": evidence_window_days,
        "evidence_count": len(clustered),
        "supporting_dates": [obs["date"] for obs in clustered],
        "dominant_value": "overload_cluster",
        "baseline_value": baseline_value,
        "strength": strength,
        "confidence": confidence,
        "source_day_record_ids": [obs["record_id"] for obs in clustered],
    }


def _detect_cycle_completion_pattern(observations: list[dict[str, Any]]) -> dict[str, Any] | None:
    cycle_days = [obs for obs in observations if obs["cycle_count"] > 0]
    if len(cycle_days) < MIN_EVIDENCE_COUNT:
        return None

    late_phase = [
        obs
        for obs in cycle_days
        if obs["day_of_month"] > (obs["days_in_month"] * 2) // 3
    ]
    if len(late_phase) < MIN_EVIDENCE_COUNT:
        return None

    evidence_window_days = _observation_span_days(cycle_days)
    baseline_value = len(cycle_days) / max(len(observations), 1)
    strength = min(len(late_phase) / max(len(cycle_days), 1), 1.0)
    confidence = _confidence_from_alignment(
        aligned_count=len(late_phase),
        sample_count=len(cycle_days),
        evidence_window_days=evidence_window_days,
        evidence_count=len(late_phase),
    )

    return {
        "candidate_type": CANDIDATE_TYPE_CYCLE_COMPLETION,
        "evidence_window_days": evidence_window_days,
        "evidence_count": len(late_phase),
        "supporting_dates": [obs["date"] for obs in late_phase],
        "dominant_value": "month_end",
        "baseline_value": baseline_value,
        "strength": strength,
        "confidence": confidence,
        "source_day_record_ids": [obs["record_id"] for obs in late_phase],
    }


def _detect_reflection_timing_pattern(observations: list[dict[str, Any]]) -> dict[str, Any] | None:
    return _detect_weekday_numeric_pattern(
        observations,
        candidate_type=CANDIDATE_TYPE_REFLECTION_TIMING,
        value_getter=lambda obs: float(obs["ritual_count"]) if obs["ritual_count"] > 0 else None,
        prefer_higher=True,
    )


def detect_calendar_rhythm_pattern_candidates_v1(
    *,
    user_id: str,
    day_records: list[dict[str, Any]] | None = None,
    month_maps: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """
    Scan day records and/or month maps for rhythm pattern candidates.

    Returns only candidates passing v1 thresholds. No confirmed patterns or recommendations.
    """
    if not user_id:
        raise CalendarRhythmPatternCandidateError("user_id required")

    observations, month_map_ids, all_record_ids = _collect_observations(
        user_id=user_id,
        day_records=day_records,
        month_maps=month_maps,
    )
    if not observations:
        return []

    detectors = (
        lambda: _detect_weekday_numeric_pattern(
            observations,
            candidate_type=CANDIDATE_TYPE_ENERGY_WEEKDAY,
            value_getter=lambda obs: float(obs["energy_score"]) if obs["energy_score"] is not None else None,
            prefer_higher=True,
        ),
        lambda: _detect_weekday_numeric_pattern(
            observations,
            candidate_type=CANDIDATE_TYPE_MOOD_WEEKDAY,
            value_getter=lambda obs: float(obs["mood_score"]) if obs["mood_score"] is not None else None,
            prefer_higher=False,
        ),
        lambda: _detect_completion_weekday_pattern(observations),
        lambda: _detect_practice_consistency_pattern(observations),
        lambda: _detect_recovery_day_pattern(observations),
        lambda: _detect_overload_density_pattern(observations),
        lambda: _detect_cycle_completion_pattern(observations),
        lambda: _detect_reflection_timing_pattern(observations),
    )

    candidates: list[dict[str, Any]] = []
    for detect in detectors:
        draft = detect()
        if draft is None:
            continue
        candidate = build_calendar_rhythm_pattern_candidate_v1(
            user_id=user_id,
            candidate_type=draft["candidate_type"],
            source_month_map_ids=month_map_ids,
            source_day_record_ids=draft.get("source_day_record_ids") or all_record_ids,
            evidence_window_days=draft["evidence_window_days"],
            evidence_count=draft["evidence_count"],
            supporting_dates=draft["supporting_dates"],
            dominant_value=draft["dominant_value"],
            baseline_value=draft["baseline_value"],
            strength=draft["strength"],
            confidence=draft["confidence"],
        )
        if candidate is not None:
            candidates.append(candidate)

    return candidates
