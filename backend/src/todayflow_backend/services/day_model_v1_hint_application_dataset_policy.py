"""P1.25 — Hint application audit → dataset candidate policy (no training)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.day_model_v1_active_knowledge import (
    ACTIVE_KNOWLEDGE_STATUS,
    DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_active_knowledge_hint_package import (
    DAY_ACTIVE_KNOWLEDGE_HINT_PACKAGE_V1_CONTRACT,
    HINT_TYPE_CACHE,
    HINT_TYPE_CONTEXT,
    HINT_TYPE_PROMPT,
    HINT_TYPE_RANKING,
    HINT_TYPE_SURFACE_PRIORITY,
)
from todayflow_backend.services.day_model_v1_hint_application import (
    DAY_HINT_APPLICATION_RESULT_V1_CONTRACT,
    FORBIDDEN_APPLICATION_OPERATIONS,
    expected_consumer_for_hint_type,
    validate_day_hint_application_result_v1,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import (
    ALLOWED_KNOWLEDGE_TYPES,
    validate_claim,
)

DAY_HINT_APPLICATION_DATASET_POLICY_V1_CONTRACT = "day_hint_application_dataset_policy_v1"

DATASET_STATUS_CANDIDATE = "candidate"
DATASET_STATUS_RUNTIME_TRACE_ONLY = "runtime_trace_only"
DATASET_STATUS_REJECTED = "rejected"

ALLOWED_DATASET_STATUSES = frozenset(
    {
        DATASET_STATUS_CANDIDATE,
        DATASET_STATUS_RUNTIME_TRACE_ONLY,
        DATASET_STATUS_REJECTED,
    }
)

HINT_TYPES_ALLOWED_FOR_DATASET = frozenset(
    {
        HINT_TYPE_CONTEXT,
        HINT_TYPE_PROMPT,
        HINT_TYPE_CACHE,
        HINT_TYPE_RANKING,
        HINT_TYPE_SURFACE_PRIORITY,
    }
)

HINT_TYPES_REQUIRING_REVIEW = frozenset(
    {HINT_TYPE_PROMPT, HINT_TYPE_RANKING, HINT_TYPE_SURFACE_PRIORITY}
)

HINT_TYPES_REQUIRING_QUALITY_EVALUATION = frozenset(
    {HINT_TYPE_PROMPT, HINT_TYPE_RANKING, HINT_TYPE_SURFACE_PRIORITY}
)

REASON_VALID_APPLICATION = "valid_application_ready_for_reaction"
REASON_INSUFFICIENT_REUSE_EVIDENCE = "insufficient_reuse_success_evidence"
REASON_MISSING_DOWNSTREAM_REACTION = "missing_downstream_reaction_evidence"
REASON_MISSING_USER_REACTION = "missing_user_reaction_evidence"
REASON_MISSING_SNAPSHOT_TRACE = "missing_snapshot_trace"
REASON_FORBIDDEN_OPERATION = "forbidden_application_operation"
REASON_MUTATION_ATTEMPT = "mutation_attempt_detected"
REASON_INCOMPATIBLE_CONSUMER = "incompatible_consumer"
REASON_APPLICATION_NOT_APPLIED = "application_not_applied"
REASON_SENSITIVE_CLAIM = "sensitive_claim"
REASON_KNOWLEDGE_NOT_ACTIVE = "knowledge_not_active"
REASON_INVALID_APPLICATION = "invalid_application"
REASON_HINT_TYPE_NOT_ALLOWED = "hint_type_not_allowed_for_dataset"

DATASET_POLICY_RESULT_CREATED = "created"
DATASET_POLICY_RESULT_REJECTED = "rejected"

DAY_HINT_APPLICATION_DATASET_POLICY_V1_KEYS = frozenset(
    {
        "contract_version",
        "dataset_policy_id",
        "application_id",
        "hint_package_id",
        "knowledge_id",
        "consumer",
        "hint_type",
        "application_mode",
        "dataset_status",
        "candidate_reason",
        "requires_reaction_evidence",
        "requires_quality_evaluation",
        "requires_review",
        "training_use_allowed",
        "created_at",
    }
)


class DayHintApplicationDatasetPolicyError(ValueError):
    """Raised when dataset policy inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _has_valid_snapshot_trace(application_result: dict[str, Any]) -> bool:
    before_hash = application_result.get("before_snapshot_hash")
    after_hash = application_result.get("after_snapshot_hash")
    return (
        isinstance(before_hash, str)
        and before_hash.startswith("snap-")
        and isinstance(after_hash, str)
        and after_hash.startswith("snap-")
    )


