"""P1.7 — LLM call gate for day content render (decision only, no API call)."""

from __future__ import annotations

from typing import Any

from todayflow_backend.services.day_model_v1_content_evaluator import (
    DAY_CONTENT_PACKAGE_EVALUATION_V1_CONTRACT,
    RECOMMENDATION_BLOCK,
    RECOMMENDATION_USE,
    RECOMMENDATION_USE_WITH_CAUTION,
)
from todayflow_backend.services.day_model_v1_content_renderer import (
    DAY_CONTENT_RENDER_V1_CONTRACT,
    REQUIRED_RENDER_SURFACES,
)
from todayflow_backend.services.day_model_v1_interpreter import LOW_CONFIDENCE_THRESHOLD

DAY_CONTENT_LLM_GATE_V1_CONTRACT = "day_content_llm_gate_v1"

DECISION_NO_CALL = "no_call"
DECISION_CALL_LLM = "call_llm"
DECISION_BLOCKED = "blocked"

DECISION_VALUES = frozenset({DECISION_NO_CALL, DECISION_CALL_LLM, DECISION_BLOCKED})

CONTEXT_DEPTH_NONE = "none"
CONTEXT_DEPTH_MINIMAL = "minimal"
CONTEXT_DEPTH_STANDARD = "standard"

MODEL_TIER_NONE = "none"
MODEL_TIER_CHEAP = "cheap"
MODEL_TIER_STANDARD = "standard"

CACHE_EXACT_ONLY = "exact_only"
CACHE_ALLOW_SIMILARITY = "allow_similarity"
CACHE_BYPASS = "bypass"

DETERMINISTIC_ONLY_SURFACES = frozenset(
    {
        "today_hero",
        "risk_card",
        "action_card",
        "tempo_card",
    }
)

NARRATIVE_SURFACES = frozenset(
    {
        "day_guidance_card",
        "reflection_card",
    }
)

ALLOWED_GATE_SURFACES = DETERMINISTIC_ONLY_SURFACES | NARRATIVE_SURFACES

DEFAULT_USER_CONTEXT_AVAILABILITY = {
    "has_user_context": False,
    "context_level": CONTEXT_DEPTH_NONE,
    "memory_available": False,
}

DEFAULT_CACHE_STATUS = {
    "exact_hit": False,
    "similarity_available": False,
}

DEFAULT_COST_POLICY = {
    "mode": "normal",
    "llm_calls_allowed": True,
    "max_tokens_budget": 512,
}

DAY_CONTENT_LLM_GATE_V1_KEYS = frozenset(
    {
        "contract_version",
        "surface",
        "decision",
        "reason",
        "render_sufficient",
        "allowed_context_depth",
        "allowed_model_tier",
        "max_tokens",
        "cache_policy",
        "save_required",
        "dataset_candidate",
        "blocked_reason",
    }
)

CONFLICT_ISSUE_PREFIX = "E-CONFLICT:"

MAX_TOKENS_BY_SURFACE = {
    "today_hero": 64,
    "day_guidance_card": 256,
    "risk_card": 96,
    "action_card": 96,
    "tempo_card": 96,
    "reflection_card": 128,
}


class DayContentLlmGateError(ValueError):
    """Raised when gate inputs are invalid."""


def _require_render_and_evaluation(
    render: dict[str, Any],
    evaluation: dict[str, Any],
) -> None:
    if render.get("contract_version") != DAY_CONTENT_RENDER_V1_CONTRACT:
        raise DayContentLlmGateError(
            f"expected render contract_version={DAY_CONTENT_RENDER_V1_CONTRACT!r}, "
            f"got {render.get('contract_version')!r}"
        )
    if evaluation.get("contract_version") != DAY_CONTENT_PACKAGE_EVALUATION_V1_CONTRACT:
        raise DayContentLlmGateError(
            f"expected evaluation contract_version={DAY_CONTENT_PACKAGE_EVALUATION_V1_CONTRACT!r}, "
            f"got {evaluation.get('contract_version')!r}"
        )


