"""P1.16 — Map raw reactions to learning signal candidates (no memory or ranking writes)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.day_model_v1_surface_candidate_audit import (
    DAY_SURFACE_CANDIDATE_AUDIT_V1_CONTRACT,
    AUDIT_STATUS_RECORDED,
    validate_day_surface_candidate_audit_v1,
)
from todayflow_backend.services.day_model_v1_surface_exposure_reaction import (
    DAY_SURFACE_EXPOSURE_V1_CONTRACT,
    DAY_SURFACE_REACTION_V1_CONTRACT,
    REACTION_SOURCE_TIMEOUT,
    REACTION_TYPE_ASK_FOLLOWUP,
    REACTION_TYPE_COMPLETE,
    REACTION_TYPE_DISMISS,
    REACTION_TYPE_IGNORE,
    REACTION_TYPE_OPEN,
    REACTION_TYPE_RATE_NEGATIVE,
    REACTION_TYPE_RATE_POSITIVE,
    REACTION_TYPE_SAVE,
    REACTION_TYPE_SKIP,
    REACTION_TYPE_VIEW,
    validate_day_surface_exposure_v1,
    validate_day_surface_reaction_v1,
)

DAY_SURFACE_LEARNING_SIGNAL_V1_CONTRACT = "day_surface_learning_signal_v1"

SIGNAL_TYPE_USEFUL = "useful"
SIGNAL_TYPE_EFFECTIVE = "effective"
SIGNAL_TYPE_IRRELEVANT = "irrelevant"
SIGNAL_TYPE_NEGATIVE = "negative"
SIGNAL_TYPE_CURIOSITY = "curiosity"
SIGNAL_TYPE_IGNORED = "ignored"

SIGNAL_DIRECTION_POSITIVE = "positive"
SIGNAL_DIRECTION_NEGATIVE = "negative"
SIGNAL_DIRECTION_NEUTRAL = "neutral"

EVIDENCE_TYPE_EXPLICIT = "explicit"
EVIDENCE_TYPE_BEHAVIORAL = "behavioral"
EVIDENCE_TYPE_TIMEOUT = "timeout"

CONFIDENCE_LOW = "low"
CONFIDENCE_LOW_MEDIUM = "low-medium"
CONFIDENCE_MEDIUM = "medium"
CONFIDENCE_MEDIUM_HIGH = "medium-high"
CONFIDENCE_HIGH = "high"

DATASET_EFFECT_KEEP = "keep_candidate"
DATASET_EFFECT_REJECT = "reject_candidate"
DATASET_EFFECT_NEEDS_EVIDENCE = "needs_more_evidence"

ALLOWED_SIGNAL_TYPES = frozenset(
    {
        SIGNAL_TYPE_USEFUL,
        SIGNAL_TYPE_EFFECTIVE,
        SIGNAL_TYPE_IRRELEVANT,
        SIGNAL_TYPE_NEGATIVE,
        SIGNAL_TYPE_CURIOSITY,
        SIGNAL_TYPE_IGNORED,
    }
)

ALLOWED_SIGNAL_DIRECTIONS = frozenset(
    {SIGNAL_DIRECTION_POSITIVE, SIGNAL_DIRECTION_NEGATIVE, SIGNAL_DIRECTION_NEUTRAL}
)

ALLOWED_EVIDENCE_TYPES = frozenset(
    {EVIDENCE_TYPE_EXPLICIT, EVIDENCE_TYPE_BEHAVIORAL, EVIDENCE_TYPE_TIMEOUT}
)

ALLOWED_CONFIDENCE_LEVELS = frozenset(
    {
        CONFIDENCE_LOW,
        CONFIDENCE_LOW_MEDIUM,
        CONFIDENCE_MEDIUM,
        CONFIDENCE_MEDIUM_HIGH,
        CONFIDENCE_HIGH,
    }
)

ALLOWED_DATASET_EFFECTS = frozenset(
    {DATASET_EFFECT_KEEP, DATASET_EFFECT_REJECT, DATASET_EFFECT_NEEDS_EVIDENCE}
)

DAY_SURFACE_LEARNING_SIGNAL_V1_KEYS = frozenset(
    {
        "contract_version",
        "learning_signal_id",
        "reaction_id",
        "exposure_id",
        "audit_id",
        "surface",
        "signal_type",
        "signal_strength",
        "signal_direction",
        "evidence_type",
        "confidence",
        "source_keys",
        "selected_source",
        "used_llm",
        "dataset_candidate_effect",
        "created_at",
        "memory_update_allowed",
        "ranking_update_allowed",
    }
)

_REACTION_SIGNAL_MAP: dict[str, dict[str, str]] = {
    REACTION_TYPE_VIEW: {
        "signal_type": SIGNAL_TYPE_IRRELEVANT,
        "signal_direction": SIGNAL_DIRECTION_NEUTRAL,
        "evidence_type": EVIDENCE_TYPE_BEHAVIORAL,
        "confidence": CONFIDENCE_LOW,
        "dataset_candidate_effect": DATASET_EFFECT_NEEDS_EVIDENCE,
    },
    REACTION_TYPE_OPEN: {
        "signal_type": SIGNAL_TYPE_CURIOSITY,
        "signal_direction": SIGNAL_DIRECTION_NEUTRAL,
        "evidence_type": EVIDENCE_TYPE_BEHAVIORAL,
        "confidence": CONFIDENCE_MEDIUM,
        "dataset_candidate_effect": DATASET_EFFECT_NEEDS_EVIDENCE,
    },
    REACTION_TYPE_SAVE: {
        "signal_type": SIGNAL_TYPE_USEFUL,
        "signal_direction": SIGNAL_DIRECTION_POSITIVE,
        "evidence_type": EVIDENCE_TYPE_BEHAVIORAL,
        "confidence": CONFIDENCE_MEDIUM_HIGH,
        "dataset_candidate_effect": DATASET_EFFECT_KEEP,
    },
    REACTION_TYPE_COMPLETE: {
        "signal_type": SIGNAL_TYPE_EFFECTIVE,
        "signal_direction": SIGNAL_DIRECTION_POSITIVE,
        "evidence_type": EVIDENCE_TYPE_BEHAVIORAL,
        "confidence": CONFIDENCE_HIGH,
        "dataset_candidate_effect": DATASET_EFFECT_KEEP,
    },
    REACTION_TYPE_RATE_POSITIVE: {
        "signal_type": SIGNAL_TYPE_USEFUL,
        "signal_direction": SIGNAL_DIRECTION_POSITIVE,
        "evidence_type": EVIDENCE_TYPE_EXPLICIT,
        "confidence": CONFIDENCE_HIGH,
        "dataset_candidate_effect": DATASET_EFFECT_KEEP,
    },
    REACTION_TYPE_ASK_FOLLOWUP: {
        "signal_type": SIGNAL_TYPE_CURIOSITY,
        "signal_direction": SIGNAL_DIRECTION_NEUTRAL,
        "evidence_type": EVIDENCE_TYPE_BEHAVIORAL,
        "confidence": CONFIDENCE_MEDIUM,
        "dataset_candidate_effect": DATASET_EFFECT_NEEDS_EVIDENCE,
    },
    REACTION_TYPE_SKIP: {
        "signal_type": SIGNAL_TYPE_NEGATIVE,
        "signal_direction": SIGNAL_DIRECTION_NEGATIVE,
        "evidence_type": EVIDENCE_TYPE_BEHAVIORAL,
        "confidence": CONFIDENCE_MEDIUM,
        "dataset_candidate_effect": DATASET_EFFECT_NEEDS_EVIDENCE,
    },
    REACTION_TYPE_DISMISS: {
        "signal_type": SIGNAL_TYPE_NEGATIVE,
        "signal_direction": SIGNAL_DIRECTION_NEGATIVE,
        "evidence_type": EVIDENCE_TYPE_BEHAVIORAL,
        "confidence": CONFIDENCE_MEDIUM,
        "dataset_candidate_effect": DATASET_EFFECT_REJECT,
    },
    REACTION_TYPE_IGNORE: {
        "signal_type": SIGNAL_TYPE_IGNORED,
        "signal_direction": SIGNAL_DIRECTION_NEUTRAL,
        "evidence_type": EVIDENCE_TYPE_TIMEOUT,
        "confidence": CONFIDENCE_LOW_MEDIUM,
        "dataset_candidate_effect": DATASET_EFFECT_NEEDS_EVIDENCE,
    },
    REACTION_TYPE_RATE_NEGATIVE: {
        "signal_type": SIGNAL_TYPE_NEGATIVE,
        "signal_direction": SIGNAL_DIRECTION_NEGATIVE,
        "evidence_type": EVIDENCE_TYPE_EXPLICIT,
        "confidence": CONFIDENCE_HIGH,
        "dataset_candidate_effect": DATASET_EFFECT_REJECT,
    },
}


class DaySurfaceLearningSignalError(ValueError):
    """Raised when learning signal inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _derive_signal_strength(reaction: dict[str, Any]) -> float:
    weight = reaction.get("reaction_weight")
    if not isinstance(weight, (int, float)):
        return 0.0
    return round(min(abs(float(weight)), 1.0), 2)


