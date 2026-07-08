"""P1.19 — Build knowledge candidates from confirmed patterns (not active Knowledge)."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.day_model_v1_confirmed_pattern import (
    DAY_CONFIRMED_PATTERN_V1_CONTRACT,
    PATTERN_STATUS_CONFIRMED,
    validate_day_confirmed_pattern_v1,
)
from todayflow_backend.services.day_model_v1_pattern_candidate import (
    ALLOWED_CANDIDATE_TYPES,
    CANDIDATE_TYPE_ACTION_PREFERENCE,
    CANDIDATE_TYPE_CONTENT_PREFERENCE,
    CANDIDATE_TYPE_RISK_TOLERANCE_SIGNAL,
    CANDIDATE_TYPE_SURFACE_PREFERENCE,
    CANDIDATE_TYPE_TEMPO_PREFERENCE,
    MIN_SIGNALS_FOR_PROMOTION,
    PROMOTION_CONFIDENCE_THRESHOLD,
)

DAY_KNOWLEDGE_CANDIDATE_V1_CONTRACT = "day_knowledge_candidate_v1"

KNOWLEDGE_TYPE_PREFERENCE = "preference"
KNOWLEDGE_TYPE_BEHAVIOR = "behavior"
KNOWLEDGE_TYPE_TIMING = "timing"
KNOWLEDGE_TYPE_CONTENT_AFFINITY = "content_affinity"
KNOWLEDGE_TYPE_RESPONSE_STYLE = "response_style"

ALLOWED_KNOWLEDGE_TYPES = frozenset(
    {
        KNOWLEDGE_TYPE_PREFERENCE,
        KNOWLEDGE_TYPE_BEHAVIOR,
        KNOWLEDGE_TYPE_TIMING,
        KNOWLEDGE_TYPE_CONTENT_AFFINITY,
        KNOWLEDGE_TYPE_RESPONSE_STYLE,
    }
)

KNOWLEDGE_CANDIDATE_STATUS = "candidate"

KNOWLEDGE_CANDIDATE_RESULT_CREATED = "created"
KNOWLEDGE_CANDIDATE_RESULT_REJECTED = "rejected"

PATTERN_TYPE_TO_KNOWLEDGE_TYPE: dict[str, str] = {
    CANDIDATE_TYPE_CONTENT_PREFERENCE: KNOWLEDGE_TYPE_CONTENT_AFFINITY,
    CANDIDATE_TYPE_SURFACE_PREFERENCE: KNOWLEDGE_TYPE_RESPONSE_STYLE,
    CANDIDATE_TYPE_ACTION_PREFERENCE: KNOWLEDGE_TYPE_BEHAVIOR,
    CANDIDATE_TYPE_TEMPO_PREFERENCE: KNOWLEDGE_TYPE_TIMING,
    CANDIDATE_TYPE_RISK_TOLERANCE_SIGNAL: KNOWLEDGE_TYPE_RESPONSE_STYLE,
}

CLAIM_PREFIX_CONTENT_AFFINITY = "prefers_content_key_group"
CLAIM_PREFIX_SURFACE = "responds_to_surface"
CLAIM_PREFIX_ACTION = "responds_to_action_mode"
CLAIM_PREFIX_TEMPO = "responds_to_tempo"
CLAIM_PREFIX_RISK = "risk_response_tolerance"

ALLOWED_CLAIM_PREFIXES = frozenset(
    {
        CLAIM_PREFIX_CONTENT_AFFINITY,
        CLAIM_PREFIX_SURFACE,
        CLAIM_PREFIX_ACTION,
        CLAIM_PREFIX_TEMPO,
        CLAIM_PREFIX_RISK,
    }
)

MACHINE_CLAIM_PATTERN = re.compile(r"^[a-z_]+:[a-z0-9_.-]+$")

FORBIDDEN_CLAIM_KEYWORDS = re.compile(
    r"(personality|trait|diagnos|medical|financial|family|political|religious|"
    r"sensitive|disorder|depression|anxiety|introvert|extrovert|disciplined|"
    r"user_is|they_are|he_is|she_is)",
    re.I,
)

FORBIDDEN_KNOWLEDGE_CANDIDATE_FIELDS = frozenset(
    {
        "knowledge_atom",
        "knowledge_atom_id",
        "ukm_atom_id",
        "active_knowledge",
        "profile_update",
        "memory_write",
        "recommendation",
        "recommendation_id",
    }
)

DAY_KNOWLEDGE_CANDIDATE_V1_KEYS = frozenset(
    {
        "contract_version",
        "knowledge_candidate_id",
        "source_pattern_id",
        "knowledge_type",
        "claim",
        "claim_strength",
        "confidence",
        "evidence_pattern_id",
        "evidence_signal_ids",
        "evidence_count",
        "evidence_window_days",
        "status",
        "created_at",
        "requires_review",
        "profile_update_allowed",
        "memory_update_allowed",
        "ranking_update_allowed",
    }
)


class DayKnowledgeCandidateError(ValueError):
    """Raised when knowledge candidate inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sanitize_claim_value(value: str) -> str:
    cleaned = value.strip().lower().replace(" ", "_")
    cleaned = re.sub(r"[^a-z0-9_.-]", "", cleaned)
    return cleaned


