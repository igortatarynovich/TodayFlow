"""P1.7 — Day content LLM call gate tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.day_content_registry_loader import clear_day_content_registry_cache
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
    DAY_CONTENT_LLM_GATE_V1_CONTRACT,
    DAY_CONTENT_LLM_GATE_V1_KEYS,
    DECISION_BLOCKED,
    DECISION_CALL_LLM,
    DECISION_NO_CALL,
    decide_day_content_llm_call_v1,
)
from tests.test_cross_domain_machine_validation import (
    ANCHOR_NUMEROLOGY,
    ANCHOR_PLANET,
    ANCHOR_SIGN,
    ANCHOR_TAROT,
    CONTRAST_ASTRO,
    CONTRAST_NUMEROLOGY,
    CONTRAST_TAROT,
)

CONTRAST_SIGN = "astrology.sign.capricorn"


@pytest.fixture(autouse=True)
def _clear_caches():
    clear_reference_machine_cache()
    clear_day_content_registry_cache()
    yield
    clear_reference_machine_cache()
    clear_day_content_registry_cache()


def _pipeline(tarot, numerology, planet, sign):
    dm = aggregate_day_model_v1(
        tarot_entity_code=tarot,
        numerology_entity_code=numerology,
        astrology_planet_code=planet,
        astrology_sign_code=sign,
    )
    interpretation = interpret_day_model_v1(dm)
    mapping = map_day_model_interpretation_to_content_keys(interpretation)
    resolution = resolve_content_entries_from_mapping(mapping)
    package = assemble_day_content_package_v1(interpretation, mapping, resolution)
    evaluation = evaluate_day_content_package_v1(package)
    render = render_day_content_package_v1(package, evaluation)
    return package, evaluation, render


def test_valid_use_render_no_call():
    _, evaluation, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    assert evaluation["recommendation"] == RECOMMENDATION_USE
    gate = decide_day_content_llm_call_v1(render, evaluation, surface="today_hero")
    assert gate["decision"] == DECISION_NO_CALL
    assert gate["render_sufficient"] is True


def test_use_with_caution_surface_dependent():
    _, evaluation, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    evaluation = copy.deepcopy(evaluation)
    evaluation["recommendation"] = RECOMMENDATION_USE_WITH_CAUTION
    evaluation["degraded"] = True

    hero_gate = decide_day_content_llm_call_v1(render, evaluation, surface="today_hero")
    guidance_gate = decide_day_content_llm_call_v1(render, evaluation, surface="day_guidance_card")

    assert hero_gate["decision"] == DECISION_NO_CALL
    assert guidance_gate["decision"] == DECISION_CALL_LLM


def test_block_recommendation_blocked():
    package, evaluation, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    package = copy.deepcopy(package)
    package["risk_warning"] = None
    evaluation = evaluate_day_content_package_v1(package)
    render = render_day_content_package_v1(package, evaluation)
    gate = decide_day_content_llm_call_v1(render, evaluation, surface="today_hero")
    assert gate["decision"] == DECISION_BLOCKED
    assert gate["blocked_reason"] == "evaluation_block"


def test_missing_surface_blocked():
    _, evaluation, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    render = copy.deepcopy(render)
    render["surfaces"].pop("risk_card")
    gate = decide_day_content_llm_call_v1(render, evaluation, surface="risk_card")
    assert gate["decision"] == DECISION_BLOCKED
    assert gate["blocked_reason"] in ("missing_surface", "missing_required_surfaces")


def test_deterministic_only_surface_no_call():
    _, evaluation, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    evaluation = copy.deepcopy(evaluation)
    evaluation["recommendation"] = RECOMMENDATION_USE_WITH_CAUTION
    gate = decide_day_content_llm_call_v1(render, evaluation, surface="action_card")
    assert gate["decision"] == DECISION_NO_CALL


def test_narrative_surface_requires_call_llm():
    _, evaluation, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    evaluation = copy.deepcopy(evaluation)
    evaluation["recommendation"] = RECOMMENDATION_USE_WITH_CAUTION
    evaluation["degraded"] = True
    evaluation["issues"] = list(evaluation["issues"]) + ["E-CONFLICT:strategy_action+tempo_slow_down"]
    gate = decide_day_content_llm_call_v1(render, evaluation, surface="day_guidance_card")
    assert gate["decision"] == DECISION_CALL_LLM


def test_cost_policy_strict_blocks_or_no_call():
    _, evaluation, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    evaluation = copy.deepcopy(evaluation)
    evaluation["recommendation"] = RECOMMENDATION_USE_WITH_CAUTION
    evaluation["degraded"] = True
    strict_cost = {"mode": "strict", "llm_calls_allowed": False, "max_tokens_budget": 128}

    blocked_gate = decide_day_content_llm_call_v1(
        render,
        evaluation,
        surface="day_guidance_card",
        cost_policy=strict_cost,
    )
    assert blocked_gate["decision"] in (DECISION_BLOCKED, DECISION_NO_CALL)
    if blocked_gate["decision"] == DECISION_BLOCKED:
        assert blocked_gate["blocked_reason"] == "cost_policy_strict"


def test_call_llm_save_required_true():
    _, evaluation, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    evaluation = copy.deepcopy(evaluation)
    evaluation["recommendation"] = RECOMMENDATION_USE_WITH_CAUTION
    evaluation["degraded"] = True
    gate = decide_day_content_llm_call_v1(render, evaluation, surface="day_guidance_card")
    assert gate["decision"] == DECISION_CALL_LLM
    assert gate["save_required"] is True


def test_call_llm_dataset_candidate_true():
    _, evaluation, render = _pipeline(CONTRAST_TAROT, CONTRAST_NUMEROLOGY, CONTRAST_ASTRO, CONTRAST_SIGN)
    evaluation = copy.deepcopy(evaluation)
    evaluation["recommendation"] = RECOMMENDATION_USE_WITH_CAUTION
    evaluation["degraded"] = True
    if "reflection_card" not in render["surfaces"]:
        pytest.skip("contrast fixture has no reflection_card")
    gate = decide_day_content_llm_call_v1(render, evaluation, surface="reflection_card")
    assert gate["decision"] == DECISION_CALL_LLM
    assert gate["dataset_candidate"] is True


def test_output_shape_stable():
    _, evaluation, render = _pipeline(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    gate = decide_day_content_llm_call_v1(render, evaluation, surface="today_hero")
    assert set(gate.keys()) == DAY_CONTENT_LLM_GATE_V1_KEYS
    assert gate["contract_version"] == DAY_CONTENT_LLM_GATE_V1_CONTRACT
