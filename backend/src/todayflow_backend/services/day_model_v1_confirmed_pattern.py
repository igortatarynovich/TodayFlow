"""P1.18 — Confirm pattern candidates into confirmed patterns (no Knowledge or Profile)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.day_model_v1_pattern_candidate import (
    ALLOWED_CANDIDATE_TYPES,
    DAY_PATTERN_CANDIDATE_V1_CONTRACT,
    MIN_EVIDENCE_DAYS_FOR_PROMOTION,
    MIN_SIGNALS_FOR_PROMOTION,
    PROMOTION_CONFIDENCE_THRESHOLD,
    STATUS_FORMED,
    validate_day_pattern_candidate_v1,
)
from todayflow_backend.services.day_model_v1_surface_learning_signal import (
    SIGNAL_DIRECTION_NEGATIVE,
    SIGNAL_DIRECTION_NEUTRAL,
    SIGNAL_DIRECTION_POSITIVE,
)

DAY_CONFIRMED_PATTERN_V1_CONTRACT = "day_confirmed_pattern_v1"

PATTERN_STATUS_CONFIRMED = "confirmed"

CONFIRMATION_RESULT_CONFIRMED = "confirmed"
CONFIRMATION_RESULT_NOT_READY = "not_ready"
CONFIRMATION_RESULT_CONFLICTED = "conflicted"
CONFIRMATION_RESULT_REJECTED = "rejected"

ALLOWED_CONFIRMATION_RESULTS = frozenset(
    {
        CONFIRMATION_RESULT_CONFIRMED,
        CONFIRMATION_RESULT_NOT_READY,
        CONFIRMATION_RESULT_CONFLICTED,
        CONFIRMATION_RESULT_REJECTED,
    }
)

MIN_DOMINANT_DIRECTION_RATIO = 0.67
MAX_CONFLICT_RATIO = 0.2

FORBIDDEN_PATTERN_FIELDS = frozenset(
    {
        "knowledge_atom",
        "knowledge_atom_id",
        "ukm_atom_id",
        "behavior_knowledge",
        "profile_update",
        "profile_field",
        "recommendation",
        "recommendation_id",
        "memory_write",
        "knowledge_candidate_id",
    }
)

DAY_CONFIRMED_PATTERN_V1_KEYS = frozenset(
    {
        "contract_version",
        "pattern_id",
        "source_pattern_candidate_id",
        "pattern_type",
        "aggregation_key",
        "evidence_signal_ids",
        "evidence_count",
        "evidence_window_days",
        "confidence",
        "direction",
        "status",
        "created_at",
        "expires_at",
        "memory_update_allowed",
        "profile_update_allowed",
        "ranking_update_allowed",
    }
)


class DayConfirmedPatternError(ValueError):
    """Raised when confirmed pattern inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _derive_direction(positive: int, negative: int) -> str:
    if positive > negative:
        return SIGNAL_DIRECTION_POSITIVE
    if negative > positive:
        return SIGNAL_DIRECTION_NEGATIVE
    return SIGNAL_DIRECTION_NEUTRAL


def _confirmation_metrics(candidate: dict[str, Any]) -> dict[str, Any]:
    positive = int(candidate.get("positive_count", 0))
    negative = int(candidate.get("negative_count", 0))
    total = int(candidate.get("signal_count", 0))
    window = candidate.get("evidence_window") or {}
    evidence_days = int(window.get("days", 0))
    confidence = float(candidate.get("confidence", 0))

    conflict_ratio = min(positive, negative) / total if total > 0 and positive > 0 and negative > 0 else 0.0
    dominant_direction_ratio = max(positive, negative) / total if total > 0 else 0.0

    return {
        "signal_count": total,
        "evidence_window_days": evidence_days,
        "confidence": confidence,
        "dominant_direction_ratio": round(dominant_direction_ratio, 4),
        "conflict_ratio": round(conflict_ratio, 4),
        "promotion_eligible": bool(candidate.get("promotion_eligible")),
    }


