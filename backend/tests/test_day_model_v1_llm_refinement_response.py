"""P1.11 — LLM refinement response contract tests."""

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
    DAY_LLM_REFINEMENT_RESPONSE_V1_CONTRACT,
    DAY_LLM_REFINEMENT_RESPONSE_V1_KEYS,
    RESPONSE_STATUS_INVALID,
    RESPONSE_STATUS_VALID,
    validate_day_llm_refinement_response_v1,
)
from todayflow_backend.services.day_model_v1_llm_request_record import (
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


def _prompt_fixture():
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
    precall = build_llm_precall_record_v1(
        gate,
        generation_id=generate_generation_id(),
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
    return build_day_llm_prompt_v1(context_slice, GUIDANCE_TEMPLATE)


def _valid_raw_response(prompt):
    fragments = prompt["input_payload"]["fragments"]
    keys = [item["key"] for item in fragments]
    combined = " ".join(item["text"] for item in fragments)
    return {
        "refined_text": combined,
        "changed": False,
        "source_keys_used": keys,
        "warnings": [],
    }


def test_valid_response_passes():
    prompt = _prompt_fixture()
    raw = _valid_raw_response(prompt)
    result = validate_day_llm_refinement_response_v1(raw, prompt)
    assert result["status"] == RESPONSE_STATUS_VALID
    assert result["issues"] == []
    assert result["refined_text"] == raw["refined_text"]


def test_empty_refined_text_invalid():
    prompt = _prompt_fixture()
    raw = _valid_raw_response(prompt)
    raw["refined_text"] = "   "
    result = validate_day_llm_refinement_response_v1(raw, prompt)
    assert result["status"] == RESPONSE_STATUS_INVALID
    assert "E-RESP-EMPTY_REFINED_TEXT" in result["issues"]


def test_too_long_refined_text_invalid():
    prompt = _prompt_fixture()
    raw = _valid_raw_response(prompt)
    max_len = prompt["constraints"]["max_length_chars"]
    raw["refined_text"] = "x" * (max_len + 1)
    result = validate_day_llm_refinement_response_v1(raw, prompt)
    assert result["status"] == RESPONSE_STATUS_INVALID
    assert any(issue.startswith("E-RESP-TOO_LONG") for issue in result["issues"])


def test_unknown_source_key_invalid():
    prompt = _prompt_fixture()
    raw = _valid_raw_response(prompt)
    raw["source_keys_used"] = list(raw["source_keys_used"]) + ["day.unknown.key"]
    result = validate_day_llm_refinement_response_v1(raw, prompt)
    assert result["status"] == RESPONSE_STATUS_INVALID
    assert any(issue.startswith("E-RESP-UNKNOWN_SOURCE_KEY:") for issue in result["issues"])


def test_added_astrology_invalid():
    prompt = _prompt_fixture()
    raw = _valid_raw_response(prompt)
    raw["refined_text"] = raw["refined_text"] + " Mars in Aries suggests urgency."
    result = validate_day_llm_refinement_response_v1(raw, prompt)
    assert result["status"] == RESPONSE_STATUS_INVALID
    assert "E-RESP-FORBIDDEN_ASTROLOGY" in result["issues"]


def test_added_tarot_invalid():
    prompt = _prompt_fixture()
    raw = _valid_raw_response(prompt)
    raw["refined_text"] = raw["refined_text"] + " The Chariot tarot card says go."
    result = validate_day_llm_refinement_response_v1(raw, prompt)
    assert result["status"] == RESPONSE_STATUS_INVALID
    assert "E-RESP-FORBIDDEN_TAROT" in result["issues"]


def test_added_numerology_invalid():
    prompt = _prompt_fixture()
    raw = _valid_raw_response(prompt)
    raw["refined_text"] = raw["refined_text"] + " Your life path number confirms this."
    result = validate_day_llm_refinement_response_v1(raw, prompt)
    assert result["status"] == RESPONSE_STATUS_INVALID
    assert "E-RESP-FORBIDDEN_NUMEROLOGY" in result["issues"]


def test_diagnosis_invalid():
    prompt = _prompt_fixture()
    raw = _valid_raw_response(prompt)
    raw["refined_text"] = raw["refined_text"] + " This looks like a clinical anxiety disorder."
    result = validate_day_llm_refinement_response_v1(raw, prompt)
    assert result["status"] == RESPONSE_STATUS_INVALID
    assert "E-RESP-FORBIDDEN_DIAGNOSIS" in result["issues"]


def test_promise_outcome_invalid():
    prompt = _prompt_fixture()
    raw = _valid_raw_response(prompt)
    raw["refined_text"] = raw["refined_text"] + " Success is guaranteed today."
    result = validate_day_llm_refinement_response_v1(raw, prompt)
    assert result["status"] == RESPONSE_STATUS_INVALID
    assert "E-RESP-FORBIDDEN_PROMISE_OUTCOME" in result["issues"]


def test_wrong_shape_invalid():
    prompt = _prompt_fixture()
    result = validate_day_llm_refinement_response_v1({"refined_text": "hello"}, prompt)
    assert result["status"] == RESPONSE_STATUS_INVALID
    assert any(issue.startswith("E-RESP-WRONG_SHAPE") for issue in result["issues"])


def test_warnings_must_be_list():
    prompt = _prompt_fixture()
    raw = _valid_raw_response(prompt)
    raw["warnings"] = "not-a-list"
    result = validate_day_llm_refinement_response_v1(raw, prompt)
    assert result["status"] == RESPONSE_STATUS_INVALID
    assert "E-RESP-WARNINGS_NOT_LIST" in result["issues"]


def test_output_shape_stable():
    prompt = _prompt_fixture()
    raw = _valid_raw_response(prompt)
    result = validate_day_llm_refinement_response_v1(raw, prompt)
    assert set(result.keys()) == DAY_LLM_REFINEMENT_RESPONSE_V1_KEYS
    assert result["contract_version"] == DAY_LLM_REFINEMENT_RESPONSE_V1_CONTRACT
