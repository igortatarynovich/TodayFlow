"""P1.17 — Aggregate learning signals into pattern candidates (never Pattern or Knowledge)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.day_model_v1_surface_learning_signal import (
    DAY_SURFACE_LEARNING_SIGNAL_V1_CONTRACT,
    SIGNAL_DIRECTION_NEGATIVE,
    SIGNAL_DIRECTION_NEUTRAL,
    SIGNAL_DIRECTION_POSITIVE,
    validate_day_surface_learning_signal_v1,
)

DAY_PATTERN_CANDIDATE_V1_CONTRACT = "day_pattern_candidate_v1"

CANDIDATE_TYPE_CONTENT_PREFERENCE = "content_preference"
CANDIDATE_TYPE_SURFACE_PREFERENCE = "surface_preference"
CANDIDATE_TYPE_ACTION_PREFERENCE = "action_preference"
CANDIDATE_TYPE_TEMPO_PREFERENCE = "tempo_preference"
CANDIDATE_TYPE_RISK_TOLERANCE_SIGNAL = "risk_tolerance_signal"

ALLOWED_CANDIDATE_TYPES = frozenset(
    {
        CANDIDATE_TYPE_CONTENT_PREFERENCE,
        CANDIDATE_TYPE_SURFACE_PREFERENCE,
        CANDIDATE_TYPE_ACTION_PREFERENCE,
        CANDIDATE_TYPE_TEMPO_PREFERENCE,
        CANDIDATE_TYPE_RISK_TOLERANCE_SIGNAL,
    }
)

STATUS_FORMED = "formed"

MIN_SIGNALS_FOR_CANDIDATE = 3
MIN_SIGNALS_FOR_PROMOTION = 5
MIN_EVIDENCE_DAYS_FOR_PROMOTION = 14
PROMOTION_CONFIDENCE_THRESHOLD = 0.65

FORBIDDEN_CANDIDATE_FIELDS = frozenset(
    {
        "pattern_confirmed",
        "pattern_id",
        "behavior_pattern",
        "behavior_knowledge",
        "knowledge_atom",
        "profile_update",
        "recommendation",
        "recommendation_id",
        "memory_write",
        "ukm_atom_id",
    }
)

DAY_PATTERN_CANDIDATE_V1_KEYS = frozenset(
    {
        "contract_version",
        "pattern_candidate_id",
        "candidate_type",
        "aggregation_key",
        "source_signals",
        "signal_count",
        "positive_count",
        "negative_count",
        "neutral_count",
        "confidence",
        "evidence_window",
        "status",
        "promotion_eligible",
        "memory_update_allowed",
        "profile_update_allowed",
        "ranking_update_allowed",
        "created_at",
    }
)


class DayPatternCandidateError(ValueError):
    """Raised when pattern candidate inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso(ts: str) -> datetime:
    normalized = ts.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def _require_valid_signals(signals: list[dict[str, Any]]) -> None:
    if not signals:
        raise DayPatternCandidateError("signals list must not be empty")
    for signal in signals:
        if signal.get("contract_version") != DAY_SURFACE_LEARNING_SIGNAL_V1_CONTRACT:
            raise DayPatternCandidateError("signal has invalid contract_version")
        errors = validate_day_surface_learning_signal_v1(signal)
        if errors:
            raise DayPatternCandidateError("; ".join(errors))


def _count_directions(signals: list[dict[str, Any]]) -> tuple[int, int, int]:
    positive = negative = neutral = 0
    for signal in signals:
        direction = signal.get("signal_direction")
        if direction == SIGNAL_DIRECTION_POSITIVE:
            positive += 1
        elif direction == SIGNAL_DIRECTION_NEGATIVE:
            negative += 1
        else:
            neutral += 1
    return positive, negative, neutral


def _signals_are_coherent(positive: int, negative: int, total: int) -> bool:
    if total < MIN_SIGNALS_FOR_CANDIDATE:
        return False
    if positive >= 1 and negative >= 1:
        if positive == negative:
            return False
        directional_total = positive + negative
        if directional_total <= 2:
            return False
        dominant = max(positive, negative)
        if dominant / directional_total < 0.67:
            return False
    return True


def _compute_confidence(
    positive: int,
    negative: int,
    neutral: int,
    total: int,
) -> float:
    if total == 0:
        return 0.0
    directional = positive + negative
    if directional == 0:
        base = 0.25
    else:
        dominance = max(positive, negative) / directional
        base = dominance * 0.65
    volume_boost = min(total / MIN_SIGNALS_FOR_PROMOTION, 1.0) * 0.25
    neutral_penalty = (neutral / total) * 0.1
    return round(min(max(base + volume_boost - neutral_penalty, 0.0), 1.0), 2)


def _evidence_window(signals: list[dict[str, Any]]) -> dict[str, Any]:
    timestamps = sorted(_parse_iso(s["created_at"]) for s in signals)
    start_at = timestamps[0].replace(microsecond=0).isoformat().replace("+00:00", "Z")
    end_at = timestamps[-1].replace(microsecond=0).isoformat().replace("+00:00", "Z")
    days = (timestamps[-1].date() - timestamps[0].date()).days
    return {"start_at": start_at, "end_at": end_at, "days": days}


def evaluate_promotion_eligible(
    *,
    signal_count: int,
    evidence_days: int,
    confidence: float,
) -> bool:
    return (
        signal_count >= MIN_SIGNALS_FOR_PROMOTION
        and evidence_days >= MIN_EVIDENCE_DAYS_FOR_PROMOTION
        and confidence > PROMOTION_CONFIDENCE_THRESHOLD
    )


