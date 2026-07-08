"""B1.9 — Evolution → Context Selector wiring (B1.7 context_selector slice as cap layer)."""

from __future__ import annotations

import copy
from typing import Any

from todayflow_backend.services.day_model_v1_knowledge_context_selection import (
    DAY_CONTEXT_SLICE_V1_KEYS,
    EXCLUSION_HARD_CAP,
    EXCLUSION_SOFT_CAP,
    HARD_CAP_DEFAULT,
    KNOWLEDGE_CONTEXT_SLICE_V1_CONTRACT,
    SOFT_CAP_DEFAULT,
    select_knowledge_context_v1,
    validate_knowledge_context_slice_v1,
)
from todayflow_backend.services.evolution_effect_consumer_map_v1 import (
    CONSUMER_CONTEXT_SELECTOR,
    EVOLUTION_EFFECT_CONSUMER_SLICE_V1_CONTRACT,
    validate_evolution_effect_consumer_slice_v1,
)
from todayflow_backend.services.evolution_effect_runtime_policy_v1 import (
    EVOLUTION_EFFECT_RUNTIME_POLICY_V1_CONTRACT,
)

EVOLUTION_CONTEXT_SELECTOR_WIRING_V1_VERSION = "1.0.0"

EXCLUSION_EVOLUTION_CAP = "evolution_cap"

EVOLUTION_CONTEXT_SELECTOR_TRACE_KEYS = frozenset(
    {
        "evolution_slice_applied",
        "evolution_ak_cap",
        "evolution_memory_window_days",
        "evolution_context_lines_cap",
        "evolution_expansion_allowed",
        "evolution_cap_reason",
        "blocked_expansions",
    }
)

KNOWLEDGE_CONTEXT_SLICE_V1_WITH_EVOLUTION_KEYS = (
    DAY_CONTEXT_SLICE_V1_KEYS | EVOLUTION_CONTEXT_SELECTOR_TRACE_KEYS
)

CONTEXT_SLICE_DEPTH_TO_LINES = {
    "minimal": 0,
    "basic": 1,
    "standard": 2,
    "enhanced": 4,
    "expert": 5,
    "full": 5,
}


class EvolutionContextSelectorWiringError(ValueError):
    """Raised when context selector wiring inputs are invalid."""


def _default_evolution_trace(*, applied: bool = False, cap_reason: str | None = None) -> dict[str, Any]:
    return {
        "evolution_slice_applied": applied,
        "evolution_ak_cap": None,
        "evolution_memory_window_days": None,
        "evolution_context_lines_cap": None,
        "evolution_expansion_allowed": False,
        "evolution_cap_reason": cap_reason,
        "blocked_expansions": [],
    }


def _is_valid_context_selector_slice(
    evolution_slice: dict[str, Any],
) -> tuple[bool, str | None]:
    if evolution_slice.get("contract_version") == EVOLUTION_EFFECT_RUNTIME_POLICY_V1_CONTRACT:
        return False, "full_policy_not_accepted"
    if evolution_slice.get("contract_version") != EVOLUTION_EFFECT_CONSUMER_SLICE_V1_CONTRACT:
        return False, "invalid_slice_contract"
    if evolution_slice.get("consumer_id") != CONSUMER_CONTEXT_SELECTOR:
        return False, "invalid_consumer_id"
    errors = validate_evolution_effect_consumer_slice_v1(
        evolution_slice,
        consumer_id=CONSUMER_CONTEXT_SELECTOR,
    )
    if errors:
        return False, "invalid_slice_payload"
    return True, None


