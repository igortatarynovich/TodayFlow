"""P1.23 — Package allowed active knowledge hints (no application)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.day_model_v1_active_knowledge import (
    DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_active_knowledge_runtime_gate import (
    DAY_ACTIVE_KNOWLEDGE_RUNTIME_DECISION_V1_CONTRACT,
    DECISION_ALLOW,
    INFLUENCE_LOW,
    INFLUENCE_MEDIUM,
    INFLUENCE_NONE,
)
from todayflow_backend.services.day_model_v1_active_knowledge_usage_policy import (
    DAY_ACTIVE_KNOWLEDGE_USAGE_POLICY_V1_CONTRACT,
    USAGE_CACHE_REUSE,
    USAGE_CONTENT_RANKING,
    USAGE_CONTEXT_SELECTION,
    USAGE_PROMPT_REFINEMENT,
    USAGE_SURFACE_PRIORITY,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import (
    ALLOWED_KNOWLEDGE_TYPES,
    validate_claim,
)

DAY_ACTIVE_KNOWLEDGE_HINT_PACKAGE_V1_CONTRACT = "day_active_knowledge_hint_package_v1"

HINT_PACKAGE_STATUS_READY = "ready"

HINT_TYPE_CONTEXT = "context"
HINT_TYPE_PROMPT = "prompt"
HINT_TYPE_CACHE = "cache"
HINT_TYPE_RANKING = "ranking"
HINT_TYPE_SURFACE_PRIORITY = "surface_priority"

ALLOWED_HINT_TYPES = frozenset(
    {
        HINT_TYPE_CONTEXT,
        HINT_TYPE_PROMPT,
        HINT_TYPE_CACHE,
        HINT_TYPE_RANKING,
        HINT_TYPE_SURFACE_PRIORITY,
    }
)

REQUESTED_USAGE_TO_HINT_TYPE: dict[str, str] = {
    USAGE_CONTEXT_SELECTION: HINT_TYPE_CONTEXT,
    USAGE_PROMPT_REFINEMENT: HINT_TYPE_PROMPT,
    USAGE_CACHE_REUSE: HINT_TYPE_CACHE,
    USAGE_CONTENT_RANKING: HINT_TYPE_RANKING,
    USAGE_SURFACE_PRIORITY: HINT_TYPE_SURFACE_PRIORITY,
}

ALLOWED_OPERATIONS_BY_HINT_TYPE: dict[str, list[str]] = {
    HINT_TYPE_CONTEXT: ["include", "prioritize", "suppress_low_relevance"],
    HINT_TYPE_PROMPT: ["adjust_tone", "adjust_length", "reduce_repetition"],
    HINT_TYPE_CACHE: ["increase_reuse_score", "allow_similarity_match"],
    HINT_TYPE_RANKING: ["boost_related_content", "lower_unrelated_content"],
    HINT_TYPE_SURFACE_PRIORITY: ["boost_surface", "delay_surface"],
}

FORBIDDEN_OPERATIONS = frozenset(
    {
        "mutate_profile",
        "write_memory",
        "approve_dataset",
        "create_recommendation",
        "infer_sensitive_trait",
        "assign_psychological_trait",
        "override_daymodel",
        "change_strategy",
        "change_risk",
        "change_tempo",
        "change_content_keys",
        "call_llm_directly",
    }
)

HINT_PACKAGE_RESULT_CREATED = "created"
HINT_PACKAGE_RESULT_REJECTED = "rejected"

DAY_ACTIVE_KNOWLEDGE_HINT_PACKAGE_V1_KEYS = frozenset(
    {
        "contract_version",
        "hint_package_id",
        "knowledge_id",
        "usage_policy_id",
        "runtime_decision_id",
        "surface",
        "requested_usage",
        "claim",
        "knowledge_type",
        "hint_type",
        "influence_level",
        "confidence",
        "allowed_operations",
        "forbidden_operations",
        "traceability",
        "status",
        "created_at",
        "applied",
    }
)


class DayActiveKnowledgeHintPackageError(ValueError):
    """Raised when hint package inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def map_requested_usage_to_hint_type(requested_usage: str) -> str | None:
    return REQUESTED_USAGE_TO_HINT_TYPE.get(requested_usage)


