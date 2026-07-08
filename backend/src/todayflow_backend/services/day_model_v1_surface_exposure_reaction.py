"""P1.15 — User exposure and reaction contracts (no learning, memory, or UI API)."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.day_model_v1_surface_candidate import SELECTED_SOURCE_BLOCKED
from todayflow_backend.services.day_model_v1_surface_candidate_audit import (
    DAY_SURFACE_CANDIDATE_AUDIT_V1_CONTRACT,
    AUDIT_STATUS_RECORDED,
    validate_day_surface_candidate_audit_v1,
)

DAY_SURFACE_EXPOSURE_V1_CONTRACT = "day_surface_exposure_v1"
DAY_SURFACE_REACTION_V1_CONTRACT = "day_surface_reaction_v1"

EXPOSURE_STATUS_SHOWN = "shown"
EXPOSURE_STATUS_SKIPPED = "skipped"
EXPOSURE_STATUS_FAILED = "failed"

VISIBILITY_VISIBLE = "visible"
VISIBILITY_PARTIALLY_VISIBLE = "partially_visible"
VISIBILITY_HIDDEN = "hidden"

REACTION_STATUS_PENDING = "pending"

REACTION_SOURCE_USER = "user_action"
REACTION_SOURCE_TIMEOUT = "system_timeout"

REACTION_TYPE_VIEW = "view"
REACTION_TYPE_OPEN = "open"
REACTION_TYPE_SAVE = "save"
REACTION_TYPE_DISMISS = "dismiss"
REACTION_TYPE_COMPLETE = "complete"
REACTION_TYPE_SKIP = "skip"
REACTION_TYPE_IGNORE = "ignore"
REACTION_TYPE_RATE_POSITIVE = "rate_positive"
REACTION_TYPE_RATE_NEGATIVE = "rate_negative"
REACTION_TYPE_ASK_FOLLOWUP = "ask_followup"

ALLOWED_REACTION_TYPES = frozenset(
    {
        REACTION_TYPE_VIEW,
        REACTION_TYPE_OPEN,
        REACTION_TYPE_SAVE,
        REACTION_TYPE_DISMISS,
        REACTION_TYPE_COMPLETE,
        REACTION_TYPE_SKIP,
        REACTION_TYPE_IGNORE,
        REACTION_TYPE_RATE_POSITIVE,
        REACTION_TYPE_RATE_NEGATIVE,
        REACTION_TYPE_ASK_FOLLOWUP,
    }
)

REACTION_WEIGHTS: dict[str, float] = {
    REACTION_TYPE_VIEW: 0.1,
    REACTION_TYPE_OPEN: 0.3,
    REACTION_TYPE_SAVE: 0.7,
    REACTION_TYPE_COMPLETE: 1.0,
    REACTION_TYPE_RATE_POSITIVE: 0.9,
    REACTION_TYPE_ASK_FOLLOWUP: 0.4,
    REACTION_TYPE_SKIP: -0.3,
    REACTION_TYPE_DISMISS: -0.5,
    REACTION_TYPE_IGNORE: -0.2,
    REACTION_TYPE_RATE_NEGATIVE: -0.9,
}

ACTION_ORIENTED_SURFACES = frozenset({"action_card", "day_guidance_card"})

ALLOWED_PLACEMENTS = frozenset({"hero", "card", "modal", "list"})

FORBIDDEN_NOTES_PATTERNS = (
    re.compile(r"\bcore_profile\b", re.I),
    re.compile(r"\buser_profile\b", re.I),
    re.compile(r"\bbirth_data\b", re.I),
    re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),
    re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
)

DAY_SURFACE_EXPOSURE_V1_KEYS = frozenset(
    {
        "contract_version",
        "exposure_id",
        "audit_id",
        "surface",
        "candidate_id",
        "selected_source",
        "display_text_hash",
        "shown_at",
        "session_id",
        "placement",
        "visibility_status",
        "exposure_status",
        "reaction_status",
    }
)

DAY_SURFACE_REACTION_V1_KEYS = frozenset(
    {
        "contract_version",
        "reaction_id",
        "exposure_id",
        "audit_id",
        "reaction_type",
        "reaction_value",
        "reaction_weight",
        "occurred_at",
        "latency_ms",
        "source",
        "notes",
    }
)


class DaySurfaceExposureReactionError(ValueError):
    """Raised when exposure or reaction inputs are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _require_valid_audit(audit_record: dict[str, Any]) -> None:
    if audit_record.get("contract_version") != DAY_SURFACE_CANDIDATE_AUDIT_V1_CONTRACT:
        raise DaySurfaceExposureReactionError("audit_record has invalid contract_version")
    if audit_record.get("status") != AUDIT_STATUS_RECORDED:
        raise DaySurfaceExposureReactionError("audit_record must have status recorded")
    errors = validate_day_surface_candidate_audit_v1(audit_record)
    if errors:
        raise DaySurfaceExposureReactionError("; ".join(errors))


