"""B1.8 — Evolution → LLM Gate wiring (B1.7 llm_gate slice as cap layer)."""

from __future__ import annotations

import copy
from typing import Any

from todayflow_backend.services.day_model_v1_llm_call_gate import (
    CONTEXT_DEPTH_MINIMAL,
    CONTEXT_DEPTH_NONE,
    CONTEXT_DEPTH_STANDARD,
    DAY_CONTENT_LLM_GATE_V1_CONTRACT,
    DAY_CONTENT_LLM_GATE_V1_KEYS,
    DECISION_CALL_LLM,
    DECISION_NO_CALL,
    MODEL_TIER_CHEAP,
    MODEL_TIER_NONE,
    MODEL_TIER_STANDARD,
    decide_day_content_llm_call_v1,
)
from todayflow_backend.services.evolution_effect_consumer_map_v1 import (
    CONSUMER_LLM_GATE,
    EVOLUTION_EFFECT_CONSUMER_SLICE_V1_CONTRACT,
    validate_evolution_effect_consumer_slice_v1,
)
from todayflow_backend.services.evolution_effect_runtime_policy_v1 import (
    EVOLUTION_EFFECT_RUNTIME_POLICY_V1_CONTRACT,
)

EVOLUTION_LLM_GATE_WIRING_V1_VERSION = "1.0.0"

EVOLUTION_LLM_GATE_TRACE_KEYS = frozenset(
    {
        "evolution_slice_applied",
        "evolution_context_depth_cap",
        "evolution_model_tier_cap",
        "evolution_token_cap",
        "cap_reason",
        "blocked_escalations",
    }
)

DAY_CONTENT_LLM_GATE_V1_WITH_EVOLUTION_KEYS = (
    DAY_CONTENT_LLM_GATE_V1_KEYS | EVOLUTION_LLM_GATE_TRACE_KEYS
)

CONTEXT_DEPTH_ORDER = {
    CONTEXT_DEPTH_NONE: 0,
    CONTEXT_DEPTH_MINIMAL: 1,
    CONTEXT_DEPTH_STANDARD: 2,
}

MODEL_TIER_ORDER = {
    MODEL_TIER_NONE: 0,
    MODEL_TIER_CHEAP: 1,
    MODEL_TIER_STANDARD: 2,
}

MAX_TOKENS_BY_CAP_LABEL = {
    "low": 128,
    "medium": 256,
    "high": 512,
}

LLM_BUDGET_TIER_ORDER = {
    "none": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
}


class EvolutionLlmGateWiringError(ValueError):
    """Raised when LLM gate wiring inputs are invalid."""


def _default_evolution_trace(*, applied: bool = False, cap_reason: str | None = None) -> dict[str, Any]:
    return {
        "evolution_slice_applied": applied,
        "evolution_context_depth_cap": None,
        "evolution_model_tier_cap": None,
        "evolution_token_cap": None,
        "cap_reason": cap_reason,
        "blocked_escalations": [],
    }


def _is_valid_llm_gate_slice(evolution_slice: dict[str, Any]) -> tuple[bool, str | None]:
    if evolution_slice.get("contract_version") == EVOLUTION_EFFECT_RUNTIME_POLICY_V1_CONTRACT:
        return False, "full_policy_not_accepted"
    if evolution_slice.get("contract_version") != EVOLUTION_EFFECT_CONSUMER_SLICE_V1_CONTRACT:
        return False, "invalid_slice_contract"
    if evolution_slice.get("consumer_id") != CONSUMER_LLM_GATE:
        return False, "invalid_consumer_id"
    errors = validate_evolution_effect_consumer_slice_v1(
        evolution_slice,
        consumer_id=CONSUMER_LLM_GATE,
    )
    if errors:
        return False, "invalid_slice_payload"
    return True, None


