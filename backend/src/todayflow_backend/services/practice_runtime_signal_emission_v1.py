"""C2.0 — Practice runtime signal emission contract (Branch C → B1.3)."""

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
from todayflow_backend.data.progression_signal_registry_loader import load_progression_signal_registry_v1
from todayflow_backend.data.ritual_definition_registry_loader import get_ritual_definition
from todayflow_backend.services.progression_signal_v1 import (
    VERIFICATION_STATUS_PENDING,
    VERIFICATION_STATUS_REJECTED,
    VERIFICATION_STATUS_VERIFIED,
    build_progression_signal_v1,
    validate_progression_signal_v1,
)

PRACTICE_RUNTIME_SIGNAL_EMISSION_V1_CONTRACT = "practice_runtime_signal_emission_v1"
PRACTICE_RUNTIME_SIGNAL_EMISSION_V1_VERSION = "1.0.0"

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

RUNTIME_ENTITY_TYPES_WITH_DIRECT_EMISSION = frozenset(
    {
        "practice",
        "habit",
        "goal",
        "ritual",
        "cycle",
    }
)

DEFAULT_EVIDENCE_BY_SIGNAL_TYPE: dict[str, tuple[int, int]] = {
    "practice_completed": (1, 1),
    "habit_streak_confirmed": (7, 7),
    "goal_milestone_reached": (1, 30),
    "weekly_goal_completed": (1, 7),
    "ritual_streak_confirmed": (3, 7),
    "evening_reflection_confirmed": (1, 1),
    "cycle_completed": (1, 90),
}

FORBIDDEN_EMISSION_FIELDS = frozenset(
    {
        "promotion_allowed",
        "promoted_stage",
        "stage_promoted_at",
        "evolution_score",
        "evolution_score_delta",
        "evolution_state",
        "evolution_state_update",
        "achievement_id",
        "commerce_hook",
        "profile_update",
        "llm_context",
        "recommendation_id",
    }
)

FORBIDDEN_EMISSION_FIELD_PATTERN = re.compile(
    r"(achievement|commerce|unlock|purchase|reward|badge|payment|subscription|promotion)",
    re.I,
)

PRACTICE_RUNTIME_SIGNAL_EMISSION_V1_KEYS = frozenset(
    {
        "contract_version",
        "emission_id",
        "user_id",
        "runtime_event_id",
        "runtime_entity_type",
        "definition_code",
        "emitted_signal_type",
        "verification_status",
        "confidence",
        "occurred_at",
        "verified_at",
        "progression_signal_id",
        "created_at",
        "version",
    }
)


class PracticeRuntimeSignalEmissionError(ValueError):
    """Raised when runtime emission inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _get_definition_entry(runtime_entity_type: str, definition_code: str) -> dict[str, Any]:
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
    raise PracticeRuntimeSignalEmissionError(f"unknown runtime_entity_type: {runtime_entity_type!r}")


def list_cd_allowed_signal_types(runtime_entity_type: str, definition_code: str) -> list[str]:
    """Return signal types the CD definition may emit (C1.x produces_signals / potential)."""
    if runtime_entity_type not in ALLOWED_RUNTIME_ENTITY_TYPES:
        raise PracticeRuntimeSignalEmissionError(f"unknown runtime_entity_type: {runtime_entity_type!r}")

    if runtime_entity_type == "ascetic":
        return []

    definition = _get_definition_entry(runtime_entity_type, definition_code)
    signals = definition.get("produces_signals") or []
    return list(signals)


def resolve_source_engine_for_signal(emitted_signal_type: str) -> str:
    registry = load_progression_signal_registry_v1()
    type_def = (registry.get("signal_types") or {}).get(emitted_signal_type)
    if not isinstance(type_def, dict):
        raise PracticeRuntimeSignalEmissionError(f"unknown emitted_signal_type: {emitted_signal_type!r}")
    source_engine = type_def.get("source_engine")
    if not isinstance(source_engine, str):
        raise PracticeRuntimeSignalEmissionError(f"missing source_engine for {emitted_signal_type!r}")
    return source_engine


def build_practice_runtime_signal_emission_v1(
    *,
    user_id: str,
    runtime_event_id: str,
    runtime_entity_type: str,
    definition_code: str,
    emitted_signal_type: str,
    verification_status: str,
    confidence: float,
    occurred_at: str,
    verified_at: str | None = None,
    emission_id: str | None = None,
    progression_signal_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build runtime emission record. Does not mutate Evolution state or score."""
    if runtime_entity_type == "ascetic":
        raise PracticeRuntimeSignalEmissionError(
            "ascetic runtime_entity_type cannot emit directly until C2.x compliance policy exists"
        )

    allowed = list_cd_allowed_signal_types(runtime_entity_type, definition_code)
    if emitted_signal_type not in allowed:
        raise PracticeRuntimeSignalEmissionError(
            f"emitted_signal_type {emitted_signal_type!r} not allowed for "
            f"{runtime_entity_type}:{definition_code!r}; allowed={allowed}"
        )

    if verification_status == VERIFICATION_STATUS_VERIFIED:
        if verified_at is None:
            verified_at = _utc_now_iso()
        if progression_signal_id is not None:
            raise PracticeRuntimeSignalEmissionError(
                "progression_signal_id must not be preset; use materialize_progression_signal_from_emission_v1"
            )
    elif verification_status in {VERIFICATION_STATUS_PENDING, VERIFICATION_STATUS_REJECTED}:
        if verified_at is not None:
            raise PracticeRuntimeSignalEmissionError("verified_at must be null unless verified")
        progression_signal_id = None
    else:
        raise PracticeRuntimeSignalEmissionError("invalid verification_status")

    emission = {
        "contract_version": PRACTICE_RUNTIME_SIGNAL_EMISSION_V1_CONTRACT,
        "emission_id": emission_id or str(uuid4()),
        "user_id": user_id,
        "runtime_event_id": runtime_event_id,
        "runtime_entity_type": runtime_entity_type,
        "definition_code": definition_code,
        "emitted_signal_type": emitted_signal_type,
        "verification_status": verification_status,
        "confidence": confidence,
        "occurred_at": occurred_at,
        "verified_at": verified_at,
        "progression_signal_id": progression_signal_id,
        "created_at": created_at or _utc_now_iso(),
        "version": PRACTICE_RUNTIME_SIGNAL_EMISSION_V1_VERSION,
    }

    errors = validate_practice_runtime_signal_emission_v1(emission)
    if errors:
        raise PracticeRuntimeSignalEmissionError("; ".join(errors[:8]))
    return emission