def _scan_forbidden_notes(notes: str) -> list[str]:
    violations: list[str] = []
    for pattern in FORBIDDEN_NOTES_PATTERNS:
        if pattern.search(notes):
            violations.append("forbidden personal data in notes")
            break
    return violations


def build_day_surface_exposure_v1(
    audit_record: dict[str, Any],
    *,
    placement: str,
    visibility_status: str = VISIBILITY_VISIBLE,
    exposure_status: str = EXPOSURE_STATUS_SHOWN,
    session_id: str | None = None,
    shown_at: str | None = None,
    exposure_id: str | None = None,
) -> dict[str, Any]:
    """
    P1.15 — record that an audited candidate was shown (or skipped/failed).

    Blocked audits cannot be exposure_status=shown. No learning or memory writes.
    """
    _require_valid_audit(audit_record)

    if placement not in ALLOWED_PLACEMENTS:
        raise DaySurfaceExposureReactionError(f"invalid placement: {placement!r}")
    if visibility_status not in {
        VISIBILITY_VISIBLE,
        VISIBILITY_PARTIALLY_VISIBLE,
        VISIBILITY_HIDDEN,
    }:
        raise DaySurfaceExposureReactionError(f"invalid visibility_status: {visibility_status!r}")
    if exposure_status not in {EXPOSURE_STATUS_SHOWN, EXPOSURE_STATUS_SKIPPED, EXPOSURE_STATUS_FAILED}:
        raise DaySurfaceExposureReactionError(f"invalid exposure_status: {exposure_status!r}")

    if audit_record.get("selected_source") == SELECTED_SOURCE_BLOCKED:
        if exposure_status == EXPOSURE_STATUS_SHOWN:
            raise DaySurfaceExposureReactionError("blocked audit cannot be exposure_status=shown")

    if exposure_status == EXPOSURE_STATUS_SHOWN:
        if not audit_record.get("display_text_hash"):
            raise DaySurfaceExposureReactionError("shown exposure requires display_text_hash")

    exposure = {
        "contract_version": DAY_SURFACE_EXPOSURE_V1_CONTRACT,
        "exposure_id": exposure_id or generate_exposure_id(),
        "audit_id": audit_record["audit_id"],
        "surface": audit_record["surface"],
        "candidate_id": audit_record["candidate_id"],
        "selected_source": audit_record["selected_source"],
        "display_text_hash": audit_record.get("display_text_hash"),
        "shown_at": shown_at or _utc_now_iso(),
        "session_id": session_id,
        "placement": placement,
        "visibility_status": visibility_status,
        "exposure_status": exposure_status,
        "reaction_status": REACTION_STATUS_PENDING,
    }

    errors = validate_day_surface_exposure_v1(exposure, audit_record=audit_record)
    if errors:
        raise DaySurfaceExposureReactionError("; ".join(errors))
    return exposure


