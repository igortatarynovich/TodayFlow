"""P1.21 — Usage policy for active knowledge (hints only, no application)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.day_model_v1_active_knowledge import (
    ACTIVE_KNOWLEDGE_STATUS,
    DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
    validate_day_active_knowledge_v1,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import (
    ALLOWED_KNOWLEDGE_TYPES,
    CLAIM_PREFIX_RISK,
    KNOWLEDGE_TYPE_BEHAVIOR,
    KNOWLEDGE_TYPE_CONTENT_AFFINITY,
    KNOWLEDGE_TYPE_PREFERENCE,
    KNOWLEDGE_TYPE_RESPONSE_STYLE,
    KNOWLEDGE_TYPE_TIMING,
    validate_claim,
)

DAY_ACTIVE_KNOWLEDGE_USAGE_POLICY_V1_CONTRACT = "day_active_knowledge_usage_policy_v1"

USAGE_CONTEXT_SELECTION = "context_selection_hint"
USAGE_PROMPT_REFINEMENT = "prompt_refinement_hint"
USAGE_CONTENT_RANKING = "content_ranking_hint"
USAGE_SURFACE_PRIORITY = "surface_priority_hint"
USAGE_CACHE_REUSE = "cache_reuse_hint"

ALLOWED_USAGE_TYPES = frozenset(
    {
        USAGE_CONTEXT_SELECTION,
        USAGE_PROMPT_REFINEMENT,
        USAGE_CONTENT_RANKING,
        USAGE_SURFACE_PRIORITY,
        USAGE_CACHE_REUSE,
    }
)

FORBIDDEN_USAGE_TYPES = frozenset(
    {
        "profile_update",
        "memory_write",
        "core_profile_mutation",
        "behavior_profile_mutation",
        "automatic_recommendation",
        "sensitive_inference",
        "psychological_trait_assignment",
        "medical_financial_claim",
        "commerce_targeting_without_gate",
    }
)

INFLUENCE_LOW = "low"
INFLUENCE_MEDIUM = "medium"
INFLUENCE_HIGH = "high"

ALLOWED_INFLUENCE_LEVELS = frozenset({INFLUENCE_LOW, INFLUENCE_MEDIUM})

KNOWLEDGE_TYPE_ALLOWED_USAGES: dict[str, list[str]] = {
    KNOWLEDGE_TYPE_CONTENT_AFFINITY: [
        USAGE_CONTEXT_SELECTION,
        USAGE_CONTENT_RANKING,
        USAGE_CACHE_REUSE,
    ],
    KNOWLEDGE_TYPE_RESPONSE_STYLE: [
        USAGE_CONTEXT_SELECTION,
        USAGE_PROMPT_REFINEMENT,
        USAGE_SURFACE_PRIORITY,
        USAGE_CACHE_REUSE,
    ],
    KNOWLEDGE_TYPE_BEHAVIOR: [
        USAGE_CONTEXT_SELECTION,
        USAGE_PROMPT_REFINEMENT,
        USAGE_CACHE_REUSE,
    ],
    KNOWLEDGE_TYPE_TIMING: [
        USAGE_CONTEXT_SELECTION,
        USAGE_SURFACE_PRIORITY,
        USAGE_CACHE_REUSE,
    ],
    KNOWLEDGE_TYPE_PREFERENCE: [
        USAGE_CONTEXT_SELECTION,
        USAGE_CONTENT_RANKING,
    ],
}

DEFAULT_MAX_INFLUENCE_BY_TYPE: dict[str, str] = {
    KNOWLEDGE_TYPE_CONTENT_AFFINITY: INFLUENCE_MEDIUM,
    KNOWLEDGE_TYPE_RESPONSE_STYLE: INFLUENCE_MEDIUM,
    KNOWLEDGE_TYPE_BEHAVIOR: INFLUENCE_MEDIUM,
    KNOWLEDGE_TYPE_TIMING: INFLUENCE_MEDIUM,
    KNOWLEDGE_TYPE_PREFERENCE: INFLUENCE_MEDIUM,
}

POLICY_RESULT_CREATED = "created"
POLICY_RESULT_REJECTED = "rejected"

DAY_ACTIVE_KNOWLEDGE_USAGE_POLICY_V1_KEYS = frozenset(
    {
        "contract_version",
        "usage_policy_id",
        "knowledge_id",
        "claim",
        "knowledge_type",
        "allowed_usages",
        "forbidden_usages",
        "max_influence_level",
        "requires_runtime_gate",
        "profile_update_allowed",
        "memory_update_allowed",
        "ranking_update_allowed",
        "created_at",
    }
)


class DayActiveKnowledgeUsagePolicyError(ValueError):
    """Raised when usage policy inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def resolve_max_influence_level(
    knowledge_type: str,
    claim: str,
) -> str:
    """Resolve max influence; risk claims capped at low."""
    if claim.startswith(f"{CLAIM_PREFIX_RISK}:"):
        return INFLUENCE_LOW
    if knowledge_type == KNOWLEDGE_TYPE_BEHAVIOR:
        return INFLUENCE_MEDIUM
    return DEFAULT_MAX_INFLUENCE_BY_TYPE.get(knowledge_type, INFLUENCE_MEDIUM)


