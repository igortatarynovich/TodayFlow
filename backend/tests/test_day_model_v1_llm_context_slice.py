"""P1.9 — LLM context slice contract tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.day_content_registry_loader import clear_day_content_registry_cache
from todayflow_backend.data.reference_machine_loader import clear_reference_machine_cache
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
from todayflow_backend.services.day_model_v1_llm_call_gate import (
    CONTEXT_DEPTH_MINIMAL,
    CONTEXT_DEPTH_NONE,
    CONTEXT_DEPTH_STANDARD,
    DECISION_CALL_LLM,
    DECISION_NO_CALL,
    decide_day_content_llm_call_v1,
)
from todayflow_backend.services.day_model_v1_llm_context_slice import (
    DAY_LLM_CONTEXT_SLICE_V1_CONTRACT,
    DAY_LLM_CONTEXT_SLICE_V1_KEYS,
    DayModelContextSliceError,
    build_llm_context_slice_v1,
    maybe_build_llm_context_slice_v1,
)
from todayflow_backend.services.day_model_v1_llm_request_record import (
    build_llm_precall_record_v1,
    generate_generation_id,
    maybe_build_llm_precall_record_v1,
)
from tests.test_cross_domain_machine_validation import (
    ANCHOR_NUMEROLOGY,
    ANCHOR_PLANET,
    ANCHOR_SIGN,
    ANCHOR_TAROT,
)

REF_IDS = {
    "render_id": "render-test-001",
    "package_id": "package-test-001",
    "evaluation_id": "evaluation-test-001",
    "context_slice_id": "context-slice-test-001",
}


@pytest.fixture(autouse=True)
def _clear_caches():
    clear_reference_machine_cache()
    clear_day_content_registry_cache()
    yield
    clear_reference_machine_cache()
    clear_day_content_registry_cache()


def _call_llm_pipeline(surface="day_guidance_card"):
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
    gate = decide_day_content_llm_call_v1(render, evaluation, surface=surface)
    assert gate["decision"] == DECISION_CALL_LLM
    generation_id = generate_generation_id()
    precall = build_llm_precall_record_v1(
        gate,
        generation_id=generation_id,
        surface=surface,
        **REF_IDS,
    )
    return precall, render, evaluation, gate


def test_none_context_has_no_user_data():
    precall, render, evaluation, gate = _call_llm_pipeline()
    depth = gate["allowed_context_depth"]
    if depth != CONTEXT_DEPTH_NONE:
        depth = CONTEXT_DEPTH_NONE
    slice_ = build_llm_context_slice_v1(
        precall, render, evaluation, surface="day_guidance_card", context_depth=depth
    )
    assert slice_["context_depth"] == CONTEXT_DEPTH_NONE
    assert slice_["surface_context"] == {}
    blob = str(slice_)
    assert "core_profile" not in blob
    assert "behavior_logs" not in blob


def test_minimal_context_no_raw_profile():
    precall, render, evaluation, _ = _call_llm_pipeline()
    slice_ = build_llm_context_slice_v1(
        precall,
        render,
        evaluation,
        surface="day_guidance_card",
        context_depth=CONTEXT_DEPTH_MINIMAL,
    )
    assert "safe_personalization_summary" not in slice_["surface_context"]
    assert slice_["surface_context"]["surface_purpose"]
    assert "profile" not in str(slice_["surface_context"]).lower()


def test_standard_context_only_safe_summary():
    precall, render, evaluation, _ = _call_llm_pipeline()
    facts = [
        "Prefers concise morning planning",
        "Recently completed a long project phase",
    ]
    slice_ = build_llm_context_slice_v1(
        precall,
        render,
        evaluation,
        surface="day_guidance_card",
        context_depth=CONTEXT_DEPTH_STANDARD,
        safe_personalization_summary=facts,
    )
    summary = slice_["surface_context"]["safe_personalization_summary"]
    assert summary == facts
    assert len(summary) <= 5
    assert "core_profile" not in str(summary)


def test_context_linked_to_generation_id():
    precall, render, evaluation, _ = _call_llm_pipeline()
    slice_ = build_llm_context_slice_v1(
        precall, render, evaluation, surface="day_guidance_card", context_depth=CONTEXT_DEPTH_MINIMAL
    )
    assert slice_["generation_id"] == precall["generation_id"]
    assert slice_["context_slice_id"] == precall["context_slice_id"]


def test_context_contains_only_target_surface():
    precall, render, evaluation, _ = _call_llm_pipeline()
    slice_ = build_llm_context_slice_v1(
        precall, render, evaluation, surface="day_guidance_card", context_depth=CONTEXT_DEPTH_MINIMAL
    )
    assert slice_["render_surface"]["surface_id"] == "day_guidance_card"
    assert "today_hero" not in slice_["render_surface"]


def test_forbidden_operations_always_present():
    precall, render, evaluation, _ = _call_llm_pipeline()
    slice_ = build_llm_context_slice_v1(
        precall, render, evaluation, surface="day_guidance_card", context_depth=CONTEXT_DEPTH_MINIMAL
    )
    forbidden = set(slice_["forbidden_operations"])
    assert "invent" in forbidden
    assert "add_tarot" in forbidden
    assert "add_astrology" in forbidden


def test_source_keys_preserved():
    precall, render, evaluation, _ = _call_llm_pipeline()
    slice_ = build_llm_context_slice_v1(
        precall, render, evaluation, surface="day_guidance_card", context_depth=CONTEXT_DEPTH_MINIMAL
    )
    render_keys = [
        entry["key"] for entry in render["surfaces"]["day_guidance_card"]["entries"]
    ]
    assert slice_["source_keys"] == render_keys
    assert all(key.startswith("day.") for key in slice_["source_keys"])


def test_missing_trace_ids_invalid():
    precall, render, evaluation, _ = _call_llm_pipeline()
    broken = copy.deepcopy(precall)
    broken["render_id"] = ""
    with pytest.raises(DayModelContextSliceError):
        build_llm_context_slice_v1(
            broken, render, evaluation, surface="day_guidance_card", context_depth=CONTEXT_DEPTH_MINIMAL
        )


def test_no_call_and_blocked_do_not_create_slice():
    dm = aggregate_day_model_v1(
        tarot_entity_code=ANCHOR_TAROT,
        numerology_entity_code=ANCHOR_NUMEROLOGY,
        astrology_planet_code=ANCHOR_PLANET,
        astrology_sign_code=ANCHOR_SIGN,
    )
    interpretation = interpret_day_model_v1(dm)
    mapping = map_day_model_interpretation_to_content_keys(interpretation)
    resolution = resolve_content_entries_from_mapping(mapping)
    package = assemble_day_model_v1 if False else assemble_day_content_package_v1(
        interpretation, mapping, resolution
    )
    evaluation = evaluate_day_content_package_v1(package)
    render = render_day_content_package_v1(package, evaluation)

    no_call_gate = decide_day_content_llm_call_v1(render, evaluation, surface="today_hero")
    assert no_call_gate["decision"] == DECISION_NO_CALL
    assert maybe_build_llm_precall_record_v1(
        no_call_gate,
        generation_id=generate_generation_id(),
        surface="today_hero",
        **REF_IDS,
    ) is None
    assert maybe_build_llm_context_slice_v1(None, render, evaluation, surface="today_hero") is None

    broken_package = copy.deepcopy(package)
    broken_package["risk_warning"] = None
    blocked_eval = evaluate_day_content_package_v1(broken_package)
    blocked_render = render_day_content_package_v1(broken_package, blocked_eval)
    blocked_gate = decide_day_content_llm_call_v1(blocked_render, blocked_eval, surface="today_hero")
    assert blocked_gate["decision"] == "blocked"
    assert maybe_build_llm_context_slice_v1(None, blocked_render, blocked_eval, surface="today_hero") is None


def test_output_shape_stable():
    precall, render, evaluation, _ = _call_llm_pipeline()
    slice_ = build_llm_context_slice_v1(
        precall, render, evaluation, surface="day_guidance_card", context_depth=CONTEXT_DEPTH_MINIMAL
    )
    assert set(slice_.keys()) == DAY_LLM_CONTEXT_SLICE_V1_KEYS
    assert slice_["contract_version"] == DAY_LLM_CONTEXT_SLICE_V1_CONTRACT
    assert slice_["status"] == "ready"