def resolve_evolution_context_caps_from_slice_v1(
    evolution_slice: dict[str, Any],
) -> dict[str, Any]:
    """Resolve evolution caps for context selection from a validated context_selector slice."""
    valid, reason = _is_valid_context_selector_slice(evolution_slice)
    if not valid:
        raise EvolutionContextSelectorWiringError(reason or "invalid evolution slice")

    limits = evolution_slice.get("effect_limits") or {}
    intelligence = (evolution_slice.get("allowed_effects") or {}).get("intelligence_effects") or {}

    ak_cap = limits.get("active_knowledge_cap")
    if ak_cap is None:
        ak_cap = intelligence.get("active_knowledge_cap", 0)

    memory_window_days = limits.get("memory_window_days")
    if memory_window_days is None:
        memory_window_days = intelligence.get("memory_window_days")

    context_slice_depth = limits.get("context_slice_depth")
    if context_slice_depth is None:
        context_slice_depth = intelligence.get("context_slice_depth", "minimal")

    context_lines_cap = CONTEXT_SLICE_DEPTH_TO_LINES.get(
        str(context_slice_depth),
        int(ak_cap),
    )

    ak_cap_int = max(0, min(int(ak_cap), HARD_CAP_DEFAULT))
    context_lines_cap = max(0, min(int(context_lines_cap), HARD_CAP_DEFAULT))

    return {
        "ak_cap": ak_cap_int,
        "memory_window_days": int(memory_window_days) if memory_window_days is not None else None,
        "context_lines_cap": context_lines_cap,
        "context_slice_depth": str(context_slice_depth),
    }


def compute_effective_selection_caps_v1(
    *,
    soft_cap: int,
    hard_cap: int,
    evolution_caps: dict[str, Any] | None = None,
) -> tuple[int, int, bool, list[str]]:
    """Return effective soft/hard caps and whether soft→hard expansion remains allowed."""
    base_hard = min(int(hard_cap), HARD_CAP_DEFAULT)
    base_soft = min(int(soft_cap), base_hard)
    blocked_expansions: list[str] = []

    if evolution_caps is None:
        expansion_allowed = base_hard > base_soft
        return base_soft, base_hard, expansion_allowed, blocked_expansions

    evolution_ak_cap = int(evolution_caps["ak_cap"])
    effective_hard = min(base_hard, evolution_ak_cap)
    effective_soft = min(base_soft, effective_hard)

    if effective_hard < base_hard:
        blocked_expansions.append(f"hard_cap:{base_hard}->{effective_hard}")
    if effective_soft < base_soft:
        blocked_expansions.append(f"soft_cap:{base_soft}->{effective_soft}")

    expansion_allowed = effective_hard > effective_soft
    if base_hard > base_soft and not expansion_allowed:
        blocked_expansions.append("soft_to_hard_expansion")

    return effective_soft, effective_hard, expansion_allowed, blocked_expansions


def _remap_cap_exclusions_for_evolution(context_slice: dict[str, Any]) -> None:
    excluded = context_slice.get("excluded_facts")
    if not isinstance(excluded, list):
        return

    remapped = False
    for entry in excluded:
        if not isinstance(entry, dict):
            continue
        if entry.get("reason") in {EXCLUSION_SOFT_CAP, EXCLUSION_HARD_CAP}:
            entry["reason"] = EXCLUSION_EVOLUTION_CAP
            remapped = True

    if remapped:
        reasons = {
            str(entry.get("reason"))
            for entry in excluded
            if isinstance(entry, dict) and entry.get("reason")
        }
        context_slice["exclusion_reasons"] = sorted(reasons)


