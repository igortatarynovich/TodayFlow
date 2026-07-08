"""A1.7 — Knowledge usage metrics and trace coverage tests."""

from __future__ import annotations

import copy
from datetime import date

import pytest

from todayflow_backend.data.day_content_registry_loader import clear_day_content_registry_cache
from todayflow_backend.data.reference_machine_loader import clear_reference_machine_cache
from todayflow_backend.services.day_context import build_day_context_v0
from todayflow_backend.services.day_model_v1_active_knowledge import (
    DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_aggregator import aggregate_day_model_v1
from todayflow_backend.services.day_model_v1_content_assembler import assemble_day_content_package_v1
from todayflow_backend.services.day_model_v1_content_evaluator import (
    RECOMMENDATION_USE_WITH_CAUTION,
    evaluate_day_content_package_v1,
)
from todayflow_backend.services.day_model_v1_content_mapper import (
    map_day_model_interpretation_to_content_keys,
)
from todayflow_backend.services.day_model_v1_content_renderer import render_day_content_package_v1
from todayflow_backend.services.day_model_v1_content_resolver import (
    resolve_content_entries_from_mapping,
)
from todayflow_backend.services.day_model_v1_interpreter import interpret_day_model_v1
from todayflow_backend.services.day_model_v1_knowledge_candidate import (
    KNOWLEDGE_TYPE_RESPONSE_STYLE,
)
from todayflow_backend.services.day_model_v1_knowledge_usage_metrics import (
    KNOWLEDGE_USAGE_METRICS_TRACE_V1_CONTRACT,
    KNOWLEDGE_USAGE_METRICS_TRACE_V1_KEYS,
    MINIMUM_METRICS_V1_KEYS,
    STAGE_A1_1,
    STAGE_A1_4,
    STAGE_A1_5,
    STAGE_A1_6,
    enrich_knowledge_usage_metrics_with_p19_context_slice,
    validate_knowledge_usage_metrics_trace_v1,
    wire_knowledge_usage_metrics_into_day_context_layers,
)
from todayflow_backend.services.day_model_v1_llm_call_gate import (
    CONTEXT_DEPTH_MINIMAL,
    CONTEXT_DEPTH_STANDARD,
    DECISION_CALL_LLM,
)
from todayflow_backend.services.day_model_v1_llm_context_slice import (
    maybe_build_llm_context_slice_v1,
)
from todayflow_backend.services.day_model_v1_llm_request_record import (
    build_llm_precall_record_v1,
    generate_generation_id,
)
from todayflow_backend.services.day_model_v1_personalization_usage_gate import (
    USAGE_DECISION_ALLOW,
    USAGE_DECISION_DENY,
)
from tests.test_cross_domain_machine_validation import (
    ANCHOR_NUMEROLOGY,
    ANCHOR_PLANET,
    ANCHOR_SIGN,
    ANCHOR_TAROT,
)


@pytest.fixture(autouse=True)
def _clear_caches():
    clear_reference_machine_cache()
    clear_day_content_registry_cache()
    yield
    clear_reference_machine_cache()
    clear_day_content_registry_cache()


REF_IDS = {
    "render_id": "render-a17-001",
    "package_id": "package-a17-001",
    "evaluation_id": "evaluation-a17-001",
    "context_slice_id": "context-a17-001",
}


def _active(**overrides):
    base = {
        "contract_version": DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
        "knowledge_id": "know-a17-001",
        "source_knowledge_candidate_id": "kcand-a17-001",
        "knowledge_type": KNOWLEDGE_TYPE_RESPONSE_STYLE,
        "claim": "responds_to_surface:short_action",
        "confidence": 0.8,
        "evidence_count": 7,
        "evidence_window_days": 21,
        "evidence_signal_ids": [f"lsig-{i}" for i in range(7)],
        "source_pattern_id": "pat-a17-001",
        "status": "active",
        "created_at": "2026-05-31T12:00:00Z",
        "last_confirmed_at": "2026-05-31T12:00:00Z",
        "expires_at": None,
        "review_required": False,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_update_allowed": False,
    }
    base.update(overrides)
    return base


def _fusion():
    return {
        "date": "2026-05-31",
        "scores": {"energy": 55},
        "cycle_context": {},
        "activity_context": {},
        "rhythm_context": {"goals": [], "habits": [], "ascetics": [], "diary": {}},
        "recommendations": [],
        "encouragement": "",
    }


def _day_context_with_metrics(active_list=None):
    ctx = build_day_context_v0(
        target_date=date(2026, 5, 31),
        locale="ru",
        insight_depth_tier="free",
        core_profile=None,
        fusion_dump=_fusion(),
        active_knowledge_list=active_list if active_list is not None else [_active()],
    )
    return ctx


def _standard_precall_pipeline():
    dm = aggregate_day_model_v1(
        tarot_entity_code=ANCHOR_TAROT,
        numerology_entity_code=ANCHOR_NUMEROLOGY,
        astrology_planet_code=ANCHOR_PLANET,
        astrology_sign_code=ANCHOR_SIGN,
    )
    interpretation = interpret_day_model_v1(dm)
    mapping = map_day_model_interpretation_to_content_keys(interpretation)
    resolution = resolve_content_entries_from_mapping(mapping)
    package = assemble_day_content_package_v1(interpretation, mapping, resolution)
    evaluation = evaluate_day_content_package_v1(package)
    render = render_day_content_package_v1(package, evaluation)
    evaluation = copy.deepcopy(evaluation)
    evaluation["recommendation"] = RECOMMENDATION_USE_WITH_CAUTION
    evaluation["degraded"] = True

    gate = {
        "contract_version": "day_content_llm_gate_v1",
        "surface": "day_guidance_card",
        "decision": DECISION_CALL_LLM,
        "reason": "test",
        "allowed_context_depth": CONTEXT_DEPTH_STANDARD,
        "allowed_model_tier": "standard",
        "max_tokens": 256,
        "save_required": True,
        "dataset_candidate": True,
    }
    precall = build_llm_precall_record_v1(
        gate,
        generation_id=generate_generation_id(),
        surface="day_guidance_card",
        **REF_IDS,
    )
    return precall, render, evaluation


def test_day_context_layers_include_metrics_trace():
    ctx = _day_context_with_metrics()
    metrics = ctx["layers"]["knowledge_usage_metrics_trace"]

    assert metrics["contract_version"] == KNOWLEDGE_USAGE_METRICS_TRACE_V1_CONTRACT
    assert metrics["selection_metrics"]["pool_count"] == 1
    assert metrics["selection_metrics"]["selected_count"] >= 1
    assert metrics["selection_metrics"]["selection_duration_ms"] is not None
    assert metrics["personalization_metrics"]["summary_fact_count"] >= 1
    assert metrics["stage_coverage"][STAGE_A1_1] is True
    assert metrics["stage_coverage"][STAGE_A1_4] is True
    assert metrics["stage_coverage"][STAGE_A1_5] is False
    minimum = metrics["minimum_metrics"]
    assert set(minimum.keys()) == set(MINIMUM_METRICS_V1_KEYS)
    assert minimum["knowledge_pool_size"] == 1
    assert minimum["selected_knowledge_count"] >= 1
    assert minimum["personalization_summary_lines"] >= 1
    assert minimum["personalization_gate_decision"] is None
    assert minimum["context_slice_personalized"] is False
    assert validate_knowledge_usage_metrics_trace_v1(metrics) == []


def test_metrics_shape_stable():
    ctx = _day_context_with_metrics()
    metrics = ctx["layers"]["knowledge_usage_metrics_trace"]
    assert set(metrics.keys()) == set(KNOWLEDGE_USAGE_METRICS_TRACE_V1_KEYS)


def test_excluded_by_reason_aggregation():
    ctx = _day_context_with_metrics(
        active_list=[
            _active(knowledge_id="know-low-001", confidence=0.1, evidence_count=1),
            _active(
                knowledge_id="know-low-002",
                claim="responds_to_surface:long_form",
                confidence=0.1,
                evidence_count=1,
            ),
        ]
    )
    metrics = ctx["layers"]["knowledge_usage_metrics_trace"]
    excluded = metrics["selection_metrics"]["excluded_by_reason"]
    assert isinstance(excluded, dict)
    assert sum(excluded.values()) == metrics["selection_metrics"]["excluded_count"]


def test_enrich_usage_gate_deny_reason():
    ctx = _day_context_with_metrics()
    metrics = ctx["layers"]["knowledge_usage_metrics_trace"]
    usage_gate = {
        "contract_version": "personalization_usage_gate_decision_v1",
        "usage_gate_id": "pug-test-001",
        "surface": "day_guidance_card",
        "decision": USAGE_DECISION_DENY,
        "reason": "context_depth_not_standard",
        "allowed_fact_count": 0,
        "safe_personalization_summary": [],
        "traceability": {},
        "status": "ready",
        "created_at": "2026-05-31T12:00:00Z",
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_model_update_allowed": False,
    }

    enriched = enrich_knowledge_usage_metrics_with_p19_context_slice(
        metrics,
        None,
        usage_gate=usage_gate,
        llm_gate_context_depth=CONTEXT_DEPTH_MINIMAL,
    )

    assert enriched["usage_gate_metrics"]["evaluated"] is True
    assert enriched["usage_gate_metrics"]["decision"] == USAGE_DECISION_DENY
    assert enriched["usage_gate_metrics"]["deny_reason"] == "context_depth_not_standard"
    assert enriched["minimum_metrics"]["personalization_gate_decision"] == USAGE_DECISION_DENY
    assert enriched["minimum_metrics"]["personalization_gate_reason"] == "context_depth_not_standard"
    assert enriched["minimum_metrics"]["llm_context_depth"] == CONTEXT_DEPTH_MINIMAL
    assert enriched["stage_coverage"][STAGE_A1_5] is True


def test_maybe_build_enriches_metrics_on_layers():
    ctx = _day_context_with_metrics()
    layers = ctx["layers"]
    precall, render, evaluation = _standard_precall_pipeline()

    maybe_build_llm_context_slice_v1(
        precall,
        render,
        evaluation,
        surface="day_guidance_card",
        day_context_layers=layers,
    )

    metrics = layers["knowledge_usage_metrics_trace"]
    assert metrics["stage_coverage"][STAGE_A1_5] is True
    assert metrics["stage_coverage"][STAGE_A1_6] is True
    assert metrics["usage_gate_metrics"]["decision"] == USAGE_DECISION_ALLOW
    assert metrics["p19_metrics"]["context_slice_built"] is True
    assert metrics["p19_metrics"]["personalization_in_slice"] is True
    assert metrics["p19_metrics"]["personalization_fact_count"] >= 1
    assert metrics["p19_metrics"]["gate_cut_personalization"] is False


def test_maybe_build_records_gate_cut_on_minimal_depth():
    ctx = _day_context_with_metrics()
    layers = ctx["layers"]
    precall, render, evaluation = _standard_precall_pipeline()
    precall = copy.deepcopy(precall)
    precall["gate_decision"]["allowed_context_depth"] = CONTEXT_DEPTH_MINIMAL

    maybe_build_llm_context_slice_v1(
        precall,
        render,
        evaluation,
        surface="day_guidance_card",
        day_context_layers=layers,
    )

    metrics = layers["knowledge_usage_metrics_trace"]
    assert metrics["p19_metrics"]["context_depth"] == CONTEXT_DEPTH_MINIMAL
    assert metrics["p19_metrics"]["personalization_in_slice"] is False
    assert metrics["p19_metrics"]["gate_cut_personalization"] is True
    assert metrics["p19_metrics"]["gate_cut_reason"] == "context_depth_not_standard"


def test_wire_metrics_without_knowledge_pipeline():
    layers = {"profile_selector": {"safe_personalization_summary": []}}
    metrics = wire_knowledge_usage_metrics_into_day_context_layers(layers)
    assert layers["knowledge_usage_metrics_trace"] is metrics
    assert metrics["selection_metrics"]["pool_count"] == 0
    assert metrics["stage_coverage"][STAGE_A1_1] is False
    assert metrics["stage_coverage"][STAGE_A1_4] is True
    assert validate_knowledge_usage_metrics_trace_v1(metrics) == []
