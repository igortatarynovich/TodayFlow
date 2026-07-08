"""P1.10 — LLM prompt template contract tests."""

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
from todayflow_backend.services.day_model_v1_llm_prompt import (
    DAY_LLM_PROMPT_V1_CONTRACT,
    DAY_LLM_PROMPT_V1_KEYS,
    PROMPT_FORBIDDEN_OPERATIONS,
    DayModelLlmPromptError,
    build_day_llm_prompt_v1,
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
REFLECTION_TEMPLATE = "day.refine.reflection.v1"


@pytest.fixture(autouse=True)
def _clear_caches():
    clear_reference_machine_cache()
    clear_day_content_registry_cache()
    clear_day_llm_prompt_template_registry_cache()
    yield
    clear_reference_machine_cache()
    clear_day_content_registry_cache()
    clear_day_llm_prompt_template_registry_cache()


def _context_slice_pipeline(surface="day_guidance_card"):
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
    context_slice = build_llm_context_slice_v1(
        precall,
        render,
        evaluation,
        surface=surface,
        context_depth=CONTEXT_DEPTH_MINIMAL,
    )
    return context_slice, package, render


def test_prompt_only_from_valid_context_slice():
    context_slice, _, _ = _context_slice_pipeline()
    prompt = build_day_llm_prompt_v1(context_slice, GUIDANCE_TEMPLATE)
    assert prompt["contract_version"] == DAY_LLM_PROMPT_V1_CONTRACT

    broken = copy.deepcopy(context_slice)
    broken["status"] = "pending"
    with pytest.raises(DayModelLlmPromptError):
        build_day_llm_prompt_v1(broken, GUIDANCE_TEMPLATE)


def test_prompt_contains_generation_id():
    context_slice, _, _ = _context_slice_pipeline()
    prompt = build_day_llm_prompt_v1(context_slice, GUIDANCE_TEMPLATE)
    assert prompt["generation_id"] == context_slice["generation_id"]


def test_prompt_contains_source_keys():
    context_slice, _, _ = _context_slice_pipeline()
    prompt = build_day_llm_prompt_v1(context_slice, GUIDANCE_TEMPLATE)
    assert prompt["input_payload"]["source_keys"] == context_slice["source_keys"]
    assert all(key.startswith("day.") for key in prompt["input_payload"]["source_keys"])


def test_prompt_contains_forbidden_operations():
    context_slice, _, _ = _context_slice_pipeline()
    prompt = build_day_llm_prompt_v1(context_slice, GUIDANCE_TEMPLATE)
    forbidden = set(prompt["constraints"]["forbidden_operations"])
    assert PROMPT_FORBIDDEN_OPERATIONS.issubset(forbidden)
    assert "add_astrology" in forbidden
    assert "promise_outcome" in forbidden
    assert "change_strategy" in forbidden


def test_prompt_no_raw_profile():
    context_slice, _, _ = _context_slice_pipeline()
    prompt = build_day_llm_prompt_v1(context_slice, GUIDANCE_TEMPLATE)
    blob = str(prompt).lower()
    assert "core_profile" not in blob
    assert "user_profile" not in blob
    assert "birth_data" not in blob


def test_prompt_no_raw_memory():
    context_slice, _, _ = _context_slice_pipeline()
    prompt = build_day_llm_prompt_v1(context_slice, GUIDANCE_TEMPLATE)
    blob = str(prompt).lower()
    assert "memory_dump" not in blob
    assert "behavior_logs" not in blob
    assert "event_history" not in blob


def test_prompt_no_full_package():
    context_slice, _, render = _context_slice_pipeline()
    prompt = build_day_llm_prompt_v1(context_slice, GUIDANCE_TEMPLATE)
    blob = str(prompt)
    assert "content_package" not in blob
    assert "day_content_package" not in blob
    assert "surfaces" not in prompt["input_payload"]
    assert "today_hero" not in prompt["input_payload"]
    assert "metadata" not in prompt["input_payload"]
    assert str(render["surfaces"]["today_hero"]) not in str(prompt["input_payload"]["fragments"])
    assert len(prompt["input_payload"]["fragments"]) == len(
        context_slice["render_surface"]["entries"]
    )


def test_wrong_template_for_surface_invalid():
    context_slice, _, _ = _context_slice_pipeline(surface="day_guidance_card")
    with pytest.raises(DayModelLlmPromptError, match="surface"):
        build_day_llm_prompt_v1(context_slice, REFLECTION_TEMPLATE)


def test_output_schema_present():
    context_slice, _, _ = _context_slice_pipeline()
    prompt = build_day_llm_prompt_v1(context_slice, GUIDANCE_TEMPLATE)
    schema = prompt["output_schema"]
    assert schema["type"] == "object"
    for field in ("refined_text", "changed", "source_keys_used", "warnings"):
        assert field in schema["required"]


def test_prompt_shape_stable():
    context_slice, _, _ = _context_slice_pipeline()
    prompt = build_day_llm_prompt_v1(context_slice, GUIDANCE_TEMPLATE)
    assert set(prompt.keys()) == DAY_LLM_PROMPT_V1_KEYS
    assert prompt["template_id"] == GUIDANCE_TEMPLATE
    assert prompt["template_version"] == "1.0.0"
    assert prompt["traceability"]["context_slice_id"] == context_slice["context_slice_id"]
    assert isinstance(prompt["max_tokens"], int) and prompt["max_tokens"] > 0
