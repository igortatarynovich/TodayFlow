"""AMLL Gate v1 for Today narrative surfaces (guide…deepen).

Pipeline order (API_MEMORY §7): exact cache → similarity reuse → template → call LLM.

Decision-only module — no provider calls. Wired from ``build_today_narrative``.
"""

from __future__ import annotations

from typing import Any, Literal

TodayNarrativeSurface = Literal["guide", "day_layer", "spheres", "evening", "deepen"]

TODAY_NARRATIVE_LLM_GATE_V1_CONTRACT = "today_narrative_llm_gate_v1"

GATE_DECISION_CACHE_HIT = "cache_hit"
GATE_DECISION_REUSE = "reuse"
GATE_DECISION_TEMPLATE = "template"
GATE_DECISION_CALL_LLM = "call_llm"
GATE_DECISION_BLOCKED = "blocked"

GATE_DECISION_VALUES = frozenset(
    {
        GATE_DECISION_CACHE_HIT,
        GATE_DECISION_REUSE,
        GATE_DECISION_TEMPLATE,
        GATE_DECISION_CALL_LLM,
        GATE_DECISION_BLOCKED,
    }
)

CONTEXT_DEPTH_NONE = "none"
CONTEXT_DEPTH_MINIMAL = "minimal"
CONTEXT_DEPTH_STANDARD = "standard"

MODEL_TIER_NONE = "none"
MODEL_TIER_CHEAP = "cheap"
MODEL_TIER_STANDARD = "standard"

CACHE_EXACT_ONLY = "exact_only"
CACHE_ALLOW_SIMILARITY = "allow_similarity"
CACHE_BYPASS = "bypass"

ALLOWED_SURFACES = frozenset({"guide", "day_layer", "spheres", "evening", "deepen"})

DEFAULT_CACHE_STATUS = {
    "exact_hit": False,
    "similarity_available": False,
    "reuse_source_generation_id": None,
}

DEFAULT_USER_CONTEXT = {
    "has_day_context": False,
    "has_foundation": False,
    "behavior_event_count": 0,
    "quality_mode": "trust_llm",
    "context_slice_id": "",
}

DEFAULT_COST_POLICY = {
    "mode": "normal",
    "llm_calls_allowed": True,
}

MAX_TOKENS_BY_SURFACE: dict[str, dict[str, int]] = {
    "guide": {"quick": 950, "normal": 1750, "deep": 2100},
    "day_layer": {"quick": 700, "normal": 1200, "deep": 1500},
    "spheres": {"quick": 500, "normal": 800, "deep": 1000},
    "evening": {"quick": 500, "normal": 800, "deep": 1000},
    "deepen": {"quick": 600, "normal": 1000, "deep": 1300},
}

TODAY_NARRATIVE_LLM_GATE_V1_KEYS = frozenset(
    {
        "contract_version",
        "surface",
        "gate_decision",
        "decision",
        "reason",
        "pipeline_stage",
        "render_sufficient",
        "allowed_context_depth",
        "allowed_model_tier",
        "max_tokens",
        "cache_policy",
        "save_required",
        "dataset_candidate",
        "blocked_reason",
        "context_slice_id",
        "reuse_source_generation_id",
    }
)


class TodayNarrativeLlmGateError(ValueError):
    """Raised when gate inputs are invalid."""


def _normalize_cache_status(raw: dict[str, Any] | None) -> dict[str, Any]:
    base = dict(DEFAULT_CACHE_STATUS)
    if isinstance(raw, dict):
        base.update({k: raw[k] for k in DEFAULT_CACHE_STATUS if k in raw})
    return base


def _normalize_user_context(raw: dict[str, Any] | None) -> dict[str, Any]:
    base = dict(DEFAULT_USER_CONTEXT)
    if isinstance(raw, dict):
        for key in DEFAULT_USER_CONTEXT:
            if key in raw:
                base[key] = raw[key]
    return base


def _normalize_cost_policy(raw: dict[str, Any] | None) -> dict[str, Any]:
    base = dict(DEFAULT_COST_POLICY)
    if isinstance(raw, dict):
        base.update({k: raw[k] for k in DEFAULT_COST_POLICY if k in raw})
    return base