def resolve_allowed_usages(knowledge_type: str) -> list[str]:
    usages = KNOWLEDGE_TYPE_ALLOWED_USAGES.get(knowledge_type)
    if usages is None:
        return []
    return list(usages)


def build_active_knowledge_usage_policy_v1(
    active_knowledge: dict[str, Any],
    *,
    created_at: str | None = None,
    usage_policy_id: str | None = None,
) -> dict[str, Any]:
    """
    P1.21 — define allowed/forbidden usages for active knowledge.

    Policy describes hints only; does not apply knowledge or mutate profile/memory.
    """
    outcome = try_build_active_knowledge_usage_policy_v1(
        active_knowledge,
        created_at=created_at,
        usage_policy_id=usage_policy_id,
    )
    if outcome["result"] != POLICY_RESULT_CREATED:
        raise DayActiveKnowledgeUsagePolicyError("; ".join(outcome["reasons"]))
    return outcome["usage_policy"]


def try_build_active_knowledge_usage_policy_v1(
    active_knowledge: dict[str, Any],
    *,
    created_at: str | None = None,
    usage_policy_id: str | None = None,
) -> dict[str, Any]:
    if active_knowledge.get("contract_version") != DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT:
        return {
            "result": POLICY_RESULT_REJECTED,
            "usage_policy": None,
            "reasons": ["invalid active knowledge contract_version"],
        }

    if active_knowledge.get("status") != ACTIVE_KNOWLEDGE_STATUS:
        return {
            "result": POLICY_RESULT_REJECTED,
            "usage_policy": None,
            "reasons": ["active knowledge status must be active"],
        }

    validation_errors = validate_day_active_knowledge_v1(active_knowledge)
    if validation_errors:
        return {
            "result": POLICY_RESULT_REJECTED,
            "usage_policy": None,
            "reasons": validation_errors,
        }

    knowledge_type = active_knowledge.get("knowledge_type")
    claim = active_knowledge.get("claim")

    if knowledge_type not in ALLOWED_KNOWLEDGE_TYPES:
        return {
            "result": POLICY_RESULT_REJECTED,
            "usage_policy": None,
            "reasons": ["invalid knowledge_type"],
        }

    if not isinstance(claim, str):
        return {
            "result": POLICY_RESULT_REJECTED,
            "usage_policy": None,
            "reasons": ["claim required"],
        }

    claim_errors = validate_claim(claim)
    if claim_errors:
        return {
            "result": POLICY_RESULT_REJECTED,
            "usage_policy": None,
            "reasons": claim_errors,
        }

    allowed = resolve_allowed_usages(knowledge_type)
    if not allowed:
        return {
            "result": POLICY_RESULT_REJECTED,
            "usage_policy": None,
            "reasons": ["no allowed usages for knowledge_type"],
        }

    max_influence = resolve_max_influence_level(knowledge_type, claim)
    if max_influence not in ALLOWED_INFLUENCE_LEVELS:
        return {
            "result": POLICY_RESULT_REJECTED,
            "usage_policy": None,
            "reasons": ["high influence not allowed in P1.21"],
        }

    policy = {
        "contract_version": DAY_ACTIVE_KNOWLEDGE_USAGE_POLICY_V1_CONTRACT,
        "usage_policy_id": usage_policy_id or generate_usage_policy_id(),
        "knowledge_id": active_knowledge["knowledge_id"],
        "claim": claim,
        "knowledge_type": knowledge_type,
        "allowed_usages": allowed,
        "forbidden_usages": sorted(FORBIDDEN_USAGE_TYPES),
        "max_influence_level": max_influence,
        "requires_runtime_gate": True,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_update_allowed": False,
        "created_at": created_at or _utc_now_iso(),
    }

    errors = validate_day_active_knowledge_usage_policy_v1(
        policy,
        active_knowledge=active_knowledge,
    )
    if errors:
        raise DayActiveKnowledgeUsagePolicyError("; ".join(errors))

    return {
        "result": POLICY_RESULT_CREATED,
        "usage_policy": policy,
        "reasons": [],
    }