def map_reaction_to_learning_signal_fields(reaction_type: str) -> dict[str, str]:
    """Return primary signal mapping for a reaction type."""
    mapping = _REACTION_SIGNAL_MAP.get(reaction_type)
    if mapping is None:
        raise DaySurfaceLearningSignalError(f"no signal mapping for reaction_type: {reaction_type!r}")
    return dict(mapping)


def build_day_surface_learning_signal_v1(
    reaction_record: dict[str, Any],
    exposure_record: dict[str, Any],
    audit_record: dict[str, Any],
    *,
    created_at: str | None = None,
    learning_signal_id: str | None = None,
) -> dict[str, Any]:
    """
    P1.16 — map one raw reaction to one primary learning signal candidate.

    Does not update memory, ranking, or dataset approval.
    """
    if reaction_record.get("contract_version") != DAY_SURFACE_REACTION_V1_CONTRACT:
        raise DaySurfaceLearningSignalError("reaction_record has invalid contract_version")
    if exposure_record.get("contract_version") != DAY_SURFACE_EXPOSURE_V1_CONTRACT:
        raise DaySurfaceLearningSignalError("exposure_record has invalid contract_version")
    if audit_record.get("contract_version") != DAY_SURFACE_CANDIDATE_AUDIT_V1_CONTRACT:
        raise DaySurfaceLearningSignalError("audit_record has invalid contract_version")
    if audit_record.get("status") != AUDIT_STATUS_RECORDED:
        raise DaySurfaceLearningSignalError("audit_record must have status recorded")

    audit_errors = validate_day_surface_candidate_audit_v1(audit_record)
    if audit_errors:
        raise DaySurfaceLearningSignalError("; ".join(audit_errors))

    exposure_errors = validate_day_surface_exposure_v1(
        exposure_record, audit_record=audit_record
    )
    if exposure_errors:
        raise DaySurfaceLearningSignalError("; ".join(exposure_errors))

    reaction_errors = validate_day_surface_reaction_v1(
        reaction_record,
        exposure_record=exposure_record,
        audit_record=audit_record,
    )
    if reaction_errors:
        raise DaySurfaceLearningSignalError("; ".join(reaction_errors))

    reaction_type = reaction_record["reaction_type"]
    mapped = map_reaction_to_learning_signal_fields(reaction_type)

    if reaction_type == REACTION_TYPE_IGNORE:
        if reaction_record.get("source") != REACTION_SOURCE_TIMEOUT:
            raise DaySurfaceLearningSignalError("ignore signal requires timeout-derived reaction")
        if mapped["evidence_type"] != EVIDENCE_TYPE_TIMEOUT:
            raise DaySurfaceLearningSignalError("ignore signal must use timeout evidence")

    signal = {
        "contract_version": DAY_SURFACE_LEARNING_SIGNAL_V1_CONTRACT,
        "learning_signal_id": learning_signal_id or generate_learning_signal_id(),
        "reaction_id": reaction_record["reaction_id"],
        "exposure_id": exposure_record["exposure_id"],
        "audit_id": audit_record["audit_id"],
        "surface": audit_record["surface"],
        "signal_type": mapped["signal_type"],
        "signal_strength": _derive_signal_strength(reaction_record),
        "signal_direction": mapped["signal_direction"],
        "evidence_type": mapped["evidence_type"],
        "confidence": mapped["confidence"],
        "source_keys": list(audit_record.get("source_keys") or []),
        "selected_source": audit_record["selected_source"],
        "used_llm": bool(audit_record.get("used_llm", False)),
        "dataset_candidate_effect": mapped["dataset_candidate_effect"],
        "created_at": created_at or _utc_now_iso(),
        "memory_update_allowed": False,
        "ranking_update_allowed": False,
    }

    errors = validate_day_surface_learning_signal_v1(
        signal,
        reaction_record=reaction_record,
        exposure_record=exposure_record,
        audit_record=audit_record,
    )
    if errors:
        raise DaySurfaceLearningSignalError("; ".join(errors))
    return signal


