"""P1.22 — Runtime gate for active knowledge usage (permission only, no hint application)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.day_model_v1_active_knowledge import (
    ACTIVE_KNOWLEDGE_STATUS,
    DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_active_knowledge_usage_policy import (
    DAY_ACTIVE_KNOWLEDGE_USAGE_POLICY_V1_CONTRACT,
    FORBIDDEN_USAGE_TYPES,
    INFLUENCE_LOW,
    INFLUENCE_MEDIUM,
    ALLOWED_USAGE_TYPES,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import validate_claim

DAY_ACTIVE_KNOWLEDGE_RUNTIME_DECISION_V1_CONTRACT = (
    "day_active_knowledge_runtime_decision_v1"
)

DECISION_ALLOW = "allow"
DECISION_DENY = "deny"

INFLUENCE_NONE = "none"

DENY_KNOWLEDGE_NOT_ACTIVE = "knowledge_not_active"
DENY_POLICY_MISSING_RUNTIME_GATE = "policy_missing_runtime_gate"
DENY_USAGE_NOT_ALLOWED = "usage_not_allowed"
DENY_USAGE_FORBIDDEN = "usage_forbidden"
DENY_INFLUENCE_TOO_HIGH = "influence_too_high"
DENY_INVALID_CLAIM = "invalid_claim"
DENY_SENSITIVE_CLAIM = "sensitive_claim"
DENY_SURFACE_NOT_COMPATIBLE = "surface_not_compatible"
DENY_EXPIRED_KNOWLEDGE = "expired_knowledge"

INFLUENCE_RANK = {
    INFLUENCE_NONE: 0,
    INFLUENCE_LOW: 1,
    INFLUENCE_MEDIUM: 2,
    "high": 3,
}

SURFACE_COMPATIBLE_USAGES: dict[str, frozenset[str]] = {
    "day_guidance_card": frozenset(
        {"context_selection_hint", "prompt_refinement_hint"}
    ),
    "reflection_card": frozenset({"prompt_refinement_hint"}),
    "today_hero": frozenset({"surface_priority_hint"}),
    "action_card": frozenset({"context_selection_hint"}),
    "cache_layer": frozenset({"cache_reuse_hint"}),
    "content_ranker": frozenset({"content_ranking_hint"}),
}

DAY_ACTIVE_KNOWLEDGE_RUNTIME_DECISION_V1_KEYS = frozenset(
    {
        "contract_version",
        "runtime_decision_id",
        "knowledge_id",
        "usage_policy_id",
        "surface",
        "requested_usage",
        "decision",
        "reason",
        "allowed_influence_level",
        "claim",
        "traceability",
        "created_at",
        "profile_update_allowed",
        "memory_update_allowed",
        "ranking_update_allowed",
    }
)


class DayActiveKnowledgeRuntimeGateError(ValueError):
    """Raised when runtime decision inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _is_knowledge_expired(
    active_knowledge: dict[str, Any],
    *,
    now: datetime | None = None,
) -> bool:
    expires_at = active_knowledge.get("expires_at")
    if not expires_at:
        return False
    if not isinstance(expires_at, str):
        return True
    current = now or datetime.now(UTC)
    return _parse_iso(expires_at) <= current


def _resolve_allowed_influence(
    requested: str,
    max_level: str,
) -> str:
    requested_rank = INFLUENCE_RANK.get(requested, -1)
    max_rank = INFLUENCE_RANK.get(max_level, -1)
    if requested_rank <= 0:
        return INFLUENCE_NONE
    if requested_rank <= max_rank:
        return requested
    return INFLUENCE_NONE


def _surface_supports_usage(surface: str, requested_usage: str) -> bool:
    compatible = SURFACE_COMPATIBLE_USAGES.get(surface)
    if compatible is None:
        return False
    return requested_usage in compatible


def evaluate_active_knowledge_runtime_gate(
    active_knowledge: dict[str, Any],
    usage_policy: dict[str, Any],
    *,
    surface: str,
    requested_usage: str,
    requested_influence: str = INFLUENCE_MEDIUM,
    now: datetime | None = None,
) -> tuple[str, str]:
    """
    Evaluate runtime gate. Returns (decision, reason).
    reason is machine-readable; empty when allow.
    """
    if active_knowledge.get("contract_version") != DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT:
        return DECISION_DENY, DENY_KNOWLEDGE_NOT_ACTIVE

    if active_knowledge.get("status") != ACTIVE_KNOWLEDGE_STATUS:
        return DECISION_DENY, DENY_KNOWLEDGE_NOT_ACTIVE

    if _is_knowledge_expired(active_knowledge, now=now):
        return DECISION_DENY, DENY_EXPIRED_KNOWLEDGE

    if usage_policy.get("contract_version") != DAY_ACTIVE_KNOWLEDGE_USAGE_POLICY_V1_CONTRACT:
        return DECISION_DENY, DENY_POLICY_MISSING_RUNTIME_GATE

    if usage_policy.get("requires_runtime_gate") is not True:
        return DECISION_DENY, DENY_POLICY_MISSING_RUNTIME_GATE

    if usage_policy.get("knowledge_id") != active_knowledge.get("knowledge_id"):
        return DECISION_DENY, DENY_POLICY_MISSING_RUNTIME_GATE

    claim = active_knowledge.get("claim")
    if not isinstance(claim, str):
        return DECISION_DENY, DENY_INVALID_CLAIM

    claim_errors = validate_claim(claim)
    if claim_errors:
        if any("sensitive" in e or "trait" in e for e in claim_errors):
            return DECISION_DENY, DENY_SENSITIVE_CLAIM
        return DECISION_DENY, DENY_INVALID_CLAIM

    if requested_usage not in ALLOWED_USAGE_TYPES:
        return DECISION_DENY, DENY_USAGE_NOT_ALLOWED

    allowed_usages = usage_policy.get("allowed_usages") or []
    if requested_usage not in allowed_usages:
        return DECISION_DENY, DENY_USAGE_NOT_ALLOWED

    forbidden_usages = usage_policy.get("forbidden_usages") or []
    if requested_usage in forbidden_usages or requested_usage in FORBIDDEN_USAGE_TYPES:
        return DECISION_DENY, DENY_USAGE_FORBIDDEN

    max_influence = usage_policy.get("max_influence_level", INFLUENCE_MEDIUM)
    requested_rank = INFLUENCE_RANK.get(requested_influence, -1)
    max_rank = INFLUENCE_RANK.get(max_influence, -1)
    if requested_rank < 0 or requested_rank > max_rank:
        return DECISION_DENY, DENY_INFLUENCE_TOO_HIGH

    if not _surface_supports_usage(surface, requested_usage):
        return DECISION_DENY, DENY_SURFACE_NOT_COMPATIBLE

    return DECISION_ALLOW, ""


