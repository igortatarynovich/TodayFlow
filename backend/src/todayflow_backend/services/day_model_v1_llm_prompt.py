"""P1.10 — LLM prompt builder from context slice (no API call, provider, or profile reads)."""

from __future__ import annotations

import hashlib
from typing import Any

from todayflow_backend.data.day_llm_prompt_template_loader import get_prompt_template
from todayflow_backend.services.day_model_v1_llm_context_slice import (
    DAY_LLM_CONTEXT_SLICE_V1_CONTRACT,
    CONTEXT_SLICE_STATUS_READY,
    validate_llm_context_slice_v1,
)

DAY_LLM_PROMPT_V1_CONTRACT = "day_llm_prompt_v1"

DAY_LLM_PROMPT_V1_KEYS = frozenset(
    {
        "contract_version",
        "prompt_id",
        "generation_id",
        "template_id",
        "template_version",
        "system_instructions",
        "task_instructions",
        "input_payload",
        "output_schema",
        "constraints",
        "max_tokens",
        "traceability",
    }
)

PROMPT_ALLOWED_OPERATIONS = frozenset(
    {"shorten", "connect", "soften", "improve_readability", "remove_repetition"}
)

PROMPT_FORBIDDEN_OPERATIONS = frozenset(
    {
        "invent",
        "change_strategy",
        "change_risk",
        "change_tempo",
        "add_astrology",
        "add_tarot",
        "add_numerology",
        "add_personal_claims",
        "diagnose",
        "promise_outcome",
    }
)

FORBIDDEN_PROMPT_DATA_KEYS = frozenset(
    {
        "core_profile",
        "profile",
        "user_profile",
        "behavior_logs",
        "raw_events",
        "event_history",
        "memory_dump",
        "birth_data",
        "full_history",
        "content_package",
        "day_content_package",
        "surfaces",
    }
)

LLM_RESPONSE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["refined_text", "changed", "source_keys_used", "warnings"],
    "properties": {
        "refined_text": {
            "type": "string",
            "description": "Final short refined text for the target surface",
        },
        "changed": {
            "type": "boolean",
            "description": "True if text was modified from deterministic input",
        },
        "source_keys_used": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Subset of allowed source keys referenced in refinement",
        },
        "warnings": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Non-fatal issues if refinement could not fully comply",
        },
    },
}


class DayModelLlmPromptError(ValueError):
    """Raised when prompt inputs or payload are invalid."""


def derive_prompt_id(
    generation_id: str,
    template_id: str,
    context_slice_id: str,
) -> str:
    payload = f"{generation_id}:{template_id}:{context_slice_id}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"prompt-{digest}"


def _require_valid_context_slice(context_slice: dict[str, Any]) -> None:
    if context_slice.get("contract_version") != DAY_LLM_CONTEXT_SLICE_V1_CONTRACT:
        raise DayModelLlmPromptError("context_slice has invalid contract_version")
    if context_slice.get("status") != CONTEXT_SLICE_STATUS_READY:
        raise DayModelLlmPromptError("context_slice must have status ready")
    errors = validate_llm_context_slice_v1(context_slice)
    if errors:
        raise DayModelLlmPromptError("; ".join(errors))


def _require_template_surface_match(template: dict[str, Any], surface: str) -> None:
    if template.get("surface") != surface:
        raise DayModelLlmPromptError(
            f"template surface {template.get('surface')!r} != context slice surface {surface!r}"
        )
    if template.get("status") != "active":
        raise DayModelLlmPromptError(
            f"prompt template {template.get('template_id')!r} is not active"
        )


def _build_fragments(render_surface: dict[str, Any]) -> list[dict[str, str]]:
    fragments: list[dict[str, str]] = []
    for entry in render_surface.get("entries", []):
        if not isinstance(entry, dict):
            continue
        key = entry.get("key")
        text = entry.get("display_text") or entry.get("text_short") or entry.get("text_medium")
        if key and text:
            fragments.append({"key": str(key), "text": str(text)})
    return fragments


def _build_input_payload(context_slice: dict[str, Any]) -> dict[str, Any]:
    render_surface = context_slice.get("render_surface") or {}
    payload: dict[str, Any] = {
        "surface": context_slice["surface"],
        "context_depth": context_slice["context_depth"],
        "fragments": _build_fragments(render_surface),
        "source_keys": list(context_slice.get("source_keys") or []),
    }
    surface_context = context_slice.get("surface_context") or {}
    if surface_context:
        payload["surface_context"] = dict(surface_context)

    evaluation_summary = context_slice.get("evaluation_summary") or {}
    payload["evaluation_hint"] = {
        "recommendation": evaluation_summary.get("recommendation"),
        "issues": list(evaluation_summary.get("issues") or []),
        "confidence": evaluation_summary.get("confidence"),
    }
    return payload