def build_claim_from_pattern(confirmed_pattern: dict[str, Any]) -> str | None:
    """Build machine-readable claim from confirmed pattern. Returns None if not expressible."""
    pattern_type = confirmed_pattern.get("pattern_type")
    aggregation_key = confirmed_pattern.get("aggregation_key")
    direction = confirmed_pattern.get("direction", "neutral")

    if not isinstance(aggregation_key, str) or not aggregation_key.strip():
        return None

    key = _sanitize_claim_value(aggregation_key)
    if not key:
        return None

    if pattern_type == CANDIDATE_TYPE_CONTENT_PREFERENCE:
        return f"{CLAIM_PREFIX_CONTENT_AFFINITY}:{key}"
    if pattern_type == CANDIDATE_TYPE_SURFACE_PREFERENCE:
        return f"{CLAIM_PREFIX_SURFACE}:{key}"
    if pattern_type == CANDIDATE_TYPE_ACTION_PREFERENCE:
        return f"{CLAIM_PREFIX_ACTION}:{key}"
    if pattern_type == CANDIDATE_TYPE_TEMPO_PREFERENCE:
        return f"{CLAIM_PREFIX_TEMPO}:{key}"
    if pattern_type == CANDIDATE_TYPE_RISK_TOLERANCE_SIGNAL:
        level = _sanitize_claim_value(str(direction))
        return f"{CLAIM_PREFIX_RISK}:{level}"
    return None


def validate_claim(claim: str) -> list[str]:
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
        errors.append("sensitive or trait claim not allowed")

    return errors


def evaluate_knowledge_candidate_gate(
    confirmed_pattern: dict[str, Any],
) -> tuple[str, list[str]]:
    """Evaluate gate for Confirmed Pattern → Knowledge Candidate."""
    if confirmed_pattern.get("contract_version") != DAY_CONFIRMED_PATTERN_V1_CONTRACT:
        return KNOWLEDGE_CANDIDATE_RESULT_REJECTED, ["invalid confirmed pattern contract_version"]

    pattern_type = confirmed_pattern.get("pattern_type")
    if pattern_type not in ALLOWED_CANDIDATE_TYPES:
        return KNOWLEDGE_CANDIDATE_RESULT_REJECTED, ["unsupported pattern type"]

    if confirmed_pattern.get("status") != PATTERN_STATUS_CONFIRMED:
        return KNOWLEDGE_CANDIDATE_RESULT_REJECTED, ["pattern status must be confirmed"]

    validation_errors = validate_day_confirmed_pattern_v1(confirmed_pattern)
    if validation_errors:
        return KNOWLEDGE_CANDIDATE_RESULT_REJECTED, validation_errors

    confidence = float(confirmed_pattern.get("confidence", 0))
    if confidence <= PROMOTION_CONFIDENCE_THRESHOLD:
        return KNOWLEDGE_CANDIDATE_RESULT_REJECTED, [
            f"confidence must be > {PROMOTION_CONFIDENCE_THRESHOLD}"
        ]

    evidence_count = int(confirmed_pattern.get("evidence_count", 0))
    if evidence_count < MIN_SIGNALS_FOR_PROMOTION:
        return KNOWLEDGE_CANDIDATE_RESULT_REJECTED, [
            f"evidence_count must be >= {MIN_SIGNALS_FOR_PROMOTION}"
        ]

    claim = build_claim_from_pattern(confirmed_pattern)
    if claim is None:
        return KNOWLEDGE_CANDIDATE_RESULT_REJECTED, ["claim cannot be expressed"]

    claim_errors = validate_claim(claim)
    if claim_errors:
        return KNOWLEDGE_CANDIDATE_RESULT_REJECTED, claim_errors

    return KNOWLEDGE_CANDIDATE_RESULT_CREATED, []


