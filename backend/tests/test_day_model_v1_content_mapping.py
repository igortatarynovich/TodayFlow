"""P1.2 — DayModel content mapping tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.day_content_registry_loader import clear_day_content_registry_cache
from todayflow_backend.data.reference_machine_loader import clear_reference_machine_cache
from todayflow_backend.services.day_model_v1_aggregator import aggregate_day_model_v1
from todayflow_backend.services.day_model_v1_content_mapper import (
    DAY_MODEL_CONTENT_MAPPING_V1_CONTRACT,
    DAY_MODEL_CONTENT_MAPPING_V1_KEYS,
    DayModelContentMappingError,
    map_day_model_interpretation_to_content_keys,
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


def _anchor_interpretation():
    dm = aggregate_day_model_v1(
        tarot_entity_code=ANCHOR_TAROT,
        numerology_entity_code=ANCHOR_NUMEROLOGY,
        astrology_planet_code=ANCHOR_PLANET,
        astrology_sign_code=ANCHOR_SIGN,
    )
    return interpret_day_model_v1(dm)


def _contrast_interpretation():
    dm = aggregate_day_model_v1(
        tarot_entity_code=CONTRAST_TAROT,
        numerology_entity_code=CONTRAST_NUMEROLOGY,
        astrology_planet_code=CONTRAST_ASTRO,
        astrology_sign_code=CONTRAST_SIGN,
    )
    return interpret_day_model_v1(dm)


def _map(interpretation):
    return map_day_model_interpretation_to_content_keys(interpretation)


def test_output_shape_stable():
    result = _map(_anchor_interpretation())
    assert set(result.keys()) == DAY_MODEL_CONTENT_MAPPING_V1_KEYS
    assert result["contract_version"] == DAY_MODEL_CONTENT_MAPPING_V1_CONTRACT
    assert isinstance(result["content_keys"], dict)
    assert isinstance(result["required_slots"], dict)
    assert isinstance(result["optional_slots"], dict)
    assert isinstance(result["missing_keys"], list)


def test_strategy_always_gives_content_key():
    result = _map(_anchor_interpretation())
    key = result["content_keys"]["strategy"]
    assert key.startswith("day.strategy.")
    assert key not in result["missing_keys"]


def test_opportunity_class_always_gives_content_key():
    result = _map(_anchor_interpretation())
    key = result["content_keys"]["opportunity_class"]
    assert key.startswith("day.opportunity.")
    assert key not in result["missing_keys"]


def test_risk_class_always_gives_content_key():
    result = _map(_anchor_interpretation())
    key = result["content_keys"]["risk_class"]
    assert key.startswith("day.risk.")
    assert key not in result["missing_keys"]


def test_tempo_instruction_always_gives_content_key():
    result = _map(_anchor_interpretation())
    key = result["content_keys"]["tempo_instruction"]
    assert key.startswith("day.tempo.")
    assert key not in result["missing_keys"]


def test_action_mode_always_gives_content_key():
    result = _map(_anchor_interpretation())
    key = result["content_keys"]["action_mode"]
    assert key.startswith("day.action_mode.")
    assert key not in result["missing_keys"]


def test_pressure_level_always_gives_content_key():
    result = _map(_anchor_interpretation())
    key = result["content_keys"]["pressure_level"]
    assert key.startswith("day.pressure.")
    assert key not in result["missing_keys"]


def test_unknown_value_gives_missing_key():
    interpretation = copy.deepcopy(_anchor_interpretation())
    interpretation["strategy"] = "not_a_strategy"
    result = _map(interpretation)
    assert "day.strategy.not_a_strategy" in result["missing_keys"]
    assert result["degraded"] is True


def test_degraded_interpretation_gives_degraded_mapping():
    interpretation = copy.deepcopy(_anchor_interpretation())
    interpretation["degraded"] = True
    result = _map(interpretation)
    assert result["degraded"] is True
    assert "day.mapping.degraded" in result["optional_slots"].get("headline", [])


def test_anchor_contrast_different_content_key_sets():
    anchor = _map(_anchor_interpretation())
    contrast = _map(_contrast_interpretation())
    anchor_keys = set(anchor["content_keys"].values())
    contrast_keys = set(contrast["content_keys"].values())
    assert anchor_keys != contrast_keys


def test_required_slots_cover_core_slots():
    result = _map(_anchor_interpretation())
    for slot in ("headline", "guidance", "risk_warning", "action_hint", "tempo_hint"):
        assert slot in result["required_slots"]
        assert len(result["required_slots"][slot]) >= 1


def test_invalid_contract_version_raises():
    interpretation = copy.deepcopy(_anchor_interpretation())
    interpretation["contract_version"] = "wrong"
    with pytest.raises(DayModelContentMappingError):
        map_day_model_interpretation_to_content_keys(interpretation)


def test_registry_covers_all_interpretation_enums():
    from todayflow_backend.data.day_content_registry_loader import load_day_content_registry
    from todayflow_backend.services.day_model_v1_interpreter import (
        ACTION_MODE_VALUES,
        OPPORTUNITY_CLASS_VALUES,
        PRESSURE_LEVEL_VALUES,
        REFLECTION_MODE_VALUES,
        RISK_CLASS_VALUES,
        STRATEGY_VALUES,
        TEMPO_INSTRUCTION_VALUES,
    )

    registry = load_day_content_registry()["keys"]
    enum_map = {
        "day.strategy": STRATEGY_VALUES,
        "day.opportunity": OPPORTUNITY_CLASS_VALUES,
        "day.risk": RISK_CLASS_VALUES,
        "day.tempo": TEMPO_INSTRUCTION_VALUES,
        "day.action_mode": ACTION_MODE_VALUES,
        "day.reflection": REFLECTION_MODE_VALUES,
        "day.pressure": PRESSURE_LEVEL_VALUES,
    }
    for prefix, values in enum_map.items():
        for value in values:
            assert f"{prefix}.{value}" in registry
