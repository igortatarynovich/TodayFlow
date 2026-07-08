"""P1.24 — Hint package application contract (trace only, no mutation)."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.day_model_v1_active_knowledge_hint_package import (
    ALLOWED_OPERATIONS_BY_HINT_TYPE,
    DAY_ACTIVE_KNOWLEDGE_HINT_PACKAGE_V1_CONTRACT,
    HINT_PACKAGE_STATUS_READY,
    HINT_TYPE_CACHE,
    HINT_TYPE_CONTEXT,
    HINT_TYPE_PROMPT,
    HINT_TYPE_RANKING,
    HINT_TYPE_SURFACE_PRIORITY,
)

DAY_HINT_APPLICATION_RESULT_V1_CONTRACT = "day_hint_application_result_v1"

CONSUMER_CONTEXT_SELECTOR = "context_selector"
CONSUMER_PROMPT_BUILDER = "prompt_builder"
CONSUMER_CACHE_REUSE = "cache_reuse"
CONSUMER_CONTENT_RANKER = "content_ranker"
CONSUMER_SURFACE_PRIORITIZER = "surface_prioritizer"

ALLOWED_CONSUMERS = frozenset(
    {
        CONSUMER_CONTEXT_SELECTOR,
        CONSUMER_PROMPT_BUILDER,
        CONSUMER_CACHE_REUSE,
        CONSUMER_CONTENT_RANKER,
        CONSUMER_SURFACE_PRIORITIZER,
    }
)

HINT_TYPE_TO_CONSUMER: dict[str, str] = {
    HINT_TYPE_CONTEXT: CONSUMER_CONTEXT_SELECTOR,
    HINT_TYPE_PROMPT: CONSUMER_PROMPT_BUILDER,
    HINT_TYPE_CACHE: CONSUMER_CACHE_REUSE,
    HINT_TYPE_RANKING: CONSUMER_CONTENT_RANKER,
    HINT_TYPE_SURFACE_PRIORITY: CONSUMER_SURFACE_PRIORITIZER,
}

APPLICATION_MODE_INCLUDE = "include"
APPLICATION_MODE_PRIORITIZE = "prioritize"
APPLICATION_MODE_SUPPRESS = "suppress"
APPLICATION_MODE_ADJUST_TONE = "adjust_tone"
APPLICATION_MODE_ADJUST_LENGTH = "adjust_length"
APPLICATION_MODE_BOOST = "boost"
APPLICATION_MODE_LOWER = "lower"
APPLICATION_MODE_DELAY = "delay"

ALLOWED_APPLICATION_MODES = frozenset(
    {
        APPLICATION_MODE_INCLUDE,
        APPLICATION_MODE_PRIORITIZE,
        APPLICATION_MODE_SUPPRESS,
        APPLICATION_MODE_ADJUST_TONE,
        APPLICATION_MODE_ADJUST_LENGTH,
        APPLICATION_MODE_BOOST,
        APPLICATION_MODE_LOWER,
        APPLICATION_MODE_DELAY,
    }
)

APPLICATION_MODES_BY_HINT_TYPE: dict[str, frozenset[str]] = {
    HINT_TYPE_CONTEXT: frozenset(
        {APPLICATION_MODE_INCLUDE, APPLICATION_MODE_PRIORITIZE, APPLICATION_MODE_SUPPRESS}
    ),
    HINT_TYPE_PROMPT: frozenset(
        {APPLICATION_MODE_ADJUST_TONE, APPLICATION_MODE_ADJUST_LENGTH}
    ),
    HINT_TYPE_CACHE: frozenset({APPLICATION_MODE_BOOST, APPLICATION_MODE_INCLUDE}),
    HINT_TYPE_RANKING: frozenset({APPLICATION_MODE_BOOST, APPLICATION_MODE_LOWER}),
    HINT_TYPE_SURFACE_PRIORITY: frozenset(
        {APPLICATION_MODE_BOOST, APPLICATION_MODE_DELAY}
    ),
}

OPERATION_TO_APPLICATION_MODE: dict[str, str] = {
    "include": APPLICATION_MODE_INCLUDE,
    "prioritize": APPLICATION_MODE_PRIORITIZE,
    "suppress_low_relevance": APPLICATION_MODE_SUPPRESS,
    "adjust_tone": APPLICATION_MODE_ADJUST_TONE,
    "adjust_length": APPLICATION_MODE_ADJUST_LENGTH,
    "reduce_repetition": APPLICATION_MODE_ADJUST_LENGTH,
    "increase_reuse_score": APPLICATION_MODE_BOOST,
    "allow_similarity_match": APPLICATION_MODE_INCLUDE,
    "boost_related_content": APPLICATION_MODE_BOOST,
    "lower_unrelated_content": APPLICATION_MODE_LOWER,
    "boost_surface": APPLICATION_MODE_BOOST,
    "delay_surface": APPLICATION_MODE_DELAY,
}

FORBIDDEN_APPLICATION_OPERATIONS = frozenset(
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
        "add_raw_profile",
        "add_sensitive_data",
        "exceed_context_depth",
        "add_claims",
        "add_astrology",
        "add_tarot",
        "add_numerology",
        "bypass_safety",
        "reuse_rejected_candidate",
        "mutate_ranking_model",
        "persist_ranking_weights",
        "suppress_critical_risk_surface",
    }
)

APPLICATION_RESULT_APPLIED = "applied"
APPLICATION_RESULT_REJECTED = "rejected"

DAY_HINT_APPLICATION_RESULT_V1_KEYS = frozenset(
    {
        "contract_version",
        "application_id",
        "hint_package_id",
        "consumer",
        "surface",
        "hint_type",
        "applied",
        "application_mode",
        "influence_level",
        "before_snapshot_hash",
        "after_snapshot_hash",
        "changes_summary",
        "traceability",
        "created_at",
        "profile_update_allowed",
        "memory_update_allowed",
        "ranking_model_update_allowed",
    }
)


class DayHintApplicationError(ValueError):
    """Raised when hint application inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def compute_state_snapshot_hash(state: dict[str, Any]) -> str:
    payload = json.dumps(state, sort_keys=True, separators=(",", ":"), default=str)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]
    return f"snap-{digest}"