def _mutation_attempt_detected(application_result: dict[str, Any]) -> bool:
    return (
        application_result.get("profile_update_allowed") is not False
        or application_result.get("memory_update_allowed") is not False
        or application_result.get("ranking_model_update_allowed") is not False
    )


def evaluate_dataset_policy_status(
    application_result: dict[str, Any],
    hint_package: dict[str, Any],
    active_knowledge: dict[str, Any],
    *,
    reuse_success_evidence: bool = False,
    downstream_reaction_evidence: bool = False,
    user_reaction_evidence: bool = False,
) -> tuple[str, str, bool, bool, bool]:
    """
    Return dataset_status, candidate_reason, requires_reaction_evidence,
    requires_quality_evaluation, requires_review.
    """
    if application_result.get("contract_version") != DAY_HINT_APPLICATION_RESULT_V1_CONTRACT:
        return (
            DATASET_STATUS_REJECTED,
            REASON_INVALID_APPLICATION,
            True,
            False,
            False,
        )

    if _mutation_attempt_detected(application_result):
        return (
            DATASET_STATUS_REJECTED,
            REASON_MUTATION_ATTEMPT,
            True,
            False,
            False,
        )

    if application_result.get("applied") is not True:
        return (
            DATASET_STATUS_REJECTED,
            REASON_APPLICATION_NOT_APPLIED,
            True,
            False,
            False,
        )

    if not _has_valid_snapshot_trace(application_result):
        return (
            DATASET_STATUS_REJECTED,
            REASON_MISSING_SNAPSHOT_TRACE,
            True,
            False,
            False,
        )

    hint_type = application_result.get("hint_type")
    consumer = application_result.get("consumer")
    if not isinstance(hint_type, str) or not isinstance(consumer, str):
        return (
            DATASET_STATUS_REJECTED,
            REASON_INVALID_APPLICATION,
            True,
            False,
            False,
        )

    if expected_consumer_for_hint_type(hint_type) != consumer:
        return (
            DATASET_STATUS_REJECTED,
            REASON_INCOMPATIBLE_CONSUMER,
            True,
            False,
            False,
        )

    application_mode = application_result.get("application_mode")
    if isinstance(application_mode, str) and application_mode in FORBIDDEN_APPLICATION_OPERATIONS:
        return (
            DATASET_STATUS_REJECTED,
            REASON_FORBIDDEN_OPERATION,
            True,
            False,
            False,
        )

    claim = hint_package.get("claim") or active_knowledge.get("claim")
    if isinstance(claim, str) and validate_claim(claim):
        return (
            DATASET_STATUS_REJECTED,
            REASON_SENSITIVE_CLAIM,
            True,
            False,
            False,
        )

    if active_knowledge.get("status") != ACTIVE_KNOWLEDGE_STATUS:
        return (
            DATASET_STATUS_REJECTED,
            REASON_KNOWLEDGE_NOT_ACTIVE,
            True,
            False,
            False,
        )

    if hint_type not in HINT_TYPES_ALLOWED_FOR_DATASET:
        return (
            DATASET_STATUS_REJECTED,
            REASON_HINT_TYPE_NOT_ALLOWED,
            True,
            False,
            False,
        )

    app_errors = validate_day_hint_application_result_v1(
        application_result,
        hint_package=hint_package,
    )
    if app_errors:
        return (
            DATASET_STATUS_REJECTED,
            REASON_INVALID_APPLICATION,
            True,
            False,
            False,
        )

    requires_review = hint_type in HINT_TYPES_REQUIRING_REVIEW
    requires_quality_evaluation = hint_type in HINT_TYPES_REQUIRING_QUALITY_EVALUATION

    if hint_type == HINT_TYPE_CACHE and not reuse_success_evidence:
        return (
            DATASET_STATUS_RUNTIME_TRACE_ONLY,
            REASON_INSUFFICIENT_REUSE_EVIDENCE,
            True,
            False,
            False,
        )

    if hint_type == HINT_TYPE_RANKING and not downstream_reaction_evidence:
        return (
            DATASET_STATUS_RUNTIME_TRACE_ONLY,
            REASON_MISSING_DOWNSTREAM_REACTION,
            True,
            requires_quality_evaluation,
            requires_review,
        )

    if hint_type == HINT_TYPE_SURFACE_PRIORITY and not user_reaction_evidence:
        return (
            DATASET_STATUS_RUNTIME_TRACE_ONLY,
            REASON_MISSING_USER_REACTION,
            True,
            requires_quality_evaluation,
            requires_review,
        )

    has_evidence = (
        (hint_type == HINT_TYPE_CACHE and reuse_success_evidence)
        or (hint_type == HINT_TYPE_RANKING and downstream_reaction_evidence)
        or (hint_type == HINT_TYPE_SURFACE_PRIORITY and user_reaction_evidence)
    )

    requires_reaction_evidence = not has_evidence and hint_type in {
        HINT_TYPE_CONTEXT,
        HINT_TYPE_PROMPT,
    }
    if hint_type in {HINT_TYPE_CONTEXT, HINT_TYPE_PROMPT}:
        requires_reaction_evidence = True

    return (
        DATASET_STATUS_CANDIDATE,
        REASON_VALID_APPLICATION,
        requires_reaction_evidence,
        requires_quality_evaluation,
        requires_review,
    )


