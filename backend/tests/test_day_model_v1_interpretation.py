"""P1.1 — DayModel v1 interpretation rules tests."""

from __future__ import annotations

import pytest

from todayflow_backend.data.reference_machine_loader import clear_reference_machine_cache
from todayflow_backend.services.day_model_v1_aggregator import (
    DAY_MODEL_V1_CONTRACT_VERSION,
    aggregate_day_model_v1,
)
from todayflow_backend.services.day_model_v1_interpreter import (
    DAY_MODEL_INTERPRETATION_V1_CONTRACT,
    DAY_MODEL_INTERPRETATION_V1_KEYS,
    DayModelInterpretationError,
    interpret_day_model_v1,
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
def _clear_loader_cache():
    clear_reference_machine_cache()
    yield
    clear_reference_machine_cache()


def _anchor_day_model():
    return aggregate_day_model_v1(
        tarot_entity_code=ANCHOR_TAROT,
        numerology_entity_code=ANCHOR_NUMEROLOGY,
        astrology_planet_code=ANCHOR_PLANET,
        astrology_sign_code=ANCHOR_SIGN,
    )


def _contrast_day_model():
    return aggregate_day_model_v1(
        tarot_entity_code=CONTRAST_TAROT,
        numerology_entity_code=CONTRAST_NUMEROLOGY,
        astrology_planet_code=CONTRAST_ASTRO,
        astrology_sign_code=CONTRAST_SIGN,
    )


def _minimal_day_model(**overrides) -> dict:
    base = {
        "contract_version": DAY_MODEL_V1_CONTRACT_VERSION,
        "mode": "multi_source",
        "vector": {
            "action_reflection": 0.0,
            "expansion_consolidation": 0.0,
            "self_others": 0.0,
            "structure_flow": 0.0,
        },
        "tempo": "steady",
        "risk": "medium",
        "risk_modifier": 0.0,
        "emotional_load": "neutral",
        "confidence": 0.8,
        "sources": [],
        "weights_used": {},
        "missing_sources": [],
        "degraded": False,
    }
    base.update(overrides)
    if "vector" in overrides:
        base["vector"] = {**base["vector"], **overrides["vector"]}
    return base


def test_output_shape_stable():
    result = interpret_day_model_v1(_anchor_day_model())
    assert set(result.keys()) == DAY_MODEL_INTERPRETATION_V1_KEYS
    assert result["contract_version"] == DAY_MODEL_INTERPRETATION_V1_CONTRACT
    assert isinstance(result["reasons"], list)
    assert len(result["reasons"]) >= 5


def test_anchor_strategy_act_or_decide():
    result = interpret_day_model_v1(_anchor_day_model())
    assert result["strategy"] in ("act", "decide", "plan")


def test_contrast_strategy_reflect_or_observe():
    result = interpret_day_model_v1(_contrast_day_model())
    assert result["strategy"] in ("reflect", "observe")


def test_high_risk_intense_load_pressure_low():
    dm = _minimal_day_model(risk="high", emotional_load="intense")
    result = interpret_day_model_v1(dm)
    assert result["pressure_level"] == "low"
    assert any("low_caution" in r for r in result["reasons"])


def test_fast_tempo_high_action_tempo_instruction_move_or_accelerate():
    dm = _minimal_day_model(
        tempo="fast",
        vector={"action_reflection": 0.7, "expansion_consolidation": 0.3, "self_others": 0.0, "structure_flow": 0.0},
    )
    result = interpret_day_model_v1(dm)
    assert result["tempo_instruction"] in ("accelerate", "move")


def test_slow_tempo_reflection_tempo_instruction_slow_down():
    result = interpret_day_model_v1(_contrast_day_model())
    assert result["tempo_instruction"] == "slow_down"


def test_structure_dominant_action_mode_plan():
    result = interpret_day_model_v1(_anchor_day_model())
    assert result["action_mode"] == "plan"


def test_flow_dominant_action_mode_adapt():
    dm = _minimal_day_model(
        vector={
            "action_reflection": 0.0,
            "expansion_consolidation": 0.0,
            "self_others": 0.0,
            "structure_flow": -0.6,
        }
    )
    result = interpret_day_model_v1(dm)
    assert result["action_mode"] == "adapt"
    assert any("adapt" in r for r in result["reasons"])


def test_low_confidence_degraded_interpretation():
    dm = _minimal_day_model(confidence=0.35)
    result = interpret_day_model_v1(dm)
    assert result["degraded"] is True
    assert result["confidence"] < 0.5


def test_rule_hits_in_reasons():
    result = interpret_day_model_v1(_anchor_day_model())
    assert any(r.startswith("R-STRATEGY:") for r in result["reasons"])
    assert any(r.startswith("R-PRESSURE:") for r in result["reasons"])


def test_invalid_contract_version_raises():
    dm = _anchor_day_model()
    dm["contract_version"] = "wrong"
    with pytest.raises(DayModelInterpretationError):
        interpret_day_model_v1(dm)


def test_anchor_contrast_strategy_differ():
    anchor = interpret_day_model_v1(_anchor_day_model())
    contrast = interpret_day_model_v1(_contrast_day_model())
    assert anchor["strategy"] != contrast["strategy"]