def try_decide_active_knowledge_runtime_v1(
    active_knowledge: dict[str, Any],
    usage_policy: dict[str, Any],
    *,
    surface: str,
    requested_usage: str,
    requested_influence: str = INFLUENCE_MEDIUM,
    now: datetime | None = None,
    created_at: str | None = None,
    runtime_decision_id: str | None = None,
) -> dict[str, Any]:
    """
    P1.22 — decide whether active knowledge may be used as a hint in runtime context.

    Permission only — does not apply hints or mutate profile/memory/ranking.
    """
    decision, reason = evaluate_active_knowledge_runtime_gate(
        active_knowledge,
        usage_policy,
        surface=surface,
        requested_usage=requested_usage,
        requested_influence=requested_influence,
        now=now,
    )

    claim = active_knowledge.get("claim", "")
    max_influence = usage_policy.get("max_influence_level", INFLUENCE_MEDIUM)
    if decision == DECISION_ALLOW:
        allowed_influence = _resolve_allowed_influence(requested_influence, str(max_influence))
    else:
        allowed_influence = INFLUENCE_NONE

    runtime_decision = {
        "contract_version": DAY_ACTIVE_KNOWLEDGE_RUNTIME_DECISION_V1_CONTRACT,
        "runtime_decision_id": runtime_decision_id or generate_runtime_decision_id(),
        "knowledge_id": active_knowledge.get("knowledge_id"),
        "usage_policy_id": usage_policy.get("usage_policy_id"),
        "surface": surface,
        "requested_usage": requested_usage,
        "decision": decision,
        "reason": reason or "allowed",
        "allowed_influence_level": allowed_influence,
        "claim": claim,
        "traceability": {
            "knowledge_id": active_knowledge.get("knowledge_id"),
            "usage_policy_id": usage_policy.get("usage_policy_id"),
            "source_pattern_id": active_knowledge.get("source_pattern_id"),
        },
        "created_at": created_at or _utc_now_iso(),
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_update_allowed": False,
    }

    errors = validate_day_active_knowledge_runtime_decision_v1(
        runtime_decision,
        active_knowledge=active_knowledge,
        usage_policy=usage_policy,
    )
    if errors:
        raise DayActiveKnowledgeRuntimeGateError("; ".join(errors))

    return runtime_decision


def generate_runtime_decision_id() -> str:
    return f"krt-{uuid4()}"


def validate_day_active_knowledge_runtime_decision_v1(
    runtime_decision: dict[str, Any],
    *,
    active_knowledge: dict[str, Any] | None = None,
    usage_policy: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if runtime_decision.get("contract_version") != DAY_ACTIVE_KNOWLEDGE_RUNTIME_DECISION_V1_CONTRACT:
        errors.append("invalid contract_version")
    for key in DAY_ACTIVE_KNOWLEDGE_RUNTIME_DECISION_V1_KEYS:
        if key not in runtime_decision:
            errors.append(f"missing field: {key}")

    decision = runtime_decision.get("decision")
    if decision not in {DECISION_ALLOW, DECISION_DENY}:
        errors.append("invalid decision")

    if runtime_decision.get("profile_update_allowed") is not False:
        errors.append("profile_update_allowed must be false")
    if runtime_decision.get("memory_update_allowed") is not False:
        errors.append("memory_update_allowed must be false")
    if runtime_decision.get("ranking_update_allowed") is not False:
        errors.append("ranking_update_allowed must be false")

    allowed_influence = runtime_decision.get("allowed_influence_level")
    if allowed_influence not in {INFLUENCE_NONE, INFLUENCE_LOW, INFLUENCE_MEDIUM}:
        errors.append("invalid allowed_influence_level")

    if decision == DECISION_DENY and allowed_influence != INFLUENCE_NONE:
        errors.append("deny decision requires allowed_influence_level=none")

    trace = runtime_decision.get("traceability")
    if not isinstance(trace, dict):
        errors.append("traceability must be object")
    elif trace.get("knowledge_id") != runtime_decision.get("knowledge_id"):
        errors.append("traceability knowledge_id mismatch")

    if active_knowledge is not None and usage_policy is not None:
        if runtime_decision.get("knowledge_id") != active_knowledge.get("knowledge_id"):
            errors.append("knowledge_id must match active knowledge")
        if runtime_decision.get("usage_policy_id") != usage_policy.get("usage_policy_id"):
            errors.append("usage_policy_id must match policy")

    return errors
