"""P1.13 — Final surface candidate selection tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.day_content_registry_loader import clear_day_content_registry_cache
from todayflow_backend.data.day_llm_prompt_template_loader import (
    clear_day_llm_prompt_template_registry_cache,
)
from todayflow_backend.data.reference_machine_loader import clear_reference_machine_cache
from todayflow_backend.services.day_model_v1_aggregator import aggregate_day_model_v1
from todayflow_backend.services.day_model_v1_content_assembler import assemble_day_content_package_v1
from todayflow_backend.services.day_model_v1_content_evaluator import (
    RECOMMENDATION_BLOCK,
    RECOMMENDATION_USE,
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
    DECISION_CALL_LLM,
    DECISION_NO_CALL,
    decide_day_content_llm_call_v1,
)
from todayflow_backend.services.day_model_v1_llm_context_slice import build_llm_context_slice_v1
from todayflow_backend.services.day_model_v1_llm_prompt import build_day_llm_prompt_v1
from todayflow_backend.services.day_model_v1_llm_refinement_response import (
    validate_day_llm_refinement_response_v1,
)
from todayflow_backend.services.day_model_v1_llm_response_evaluation import (
    evaluate_day_llm_response_v1,
)
from todayflow_backend.services.day_model_v1_llm_request_record import (
    build_llm_precall_record_v1,
    generate_generation_id,
)
from todayflow_backend.services.day_model_v1_surface_candidate import (
    DAY_SURFACE_CANDIDATE_V1_CONTRACT,
    DAY_SURFACE_CANDIDATE_V1_KEYS,
    SELECTED_SOURCE_BLOCKED,
    SELECTED_SOURCE_DETERMINISTIC,
    SELECTED_SOURCE_LLM_REFINED,
    select_day_surface_candidate_v1,
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

LLM_TRACE = {
    "prompt_id": "prompt-test-001",
    "context_slice_id": REF_IDS["context_slice_id"],
}

GUIDANCE_TEMPLATE = "day.refine.guidance.v1"


@pytest.fixture(autouse=True)
def _clear_caches():
    clear_reference_machine_cache()
    clear_day_content_registry_cache()
    clear_day_llm_prompt_template_registry_cache()
    yield
    clear_reference_machine_cache()
    clear_day_content_registry_cache()
    clear_day_llm_prompt_template_registry_cache()


def _base_artifacts():
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
    return package, evaluation, render


def _call_llm_bundle():
    package, evaluation, render = _base_artifacts()
    evaluation = copy.deepcopy(evaluation)
    evaluation["recommendation"] = RECOMMENDATION_USE_WITH_CAUTION
    evaluation["degraded"] = True
    gate = decide_day_content_llm_call_v1(render, evaluation, surface="day_guidance_card")
    assert gate["decision"] == DECISION_CALL_LLM
    generation_id = generate_generation_id()
    precall = build_llm_precall_record_v1(
        gate,
        generation_id=generation_id,
        surface="day_guidance_card",
        **REF_IDS,
    )
    context_slice = build_llm_context_slice_v1(
        precall,
        render,
        evaluation,
        surface="day_guidance_card",
        context_depth=CONTEXT_DEPTH_MINIMAL,
    )
    prompt = build_day_llm_prompt_v1(context_slice, GUIDANCE_TEMPLATE)
    fragments = prompt["input_payload"]["fragments"]
    keys = [item["key"] for item in fragments]
    combined = " ".join(item["text"] for item in fragments)
    raw = {
        "refined_text": combined,
        "changed": True,
        "source_keys_used": keys,
        "warnings": [],
    }
    validated = validate_day_llm_refinement_response_v1(raw, prompt)
    llm_eval = evaluate_day_llm_response_v1(
        validated, prompt, generation_id=generation_id
    )
    return render, evaluation, gate, validated, llm_eval


def test_no_call_selects_deterministic():
    package, evaluation, _ = _base_artifacts()
    evaluation = copy.deepcopy(evaluation)
    evaluation["recommendation"] = RECOMMENDATION_USE
    evaluation["degraded"] = False
    evaluation["issues"] = []
    render = render_day_content_package_v1(package, evaluation)
    gate = decide_day_content_llm_call_v1(render, evaluation, surface="today_hero")
    assert gate["decision"] == DECISION_NO_CALL
    candidate = select_day_surface_candidate_v1(
        render,
        evaluation,
        gate,
        surface="today_hero",
        render_trace=REF_IDS,
    )
    assert candidate["selected_source"] == SELECTED_SOURCE_DETERMINISTIC
    assert candidate["used_llm"] is False
    assert candidate["display_text"]


def test_blocked_gate_returns_blocked():
    package, evaluation, render = _base_artifacts()
    evaluation = copy.deepcopy(evaluation)
    evaluation["recommendation"] = RECOMMENDATION_BLOCK
    render = render_day_content_package_v1(package, evaluation)
    gate = decide_day_content_llm_call_v1(render, evaluation, surface="day_guidance_card")
    assert gate["decision"] == "blocked"
    candidate = select_day_surface_candidate_v1(
        render,
        evaluation,
        gate,
        surface="day_guidance_card",
        render_trace=REF_IDS,
    )
    assert candidate["selected_source"] == SELECTED_SOURCE_BLOCKED
    assert candidate["display_text"] is None


def test_call_llm_accepted_high_quality_selects_llm():
    render, evaluation, gate, validated, llm_eval = _call_llm_bundle()
    assert llm_eval["quality_score"] >= 0.75
    candidate = select_day_surface_candidate_v1(
        render,
        evaluation,
        gate,
        surface="day_guidance_card",
        llm_response_evaluation=llm_eval,
        validated_llm_response=validated,
        render_trace=REF_IDS,
        llm_trace={**LLM_TRACE, "generation_id": llm_eval["generation_id"]},
    )
    assert candidate["selected_source"] == SELECTED_SOURCE_LLM_REFINED
    assert candidate["used_llm"] is True
    assert candidate["display_text"] == validated["refined_text"]


def test_call_llm_invalid_response_fallback_deterministic():
    render, evaluation, gate, validated, llm_eval = _call_llm_bundle()
    invalid = copy.deepcopy(validated)
    invalid["status"] = "invalid"
    invalid["issues"] = ["E-RESP-EMPTY_REFINED_TEXT"]
    bad_eval = copy.deepcopy(llm_eval)
    bad_eval["response_status"] = "invalid"
    bad_eval["recommendation"] = "reject"
    bad_eval["usable_candidate"] = False
    bad_eval["dataset_status"] = "rejected"
    bad_eval["quality_score"] = 0.0
    candidate = select_day_surface_candidate_v1(
        render,
        evaluation,
        gate,
        surface="day_guidance_card",
        llm_response_evaluation=bad_eval,
        validated_llm_response=invalid,
        render_trace=REF_IDS,
        llm_trace=LLM_TRACE,
    )
    assert candidate["selected_source"] == SELECTED_SOURCE_DETERMINISTIC
    assert candidate["used_llm"] is False
    assert "fallback_invalid_response" in candidate["selection_reason"]


def test_call_llm_low_quality_fallback_deterministic():
    render, evaluation, gate, validated, llm_eval = _call_llm_bundle()
    low_eval = copy.deepcopy(llm_eval)
    low_eval["quality_score"] = 0.7
    candidate = select_day_surface_candidate_v1(
        render,
        evaluation,
        gate,
        surface="day_guidance_card",
        llm_response_evaluation=low_eval,
        validated_llm_response=validated,
        render_trace=REF_IDS,
        llm_trace=LLM_TRACE,
    )
    assert candidate["selected_source"] == SELECTED_SOURCE_DETERMINISTIC
    assert "fallback_low_quality" in candidate["selection_reason"]


def test_call_llm_no_deterministic_fallback_blocked():
    render, evaluation, gate, validated, llm_eval = _call_llm_bundle()
    broken_render = copy.deepcopy(render)
    broken_render["surfaces"] = copy.deepcopy(render["surfaces"])
    del broken_render["surfaces"]["day_guidance_card"]
    low_eval = copy.deepcopy(llm_eval)
    low_eval["quality_score"] = 0.0
    low_eval["recommendation"] = "reject"
    low_eval["usable_candidate"] = False
    invalid = copy.deepcopy(validated)
    invalid["status"] = "invalid"
    candidate = select_day_surface_candidate_v1(
        broken_render,
        evaluation,
        gate,
        surface="day_guidance_card",
        llm_response_evaluation=low_eval,
        validated_llm_response=invalid,
        render_trace=REF_IDS,
        llm_trace=LLM_TRACE,
    )
    assert candidate["selected_source"] == SELECTED_SOURCE_BLOCKED
    assert candidate["display_text"] is None


def test_wrong_surface_fallback_deterministic():
    render, evaluation, gate, validated, llm_eval = _call_llm_bundle()
    candidate = select_day_surface_candidate_v1(
        render,
        evaluation,
        gate,
        surface="today_hero",
        llm_response_evaluation=llm_eval,
        validated_llm_response=validated,
        render_trace=REF_IDS,
        llm_trace=LLM_TRACE,
    )
    assert candidate["selected_source"] == SELECTED_SOURCE_DETERMINISTIC
    assert candidate["used_llm"] is False
    assert "fallback_wrong_surface" in candidate["selection_reason"]


def test_traceability_preserved():
    render, evaluation, gate, validated, llm_eval = _call_llm_bundle()
    candidate = select_day_surface_candidate_v1(
        render,
        evaluation,
        gate,
        surface="day_guidance_card",
        llm_response_evaluation=llm_eval,
        validated_llm_response=validated,
        render_trace=REF_IDS,
        llm_trace={**LLM_TRACE, "generation_id": llm_eval["generation_id"]},
    )
    assert candidate["render_trace"]["render_id"] == REF_IDS["render_id"]
    assert candidate["render_trace"]["package_id"] == REF_IDS["package_id"]
    assert candidate["render_trace"]["evaluation_id"] == REF_IDS["evaluation_id"]
    assert candidate["llm_trace"]["prompt_id"] == LLM_TRACE["prompt_id"]
    assert candidate["llm_trace"]["llm_response_evaluation_id"] == llm_eval[
        "llm_response_evaluation_id"
    ]


def test_used_llm_flag_correct():
    render, evaluation, gate, validated, llm_eval = _call_llm_bundle()
    llm_candidate = select_day_surface_candidate_v1(
        render,
        evaluation,
        gate,
        surface="day_guidance_card",
        llm_response_evaluation=llm_eval,
        validated_llm_response=validated,
        render_trace=REF_IDS,
        llm_trace=LLM_TRACE,
    )
    assert llm_candidate["used_llm"] is True

    no_call_gate = decide_day_content_llm_call_v1(render, evaluation, surface="today_hero")
    det_candidate = select_day_surface_candidate_v1(
        render,
        evaluation,
        no_call_gate,
        surface="today_hero",
        render_trace=REF_IDS,
    )
    assert det_candidate["used_llm"] is False


def test_output_shape_stable():
    render, evaluation, gate, validated, llm_eval = _call_llm_bundle()
    candidate = select_day_surface_candidate_v1(
        render,
        evaluation,
        gate,
        surface="day_guidance_card",
        llm_response_evaluation=llm_eval,
        validated_llm_response=validated,
        render_trace=REF_IDS,
        llm_trace=LLM_TRACE,
    )
    assert set(candidate.keys()) == DAY_SURFACE_CANDIDATE_V1_KEYS
    assert candidate["contract_version"] == DAY_SURFACE_CANDIDATE_V1_CONTRACT