def expected_consumer_for_hint_type(hint_type: str) -> str | None:
    return HINT_TYPE_TO_CONSUMER.get(hint_type)


def is_application_mode_allowed_for_hint(
    hint_type: str,
    application_mode: str,
    *,
    allowed_operations: list[str] | None = None,
) -> bool:
    if application_mode not in ALLOWED_APPLICATION_MODES:
        return False
    if application_mode in FORBIDDEN_APPLICATION_OPERATIONS:
        return False
    allowed_modes = APPLICATION_MODES_BY_HINT_TYPE.get(hint_type, frozenset())
    if application_mode not in allowed_modes:
        return False
    if allowed_operations is not None:
        mapped_modes = {
            OPERATION_TO_APPLICATION_MODE[op]
            for op in allowed_operations
            if op in OPERATION_TO_APPLICATION_MODE
        }
        if application_mode not in mapped_modes:
            return False
    return True


def build_changes_summary(
    *,
    hint_type: str,
    application_mode: str,
    claim: str,
) -> str:
    return f"{hint_type}:{application_mode}:claim={claim}"


def try_apply_hint_package_v1(
    hint_package: dict[str, Any],
    *,
    consumer: str,
    application_mode: str,
    before_state: dict[str, Any],
    after_state: dict[str, Any],
    applied: bool = True,
    created_at: str | None = None,
    application_id: str | None = None,
) -> dict[str, Any]:
    """
    P1.24 — apply hint package to a local runtime decision with trace.

    Hint application ≠ mutation. Does not modify hint_package or persist learning.
    """
    if hint_package.get("contract_version") != DAY_ACTIVE_KNOWLEDGE_HINT_PACKAGE_V1_CONTRACT:
        return {
            "result": APPLICATION_RESULT_REJECTED,
            "application_result": None,
            "reasons": ["invalid hint package contract_version"],
        }

    if hint_package.get("status") != HINT_PACKAGE_STATUS_READY:
        return {
            "result": APPLICATION_RESULT_REJECTED,
            "application_result": None,
            "reasons": ["hint package status must be ready"],
        }

    if hint_package.get("applied") is not False:
        return {
            "result": APPLICATION_RESULT_REJECTED,
            "application_result": None,
            "reasons": ["hint package already applied"],
        }

    hint_type = hint_package.get("hint_type")
    if not isinstance(hint_type, str):
        return {
            "result": APPLICATION_RESULT_REJECTED,
            "application_result": None,
            "reasons": ["invalid hint_type"],
        }

    expected_consumer = expected_consumer_for_hint_type(hint_type)
    if consumer not in ALLOWED_CONSUMERS:
        return {
            "result": APPLICATION_RESULT_REJECTED,
            "application_result": None,
            "reasons": ["invalid consumer"],
        }

    if consumer != expected_consumer:
        return {
            "result": APPLICATION_RESULT_REJECTED,
            "application_result": None,
            "reasons": ["consumer incompatible with hint_type"],
        }

    if application_mode in FORBIDDEN_APPLICATION_OPERATIONS:
        return {
            "result": APPLICATION_RESULT_REJECTED,
            "application_result": None,
            "reasons": ["forbidden application operation"],
        }

    allowed_operations = hint_package.get("allowed_operations")
    if not isinstance(allowed_operations, list):
        return {
            "result": APPLICATION_RESULT_REJECTED,
            "application_result": None,
            "reasons": ["invalid allowed_operations on hint package"],
        }

    if not is_application_mode_allowed_for_hint(
        hint_type,
        application_mode,
        allowed_operations=allowed_operations,
    ):
        return {
            "result": APPLICATION_RESULT_REJECTED,
            "application_result": None,
            "reasons": ["application_mode not allowed for hint_type"],
        }

    if not isinstance(before_state, dict) or not before_state:
        return {
            "result": APPLICATION_RESULT_REJECTED,
            "application_result": None,
            "reasons": ["before_state required"],
        }

    if not isinstance(after_state, dict) or not after_state:
        return {
            "result": APPLICATION_RESULT_REJECTED,
            "application_result": None,
            "reasons": ["after_state required"],
        }

    before_hash = compute_state_snapshot_hash(before_state)
    after_hash = compute_state_snapshot_hash(after_state)

    if not before_hash or not after_hash:
        return {
            "result": APPLICATION_RESULT_REJECTED,
            "application_result": None,
            "reasons": ["before/after snapshot hash required"],
        }

    claim = hint_package.get("claim", "")
    influence_level = hint_package.get("influence_level")
    traceability = hint_package.get("traceability") or {}

    application_result = {
        "contract_version": DAY_HINT_APPLICATION_RESULT_V1_CONTRACT,
        "application_id": application_id or generate_application_id(),
        "hint_package_id": hint_package["hint_package_id"],
        "consumer": consumer,
        "surface": hint_package["surface"],
        "hint_type": hint_type,
        "applied": applied,
        "application_mode": application_mode,
        "influence_level": influence_level,
        "before_snapshot_hash": before_hash,
        "after_snapshot_hash": after_hash,
        "changes_summary": build_changes_summary(
            hint_type=hint_type,
            application_mode=application_mode,
            claim=str(claim),
        ),
        "traceability": {
            "knowledge_id": hint_package.get("knowledge_id"),
            "runtime_decision_id": hint_package.get("runtime_decision_id"),
            "policy_id": hint_package.get("usage_policy_id"),
            "source_pattern_id": traceability.get("source_pattern_id"),
        },
        "created_at": created_at or _utc_now_iso(),
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_model_update_allowed": False,
    }

    errors = validate_day_hint_application_result_v1(
        application_result,
        hint_package=hint_package,
    )
    if errors:
        raise DayHintApplicationError("; ".join(errors))

    return {
        "result": APPLICATION_RESULT_APPLIED,
        "application_result": application_result,
        "reasons": [],
    }


