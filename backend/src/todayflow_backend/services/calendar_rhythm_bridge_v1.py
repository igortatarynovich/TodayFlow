"""E1.6 — Bridge confirmed calendar rhythm patterns to Knowledge / Evolution context."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.calendar_rhythm_pattern_candidate_v1 import (
    ALLOWED_CANDIDATE_TYPES,
    CANDIDATE_TYPE_COMPLETION_WEEKDAY,
    CANDIDATE_TYPE_CYCLE_COMPLETION,
    CANDIDATE_TYPE_ENERGY_WEEKDAY,
    CANDIDATE_TYPE_MOOD_WEEKDAY,
    CANDIDATE_TYPE_OVERLOAD_DENSITY,
    CANDIDATE_TYPE_PRACTICE_CONSISTENCY,
    CANDIDATE_TYPE_RECOVERY_DAY,
    CANDIDATE_TYPE_REFLECTION_TIMING,
)
from todayflow_backend.services.calendar_rhythm_pattern_v1 import (
    CALENDAR_RHYTHM_PATTERN_V1_CONTRACT,
    PATTERN_STATUS_CONFIRMED,
    validate_calendar_rhythm_pattern_v1,
)

CALENDAR_RHYTHM_KNOWLEDGE_CANDIDATE_V1_CONTRACT = "calendar_rhythm_knowledge_candidate_v1"
CALENDAR_RHYTHM_KNOWLEDGE_CANDIDATE_V1_VERSION = "1.0.0"

CALENDAR_EVOLUTION_PROGRESSION_CONTEXT_V1_CONTRACT = "calendar_evolution_progression_context_v1"
CALENDAR_EVOLUTION_PROGRESSION_CONTEXT_V1_VERSION = "1.0.0"

KNOWLEDGE_TYPE_TIMING = "timing"
KNOWLEDGE_TYPE_BEHAVIOR = "behavior"
KNOWLEDGE_TYPE_RHYTHM = "rhythm"

ALLOWED_KNOWLEDGE_TYPES = frozenset(
    {
        KNOWLEDGE_TYPE_TIMING,
        KNOWLEDGE_TYPE_BEHAVIOR,
        KNOWLEDGE_TYPE_RHYTHM,
    }
)

KNOWLEDGE_CANDIDATE_STATUS = "candidate"
PROGRESSION_CONTEXT_STATUS = "context"

EVOLUTION_BUCKET_RHYTHM = "rhythm"

BRIDGE_RESULT_BRIDGED = "bridged"
BRIDGE_RESULT_NOT_READY = "not_ready"
BRIDGE_RESULT_REJECTED = "rejected"

ALLOWED_BRIDGE_RESULTS = frozenset(
    {
        BRIDGE_RESULT_BRIDGED,
        BRIDGE_RESULT_NOT_READY,
        BRIDGE_RESULT_REJECTED,
    }
)

PATTERN_TYPE_TO_KNOWLEDGE_TYPE: dict[str, str] = {
    CANDIDATE_TYPE_ENERGY_WEEKDAY: KNOWLEDGE_TYPE_TIMING,
    CANDIDATE_TYPE_MOOD_WEEKDAY: KNOWLEDGE_TYPE_TIMING,
    CANDIDATE_TYPE_COMPLETION_WEEKDAY: KNOWLEDGE_TYPE_BEHAVIOR,
    CANDIDATE_TYPE_RECOVERY_DAY: KNOWLEDGE_TYPE_BEHAVIOR,
    CANDIDATE_TYPE_OVERLOAD_DENSITY: KNOWLEDGE_TYPE_RHYTHM,
    CANDIDATE_TYPE_CYCLE_COMPLETION: KNOWLEDGE_TYPE_TIMING,
    CANDIDATE_TYPE_PRACTICE_CONSISTENCY: KNOWLEDGE_TYPE_BEHAVIOR,
    CANDIDATE_TYPE_REFLECTION_TIMING: KNOWLEDGE_TYPE_TIMING,
}

PATTERN_TYPE_TO_CONTEXT_SIGNAL_CODE: dict[str, str] = {
    CANDIDATE_TYPE_ENERGY_WEEKDAY: "rhythm_energy_weekday",
    CANDIDATE_TYPE_MOOD_WEEKDAY: "rhythm_mood_weekday",
    CANDIDATE_TYPE_COMPLETION_WEEKDAY: "rhythm_completion_weekday",
    CANDIDATE_TYPE_RECOVERY_DAY: "rhythm_recovery_sequence",
    CANDIDATE_TYPE_OVERLOAD_DENSITY: "rhythm_overload_cluster",
    CANDIDATE_TYPE_CYCLE_COMPLETION: "rhythm_cycle_month_end",
    CANDIDATE_TYPE_PRACTICE_CONSISTENCY: "rhythm_practice_streak",
    CANDIDATE_TYPE_REFLECTION_TIMING: "rhythm_reflection_weekday",
}

CLAIM_PREFIX_BY_PATTERN_TYPE: dict[str, str] = {
    CANDIDATE_TYPE_ENERGY_WEEKDAY: "rhythm_energy_weekday",
    CANDIDATE_TYPE_MOOD_WEEKDAY: "rhythm_mood_weekday",
    CANDIDATE_TYPE_COMPLETION_WEEKDAY: "rhythm_completion_weekday",
    CANDIDATE_TYPE_RECOVERY_DAY: "rhythm_recovery_after_overload",
    CANDIDATE_TYPE_OVERLOAD_DENSITY: "rhythm_overload_cluster",
    CANDIDATE_TYPE_CYCLE_COMPLETION: "rhythm_cycle_month_end",
    CANDIDATE_TYPE_PRACTICE_CONSISTENCY: "rhythm_practice_streak",
    CANDIDATE_TYPE_REFLECTION_TIMING: "rhythm_reflection_weekday",
}

ALLOWED_CLAIM_PREFIXES = frozenset(CLAIM_PREFIX_BY_PATTERN_TYPE.values())

MACHINE_CLAIM_PATTERN = re.compile(r"^[a-z_]+:[a-z0-9_.-]+$")

FORBIDDEN_CLAIM_KEYWORDS = re.compile(
    r"(personality|trait|diagnos|medical|burnout|overload_claim|best_day|worst_day|"
    r"recommend|insight|user_is|they_are|he_is|she_is)",
    re.I,
)

CALENDAR_RHYTHM_KNOWLEDGE_CANDIDATE_V1_KEYS = frozenset(
    {
        "contract_version",
        "knowledge_candidate_id",
        "source_pattern_id",
        "user_id",
        "knowledge_type",
        "claim",
        "claim_strength",
        "confidence",
        "evidence_pattern_id",
        "source_month_map_ids",
        "source_day_record_ids",
        "supporting_dates",
        "evidence_count",
        "evidence_window_days",
        "status",
        "created_at",
        "requires_review",
        "profile_update_allowed",
        "memory_update_allowed",
        "ranking_update_allowed",
        "version",
    }
)

CALENDAR_EVOLUTION_PROGRESSION_CONTEXT_V1_KEYS = frozenset(
    {
        "contract_version",
        "progression_context_id",
        "user_id",
        "source_pattern_id",
        "pattern_type",
        "evolution_bucket",
        "context_signal_code",
        "dominant_value",
        "strength",
        "confidence",
        "evidence_window_days",
        "evidence_count",
        "source_month_map_ids",
        "source_day_record_ids",
        "supporting_dates",
        "status",
        "created_at",
        "evolution_stage_update_allowed",
        "profile_update_allowed",
        "memory_update_allowed",
        "insight_allowed",
        "recommendation_allowed",
        "version",
    }
)

FORBIDDEN_BRIDGE_OUTPUT_FIELDS = frozenset(
    {
        "insight",
        "insight_text",
        "recommendation",
        "recommendation_id",
        "action_advice",
        "best_day",
        "worst_day",
        "diagnosis",
        "burnout_claim",
        "commerce",
        "llm_output",
        "llm_call",
        "profile",
        "profile_update",
        "memory",
        "memory_write",
        "evolution_stage",
        "evolution_stage_update",
        "current_stage",
        "promoted_stage",
        "knowledge_atom",
        "ukm_atom_id",
        "active_knowledge",
    }
)


class CalendarRhythmBridgeError(ValueError):
    """Raised when calendar rhythm bridge inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def generate_calendar_rhythm_knowledge_candidate_id() -> str:
    return f"crkc-{uuid4()}"


