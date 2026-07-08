"""P1.27 — Training dataset registry (registration only, no export/training)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.day_model_v1_active_knowledge import (
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
    validate_day_hint_application_result_v1,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import validate_claim
from todayflow_backend.services.day_model_v1_training_example_approval import (
    APPROVAL_STATUS_APPROVED,
    DAY_TRAINING_EXAMPLE_APPROVAL_V1_CONTRACT,
    validate_day_training_example_approval_v1,
)

DAY_TRAINING_DATASET_REGISTRY_ITEM_V1_CONTRACT = "day_training_dataset_registry_item_v1"

REGISTRY_STATUS_REGISTERED = "registered"

DATASET_SPLIT_UNASSIGNED = "unassigned"
ALLOWED_DATASET_SPLITS = frozenset({DATASET_SPLIT_UNASSIGNED})

DATASET_DOMAIN_DAY_MODEL = "day_model"
DATASET_DOMAIN_PROMPT_REFINEMENT = "prompt_refinement"
DATASET_DOMAIN_CONTEXT_SELECTION = "context_selection"
DATASET_DOMAIN_CACHE_REUSE = "cache_reuse"
DATASET_DOMAIN_RANKING = "ranking"

ALLOWED_DATASET_DOMAINS = frozenset(
    {
        DATASET_DOMAIN_DAY_MODEL,
        DATASET_DOMAIN_PROMPT_REFINEMENT,
        DATASET_DOMAIN_CONTEXT_SELECTION,
        DATASET_DOMAIN_CACHE_REUSE,
        DATASET_DOMAIN_RANKING,
    }
)

EXAMPLE_TYPE_PROMPT_REFINEMENT = "prompt_refinement"
EXAMPLE_TYPE_CONTEXT_HINT = "context_hint"
EXAMPLE_TYPE_CACHE_HINT = "cache_hint"
EXAMPLE_TYPE_RANKING_HINT = "ranking_hint"
EXAMPLE_TYPE_SURFACE_PRIORITY_HINT = "surface_priority_hint"

ALLOWED_EXAMPLE_TYPES = frozenset(
    {
        EXAMPLE_TYPE_PROMPT_REFINEMENT,
        EXAMPLE_TYPE_CONTEXT_HINT,
        EXAMPLE_TYPE_CACHE_HINT,
        EXAMPLE_TYPE_RANKING_HINT,
        EXAMPLE_TYPE_SURFACE_PRIORITY_HINT,
    }
)

HINT_TYPE_TO_DATASET_DOMAIN: dict[str, str] = {
    HINT_TYPE_PROMPT: DATASET_DOMAIN_PROMPT_REFINEMENT,
    HINT_TYPE_CONTEXT: DATASET_DOMAIN_CONTEXT_SELECTION,
    HINT_TYPE_CACHE: DATASET_DOMAIN_CACHE_REUSE,
    HINT_TYPE_RANKING: DATASET_DOMAIN_RANKING,
    HINT_TYPE_SURFACE_PRIORITY: DATASET_DOMAIN_DAY_MODEL,
}

HINT_TYPE_TO_EXAMPLE_TYPE: dict[str, str] = {
    HINT_TYPE_PROMPT: EXAMPLE_TYPE_PROMPT_REFINEMENT,
    HINT_TYPE_CONTEXT: EXAMPLE_TYPE_CONTEXT_HINT,
    HINT_TYPE_CACHE: EXAMPLE_TYPE_CACHE_HINT,
    HINT_TYPE_RANKING: EXAMPLE_TYPE_RANKING_HINT,
    HINT_TYPE_SURFACE_PRIORITY: EXAMPLE_TYPE_SURFACE_PRIORITY_HINT,
}

REGISTRY_RESULT_REGISTERED = "registered"
REGISTRY_RESULT_REJECTED = "rejected"

REASON_NOT_APPROVED = "approval_status_not_approved"
REASON_TRAINING_USE_NOT_ALLOWED = "training_use_not_allowed"
REASON_MISSING_SNAPSHOT_TRACE = "missing_snapshot_trace"
REASON_MUTATION_ATTEMPT = "mutation_attempt_detected"
REASON_FORBIDDEN_OPERATION = "forbidden_application_operation"
REASON_SENSITIVE_CLAIM = "sensitive_claim"
REASON_INVALID_TRAINING_EXAMPLE = "invalid_training_example"
REASON_INVALID_APPLICATION = "invalid_application"

DAY_TRAINING_DATASET_REGISTRY_ITEM_V1_KEYS = frozenset(
    {
        "contract_version",
        "registry_item_id",
        "training_example_id",
        "dataset_domain",
        "dataset_split",
        "example_type",
        "input_snapshot_hash",
        "output_snapshot_hash",
        "quality_evidence_ref",
        "reaction_evidence_ref",
        "source_knowledge_id",
        "source_application_id",
        "status",
        "export_allowed",
        "training_started",
        "created_at",
        "profile_update_allowed",
        "memory_update_allowed",
        "ranking_model_update_allowed",
    }
)


class DayTrainingDatasetRegistryError(ValueError):
    """Raised when registry inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def map_hint_type_to_dataset_domain(hint_type: str) -> str | None:
    return HINT_TYPE_TO_DATASET_DOMAIN.get(hint_type)