def try_build_knowledge_candidate_from_pattern_v1(
    confirmed_pattern: dict[str, Any],
    *,
    created_at: str | None = None,
    knowledge_candidate_id: str | None = None,
    requires_review: bool = True,
) -> dict[str, Any]:
    """
    P1.19 — Confirmed Pattern → Knowledge Candidate.

    Never creates active Knowledge, memory writes, profile updates, or ranking changes.
    """
    result, reasons = evaluate_knowledge_candidate_gate(confirmed_pattern)

    if result != KNOWLEDGE_CANDIDATE_RESULT_CREATED:
        return {
            "result": KNOWLEDGE_CANDIDATE_RESULT_REJECTED,
            "knowledge_candidate": None,
            "reasons": reasons,
        }

    pattern_type = confirmed_pattern["pattern_type"]
    knowledge_type = PATTERN_TYPE_TO_KNOWLEDGE_TYPE[pattern_type]
    claim = build_claim_from_pattern(confirmed_pattern)
    assert claim is not None

    confidence = float(confirmed_pattern["confidence"])
    knowledge_candidate = {
        "contract_version": DAY_KNOWLEDGE_CANDIDATE_V1_CONTRACT,
        "knowledge_candidate_id": knowledge_candidate_id or generate_knowledge_candidate_id(),
        "source_pattern_id": confirmed_pattern["pattern_id"],
        "knowledge_type": knowledge_type,
        "claim": claim,
        "claim_strength": round(min(confidence, 1.0), 2),
        "confidence": confidence,
        "evidence_pattern_id": confirmed_pattern["pattern_id"],
        "evidence_signal_ids": list(confirmed_pattern["evidence_signal_ids"]),
        "evidence_count": confirmed_pattern["evidence_count"],
        "evidence_window_days": confirmed_pattern["evidence_window_days"],
        "status": KNOWLEDGE_CANDIDATE_STATUS,
        "created_at": created_at or _utc_now_iso(),
        "requires_review": requires_review,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_update_allowed": False,
    }

    errors = validate_day_knowledge_candidate_v1(
        knowledge_candidate,
        confirmed_pattern=confirmed_pattern,
    )
    if errors:
        raise DayKnowledgeCandidateError("; ".join(errors))

    return {
        "result": KNOWLEDGE_CANDIDATE_RESULT_CREATED,
        "knowledge_candidate": knowledge_candidate,
        "reasons": [],
    }


def generate_knowledge_candidate_id() -> str:
    return f"kcand-{uuid4()}"


def validate_day_knowledge_candidate_v1(
    knowledge_candidate: dict[str, Any],
    *,
    confirmed_pattern: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if knowledge_candidate.get("contract_version") != DAY_KNOWLEDGE_CANDIDATE_V1_CONTRACT:
        errors.append("invalid contract_version")
    for key in DAY_KNOWLEDGE_CANDIDATE_V1_KEYS:
        if key not in knowledge_candidate:
            errors.append(f"missing field: {key}")

    for forbidden in FORBIDDEN_KNOWLEDGE_CANDIDATE_FIELDS:
        if forbidden in knowledge_candidate:
            errors.append(f"forbidden field: {forbidden}")

    if knowledge_candidate.get("knowledge_type") not in ALLOWED_KNOWLEDGE_TYPES:
        errors.append("invalid knowledge_type")

    if knowledge_candidate.get("status") != KNOWLEDGE_CANDIDATE_STATUS:
        errors.append("status must be candidate")

    if knowledge_candidate.get("profile_update_allowed") is not False:
        errors.append("profile_update_allowed must be false")
    if knowledge_candidate.get("memory_update_allowed") is not False:
        errors.append("memory_update_allowed must be false")
    if knowledge_candidate.get("ranking_update_allowed") is not False:
        errors.append("ranking_update_allowed must be false")

    claim = knowledge_candidate.get("claim")
    if isinstance(claim, str):
        errors.extend(validate_claim(claim))

    claim_strength = knowledge_candidate.get("claim_strength")
    if not isinstance(claim_strength, (int, float)) or claim_strength < 0 or claim_strength > 1:
        errors.append("claim_strength must be 0..1")

    confidence = knowledge_candidate.get("confidence")
    if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
        errors.append("confidence must be 0..1")

    if isinstance(confidence, (int, float)) and confidence <= PROMOTION_CONFIDENCE_THRESHOLD:
        errors.append("knowledge candidate requires confidence above threshold")

    if confirmed_pattern is not None:
        if knowledge_candidate.get("source_pattern_id") != confirmed_pattern.get("pattern_id"):
            errors.append("source_pattern_id must match pattern")
        if knowledge_candidate.get("evidence_pattern_id") != confirmed_pattern.get("pattern_id"):
            errors.append("evidence_pattern_id must match pattern")
        expected_type = PATTERN_TYPE_TO_KNOWLEDGE_TYPE.get(confirmed_pattern.get("pattern_type", ""))
        if expected_type and knowledge_candidate.get("knowledge_type") != expected_type:
            errors.append("knowledge_type mismatch for pattern type")
        if list(knowledge_candidate.get("evidence_signal_ids") or []) != list(
            confirmed_pattern.get("evidence_signal_ids") or []
        ):
            errors.append("evidence_signal_ids must match pattern")

    return errors