def apply_evolution_caps_to_knowledge_context_slice_v1(
    context_slice: dict[str, Any],
    evolution_slice: dict[str, Any] | None = None,
    *,
    base_soft_cap: int = SOFT_CAP_DEFAULT,
    base_hard_cap: int = HARD_CAP_DEFAULT,
) -> dict[str, Any]:
    """
    Apply B1.7 context_selector slice as read-only caps on an existing A1.1 context slice.

    Re-runs cap tightening when needed; never increases selected_facts count.
    """
    if context_slice.get("contract_version") != KNOWLEDGE_CONTEXT_SLICE_V1_CONTRACT:
        raise EvolutionContextSelectorWiringError("invalid context_slice contract_version")

    wired = copy.deepcopy(context_slice)
    for key in EVOLUTION_CONTEXT_SELECTOR_TRACE_KEYS:
        wired.pop(key, None)

    if evolution_slice is None:
        wired.update(_default_evolution_trace(applied=False, cap_reason="no_evolution_slice"))
        return wired

    valid, invalid_reason = _is_valid_context_selector_slice(evolution_slice)
    if not valid:
        wired.update(
            _default_evolution_trace(
                applied=False,
                cap_reason=f"ignored:{invalid_reason}",
            )
        )
        return wired

    evolution_caps = resolve_evolution_context_caps_from_slice_v1(evolution_slice)
    effective_soft, effective_hard, expansion_allowed, blocked_expansions = (
        compute_effective_selection_caps_v1(
            soft_cap=base_soft_cap,
            hard_cap=base_hard_cap,
            evolution_caps=evolution_caps,
        )
    )

    current_selected = wired.get("selected_facts") or []

    if len(current_selected) > effective_hard:
        overflow = current_selected[effective_hard:]
        wired["selected_facts"] = current_selected[:effective_hard]
        excluded = list(wired.get("excluded_facts") or [])
        for fact in overflow:
            if not isinstance(fact, dict):
                continue
            excluded.append(
                {
                    "knowledge_id": fact.get("knowledge_id"),
                    "claim": fact.get("claim"),
                    "reason": EXCLUSION_EVOLUTION_CAP,
                    "detail": f"evolution_ak_cap={evolution_caps['ak_cap']}",
                }
            )
        wired["excluded_facts"] = excluded
        reasons = {
            str(entry.get("reason"))
            for entry in excluded
            if isinstance(entry, dict) and entry.get("reason")
        }
        wired["exclusion_reasons"] = sorted(reasons)
        traceability = dict(wired.get("traceability") or {})
        traceability["selected_count"] = len(wired["selected_facts"])
        traceability["excluded_count"] = len(excluded)
        wired["traceability"] = traceability
        blocked_expansions.append(
            f"selected_facts:{len(current_selected)}->{len(wired['selected_facts'])}"
        )

    wired["soft_cap"] = effective_soft
    wired["hard_cap"] = effective_hard
    _remap_cap_exclusions_for_evolution(wired)

    trace = _default_evolution_trace(applied=True, cap_reason="evolution_caps_applied")
    trace["evolution_ak_cap"] = evolution_caps["ak_cap"]
    trace["evolution_memory_window_days"] = evolution_caps["memory_window_days"]
    trace["evolution_context_lines_cap"] = evolution_caps["context_lines_cap"]
    trace["evolution_expansion_allowed"] = expansion_allowed
    trace["blocked_expansions"] = blocked_expansions
    wired.update(trace)
    return wired


