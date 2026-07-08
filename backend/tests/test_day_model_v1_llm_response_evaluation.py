"""P1.12 — LLM response evaluation and post-call integration tests."""

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
    decide_day_content_llm_call_v1,
)
from todayflow_backend.services.day_model_v1_llm_context_slice import build_llm_context_slice_v1
from todayflow_backend.services.day_model_v1_llm_prompt import build_day_llm_prompt_v1
from todayflow_backend.services.day_model_v1_llm_refinement_response import (
    RESPONSE_STATUS_INVALID,
    validate_day_llm_refinement_response_v1,
)
from todayflow_backend.services.day_model_v1_llm_response_evaluation import (
    DATASET_STATUS_CANDIDATE,
    DATASET_STATUS_REJECTED,
    DAY_LLM_RESPONSE_EVALUATION_V1_CONTRACT,
    DAY_LLM_RESPONSE_EVALUATION_V1_KEYS,
    RECOMMENDATION_ACCEPT_CANDIDATE,
    RECOMMENDATION_REJECT,
    apply_response_evaluation_to_postcall_v1,
    build_llm_postcall_record_with_evaluation_v1,
    evaluate_day_llm_response_v1,
)
from todayflow_backend.services.day_model_v1_llm_request_record import (
    build_llm_postcall_record_v1,
    build_llm_precall_record_v1,
    generate_generation_id,
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


def _pipeline():
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
    return precall, prompt


def _valid_raw(prompt):
    fragments = prompt["input_payload"]["fragments"]
    keys = [item["key"] for item in fragments]
    combined = " ".join(item["text"] for item in fragments)
    return {
        "refined_text": combined,
        "changed": True,
        "source_keys_used": keys,
        "warnings": [],
    }


def test_valid_response_accept_candidate():
    precall, prompt = _pipeline()
    validated = validate_day_llm_refinement_response_v1(_valid_raw(prompt), prompt)
    evaluation = evaluate_day_llm_response_v1(
        validated, prompt, generation_id=precall["generation_id"]
    )
    assert evaluation["recommendation"] == RECOMMENDATION_ACCEPT_CANDIDATE
    assert evaluation["usable_candidate"] is True
    assert evaluation["quality_score"] == 1.0


def test_invalid_response_reject():
    precall, prompt = _pipeline()
    raw = _valid_raw(prompt)
    raw["refined_text"] = ""
    validated = validate_day_llm_refinement_response_v1(raw, prompt)
    assert validated["status"] == RESPONSE_STATUS_INVALID
    evaluation = evaluate_day_llm_response_v1(
        validated, prompt, generation_id=precall["generation_id"]
    )
    assert evaluation["recommendation"] == RECOMMENDATION_REJECT
    assert evaluation["usable_candidate"] is False
    assert evaluation["dataset_status"] == DATASET_STATUS_REJECTED


def test_forbidden_issue_sets_safety_flag():
    precall, prompt = _pipeline()
    raw = _valid_raw(prompt)
    raw["refined_text"] = raw["refined_text"] + " Mars in Aries suggests urgency."
    validated = validate_day_llm_refinement_response_v1(raw, prompt)
    evaluation = evaluate_day_llm_response_v1(
        validated, prompt, generation_id=precall["generation_id"]
    )
    assert "forbidden_astrology" in evaluation["safety_flags"]
    assert evaluation["recommendation"] == RECOMMENDATION_REJECT


def test_warnings_lower_quality():
    precall, prompt = _pipeline()
    raw = _valid_raw(prompt)
    raw["warnings"] = ["minor phrasing concern"]
    validated = validate_day_llm_refinement_response_v1(raw, prompt)
    evaluation = evaluate_day_llm_response_v1(
        validated, prompt, generation_id=precall["generation_id"]
    )
    assert evaluation["recommendation"] == RECOMMENDATION_ACCEPT_CANDIDATE
    assert evaluation["quality_score"] < 1.0
    assert evaluation["quality_score"] == pytest.approx(0.92, abs=0.001)


def test_unchanged_lowers_quality_not_reject():
    precall, prompt = _pipeline()
    raw = _valid_raw(prompt)
    raw["changed"] = False
    validated = validate_day_llm_refinement_response_v1(raw, prompt)
    evaluation = evaluate_day_llm_response_v1(
        validated, prompt, generation_id=precall["generation_id"]
    )
    assert evaluation["recommendation"] == RECOMMENDATION_ACCEPT_CANDIDATE
    assert evaluation["quality_score"] == pytest.approx(0.95, abs=0.001)


def test_used_in_ui_always_false():
    precall, prompt = _pipeline()
    validated = validate_day_llm_refinement_response_v1(_valid_raw(prompt), prompt)
    evaluation = evaluate_day_llm_response_v1(
        validated, prompt, generation_id=precall["generation_id"]
    )
    assert evaluation["used_in_ui"] is False


def test_dataset_status_candidate_only_for_valid():
    precall, prompt = _pipeline()
    valid_eval = evaluate_day_llm_response_v1(
        validate_day_llm_refinement_response_v1(_valid_raw(prompt), prompt),
        prompt,
        generation_id=precall["generation_id"],
    )
    assert valid_eval["dataset_status"] == DATASET_STATUS_CANDIDATE

    invalid_raw = _valid_raw(prompt)
    invalid_raw["refined_text"] = ""
    invalid_eval = evaluate_day_llm_response_v1(
        validate_day_llm_refinement_response_v1(invalid_raw, prompt),
        prompt,
        generation_id=precall["generation_id"],
    )
    assert invalid_eval["dataset_status"] == DATASET_STATUS_REJECTED


def test_postcall_receives_evaluation_fields():
    precall, prompt = _pipeline()
    _, evaluation, postcall = build_llm_postcall_record_with_evaluation_v1(
        precall,
        raw_response=_valid_raw(prompt),
        prompt=prompt,
        provider="openai",
        model="gpt-4o-mini",
        input_tokens=100,
        output_tokens=50,
        cost_estimate=0.001,
        raw_response_text='{"refined_text":"ok"}',
    )
    assert postcall["llm_response_evaluation_id"] == evaluation["llm_response_evaluation_id"]
    assert postcall["quality_score"] == evaluation["quality_score"]
    assert postcall["safety_flags"] == evaluation["safety_flags"]
    assert postcall["used_in_ui"] is False


def test_generation_id_must_match():
    precall, prompt = _pipeline()
    validated = validate_day_llm_refinement_response_v1(_valid_raw(prompt), prompt)
    with pytest.raises(Exception):
        evaluate_day_llm_response_v1(
            validated, prompt, generation_id="wrong-generation-id"
        )

    postcall = build_llm_postcall_record_v1(
        precall,
        provider="openai",
        model="gpt-4o-mini",
        input_tokens=10,
        output_tokens=5,
        cost_estimate=0.001,
        raw_response="{}",
        parsed_response={},
        finish_reason="stop",
        status="completed",
    )
    evaluation = evaluate_day_llm_response_v1(
        validated, prompt, generation_id=precall["generation_id"]
    )
    bad_eval = copy.deepcopy(evaluation)
    bad_eval["generation_id"] = "mismatch"
    with pytest.raises(Exception):
        apply_response_evaluation_to_postcall_v1(postcall, bad_eval, precall_record=precall)


def test_output_shape_stable():
    precall, prompt = _pipeline()
    validated = validate_day_llm_refinement_response_v1(_valid_raw(prompt), prompt)
    evaluation = evaluate_day_llm_response_v1(
        validated, prompt, generation_id=precall["generation_id"]
    )
    assert set(evaluation.keys()) == DAY_LLM_RESPONSE_EVALUATION_V1_KEYS
    assert evaluation["contract_version"] == DAY_LLM_RESPONSE_EVALUATION_V1_CONTRACT
