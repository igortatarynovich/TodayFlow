"""P1.8 — LLM request record contract tests."""

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
    DECISION_CALL_LLM,
    DECISION_NO_CALL,
    decide_day_content_llm_call_v1,
)
from todayflow_backend.services.day_model_v1_llm_request_record import (
    DAY_LLM_POSTCALL_RECORD_V1_CONTRACT,
    DAY_LLM_POSTCALL_RECORD_V1_KEYS,
    DAY_LLM_PRECALL_RECORD_V1_CONTRACT,
    DAY_LLM_PRECALL_RECORD_V1_KEYS,
    DayModelLlmRecordError,
    build_llm_postcall_record_v1,
    build_llm_precall_record_v1,
    generate_generation_id,
    maybe_build_llm_precall_record_v1,
    validate_llm_precall_record_v1,
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
    "context_slice_id": "context-slice-pending-001",
}


@pytest.fixture(autouse=True)
def _clear_caches():
    clear_reference_machine_cache()
    clear_day_content_registry_cache()
    yield
    clear_reference_machine_cache()
    clear_day_content_registry_cache()


def _call_llm_gate_and_artifacts():
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
    return gate, render, package, evaluation


def test_call_llm_creates_valid_precall_record():
    gate, _, _, _ = _call_llm_gate_and_artifacts()
    record = build_llm_precall_record_v1(
        gate,
        generation_id=generate_generation_id(),
        surface="day_guidance_card",
        **REF_IDS,
    )
    assert validate_llm_precall_record_v1(record) == []
    assert record["contract_version"] == DAY_LLM_PRECALL_RECORD_V1_CONTRACT


def test_no_call_does_not_create_record():
    gate, render, _, evaluation = _call_llm_gate_and_artifacts()
    evaluation = copy.deepcopy(evaluation)
    evaluation["recommendation"] = "use"
    evaluation["degraded"] = False
    evaluation["issues"] = []
    no_call_gate = decide_day_content_llm_call_v1(render, evaluation, surface="today_hero")
    assert no_call_gate["decision"] == DECISION_NO_CALL
    assert maybe_build_llm_precall_record_v1(
        no_call_gate,
        generation_id=generate_generation_id(),
        surface="today_hero",
        **REF_IDS,
    ) is None


def test_blocked_does_not_create_record():
    gate, render, package, _ = _call_llm_gate_and_artifacts()
    package = copy.deepcopy(package)
    package["risk_warning"] = None
    evaluation = evaluate_day_content_package_v1(package)
    render = render_day_content_package_v1(package, evaluation)
    blocked_gate = decide_day_content_llm_call_v1(render, evaluation, surface="today_hero")
    assert blocked_gate["decision"] == "blocked"
    assert maybe_build_llm_precall_record_v1(
        blocked_gate,
        generation_id=generate_generation_id(),
        surface="today_hero",
        **REF_IDS,
    ) is None


def test_precall_contains_full_gate_decision():
    gate, _, _, _ = _call_llm_gate_and_artifacts()
    record = build_llm_precall_record_v1(
        gate,
        generation_id=generate_generation_id(),
        surface="day_guidance_card",
        **REF_IDS,
    )
    assert record["gate_decision"] == gate


def test_save_required_always_true():
    gate, _, _, _ = _call_llm_gate_and_artifacts()
    record = build_llm_precall_record_v1(
        gate,
        generation_id=generate_generation_id(),
        surface="day_guidance_card",
        **REF_IDS,
    )
    assert record["save_required"] is True


def test_dataset_candidate_always_true():
    gate, _, _, _ = _call_llm_gate_and_artifacts()
    record = build_llm_precall_record_v1(
        gate,
        generation_id=generate_generation_id(),
        surface="day_guidance_card",
        **REF_IDS,
    )
    assert record["dataset_candidate"] is True


def test_missing_generation_id_invalid():
    gate, _, _, _ = _call_llm_gate_and_artifacts()
    with pytest.raises(DayModelLlmRecordError):
        build_llm_precall_record_v1(
            gate,
            generation_id="",
            surface="day_guidance_card",
            **REF_IDS,
        )


def test_postcall_links_to_precall_via_generation_id():
    gate, _, _, _ = _call_llm_gate_and_artifacts()
    generation_id = generate_generation_id()
    precall = build_llm_precall_record_v1(
        gate,
        generation_id=generation_id,
        surface="day_guidance_card",
        **REF_IDS,
    )
    postcall = build_llm_postcall_record_v1(
        precall,
        provider="openai",
        model="gpt-4o-mini",
        input_tokens=120,
        output_tokens=80,
        cost_estimate=0.002,
        raw_response='{"text":"refined"}',
        parsed_response={"text": "refined"},
        finish_reason="stop",
        status="completed",
    )
    assert postcall["generation_id"] == generation_id
    assert postcall["generation_id"] == precall["generation_id"]


def test_failed_postcall_preserves_error():
    gate, _, _, _ = _call_llm_gate_and_artifacts()
    precall = build_llm_precall_record_v1(
        gate,
        generation_id=generate_generation_id(),
        surface="day_guidance_card",
        **REF_IDS,
    )
    postcall = build_llm_postcall_record_v1(
        precall,
        provider="openai",
        model="gpt-4o-mini",
        input_tokens=0,
        output_tokens=0,
        cost_estimate=0.0,
        raw_response="",
        parsed_response={},
        finish_reason="error",
        status="failed",
        error="rate_limit_exceeded",
    )
    assert postcall["status"] == "failed"
    assert postcall["error"] == "rate_limit_exceeded"


def test_output_shape_stable():
    gate, _, _, _ = _call_llm_gate_and_artifacts()
    generation_id = generate_generation_id()
    precall = build_llm_precall_record_v1(
        gate,
        generation_id=generation_id,
        surface="day_guidance_card",
        **REF_IDS,
    )
    postcall = build_llm_postcall_record_v1(
        precall,
        provider="openai",
        model="gpt-4o-mini",
        input_tokens=10,
        output_tokens=5,
        cost_estimate=0.001,
        raw_response="ok",
        parsed_response={"ok": True},
        finish_reason="stop",
        status="completed",
    )
    assert set(precall.keys()) == DAY_LLM_PRECALL_RECORD_V1_KEYS
    assert set(postcall.keys()) == DAY_LLM_POSTCALL_RECORD_V1_KEYS
    assert precall["contract_version"] == DAY_LLM_PRECALL_RECORD_V1_CONTRACT
    assert postcall["contract_version"] == DAY_LLM_POSTCALL_RECORD_V1_CONTRACT