def evaluate_pattern_confirmation_gate(
    pattern_candidate: dict[str, Any],
) -> tuple[str, list[str]]:
    """
    Evaluate confirmation gate for a pattern candidate.

    promotion_eligible=true is necessary but not sufficient.
    Returns (result, reasons).
    """
    if pattern_candidate.get("contract_version") != DAY_PATTERN_CANDIDATE_V1_CONTRACT:
        return CONFIRMATION_RESULT_REJECTED, ["invalid pattern candidate contract_version"]

    if pattern_candidate.get("candidate_type") not in ALLOWED_CANDIDATE_TYPES:
        return CONFIRMATION_RESULT_REJECTED, ["invalid candidate_type"]

    if pattern_candidate.get("status") != STATUS_FORMED:
        return CONFIRMATION_RESULT_REJECTED, ["pattern candidate status must be formed"]

    validation_errors = validate_day_pattern_candidate_v1(pattern_candidate)
    if validation_errors:
        return CONFIRMATION_RESULT_REJECTED, validation_errors

    metrics = _confirmation_metrics(pattern_candidate)
    reasons: list[str] = []

    if metrics["conflict_ratio"] > MAX_CONFLICT_RATIO:
        return CONFIRMATION_RESULT_CONFLICTED, [
            f"conflict_ratio {metrics['conflict_ratio']} exceeds {MAX_CONFLICT_RATIO}"
        ]

    if metrics["dominant_direction_ratio"] < MIN_DOMINANT_DIRECTION_RATIO:
        if metrics["conflict_ratio"] > 0:
            return CONFIRMATION_RESULT_CONFLICTED, [
                f"dominant_direction_ratio {metrics['dominant_direction_ratio']} below {MIN_DOMINANT_DIRECTION_RATIO}"
            ]
        reasons.append(
            f"dominant_direction_ratio {metrics['dominant_direction_ratio']} below {MIN_DOMINANT_DIRECTION_RATIO}"
        )

    if not metrics["promotion_eligible"]:
        reasons.append("promotion_eligible must be true")

    if metrics["signal_count"] < MIN_SIGNALS_FOR_PROMOTION:
        reasons.append(f"signal_count must be >= {MIN_SIGNALS_FOR_PROMOTION}")

    if metrics["evidence_window_days"] < MIN_EVIDENCE_DAYS_FOR_PROMOTION:
        reasons.append(f"evidence_window_days must be >= {MIN_EVIDENCE_DAYS_FOR_PROMOTION}")

    if metrics["confidence"] <= PROMOTION_CONFIDENCE_THRESHOLD:
        reasons.append(f"confidence must be > {PROMOTION_CONFIDENCE_THRESHOLD}")

    if metrics["dominant_direction_ratio"] < MIN_DOMINANT_DIRECTION_RATIO:
        if not reasons or reasons[0].startswith("dominant"):
            pass  # already added
        elif metrics["conflict_ratio"] == 0:
            reasons.append(
                f"dominant_direction_ratio {metrics['dominant_direction_ratio']} below {MIN_DOMINANT_DIRECTION_RATIO}"
            )

    if reasons:
        return CONFIRMATION_RESULT_NOT_READY, reasons

    return CONFIRMATION_RESULT_CONFIRMED, []


