"""A1.6 — Wire safe summary into P1.9 context slice tests."""

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
from todayflow_backend.services.day_model_v1_llm_call_gate import (
    CONTEXT_DEPTH_STANDARD,
    DECISION_CALL_LLM,
)
from todayflow_backend.services.day_model_v1_llm_context_slice import (
    CONTEXT_DEPTH_MINIMAL,
    maybe_build_llm_context_slice_v1,
)
from todayflow_backend.services.day_model_v1_llm_request_record import (
    build_llm_precall_record_v1,
    generate_generation_id,
)
from todayflow_backend.services.day_model_v1_personalization_usage_gate import (
    USAGE_DECISION_ALLOW,
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
    "render_id": "render-a16-001",
    "package_id": "package-a16-001",
    "evaluation_id": "evaluation-a16-001",
    "context_slice_id": "context-a16-001",
}


def _active(**overrides):
    base = {
        "contract_version": DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
        "knowledge_id": "know-a16-001",
        "source_knowledge_candidate_id": "kcand-a16-001",
        "knowledge_type": KNOWLEDGE_TYPE_RESPONSE_STYLE,
        "claim": "responds_to_surface:short_action",
        "confidence": 0.8,
        "evidence_count": 7,
        "evidence_window_days": 21,
        "evidence_signal_ids": [f"lsig-{i}" for i in range(7)],
        "source_pattern_id": "pat-a16-001",
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


def _day_context_layers():
    fusion = {
        "date": "2026-05-31",
        "scores": {"energy": 55},
        "cycle_context": {},
        "activity_context": {},
        "rhythm_context": {"goals": [], "habits": [], "ascetics": [], "diary": {}},
        "recommendations": [],
        "encouragement": "",
    }
    ctx = build_day_context_v0(
        target_date=date(2026, 5, 31),
        locale="ru",
        insight_depth_tier="free",
        core_profile=None,
        fusion_dump=fusion,
        active_knowledge_list=[_active()],
    )
    return ctx["layers"]


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


def test_maybe_build_wires_summary_from_day_context_layers():
    precall, render, evaluation = _standard_precall_pipeline()
    layers = _day_context_layers()

    slice_out = maybe_build_llm_context_slice_v1(
        precall,
        render,
        evaluation,
        surface="day_guidance_card",
        day_context_layers=layers,
    )

    assert slice_out is not None
    assert slice_out["context_depth"] == CONTEXT_DEPTH_STANDARD
    summary = slice_out["surface_context"]["safe_personalization_summary"]
    assert len(summary) >= 1
    assert "short action" in summary[0].lower()
    assert slice_out["traceability"]["personalization_gate_decision"] == USAGE_DECISION_ALLOW
    assert slice_out["traceability"]["personalization_usage_gate_id"]


def test_maybe_build_without_layers_uses_empty_standard_summary():
    precall, render, evaluation = _standard_precall_pipeline()

    slice_out = maybe_build_llm_context_slice_v1(
        precall,
        render,
        evaluation,
        surface="day_guidance_card",
    )

    assert slice_out is not None
    assert slice_out["surface_context"]["safe_personalization_summary"] == []


def test_explicit_summary_bypasses_usage_gate():
    precall, render, evaluation = _standard_precall_pipeline()
    explicit = ["Explicit personalization fact"]

    slice_out = maybe_build_llm_context_slice_v1(
        precall,
        render,
        evaluation,
        surface="day_guidance_card",
        safe_personalization_summary=explicit,
    )

    assert slice_out["surface_context"]["safe_personalization_summary"] == explicit
    assert "personalization_usage_gate_id" not in (slice_out.get("traceability") or {})


def test_layers_with_minimal_gate_depth_no_personalization_in_slice():
    precall, render, evaluation = _standard_precall_pipeline()
    precall = copy.deepcopy(precall)
    precall["gate_decision"]["allowed_context_depth"] = CONTEXT_DEPTH_MINIMAL
    layers = _day_context_layers()

    slice_out = maybe_build_llm_context_slice_v1(
        precall,
        render,
        evaluation,
        surface="day_guidance_card",
        day_context_layers=layers,
    )

    assert slice_out is not None
    assert slice_out["context_depth"] == CONTEXT_DEPTH_MINIMAL
    assert "safe_personalization_summary" not in slice_out["surface_context"]
