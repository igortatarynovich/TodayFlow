"""P1.9 — Safe LLM context slice builder (no prompt, profile, or API call)."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from todayflow_backend.services.day_model_v1_content_evaluator import (
    DAY_CONTENT_PACKAGE_EVALUATION_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_content_renderer import (
    DAY_CONTENT_RENDER_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_llm_call_gate import (
    CONTEXT_DEPTH_MINIMAL,
    CONTEXT_DEPTH_NONE,
    CONTEXT_DEPTH_STANDARD,
    DECISION_CALL_LLM,
)
from todayflow_backend.services.day_model_v1_llm_request_record import (
    DAY_LLM_PRECALL_RECORD_V1_CONTRACT,
)

DAY_LLM_CONTEXT_SLICE_V1_CONTRACT = "day_llm_context_slice_v1"

CONTEXT_SLICE_STATUS_READY = "ready"

ALLOWED_CONTEXT_DEPTHS = frozenset(
    {CONTEXT_DEPTH_NONE, CONTEXT_DEPTH_MINIMAL, CONTEXT_DEPTH_STANDARD}
)

ALLOWED_OPERATIONS = frozenset({"rewrite", "shorten", "connect", "soften"})

FORBIDDEN_OPERATIONS = frozenset(
    {
        "invent",
        "diagnose",
        "add_astrology",
        "add_tarot",
        "add_numerology",
    }
)

FORBIDDEN_USER_DATA_KEYS = frozenset(
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
    }
)

SURFACE_PURPOSES = {
    "today_hero": "Short hero line refinement only",
    "day_guidance_card": "Connect guidance fragments into readable flow",
    "risk_card": "Soften risk warning without adding new risks",
    "action_card": "Clarify action hint without new instructions",
    "tempo_card": "Clarify tempo hint without changing pace class",
    "reflection_card": "Soften reflection hint without new questions",
}

MAX_SAFE_PERSONALIZATION_FACTS = 5

SURFACE_MAX_CHARS = {
    "today_hero": 120,
    "day_guidance_card": 480,
    "risk_card": 160,
    "action_card": 160,
    "tempo_card": 160,
    "reflection_card": 200,
}

DAY_LLM_CONTEXT_SLICE_V1_KEYS = frozenset(
    {
        "contract_version",
        "context_slice_id",
        "generation_id",
        "surface",
        "context_depth",
        "render_surface",
        "evaluation_summary",
        "constraints",
        "allowed_operations",
        "forbidden_operations",
        "source_keys",
        "traceability",
        "surface_context",
        "status",
    }
)


class DayModelContextSliceError(ValueError):
    """Raised when context slice inputs or payload are invalid."""


def derive_context_slice_id(
    generation_id: str,
    surface: str,
    context_depth: str,
) -> str:
    payload = f"{generation_id}:{surface}:{context_depth}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"ctx-{digest}"


def _require_precall_call_llm(precall_record: dict[str, Any]) -> dict[str, Any]:
    if precall_record.get("contract_version") != DAY_LLM_PRECALL_RECORD_V1_CONTRACT:
        raise DayModelContextSliceError("precall_record has invalid contract_version")
    gate = precall_record.get("gate_decision")
    if not isinstance(gate, dict) or gate.get("decision") != DECISION_CALL_LLM:
        raise DayModelContextSliceError(
            "context slice is only created when precall gate decision is call_llm"
        )
    return gate


def _require_render_evaluation(
    render: dict[str, Any],
    evaluation: dict[str, Any],
) -> None:
    if render.get("contract_version") != DAY_CONTENT_RENDER_V1_CONTRACT:
        raise DayModelContextSliceError("render has invalid contract_version")
    if evaluation.get("contract_version") != DAY_CONTENT_PACKAGE_EVALUATION_V1_CONTRACT:
        raise DayModelContextSliceError("evaluation has invalid contract_version")
    if not render.get("renderable", False):
        raise DayModelContextSliceError("render must be renderable for context slice")


def _extract_render_surface(render: dict[str, Any], surface: str) -> dict[str, Any]:
    surfaces = render.get("surfaces") or {}
    target = surfaces.get(surface)
    if not target:
        raise DayModelContextSliceError(f"render missing target surface: {surface!r}")
    return dict(target)


def _collect_source_keys(render_surface: dict[str, Any]) -> list[str]:
    keys: list[str] = []
    for entry in render_surface.get("entries", []):
        if isinstance(entry, dict) and entry.get("key"):
            keys.append(str(entry["key"]))
    return keys


def _dominant_tone(render_surface: dict[str, Any]) -> str:
    tones = [
        str(entry.get("tone"))
        for entry in render_surface.get("entries", [])
        if isinstance(entry, dict) and entry.get("tone")
    ]
    if not tones:
        return "neutral"
    return max(set(tones), key=tones.count)


def _evaluation_summary(evaluation: dict[str, Any], render: dict[str, Any]) -> dict[str, Any]:
    metadata = render.get("metadata") or {}
    interpretation = metadata.get("interpretation") or {}
    confidence = interpretation.get("confidence", evaluation.get("confidence_score"))
    return {
        "recommendation": evaluation.get("recommendation"),
        "issues": list(evaluation.get("issues", [])),
        "confidence": confidence,
        "score": evaluation.get("score"),
        "degraded": bool(evaluation.get("degraded", False)),
    }


def _build_constraints(
    *,
    surface: str,
    render_surface: dict[str, Any],
    context_depth: str,
    gate_decision: dict[str, Any],
) -> dict[str, Any]:
    tone = _dominant_tone(render_surface)
    if context_depth in {CONTEXT_DEPTH_NONE, CONTEXT_DEPTH_MINIMAL} or render_surface.get(
        "degraded", False
    ):
        tone = "soft" if tone == "direct" else tone
    return {
        "max_length_chars": SURFACE_MAX_CHARS.get(surface, 240),
        "max_tokens_hint": gate_decision.get("max_tokens"),
        "tone": tone,
        "no_new_claims": True,
        "preserve_source_keys": True,
        "preserve_recommendation": True,
    }


def _build_surface_context(
    *,
    context_depth: str,
    surface: str,
    render_surface: dict[str, Any],
    evaluation: dict[str, Any],
    safe_personalization_summary: list[str] | None,
) -> dict[str, Any]:
    if context_depth == CONTEXT_DEPTH_NONE:
        return {}

    purpose = SURFACE_PURPOSES.get(surface, "Refine deterministic surface text")
    tone_preference = _dominant_tone(render_surface)
    caution_flags = [
        issue for issue in evaluation.get("issues", []) if str(issue).startswith("E-")
    ]
    if evaluation.get("degraded"):
        caution_flags.append("evaluation_degraded")
    if render_surface.get("degraded"):
        caution_flags.append("render_degraded")

    minimal = {
        "surface_purpose": purpose,
        "tone_preference": tone_preference,
        "caution_flags": sorted(set(caution_flags)),
    }

    if context_depth == CONTEXT_DEPTH_MINIMAL:
        return minimal

    facts = list(safe_personalization_summary or [])[:MAX_SAFE_PERSONALIZATION_FACTS]
    return {
        **minimal,
        "safe_personalization_summary": facts,
    }

def _scan_forbidden_user_data(payload: Any, path: str = "") -> list[str]:
    violations: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            key_lower = str(key).lower()
            if key_lower in FORBIDDEN_USER_DATA_KEYS or "coreprofile" in key_lower.replace("_", ""):
                violations.append(f"{path}.{key}" if path else key)
            violations.extend(_scan_forbidden_user_data(value, f"{path}.{key}" if path else key))
    elif isinstance(payload, list):
        for index, item in enumerate(payload):
            violations.extend(_scan_forbidden_user_data(item, f"{path}[{index}]"))
    return violations


def maybe_build_llm_context_slice_v1(
    precall_record: dict[str, Any] | None,
    render: dict[str, Any],
    evaluation: dict[str, Any],
    *,
    surface: str,
    context_depth: str | None = None,
    safe_personalization_summary: list[str] | None = None,
    day_context_layers: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Return context slice for call_llm precall, else None."""
    if precall_record is None:
        return None
    gate = precall_record.get("gate_decision") or {}
    if gate.get("decision") != DECISION_CALL_LLM:
        return None

    resolved_summary = safe_personalization_summary
    personalization_usage_gate = None
    if resolved_summary is None and day_context_layers is not None:
        from todayflow_backend.services.day_model_v1_personalization_usage_gate import (
            resolve_safe_personalization_for_context_slice,
        )

        resolved_summary, personalization_usage_gate = (
            resolve_safe_personalization_for_context_slice(
                surface=surface,
                llm_gate_decision=gate,
                day_context_layers=day_context_layers,
            )
        )

    context_slice = build_llm_context_slice_v1(
        precall_record,
        render,
        evaluation,
        surface=surface,
        context_depth=context_depth,
        safe_personalization_summary=resolved_summary,
    )

    if personalization_usage_gate is not None:
        trace = dict(context_slice.get("traceability") or {})
        trace["personalization_usage_gate_id"] = personalization_usage_gate.get(
            "usage_gate_id"
        )
        trace["personalization_gate_decision"] = personalization_usage_gate.get(
            "decision"
        )
        context_slice["traceability"] = trace

    if day_context_layers is not None and isinstance(
        day_context_layers.get("knowledge_usage_metrics_trace"), dict
    ):
        from todayflow_backend.services.day_model_v1_knowledge_usage_metrics import (
            enrich_knowledge_usage_metrics_with_p19_context_slice,
        )

        gate = precall_record.get("gate_decision") or {}
        day_context_layers["knowledge_usage_metrics_trace"] = (
            enrich_knowledge_usage_metrics_with_p19_context_slice(
                day_context_layers["knowledge_usage_metrics_trace"],
                context_slice,
                usage_gate=personalization_usage_gate,
                llm_gate_context_depth=gate.get("allowed_context_depth"),
            )
        )

    return context_slice