def _max_tokens_for_surface(surface: str, depth_level: str) -> int:
    depth = depth_level if depth_level in ("quick", "normal", "deep") else "normal"
    table = MAX_TOKENS_BY_SURFACE.get(surface) or MAX_TOKENS_BY_SURFACE["guide"]
    return int(table.get(depth) or table["normal"])


def _model_tier_for_surface(surface: str, depth_level: str) -> str:
    if surface in ("spheres", "evening"):
        return MODEL_TIER_CHEAP
    if surface == "deepen" and depth_level == "quick":
        return MODEL_TIER_CHEAP
    return MODEL_TIER_STANDARD


def _context_depth_for_surface(surface: str, user_context: dict[str, Any]) -> str:
    if not user_context.get("has_day_context"):
        return CONTEXT_DEPTH_MINIMAL
    if surface == "guide":
        return CONTEXT_DEPTH_STANDARD
    if int(user_context.get("behavior_event_count") or 0) >= 3:
        return CONTEXT_DEPTH_STANDARD
    return CONTEXT_DEPTH_MINIMAL


def _gate_result(
    *,
    surface: str,
    gate_decision: str,
    reason: str,
    pipeline_stage: str,
    render_sufficient: bool = False,
    allowed_context_depth: str = CONTEXT_DEPTH_NONE,
    allowed_model_tier: str = MODEL_TIER_NONE,
    max_tokens: int = 0,
    cache_policy: str = CACHE_BYPASS,
    save_required: bool = False,
    dataset_candidate: bool = False,
    blocked_reason: str | None = None,
    context_slice_id: str = "",
    reuse_source_generation_id: int | None = None,
) -> dict[str, Any]:
    out = {
        "contract_version": TODAY_NARRATIVE_LLM_GATE_V1_CONTRACT,
        "surface": surface,
        "gate_decision": gate_decision,
        "decision": gate_decision,
        "reason": reason,
        "pipeline_stage": pipeline_stage,
        "render_sufficient": render_sufficient,
        "allowed_context_depth": allowed_context_depth,
        "allowed_model_tier": allowed_model_tier,
        "max_tokens": max_tokens,
        "cache_policy": cache_policy,
        "save_required": save_required,
        "dataset_candidate": dataset_candidate,
        "blocked_reason": blocked_reason,
        "context_slice_id": context_slice_id,
        "reuse_source_generation_id": reuse_source_generation_id,
    }
    errors = validate_today_narrative_llm_gate_v1(out)
    if errors:
        raise TodayNarrativeLlmGateError("; ".join(errors))
    return out


