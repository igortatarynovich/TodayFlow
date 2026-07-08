"""P1.26 — Dataset candidate promotion gate (approval only, no training)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.day_model_v1_active_knowledge import (
    DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_active_knowledge_hint_package import (
    DAY_ACTIVE_KNOWLEDGE_HINT_PACKAGE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_hint_application import (
    DAY_HINT_APPLICATION_RESULT_V1_CONTRACT,
    FORBIDDEN_APPLICATION_OPERATIONS,
    validate_day_hint_application_result_v1,
)
from todayflow_backend.services.day_model_v1_hint_application_dataset_policy import (
    DATASET_STATUS_CANDIDATE,
    DATASET_STATUS_REJECTED,
    DATASET_STATUS_RUNTIME_TRACE_ONLY,
    DAY_HINT_APPLICATION_DATASET_POLICY_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import validate_claim

DAY_TRAINING_EXAMPLE_APPROVAL_V1_CONTRACT = "day_training_example_approval_v1"

APPROVAL_STATUS_APPROVED = "approved"
APPROVAL_STATUS_NOT_READY = "not_ready"
APPROVAL_STATUS_REJECTED = "rejected"

ALLOWED_APPROVAL_STATUSES = frozenset(
    {
        APPROVAL_STATUS_APPROVED,
        APPROVAL_STATUS_NOT_READY,
        APPROVAL_STATUS_REJECTED,
    }
)

REASON_ALL_GATES_PASSED = "all_gates_passed"
REASON_DATASET_NOT_CANDIDATE = "dataset_status_not_candidate"
REASON_RUNTIME_TRACE_NOT_PROMOTABLE = "runtime_trace_only_not_promotable"
REASON_DATASET_POLICY_REJECTED = "dataset_policy_rejected"
REASON_MISSING_REACTION_EVIDENCE = "missing_reaction_evidence"
REASON_QUALITY_NOT_PASSED = "quality_evaluation_not_passed"
REASON_REVIEW_NOT_APPROVED = "review_not_approved"
REASON_FORBIDDEN_OPERATION = "forbidden_application_operation"
REASON_MUTATION_ATTEMPT = "mutation_attempt_detected"
REASON_MISSING_SNAPSHOT_TRACE = "missing_snapshot_trace"
REASON_SENSITIVE_CLAIM = "sensitive_claim"
REASON_INVALID_APPLICATION = "invalid_application"
REASON_TRAINING_USE_NOT_ALLOWED = "training_use_must_be_false_from_p1_25"

PROMOTION_RESULT_APPROVED = "approved"
PROMOTION_RESULT_NOT_READY = "not_ready"
PROMOTION_RESULT_REJECTED = "rejected"

DAY_TRAINING_EXAMPLE_APPROVAL_V1_KEYS = frozenset(
    {
        "contract_version",
        "training_example_id",
        "source_dataset_policy_id",
        "application_id",
        "hint_package_id",
        "knowledge_id",
        "consumer",
        "input_snapshot_hash",
        "output_snapshot_hash",
        "quality_evidence",
        "reaction_evidence",
        "approval_status",
        "approval_reason",
        "training_use_allowed",
        "requires_review",
        "created_at",
        "profile_update_allowed",
        "memory_update_allowed",
        "ranking_model_update_allowed",
    }
)


class DayTrainingExampleApprovalError(ValueError):
    """Raised when training example approval inputs or payload are invalid."""


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


def reaction_evidence_present(reaction_evidence: dict[str, Any] | None) -> bool:
    if not isinstance(reaction_evidence, dict):
        return False
    if reaction_evidence.get("present") is True:
        return True
    return bool(reaction_evidence.get("reaction_type"))


def quality_evaluation_passed(quality_evidence: dict[str, Any] | None) -> bool:
    if not isinstance(quality_evidence, dict):
        return False
    return quality_evidence.get("passed") is True


def evaluate_promotion_gate(
    dataset_policy: dict[str, Any],
    application_result: dict[str, Any],
    hint_package: dict[str, Any],
    active_knowledge: dict[str, Any],
    *,
    reaction_evidence: dict[str, Any] | None = None,
    quality_evidence: dict[str, Any] | None = None,
    review_approved: bool = False,
) -> tuple[str, str]:
    """Return approval_status, approval_reason."""
    dataset_status = dataset_policy.get("dataset_status")

    if dataset_status == DATASET_STATUS_RUNTIME_TRACE_ONLY:
        return APPROVAL_STATUS_REJECTED, REASON_RUNTIME_TRACE_NOT_PROMOTABLE

    if dataset_status == DATASET_STATUS_REJECTED:
        return APPROVAL_STATUS_REJECTED, REASON_DATASET_POLICY_REJECTED

    if dataset_status != DATASET_STATUS_CANDIDATE:
        return APPROVAL_STATUS_REJECTED, REASON_DATASET_NOT_CANDIDATE

    if dataset_policy.get("training_use_allowed") is not False:
        return APPROVAL_STATUS_REJECTED, REASON_TRAINING_USE_NOT_ALLOWED

    if application_result.get("contract_version") != DAY_HINT_APPLICATION_RESULT_V1_CONTRACT:
        return APPROVAL_STATUS_REJECTED, REASON_INVALID_APPLICATION

    if _mutation_attempt_detected(application_result):
        return APPROVAL_STATUS_REJECTED, REASON_MUTATION_ATTEMPT

    application_mode = application_result.get("application_mode")
    if isinstance(application_mode, str) and application_mode in FORBIDDEN_APPLICATION_OPERATIONS:
        return APPROVAL_STATUS_REJECTED, REASON_FORBIDDEN_OPERATION

    if not _has_valid_snapshot_trace(application_result):
        return APPROVAL_STATUS_REJECTED, REASON_MISSING_SNAPSHOT_TRACE

    claim = hint_package.get("claim") or active_knowledge.get("claim")
    if isinstance(claim, str) and validate_claim(claim):
        return APPROVAL_STATUS_REJECTED, REASON_SENSITIVE_CLAIM

    app_errors = validate_day_hint_application_result_v1(
        application_result,
        hint_package=hint_package,
    )
    if app_errors:
        return APPROVAL_STATUS_REJECTED, REASON_INVALID_APPLICATION

    requires_reaction = dataset_policy.get("requires_reaction_evidence") is True
    requires_quality = dataset_policy.get("requires_quality_evaluation") is True
    requires_review = dataset_policy.get("requires_review") is True

    if requires_reaction and not reaction_evidence_present(reaction_evidence):
        return APPROVAL_STATUS_NOT_READY, REASON_MISSING_REACTION_EVIDENCE

    if requires_quality and not quality_evaluation_passed(quality_evidence):
        return APPROVAL_STATUS_NOT_READY, REASON_QUALITY_NOT_PASSED

    if requires_review and review_approved is not True:
        return APPROVAL_STATUS_NOT_READY, REASON_REVIEW_NOT_APPROVED

    return APPROVAL_STATUS_APPROVED, REASON_ALL_GATES_PASSED


def try_promote_dataset_candidate_v1(
    dataset_policy: dict[str, Any],
    application_result: dict[str, Any],
    hint_package: dict[str, Any],
    active_knowledge: dict[str, Any],
    *,
    reaction_evidence: dict[str, Any] | None = None,
    quality_evidence: dict[str, Any] | None = None,
    review_approved: bool = False,
    created_at: str | None = None,
    training_example_id: str | None = None,
) -> dict[str, Any]:
    """
    P1.26 — promote P1.25 candidate to approved training example when gates pass.

    Dataset candidate ≠ approved training example. Does not start training.
    """
    if dataset_policy.get("contract_version") != DAY_HINT_APPLICATION_DATASET_POLICY_V1_CONTRACT:
        return {
            "result": PROMOTION_RESULT_REJECTED,
            "training_example": None,
            "reasons": ["invalid dataset policy contract_version"],
        }

    if application_result.get("contract_version") != DAY_HINT_APPLICATION_RESULT_V1_CONTRACT:
        return {
            "result": PROMOTION_RESULT_REJECTED,
            "training_example": None,
            "reasons": ["invalid application result contract_version"],
        }

    if hint_package.get("contract_version") != DAY_ACTIVE_KNOWLEDGE_HINT_PACKAGE_V1_CONTRACT:
        return {
            "result": PROMOTION_RESULT_REJECTED,
            "training_example": None,
            "reasons": ["invalid hint package contract_version"],
        }

    if active_knowledge.get("contract_version") != DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT:
        return {
            "result": PROMOTION_RESULT_REJECTED,
            "training_example": None,
            "reasons": ["invalid active knowledge contract_version"],
        }

    if dataset_policy.get("application_id") != application_result.get("application_id"):
        return {
            "result": PROMOTION_RESULT_REJECTED,
            "training_example": None,
            "reasons": ["application_id mismatch"],
        }

    if dataset_policy.get("hint_package_id") != hint_package.get("hint_package_id"):
        return {
            "result": PROMOTION_RESULT_REJECTED,
            "training_example": None,
            "reasons": ["hint_package_id mismatch"],
        }

    approval_status, approval_reason = evaluate_promotion_gate(
        dataset_policy,
        application_result,
        hint_package,
        active_knowledge,
        reaction_evidence=reaction_evidence,
        quality_evidence=quality_evidence,
        review_approved=review_approved,
    )

    training_use_allowed = approval_status == APPROVAL_STATUS_APPROVED

    training_example = {
        "contract_version": DAY_TRAINING_EXAMPLE_APPROVAL_V1_CONTRACT,
        "training_example_id": training_example_id or generate_training_example_id(),
        "source_dataset_policy_id": dataset_policy["dataset_policy_id"],
        "application_id": application_result["application_id"],
        "hint_package_id": hint_package["hint_package_id"],
        "knowledge_id": dataset_policy.get("knowledge_id"),
        "consumer": application_result.get("consumer"),
        "input_snapshot_hash": application_result.get("before_snapshot_hash"),
        "output_snapshot_hash": application_result.get("after_snapshot_hash"),
        "quality_evidence": quality_evidence or {},
        "reaction_evidence": reaction_evidence or {},
        "approval_status": approval_status,
        "approval_reason": approval_reason,
        "training_use_allowed": training_use_allowed,
        "requires_review": dataset_policy.get("requires_review") is True,
        "created_at": created_at or _utc_now_iso(),
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_model_update_allowed": False,
    }

    errors = validate_day_training_example_approval_v1(
        training_example,
        dataset_policy=dataset_policy,
        application_result=application_result,
        hint_package=hint_package,
    )
    if errors:
        raise DayTrainingExampleApprovalError("; ".join(errors))

    result_map = {
        APPROVAL_STATUS_APPROVED: PROMOTION_RESULT_APPROVED,
        APPROVAL_STATUS_NOT_READY: PROMOTION_RESULT_NOT_READY,
        APPROVAL_STATUS_REJECTED: PROMOTION_RESULT_REJECTED,
    }

    return {
        "result": result_map[approval_status],
        "training_example": training_example,
        "reasons": [] if approval_status == APPROVAL_STATUS_APPROVED else [approval_reason],
    }


def generate_training_example_id() -> str:
    return f"texp-{uuid4()}"


def validate_day_training_example_approval_v1(
    training_example: dict[str, Any],
    *,
    dataset_policy: dict[str, Any] | None = None,
    application_result: dict[str, Any] | None = None,
    hint_package: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if training_example.get("contract_version") != DAY_TRAINING_EXAMPLE_APPROVAL_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in DAY_TRAINING_EXAMPLE_APPROVAL_V1_KEYS:
        if key not in training_example:
            errors.append(f"missing field: {key}")

    if training_example.get("profile_update_allowed") is not False:
        errors.append("profile_update_allowed must be false")
    if training_example.get("memory_update_allowed") is not False:
        errors.append("memory_update_allowed must be false")
    if training_example.get("ranking_model_update_allowed") is not False:
        errors.append("ranking_model_update_allowed must be false")

    approval_status = training_example.get("approval_status")
    if approval_status not in ALLOWED_APPROVAL_STATUSES:
        errors.append("invalid approval_status")

    training_use_allowed = training_example.get("training_use_allowed")
    if approval_status == APPROVAL_STATUS_APPROVED:
        if training_use_allowed is not True:
            errors.append("training_use_allowed must be true when approved")
        if training_example.get("approval_reason") != REASON_ALL_GATES_PASSED:
            errors.append("approved status requires all_gates_passed reason")
    else:
        if training_use_allowed is not False:
            errors.append("training_use_allowed must be false unless approved")

    input_hash = training_example.get("input_snapshot_hash")
    output_hash = training_example.get("output_snapshot_hash")
    if not isinstance(input_hash, str) or not input_hash.startswith("snap-"):
        errors.append("input_snapshot_hash required")
    if not isinstance(output_hash, str) or not output_hash.startswith("snap-"):
        errors.append("output_snapshot_hash required")

    if dataset_policy is not None:
        if training_example.get("source_dataset_policy_id") != dataset_policy.get(
            "dataset_policy_id"
        ):
            errors.append("source_dataset_policy_id must match dataset policy")
        if training_example.get("knowledge_id") != dataset_policy.get("knowledge_id"):
            errors.append("knowledge_id must match dataset policy")

    if application_result is not None:
        if training_example.get("application_id") != application_result.get("application_id"):
            errors.append("application_id must match application result")
        if training_example.get("input_snapshot_hash") != application_result.get(
            "before_snapshot_hash"
        ):
            errors.append("input_snapshot_hash must match before_snapshot_hash")
        if training_example.get("output_snapshot_hash") != application_result.get(
            "after_snapshot_hash"
        ):
            errors.append("output_snapshot_hash must match after_snapshot_hash")

    if hint_package is not None:
        if training_example.get("hint_package_id") != hint_package.get("hint_package_id"):
            errors.append("hint_package_id must match hint package")

    return errors