def _build_constraints(context_slice: dict[str, Any]) -> dict[str, Any]:
    slice_constraints = dict(context_slice.get("constraints") or {})
    return {
        **slice_constraints,
        "allowed_operations": sorted(PROMPT_ALLOWED_OPERATIONS),
        "forbidden_operations": sorted(PROMPT_FORBIDDEN_OPERATIONS),
        "preserve_source_keys": True,
        "preserve_recommendation": True,
        "structured_output_required": True,
    }


def _resolve_max_tokens(context_slice: dict[str, Any]) -> int:
    constraints = context_slice.get("constraints") or {}
    hint = constraints.get("max_tokens_hint")
    if isinstance(hint, int) and hint > 0:
        return hint
    return 128


def _scan_forbidden_prompt_data(payload: Any, path: str = "") -> list[str]:
    violations: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            key_lower = str(key).lower()
            if key_lower in FORBIDDEN_PROMPT_DATA_KEYS or "coreprofile" in key_lower.replace(
                "_", ""
            ):
                violations.append(f"{path}.{key}" if path else key)
            violations.extend(_scan_forbidden_prompt_data(value, f"{path}.{key}" if path else key))
    elif isinstance(payload, list):
        for index, item in enumerate(payload):
            violations.extend(_scan_forbidden_prompt_data(item, f"{path}[{index}]"))
    return violations


def build_day_llm_prompt_v1(
    context_slice: dict[str, Any],
    template_id: str,
    *,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    P1.10 — build LLM prompt from validated context slice and registry template.

    No LLM call, provider selection, profile/memory reads, or full package embedding.
    """
    _require_valid_context_slice(context_slice)
    if not template_id or not str(template_id).strip():
        raise DayModelLlmPromptError("template_id is required")

    surface = context_slice["surface"]
    template = get_prompt_template(template_id, registry=registry)
    _require_template_surface_match(template, surface)

    generation_id = context_slice["generation_id"]
    context_slice_id = context_slice["context_slice_id"]
    trace = context_slice.get("traceability") or {}

    prompt = {
        "contract_version": DAY_LLM_PROMPT_V1_CONTRACT,
        "prompt_id": derive_prompt_id(generation_id, template_id, context_slice_id),
        "generation_id": generation_id,
        "template_id": template_id,
        "template_version": template["template_version"],
        "system_instructions": template["system_instructions"],
        "task_instructions": template["task_instructions"],
        "input_payload": _build_input_payload(context_slice),
        "output_schema": dict(LLM_RESPONSE_OUTPUT_SCHEMA),
        "constraints": _build_constraints(context_slice),
        "max_tokens": _resolve_max_tokens(context_slice),
        "traceability": {
            "context_slice_id": context_slice_id,
            "render_id": trace.get("render_id"),
            "package_id": trace.get("package_id"),
            "evaluation_id": trace.get("evaluation_id"),
        },
    }

    errors = validate_day_llm_prompt_v1(prompt, context_slice=context_slice)
    if errors:
        raise DayModelLlmPromptError("; ".join(errors))
    return prompt


def validate_day_llm_prompt_v1(
    prompt: dict[str, Any],
    *,
    context_slice: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if prompt.get("contract_version") != DAY_LLM_PROMPT_V1_CONTRACT:
        errors.append("invalid contract_version")
    for key in DAY_LLM_PROMPT_V1_KEYS:
        if key not in prompt:
            errors.append(f"missing field: {key}")

    if not prompt.get("generation_id"):
        errors.append("generation_id required")
    if not prompt.get("prompt_id"):
        errors.append("prompt_id required")

    forbidden_ops = set((prompt.get("constraints") or {}).get("forbidden_operations") or [])
    if not PROMPT_FORBIDDEN_OPERATIONS.issubset(forbidden_ops):
        errors.append("forbidden_operations incomplete")

    output_schema = prompt.get("output_schema")
    if not isinstance(output_schema, dict):
        errors.append("output_schema must be object")
    else:
        required = set(output_schema.get("required") or [])
        for field in ("refined_text", "changed", "source_keys_used", "warnings"):
            if field not in required:
                errors.append(f"output_schema missing required field: {field}")

    input_payload = prompt.get("input_payload") or {}
    source_keys = input_payload.get("source_keys")
    if not source_keys:
        errors.append("input_payload.source_keys required")
    if "surfaces" in input_payload or "content_package" in input_payload:
        errors.append("input_payload must not embed full package or all surfaces")

    if context_slice is not None:
        if prompt.get("generation_id") != context_slice.get("generation_id"):
            errors.append("generation_id must match context_slice")
        slice_keys = context_slice.get("source_keys") or []
        payload_keys = input_payload.get("source_keys") or []
        if payload_keys != slice_keys:
            errors.append("input_payload.source_keys must match context_slice.source_keys")

    trace = prompt.get("traceability") or {}
    for field in ("context_slice_id", "render_id", "package_id", "evaluation_id"):
        if not trace.get(field):
            errors.append(f"traceability.{field} required")

    max_tokens = prompt.get("max_tokens")
    if not isinstance(max_tokens, int) or max_tokens <= 0:
        errors.append("max_tokens must be positive int")

    errors.extend(_scan_forbidden_prompt_data(prompt))
    return errors