def validate_practice_runtime_signal_emission_v1(emission: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if emission.get("contract_version") != PRACTICE_RUNTIME_SIGNAL_EMISSION_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in PRACTICE_RUNTIME_SIGNAL_EMISSION_V1_KEYS:
        if key not in emission:
            errors.append(f"missing field: {key}")

    for key in emission:
        if key in FORBIDDEN_EMISSION_FIELDS:
            errors.append(f"forbidden field: {key}")
        if FORBIDDEN_EMISSION_FIELD_PATTERN.search(key):
            errors.append(f"forbidden field name: {key}")

    runtime_entity_type = emission.get("runtime_entity_type")
    definition_code = emission.get("definition_code")
    emitted_signal_type = emission.get("emitted_signal_type")
    verification_status = emission.get("verification_status")

    if runtime_entity_type not in ALLOWED_RUNTIME_ENTITY_TYPES:
        errors.append("invalid runtime_entity_type")

    if runtime_entity_type == "ascetic":
        errors.append("ascetic direct emission not allowed in C2.0")

    confidence = emission.get("confidence")
    if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
        errors.append("confidence must be 0..1")

    if verification_status not in {
        VERIFICATION_STATUS_PENDING,
        VERIFICATION_STATUS_VERIFIED,
        VERIFICATION_STATUS_REJECTED,
    }:
        errors.append("invalid verification_status")

    verified_at = emission.get("verified_at")
    progression_signal_id = emission.get("progression_signal_id")

    if verification_status == VERIFICATION_STATUS_VERIFIED:
        if not isinstance(verified_at, str) or not verified_at:
            errors.append("verified_at required when verified")
        if progression_signal_id is not None and not isinstance(progression_signal_id, str):
            errors.append("progression_signal_id must be string or null")
    else:
        if verified_at is not None:
            errors.append("verified_at must be null unless verified")
        if progression_signal_id is not None:
            errors.append("progression_signal_id must be null unless materialized from verified emission")

    if (
        isinstance(runtime_entity_type, str)
        and isinstance(definition_code, str)
        and isinstance(emitted_signal_type, str)
        and runtime_entity_type in RUNTIME_ENTITY_TYPES_WITH_DIRECT_EMISSION
    ):
        try:
            allowed = list_cd_allowed_signal_types(runtime_entity_type, definition_code)
        except PracticeRuntimeSignalEmissionError as exc:
            errors.append(str(exc))
            allowed = []
        if allowed and emitted_signal_type not in allowed:
            errors.append(
                f"emitted_signal_type {emitted_signal_type!r} not allowed by CD for "
                f"{runtime_entity_type}:{definition_code!r}"
            )

        try:
            resolve_source_engine_for_signal(emitted_signal_type)
        except PracticeRuntimeSignalEmissionError as exc:
            errors.append(str(exc))

    return errors


def materialize_progression_signal_from_emission_v1(
    emission: dict[str, Any],
    *,
    path_theme_code: str | None = None,
    evidence_count: int | None = None,
    evidence_window_days: int | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """
    If emission is verified, build B1.3 progression_signal_v1 and attach progression_signal_id.

    Does not promote stage, update evolution state, or mutate score.
    """
    errors = validate_practice_runtime_signal_emission_v1(emission)
    if errors:
        raise PracticeRuntimeSignalEmissionError("; ".join(errors[:8]))

    if emission.get("verification_status") != VERIFICATION_STATUS_VERIFIED:
        return dict(emission), None

    if emission.get("progression_signal_id") is not None:
        raise PracticeRuntimeSignalEmissionError("emission already materialized")

    signal_type = emission["emitted_signal_type"]
    defaults = DEFAULT_EVIDENCE_BY_SIGNAL_TYPE.get(signal_type, (1, 1))
    count = evidence_count if evidence_count is not None else defaults[0]
    window = evidence_window_days if evidence_window_days is not None else defaults[1]

    progression_signal = build_progression_signal_v1(
        user_id=emission["user_id"],
        signal_type=signal_type,
        source_engine=resolve_source_engine_for_signal(signal_type),
        source_event_id=emission["runtime_event_id"],
        observed_at=emission["occurred_at"],
        verification_status=VERIFICATION_STATUS_VERIFIED,
        verified_at=emission.get("verified_at"),
        confidence=float(emission["confidence"]),
        evidence_count=count,
        evidence_window_days=window,
        path_theme_code=path_theme_code,
    )

    signal_errors = validate_progression_signal_v1(progression_signal)
    if signal_errors:
        raise PracticeRuntimeSignalEmissionError("; ".join(signal_errors[:8]))

    updated = dict(emission)
    updated["progression_signal_id"] = progression_signal["progression_signal_id"]
    return updated, progression_signal