def map_hint_type_to_example_type(hint_type: str) -> str | None:
    return HINT_TYPE_TO_EXAMPLE_TYPE.get(hint_type)


def _has_valid_snapshot_hashes(training_example: dict[str, Any]) -> bool:
    input_hash = training_example.get("input_snapshot_hash")
    output_hash = training_example.get("output_snapshot_hash")
    return (
        isinstance(input_hash, str)
        and input_hash.startswith("snap-")
        and isinstance(output_hash, str)
        and output_hash.startswith("snap-")
    )


def _mutation_attempt_detected(training_example: dict[str, Any]) -> bool:
    return (
        training_example.get("profile_update_allowed") is not False
        or training_example.get("memory_update_allowed") is not False
        or training_example.get("ranking_model_update_allowed") is not False
    )


def build_evidence_ref(
    *,
    training_example_id: str,
    evidence: dict[str, Any] | None,
    evidence_kind: str,
) -> dict[str, Any]:
    payload = evidence if isinstance(evidence, dict) else {}
    return {
        "source": "training_example",
        "training_example_id": training_example_id,
        "evidence_kind": evidence_kind,
        "present": bool(payload),
        "payload": payload,
    }


def evaluate_registry_eligibility(
    training_example: dict[str, Any],
    application_result: dict[str, Any],
    hint_package: dict[str, Any],
    active_knowledge: dict[str, Any],
) -> tuple[bool, str]:
    if training_example.get("contract_version") != DAY_TRAINING_EXAMPLE_APPROVAL_V1_CONTRACT:
        return False, REASON_INVALID_TRAINING_EXAMPLE

    if training_example.get("approval_status") != APPROVAL_STATUS_APPROVED:
        return False, REASON_NOT_APPROVED

    if training_example.get("training_use_allowed") is not True:
        return False, REASON_TRAINING_USE_NOT_ALLOWED

    if _mutation_attempt_detected(training_example):
        return False, REASON_MUTATION_ATTEMPT

    if not _has_valid_snapshot_hashes(training_example):
        return False, REASON_MISSING_SNAPSHOT_TRACE

    application_mode = application_result.get("application_mode")
    if isinstance(application_mode, str) and application_mode in FORBIDDEN_APPLICATION_OPERATIONS:
        return False, REASON_FORBIDDEN_OPERATION

    claim = hint_package.get("claim") or active_knowledge.get("claim")
    if isinstance(claim, str) and validate_claim(claim):
        return False, REASON_SENSITIVE_CLAIM

    example_errors = validate_day_training_example_approval_v1(
        training_example,
        application_result=application_result,
        hint_package=hint_package,
    )
    if example_errors:
        return False, REASON_INVALID_TRAINING_EXAMPLE

    app_errors = validate_day_hint_application_result_v1(
        application_result,
        hint_package=hint_package,
    )
    if app_errors:
        return False, REASON_INVALID_APPLICATION

    return True, "eligible"


def try_register_training_example_v1(
    training_example: dict[str, Any],
    application_result: dict[str, Any],
    hint_package: dict[str, Any],
    active_knowledge: dict[str, Any],
    *,
    created_at: str | None = None,
    registry_item_id: str | None = None,
) -> dict[str, Any]:
    """
    P1.27 — register approved training example in dataset registry.

    Approved training example ≠ dataset export. Does not start training.
    """
    if application_result.get("contract_version") != DAY_HINT_APPLICATION_RESULT_V1_CONTRACT:
        return {
            "result": REGISTRY_RESULT_REJECTED,
            "registry_item": None,
            "reasons": ["invalid application result contract_version"],
        }

    if hint_package.get("contract_version") != DAY_ACTIVE_KNOWLEDGE_HINT_PACKAGE_V1_CONTRACT:
        return {
            "result": REGISTRY_RESULT_REJECTED,
            "registry_item": None,
            "reasons": ["invalid hint package contract_version"],
        }

    if active_knowledge.get("contract_version") != DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT:
        return {
            "result": REGISTRY_RESULT_REJECTED,
            "registry_item": None,
            "reasons": ["invalid active knowledge contract_version"],
        }

    if training_example.get("application_id") != application_result.get("application_id"):
        return {
            "result": REGISTRY_RESULT_REJECTED,
            "registry_item": None,
            "reasons": ["application_id mismatch"],
        }

    if training_example.get("hint_package_id") != hint_package.get("hint_package_id"):
        return {
            "result": REGISTRY_RESULT_REJECTED,
            "registry_item": None,
            "reasons": ["hint_package_id mismatch"],
        }

    eligible, reason = evaluate_registry_eligibility(
        training_example,
        application_result,
        hint_package,
        active_knowledge,
    )
    if not eligible:
        return {
            "result": REGISTRY_RESULT_REJECTED,
            "registry_item": None,
            "reasons": [reason],
        }

    hint_type = hint_package.get("hint_type")
    if not isinstance(hint_type, str):
        return {
            "result": REGISTRY_RESULT_REJECTED,
            "registry_item": None,
            "reasons": ["invalid hint_type"],
        }

    dataset_domain = map_hint_type_to_dataset_domain(hint_type)
    example_type = map_hint_type_to_example_type(hint_type)
    if dataset_domain is None or example_type is None:
        return {
            "result": REGISTRY_RESULT_REJECTED,
            "registry_item": None,
            "reasons": ["unsupported hint_type for registry"],
        }

    training_example_id = training_example["training_example_id"]

    registry_item = {
        "contract_version": DAY_TRAINING_DATASET_REGISTRY_ITEM_V1_CONTRACT,
        "registry_item_id": registry_item_id or generate_registry_item_id(),
        "training_example_id": training_example_id,
        "dataset_domain": dataset_domain,
        "dataset_split": DATASET_SPLIT_UNASSIGNED,
        "example_type": example_type,
        "input_snapshot_hash": training_example["input_snapshot_hash"],
        "output_snapshot_hash": training_example["output_snapshot_hash"],
        "quality_evidence_ref": build_evidence_ref(
            training_example_id=training_example_id,
            evidence=training_example.get("quality_evidence"),
            evidence_kind="quality",
        ),
        "reaction_evidence_ref": build_evidence_ref(
            training_example_id=training_example_id,
            evidence=training_example.get("reaction_evidence"),
            evidence_kind="reaction",
        ),
        "source_knowledge_id": training_example.get("knowledge_id"),
        "source_application_id": training_example.get("application_id"),
        "status": REGISTRY_STATUS_REGISTERED,
        "export_allowed": False,
        "training_started": False,
        "created_at": created_at or _utc_now_iso(),
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_model_update_allowed": False,
    }

    errors = validate_day_training_dataset_registry_item_v1(
        registry_item,
        training_example=training_example,
        hint_package=hint_package,
    )
    if errors:
        raise DayTrainingDatasetRegistryError("; ".join(errors))

    return {
        "result": REGISTRY_RESULT_REGISTERED,
        "registry_item": registry_item,
        "reasons": [],
    }