def validate_today_narrative_llm_gate_v1(gate: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if gate.get("contract_version") != TODAY_NARRATIVE_LLM_GATE_V1_CONTRACT:
        errors.append("invalid contract_version")
    for key in TODAY_NARRATIVE_LLM_GATE_V1_KEYS:
        if key not in gate:
            errors.append(f"missing field: {key}")
    decision = gate.get("gate_decision")
    if decision not in GATE_DECISION_VALUES:
        errors.append("invalid gate_decision")
    if gate.get("decision") != decision:
        errors.append("decision must match gate_decision")
    if decision == GATE_DECISION_CALL_LLM:
        max_tokens = gate.get("max_tokens")
        if not isinstance(max_tokens, int) or max_tokens <= 0:
            errors.append("call_llm requires max_tokens > 0")
        if gate.get("allowed_model_tier") == MODEL_TIER_NONE:
            errors.append("call_llm requires allowed_model_tier")
    if decision == GATE_DECISION_BLOCKED and not gate.get("blocked_reason"):
        errors.append("blocked requires blocked_reason")
    return errors


def build_cache_hit_gate_v1(
    *,
    surface: str,
    source_generation_log_id: int,
    context_slice_id: str = "",
    match_mode: str = "exact",
) -> dict[str, Any]:
    """Gate outcome when ``_load_narrative_cache`` returns a valid row.

    ``match_mode`` distinguishes an exact ``day_context_sha256`` match from a
    same-day reuse: within a day the DayContext hash drifts as the user's own
    tracked activity moves fusion scores / history, so an exact hash is a
    freshness *preference*, not a hard gate. Reuse of the same-day narrative is
    still a no-LLM outcome; the reason/cache_policy make the reuse auditable.
    """
    if surface not in ALLOWED_SURFACES:
        raise TodayNarrativeLlmGateError(f"unsupported surface: {surface!r}")
    same_day_reuse = str(match_mode or "exact") != "exact"
    return _gate_result(
        surface=surface,
        gate_decision=GATE_DECISION_CACHE_HIT,
        reason=(
            "GATE:cache_hit:same_day_reuse"
            if same_day_reuse
            else "GATE:cache_hit:exact_context_match"
        ),
        pipeline_stage="cache",
        render_sufficient=True,
        cache_policy=CACHE_ALLOW_SIMILARITY if same_day_reuse else CACHE_EXACT_ONLY,
        context_slice_id=context_slice_id,
        reuse_source_generation_id=int(source_generation_log_id),
    )


def decide_today_narrative_llm_call_v1(
    *,
    surface: str,
    llm_configured: bool,
    cache_status: dict[str, Any] | None = None,
    user_context: dict[str, Any] | None = None,
    cost_policy: dict[str, Any] | None = None,
    depth_level: str = "normal",
) -> dict[str, Any]:
    """
    AMLL Gate v1 for narrative miss path (after exact cache miss).

    Order: reuse (similarity) → template (no LLM) → call_llm → blocked.
    """
    if surface not in ALLOWED_SURFACES:
        raise TodayNarrativeLlmGateError(f"unsupported surface: {surface!r}")

    cache = _normalize_cache_status(cache_status)
    ctx = _normalize_user_context(user_context)
    cost = _normalize_cost_policy(cost_policy)
    depth = depth_level if depth_level in ("quick", "normal", "deep") else "normal"
    slice_id = str(ctx.get("context_slice_id") or "")

    if cache.get("exact_hit"):
        return build_cache_hit_gate_v1(
            surface=surface,
            source_generation_log_id=int(cache.get("reuse_source_generation_id") or 0),
            context_slice_id=slice_id,
        )

    if cache.get("similarity_available"):
        reuse_id = cache.get("reuse_source_generation_id")
        return _gate_result(
            surface=surface,
            gate_decision=GATE_DECISION_REUSE,
            reason="GATE:reuse:similarity_match",
            pipeline_stage="reuse",
            render_sufficient=True,
            cache_policy=CACHE_ALLOW_SIMILARITY,
            context_slice_id=slice_id,
            reuse_source_generation_id=int(reuse_id) if reuse_id is not None else None,
        )

    if not llm_configured:
        return _gate_result(
            surface=surface,
            gate_decision=GATE_DECISION_TEMPLATE,
            reason="GATE:template:llm_not_configured",
            pipeline_stage="template",
            render_sufficient=False,
            allowed_context_depth=CONTEXT_DEPTH_MINIMAL,
            context_slice_id=slice_id,
        )

    if cost.get("mode") == "strict" and not cost.get("llm_calls_allowed", True):
        return _gate_result(
            surface=surface,
            gate_decision=GATE_DECISION_BLOCKED,
            reason="GATE:blocked:cost_policy_strict",
            pipeline_stage="blocked",
            blocked_reason="cost_policy_strict",
            context_slice_id=slice_id,
        )

    context_depth = _context_depth_for_surface(surface, ctx)
    model_tier = _model_tier_for_surface(surface, depth)
    max_tokens = _max_tokens_for_surface(surface, depth)
    cache_policy = CACHE_ALLOW_SIMILARITY if cache.get("similarity_available") else CACHE_BYPASS

    return _gate_result(
        surface=surface,
        gate_decision=GATE_DECISION_CALL_LLM,
        reason="GATE:call_llm:narrative_generation",
        pipeline_stage="llm",
        allowed_context_depth=context_depth,
        allowed_model_tier=model_tier,
        max_tokens=max_tokens,
        cache_policy=cache_policy,
        save_required=True,
        dataset_candidate=True,
        context_slice_id=slice_id,
    )


def should_skip_llm_for_gate(gate: dict[str, Any]) -> bool:
    """True when pipeline must not call external LLM (template / blocked / reuse)."""
    decision = gate.get("gate_decision")
    return decision in {
        GATE_DECISION_TEMPLATE,
        GATE_DECISION_BLOCKED,
        GATE_DECISION_REUSE,
        GATE_DECISION_CACHE_HIT,
    }