def generate_calendar_evolution_progression_context_id() -> str:
    return f"cepc-{uuid4()}"


def _sanitize_claim_value(value: str) -> str:
    cleaned = value.strip().lower().replace(" ", "_")
    cleaned = re.sub(r"[^a-z0-9_.-]", "", cleaned)
    return cleaned


def build_rhythm_claim_from_pattern(pattern: dict[str, Any]) -> str | None:
    pattern_type = pattern.get("pattern_type")
    dominant_value = pattern.get("dominant_value")
    if pattern_type not in CLAIM_PREFIX_BY_PATTERN_TYPE:
        return None
    if not isinstance(dominant_value, str) or not dominant_value.strip():
        return None
    suffix = _sanitize_claim_value(dominant_value)
    if not suffix:
        return None
    return f"{CLAIM_PREFIX_BY_PATTERN_TYPE[pattern_type]}:{suffix}"


def validate_rhythm_claim(claim: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(claim, str) or not claim.strip():
        errors.append("claim required")
        return errors
    if " " in claim:
        errors.append("prose claim not allowed")
    if not MACHINE_CLAIM_PATTERN.match(claim):
        errors.append("claim must be machine-readable key:value")
    prefix = claim.split(":", 1)[0] if ":" in claim else ""
    if prefix not in ALLOWED_CLAIM_PREFIXES:
        errors.append("claim prefix not allowed")
    if FORBIDDEN_CLAIM_KEYWORDS.search(claim):
        errors.append("forbidden claim keyword")
    return errors


def _pattern_is_expired(pattern: dict[str, Any], *, now: datetime | None = None) -> bool:
    expires_at = pattern.get("expires_at")
    if not isinstance(expires_at, str) or not expires_at:
        return False
    reference = now or datetime.now(UTC)
    return _parse_iso(expires_at) < reference


def evaluate_calendar_rhythm_bridge_gate_v1(
    pattern: dict[str, Any],
    *,
    now: datetime | None = None,
) -> tuple[str, list[str]]:
    """Evaluate whether a confirmed rhythm pattern may bridge downstream."""
    if pattern.get("contract_version") != CALENDAR_RHYTHM_PATTERN_V1_CONTRACT:
        return BRIDGE_RESULT_REJECTED, ["invalid rhythm pattern contract_version"]

    if pattern.get("status") != PATTERN_STATUS_CONFIRMED:
        return BRIDGE_RESULT_REJECTED, ["pattern status must be confirmed"]

    pattern_type = pattern.get("pattern_type")
    if pattern_type not in ALLOWED_CANDIDATE_TYPES:
        return BRIDGE_RESULT_REJECTED, ["unsupported pattern_type"]

    validation_errors = validate_calendar_rhythm_pattern_v1(pattern)
    if validation_errors:
        return BRIDGE_RESULT_REJECTED, validation_errors

    if pattern.get("profile_update_allowed") is not False:
        return BRIDGE_RESULT_REJECTED, ["pattern profile_update_allowed must be false"]
    if pattern.get("memory_update_allowed") is not False:
        return BRIDGE_RESULT_REJECTED, ["pattern memory_update_allowed must be false"]

    if _pattern_is_expired(pattern, now=now):
        return BRIDGE_RESULT_NOT_READY, ["pattern expired"]

    claim = build_rhythm_claim_from_pattern(pattern)
    if claim is None:
        return BRIDGE_RESULT_NOT_READY, ["claim cannot be expressed from pattern"]

    claim_errors = validate_rhythm_claim(claim)
    if claim_errors:
        return BRIDGE_RESULT_REJECTED, claim_errors

    return BRIDGE_RESULT_BRIDGED, []


def build_calendar_rhythm_knowledge_candidate_v1(
    *,
    pattern: dict[str, Any],
    knowledge_candidate_id: str | None = None,
    created_at: str | None = None,
    requires_review: bool = True,
) -> dict[str, Any]:
    claim = build_rhythm_claim_from_pattern(pattern)
    if claim is None:
        raise CalendarRhythmBridgeError("claim cannot be expressed from pattern")

    pattern_type = pattern["pattern_type"]
    knowledge_type = PATTERN_TYPE_TO_KNOWLEDGE_TYPE[pattern_type]
    confidence = float(pattern["confidence"])

    candidate = {
        "contract_version": CALENDAR_RHYTHM_KNOWLEDGE_CANDIDATE_V1_CONTRACT,
        "knowledge_candidate_id": knowledge_candidate_id or generate_calendar_rhythm_knowledge_candidate_id(),
        "source_pattern_id": pattern["pattern_id"],
        "user_id": pattern["user_id"],
        "knowledge_type": knowledge_type,
        "claim": claim,
        "claim_strength": round(min(float(pattern["strength"]), 1.0), 4),
        "confidence": round(confidence, 4),
        "evidence_pattern_id": pattern["pattern_id"],
        "source_month_map_ids": list(pattern.get("source_month_map_ids") or []),
        "source_day_record_ids": list(pattern.get("source_day_record_ids") or []),
        "supporting_dates": list(pattern.get("supporting_dates") or []),
        "evidence_count": int(pattern["evidence_count"]),
        "evidence_window_days": int(pattern["evidence_window_days"]),
        "status": KNOWLEDGE_CANDIDATE_STATUS,
        "created_at": created_at or _utc_now_iso(),
        "requires_review": requires_review,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_update_allowed": False,
        "version": CALENDAR_RHYTHM_KNOWLEDGE_CANDIDATE_V1_VERSION,
    }

    errors = validate_calendar_rhythm_knowledge_candidate_v1(candidate, pattern=pattern)
    if errors:
        raise CalendarRhythmBridgeError("; ".join(errors))

    return candidate


def build_calendar_evolution_progression_context_v1(
    *,
    pattern: dict[str, Any],
    progression_context_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    pattern_type = pattern["pattern_type"]
    context = {
        "contract_version": CALENDAR_EVOLUTION_PROGRESSION_CONTEXT_V1_CONTRACT,
        "progression_context_id": progression_context_id or generate_calendar_evolution_progression_context_id(),
        "user_id": pattern["user_id"],
        "source_pattern_id": pattern["pattern_id"],
        "pattern_type": pattern_type,
        "evolution_bucket": EVOLUTION_BUCKET_RHYTHM,
        "context_signal_code": PATTERN_TYPE_TO_CONTEXT_SIGNAL_CODE[pattern_type],
        "dominant_value": pattern["dominant_value"],
        "strength": round(float(pattern["strength"]), 4),
        "confidence": round(float(pattern["confidence"]), 4),
        "evidence_window_days": int(pattern["evidence_window_days"]),
        "evidence_count": int(pattern["evidence_count"]),
        "source_month_map_ids": list(pattern.get("source_month_map_ids") or []),
        "source_day_record_ids": list(pattern.get("source_day_record_ids") or []),
        "supporting_dates": list(pattern.get("supporting_dates") or []),
        "status": PROGRESSION_CONTEXT_STATUS,
        "created_at": created_at or _utc_now_iso(),
        "evolution_stage_update_allowed": False,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "insight_allowed": False,
        "recommendation_allowed": False,
        "version": CALENDAR_EVOLUTION_PROGRESSION_CONTEXT_V1_VERSION,
    }

    errors = validate_calendar_evolution_progression_context_v1(context, pattern=pattern)
    if errors:
        raise CalendarRhythmBridgeError("; ".join(errors))

    return context


def try_bridge_calendar_rhythm_pattern_v1(
    pattern: dict[str, Any],
    *,
    now: datetime | None = None,
    created_at: str | None = None,
    requires_review: bool = True,
) -> dict[str, Any]:
    """
    E1.6 — bridge confirmed calendar rhythm pattern to knowledge candidate + progression context.

    Never writes profile, memory, evolution stage, insight, or recommendation.
    """
    result, reasons = evaluate_calendar_rhythm_bridge_gate_v1(pattern, now=now)

    if result != BRIDGE_RESULT_BRIDGED:
        return {
            "result": result,
            "knowledge_candidate": None,
            "progression_context": None,
            "reasons": reasons,
        }

    knowledge_candidate = build_calendar_rhythm_knowledge_candidate_v1(
        pattern=pattern,
        created_at=created_at,
        requires_review=requires_review,
    )
    progression_context = build_calendar_evolution_progression_context_v1(
        pattern=pattern,
        created_at=created_at,
    )

    return {
        "result": BRIDGE_RESULT_BRIDGED,
        "knowledge_candidate": knowledge_candidate,
        "progression_context": progression_context,
        "reasons": [],
    }


def validate_calendar_rhythm_knowledge_candidate_v1(
    candidate: dict[str, Any],
    *,
    pattern: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []

    if candidate.get("contract_version") != CALENDAR_RHYTHM_KNOWLEDGE_CANDIDATE_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in CALENDAR_RHYTHM_KNOWLEDGE_CANDIDATE_V1_KEYS:
        if key not in candidate:
            errors.append(f"missing field: {key}")

    forbidden = set(candidate.keys()) & FORBIDDEN_BRIDGE_OUTPUT_FIELDS
    if forbidden:
        errors.append(f"forbidden fields: {sorted(forbidden)}")

    if candidate.get("status") != KNOWLEDGE_CANDIDATE_STATUS:
        errors.append("status must be candidate")

    if candidate.get("knowledge_type") not in ALLOWED_KNOWLEDGE_TYPES:
        errors.append("invalid knowledge_type")

    for flag in ("profile_update_allowed", "memory_update_allowed", "ranking_update_allowed"):
        if candidate.get(flag) is not False:
            errors.append(f"{flag} must be false")

    claim = candidate.get("claim")
    if isinstance(claim, str):
        errors.extend(validate_rhythm_claim(claim))

    if pattern is not None:
        if candidate.get("source_pattern_id") != pattern.get("pattern_id"):
            errors.append("source_pattern_id must match pattern")
        expected_type = PATTERN_TYPE_TO_KNOWLEDGE_TYPE.get(pattern.get("pattern_type", ""))
        if expected_type and candidate.get("knowledge_type") != expected_type:
            errors.append("knowledge_type mismatch for pattern type")

    return errors


def validate_calendar_evolution_progression_context_v1(
    context: dict[str, Any],
    *,
    pattern: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []

    if context.get("contract_version") != CALENDAR_EVOLUTION_PROGRESSION_CONTEXT_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in CALENDAR_EVOLUTION_PROGRESSION_CONTEXT_V1_KEYS:
        if key not in context:
            errors.append(f"missing field: {key}")

    forbidden = set(context.keys()) & FORBIDDEN_BRIDGE_OUTPUT_FIELDS
    if forbidden:
        errors.append(f"forbidden fields: {sorted(forbidden)}")

    if context.get("status") != PROGRESSION_CONTEXT_STATUS:
        errors.append("status must be context")

    if context.get("evolution_bucket") != EVOLUTION_BUCKET_RHYTHM:
        errors.append("evolution_bucket must be rhythm")

    pattern_type = context.get("pattern_type")
    if pattern_type not in ALLOWED_CANDIDATE_TYPES:
        errors.append("invalid pattern_type")

    expected_code = PATTERN_TYPE_TO_CONTEXT_SIGNAL_CODE.get(str(pattern_type), "")
    if context.get("context_signal_code") != expected_code:
        errors.append("invalid context_signal_code")

    for flag in (
        "evolution_stage_update_allowed",
        "profile_update_allowed",
        "memory_update_allowed",
        "insight_allowed",
        "recommendation_allowed",
    ):
        if context.get(flag) is not False:
            errors.append(f"{flag} must be false")

    if pattern is not None:
        if context.get("source_pattern_id") != pattern.get("pattern_id"):
            errors.append("source_pattern_id must match pattern")
        if context.get("pattern_type") != pattern.get("pattern_type"):
            errors.append("pattern_type must match pattern")

    return errors