def _normalize_user_context(raw: dict[str, Any] | None) -> dict[str, Any]:
    base = dict(DEFAULT_USER_CONTEXT_AVAILABILITY)
    if raw:
        base.update(raw)
    return base


def _normalize_cache_status(raw: dict[str, Any] | None) -> dict[str, Any]:
    base = dict(DEFAULT_CACHE_STATUS)
    if raw:
        base.update(raw)
    return base


def _normalize_cost_policy(raw: dict[str, Any] | None) -> dict[str, Any]:
    base = dict(DEFAULT_COST_POLICY)
    if raw:
        base.update(raw)
    return base


def _has_high_risk_conflicts(evaluation: dict[str, Any]) -> bool:
    return any(
        issue.startswith(CONFLICT_ISSUE_PREFIX) for issue in evaluation.get("issues", [])
    )


def _confidence_sufficient(render: dict[str, Any]) -> bool:
    metadata = render.get("metadata") or {}
    interpretation = metadata.get("interpretation") or {}
    confidence = interpretation.get("confidence")
    if confidence is None:
        return False
    return float(confidence) >= LOW_CONFIDENCE_THRESHOLD


def _required_surfaces_present(render: dict[str, Any]) -> bool:
    surfaces = render.get("surfaces") or {}
    return all(surface in surfaces and surfaces[surface] for surface in REQUIRED_RENDER_SURFACES)


def _surface_present(render: dict[str, Any], surface: str) -> bool:
    surfaces = render.get("surfaces") or {}
    return surface in surfaces and bool(surfaces[surface])


def _blocked_result(
    *,
    surface: str,
    blocked_reason: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "contract_version": DAY_CONTENT_LLM_GATE_V1_CONTRACT,
        "surface": surface,
        "decision": DECISION_BLOCKED,
        "reason": reason,
        "render_sufficient": False,
        "allowed_context_depth": CONTEXT_DEPTH_NONE,
        "allowed_model_tier": MODEL_TIER_NONE,
        "max_tokens": 0,
        "cache_policy": CACHE_EXACT_ONLY,
        "save_required": False,
        "dataset_candidate": False,
        "blocked_reason": blocked_reason,
    }


def _no_call_result(
    *,
    surface: str,
    reason: str,
    cache_policy: str = CACHE_EXACT_ONLY,
) -> dict[str, Any]:
    return {
        "contract_version": DAY_CONTENT_LLM_GATE_V1_CONTRACT,
        "surface": surface,
        "decision": DECISION_NO_CALL,
        "reason": reason,
        "render_sufficient": True,
        "allowed_context_depth": CONTEXT_DEPTH_NONE,
        "allowed_model_tier": MODEL_TIER_NONE,
        "max_tokens": 0,
        "cache_policy": cache_policy,
        "save_required": False,
        "dataset_candidate": False,
        "blocked_reason": None,
    }


def _call_llm_result(
    *,
    surface: str,
    reason: str,
    context_depth: str,
    model_tier: str,
    max_tokens: int,
    cache_policy: str,
) -> dict[str, Any]:
    return {
        "contract_version": DAY_CONTENT_LLM_GATE_V1_CONTRACT,
        "surface": surface,
        "decision": DECISION_CALL_LLM,
        "reason": reason,
        "render_sufficient": False,
        "allowed_context_depth": context_depth,
        "allowed_model_tier": model_tier,
        "max_tokens": max_tokens,
        "cache_policy": cache_policy,
        "save_required": True,
        "dataset_candidate": True,
        "blocked_reason": None,
    }


def _max_tokens_for_surface(surface: str, cost_policy: dict[str, Any]) -> int:
    surface_cap = MAX_TOKENS_BY_SURFACE.get(surface, 128)
    budget = int(cost_policy.get("max_tokens_budget", 512))
    return min(surface_cap, budget)


