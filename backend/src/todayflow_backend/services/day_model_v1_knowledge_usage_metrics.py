"""A1.7 — Branch A knowledge usage metrics and trace coverage."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.day_model_v1_day_engine_knowledge_integration import (
    DAY_ENGINE_KNOWLEDGE_INPUT_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_day_engine_knowledge_wiring import (
    DAY_ENGINE_KNOWLEDGE_WIRING_RESULT_V1_CONTRACT,
    WIRING_RESULT_APPLIED,
    WIRING_RESULT_NOOP,
    WIRING_RESULT_REJECTED,
)
from todayflow_backend.services.day_model_v1_knowledge_context_selection import (
    KNOWLEDGE_CONTEXT_SLICE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_llm_call_gate import CONTEXT_DEPTH_STANDARD
from todayflow_backend.services.day_model_v1_llm_context_slice import (
    DAY_LLM_CONTEXT_SLICE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_personalization_usage_gate import (
    PERSONALIZATION_USAGE_GATE_V1_CONTRACT,
    USAGE_DECISION_ALLOW,
    USAGE_DECISION_DENY,
)
from todayflow_backend.services.day_model_v1_profile_knowledge_personalization import (
    PROFILE_KNOWLEDGE_PERSONALIZATION_V1_CONTRACT,
)

KNOWLEDGE_USAGE_METRICS_TRACE_V1_CONTRACT = "knowledge_usage_metrics_trace_v1"
METRICS_POLICY_VERSION = "1.1.0"

# Canonical minimum metrics (A1.7) — flat names for logs/dashboards.
MINIMUM_METRIC_KNOWLEDGE_POOL_SIZE = "knowledge_pool_size"
MINIMUM_METRIC_ELIGIBLE_COUNT = "eligible_knowledge_count"
MINIMUM_METRIC_SELECTED_COUNT = "selected_knowledge_count"
MINIMUM_METRIC_EXCLUDED_COUNT = "excluded_knowledge_count"
MINIMUM_METRIC_EXCLUSION_REASONS = "exclusion_reasons"
MINIMUM_METRIC_PERSONALIZATION_LINES = "personalization_summary_lines"
MINIMUM_METRIC_GATE_DECISION = "personalization_gate_decision"
MINIMUM_METRIC_GATE_REASON = "personalization_gate_reason"
MINIMUM_METRIC_CONTEXT_SLICE_PERSONALIZED = "context_slice_personalized"
MINIMUM_METRIC_LLM_CONTEXT_DEPTH = "llm_context_depth"

MINIMUM_METRICS_V1_KEYS = frozenset(
    {
        MINIMUM_METRIC_KNOWLEDGE_POOL_SIZE,
        MINIMUM_METRIC_ELIGIBLE_COUNT,
        MINIMUM_METRIC_SELECTED_COUNT,
        MINIMUM_METRIC_EXCLUDED_COUNT,
        MINIMUM_METRIC_EXCLUSION_REASONS,
        MINIMUM_METRIC_PERSONALIZATION_LINES,
        MINIMUM_METRIC_GATE_DECISION,
        MINIMUM_METRIC_GATE_REASON,
        MINIMUM_METRIC_CONTEXT_SLICE_PERSONALIZED,
        MINIMUM_METRIC_LLM_CONTEXT_DEPTH,
    }
)

METRICS_STATUS_READY = "ready"

STAGE_A1_1 = "a1_1_selection"
STAGE_A1_2 = "a1_2_integration"
STAGE_A1_3 = "a1_3_wiring"
STAGE_A1_4 = "a1_4_personalization"
STAGE_A1_5 = "a1_5_usage_gate"
STAGE_A1_6 = "a1_6_p19_wire"

KNOWLEDGE_USAGE_METRICS_TRACE_V1_KEYS = frozenset(
    {
        "contract_version",
        "metrics_trace_id",
        "target_surface",
        "selection_metrics",
        "day_engine_metrics",
        "personalization_metrics",
        "usage_gate_metrics",
        "p19_metrics",
        "minimum_metrics",
        "stage_coverage",
        "traceability",
        "status",
        "created_at",
        "profile_update_allowed",
        "memory_update_allowed",
        "ranking_model_update_allowed",
    }
)


class KnowledgeUsageMetricsError(ValueError):
    """Raised when metrics trace inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _empty_selection_metrics() -> dict[str, Any]:
    return {
        "pool_count": 0,
        "eligible_count": 0,
        "selected_count": 0,
        "excluded_count": 0,
        "exclusion_reasons": [],
        "excluded_by_reason": {},
        "selection_duration_ms": None,
        "soft_cap": None,
        "hard_cap": None,
    }