def generate_usage_policy_id() -> str:
    return f"kuse-{uuid4()}"


def validate_day_active_knowledge_usage_policy_v1(
    policy: dict[str, Any],
    *,
    active_knowledge: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if policy.get("contract_version") != DAY_ACTIVE_KNOWLEDGE_USAGE_POLICY_V1_CONTRACT:
        errors.append("invalid contract_version")
    for key in DAY_ACTIVE_KNOWLEDGE_USAGE_POLICY_V1_KEYS:
        if key not in policy:
            errors.append(f"missing field: {key}")

    knowledge_type = policy.get("knowledge_type")
    if knowledge_type not in ALLOWED_KNOWLEDGE_TYPES:
        errors.append("invalid knowledge_type")

    max_influence = policy.get("max_influence_level")
    if max_influence == INFLUENCE_HIGH:
        errors.append("high influence not allowed")
    elif max_influence not in ALLOWED_INFLUENCE_LEVELS:
        errors.append("invalid max_influence_level")

    if policy.get("requires_runtime_gate") is not True:
        errors.append("requires_runtime_gate must be true")

    if policy.get("profile_update_allowed") is not False:
        errors.append("profile_update_allowed must be false")
    if policy.get("memory_update_allowed") is not False:
        errors.append("memory_update_allowed must be false")
    if policy.get("ranking_update_allowed") is not False:
        errors.append("ranking_update_allowed must be false")

    allowed = policy.get("allowed_usages")
    if not isinstance(allowed, list) or not allowed:
        errors.append("allowed_usages must be non-empty list")
    elif isinstance(allowed, list):
        for usage in allowed:
            if usage not in ALLOWED_USAGE_TYPES:
                errors.append(f"invalid allowed usage: {usage}")

    forbidden = policy.get("forbidden_usages")
    if not isinstance(forbidden, list):
        errors.append("forbidden_usages must be list")
    elif isinstance(forbidden, list):
        forbidden_set = set(forbidden)
        if not FORBIDDEN_USAGE_TYPES.issubset(forbidden_set):
            errors.append("forbidden_usages must include all standard forbidden usages")

    claim = policy.get("claim")
    if isinstance(claim, str):
        errors.extend(validate_claim(claim))

    if active_knowledge is not None and knowledge_type:
        expected_allowed = resolve_allowed_usages(knowledge_type)
        if list(policy.get("allowed_usages") or []) != expected_allowed:
            errors.append("allowed_usages mismatch for knowledge_type")
        if policy.get("knowledge_id") != active_knowledge.get("knowledge_id"):
            errors.append("knowledge_id must match active knowledge")
        if policy.get("claim") != active_knowledge.get("claim"):
            errors.append("claim must match active knowledge")
        expected_influence = resolve_max_influence_level(
            knowledge_type,
            str(active_knowledge.get("claim", "")),
        )
        if policy.get("max_influence_level") != expected_influence:
            errors.append("max_influence_level mismatch")

    return errors
