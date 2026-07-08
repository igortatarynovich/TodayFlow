"""A1.8 — Branch A hot path wiring helpers for `build_today_narrative`."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.services.day_model_v1_active_knowledge_loader import (
    load_user_active_knowledge_list_v1,
)

NARRATIVE_SURFACE_TO_KNOWLEDGE_TARGET: dict[str, str] = {
    "guide": "day_guidance_card",
    "day_layer": "day_guidance_card",
    "spheres": "day_guidance_card",
    "evening": "reflection_card",
    "deepen": "day_guidance_card",
}

DEFAULT_KNOWLEDGE_TARGET_SURFACE = "day_guidance_card"


def narrative_surface_to_knowledge_target(surface: str) -> str:
    normalized = (surface or "").strip().lower()
    return NARRATIVE_SURFACE_TO_KNOWLEDGE_TARGET.get(
        normalized, DEFAULT_KNOWLEDGE_TARGET_SURFACE
    )


def resolve_active_knowledge_for_narrative(
    db: Session,
    user_id: int,
    *,
    surface: str,
) -> tuple[list[dict[str, Any]] | None, str]:
    """
    Load Active Knowledge for narrative DayContext.

    Returns (None, target_surface) when pool empty — preserves legacy DayContext hash.
    """
    target_surface = narrative_surface_to_knowledge_target(surface)
    records = load_user_active_knowledge_list_v1(db, user_id)
    if not records:
        return None, target_surface
    return records, target_surface


def slim_knowledge_usage_metrics_for_log(metrics_trace: dict[str, Any]) -> dict[str, Any]:
    """Compact metrics for GenerationLog — counts and gate outcomes only."""
    selection = metrics_trace.get("selection_metrics") or {}
    personalization = metrics_trace.get("personalization_metrics") or {}
    usage_gate = metrics_trace.get("usage_gate_metrics") or {}
    p19 = metrics_trace.get("p19_metrics") or {}
    minimum = metrics_trace.get("minimum_metrics") or build_minimum_metrics_v1(
        selection_metrics=selection,
        personalization_metrics=personalization,
        usage_gate_metrics=usage_gate,
        p19_metrics=p19,
    )
    trace = metrics_trace.get("traceability") or {}

    return {
        "metrics_trace_id": metrics_trace.get("metrics_trace_id"),
        "target_surface": metrics_trace.get("target_surface"),
        "minimum_metrics": minimum,
        "selection_metrics": {
            "pool_count": selection.get("pool_count"),
            "eligible_count": selection.get("eligible_count"),
            "selected_count": selection.get("selected_count"),
            "excluded_count": selection.get("excluded_count"),
            "excluded_by_reason": selection.get("excluded_by_reason"),
            "selection_duration_ms": selection.get("selection_duration_ms"),
        },
        "day_engine_metrics": metrics_trace.get("day_engine_metrics"),
        "personalization_metrics": {
            "result": personalization.get("result"),
            "summary_fact_count": personalization.get("summary_fact_count"),
        },
        "usage_gate_metrics": {
            "evaluated": usage_gate.get("evaluated"),
            "decision": usage_gate.get("decision"),
            "deny_reason": usage_gate.get("deny_reason"),
            "context_depth_at_gate": usage_gate.get("context_depth_at_gate"),
        },
        "p19_metrics": {
            "context_slice_built": p19.get("context_slice_built"),
            "context_depth": p19.get("context_depth"),
            "personalization_in_slice": p19.get("personalization_in_slice"),
            "personalization_fact_count": p19.get("personalization_fact_count"),
            "gate_cut_personalization": p19.get("gate_cut_personalization"),
            "gate_cut_reason": p19.get("gate_cut_reason"),
        },
        "stage_coverage": metrics_trace.get("stage_coverage"),
        "traceability": {
            "context_slice_id": trace.get("context_slice_id"),
            "usage_gate_id": trace.get("usage_gate_id"),
            "llm_context_slice_id": trace.get("llm_context_slice_id"),
        },
    }


def try_build_p19_context_from_narrative_day_context(
    day_ctx: dict[str, Any],
    precall_record: dict[str, Any],
    render: dict[str, Any],
    evaluation: dict[str, Any],
    *,
    surface: str | None = None,
) -> dict[str, Any] | None:
    """
    P1.9 entry for narrative hot path — passes `day_context_layers` with metrics enrich.
    """
    layers = day_ctx.get("layers")
    if not isinstance(layers, dict):
        return None

    from todayflow_backend.services.day_model_v1_llm_context_slice import (
        maybe_build_llm_context_slice_v1,
    )

    target = surface or DEFAULT_KNOWLEDGE_TARGET_SURFACE
    return maybe_build_llm_context_slice_v1(
        precall_record,
        render,
        evaluation,
        surface=target,
        day_context_layers=layers,
    )