def _empty_day_engine_metrics() -> dict[str, Any]:
    return {
        "integration_created": False,
        "hint_count": 0,
        "wiring_result": None,
        "hints_applied_count": 0,
        "presentation_adjusted": False,
    }


def _empty_personalization_metrics() -> dict[str, Any]:
    return {
        "result": None,
        "summary_fact_count": 0,
        "included_count": 0,
    }


def _empty_usage_gate_metrics() -> dict[str, Any]:
    return {
        "evaluated": False,
        "decision": None,
        "deny_reason": None,
        "allowed_fact_count": 0,
        "context_depth_at_gate": None,
    }


def _empty_p19_metrics() -> dict[str, Any]:
    return {
        "context_slice_built": False,
        "context_depth": None,
        "personalization_in_slice": False,
        "personalization_fact_count": 0,
        "gate_cut_personalization": False,
        "gate_cut_reason": None,
    }


def _empty_minimum_metrics() -> dict[str, Any]:
    return {
        MINIMUM_METRIC_KNOWLEDGE_POOL_SIZE: 0,
        MINIMUM_METRIC_ELIGIBLE_COUNT: 0,
        MINIMUM_METRIC_SELECTED_COUNT: 0,
        MINIMUM_METRIC_EXCLUDED_COUNT: 0,
        MINIMUM_METRIC_EXCLUSION_REASONS: [],
        MINIMUM_METRIC_PERSONALIZATION_LINES: 0,
        MINIMUM_METRIC_GATE_DECISION: None,
        MINIMUM_METRIC_GATE_REASON: None,
        MINIMUM_METRIC_CONTEXT_SLICE_PERSONALIZED: False,
        MINIMUM_METRIC_LLM_CONTEXT_DEPTH: None,
    }


