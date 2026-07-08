"""P1.8 — LLM request record contract (pre/post call builders and validators)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.day_model_v1_llm_call_gate import (
    DAY_CONTENT_LLM_GATE_V1_CONTRACT,
    DECISION_CALL_LLM,
)

DAY_LLM_PRECALL_RECORD_V1_CONTRACT = "day_llm_precall_record_v1"
DAY_LLM_POSTCALL_RECORD_V1_CONTRACT = "day_llm_postcall_record_v1"

PRECALL_STATUS_PENDING = "pending"
POSTCALL_STATUS_COMPLETED = "completed"
POSTCALL_STATUS_FAILED = "failed"

FINISH_REASON_VALUES = frozenset({"stop", "length", "error"})

DAY_LLM_PRECALL_RECORD_V1_KEYS = frozenset(
    {
        "contract_version",
        "generation_id",
        "surface",
        "gate_decision",
        "render_id",
        "package_id",
        "evaluation_id",
        "context_slice_id",
        "prompt_template_id",
        "prompt_version",
        "model_tier_allowed",
        "max_tokens",
        "save_required",
        "dataset_candidate",
        "status",
        "created_at",
    }
)

DAY_LLM_POSTCALL_RECORD_V1_KEYS = frozenset(
    {
        "contract_version",
        "generation_id",
        "provider",
        "model",
        "input_tokens",
        "output_tokens",
        "cost_estimate",
        "raw_response",
        "parsed_response",
        "finish_reason",
        "error",
        "status",
        "created_at",
        "llm_response_evaluation_id",
        "quality_score",
        "safety_flags",
        "used_in_ui",
    }
)


class DayModelLlmRecordError(ValueError):
    """Raised when record inputs or payloads are invalid."""


def generate_generation_id() -> str:
    return str(uuid4())


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _require_call_llm_gate(gate_decision: dict[str, Any]) -> None:
    if gate_decision.get("contract_version") != DAY_CONTENT_LLM_GATE_V1_CONTRACT:
        raise DayModelLlmRecordError(
            f"expected gate contract_version={DAY_CONTENT_LLM_GATE_V1_CONTRACT!r}, "
            f"got {gate_decision.get('contract_version')!r}"
        )
    if gate_decision.get("decision") != DECISION_CALL_LLM:
        raise DayModelLlmRecordError(
            "LLM request record is only created when gate decision is call_llm"
        )
    if not gate_decision.get("save_required", False):
        raise DayModelLlmRecordError("call_llm gate decision must have save_required=true")
    if not gate_decision.get("dataset_candidate", False):
        raise DayModelLlmRecordError("call_llm gate decision must have dataset_candidate=true")


def maybe_build_llm_precall_record_v1(
    gate_decision: dict[str, Any],
    *,
    generation_id: str,
    surface: str,
    render_id: str,
    package_id: str,
    evaluation_id: str,
    context_slice_id: str,
    prompt_template_id: str | None = None,
    prompt_version: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any] | None:
    """Return pre-call record for call_llm, else None (no record for no_call/blocked)."""
    if gate_decision.get("decision") != DECISION_CALL_LLM:
        return None
    return build_llm_precall_record_v1(
        gate_decision,
        generation_id=generation_id,
        surface=surface,
        render_id=render_id,
        package_id=package_id,
        evaluation_id=evaluation_id,
        context_slice_id=context_slice_id,
        prompt_template_id=prompt_template_id,
        prompt_version=prompt_version,
        created_at=created_at,
    )


def build_llm_precall_record_v1(
    gate_decision: dict[str, Any],
    *,
    generation_id: str,
    surface: str,
    render_id: str,
    package_id: str,
    evaluation_id: str,
    context_slice_id: str,
    prompt_template_id: str | None = None,
    prompt_version: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """
    P1.8 — build pre-call record before external LLM API.

    No prompt, provider selection, profile/memory, or API call.
    """
    _require_call_llm_gate(gate_decision)
    if gate_decision.get("surface") != surface:
        raise DayModelLlmRecordError(
            f"gate surface {gate_decision.get('surface')!r} != requested surface {surface!r}"
        )
    if not generation_id or not str(generation_id).strip():
        raise DayModelLlmRecordError("generation_id is required")

    max_tokens = gate_decision.get("max_tokens")
    if not isinstance(max_tokens, int) or max_tokens <= 0:
        raise DayModelLlmRecordError("call_llm gate decision must include max_tokens > 0")

    record = {
        "contract_version": DAY_LLM_PRECALL_RECORD_V1_CONTRACT,
        "generation_id": str(generation_id),
        "surface": surface,
        "gate_decision": dict(gate_decision),
        "render_id": render_id,
        "package_id": package_id,
        "evaluation_id": evaluation_id,
        "context_slice_id": context_slice_id,
        "prompt_template_id": prompt_template_id,
        "prompt_version": prompt_version,
        "model_tier_allowed": gate_decision.get("allowed_model_tier"),
        "max_tokens": max_tokens,
        "save_required": True,
        "dataset_candidate": True,
        "status": PRECALL_STATUS_PENDING,
        "created_at": created_at or _utc_now_iso(),
    }
    errors = validate_llm_precall_record_v1(record)
    if errors:
        raise DayModelLlmRecordError("; ".join(errors))
    return record


def build_llm_postcall_record_v1(
    precall_record: dict[str, Any],
    *,
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cost_estimate: float,
    raw_response: str,
    parsed_response: dict[str, Any] | list[Any] | str,
    finish_reason: str,
    status: str,
    error: str | None = None,
    created_at: str | None = None,
    llm_response_evaluation_id: str | None = None,
    quality_score: float | None = None,
    safety_flags: list[str] | None = None,
    used_in_ui: bool | None = None,
) -> dict[str, Any]:
    """
    P1.8 — build post-call record after external LLM API (builder only, no API here).
    """
    if precall_record.get("contract_version") != DAY_LLM_PRECALL_RECORD_V1_CONTRACT:
        raise DayModelLlmRecordError("precall_record has invalid contract_version")
    if status not in {POSTCALL_STATUS_COMPLETED, POSTCALL_STATUS_FAILED}:
        raise DayModelLlmRecordError(f"invalid post-call status: {status!r}")
    if finish_reason not in FINISH_REASON_VALUES:
        raise DayModelLlmRecordError(f"invalid finish_reason: {finish_reason!r}")
    if status == POSTCALL_STATUS_FAILED and not error:
        raise DayModelLlmRecordError("failed post-call record requires error")

    record = {
        "contract_version": DAY_LLM_POSTCALL_RECORD_V1_CONTRACT,
        "generation_id": precall_record["generation_id"],
        "provider": provider,
        "model": model,
        "input_tokens": int(input_tokens),
        "output_tokens": int(output_tokens),
        "cost_estimate": float(cost_estimate),
        "raw_response": raw_response,
        "parsed_response": parsed_response,
        "finish_reason": finish_reason,
        "error": error,
        "status": status,
        "created_at": created_at or _utc_now_iso(),
        "llm_response_evaluation_id": llm_response_evaluation_id,
        "quality_score": quality_score,
        "safety_flags": list(safety_flags) if safety_flags is not None else None,
        "used_in_ui": used_in_ui,
    }
    errors = validate_llm_postcall_record_v1(record, precall_record=precall_record)
    if errors:
        raise DayModelLlmRecordError("; ".join(errors))
    return record


def validate_llm_precall_record_v1(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if record.get("contract_version") != DAY_LLM_PRECALL_RECORD_V1_CONTRACT:
        errors.append("invalid contract_version")
    for key in DAY_LLM_PRECALL_RECORD_V1_KEYS:
        if key not in record:
            errors.append(f"missing field: {key}")
    if not record.get("generation_id"):
        errors.append("generation_id required")
    gate = record.get("gate_decision")
    if not isinstance(gate, dict):
        errors.append("gate_decision must be object")
    elif gate.get("decision") != DECISION_CALL_LLM:
        errors.append("gate_decision.decision must be call_llm")
    if record.get("save_required") is not True:
        errors.append("save_required must be true")
    if record.get("dataset_candidate") is not True:
        errors.append("dataset_candidate must be true")
    if record.get("status") != PRECALL_STATUS_PENDING:
        errors.append("status must be pending")
    max_tokens = record.get("max_tokens")
    if not isinstance(max_tokens, int) or max_tokens <= 0:
        errors.append("max_tokens must be positive int")
    return errors


def validate_llm_postcall_record_v1(
    record: dict[str, Any],
    *,
    precall_record: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if record.get("contract_version") != DAY_LLM_POSTCALL_RECORD_V1_CONTRACT:
        errors.append("invalid contract_version")
    for key in DAY_LLM_POSTCALL_RECORD_V1_KEYS:
        if key not in record:
            errors.append(f"missing field: {key}")
    if not record.get("generation_id"):
        errors.append("generation_id required")
    if precall_record is not None and record.get("generation_id") != precall_record.get(
        "generation_id"
    ):
        errors.append("generation_id must match precall record")
    if record.get("status") == POSTCALL_STATUS_FAILED and not record.get("error"):
        errors.append("failed status requires error")
    finish_reason = record.get("finish_reason")
    if finish_reason not in FINISH_REASON_VALUES:
        errors.append("invalid finish_reason")
    if not record.get("created_at"):
        errors.append("created_at required")
    return errors