def generate_application_id() -> str:
    return f"happ-{uuid4()}"


def validate_day_hint_application_result_v1(
    application_result: dict[str, Any],
    *,
    hint_package: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if application_result.get("contract_version") != DAY_HINT_APPLICATION_RESULT_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in DAY_HINT_APPLICATION_RESULT_V1_KEYS:
        if key not in application_result:
            errors.append(f"missing field: {key}")

    if application_result.get("profile_update_allowed") is not False:
        errors.append("profile_update_allowed must be false")
    if application_result.get("memory_update_allowed") is not False:
        errors.append("memory_update_allowed must be false")
    if application_result.get("ranking_model_update_allowed") is not False:
        errors.append("ranking_model_update_allowed must be false")

    before_hash = application_result.get("before_snapshot_hash")
    after_hash = application_result.get("after_snapshot_hash")
    if not isinstance(before_hash, str) or not before_hash.startswith("snap-"):
        errors.append("before_snapshot_hash required")
    if not isinstance(after_hash, str) or not after_hash.startswith("snap-"):
        errors.append("after_snapshot_hash required")

    consumer = application_result.get("consumer")
    hint_type = application_result.get("hint_type")
    if isinstance(hint_type, str) and isinstance(consumer, str):
        if expected_consumer_for_hint_type(hint_type) != consumer:
            errors.append("consumer incompatible with hint_type")

    application_mode = application_result.get("application_mode")
    if isinstance(application_mode, str):
        if application_mode in FORBIDDEN_APPLICATION_OPERATIONS:
            errors.append("forbidden application_mode")
        elif isinstance(hint_type, str):
            allowed_ops = None
            if hint_package is not None:
                ops = hint_package.get("allowed_operations")
                if isinstance(ops, list):
                    allowed_ops = ops
            if not is_application_mode_allowed_for_hint(
                hint_type,
                application_mode,
                allowed_operations=allowed_ops,
            ):
                errors.append("application_mode not allowed for hint_type")

    if hint_package is not None:
        if application_result.get("hint_package_id") != hint_package.get("hint_package_id"):
            errors.append("hint_package_id must match hint package")
        if application_result.get("hint_type") != hint_package.get("hint_type"):
            errors.append("hint_type must match hint package")
        if application_result.get("surface") != hint_package.get("surface"):
            errors.append("surface must match hint package")
        if application_result.get("influence_level") != hint_package.get("influence_level"):
            errors.append("influence_level must match hint package")

        trace = application_result.get("traceability")
        if isinstance(trace, dict):
            if trace.get("knowledge_id") != hint_package.get("knowledge_id"):
                errors.append("traceability.knowledge_id must match hint package")
            if trace.get("runtime_decision_id") != hint_package.get("runtime_decision_id"):
                errors.append("traceability.runtime_decision_id must match hint package")
            if trace.get("policy_id") != hint_package.get("usage_policy_id"):
                errors.append("traceability.policy_id must match hint package")

    return errors