def build_minimum_metrics_v1(
    *,
    selection_metrics: dict[str, Any] | None = None,
    personalization_metrics: dict[str, Any] | None = None,
    usage_gate_metrics: dict[str, Any] | None = None,
    p19_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Canonical flat metrics for Branch A observability (read-only derived view).

    Does not alter selection, gates, or prompts.
    """
    selection = selection_metrics or {}
    personalization = personalization_metrics or {}
    usage_gate = usage_gate_metrics or {}
    p19 = p19_metrics or {}

    gate_decision = None
    gate_reason = None
    if usage_gate.get("evaluated"):
        gate_decision = usage_gate.get("decision")
        gate_reason = usage_gate.get("deny_reason")

    llm_depth = None
    if p19.get("context_slice_built"):
        llm_depth = p19.get("context_depth")
    elif usage_gate.get("evaluated"):
        llm_depth = usage_gate.get("context_depth_at_gate")

    return {
        MINIMUM_METRIC_KNOWLEDGE_POOL_SIZE: selection.get("pool_count", 0),
        MINIMUM_METRIC_ELIGIBLE_COUNT: selection.get("eligible_count", 0),
        MINIMUM_METRIC_SELECTED_COUNT: selection.get("selected_count", 0),
        MINIMUM_METRIC_EXCLUDED_COUNT: selection.get("excluded_count", 0),
        MINIMUM_METRIC_EXCLUSION_REASONS: list(selection.get("exclusion_reasons") or []),
        MINIMUM_METRIC_PERSONALIZATION_LINES: personalization.get("summary_fact_count", 0),
        MINIMUM_METRIC_GATE_DECISION: gate_decision,
        MINIMUM_METRIC_GATE_REASON: gate_reason,
        MINIMUM_METRIC_CONTEXT_SLICE_PERSONALIZED: bool(p19.get("personalization_in_slice")),
        MINIMUM_METRIC_LLM_CONTEXT_DEPTH: llm_depth,
    }


def _attach_minimum_metrics(metrics_trace: dict[str, Any]) -> dict[str, Any]:
    metrics_trace["minimum_metrics"] = build_minimum_metrics_v1(
        selection_metrics=metrics_trace.get("selection_metrics"),
        personalization_metrics=metrics_trace.get("personalization_metrics"),
        usage_gate_metrics=metrics_trace.get("usage_gate_metrics"),
        p19_metrics=metrics_trace.get("p19_metrics"),
    )
    return metrics_trace


def _empty_stage_coverage() -> dict[str, bool]:
    return {
        STAGE_A1_1: False,
        STAGE_A1_2: False,
        STAGE_A1_3: False,
        STAGE_A1_4: False,
        STAGE_A1_5: False,
        STAGE_A1_6: False,
    }


def _count_excluded_by_reason(excluded_facts: list[Any]) -> dict[str, int]:
    reasons: list[str] = []
    for item in excluded_facts:
        if isinstance(item, dict) and item.get("reason"):
            reasons.append(str(item["reason"]))
    return dict(Counter(reasons))


def _build_selection_metrics(
    context_slice: dict[str, Any] | None,
    *,
    pool_count: int | None = None,
) -> dict[str, Any]:
    if not isinstance(context_slice, dict):
        return _empty_selection_metrics()

    trace = context_slice.get("traceability") or {}
    excluded_facts = context_slice.get("excluded_facts") or []
    return {
        "pool_count": pool_count if pool_count is not None else trace.get("pool_count", 0),
        "eligible_count": trace.get("eligible_count", 0),
        "selected_count": trace.get("selected_count", 0),
        "excluded_count": trace.get("excluded_count", len(excluded_facts)),
        "exclusion_reasons": list(context_slice.get("exclusion_reasons") or []),
        "excluded_by_reason": _count_excluded_by_reason(excluded_facts),
        "selection_duration_ms": trace.get("selection_duration_ms"),
        "soft_cap": context_slice.get("soft_cap"),
        "hard_cap": context_slice.get("hard_cap"),
    }


def _build_day_engine_metrics(
    knowledge_input: dict[str, Any] | None,
    wiring_result: dict[str, Any] | None,
) -> dict[str, Any]:
    metrics = _empty_day_engine_metrics()

    if isinstance(knowledge_input, dict):
        if knowledge_input.get("contract_version") == DAY_ENGINE_KNOWLEDGE_INPUT_V1_CONTRACT:
            hints = knowledge_input.get("hints") or []
            metrics["integration_created"] = True
            metrics["hint_count"] = len(hints) if isinstance(hints, list) else 0

    if not isinstance(wiring_result, dict):
        return metrics

    if wiring_result.get("contract_version") != DAY_ENGINE_KNOWLEDGE_WIRING_RESULT_V1_CONTRACT:
        return metrics

    applied = wiring_result.get("applied")
    hints_applied = wiring_result.get("knowledge_hints_applied") or []
    presentation = wiring_result.get("presentation_adjustments") or {}

    if applied is True:
        metrics["wiring_result"] = WIRING_RESULT_APPLIED
    elif applied is False and presentation.get("noop"):
        metrics["wiring_result"] = WIRING_RESULT_NOOP
    else:
        metrics["wiring_result"] = WIRING_RESULT_NOOP if applied is False else WIRING_RESULT_REJECTED

    metrics["hints_applied_count"] = (
        len(hints_applied) if isinstance(hints_applied, list) else 0
    )
    metrics["presentation_adjusted"] = bool(
        presentation.get("do_items_trimmed")
        or presentation.get("subline_clipped")
        or (
            metrics["wiring_result"] == WIRING_RESULT_APPLIED
            and metrics["hints_applied_count"] > 0
        )
    )
    return metrics


def _build_personalization_metrics(
    personalization: dict[str, Any] | None,
    profile_selector: dict[str, Any] | None,
) -> dict[str, Any]:
    metrics = _empty_personalization_metrics()

    if isinstance(personalization, dict):
        if (
            personalization.get("contract_version")
            == PROFILE_KNOWLEDGE_PERSONALIZATION_V1_CONTRACT
        ):
            summary = personalization.get("safe_personalization_summary") or []
            metrics["summary_fact_count"] = len(summary) if isinstance(summary, list) else 0
            trace = personalization.get("traceability") or {}
            metrics["included_count"] = trace.get("included_count", metrics["summary_fact_count"])
            if metrics["summary_fact_count"] > 0:
                metrics["result"] = "created"
            else:
                metrics["result"] = "empty"
    elif isinstance(profile_selector, dict):
        summary = profile_selector.get("safe_personalization_summary") or []
        if isinstance(summary, list):
            metrics["summary_fact_count"] = len(summary)
            metrics["included_count"] = len(summary)
            metrics["result"] = "created" if summary else "empty"

    if isinstance(profile_selector, dict) and profile_selector.get("knowledge_personalization_error"):
        metrics["result"] = "rejected"

    return metrics


def _build_traceability(
    *,
    context_slice: dict[str, Any] | None,
    knowledge_input: dict[str, Any] | None,
    wiring_result: dict[str, Any] | None,
    personalization: dict[str, Any] | None,
    usage_gate: dict[str, Any] | None,
    llm_context_slice: dict[str, Any] | None,
) -> dict[str, Any]:
    trace: dict[str, Any] = {
        "metrics_policy_version": METRICS_POLICY_VERSION,
    }
    if isinstance(context_slice, dict):
        trace["context_slice_id"] = context_slice.get("context_slice_id")
    if isinstance(knowledge_input, dict):
        trace["integration_id"] = knowledge_input.get("integration_id")
    if isinstance(wiring_result, dict):
        trace["wiring_id"] = wiring_result.get("wiring_id")
    if isinstance(personalization, dict):
        trace["personalization_id"] = personalization.get("personalization_id")
    if isinstance(usage_gate, dict):
        trace["usage_gate_id"] = usage_gate.get("usage_gate_id")
    if isinstance(llm_context_slice, dict):
        trace["llm_context_slice_id"] = llm_context_slice.get("context_slice_id")
        slice_trace = llm_context_slice.get("traceability") or {}
        if slice_trace.get("personalization_usage_gate_id"):
            trace["usage_gate_id"] = slice_trace["personalization_usage_gate_id"]
    return trace


def try_build_knowledge_usage_metrics_from_layers(
    layers: dict[str, Any],
    *,
    pool_count: int | None = None,
    target_surface: str | None = None,
    created_at: str | None = None,
    metrics_trace_id: str | None = None,
) -> dict[str, Any]:
    """
    Build A1.7 metrics snapshot from DayContext layers (A1.1–A1.4).

    Does not evaluate usage gate or P1.9 — use enrich helpers after LLM path.
    """
    context_slice = layers.get("knowledge_context_slice")
    knowledge_input = layers.get("day_engine_knowledge_input")
    wiring_result = layers.get("day_engine_knowledge_wiring")
    personalization = layers.get("profile_knowledge_personalization")
    profile_selector = layers.get("profile_selector")

    surface = target_surface
    if isinstance(context_slice, dict) and not surface:
        surface = context_slice.get("target_surface")

    stage_coverage = _empty_stage_coverage()
    if isinstance(context_slice, dict):
        if context_slice.get("contract_version") == KNOWLEDGE_CONTEXT_SLICE_V1_CONTRACT:
            stage_coverage[STAGE_A1_1] = True
    if isinstance(knowledge_input, dict):
        if knowledge_input.get("contract_version") == DAY_ENGINE_KNOWLEDGE_INPUT_V1_CONTRACT:
            stage_coverage[STAGE_A1_2] = True
    if isinstance(wiring_result, dict):
        if wiring_result.get("contract_version") == DAY_ENGINE_KNOWLEDGE_WIRING_RESULT_V1_CONTRACT:
            stage_coverage[STAGE_A1_3] = True
    if isinstance(personalization, dict) or (
        isinstance(profile_selector, dict)
        and "safe_personalization_summary" in profile_selector
    ):
        stage_coverage[STAGE_A1_4] = True

    metrics_trace = {
        "contract_version": KNOWLEDGE_USAGE_METRICS_TRACE_V1_CONTRACT,
        "metrics_trace_id": metrics_trace_id or generate_metrics_trace_id(),
        "target_surface": surface or "day_guidance_card",
        "selection_metrics": _build_selection_metrics(
            context_slice if isinstance(context_slice, dict) else None,
            pool_count=pool_count,
        ),
        "day_engine_metrics": _build_day_engine_metrics(
            knowledge_input if isinstance(knowledge_input, dict) else None,
            wiring_result if isinstance(wiring_result, dict) else None,
        ),
        "personalization_metrics": _build_personalization_metrics(
            personalization if isinstance(personalization, dict) else None,
            profile_selector if isinstance(profile_selector, dict) else None,
        ),
        "usage_gate_metrics": _empty_usage_gate_metrics(),
        "p19_metrics": _empty_p19_metrics(),
        "stage_coverage": stage_coverage,
        "traceability": _build_traceability(
            context_slice=context_slice if isinstance(context_slice, dict) else None,
            knowledge_input=knowledge_input if isinstance(knowledge_input, dict) else None,
            wiring_result=wiring_result if isinstance(wiring_result, dict) else None,
            personalization=personalization if isinstance(personalization, dict) else None,
            usage_gate=None,
            llm_context_slice=None,
        ),
        "status": METRICS_STATUS_READY,
        "created_at": created_at or _utc_now_iso(),
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_model_update_allowed": False,
    }
    _attach_minimum_metrics(metrics_trace)

    errors = validate_knowledge_usage_metrics_trace_v1(metrics_trace)
    if errors:
        raise KnowledgeUsageMetricsError("; ".join(errors))

    return metrics_trace


def enrich_knowledge_usage_metrics_with_usage_gate(
    metrics_trace: dict[str, Any],
    usage_gate: dict[str, Any] | None,
    *,
    llm_gate_context_depth: str | None = None,
) -> dict[str, Any]:
    """Record A1.5 usage gate outcome on metrics trace."""
    updated = dict(metrics_trace)
    stage_coverage = dict(updated.get("stage_coverage") or _empty_stage_coverage())
    gate_metrics = _empty_usage_gate_metrics()
    gate_metrics["evaluated"] = usage_gate is not None
    gate_metrics["context_depth_at_gate"] = llm_gate_context_depth

    if isinstance(usage_gate, dict):
        if usage_gate.get("contract_version") == PERSONALIZATION_USAGE_GATE_V1_CONTRACT:
            stage_coverage[STAGE_A1_5] = True
            gate_metrics["decision"] = usage_gate.get("decision")
            gate_metrics["allowed_fact_count"] = usage_gate.get("allowed_fact_count", 0)
            if usage_gate.get("decision") == USAGE_DECISION_DENY:
                gate_metrics["deny_reason"] = usage_gate.get("reason")
            if llm_gate_context_depth is None:
                gate_metrics["context_depth_at_gate"] = usage_gate.get(
                    "llm_gate_context_depth"
                )

    updated["usage_gate_metrics"] = gate_metrics
    updated["stage_coverage"] = stage_coverage
    trace = dict(updated.get("traceability") or {})
    if isinstance(usage_gate, dict):
        trace["usage_gate_id"] = usage_gate.get("usage_gate_id")
    updated["traceability"] = trace
    return _attach_minimum_metrics(updated)


def enrich_knowledge_usage_metrics_with_p19_context_slice(
    metrics_trace: dict[str, Any],
    llm_context_slice: dict[str, Any] | None,
    *,
    usage_gate: dict[str, Any] | None = None,
    llm_gate_context_depth: str | None = None,
) -> dict[str, Any]:
    """Record A1.6 / P1.9 outcome — when summary entered context slice."""
    updated = enrich_knowledge_usage_metrics_with_usage_gate(
        metrics_trace,
        usage_gate,
        llm_gate_context_depth=llm_gate_context_depth,
    )
    stage_coverage = dict(updated.get("stage_coverage") or _empty_stage_coverage())
    p19_metrics = _empty_p19_metrics()

    if isinstance(llm_context_slice, dict):
        if llm_context_slice.get("contract_version") == DAY_LLM_CONTEXT_SLICE_V1_CONTRACT:
            stage_coverage[STAGE_A1_6] = True
            p19_metrics["context_slice_built"] = True
            depth = llm_context_slice.get("context_depth")
            p19_metrics["context_depth"] = depth

            surface_context = llm_context_slice.get("surface_context") or {}
            facts = surface_context.get("safe_personalization_summary")
            if isinstance(facts, list):
                p19_metrics["personalization_fact_count"] = len(facts)
                p19_metrics["personalization_in_slice"] = len(facts) > 0

            gate_cut = False
            gate_cut_reason = None

            if depth != CONTEXT_DEPTH_STANDARD:
                gate_cut = True
                gate_cut_reason = "context_depth_not_standard"
            elif isinstance(usage_gate, dict):
                if usage_gate.get("decision") == USAGE_DECISION_DENY:
                    gate_cut = True
                    gate_cut_reason = usage_gate.get("reason")
                elif usage_gate.get("decision") == USAGE_DECISION_ALLOW and not p19_metrics[
                    "personalization_in_slice"
                ]:
                    gate_cut = True
                    gate_cut_reason = "empty_summary_after_gate"
            elif not p19_metrics["personalization_in_slice"]:
                gate_cut = True
                gate_cut_reason = "no_personalization_source"

            p19_metrics["gate_cut_personalization"] = gate_cut
            p19_metrics["gate_cut_reason"] = gate_cut_reason

    updated["p19_metrics"] = p19_metrics
    updated["stage_coverage"] = stage_coverage
    trace = dict(updated.get("traceability") or {})
    if isinstance(llm_context_slice, dict):
        trace["llm_context_slice_id"] = llm_context_slice.get("context_slice_id")
    updated["traceability"] = trace

    updated = _attach_minimum_metrics(updated)

    errors = validate_knowledge_usage_metrics_trace_v1(updated)
    if errors:
        raise KnowledgeUsageMetricsError("; ".join(errors))

    return updated


def wire_knowledge_usage_metrics_into_day_context_layers(
    layers: dict[str, Any],
    *,
    pool_count: int | None = None,
    target_surface: str | None = None,
) -> dict[str, Any]:
    """Attach A1.7 metrics trace to DayContext layers after A1.1–A1.4."""
    metrics_trace = try_build_knowledge_usage_metrics_from_layers(
        layers,
        pool_count=pool_count,
        target_surface=target_surface,
    )
    layers["knowledge_usage_metrics_trace"] = metrics_trace
    return metrics_trace


def generate_metrics_trace_id() -> str:
    return f"kumt-{uuid4()}"


def validate_knowledge_usage_metrics_trace_v1(metrics_trace: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if metrics_trace.get("contract_version") != KNOWLEDGE_USAGE_METRICS_TRACE_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in KNOWLEDGE_USAGE_METRICS_TRACE_V1_KEYS:
        if key not in metrics_trace:
            errors.append(f"missing field: {key}")

    if metrics_trace.get("status") != METRICS_STATUS_READY:
        errors.append("status must be ready")

    for flag in (
        "profile_update_allowed",
        "memory_update_allowed",
        "ranking_model_update_allowed",
    ):
        if metrics_trace.get(flag) is not False:
            errors.append(f"{flag} must be false")

    selection = metrics_trace.get("selection_metrics") or {}
    for field in (
        "pool_count",
        "eligible_count",
        "selected_count",
        "excluded_count",
    ):
        if field not in selection:
            errors.append(f"selection_metrics missing {field}")

    stage_coverage = metrics_trace.get("stage_coverage") or {}
    for stage in (
        STAGE_A1_1,
        STAGE_A1_2,
        STAGE_A1_3,
        STAGE_A1_4,
        STAGE_A1_5,
        STAGE_A1_6,
    ):
        if stage not in stage_coverage:
            errors.append(f"stage_coverage missing {stage}")

    usage_gate = metrics_trace.get("usage_gate_metrics") or {}
    if usage_gate.get("evaluated") and usage_gate.get("decision") not in {
        USAGE_DECISION_ALLOW,
        USAGE_DECISION_DENY,
        None,
    }:
        errors.append("invalid usage_gate_metrics.decision")

    p19 = metrics_trace.get("p19_metrics") or {}
    if p19.get("context_slice_built") and p19.get("context_depth") is None:
        errors.append("p19_metrics requires context_depth when slice built")

    minimum = metrics_trace.get("minimum_metrics") or {}
    for key in MINIMUM_METRICS_V1_KEYS:
        if key not in minimum:
            errors.append(f"minimum_metrics missing {key}")

    if minimum.get(MINIMUM_METRIC_GATE_DECISION) not in {
        USAGE_DECISION_ALLOW,
        USAGE_DECISION_DENY,
        None,
    }:
        errors.append("invalid minimum_metrics.personalization_gate_decision")

    return errors