def resolve_evolution_llm_caps_from_slice_v1(
    evolution_slice: dict[str, Any],
) -> dict[str, Any]:
    """Resolve evolution caps for LLM gate from a validated llm_gate consumer slice."""
    valid, reason = _is_valid_llm_gate_slice(evolution_slice)
    if not valid:
        raise EvolutionLlmGateWiringError(reason or "invalid evolution slice")

    limits = evolution_slice.get("effect_limits") or {}
    engine = (evolution_slice.get("allowed_effects") or {}).get("engine_effects") or {}

    llm_budget_tier = limits.get("llm_budget_tier") or engine.get("llm_budget_tier") or "none"
    max_context_lines = limits.get("max_context_lines")
    if max_context_lines is None:
        max_context_lines = engine.get("max_context_lines", 0)
    llm_model_tier = limits.get("llm_model_tier") or engine.get("llm_model_tier") or "cheap"
    token_cap_label = limits.get("max_tokens_cap") or engine.get("max_tokens_cap") or "low"

    if llm_budget_tier == "none" or int(max_context_lines) <= 0:
        context_depth_cap = CONTEXT_DEPTH_NONE
    elif int(max_context_lines) <= 2:
        context_depth_cap = CONTEXT_DEPTH_MINIMAL
    else:
        context_depth_cap = CONTEXT_DEPTH_STANDARD

    if llm_budget_tier == "none":
        model_tier_cap = MODEL_TIER_NONE
    elif llm_model_tier == "cheap" or llm_budget_tier == "low":
        model_tier_cap = MODEL_TIER_CHEAP
    else:
        model_tier_cap = MODEL_TIER_STANDARD

    token_cap = MAX_TOKENS_BY_CAP_LABEL.get(str(token_cap_label), 128)

    return {
        "llm_budget_tier": llm_budget_tier,
        "context_depth_cap": context_depth_cap,
        "model_tier_cap": model_tier_cap,
        "token_cap": token_cap,
        "max_context_lines": int(max_context_lines),
    }


def _min_context_depth(current: str, cap: str) -> str:
    if CONTEXT_DEPTH_ORDER.get(current, 0) <= CONTEXT_DEPTH_ORDER.get(cap, 0):
        return current
    return cap


def _min_model_tier(current: str, cap: str) -> str:
    if MODEL_TIER_ORDER.get(current, 0) <= MODEL_TIER_ORDER.get(cap, 0):
        return current
    return cap


