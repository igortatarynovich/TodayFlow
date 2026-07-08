"""P1.5 — DayModel package evaluation tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.day_content_registry_loader import clear_day_content_registry_cache
from todayflow_backend.data.reference_machine_loader import clear_reference_machine_cache
from todayflow_backend.services.day_model_v1_aggregator import aggregate_day_model_v1
from todayflow_backend.services.day_model_v1_content_assembler import assemble_day_content_package_v1
from todayflow_backend.services.day_model_v1_content_evaluator import (
    DAY_CONTENT_PACKAGE_EVALUATION_V1_CONTRACT,
    DAY_CONTENT_PACKAGE_EVALUATION_V1_KEYS,
    RECOMMENDATION_BLOCK,
    RECOMMENDATION_USE,
    RECOMMENDATION_USE_WITH_CAUTION,
    evaluate_day_content_package_v1,
)
from todayflow_backend.services.day_model_v1_content_mapper import (
    map_day_model_interpretation_to_content_keys,
)
from todayflow_backend.services.day_model_v1_content_resolver import (
    resolve_content_entries_from_mapping,
)
from todayflow_backend.services.day_model_v1_interpreter import interpret_day_model_v1
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


def _full_package(tarot, numerology, planet, sign):
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
    return package


def test_anchor_valid_recommendation_use():
    package = _full_package(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    result = evaluate_day_content_package_v1(package)
    assert result["recommendation"] == RECOMMENDATION_USE
    assert result["valid"] is True
    assert result["degraded"] is False


def test_contrast_valid_recommendation_use():
    package = _full_package(CONTRAST_TAROT, CONTRAST_NUMEROLOGY, CONTRAST_ASTRO, CONTRAST_SIGN)
    result = evaluate_day_content_package_v1(package)
    assert result["recommendation"] == RECOMMENDATION_USE
    assert result["valid"] is True


def test_missing_required_slot_block():
    package = _full_package(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    package = copy.deepcopy(package)
    package["risk_warning"] = None
    package["metadata"]["missing_slots"] = ["risk_warning"]
    result = evaluate_day_content_package_v1(package)
    assert result["recommendation"] == RECOMMENDATION_BLOCK
    assert result["valid"] is False
    assert any("missing_slot:risk_warning" in issue for issue in result["issues"])


def test_low_confidence_use_with_caution():
    package = _full_package(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    package = copy.deepcopy(package)
    package["metadata"]["confidence"] = 0.35
    result = evaluate_day_content_package_v1(package)
    assert result["recommendation"] == RECOMMENDATION_USE_WITH_CAUTION
    assert result["valid"] is True
    assert any(issue.startswith("E-CONFIDENCE:") for issue in result["issues"])


def test_degraded_package_use_with_caution():
    package = _full_package(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    package = copy.deepcopy(package)
    package["degraded"] = True
    package["metadata"]["degraded"] = True
    result = evaluate_day_content_package_v1(package)
    assert result["recommendation"] == RECOMMENDATION_USE_WITH_CAUTION
    assert result["degraded"] is True
    assert any(issue.startswith("E-DEGRADED:") for issue in result["issues"])


def test_conflict_act_slow_down_issue():
    package = _full_package(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    package = copy.deepcopy(package)
    package["metadata"]["strategy"] = "act"
    package["metadata"]["tempo_instruction"] = "slow_down"
    result = evaluate_day_content_package_v1(package)
    assert any(issue == "E-CONFLICT:strategy_action+tempo_slow_down" for issue in result["issues"])
    assert result["recommendation"] == RECOMMENDATION_USE_WITH_CAUTION


def test_conflict_high_pressure_accelerate_issue():
    package = _full_package(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    package = copy.deepcopy(package)
    package["metadata"]["pressure_level"] = "high"
    package["metadata"]["tempo_instruction"] = "accelerate"
    result = evaluate_day_content_package_v1(package)
    assert any(issue == "E-CONFLICT:pressure_high+tempo_accelerate" for issue in result["issues"])
    assert result["recommendation"] == RECOMMENDATION_USE_WITH_CAUTION


def test_duplicate_key_repetition_issue():
    package = _full_package(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    package = copy.deepcopy(package)
    duplicate = package["headline"]
    package["guidance"] = [duplicate, duplicate, duplicate]
    result = evaluate_day_content_package_v1(package)
    assert any(issue.startswith("E-REPETITION:") for issue in result["issues"])
    assert result["recommendation"] == RECOMMENDATION_USE_WITH_CAUTION


def test_issues_machine_readable():
    package = _full_package(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    package = copy.deepcopy(package)
    package["metadata"]["strategy"] = "act"
    package["metadata"]["tempo_instruction"] = "slow_down"
    result = evaluate_day_content_package_v1(package)
    assert all(":" in issue for issue in result["issues"])


def test_output_shape_stable():
    package = _full_package(ANCHOR_TAROT, ANCHOR_NUMEROLOGY, ANCHOR_PLANET, ANCHOR_SIGN)
    result = evaluate_day_content_package_v1(package)
    assert set(result.keys()) == DAY_CONTENT_PACKAGE_EVALUATION_V1_KEYS
    assert result["contract_version"] == DAY_CONTENT_PACKAGE_EVALUATION_V1_CONTRACT
    assert isinstance(result["issues"], list)