def try_build_active_knowledge_hint_package_v1(
    active_knowledge: dict[str, Any],
    usage_policy: dict[str, Any],
    runtime_decision: dict[str, Any],
    *,
    created_at: str | None = None,
    hint_package_id: str | None = None,
) -> dict[str, Any]:
    """
    P1.23 — package an allowed runtime hint for downstream consumers.

    Runtime allow ≠ hint applied. applied=false always on creation.
    """
    if runtime_decision.get("contract_version") != DAY_ACTIVE_KNOWLEDGE_RUNTIME_DECISION_V1_CONTRACT:
        return {
            "result": HINT_PACKAGE_RESULT_REJECTED,
            "hint_package": None,
            "reasons": ["invalid runtime decision contract_version"],
        }

    if runtime_decision.get("decision") != DECISION_ALLOW:
        return {
            "result": HINT_PACKAGE_RESULT_REJECTED,
            "hint_package": None,
            "reasons": ["runtime decision must be allow"],
        }

    if active_knowledge.get("contract_version") != DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT:
        return {
            "result": HINT_PACKAGE_RESULT_REJECTED,
            "hint_package": None,
            "reasons": ["invalid active knowledge contract_version"],
        }

    if usage_policy.get("contract_version") != DAY_ACTIVE_KNOWLEDGE_USAGE_POLICY_V1_CONTRACT:
        return {
            "result": HINT_PACKAGE_RESULT_REJECTED,
            "hint_package": None,
            "reasons": ["invalid usage policy contract_version"],
        }

    if runtime_decision.get("knowledge_id") != active_knowledge.get("knowledge_id"):
        return {
            "result": HINT_PACKAGE_RESULT_REJECTED,
            "hint_package": None,
            "reasons": ["runtime decision knowledge_id mismatch"],
        }

    if runtime_decision.get("usage_policy_id") != usage_policy.get("usage_policy_id"):
        return {
            "result": HINT_PACKAGE_RESULT_REJECTED,
            "hint_package": None,
            "reasons": ["runtime decision usage_policy_id mismatch"],
        }

    claim = active_knowledge.get("claim")
    if not isinstance(claim, str):
        return {
            "result": HINT_PACKAGE_RESULT_REJECTED,
            "hint_package": None,
            "reasons": ["claim required"],
        }

    claim_errors = validate_claim(claim)
    if claim_errors:
        return {
            "result": HINT_PACKAGE_RESULT_REJECTED,
            "hint_package": None,
            "reasons": claim_errors,
        }

    requested_usage = runtime_decision.get("requested_usage")
    hint_type = map_requested_usage_to_hint_type(str(requested_usage or ""))
    if hint_type is None:
        return {
            "result": HINT_PACKAGE_RESULT_REJECTED,
            "hint_package": None,
            "reasons": ["unsupported requested_usage for hint_type"],
        }

    influence_level = runtime_decision.get("allowed_influence_level")
    if influence_level not in {INFLUENCE_LOW, INFLUENCE_MEDIUM}:
        return {
            "result": HINT_PACKAGE_RESULT_REJECTED,
            "hint_package": None,
            "reasons": ["influence_level must be low or medium"],
        }

    knowledge_type = active_knowledge.get("knowledge_type")
    if knowledge_type not in ALLOWED_KNOWLEDGE_TYPES:
        return {
            "result": HINT_PACKAGE_RESULT_REJECTED,
            "hint_package": None,
            "reasons": ["invalid knowledge_type"],
        }

    confidence = active_knowledge.get("confidence")
    if not isinstance(confidence, (int, float)):
        return {
            "result": HINT_PACKAGE_RESULT_REJECTED,
            "hint_package": None,
            "reasons": ["confidence required"],
        }

    allowed_ops = list(ALLOWED_OPERATIONS_BY_HINT_TYPE[hint_type])

    hint_package = {
        "contract_version": DAY_ACTIVE_KNOWLEDGE_HINT_PACKAGE_V1_CONTRACT,
        "hint_package_id": hint_package_id or generate_hint_package_id(),
        "knowledge_id": active_knowledge["knowledge_id"],
        "usage_policy_id": usage_policy["usage_policy_id"],
        "runtime_decision_id": runtime_decision["runtime_decision_id"],
        "surface": runtime_decision["surface"],
        "requested_usage": requested_usage,
        "claim": claim,
        "knowledge_type": knowledge_type,
        "hint_type": hint_type,
        "influence_level": influence_level,
        "confidence": confidence,
        "allowed_operations": allowed_ops,
        "forbidden_operations": sorted(FORBIDDEN_OPERATIONS),
        "traceability": {
            "knowledge_id": active_knowledge["knowledge_id"],
            "usage_policy_id": usage_policy["usage_policy_id"],
            "runtime_decision_id": runtime_decision["runtime_decision_id"],
            "source_pattern_id": active_knowledge.get("source_pattern_id"),
            "source_knowledge_candidate_id": active_knowledge.get(
                "source_knowledge_candidate_id"
            ),
            "evidence_signal_ids": list(active_knowledge.get("evidence_signal_ids") or []),
            "evidence_count": active_knowledge.get("evidence_count"),
            "evidence_window_days": active_knowledge.get("evidence_window_days"),
        },
        "status": HINT_PACKAGE_STATUS_READY,
        "created_at": created_at or _utc_now_iso(),
        "applied": False,
    }

    errors = validate_day_active_knowledge_hint_package_v1(
        hint_package,
        active_knowledge=active_knowledge,
        usage_policy=usage_policy,
        runtime_decision=runtime_decision,
    )
    if errors:
        raise DayActiveKnowledgeHintPackageError("; ".join(errors))

    return {
        "result": HINT_PACKAGE_RESULT_CREATED,
        "hint_package": hint_package,
        "reasons": [],
    }


