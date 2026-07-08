"""P1.20 — Activate knowledge candidates into active knowledge (no Profile/Memory writes)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.day_model_v1_knowledge_candidate import (
    ALLOWED_KNOWLEDGE_TYPES,
    DAY_KNOWLEDGE_CANDIDATE_V1_CONTRACT,
    KNOWLEDGE_CANDIDATE_STATUS,
    validate_claim,
    validate_day_knowledge_candidate_v1,
)

DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT = "day_active_knowledge_v1"

ACTIVE_KNOWLEDGE_STATUS = "active"

ACTIVATION_RESULT_ACTIVATED = "activated"
ACTIVATION_RESULT_NOT_READY = "not_ready"
ACTIVATION_RESULT_REQUIRES_REVIEW = "requires_review"
ACTIVATION_RESULT_REJECTED = "rejected"

ALLOWED_ACTIVATION_RESULTS = frozenset(
    {
        ACTIVATION_RESULT_ACTIVATED,
        ACTIVATION_RESULT_NOT_READY,
        ACTIVATION_RESULT_REQUIRES_REVIEW,
        ACTIVATION_RESULT_REJECTED,
    }
)

MIN_CONFIDENCE_FOR_ACTIVATION = 0.75
MIN_EVIDENCE_COUNT_FOR_ACTIVATION = 7
MIN_EVIDENCE_DAYS_FOR_ACTIVATION = 21

FORBIDDEN_ACTIVE_KNOWLEDGE_FIELDS = frozenset(
    {
        "knowledge_atom_id",
        "ukm_atom_id",
        "profile_update",
        "profile_field",
        "memory_write",
        "recommendation",
        "recommendation_id",
        "behavior_profile_update",
        "core_profile_update",
    }
)

DAY_ACTIVE_KNOWLEDGE_V1_KEYS = frozenset(
    {
        "contract_version",
        "knowledge_id",
        "source_knowledge_candidate_id",
        "knowledge_type",
        "claim",
        "confidence",
        "evidence_count",
        "evidence_window_days",
        "evidence_signal_ids",
        "source_pattern_id",
        "status",
        "created_at",
        "last_confirmed_at",
        "expires_at",
        "review_required",
        "profile_update_allowed",
        "memory_update_allowed",
        "ranking_update_allowed",
    }
)


class DayActiveKnowledgeError(ValueError):
    """Raised when active knowledge inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def evaluate_active_knowledge_gate(
    knowledge_candidate: dict[str, Any],
    *,
    review_approved: bool = False,
) -> tuple[str, list[str]]:
    """
    Evaluate confirmation gate for Knowledge Candidate → Active Knowledge.

    promotion_eligible-style flags on candidate do not auto-activate.
    """
    if knowledge_candidate.get("contract_version") != DAY_KNOWLEDGE_CANDIDATE_V1_CONTRACT:
        return ACTIVATION_RESULT_REJECTED, ["invalid knowledge candidate contract_version"]

    if knowledge_candidate.get("status") != KNOWLEDGE_CANDIDATE_STATUS:
        return ACTIVATION_RESULT_REJECTED, ["knowledge candidate status must be candidate"]

    if knowledge_candidate.get("knowledge_type") not in ALLOWED_KNOWLEDGE_TYPES:
        return ACTIVATION_RESULT_REJECTED, ["invalid knowledge_type"]

    validation_errors = validate_day_knowledge_candidate_v1(knowledge_candidate)
    if validation_errors:
        return ACTIVATION_RESULT_REJECTED, validation_errors

    claim = knowledge_candidate.get("claim")
    if not isinstance(claim, str):
        return ACTIVATION_RESULT_REJECTED, ["claim required"]

    claim_errors = validate_claim(claim)
    if claim_errors:
        return ACTIVATION_RESULT_REJECTED, claim_errors

    if knowledge_candidate.get("requires_review") is not True:
        return ACTIVATION_RESULT_REJECTED, ["requires_review must be true on candidate"]

    confidence = float(knowledge_candidate.get("confidence", 0))
    evidence_count = int(knowledge_candidate.get("evidence_count", 0))
    evidence_window_days = int(knowledge_candidate.get("evidence_window_days", 0))

    not_ready_reasons: list[str] = []

    if confidence < MIN_CONFIDENCE_FOR_ACTIVATION:
        not_ready_reasons.append(f"confidence must be >= {MIN_CONFIDENCE_FOR_ACTIVATION}")

    if evidence_count < MIN_EVIDENCE_COUNT_FOR_ACTIVATION:
        not_ready_reasons.append(
            f"evidence_count must be >= {MIN_EVIDENCE_COUNT_FOR_ACTIVATION}"
        )

    if evidence_window_days < MIN_EVIDENCE_DAYS_FOR_ACTIVATION:
        not_ready_reasons.append(
            f"evidence_window_days must be >= {MIN_EVIDENCE_DAYS_FOR_ACTIVATION}"
        )

    if not_ready_reasons:
        return ACTIVATION_RESULT_NOT_READY, not_ready_reasons

    if not review_approved:
        return ACTIVATION_RESULT_REQUIRES_REVIEW, ["review approval required for activation"]

    return ACTIVATION_RESULT_ACTIVATED, []


