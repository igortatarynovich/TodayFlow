"""E1.5 — Confirm calendar rhythm pattern candidates into confirmed patterns (no insight)."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from todayflow_backend.services.calendar_rhythm_pattern_candidate_v1 import (
    ALLOWED_CANDIDATE_TYPES,
    CALENDAR_RHYTHM_PATTERN_CANDIDATE_V1_CONTRACT,
    CANDIDATE_STATUS,
    validate_calendar_rhythm_pattern_candidate_v1,
)

CALENDAR_RHYTHM_PATTERN_V1_CONTRACT = "calendar_rhythm_pattern_v1"
CALENDAR_RHYTHM_PATTERN_V1_VERSION = "1.0.0"

PATTERN_STATUS_CONFIRMED = "confirmed"

CONFIRMATION_RESULT_CONFIRMED = "confirmed"
CONFIRMATION_RESULT_NOT_READY = "not_ready"
CONFIRMATION_RESULT_REJECTED = "rejected"

ALLOWED_CONFIRMATION_RESULTS = frozenset(
    {
        CONFIRMATION_RESULT_CONFIRMED,
        CONFIRMATION_RESULT_NOT_READY,
        CONFIRMATION_RESULT_REJECTED,
    }
)

MIN_CONFIRM_EVIDENCE_WINDOW_DAYS = 21
MIN_CONFIRM_EVIDENCE_COUNT = 6
MIN_CONFIRM_STRENGTH = 0.35
MIN_CONFIRM_CONFIDENCE = 0.55
MIN_CONFIRM_UNIQUE_SUPPORTING_DATES = 4

CALENDAR_RHYTHM_PATTERN_V1_KEYS = frozenset(
    {
        "contract_version",
        "pattern_id",
        "source_candidate_id",
        "user_id",
        "pattern_type",
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
        "expires_at",
        "insight_allowed",
        "recommendation_allowed",
        "profile_update_allowed",
        "memory_update_allowed",
        "version",
    }
)

FORBIDDEN_PATTERN_FIELDS = frozenset(
    {
        "insight",
        "insight_text",
        "recommendation",
        "recommendation_id",
        "action_advice",
        "best_day",
        "worst_day",
        "diagnosis",
        "burnout",
        "burnout_claim",
        "commerce",
        "llm_output",
        "llm_call",
        "profile",
        "profile_update",
        "memory",
        "memory_write",
        "evolution_stage",
        "evolution_update",
        "current_stage",
        "promoted_stage",
        "knowledge_atom",
        "knowledge_candidate",
    }
)


class CalendarRhythmPatternError(ValueError):
    """Raised when confirmed rhythm pattern inputs or payload are invalid."""


def _utc_now_iso() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_calendar_rhythm_pattern_id() -> str:
    return f"crp-{uuid4()}"


def _unique_supporting_dates(candidate: dict[str, Any]) -> list[str]:
    dates = candidate.get("supporting_dates") or []
    return sorted({item for item in dates if isinstance(item, str) and item})


def evaluate_rhythm_pattern_confirmation_gate_v1(
    candidate: dict[str, Any],
) -> tuple[str, list[str]]:
    """
    Evaluate whether an E1.4 candidate may become a confirmed rhythm pattern.

    Confirmed Rhythm Pattern ≠ Insight — gate checks statistical stability only.
    Returns (result, reasons).
    """
    if candidate.get("contract_version") != CALENDAR_RHYTHM_PATTERN_CANDIDATE_V1_CONTRACT:
        return CONFIRMATION_RESULT_REJECTED, ["invalid candidate contract_version"]

    if candidate.get("candidate_type") not in ALLOWED_CANDIDATE_TYPES:
        return CONFIRMATION_RESULT_REJECTED, ["invalid candidate_type"]

    if candidate.get("status") != CANDIDATE_STATUS:
        return CONFIRMATION_RESULT_REJECTED, ["candidate status must be candidate"]

    validation_errors = validate_calendar_rhythm_pattern_candidate_v1(candidate)
    if validation_errors:
        return CONFIRMATION_RESULT_REJECTED, validation_errors

    reasons: list[str] = []

    evidence_window_days = int(candidate.get("evidence_window_days", 0))
    if evidence_window_days < MIN_CONFIRM_EVIDENCE_WINDOW_DAYS:
        reasons.append(f"evidence_window_days must be >= {MIN_CONFIRM_EVIDENCE_WINDOW_DAYS}")

    evidence_count = int(candidate.get("evidence_count", 0))
    if evidence_count < MIN_CONFIRM_EVIDENCE_COUNT:
        reasons.append(f"evidence_count must be >= {MIN_CONFIRM_EVIDENCE_COUNT}")

    strength = float(candidate.get("strength", 0))
    if strength < MIN_CONFIRM_STRENGTH:
        reasons.append(f"strength must be >= {MIN_CONFIRM_STRENGTH}")

    confidence = float(candidate.get("confidence", 0))
    if confidence < MIN_CONFIRM_CONFIDENCE:
        reasons.append(f"confidence must be >= {MIN_CONFIRM_CONFIDENCE}")

    unique_dates = _unique_supporting_dates(candidate)
    if len(unique_dates) < MIN_CONFIRM_UNIQUE_SUPPORTING_DATES:
        reasons.append(f"supporting_dates must include >= {MIN_CONFIRM_UNIQUE_SUPPORTING_DATES} unique dates")

    if reasons:
        return CONFIRMATION_RESULT_NOT_READY, reasons

    return CONFIRMATION_RESULT_CONFIRMED, []


def build_calendar_rhythm_pattern_v1(
    *,
    candidate: dict[str, Any],
    pattern_id: str | None = None,
    created_at: str | None = None,
    expires_at: str | None = None,
) -> dict[str, Any]:
    """Build confirmed rhythm pattern payload from a gate-passing candidate."""
    unique_dates = _unique_supporting_dates(candidate)
    pattern = {
        "contract_version": CALENDAR_RHYTHM_PATTERN_V1_CONTRACT,
        "pattern_id": pattern_id or generate_calendar_rhythm_pattern_id(),
        "source_candidate_id": candidate["candidate_id"],
        "user_id": candidate["user_id"],
        "pattern_type": candidate["candidate_type"],
        "source_month_map_ids": list(candidate.get("source_month_map_ids") or []),
        "source_day_record_ids": list(candidate.get("source_day_record_ids") or []),
        "evidence_window_days": int(candidate["evidence_window_days"]),
        "evidence_count": int(candidate["evidence_count"]),
        "supporting_dates": unique_dates,
        "dominant_value": candidate["dominant_value"],
        "baseline_value": float(candidate["baseline_value"]),
        "strength": round(float(candidate["strength"]), 4),
        "confidence": round(float(candidate["confidence"]), 4),
        "status": PATTERN_STATUS_CONFIRMED,
        "created_at": created_at or _utc_now_iso(),
        "expires_at": expires_at,
        "insight_allowed": False,
        "recommendation_allowed": False,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "version": CALENDAR_RHYTHM_PATTERN_V1_VERSION,
    }

    errors = validate_calendar_rhythm_pattern_v1(pattern, candidate=candidate)
    if errors:
        raise CalendarRhythmPatternError("; ".join(errors))

    return pattern


def try_confirm_rhythm_pattern_from_candidate_v1(
    candidate: dict[str, Any],
    *,
    pattern_id: str | None = None,
    created_at: str | None = None,
    expires_at: str | None = None,
) -> dict[str, Any]:
    """
    E1.5 — attempt rhythm candidate → confirmed pattern via confirmation gate.

    Never creates insight, recommendation, profile update, or memory write.
    """
    result, reasons = evaluate_rhythm_pattern_confirmation_gate_v1(candidate)

    if result != CONFIRMATION_RESULT_CONFIRMED:
        return {
            "result": result,
            "pattern": None,
            "reasons": reasons,
        }

    pattern = build_calendar_rhythm_pattern_v1(
        candidate=candidate,
        pattern_id=pattern_id,
        created_at=created_at,
        expires_at=expires_at,
    )

    return {
        "result": CONFIRMATION_RESULT_CONFIRMED,
        "pattern": pattern,
        "reasons": [],
    }


def validate_calendar_rhythm_pattern_v1(
    pattern: dict[str, Any],
    *,
    candidate: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []

    if pattern.get("contract_version") != CALENDAR_RHYTHM_PATTERN_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in CALENDAR_RHYTHM_PATTERN_V1_KEYS:
        if key not in pattern:
            errors.append(f"missing field: {key}")

    forbidden = set(pattern.keys()) & FORBIDDEN_PATTERN_FIELDS
    if forbidden:
        errors.append(f"forbidden fields: {sorted(forbidden)}")

    if pattern.get("status") != PATTERN_STATUS_CONFIRMED:
        errors.append("status must be confirmed")

    if pattern.get("insight_allowed") is not False:
        errors.append("insight_allowed must be false")
    if pattern.get("recommendation_allowed") is not False:
        errors.append("recommendation_allowed must be false")
    if pattern.get("profile_update_allowed") is not False:
        errors.append("profile_update_allowed must be false")
    if pattern.get("memory_update_allowed") is not False:
        errors.append("memory_update_allowed must be false")

    pattern_type = pattern.get("pattern_type")
    if pattern_type not in ALLOWED_CANDIDATE_TYPES:
        errors.append("invalid pattern_type")

    for field in ("source_month_map_ids", "source_day_record_ids", "supporting_dates"):
        value = pattern.get(field)
        if not isinstance(value, list):
            errors.append(f"{field} must be array")

    evidence_window_days = pattern.get("evidence_window_days")
    if not isinstance(evidence_window_days, int) or evidence_window_days < MIN_CONFIRM_EVIDENCE_WINDOW_DAYS:
        errors.append(f"evidence_window_days must be >= {MIN_CONFIRM_EVIDENCE_WINDOW_DAYS}")

    evidence_count = pattern.get("evidence_count")
    if not isinstance(evidence_count, int) or evidence_count < MIN_CONFIRM_EVIDENCE_COUNT:
        errors.append(f"evidence_count must be >= {MIN_CONFIRM_EVIDENCE_COUNT}")

    supporting_dates = pattern.get("supporting_dates")
    if isinstance(supporting_dates, list):
        unique_count = len({item for item in supporting_dates if isinstance(item, str) and item})
        if unique_count < MIN_CONFIRM_UNIQUE_SUPPORTING_DATES:
            errors.append(
                f"supporting_dates must include >= {MIN_CONFIRM_UNIQUE_SUPPORTING_DATES} unique dates"
            )

    for field in ("strength", "confidence"):
        value = pattern.get(field)
        if not isinstance(value, (int, float)):
            errors.append(f"{field} must be number")
        elif value < 0 or value > 1:
            errors.append(f"{field} must be between 0 and 1")

    strength = pattern.get("strength")
    if isinstance(strength, (int, float)) and strength < MIN_CONFIRM_STRENGTH:
        errors.append(f"strength must be >= {MIN_CONFIRM_STRENGTH}")

    confidence = pattern.get("confidence")
    if isinstance(confidence, (int, float)) and confidence < MIN_CONFIRM_CONFIDENCE:
        errors.append(f"confidence must be >= {MIN_CONFIRM_CONFIDENCE}")

    if candidate is not None:
        if pattern.get("source_candidate_id") != candidate.get("candidate_id"):
            errors.append("source_candidate_id must match candidate")
        if pattern.get("pattern_type") != candidate.get("candidate_type"):
            errors.append("pattern_type must match candidate_type")
        if pattern.get("user_id") != candidate.get("user_id"):
            errors.append("user_id must match candidate")

    return errors