def build_day_surface_reaction_v1(
    exposure_record: dict[str, Any],
    audit_record: dict[str, Any],
    *,
    reaction_type: str,
    source: str,
    reaction_value: Any = None,
    occurred_at: str | None = None,
    latency_ms: int | None = None,
    notes: str | None = None,
    reaction_id: str | None = None,
) -> dict[str, Any]:
    """
    P1.15 — record user (or timeout) reaction after exposure.

    Raw weight only — not a learning signal. No memory mutation.
    """
    if exposure_record.get("contract_version") != DAY_SURFACE_EXPOSURE_V1_CONTRACT:
        raise DaySurfaceExposureReactionError("exposure_record has invalid contract_version")
    _require_valid_audit(audit_record)

    exposure_errors = validate_day_surface_exposure_v1(
        exposure_record, audit_record=audit_record
    )
    if exposure_errors:
        raise DaySurfaceExposureReactionError("; ".join(exposure_errors))

    if exposure_record.get("audit_id") != audit_record.get("audit_id"):
        raise DaySurfaceExposureReactionError("exposure audit_id must match audit_record")
    if exposure_record.get("exposure_status") != EXPOSURE_STATUS_SHOWN:
        raise DaySurfaceExposureReactionError("reactions require exposure_status=shown")

    if reaction_type not in ALLOWED_REACTION_TYPES:
        raise DaySurfaceExposureReactionError(f"invalid reaction_type: {reaction_type!r}")
    if source not in {REACTION_SOURCE_USER, REACTION_SOURCE_TIMEOUT}:
        raise DaySurfaceExposureReactionError(f"invalid source: {source!r}")

    if reaction_type == REACTION_TYPE_IGNORE and source != REACTION_SOURCE_TIMEOUT:
        raise DaySurfaceExposureReactionError("ignore reaction requires source=system_timeout")
    if source == REACTION_SOURCE_TIMEOUT and reaction_type != REACTION_TYPE_IGNORE:
        raise DaySurfaceExposureReactionError("system_timeout may only create ignore reaction")

    surface = audit_record.get("surface")
    if reaction_type == REACTION_TYPE_COMPLETE and surface not in ACTION_ORIENTED_SURFACES:
        raise DaySurfaceExposureReactionError(
            f"complete reaction not allowed for surface {surface!r}"
        )

    if notes is not None:
        if not isinstance(notes, str):
            raise DaySurfaceExposureReactionError("notes must be string")
        note_errors = _scan_forbidden_notes(notes)
        if note_errors:
            raise DaySurfaceExposureReactionError(note_errors[0])

    weight = REACTION_WEIGHTS.get(reaction_type)
    if weight is None:
        raise DaySurfaceExposureReactionError(f"no weight for reaction_type: {reaction_type!r}")

    reaction = {
        "contract_version": DAY_SURFACE_REACTION_V1_CONTRACT,
        "reaction_id": reaction_id or generate_reaction_id(),
        "exposure_id": exposure_record["exposure_id"],
        "audit_id": audit_record["audit_id"],
        "reaction_type": reaction_type,
        "reaction_value": reaction_value,
        "reaction_weight": weight,
        "occurred_at": occurred_at or _utc_now_iso(),
        "latency_ms": latency_ms,
        "source": source,
        "notes": notes,
    }

    errors = validate_day_surface_reaction_v1(
        reaction,
        exposure_record=exposure_record,
        audit_record=audit_record,
    )
    if errors:
        raise DaySurfaceExposureReactionError("; ".join(errors))
    return reaction


def generate_exposure_id() -> str:
    return f"exp-{uuid4()}"


def generate_reaction_id() -> str:
    return f"react-{uuid4()}"


def validate_day_surface_exposure_v1(
    exposure: dict[str, Any],
    *,
    audit_record: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if exposure.get("contract_version") != DAY_SURFACE_EXPOSURE_V1_CONTRACT:
        errors.append("invalid contract_version")
    for key in DAY_SURFACE_EXPOSURE_V1_KEYS:
        if key not in exposure:
            errors.append(f"missing field: {key}")

    if exposure.get("reaction_status") != REACTION_STATUS_PENDING:
        errors.append("reaction_status must be pending on creation")

    if audit_record is not None:
        if exposure.get("audit_id") != audit_record.get("audit_id"):
            errors.append("audit_id must match audit_record")
        if exposure.get("display_text_hash") != audit_record.get("display_text_hash"):
            errors.append("display_text_hash must match audit_record")
        if exposure.get("candidate_id") != audit_record.get("candidate_id"):
            errors.append("candidate_id must match audit_record")
        if (
            audit_record.get("selected_source") == SELECTED_SOURCE_BLOCKED
            and exposure.get("exposure_status") == EXPOSURE_STATUS_SHOWN
        ):
            errors.append("blocked audit cannot be shown")

    return errors


def validate_day_surface_reaction_v1(
    reaction: dict[str, Any],
    *,
    exposure_record: dict[str, Any] | None = None,
    audit_record: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if reaction.get("contract_version") != DAY_SURFACE_REACTION_V1_CONTRACT:
        errors.append("invalid contract_version")
    for key in DAY_SURFACE_REACTION_V1_KEYS:
        if key not in reaction:
            errors.append(f"missing field: {key}")

    reaction_type = reaction.get("reaction_type")
    if reaction_type not in ALLOWED_REACTION_TYPES:
        errors.append("invalid reaction_type")

    expected_weight = REACTION_WEIGHTS.get(reaction_type or "")
    if reaction.get("reaction_weight") != expected_weight:
        errors.append("reaction_weight mismatch")

    if reaction_type == REACTION_TYPE_IGNORE and reaction.get("source") != REACTION_SOURCE_TIMEOUT:
        errors.append("ignore requires system_timeout source")

    if exposure_record is not None and reaction.get("exposure_id") != exposure_record.get(
        "exposure_id"
    ):
        errors.append("exposure_id must match exposure_record")

    if audit_record is not None:
        if reaction.get("audit_id") != audit_record.get("audit_id"):
            errors.append("audit_id must match audit_record")
        surface = audit_record.get("surface")
        if reaction_type == REACTION_TYPE_COMPLETE and surface not in ACTION_ORIENTED_SURFACES:
            errors.append("complete not allowed for surface")

    notes = reaction.get("notes")
    if notes is not None and isinstance(notes, str):
        errors.extend(_scan_forbidden_notes(notes))

    return errors