def build_llm_context_slice_v1(
    precall_record: dict[str, Any],
    render: dict[str, Any],
    evaluation: dict[str, Any],
    *,
    surface: str,
    context_depth: str | None = None,
    safe_personalization_summary: list[str] | None = None,
) -> dict[str, Any]:
    """
    P1.9 — build safe context slice for LLM refinement.

    No prompt, API call, profile/memory reads, or reference catalog access.
    """
    gate_decision = _require_precall_call_llm(precall_record)
    _require_render_evaluation(render, evaluation)

    if precall_record.get("surface") != surface:
        raise DayModelContextSliceError(
            f"precall surface {precall_record.get('surface')!r} != requested {surface!r}"
        )
    if gate_decision.get("surface") != surface:
        raise DayModelContextSliceError("precall gate surface mismatch")

    depth = context_depth or gate_decision.get("allowed_context_depth", CONTEXT_DEPTH_NONE)
    if depth not in ALLOWED_CONTEXT_DEPTHS:
        raise DayModelContextSliceError(f"invalid context_depth: {depth!r}")

    for trace_field in ("render_id", "package_id", "evaluation_id", "generation_id"):
        if not precall_record.get(trace_field):
            raise DayModelContextSliceError(f"precall_record missing {trace_field}")

    if safe_personalization_summary is not None:
        if len(safe_personalization_summary) > MAX_SAFE_PERSONALIZATION_FACTS:
            raise DayModelContextSliceError(
                f"safe_personalization_summary max {MAX_SAFE_PERSONALIZATION_FACTS} facts"
            )
        if depth != CONTEXT_DEPTH_STANDARD:
            raise DayModelContextSliceError(
                "safe_personalization_summary only allowed for standard context_depth"
            )
    elif depth == CONTEXT_DEPTH_STANDARD:
        safe_personalization_summary = []

    render_surface = _extract_render_surface(render, surface)
    source_keys = _collect_source_keys(render_surface)
    slice_id = precall_record.get("context_slice_id") or derive_context_slice_id(
        precall_record["generation_id"],
        surface,
        depth,
    )

    surface_context = _build_surface_context(
        context_depth=depth,
        surface=surface,
        render_surface=render_surface,
        evaluation=evaluation,
        safe_personalization_summary=safe_personalization_summary,
    )

    context_slice = {
        "contract_version": DAY_LLM_CONTEXT_SLICE_V1_CONTRACT,
        "context_slice_id": slice_id,
        "generation_id": precall_record["generation_id"],
        "surface": surface,
        "context_depth": depth,
        "render_surface": render_surface,
        "evaluation_summary": _evaluation_summary(evaluation, render),
        "constraints": _build_constraints(
            surface=surface,
            render_surface=render_surface,
            context_depth=depth,
            gate_decision=gate_decision,
        ),
        "allowed_operations": sorted(ALLOWED_OPERATIONS),
        "forbidden_operations": sorted(FORBIDDEN_OPERATIONS),
        "source_keys": source_keys,
        "traceability": {
            "render_id": precall_record["render_id"],
            "package_id": precall_record["package_id"],
            "evaluation_id": precall_record["evaluation_id"],
        },
        "surface_context": surface_context,
        "status": CONTEXT_SLICE_STATUS_READY,
    }

    errors = validate_llm_context_slice_v1(context_slice)
    if errors:
        raise DayModelContextSliceError("; ".join(errors))
    return context_slice


