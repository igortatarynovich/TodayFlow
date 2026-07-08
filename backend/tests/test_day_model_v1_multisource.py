"""P1.0 — DayModel v1 multi-source weighted aggregation."""

from __future__ import annotations

import pytest

from todayflow_backend.data.reference_machine_loader import (
    VECTOR_AXIS_KEYS,
    clear_reference_machine_cache,
)
from todayflow_backend.services.day_model_v1_aggregator import (
    DAY_MODEL_V1_CONTRACT_VERSION,
    DAY_MODEL_V1_KEYS,
    PREVIEW_MODE_MULTI_SOURCE,
    TEMPO_DOMAIN_WEIGHTS,
    TEMPO_SCORES,
    VECTOR_DOMAIN_WEIGHTS,
    DayModelAggregationError,
    aggregate_day_model_v1,
    compose_astrology_atom_pair,
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


def _aggregate_anchor():
    return aggregate_day_model_v1(
        tarot_entity_code=ANCHOR_TAROT,
        numerology_entity_code=ANCHOR_NUMEROLOGY,
        astrology_planet_code=ANCHOR_PLANET,
        astrology_sign_code=ANCHOR_SIGN,
    )


def _aggregate_contrast():
    return aggregate_day_model_v1(
        tarot_entity_code=CONTRAST_TAROT,
        numerology_entity_code=CONTRAST_NUMEROLOGY,
        astrology_planet_code=CONTRAST_ASTRO,
        astrology_sign_code=CONTRAST_SIGN,
    )


def test_output_shape_stable():
    result = _aggregate_anchor()
    assert set(result.keys()) == DAY_MODEL_V1_KEYS
    assert result["contract_version"] == DAY_MODEL_V1_CONTRACT_VERSION
    assert result["mode"] == PREVIEW_MODE_MULTI_SOURCE
    assert set(result["vector"].keys()) == set(VECTOR_AXIS_KEYS)


def test_weights_used_match_canon():
    result = _aggregate_anchor()
    assert result["weights_used"]["vector"] == VECTOR_DOMAIN_WEIGHTS
    assert result["weights_used"]["tempo"] == TEMPO_DOMAIN_WEIGHTS
    assert sum(VECTOR_DOMAIN_WEIGHTS.values()) == pytest.approx(1.0)
    assert sum(TEMPO_DOMAIN_WEIGHTS.values()) == pytest.approx(1.0)


def test_all_three_domains_required_in_sources():
    result = _aggregate_anchor()
    assert len(result["sources"]) == 4
    assert ANCHOR_TAROT in result["sources"]
    assert ANCHOR_NUMEROLOGY in result["sources"]
    assert ANCHOR_PLANET in result["sources"]
    assert ANCHOR_SIGN in result["sources"]
    assert result["missing_sources"] == []
    assert result["degraded"] is False


def test_vector_weighted_per_axis():
    result = _aggregate_anchor()
    assert result["vector"]["action_reflection"] > 0.0
    for axis in VECTOR_AXIS_KEYS:
        assert -1.0 <= result["vector"][axis] <= 1.0


def test_tempo_aggregated_via_score_not_plain_enum_pick():
    result = _aggregate_anchor()
    assert result["tempo"] != "slow"
    assert result["tempo"] in TEMPO_SCORES


def test_risk_and_risk_modifier_present():
    result = _aggregate_anchor()
    assert result["risk"] in ("low", "medium", "high")
    assert -1.0 <= result["risk_modifier"] <= 1.0


def test_emotional_load_aggregated():
    result = _aggregate_anchor()
    assert result["emotional_load"] in ("calm", "neutral", "intense")


def test_confidence_weighted_average():
    result = _aggregate_anchor()
    assert 0.0 < result["confidence"] <= 1.0


def test_anchor_set_action_oriented_through_aggregator():
    result = _aggregate_anchor()
    assert result["vector"]["action_reflection"] > 0.15
    assert result["tempo"] != "slow"
    assert result["risk"] != "low"
    assert result["emotional_load"] != "calm"


def test_contrast_set_reflection_oriented_through_aggregator():
    result = _aggregate_contrast()
    assert result["vector"]["action_reflection"] < 0.0
    assert result["tempo"] in ("slow", "steady")
    assert result["emotional_load"] in ("calm", "neutral")


def test_anchor_vs_contrast_separable_on_action():
    anchor = _aggregate_anchor()
    contrast = _aggregate_contrast()
    assert anchor["vector"]["action_reflection"] > contrast["vector"]["action_reflection"]


def test_unknown_tarot_raises_clear_error():
    with pytest.raises(DayModelAggregationError, match="unknown reference machine source"):
        aggregate_day_model_v1(
            tarot_entity_code="tarot.major.99",
            numerology_entity_code=ANCHOR_NUMEROLOGY,
            astrology_planet_code=ANCHOR_PLANET,
            astrology_sign_code=ANCHOR_SIGN,
        )


def test_missing_domain_raises_when_required():
    with pytest.raises(DayModelAggregationError, match="missing: tarot"):
        aggregate_day_model_v1(
            tarot_entity_code="",
            numerology_entity_code=ANCHOR_NUMEROLOGY,
            astrology_planet_code=ANCHOR_PLANET,
            astrology_sign_code=ANCHOR_SIGN,
        )


def test_missing_domain_degraded_when_not_required():
    result = aggregate_day_model_v1(
        tarot_entity_code="",
        numerology_entity_code=ANCHOR_NUMEROLOGY,
        astrology_planet_code=ANCHOR_PLANET,
        astrology_sign_code=ANCHOR_SIGN,
        require_all_domains=False,
    )
    assert result["degraded"] is True
    assert "tarot" in result["missing_sources"]


def test_compose_astrology_atom_pair_is_in_memory_only():
    composed = compose_astrology_atom_pair(ANCHOR_PLANET, ANCHOR_SIGN)
    assert composed.vector.action_reflection > 0.7