def generate_registry_item_id() -> str:
    return f"treg-{uuid4()}"


def validate_day_training_dataset_registry_item_v1(
    registry_item: dict[str, Any],
    *,
    training_example: dict[str, Any] | None = None,
    hint_package: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if registry_item.get("contract_version") != DAY_TRAINING_DATASET_REGISTRY_ITEM_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in DAY_TRAINING_DATASET_REGISTRY_ITEM_V1_KEYS:
        if key not in registry_item:
            errors.append(f"missing field: {key}")

    if registry_item.get("status") != REGISTRY_STATUS_REGISTERED:
        errors.append("status must be registered")

    if registry_item.get("dataset_split") != DATASET_SPLIT_UNASSIGNED:
        errors.append("dataset_split must be unassigned")

    if registry_item.get("export_allowed") is not False:
        errors.append("export_allowed must be false")

    if registry_item.get("training_started") is not False:
        errors.append("training_started must be false")

    if registry_item.get("profile_update_allowed") is not False:
        errors.append("profile_update_allowed must be false")
    if registry_item.get("memory_update_allowed") is not False:
        errors.append("memory_update_allowed must be false")
    if registry_item.get("ranking_model_update_allowed") is not False:
        errors.append("ranking_model_update_allowed must be false")

    domain = registry_item.get("dataset_domain")
    if domain not in ALLOWED_DATASET_DOMAINS:
        errors.append("invalid dataset_domain")

    example_type = registry_item.get("example_type")
    if example_type not in ALLOWED_EXAMPLE_TYPES:
        errors.append("invalid example_type")

    input_hash = registry_item.get("input_snapshot_hash")
    output_hash = registry_item.get("output_snapshot_hash")
    if not isinstance(input_hash, str) or not input_hash.startswith("snap-"):
        errors.append("input_snapshot_hash required")
    if not isinstance(output_hash, str) or not output_hash.startswith("snap-"):
        errors.append("output_snapshot_hash required")

    if hint_package is not None:
        hint_type = hint_package.get("hint_type")
        if isinstance(hint_type, str):
            expected_domain = map_hint_type_to_dataset_domain(hint_type)
            expected_example = map_hint_type_to_example_type(hint_type)
            if expected_domain and domain != expected_domain:
                errors.append("dataset_domain mismatch for hint_type")
            if expected_example and example_type != expected_example:
                errors.append("example_type mismatch for hint_type")

    if training_example is not None:
        if registry_item.get("training_example_id") != training_example.get(
            "training_example_id"
        ):
            errors.append("training_example_id must match training example")
        if registry_item.get("source_application_id") != training_example.get("application_id"):
            errors.append("source_application_id must match training example")
        if registry_item.get("source_knowledge_id") != training_example.get("knowledge_id"):
            errors.append("source_knowledge_id must match training example")
        if registry_item.get("input_snapshot_hash") != training_example.get(
            "input_snapshot_hash"
        ):
            errors.append("input_snapshot_hash must match training example")
        if registry_item.get("output_snapshot_hash") != training_example.get(
            "output_snapshot_hash"
        ):
            errors.append("output_snapshot_hash must match training example")

    return errors