def validate_llm_context_slice_v1(context_slice: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if context_slice.get("contract_version") != DAY_LLM_CONTEXT_SLICE_V1_CONTRACT:
        errors.append("invalid contract_version")
    for key in DAY_LLM_CONTEXT_SLICE_V1_KEYS:
        if key not in context_slice:
            errors.append(f"missing field: {key}")

    depth = context_slice.get("context_depth")
    surface_context = context_slice.get("surface_context") or {}

    if depth == CONTEXT_DEPTH_NONE:
        if surface_context.get("safe_personalization_summary"):
            errors.append("none depth must not include safe_personalization_summary")
        if surface_context.get("surface_purpose"):
            errors.append("none depth must not include surface_purpose")
    elif depth == CONTEXT_DEPTH_MINIMAL:
        if "safe_personalization_summary" in surface_context:
            errors.append("minimal depth must not include safe_personalization_summary")
        if not surface_context.get("surface_purpose"):
            errors.append("minimal depth requires surface_purpose")
    elif depth == CONTEXT_DEPTH_STANDARD:
        if "safe_personalization_summary" not in surface_context:
            errors.append("standard depth requires safe_personalization_summary key")
        facts = surface_context.get("safe_personalization_summary")
        if facts is not None and len(facts) > MAX_SAFE_PERSONALIZATION_FACTS:
            errors.append("too many safe_personalization_summary facts")

    forbidden_ops = set(context_slice.get("forbidden_operations") or [])
    if not FORBIDDEN_OPERATIONS.issubset(forbidden_ops):
        errors.append("forbidden_operations incomplete")

    if not context_slice.get("source_keys"):
        errors.append("source_keys required")

    trace = context_slice.get("traceability") or {}
    for field in ("render_id", "package_id", "evaluation_id"):
        if not trace.get(field):
            errors.append(f"traceability.{field} required")

    if context_slice.get("status") != CONTEXT_SLICE_STATUS_READY:
        errors.append("status must be ready")

    errors.extend(_scan_forbidden_user_data(context_slice))

    return errors