def generate_hint_package_id() -> str:
    return f"hpkg-{uuid4()}"


def validate_day_active_knowledge_hint_package_v1(
    hint_package: dict[str, Any],
    *,
    active_knowledge: dict[str, Any] | None = None,
    usage_policy: dict[str, Any] | None = None,
    runtime_decision: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if hint_package.get("contract_version") != DAY_ACTIVE_KNOWLEDGE_HINT_PACKAGE_V1_CONTRACT:
        errors.append("invalid contract_version")
    for key in DAY_ACTIVE_KNOWLEDGE_HINT_PACKAGE_V1_KEYS:
        if key not in hint_package:
            errors.append(f"missing field: {key}")

    if hint_package.get("status") != HINT_PACKAGE_STATUS_READY:
        errors.append("status must be ready")

    if hint_package.get("applied") is not False:
        errors.append("applied must be false")

    hint_type = hint_package.get("hint_type")
    if hint_type not in ALLOWED_HINT_TYPES:
        errors.append("invalid hint_type")

    influence = hint_package.get("influence_level")
    if influence not in {INFLUENCE_LOW, INFLUENCE_MEDIUM}:
        errors.append("influence_level must be low or medium")

    claim = hint_package.get("claim")
    if isinstance(claim, str):
        errors.extend(validate_claim(claim))

    forbidden = hint_package.get("forbidden_operations")
    if not isinstance(forbidden, list):
        errors.append("forbidden_operations must be list")
    elif isinstance(forbidden, list):
        if not FORBIDDEN_OPERATIONS.issubset(set(forbidden)):
            errors.append("forbidden_operations must include all standard forbidden ops")

    allowed = hint_package.get("allowed_operations")
    if hint_type and isinstance(allowed, list):
        expected = ALLOWED_OPERATIONS_BY_HINT_TYPE.get(hint_type, [])
        if allowed != expected:
            errors.append("allowed_operations mismatch for hint_type")

    requested = hint_package.get("requested_usage")
    if isinstance(requested, str):
        expected_hint = map_requested_usage_to_hint_type(requested)
        if expected_hint and hint_type != expected_hint:
            errors.append("hint_type mismatch for requested_usage")

    if runtime_decision is not None:
        if hint_package.get("runtime_decision_id") != runtime_decision.get(
            "runtime_decision_id"
        ):
            errors.append("runtime_decision_id must match decision")
        if runtime_decision.get("decision") != DECISION_ALLOW:
            errors.append("hint package requires allow runtime decision")
        runtime_influence = runtime_decision.get("allowed_influence_level")
        if runtime_influence == INFLUENCE_NONE:
            errors.append("runtime decision must grant influence")
        elif influence and runtime_influence in {INFLUENCE_LOW, INFLUENCE_MEDIUM}:
            if influence != runtime_influence:
                errors.append("influence_level must match runtime decision")

    if active_knowledge is not None:
        if hint_package.get("knowledge_id") != active_knowledge.get("knowledge_id"):
            errors.append("knowledge_id must match active knowledge")
        if hint_package.get("claim") != active_knowledge.get("claim"):
            errors.append("claim must match active knowledge")
        if hint_package.get("knowledge_type") != active_knowledge.get("knowledge_type"):
            errors.append("knowledge_type must match active knowledge")
        if hint_package.get("confidence") != active_knowledge.get("confidence"):
            errors.append("confidence must match active knowledge")

    if usage_policy is not None:
        if hint_package.get("usage_policy_id") != usage_policy.get("usage_policy_id"):
            errors.append("usage_policy_id must match policy")

    return errors