def try_aggregate_pattern_candidate_v1(
    signals: list[dict[str, Any]],
    *,
    candidate_type: str,
    aggregation_key: str,
    created_at: str | None = None,
    pattern_candidate_id: str | None = None,
) -> dict[str, Any] | None:
    """
    P1.17 — aggregate learning signals into a pattern candidate when coherent.

    Returns None if aggregation conditions are not met.
    Never creates Pattern, Knowledge, or Profile updates.
    """
    _require_valid_signals(signals)

    if candidate_type not in ALLOWED_CANDIDATE_TYPES:
        raise DayPatternCandidateError(f"invalid candidate_type: {candidate_type!r}")
    if not aggregation_key:
        raise DayPatternCandidateError("aggregation_key required")

    signal_ids = [s["learning_signal_id"] for s in signals]
    if len(signal_ids) != len(set(signal_ids)):
        raise DayPatternCandidateError("duplicate learning_signal_id in batch")

    positive, negative, neutral = _count_directions(signals)
    total = len(signals)

    if not _signals_are_coherent(positive, negative, total):
        return None

    confidence = _compute_confidence(positive, negative, neutral, total)
    window = _evidence_window(signals)

    candidate = {
        "contract_version": DAY_PATTERN_CANDIDATE_V1_CONTRACT,
        "pattern_candidate_id": pattern_candidate_id or generate_pattern_candidate_id(),
        "candidate_type": candidate_type,
        "aggregation_key": aggregation_key,
        "source_signals": signal_ids,
        "signal_count": total,
        "positive_count": positive,
        "negative_count": negative,
        "neutral_count": neutral,
        "confidence": confidence,
        "evidence_window": window,
        "status": STATUS_FORMED,
        "promotion_eligible": evaluate_promotion_eligible(
            signal_count=total,
            evidence_days=window["days"],
            confidence=confidence,
        ),
        "memory_update_allowed": False,
        "profile_update_allowed": False,
        "ranking_update_allowed": False,
        "created_at": created_at or _utc_now_iso(),
    }

    errors = validate_day_pattern_candidate_v1(candidate)
    if errors:
        raise DayPatternCandidateError("; ".join(errors))
    return candidate


def generate_pattern_candidate_id() -> str:
    return f"pcand-{uuid4()}"


def validate_day_pattern_candidate_v1(candidate: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if candidate.get("contract_version") != DAY_PATTERN_CANDIDATE_V1_CONTRACT:
        errors.append("invalid contract_version")
    for key in DAY_PATTERN_CANDIDATE_V1_KEYS:
        if key not in candidate:
            errors.append(f"missing field: {key}")

    for forbidden in FORBIDDEN_CANDIDATE_FIELDS:
        if forbidden in candidate:
            errors.append(f"forbidden field: {forbidden}")

    if candidate.get("candidate_type") not in ALLOWED_CANDIDATE_TYPES:
        errors.append("invalid candidate_type")

    if candidate.get("status") != STATUS_FORMED:
        errors.append("status must be formed")

    if candidate.get("memory_update_allowed") is not False:
        errors.append("memory_update_allowed must be false")
    if candidate.get("profile_update_allowed") is not False:
        errors.append("profile_update_allowed must be false")
    if candidate.get("ranking_update_allowed") is not False:
        errors.append("ranking_update_allowed must be false")

    source_signals = candidate.get("source_signals")
    if not isinstance(source_signals, list) or not source_signals:
        errors.append("source_signals must be non-empty list")

    signal_count = candidate.get("signal_count")
    if not isinstance(signal_count, int) or signal_count < MIN_SIGNALS_FOR_CANDIDATE:
        errors.append(f"signal_count must be >= {MIN_SIGNALS_FOR_CANDIDATE}")

    if isinstance(source_signals, list) and signal_count != len(source_signals):
        errors.append("signal_count must match source_signals length")

    pos = candidate.get("positive_count", 0)
    neg = candidate.get("negative_count", 0)
    neu = candidate.get("neutral_count", 0)
    if isinstance(signal_count, int) and isinstance(pos, int) and isinstance(neg, int):
        if isinstance(neu, int) and pos + neg + neu != signal_count:
            errors.append("direction counts must sum to signal_count")

    confidence = candidate.get("confidence")
    if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
        errors.append("confidence must be 0..1")

    window = candidate.get("evidence_window")
    if not isinstance(window, dict):
        errors.append("evidence_window must be object")
    elif "start_at" not in window or "end_at" not in window or "days" not in window:
        errors.append("evidence_window missing required keys")

    promotion = candidate.get("promotion_eligible")
    if not isinstance(promotion, bool):
        errors.append("promotion_eligible must be boolean")
    elif isinstance(promotion, bool) and promotion and isinstance(window, dict):
        if signal_count < MIN_SIGNALS_FOR_PROMOTION:
            errors.append("promotion_eligible requires >= 5 signals")
        if window.get("days", 0) < MIN_EVIDENCE_DAYS_FOR_PROMOTION:
            errors.append("promotion_eligible requires >= 14 day window")
        if isinstance(confidence, (int, float)) and confidence <= PROMOTION_CONFIDENCE_THRESHOLD:
            errors.append("promotion_eligible requires confidence above threshold")

    return errors
