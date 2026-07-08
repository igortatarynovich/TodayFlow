"""B1.3 — Progression signal contract (feeds gate eligibility, no promotion)."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.data.evolution_cd_loader import load_evolution_cd_v1
from todayflow_backend.data.evolution_cd_validator import ALLOWED_PROGRESSION_SIGNAL_TYPES
from todayflow_backend.data.progression_signal_registry_loader import (
    ALLOWED_SOURCE_ENGINES,
    load_progression_signal_registry_v1,
)
from todayflow_backend.services.evolution_user_state_v1 import PROGRESS_SNAPSHOT_V1_KEYS

PROGRESSION_SIGNAL_V1_CONTRACT = "progression_signal_v1"
PROGRESSION_SIGNAL_V1_VERSION = "1.0.0"

VERIFICATION_STATUS_PENDING = "pending"
VERIFICATION_STATUS_VERIFIED = "verified"
VERIFICATION_STATUS_REJECTED = "rejected"

ALLOWED_VERIFICATION_STATUSES = frozenset(
    {
        VERIFICATION_STATUS_PENDING,
        VERIFICATION_STATUS_VERIFIED,
        VERIFICATION_STATUS_REJECTED,
    }
)

ALLOWED_SIGNAL_STATUSES = frozenset({"active", "superseded", "revoked"})

PROGRESSION_SIGNAL_V1_KEYS = frozenset(
    {
        "contract_version",
        "progression_signal_id",
        "user_id",
        "signal_type",
        "source_engine",
        "source_event_id",
        "path_theme_code",
        "observed_at",
        "verification_status",
        "verified_at",
        "confidence",
        "evidence_count",
        "evidence_window_days",
        "contributes_to_gate_eligibility",
        "promotion_allowed",
        "status",
        "created_at",
        "version",
    }
)

FORBIDDEN_PROGRESSION_SIGNAL_FIELDS = frozenset(
    {
        "achievement_id",
        "achievement_unlocked",
        "achievements",
        "commerce_hook",
        "commerce_purchase",
        "profile_update",
        "core_profile_update",
        "memory_write",
        "recommendation",
        "recommendation_id",
        "llm_context",
        "llm_call",
        "promoted_stage",
        "stage_promoted_at",
    }
)

FORBIDDEN_SIGNAL_SOURCE_PATTERN = re.compile(
    r"(achievement|commerce|unlock|purchase|reward|badge|payment|subscription)",
    re.I,
)

_SIGNAL_TO_PROGRESS_FIELD: dict[str, str] = {
    "confirmed_pattern": "confirmed_patterns",
    "cycle_completed": "completed_cycles",
    "evening_reflection_confirmed": "reflection_events",
}


class ProgressionSignalError(ValueError):
    """Raised when progression signal inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_progression_signal_v1(
    *,
    user_id: str,
    signal_type: str,
    source_engine: str,
    source_event_id: str,
    observed_at: str,
    verification_status: str,
    confidence: float,
    evidence_count: int,
    evidence_window_days: int,
    path_theme_code: str | None = None,
    verified_at: str | None = None,
    status: str = "active",
    progression_signal_id: str | None = None,
    created_at: str | None = None,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build validated progression signal referencing B1.3 registry."""
    reg = registry if registry is not None else load_progression_signal_registry_v1()
    type_def = (reg.get("signal_types") or {}).get(signal_type)
    if not isinstance(type_def, dict):
        raise ProgressionSignalError(f"unknown signal_type: {signal_type!r}")

    if source_engine != type_def.get("source_engine"):
        raise ProgressionSignalError(
            f"source_engine {source_engine!r} does not match registry for {signal_type!r}"
        )

    contributes = _compute_contributes_to_gate_eligibility(
        verification_status=verification_status,
        confidence=confidence,
        type_def=type_def,
        status=status,
    )

    if verification_status == VERIFICATION_STATUS_VERIFIED and verified_at is None:
        verified_at = _utc_now_iso()

    signal = {
        "contract_version": PROGRESSION_SIGNAL_V1_CONTRACT,
        "progression_signal_id": progression_signal_id or str(uuid4()),
        "user_id": user_id,
        "signal_type": signal_type,
        "source_engine": source_engine,
        "source_event_id": source_event_id,
        "path_theme_code": path_theme_code,
        "observed_at": observed_at,
        "verification_status": verification_status,
        "verified_at": verified_at,
        "confidence": confidence,
        "evidence_count": evidence_count,
        "evidence_window_days": evidence_window_days,
        "contributes_to_gate_eligibility": contributes,
        "promotion_allowed": False,
        "status": status,
        "created_at": created_at or _utc_now_iso(),
        "version": PROGRESSION_SIGNAL_V1_VERSION,
    }

    errors = validate_progression_signal_v1(signal, registry=reg)
    if errors:
        raise ProgressionSignalError("; ".join(errors[:8]))
    return signal


def validate_progression_signal_v1(
    signal: dict[str, Any],
    *,
    registry: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []

    if signal.get("contract_version") != PROGRESSION_SIGNAL_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in PROGRESSION_SIGNAL_V1_KEYS:
        if key not in signal:
            errors.append(f"missing field: {key}")

    errors.extend(_validate_forbidden_fields(signal, recursive=True))

    signal_type = signal.get("signal_type")
    if signal_type not in ALLOWED_PROGRESSION_SIGNAL_TYPES:
        errors.append(f"unknown signal_type: {signal_type!r}")

    if signal.get("source_engine") not in ALLOWED_SOURCE_ENGINES:
        errors.append("invalid source_engine")

    if signal.get("verification_status") not in ALLOWED_VERIFICATION_STATUSES:
        errors.append("invalid verification_status")

    if signal.get("status") not in ALLOWED_SIGNAL_STATUSES:
        errors.append("invalid status")

    if signal.get("promotion_allowed") is not False:
        errors.append("promotion_allowed must be false")

    confidence = signal.get("confidence")
    if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
        errors.append("confidence must be 0..1")

    for int_field in ("evidence_count", "evidence_window_days"):
        val = signal.get(int_field)
        if not isinstance(val, int) or val < 0:
            errors.append(f"{int_field} must be non-negative int")

    verification_status = signal.get("verification_status")
    verified_at = signal.get("verified_at")
    if verification_status == VERIFICATION_STATUS_VERIFIED:
        if not isinstance(verified_at, str) or not verified_at:
            errors.append("verified_at required when verification_status is verified")
    elif verified_at is not None:
        errors.append("verified_at must be null unless verified")

    reg = registry if registry is not None else load_progression_signal_registry_v1()
    type_def = (reg.get("signal_types") or {}).get(signal_type or "")
    if isinstance(type_def, dict):
        if signal.get("source_engine") != type_def.get("source_engine"):
            errors.append("source_engine must match registry definition")
        if type_def.get("feeds_stage_directly") is not False:
            errors.append("registry signal type must not feed stage directly")

        contributes = signal.get("contributes_to_gate_eligibility")
        expected = _compute_contributes_to_gate_eligibility(
            verification_status=verification_status if isinstance(verification_status, str) else "",
            confidence=float(confidence) if isinstance(confidence, (int, float)) else 0.0,
            type_def=type_def,
            status=signal.get("status") if isinstance(signal.get("status"), str) else "",
        )
        if contributes is not expected:
            errors.append("contributes_to_gate_eligibility inconsistent with verification rules")

    path_theme = signal.get("path_theme_code")
    if path_theme is not None:
        cd = load_evolution_cd_v1()
        themes = cd.get("evolution_path_themes") or {}
        if path_theme not in themes:
            errors.append(f"unknown path_theme_code: {path_theme!r}")
        elif isinstance(signal_type, str) and signal_type not in (
            themes[path_theme].get("allowed_progression_signal_types") or []
        ):
            errors.append(
                f"signal_type {signal_type!r} not allowed for path theme {path_theme!r}"
            )

    return errors


def aggregate_eligibility_progress_from_signals_v1(
    signals: list[dict[str, Any]],
    *,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Aggregate verified progression signals into B1.2 progress_snapshot shape.

    Does not promote stage; read-only aggregation for eligibility evaluation.
    """
    reg = registry if registry is not None else load_progression_signal_registry_v1()

    confirmed_patterns = 0
    completed_cycles = 0
    reflection_events = 0
    signal_counts: dict[str, int] = {}
    active_day_dates: set[str] = set()
    confidences: list[float] = []

    for signal in signals:
        if not isinstance(signal, dict):
            continue
        if validate_progression_signal_v1(signal, registry=reg):
            continue
        if signal.get("status") != "active":
            continue
        if signal.get("contributes_to_gate_eligibility") is not True:
            continue

        signal_type = signal.get("signal_type")
        if not isinstance(signal_type, str):
            continue

        signal_counts[signal_type] = signal_counts.get(signal_type, 0) + 1

        progress_field = _SIGNAL_TO_PROGRESS_FIELD.get(signal_type)
        if progress_field == "confirmed_patterns":
            confirmed_patterns += 1
        elif progress_field == "completed_cycles":
            completed_cycles += 1
        elif progress_field == "reflection_events":
            reflection_events += 1

        observed_at = signal.get("observed_at")
        if isinstance(observed_at, str) and observed_at:
            active_day_dates.add(observed_at[:10])

        conf = signal.get("confidence")
        if isinstance(conf, (int, float)):
            confidences.append(float(conf))

    confidence = sum(confidences) / len(confidences) if confidences else 0.0

    progress = {
        "confirmed_patterns": confirmed_patterns,
        "completed_cycles": completed_cycles,
        "reflection_events": reflection_events,
        "active_days": len(active_day_dates),
        "signal_counts": signal_counts,
        "confidence": confidence,
    }

    if set(progress.keys()) != PROGRESS_SNAPSHOT_V1_KEYS:
        raise ProgressionSignalError("aggregated progress_snapshot shape invalid")
    return progress


def _compute_contributes_to_gate_eligibility(
    *,
    verification_status: str,
    confidence: float,
    type_def: dict[str, Any],
    status: str,
) -> bool:
    if status != "active":
        return False
    if verification_status != VERIFICATION_STATUS_VERIFIED:
        return False
    if type_def.get("feeds_gate_eligibility") is not True:
        return False
    if type_def.get("feeds_stage_directly") is not False:
        return False
    min_conf = type_def.get("min_confidence_for_gate", 0)
    if not isinstance(min_conf, (int, float)):
        min_conf = 0
    return confidence >= float(min_conf)


def _validate_forbidden_fields(
    payload: dict[str, Any],
    *,
    recursive: bool = False,
) -> list[str]:
    errors: list[str] = []
    for key, value in payload.items():
        if key in FORBIDDEN_PROGRESSION_SIGNAL_FIELDS:
            errors.append(f"forbidden field: {key}")
        if FORBIDDEN_SIGNAL_SOURCE_PATTERN.search(key):
            errors.append(f"forbidden field name: {key}")
        if recursive and isinstance(value, dict):
            errors.extend(_validate_forbidden_fields(value, recursive=True))
    return errors