def select_knowledge_context_with_evolution_v1(
    active_knowledge_list: list[dict[str, Any]],
    *,
    day_context: dict[str, Any] | None = None,
    goals: list[dict[str, Any]] | None = None,
    practices: list[dict[str, Any]] | None = None,
    evolution_stage: str | None = None,
    target_surface: str = "day_guidance_card",
    soft_cap: int = SOFT_CAP_DEFAULT,
    hard_cap: int = HARD_CAP_DEFAULT,
    evolution_slice: dict[str, Any] | None = None,
    now=None,
    created_at: str | None = None,
    context_slice_id: str | None = None,
) -> dict[str, Any]:
    """A1.1 selection with optional B1.9 evolution cap layer."""
    if evolution_slice is None:
        context_slice = select_knowledge_context_v1(
            active_knowledge_list,
            day_context=day_context,
            goals=goals,
            practices=practices,
            evolution_stage=evolution_stage,
            target_surface=target_surface,
            soft_cap=soft_cap,
            hard_cap=hard_cap,
            now=now,
            created_at=created_at,
            context_slice_id=context_slice_id,
        )
        context_slice.update(_default_evolution_trace(applied=False, cap_reason="no_evolution_slice"))
        return context_slice

    valid, invalid_reason = _is_valid_context_selector_slice(evolution_slice)
    if not valid:
        context_slice = select_knowledge_context_v1(
            active_knowledge_list,
            day_context=day_context,
            goals=goals,
            practices=practices,
            evolution_stage=evolution_stage,
            target_surface=target_surface,
            soft_cap=soft_cap,
            hard_cap=hard_cap,
            now=now,
            created_at=created_at,
            context_slice_id=context_slice_id,
        )
        context_slice.update(
            _default_evolution_trace(
                applied=False,
                cap_reason=f"ignored:{invalid_reason}",
            )
        )
        return context_slice

    evolution_caps = resolve_evolution_context_caps_from_slice_v1(evolution_slice)
    effective_soft, effective_hard, expansion_allowed, blocked_expansions = (
        compute_effective_selection_caps_v1(
            soft_cap=soft_cap,
            hard_cap=hard_cap,
            evolution_caps=evolution_caps,
        )
    )

    context_slice = select_knowledge_context_v1(
        active_knowledge_list,
        day_context=day_context,
        goals=goals,
        practices=practices,
        evolution_stage=evolution_stage,
        target_surface=target_surface,
        soft_cap=effective_soft,
        hard_cap=effective_hard,
        now=now,
        created_at=created_at,
        context_slice_id=context_slice_id,
    )

    _remap_cap_exclusions_for_evolution(context_slice)

    trace = _default_evolution_trace(applied=True, cap_reason="evolution_caps_applied")
    trace["evolution_ak_cap"] = evolution_caps["ak_cap"]
    trace["evolution_memory_window_days"] = evolution_caps["memory_window_days"]
    trace["evolution_context_lines_cap"] = evolution_caps["context_lines_cap"]
    trace["evolution_expansion_allowed"] = expansion_allowed
    trace["blocked_expansions"] = blocked_expansions
    context_slice.update(trace)
    return context_slice


def validate_evolution_context_selector_wiring_v1(context_slice: dict[str, Any]) -> list[str]:
    errors = list(validate_knowledge_context_slice_v1(context_slice))

    if "evolution_slice_applied" in context_slice:
        for key in EVOLUTION_CONTEXT_SELECTOR_TRACE_KEYS:
            if key not in context_slice:
                errors.append(f"missing evolution trace field: {key}")
        if not isinstance(context_slice.get("blocked_expansions"), list):
            errors.append("blocked_expansions must be array")

        if context_slice.get("evolution_slice_applied") is True:
            if context_slice.get("evolution_ak_cap") is None:
                errors.append("evolution_ak_cap required when slice applied")
            if context_slice.get("evolution_context_lines_cap") is None:
                errors.append("evolution_context_lines_cap required when slice applied")

        selected = context_slice.get("selected_facts")
        ak_cap = context_slice.get("evolution_ak_cap")
        hard_cap = context_slice.get("hard_cap", HARD_CAP_DEFAULT)
        if (
            context_slice.get("evolution_slice_applied") is True
            and isinstance(selected, list)
            and isinstance(ak_cap, int)
            and len(selected) > ak_cap
        ):
            errors.append("selected_facts exceeds evolution_ak_cap")

        if isinstance(selected, list) and isinstance(hard_cap, int) and len(selected) > hard_cap:
            errors.append("selected_facts exceeds hard_cap")

    forbidden = set(context_slice.keys()) & {
        "blocked_effects",
        "stage_effects_ref",
        "evolution_score_snapshot_id",
        "allowed_effects",
        "effect_limits",
    }
    if forbidden:
        errors.append(f"forbidden evolution policy fields on context slice: {sorted(forbidden)}")

    extra = set(context_slice.keys()) - KNOWLEDGE_CONTEXT_SLICE_V1_WITH_EVOLUTION_KEYS
    if extra:
        errors.append(f"unexpected fields: {sorted(extra)}")

    return errors