def _narrative_needs_llm(
    render: dict[str, Any],
    evaluation: dict[str, Any],
    user_context: dict[str, Any],
) -> bool:
    recommendation = evaluation.get("recommendation")
    if recommendation == RECOMMENDATION_USE_WITH_CAUTION:
        return True
    if _has_high_risk_conflicts(evaluation):
        return True
    if bool(render.get("degraded", False)):
        return True
    if not _confidence_sufficient(render):
        return True
    if user_context.get("has_user_context") and user_context.get("context_level") != CONTEXT_DEPTH_NONE:
        return True
    return False


def decide_day_content_llm_call_v1(
    render: dict[str, Any],
    evaluation: dict[str, Any],
    *,
    surface: str,
    user_context_availability: dict[str, Any] | None = None,
    cache_status: dict[str, Any] | None = None,
    cost_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    P1.7 — decide whether LLM refinement is needed for a render surface.

    Gate only: no prompts, API calls, profile/memory reads, or render mutation.
    """
    _require_render_and_evaluation(render, evaluation)
    user_context = _normalize_user_context(user_context_availability)
    cache = _normalize_cache_status(cache_status)
    cost = _normalize_cost_policy(cost_policy)

    if surface not in ALLOWED_GATE_SURFACES:
        return _blocked_result(
            surface=surface,
            blocked_reason="forbidden_surface",
            reason="GATE:blocked:forbidden_surface",
        )

    if evaluation.get("recommendation") == RECOMMENDATION_BLOCK:
        return _blocked_result(
            surface=surface,
            blocked_reason="evaluation_block",
            reason="GATE:blocked:evaluation_block",
        )

    if not render.get("renderable", False):
        return _blocked_result(
            surface=surface,
            blocked_reason="render_not_renderable",
            reason="GATE:blocked:render_not_renderable",
        )

    if not _required_surfaces_present(render):
        return _blocked_result(
            surface=surface,
            blocked_reason="missing_required_surfaces",
            reason="GATE:blocked:missing_required_surfaces",
        )

    if not _surface_present(render, surface):
        return _blocked_result(
            surface=surface,
            blocked_reason="missing_surface",
            reason=f"GATE:blocked:missing_surface:{surface}",
        )

    if cache.get("exact_hit"):
        return _no_call_result(
            surface=surface,
            reason="GATE:no_call:exact_cache_hit",
            cache_policy=CACHE_EXACT_ONLY,
        )

    if surface in DETERMINISTIC_ONLY_SURFACES:
        return _no_call_result(
            surface=surface,
            reason="GATE:no_call:deterministic_surface_sufficient",
        )

    needs_llm = _narrative_needs_llm(render, evaluation, user_context)

    if not needs_llm and evaluation.get("recommendation") == RECOMMENDATION_USE:
        return _no_call_result(
            surface=surface,
            reason="GATE:no_call:render_sufficient",
        )

    if cost.get("mode") == "strict":
        if needs_llm and not cost.get("llm_calls_allowed", True):
            return _blocked_result(
                surface=surface,
                blocked_reason="cost_policy_strict",
                reason="GATE:blocked:cost_policy_strict",
            )
        return _no_call_result(
            surface=surface,
            reason="GATE:no_call:cost_policy_strict",
        )

    context_depth = CONTEXT_DEPTH_MINIMAL
    model_tier = MODEL_TIER_CHEAP
    if evaluation.get("recommendation") == RECOMMENDATION_USE and not render.get("degraded", False):
        context_depth = CONTEXT_DEPTH_STANDARD
        model_tier = MODEL_TIER_STANDARD

    cache_policy = CACHE_ALLOW_SIMILARITY if cache.get("similarity_available") else CACHE_BYPASS

    return _call_llm_result(
        surface=surface,
        reason="GATE:call_llm:narrative_refinement_required",
        context_depth=context_depth,
        model_tier=model_tier,
        max_tokens=_max_tokens_for_surface(surface, cost),
        cache_policy=cache_policy,
    )