def try_confirm_pattern_from_candidate_v1(
    pattern_candidate: dict[str, Any],
    *,
    expires_at: str | None = None,
    pattern_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """
    P1.18 — attempt Pattern Candidate → Confirmed Pattern via confirmation gate.

    Never creates Knowledge, Profile updates, memory writes, or recommendations.
    """
    result, reasons = evaluate_pattern_confirmation_gate(pattern_candidate)

    if result != CONFIRMATION_RESULT_CONFIRMED:
        return {
            "result": result,
            "pattern": None,
            "reasons": reasons,
        }

    positive = int(pattern_candidate["positive_count"])
    negative = int(pattern_candidate["negative_count"])
    window = pattern_candidate["evidence_window"]

    pattern = {
        "contract_version": DAY_CONFIRMED_PATTERN_V1_CONTRACT,
        "pattern_id": pattern_id or generate_confirmed_pattern_id(),
        "source_pattern_candidate_id": pattern_candidate["pattern_candidate_id"],
        "pattern_type": pattern_candidate["candidate_type"],
        "aggregation_key": pattern_candidate["aggregation_key"],
        "evidence_signal_ids": list(pattern_candidate["source_signals"]),
        "evidence_count": pattern_candidate["signal_count"],
        "evidence_window_days": window["days"],
        "confidence": pattern_candidate["confidence"],
        "direction": _derive_direction(positive, negative),
        "status": PATTERN_STATUS_CONFIRMED,
        "created_at": created_at or _utc_now_iso(),
        "expires_at": expires_at,
        "memory_update_allowed": False,
        "profile_update_allowed": False,
        "ranking_update_allowed": False,
    }

    errors = validate_day_confirmed_pattern_v1(
        pattern,
        pattern_candidate=pattern_candidate,
    )
    if errors:
        raise DayConfirmedPatternError("; ".join(errors))

    return {
        "result": CONFIRMATION_RESULT_CONFIRMED,
        "pattern": pattern,
        "reasons": [],
    }


def generate_confirmed_pattern_id() -> str:
    return f"pat-{uuid4()}"


def validate_day_confirmed_pattern_v1(
    pattern: dict[str, Any],
    *,
    pattern_candidate: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if pattern.get("contract_version") != DAY_CONFIRMED_PATTERN_V1_CONTRACT:
        errors.append("invalid contract_version")
    for key in DAY_CONFIRMED_PATTERN_V1_KEYS:
        if key not in pattern:
            errors.append(f"missing field: {key}")

    for forbidden in FORBIDDEN_PATTERN_FIELDS:
        if forbidden in pattern:
            errors.append(f"forbidden field: {forbidden}")

    if pattern.get("pattern_type") not in ALLOWED_CANDIDATE_TYPES:
        errors.append("invalid pattern_type")

    if pattern.get("status") != PATTERN_STATUS_CONFIRMED:
        errors.append("status must be confirmed")

    if pattern.get("memory_update_allowed") is not False:
        errors.append("memory_update_allowed must be false")
    if pattern.get("profile_update_allowed") is not False:
        errors.append("profile_update_allowed must be false")
    if pattern.get("ranking_update_allowed") is not False:
        errors.append("ranking_update_allowed must be false")

    confidence = pattern.get("confidence")
    if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
        errors.append("confidence must be 0..1")

    direction = pattern.get("direction")
    if direction not in {
        SIGNAL_DIRECTION_POSITIVE,
        SIGNAL_DIRECTION_NEGATIVE,
        SIGNAL_DIRECTION_NEUTRAL,
    }:
        errors.append("invalid direction")

    evidence_ids = pattern.get("evidence_signal_ids")
    evidence_count = pattern.get("evidence_count")
    if isinstance(evidence_ids, list) and isinstance(evidence_count, int):
        if evidence_count != len(evidence_ids):
            errors.append("evidence_count must match evidence_signal_ids length")
        if evidence_count < MIN_SIGNALS_FOR_PROMOTION:
            errors.append(f"evidence_count must be >= {MIN_SIGNALS_FOR_PROMOTION}")

    window_days = pattern.get("evidence_window_days")
    if isinstance(window_days, int) and window_days < MIN_EVIDENCE_DAYS_FOR_PROMOTION:
        errors.append(f"evidence_window_days must be >= {MIN_EVIDENCE_DAYS_FOR_PROMOTION}")

    if isinstance(confidence, (int, float)) and confidence <= PROMOTION_CONFIDENCE_THRESHOLD:
        errors.append("confirmed pattern requires confidence above threshold")

    if pattern_candidate is not None:
        if pattern.get("source_pattern_candidate_id") != pattern_candidate.get(
            "pattern_candidate_id"
        ):
            errors.append("source_pattern_candidate_id must match candidate")
        if pattern.get("pattern_type") != pattern_candidate.get("candidate_type"):
            errors.append("pattern_type must match candidate_type")
        if pattern.get("aggregation_key") != pattern_candidate.get("aggregation_key"):
            errors.append("aggregation_key must match candidate")
        if list(pattern.get("evidence_signal_ids") or []) != list(
            pattern_candidate.get("source_signals") or []
        ):
            errors.append("evidence_signal_ids must match candidate source_signals")
        if not pattern_candidate.get("promotion_eligible"):
            errors.append("confirmed pattern requires promotion_eligible candidate")

    return errors