def try_build_hint_application_dataset_policy_v1(
    application_result: dict[str, Any],
    hint_package: dict[str, Any],
    active_knowledge: dict[str, Any],
    *,
    reuse_success_evidence: bool = False,
    downstream_reaction_evidence: bool = False,
    user_reaction_evidence: bool = False,
    created_at: str | None = None,
    dataset_policy_id: str | None = None,
) -> dict[str, Any]:
    """
    P1.25 — decide whether a hint application may be a future dataset candidate.

    Hint application ≠ training example. training_use_allowed=false always.
    """
    if hint_package.get("contract_version") != DAY_ACTIVE_KNOWLEDGE_HINT_PACKAGE_V1_CONTRACT:
        return {
            "result": DATASET_POLICY_RESULT_REJECTED,
            "dataset_policy": None,
            "reasons": ["invalid hint package contract_version"],
        }

    if active_knowledge.get("contract_version") != DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT:
        return {
            "result": DATASET_POLICY_RESULT_REJECTED,
            "dataset_policy": None,
            "reasons": ["invalid active knowledge contract_version"],
        }

    if application_result.get("hint_package_id") != hint_package.get("hint_package_id"):
        return {
            "result": DATASET_POLICY_RESULT_REJECTED,
            "dataset_policy": None,
            "reasons": ["application hint_package_id mismatch"],
        }

    knowledge_type = active_knowledge.get("knowledge_type")
    if knowledge_type not in ALLOWED_KNOWLEDGE_TYPES:
        return {
            "result": DATASET_POLICY_RESULT_REJECTED,
            "dataset_policy": None,
            "reasons": ["invalid knowledge_type"],
        }

    trace = application_result.get("traceability") or {}
    knowledge_id = trace.get("knowledge_id") or hint_package.get("knowledge_id")
    if knowledge_id != active_knowledge.get("knowledge_id"):
        return {
            "result": DATASET_POLICY_RESULT_REJECTED,
            "dataset_policy": None,
            "reasons": ["knowledge_id mismatch"],
        }

    (
        dataset_status,
        candidate_reason,
        requires_reaction_evidence,
        requires_quality_evaluation,
        requires_review,
    ) = evaluate_dataset_policy_status(
        application_result,
        hint_package,
        active_knowledge,
        reuse_success_evidence=reuse_success_evidence,
        downstream_reaction_evidence=downstream_reaction_evidence,
        user_reaction_evidence=user_reaction_evidence,
    )

    dataset_policy = {
        "contract_version": DAY_HINT_APPLICATION_DATASET_POLICY_V1_CONTRACT,
        "dataset_policy_id": dataset_policy_id or generate_dataset_policy_id(),
        "application_id": application_result.get("application_id"),
        "hint_package_id": hint_package.get("hint_package_id"),
        "knowledge_id": knowledge_id,
        "consumer": application_result.get("consumer"),
        "hint_type": application_result.get("hint_type"),
        "application_mode": application_result.get("application_mode"),
        "dataset_status": dataset_status,
        "candidate_reason": candidate_reason,
        "requires_reaction_evidence": requires_reaction_evidence,
        "requires_quality_evaluation": requires_quality_evaluation,
        "requires_review": requires_review,
        "training_use_allowed": False,
        "created_at": created_at or _utc_now_iso(),
    }

    errors = validate_day_hint_application_dataset_policy_v1(
        dataset_policy,
        application_result=application_result,
        hint_package=hint_package,
        active_knowledge=active_knowledge,
    )
    if errors:
        raise DayHintApplicationDatasetPolicyError("; ".join(errors))

    return {
        "result": DATASET_POLICY_RESULT_CREATED,
        "dataset_policy": dataset_policy,
        "reasons": [],
    }