def try_activate_knowledge_from_candidate_v1(
    knowledge_candidate: dict[str, Any],
    *,
    review_approved: bool = False,
    created_at: str | None = None,
    last_confirmed_at: str | None = None,
    expires_at: str | None = None,
    knowledge_id: str | None = None,
) -> dict[str, Any]:
    """
    P1.20 — Knowledge Candidate → Active Knowledge via confirmation gate.

    Active Knowledge ≠ Profile Update. No memory, ranking, or recommendation writes.
    """
    result, reasons = evaluate_active_knowledge_gate(
        knowledge_candidate,
        review_approved=review_approved,
    )

    if result != ACTIVATION_RESULT_ACTIVATED:
        return {
            "result": result,
            "active_knowledge": None,
            "reasons": reasons,
        }

    ts = created_at or _utc_now_iso()
    active = {
        "contract_version": DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
        "knowledge_id": knowledge_id or generate_active_knowledge_id(),
        "source_knowledge_candidate_id": knowledge_candidate["knowledge_candidate_id"],
        "knowledge_type": knowledge_candidate["knowledge_type"],
        "claim": knowledge_candidate["claim"],
        "confidence": knowledge_candidate["confidence"],
        "evidence_count": knowledge_candidate["evidence_count"],
        "evidence_window_days": knowledge_candidate["evidence_window_days"],
        "evidence_signal_ids": list(knowledge_candidate["evidence_signal_ids"]),
        "source_pattern_id": knowledge_candidate["source_pattern_id"],
        "status": ACTIVE_KNOWLEDGE_STATUS,
        "created_at": ts,
        "last_confirmed_at": last_confirmed_at or ts,
        "expires_at": expires_at,
        "review_required": False,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_update_allowed": False,
    }

    errors = validate_day_active_knowledge_v1(
        active,
        knowledge_candidate=knowledge_candidate,
    )
    if errors:
        raise DayActiveKnowledgeError("; ".join(errors))

    return {
        "result": ACTIVATION_RESULT_ACTIVATED,
        "active_knowledge": active,
        "reasons": [],
    }


def generate_active_knowledge_id() -> str:
    return f"know-{uuid4()}"


def validate_day_active_knowledge_v1(
    active_knowledge: dict[str, Any],
    *,
    knowledge_candidate: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if active_knowledge.get("contract_version") != DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT:
        errors.append("invalid contract_version")
    for key in DAY_ACTIVE_KNOWLEDGE_V1_KEYS:
        if key not in active_knowledge:
            errors.append(f"missing field: {key}")

    for forbidden in FORBIDDEN_ACTIVE_KNOWLEDGE_FIELDS:
        if forbidden in active_knowledge:
            errors.append(f"forbidden field: {forbidden}")

    if active_knowledge.get("knowledge_type") not in ALLOWED_KNOWLEDGE_TYPES:
        errors.append("invalid knowledge_type")

    if active_knowledge.get("status") != ACTIVE_KNOWLEDGE_STATUS:
        errors.append("status must be active")

    if active_knowledge.get("profile_update_allowed") is not False:
        errors.append("profile_update_allowed must be false")
    if active_knowledge.get("memory_update_allowed") is not False:
        errors.append("memory_update_allowed must be false")
    if active_knowledge.get("ranking_update_allowed") is not False:
        errors.append("ranking_update_allowed must be false")

    claim = active_knowledge.get("claim")
    if isinstance(claim, str):
        errors.extend(validate_claim(claim))

    confidence = active_knowledge.get("confidence")
    if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
        errors.append("confidence must be 0..1")
    elif confidence < MIN_CONFIDENCE_FOR_ACTIVATION:
        errors.append(f"confidence must be >= {MIN_CONFIDENCE_FOR_ACTIVATION}")

    evidence_count = active_knowledge.get("evidence_count")
    if not isinstance(evidence_count, int) or evidence_count < MIN_EVIDENCE_COUNT_FOR_ACTIVATION:
        errors.append(f"evidence_count must be >= {MIN_EVIDENCE_COUNT_FOR_ACTIVATION}")

    window_days = active_knowledge.get("evidence_window_days")
    if not isinstance(window_days, int) or window_days < MIN_EVIDENCE_DAYS_FOR_ACTIVATION:
        errors.append(f"evidence_window_days must be >= {MIN_EVIDENCE_DAYS_FOR_ACTIVATION}")

    last_confirmed = active_knowledge.get("last_confirmed_at")
    if not isinstance(last_confirmed, str) or not last_confirmed.strip():
        errors.append("last_confirmed_at required")

    if knowledge_candidate is not None:
        if active_knowledge.get("source_knowledge_candidate_id") != knowledge_candidate.get(
            "knowledge_candidate_id"
        ):
            errors.append("source_knowledge_candidate_id must match candidate")
        if active_knowledge.get("source_pattern_id") != knowledge_candidate.get("source_pattern_id"):
            errors.append("source_pattern_id must match candidate")
        if active_knowledge.get("knowledge_type") != knowledge_candidate.get("knowledge_type"):
            errors.append("knowledge_type must match candidate")
        if active_knowledge.get("claim") != knowledge_candidate.get("claim"):
            errors.append("claim must match candidate")
        if list(active_knowledge.get("evidence_signal_ids") or []) != list(
            knowledge_candidate.get("evidence_signal_ids") or []
        ):
            errors.append("evidence_signal_ids must match candidate")

    return errors
