"""C2.1 — Practice runtime event contracts (source facts for C2.0 emitter)."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.data.ascetic_definition_registry_loader import get_ascetic_definition
from todayflow_backend.data.cycle_definition_registry_loader import get_cycle_definition
from todayflow_backend.data.goal_definition_registry_loader import get_goal_definition
from todayflow_backend.data.habit_definition_registry_loader import get_habit_definition
from todayflow_backend.data.practice_definition_registry_loader import get_practice_definition
from todayflow_backend.data.ritual_definition_registry_loader import get_ritual_definition
from todayflow_backend.services.practice_runtime_signal_emission_v1 import (
    VERIFICATION_STATUS_PENDING,
    VERIFICATION_STATUS_REJECTED,
    VERIFICATION_STATUS_VERIFIED,
    list_cd_allowed_signal_types,
)

PRACTICE_RUNTIME_EVENT_V1_CONTRACT = "practice_runtime_event_v1"
PRACTICE_RUNTIME_EVENT_V1_VERSION = "1.0.0"

MIN_VERIFIED_CONFIDENCE_DEFAULT = 0.5

ALLOWED_RUNTIME_ENTITY_TYPES = frozenset(
    {
        "practice",
        "habit",
        "goal",
        "ascetic",
        "ritual",
        "cycle",
    }
)

ALLOWED_EVENT_KINDS = frozenset(
    {
        "practice_completed_event",
        "habit_streak_event",
        "goal_progress_event",
        "ritual_streak_event",
        "cycle_completion_event",
        "ascetic_compliance_event",
    }
)

ALLOWED_EVENT_TYPES = frozenset(
    {
        "completed",
        "streak_confirmed",
        "progress_recorded",
        "cycle_completed",
    }
)

ALLOWED_EVENT_SOURCES = frozenset(
    {
        "user_action",
        "system_detection",
        "scheduled_check",
    }
)

ALLOWED_VERIFICATION_STATUSES = frozenset(
    {
        VERIFICATION_STATUS_PENDING,
        VERIFICATION_STATUS_VERIFIED,
        VERIFICATION_STATUS_REJECTED,
    }
)

EVENT_KIND_ENTITY_BINDING: dict[str, tuple[str, str]] = {
    "practice_completed_event": ("practice", "completed"),
    "habit_streak_event": ("habit", "streak_confirmed"),
    "goal_progress_event": ("goal", "progress_recorded"),
    "ritual_streak_event": ("ritual", "streak_confirmed"),
    "cycle_completion_event": ("cycle", "cycle_completed"),
    "ascetic_compliance_event": ("ascetic", "progress_recorded"),
}

PRACTICE_COMPLETED_METADATA_KEYS = frozenset(
    {
        "duration_minutes",
        "completion_quality",
        "source_surface",
    }
)

HABIT_STREAK_METADATA_KEYS = frozenset(
    {
        "streak_length",
        "period_days",
        "missed_days",
        "threshold_met",
    }
)

GOAL_PROGRESS_METADATA_KEYS = frozenset(
    {
        "progress_value",
        "target_value",
        "milestone_code",
        "period_type",
    }
)

RITUAL_STREAK_METADATA_KEYS = frozenset(
    {
        "streak_length",
        "completed_components_count",
        "required_components_count",
        "threshold_met",
    }
)

CYCLE_COMPLETION_METADATA_KEYS = frozenset(
    {
        "duration_days",
        "completion_rate",
        "required_threshold",
        "completed_components_count",
    }
)

ASCETIC_COMPLIANCE_METADATA_KEYS = frozenset(
    {
        "compliance_status",
        "compliance_days",
        "safety_flag",
        "emits_signal",
    }
)

METADATA_KEYS_BY_EVENT_KIND: dict[str, frozenset[str]] = {
    "practice_completed_event": PRACTICE_COMPLETED_METADATA_KEYS,
    "habit_streak_event": HABIT_STREAK_METADATA_KEYS,
    "goal_progress_event": GOAL_PROGRESS_METADATA_KEYS,
    "ritual_streak_event": RITUAL_STREAK_METADATA_KEYS,
    "cycle_completion_event": CYCLE_COMPLETION_METADATA_KEYS,
    "ascetic_compliance_event": ASCETIC_COMPLIANCE_METADATA_KEYS,
}

FORBIDDEN_EVENT_FIELDS = frozenset(
    {
        "promotion_allowed",
        "promoted_stage",
        "progression_signal_id",
        "progression_signal",
        "evolution_score",
        "evolution_state",
        "achievement_id",
        "reward_id",
        "memory_write",
        "profile_update",
        "commerce_hook",
    }
)

FORBIDDEN_EVENT_FIELD_PATTERN = re.compile(
    r"(achievement|commerce|unlock|purchase|reward|badge|payment|subscription|promotion|memory|profile)",
    re.I,
)

PRACTICE_RUNTIME_EVENT_V1_KEYS = frozenset(
    {
        "contract_version",
        "event_id",
        "user_id",
        "runtime_entity_type",
        "definition_code",
        "event_kind",
        "event_type",
        "occurred_at",
        "source",
        "verification_status",
        "confidence",
        "metadata",
        "created_at",
        "version",
    }
)


class PracticeRuntimeEventError(ValueError):
    """Raised when runtime event inputs or payload are invalid."""


def _get_cd_definition_entry(runtime_entity_type: str, definition_code: str) -> dict[str, Any]:
    if runtime_entity_type == "practice":
        return get_practice_definition(definition_code)
    if runtime_entity_type == "habit":
        return get_habit_definition(definition_code)
    if runtime_entity_type == "goal":
        return get_goal_definition(definition_code)
    if runtime_entity_type == "ascetic":
        return get_ascetic_definition(definition_code)
    if runtime_entity_type == "ritual":
        return get_ritual_definition(definition_code)
    if runtime_entity_type == "cycle":
        return get_cycle_definition(definition_code)
    raise PracticeRuntimeEventError(f"unknown runtime_entity_type: {runtime_entity_type!r}")


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _validate_metadata_for_event_kind(event_kind: str, metadata: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    prefix = f"metadata[{event_kind}]"
    expected_keys = METADATA_KEYS_BY_EVENT_KIND.get(event_kind)
    if expected_keys is None:
        return [f"unknown event_kind for metadata: {event_kind!r}"]

    if set(metadata.keys()) != expected_keys:
        errors.append(f"{prefix}: keys must be exactly {sorted(expected_keys)}")

    if event_kind == "practice_completed_event":
        duration = metadata.get("duration_minutes")
        if not isinstance(duration, int) or duration < 1:
            errors.append(f"{prefix}: duration_minutes must be positive int")
        if metadata.get("completion_quality") not in {"partial", "complete"}:
            errors.append(f"{prefix}: invalid completion_quality")
        if not isinstance(metadata.get("source_surface"), str) or not metadata["source_surface"].strip():
            errors.append(f"{prefix}: source_surface must be non-empty string")

    elif event_kind == "habit_streak_event":
        for field in ("streak_length", "period_days", "missed_days"):
            val = metadata.get(field)
            if not isinstance(val, int) or val < 0:
                errors.append(f"{prefix}: {field} must be non-negative int")
        if not isinstance(metadata.get("threshold_met"), bool):
            errors.append(f"{prefix}: threshold_met must be boolean")

    elif event_kind == "goal_progress_event":
        progress = metadata.get("progress_value")
        target = metadata.get("target_value")
        if not isinstance(progress, int) or progress < 0:
            errors.append(f"{prefix}: progress_value must be non-negative int")
        if not isinstance(target, int) or target < 1:
            errors.append(f"{prefix}: target_value must be positive int")
        if progress is not None and target is not None and isinstance(progress, int) and progress > target:
            errors.append(f"{prefix}: progress_value cannot exceed target_value")
        milestone = metadata.get("milestone_code")
        if milestone is not None and (not isinstance(milestone, str) or not milestone.strip()):
            errors.append(f"{prefix}: milestone_code must be non-empty string or null")
        if metadata.get("period_type") not in {"weekly", "milestone", "long_horizon"}:
            errors.append(f"{prefix}: invalid period_type")

    elif event_kind == "ritual_streak_event":
        for field in ("streak_length", "completed_components_count", "required_components_count"):
            val = metadata.get(field)
            if not isinstance(val, int) or val < 0:
                errors.append(f"{prefix}: {field} must be non-negative int")
        if not isinstance(metadata.get("threshold_met"), bool):
            errors.append(f"{prefix}: threshold_met must be boolean")

    elif event_kind == "cycle_completion_event":
        duration = metadata.get("duration_days")
        if duration not in {7, 21, 30, 90}:
            errors.append(f"{prefix}: duration_days must be 7, 21, 30, or 90")
        rate = metadata.get("completion_rate")
        if not isinstance(rate, (int, float)) or rate < 0 or rate > 1:
            errors.append(f"{prefix}: completion_rate must be 0..1")
        threshold = metadata.get("required_threshold")
        if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 1:
            errors.append(f"{prefix}: required_threshold must be 0..1")
        count = metadata.get("completed_components_count")
        if not isinstance(count, int) or count < 0:
            errors.append(f"{prefix}: completed_components_count must be non-negative int")

    elif event_kind == "ascetic_compliance_event":
        if metadata.get("compliance_status") not in {"kept", "broken", "partial"}:
            errors.append(f"{prefix}: invalid compliance_status")
        days = metadata.get("compliance_days")
        if not isinstance(days, int) or days < 0:
            errors.append(f"{prefix}: compliance_days must be non-negative int")
        if not isinstance(metadata.get("safety_flag"), bool):
            errors.append(f"{prefix}: safety_flag must be boolean")
        if metadata.get("emits_signal") is not False:
            errors.append(f"{prefix}: emits_signal must be false for ascetic compliance")

    return errors


def build_practice_runtime_event_v1(
    *,
    user_id: str,
    runtime_entity_type: str,
    definition_code: str,
    event_kind: str,
    occurred_at: str,
    source: str,
    verification_status: str,
    confidence: float,
    metadata: dict[str, Any],
    event_id: str | None = None,
    created_at: str | None = None,
    min_verified_confidence: float = MIN_VERIFIED_CONFIDENCE_DEFAULT,
) -> dict[str, Any]:
    """Build validated runtime event. Does not create progression signals."""
    binding = EVENT_KIND_ENTITY_BINDING.get(event_kind)
    if binding is None:
        raise PracticeRuntimeEventError(f"unknown event_kind: {event_kind!r}")

    expected_entity, expected_event_type = binding
    if runtime_entity_type != expected_entity:
        raise PracticeRuntimeEventError(
            f"runtime_entity_type {runtime_entity_type!r} incompatible with event_kind {event_kind!r}"
        )

    if verification_status == VERIFICATION_STATUS_VERIFIED and confidence < min_verified_confidence:
        raise PracticeRuntimeEventError(
            f"confidence {confidence} below verified threshold {min_verified_confidence}"
        )

    event = {
        "contract_version": PRACTICE_RUNTIME_EVENT_V1_CONTRACT,
        "event_id": event_id or str(uuid4()),
        "user_id": user_id,
        "runtime_entity_type": runtime_entity_type,
        "definition_code": definition_code,
        "event_kind": event_kind,
        "event_type": expected_event_type,
        "occurred_at": occurred_at,
        "source": source,
        "verification_status": verification_status,
        "confidence": confidence,
        "metadata": dict(metadata),
        "created_at": created_at or _utc_now_iso(),
        "version": PRACTICE_RUNTIME_EVENT_V1_VERSION,
    }

    errors = validate_practice_runtime_event_v1(
        event,
        min_verified_confidence=min_verified_confidence,
    )
    if errors:
        raise PracticeRuntimeEventError("; ".join(errors[:8]))
    return event


def validate_practice_runtime_event_v1(
    event: dict[str, Any],
    *,
    min_verified_confidence: float = MIN_VERIFIED_CONFIDENCE_DEFAULT,
) -> list[str]:
    errors: list[str] = []

    if event.get("contract_version") != PRACTICE_RUNTIME_EVENT_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in PRACTICE_RUNTIME_EVENT_V1_KEYS:
        if key not in event:
            errors.append(f"missing field: {key}")

    for key in event:
        if key in FORBIDDEN_EVENT_FIELDS:
            errors.append(f"forbidden field: {key}")
        if FORBIDDEN_EVENT_FIELD_PATTERN.search(key):
            errors.append(f"forbidden field name: {key}")

    runtime_entity_type = event.get("runtime_entity_type")
    definition_code = event.get("definition_code")
    event_kind = event.get("event_kind")
    event_type = event.get("event_type")

    if runtime_entity_type not in ALLOWED_RUNTIME_ENTITY_TYPES:
        errors.append("invalid runtime_entity_type")

    if event_kind not in ALLOWED_EVENT_KINDS:
        errors.append("invalid event_kind")

    if event_type not in ALLOWED_EVENT_TYPES:
        errors.append("invalid event_type")

    if isinstance(event_kind, str) and event_kind in EVENT_KIND_ENTITY_BINDING:
        expected_entity, expected_type = EVENT_KIND_ENTITY_BINDING[event_kind]
        if runtime_entity_type != expected_entity:
            errors.append(f"runtime_entity_type must be {expected_entity!r} for {event_kind!r}")
        if event_type != expected_type:
            errors.append(f"event_type must be {expected_type!r} for {event_kind!r}")

    if event.get("source") not in ALLOWED_EVENT_SOURCES:
        errors.append("invalid source")

    verification_status = event.get("verification_status")
    if verification_status not in ALLOWED_VERIFICATION_STATUSES:
        errors.append("invalid verification_status")

    confidence = event.get("confidence")
    if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
        errors.append("confidence must be 0..1")
    elif verification_status == VERIFICATION_STATUS_VERIFIED and float(confidence) < min_verified_confidence:
        errors.append(f"verified event requires confidence >= {min_verified_confidence}")

    if isinstance(runtime_entity_type, str) and isinstance(definition_code, str):
        try:
            _get_cd_definition_entry(runtime_entity_type, definition_code)
        except Exception as exc:
            errors.append(f"definition_code not found in CD: {exc}")

    metadata = event.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("metadata must be object")
    elif isinstance(event_kind, str):
        errors.extend(_validate_metadata_for_event_kind(event_kind, metadata))

    if event_kind == "ascetic_compliance_event":
        if verification_status == VERIFICATION_STATUS_VERIFIED:
            errors.append("ascetic compliance events remain pending-only in C2.1 (no direct signal path)")

    return errors


def resolve_emitted_signal_type_from_event(event: dict[str, Any]) -> str | None:
    """Map verified runtime event to B1.3 signal type for C2.0 path check. Ascetic returns None."""
    errors = validate_practice_runtime_event_v1(event)
    if errors:
        raise PracticeRuntimeEventError("; ".join(errors[:8]))

    event_kind = event["event_kind"]
    if event_kind == "ascetic_compliance_event":
        return None

    if event["verification_status"] != VERIFICATION_STATUS_VERIFIED:
        return None

    metadata = event.get("metadata") or {}

    if event_kind == "practice_completed_event":
        return "practice_completed"

    if event_kind == "habit_streak_event":
        if metadata.get("threshold_met") is not True:
            return None
        return "habit_streak_confirmed"

    if event_kind == "goal_progress_event":
        period_type = metadata.get("period_type")
        if metadata.get("progress_value", 0) < metadata.get("target_value", 1):
            return None
        if period_type == "weekly":
            return "weekly_goal_completed"
        return "goal_milestone_reached"

    if event_kind == "ritual_streak_event":
        if metadata.get("threshold_met") is not True:
            return None
        return "ritual_streak_confirmed"

    if event_kind == "cycle_completion_event":
        rate = metadata.get("completion_rate", 0)
        threshold = metadata.get("required_threshold", 1)
        if not isinstance(rate, (int, float)) or not isinstance(threshold, (int, float)):
            return None
        if float(rate) < float(threshold):
            return None
        return "cycle_completed"

    return None


def validate_event_emission_path_v1(event: dict[str, Any]) -> list[str]:
    """Validate that a verified event can feed C2.0 emission (path check only; C2.2 builds emission)."""
    errors = validate_practice_runtime_event_v1(event)
    if errors:
        return errors

    if event.get("event_kind") == "ascetic_compliance_event":
        if event.get("verification_status") == VERIFICATION_STATUS_VERIFIED:
            errors.append("ascetic events cannot be verified for emission in C2.1")
        return errors

    signal_type = resolve_emitted_signal_type_from_event(event)
    if event.get("verification_status") == VERIFICATION_STATUS_VERIFIED:
        if signal_type is None:
            errors.append("verified event does not resolve to an emitted signal type")
        else:
            try:
                allowed = list_cd_allowed_signal_types(
                    event["runtime_entity_type"],
                    event["definition_code"],
                )
            except Exception as exc:
                errors.append(str(exc))
                allowed = []
            if signal_type not in allowed:
                errors.append(
                    f"resolved signal {signal_type!r} not allowed by CD for "
                    f"{event['runtime_entity_type']}:{event['definition_code']!r}"
                )

    if event.get("verification_status") == VERIFICATION_STATUS_REJECTED:
        return errors

    return errors


def build_practice_completed_event_v1(
    *,
    user_id: str,
    definition_code: str,
    occurred_at: str,
    source: str,
    verification_status: str,
    confidence: float,
    duration_minutes: int,
    completion_quality: str,
    source_surface: str,
    **kwargs: Any,
) -> dict[str, Any]:
    return build_practice_runtime_event_v1(
        user_id=user_id,
        runtime_entity_type="practice",
        definition_code=definition_code,
        event_kind="practice_completed_event",
        occurred_at=occurred_at,
        source=source,
        verification_status=verification_status,
        confidence=confidence,
        metadata={
            "duration_minutes": duration_minutes,
            "completion_quality": completion_quality,
            "source_surface": source_surface,
        },
        **kwargs,
    )


def build_habit_streak_event_v1(
    *,
    user_id: str,
    definition_code: str,
    occurred_at: str,
    source: str,
    verification_status: str,
    confidence: float,
    streak_length: int,
    period_days: int,
    missed_days: int,
    threshold_met: bool,
    **kwargs: Any,
) -> dict[str, Any]:
    return build_practice_runtime_event_v1(
        user_id=user_id,
        runtime_entity_type="habit",
        definition_code=definition_code,
        event_kind="habit_streak_event",
        occurred_at=occurred_at,
        source=source,
        verification_status=verification_status,
        confidence=confidence,
        metadata={
            "streak_length": streak_length,
            "period_days": period_days,
            "missed_days": missed_days,
            "threshold_met": threshold_met,
        },
        **kwargs,
    )


def build_goal_progress_event_v1(
    *,
    user_id: str,
    definition_code: str,
    occurred_at: str,
    source: str,
    verification_status: str,
    confidence: float,
    progress_value: int,
    target_value: int,
    milestone_code: str | None,
    period_type: str,
    **kwargs: Any,
) -> dict[str, Any]:
    return build_practice_runtime_event_v1(
        user_id=user_id,
        runtime_entity_type="goal",
        definition_code=definition_code,
        event_kind="goal_progress_event",
        occurred_at=occurred_at,
        source=source,
        verification_status=verification_status,
        confidence=confidence,
        metadata={
            "progress_value": progress_value,
            "target_value": target_value,
            "milestone_code": milestone_code,
            "period_type": period_type,
        },
        **kwargs,
    )


def build_ritual_streak_event_v1(
    *,
    user_id: str,
    definition_code: str,
    occurred_at: str,
    source: str,
    verification_status: str,
    confidence: float,
    streak_length: int,
    completed_components_count: int,
    required_components_count: int,
    threshold_met: bool,
    **kwargs: Any,
) -> dict[str, Any]:
    return build_practice_runtime_event_v1(
        user_id=user_id,
        runtime_entity_type="ritual",
        definition_code=definition_code,
        event_kind="ritual_streak_event",
        occurred_at=occurred_at,
        source=source,
        verification_status=verification_status,
        confidence=confidence,
        metadata={
            "streak_length": streak_length,
            "completed_components_count": completed_components_count,
            "required_components_count": required_components_count,
            "threshold_met": threshold_met,
        },
        **kwargs,
    )


def build_cycle_completion_event_v1(
    *,
    user_id: str,
    definition_code: str,
    occurred_at: str,
    source: str,
    verification_status: str,
    confidence: float,
    duration_days: int,
    completion_rate: float,
    required_threshold: float,
    completed_components_count: int,
    **kwargs: Any,
) -> dict[str, Any]:
    return build_practice_runtime_event_v1(
        user_id=user_id,
        runtime_entity_type="cycle",
        definition_code=definition_code,
        event_kind="cycle_completion_event",
        occurred_at=occurred_at,
        source=source,
        verification_status=verification_status,
        confidence=confidence,
        metadata={
            "duration_days": duration_days,
            "completion_rate": completion_rate,
            "required_threshold": required_threshold,
            "completed_components_count": completed_components_count,
        },
        **kwargs,
    )


def build_ascetic_compliance_event_v1(
    *,
    user_id: str,
    definition_code: str,
    occurred_at: str,
    source: str,
    verification_status: str,
    confidence: float,
    compliance_status: str,
    compliance_days: int,
    safety_flag: bool,
    **kwargs: Any,
) -> dict[str, Any]:
    if verification_status == VERIFICATION_STATUS_VERIFIED:
        raise PracticeRuntimeEventError("ascetic compliance events cannot be verified in C2.1")

    return build_practice_runtime_event_v1(
        user_id=user_id,
        runtime_entity_type="ascetic",
        definition_code=definition_code,
        event_kind="ascetic_compliance_event",
        occurred_at=occurred_at,
        source=source,
        verification_status=verification_status,
        confidence=confidence,
        metadata={
            "compliance_status": compliance_status,
            "compliance_days": compliance_days,
            "safety_flag": safety_flag,
            "emits_signal": False,
        },
        **kwargs,
    )