def generate_dataset_policy_id() -> str:
    return f"hdsp-{uuid4()}"


def validate_day_hint_application_dataset_policy_v1(
    dataset_policy: dict[str, Any],
    *,
    application_result: dict[str, Any] | None = None,
    hint_package: dict[str, Any] | None = None,
    active_knowledge: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if dataset_policy.get("contract_version") != DAY_HINT_APPLICATION_DATASET_POLICY_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in DAY_HINT_APPLICATION_DATASET_POLICY_V1_KEYS:
        if key not in dataset_policy:
            errors.append(f"missing field: {key}")

    if dataset_policy.get("training_use_allowed") is not False:
        errors.append("training_use_allowed must be false")

    dataset_status = dataset_policy.get("dataset_status")
    if dataset_status not in ALLOWED_DATASET_STATUSES:
        errors.append("invalid dataset_status")

    hint_type = dataset_policy.get("hint_type")
    if isinstance(hint_type, str) and hint_type not in HINT_TYPES_ALLOWED_FOR_DATASET:
        errors.append("invalid hint_type")

    if dataset_status == DATASET_STATUS_CANDIDATE:
        if dataset_policy.get("candidate_reason") != REASON_VALID_APPLICATION:
            errors.append("candidate status requires valid_application reason")

    if dataset_status == DATASET_STATUS_REJECTED:
        reason = dataset_policy.get("candidate_reason")
        if reason == REASON_VALID_APPLICATION:
            errors.append("rejected status cannot have valid_application reason")

    if application_result is not None:
        if dataset_policy.get("application_id") != application_result.get("application_id"):
            errors.append("application_id must match application result")
        if dataset_policy.get("consumer") != application_result.get("consumer"):
            errors.append("consumer must match application result")
        if dataset_policy.get("hint_type") != application_result.get("hint_type"):
            errors.append("hint_type must match application result")
        if dataset_policy.get("application_mode") != application_result.get(
            "application_mode"
        ):
            errors.append("application_mode must match application result")

    if hint_package is not None:
        if dataset_policy.get("hint_package_id") != hint_package.get("hint_package_id"):
            errors.append("hint_package_id must match hint package")

    if active_knowledge is not None:
        if dataset_policy.get("knowledge_id") != active_knowledge.get("knowledge_id"):
            errors.append("knowledge_id must match active knowledge")

    return errors