def apply_evolution_caps_to_llm_gate_decision_v1(
    gate_decision: dict[str, Any],
    evolution_slice: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Apply B1.7 llm_gate slice as read-only caps on an existing P1.7 gate decision.

    Evolution can cap or downgrade LLM usage but cannot force call_llm.
    """
    if gate_decision.get("contract_version") != DAY_CONTENT_LLM_GATE_V1_CONTRACT:
        raise EvolutionLlmGateWiringError("invalid gate_decision contract_version")

    wired = copy.deepcopy(gate_decision)
    for key in EVOLUTION_LLM_GATE_TRACE_KEYS:
        wired.pop(key, None)

    if evolution_slice is None:
        wired.update(_default_evolution_trace(applied=False, cap_reason="no_evolution_slice"))
        return wired

    valid, invalid_reason = _is_valid_llm_gate_slice(evolution_slice)
    if not valid:
        wired.update(
            _default_evolution_trace(
                applied=False,
                cap_reason=f"ignored:{invalid_reason}",
            )
        )
        return wired

    caps = resolve_evolution_llm_caps_from_slice_v1(evolution_slice)
    blocked_escalations: list[str] = []
    cap_reasons: list[str] = []

    trace = _default_evolution_trace(applied=True)
    trace["evolution_context_depth_cap"] = caps["context_depth_cap"]
    trace["evolution_model_tier_cap"] = caps["model_tier_cap"]
    trace["evolution_token_cap"] = caps["token_cap"]

    if wired.get("decision") == DECISION_CALL_LLM:
        if caps["llm_budget_tier"] == "none":
            wired["decision"] = DECISION_NO_CALL
            wired["reason"] = "GATE:no_call:evolution_llm_budget_none"
            wired["render_sufficient"] = True
            wired["allowed_context_depth"] = CONTEXT_DEPTH_NONE
            wired["allowed_model_tier"] = MODEL_TIER_NONE
            wired["max_tokens"] = 0
            wired["save_required"] = False
            wired["dataset_candidate"] = False
            blocked_escalations.append("decision:call_llm->no_call")
            cap_reasons.append("evolution_llm_budget_none")
        else:
            previous_depth = wired.get("allowed_context_depth", CONTEXT_DEPTH_MINIMAL)
            previous_tier = wired.get("allowed_model_tier", MODEL_TIER_CHEAP)
            previous_tokens = int(wired.get("max_tokens", 0))

            capped_depth = _min_context_depth(str(previous_depth), caps["context_depth_cap"])
            capped_tier = _min_model_tier(str(previous_tier), caps["model_tier_cap"])
            capped_tokens = min(previous_tokens, caps["token_cap"])

            if capped_depth != previous_depth:
                blocked_escalations.append(f"context_depth:{previous_depth}->{capped_depth}")
            if capped_tier != previous_tier:
                blocked_escalations.append(f"model_tier:{previous_tier}->{capped_tier}")
            if capped_tokens != previous_tokens:
                blocked_escalations.append(f"max_tokens:{previous_tokens}->{capped_tokens}")

            wired["allowed_context_depth"] = capped_depth
            wired["allowed_model_tier"] = capped_tier
            wired["max_tokens"] = capped_tokens

            if blocked_escalations:
                cap_reasons.append("evolution_caps_applied")

    trace["blocked_escalations"] = blocked_escalations
    trace["cap_reason"] = "; ".join(cap_reasons) if cap_reasons else "evolution_caps_available"
    wired.update(trace)
    return wired


def decide_day_content_llm_call_with_evolution_v1(
    render: dict[str, Any],
    evaluation: dict[str, Any],
    *,
    surface: str,
    evolution_slice: dict[str, Any] | None = None,
    user_context_availability: dict[str, Any] | None = None,
    cache_status: dict[str, Any] | None = None,
    cost_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """P1.7 gate decision with optional B1.8 evolution cap layer."""
    gate = decide_day_content_llm_call_v1(
        render,
        evaluation,
        surface=surface,
        user_context_availability=user_context_availability,
        cache_status=cache_status,
        cost_policy=cost_policy,
    )
    return apply_evolution_caps_to_llm_gate_decision_v1(gate, evolution_slice)


def validate_evolution_llm_gate_wiring_v1(gate_decision: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if gate_decision.get("contract_version") != DAY_CONTENT_LLM_GATE_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in DAY_CONTENT_LLM_GATE_V1_KEYS:
        if key not in gate_decision:
            errors.append(f"missing gate field: {key}")

    if "evolution_slice_applied" in gate_decision:
        for key in EVOLUTION_LLM_GATE_TRACE_KEYS:
            if key not in gate_decision:
                errors.append(f"missing evolution trace field: {key}")
        if not isinstance(gate_decision.get("blocked_escalations"), list):
            errors.append("blocked_escalations must be array")

        if gate_decision.get("evolution_slice_applied") is True:
            if gate_decision.get("evolution_context_depth_cap") is None:
                errors.append("evolution_context_depth_cap required when slice applied")
            if gate_decision.get("evolution_model_tier_cap") is None:
                errors.append("evolution_model_tier_cap required when slice applied")
            if gate_decision.get("evolution_token_cap") is None:
                errors.append("evolution_token_cap required when slice applied")

    forbidden = set(gate_decision.keys()) & {
        "blocked_effects",
        "stage_effects_ref",
        "evolution_score_snapshot_id",
        "allowed_effects",
        "effect_limits",
    }
    if forbidden:
        errors.append(f"forbidden evolution policy fields on gate output: {sorted(forbidden)}")

    return errors