def generate_learning_signal_id() -> str:
    return f"lsig-{uuid4()}"


def validate_day_surface_learning_signal_v1(
    signal: dict[str, Any],
    *,
    reaction_record: dict[str, Any] | None = None,
    exposure_record: dict[str, Any] | None = None,
    audit_record: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if signal.get("contract_version") != DAY_SURFACE_LEARNING_SIGNAL_V1_CONTRACT:
        errors.append("invalid contract_version")
    for key in DAY_SURFACE_LEARNING_SIGNAL_V1_KEYS:
        if key not in signal:
            errors.append(f"missing field: {key}")

    if signal.get("signal_type") not in ALLOWED_SIGNAL_TYPES:
        errors.append("invalid signal_type")
    if signal.get("signal_direction") not in ALLOWED_SIGNAL_DIRECTIONS:
        errors.append("invalid signal_direction")
    if signal.get("evidence_type") not in ALLOWED_EVIDENCE_TYPES:
        errors.append("invalid evidence_type")
    if signal.get("confidence") not in ALLOWED_CONFIDENCE_LEVELS:
        errors.append("invalid confidence")
    if signal.get("dataset_candidate_effect") not in ALLOWED_DATASET_EFFECTS:
        errors.append("invalid dataset_candidate_effect")

    strength = signal.get("signal_strength")
    if not isinstance(strength, (int, float)) or strength < 0 or strength > 1:
        errors.append("signal_strength must be 0..1")

    if signal.get("memory_update_allowed") is not False:
        errors.append("memory_update_allowed must be false")
    if signal.get("ranking_update_allowed") is not False:
        errors.append("ranking_update_allowed must be false")

    reaction_type = None
    if reaction_record is not None:
        reaction_type = reaction_record.get("reaction_type")
        if signal.get("reaction_id") != reaction_record.get("reaction_id"):
            errors.append("reaction_id must match reaction_record")
        expected = map_reaction_to_learning_signal_fields(reaction_type)
        if signal.get("signal_type") != expected["signal_type"]:
            errors.append("signal_type mismatch for reaction")
        if signal.get("signal_direction") != expected["signal_direction"]:
            errors.append("signal_direction mismatch for reaction")
        if signal.get("evidence_type") != expected["evidence_type"]:
            errors.append("evidence_type mismatch for reaction")
        if signal.get("confidence") != expected["confidence"]:
            errors.append("confidence mismatch for reaction")
        if signal.get("dataset_candidate_effect") != expected["dataset_candidate_effect"]:
            errors.append("dataset_candidate_effect mismatch for reaction")
        expected_strength = _derive_signal_strength(reaction_record)
        if signal.get("signal_strength") != expected_strength:
            errors.append("signal_strength mismatch for reaction")

        if reaction_type == REACTION_TYPE_ASK_FOLLOWUP:
            if signal.get("signal_direction") == SIGNAL_DIRECTION_POSITIVE:
                errors.append("ask_followup must not be automatically positive")
        if reaction_type == REACTION_TYPE_VIEW:
            if signal.get("confidence") != CONFIDENCE_LOW:
                errors.append("view must have low confidence")
        if reaction_type == REACTION_TYPE_IGNORE:
            if reaction_record.get("source") != REACTION_SOURCE_TIMEOUT:
                errors.append("ignore reaction must be timeout-derived")
            if signal.get("evidence_type") != EVIDENCE_TYPE_TIMEOUT:
                errors.append("ignore must use timeout evidence")

    if exposure_record is not None and signal.get("exposure_id") != exposure_record.get(
        "exposure_id"
    ):
        errors.append("exposure_id must match exposure_record")

    if audit_record is not None:
        if signal.get("audit_id") != audit_record.get("audit_id"):
            errors.append("audit_id must match audit_record")
        if signal.get("surface") != audit_record.get("surface"):
            errors.append("surface must match audit_record")
        if signal.get("selected_source") != audit_record.get("selected_source"):
            errors.append("selected_source must match audit_record")
        if signal.get("used_llm") != bool(audit_record.get("used_llm", False)):
            errors.append("used_llm must match audit_record")
        audit_keys = list(audit_record.get("source_keys") or [])
        if signal.get("source_keys") != audit_keys:
            errors.append("source_keys must match audit_record")

    return errors
