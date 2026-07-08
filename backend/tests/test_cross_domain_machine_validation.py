"""P0.9 — Cross-domain machine validation (shared coordinate system, not DayModel aggregation)."""

from __future__ import annotations

import pytest

from todayflow_backend.data.reference_machine_loader import (
    EMOTIONAL_LOAD_VALUES,
    RISK_VALUES,
    TEMPO_VALUES,
    VECTOR_AXIS_KEYS,
    clear_reference_machine_cache,
    load_astrology_machine_contracts,
    load_numerology_machine_contracts,
    load_reference_machine_contract,
    load_tarot_major_machine_contracts,
)

# P0.9 anchor / contrast entity codes (atomic CD only — no composite JSON).
ANCHOR_TAROT = "tarot.major.07"
ANCHOR_NUMEROLOGY = "numerology.personal_year.8"
ANCHOR_PLANET = "astrology.planet.mars"
ANCHOR_SIGN = "astrology.sign.aries"

CONTRAST_TAROT = "tarot.major.09"
CONTRAST_NUMEROLOGY = "numerology.core.7"
CONTRAST_ASTRO = "astrology.planet.saturn"

ACTION_PAIRWISE_MAX_DELTA = 0.35


@pytest.fixture(autouse=True)
def _clear_loader_cache():
    clear_reference_machine_cache()
    yield
    clear_reference_machine_cache()


def _mc(record):
    return record.machine_contract


def _vector_dict(record) -> dict[str, float]:
    return _mc(record).vector.as_dict()


def _compose_planet_sign_test_helper(planet_code: str, sign_code: str, *, w_planet: float = 0.55) -> dict[str, float]:
    """
    P0.9 test-only compose — NOT Astrology Composition Engine, NOT Reference JSON.

    See docs/ASTROLOGY_COMPOSITION_MODEL.md §3.1 sketch.
    """
    w_sign = 1.0 - w_planet
    planet = _vector_dict(load_reference_machine_contract("astrology", planet_code))
    sign = _vector_dict(load_reference_machine_contract("astrology", sign_code))
    composed: dict[str, float] = {}
    for axis in VECTOR_AXIS_KEYS:
        composed[axis] = round(w_planet * planet[axis] + w_sign * sign[axis], 2)
    return composed


def _assert_same_machine_scales(record, *, label: str) -> None:
    mc = _mc(record)
    vec = mc.vector.as_dict()
    assert set(vec.keys()) == set(VECTOR_AXIS_KEYS), label
    for axis, value in vec.items():
        assert -1.0 <= value <= 1.0, f"{label}.{axis}={value}"
    assert mc.tempo in TEMPO_VALUES, label
    assert mc.risk in RISK_VALUES, label
    assert mc.emotional_load in EMOTIONAL_LOAD_VALUES, label
    assert 0.0 <= mc.confidence <= 1.0, label
    assert -1.0 <= mc.risk_modifier <= 1.0, label


def _assert_anchor_profile(record, *, label: str) -> None:
    mc = _mc(record)
    assert mc.vector.action_reflection > 0.0, f"{label}: expected action bias"
    assert mc.tempo != "slow", f"{label}: tempo must not be slow"
    assert mc.risk != "low", f"{label}: risk must not be low"
    assert mc.emotional_load != "calm", f"{label}: emotional_load must not be calm"


def _assert_anchor_vector(vector: dict[str, float], *, label: str) -> None:
    assert vector["action_reflection"] > 0.0, f"{label}: expected action bias"
    for axis in VECTOR_AXIS_KEYS:
        assert -1.0 <= vector[axis] <= 1.0, f"{label}.{axis}"


def _assert_contrast_profile(record, *, label: str) -> None:
    mc = _mc(record)
    assert mc.vector.action_reflection <= 0.15, f"{label}: expected reflection bias"
    assert mc.tempo in ("slow", "steady"), f"{label}: tempo slow or steady"
    assert mc.risk in ("low", "medium"), f"{label}: risk controlled"
    assert mc.emotional_load in ("calm", "neutral"), f"{label}: calm or neutral load"


def test_all_three_domains_use_identical_machine_scale_shape():
    """Every CD record exposes the same DayModel-facing machine fields."""
    for record in load_tarot_major_machine_contracts():
        _assert_same_machine_scales(record, label=record.entity_code)
    for record in load_numerology_machine_contracts():
        _assert_same_machine_scales(record, label=record.entity_code)
    for record in load_astrology_machine_contracts():
        _assert_same_machine_scales(record, label=record.entity_code)


def test_anchor_set_action_tempo_risk_load():
    chariot = load_reference_machine_contract("tarot", ANCHOR_TAROT)
    year8 = load_reference_machine_contract("numerology", ANCHOR_NUMEROLOGY)
    mars = load_reference_machine_contract("astrology", ANCHOR_PLANET)
    aries = load_reference_machine_contract("astrology", ANCHOR_SIGN)

    _assert_anchor_profile(chariot, label=ANCHOR_TAROT)
    _assert_anchor_profile(year8, label=ANCHOR_NUMEROLOGY)
    _assert_anchor_profile(mars, label=ANCHOR_PLANET)
    _assert_anchor_profile(aries, label=ANCHOR_SIGN)

    composed = _compose_planet_sign_test_helper(ANCHOR_PLANET, ANCHOR_SIGN)
    _assert_anchor_vector(composed, label="compose(mars,aries)")


def test_anchor_set_strong_archetypes_do_not_conflict():
    """Same direction on action axis; pairwise deltas within editorial tolerance."""
    records = [
        load_reference_machine_contract("tarot", ANCHOR_TAROT),
        load_reference_machine_contract("numerology", ANCHOR_NUMEROLOGY),
        load_reference_machine_contract("astrology", ANCHOR_PLANET),
        load_reference_machine_contract("astrology", ANCHOR_SIGN),
    ]
    actions = [r.machine_contract.vector.action_reflection for r in records]
    assert all(a > 0 for a in actions)
    for i, a in enumerate(actions):
        for b in actions[i + 1 :]:
            assert abs(a - b) <= ACTION_PAIRWISE_MAX_DELTA, f"anchor action delta {a} vs {b}"


def test_contrast_set_reflection_tempo_risk_load():
    hermit = load_reference_machine_contract("tarot", CONTRAST_TAROT)
    seven = load_reference_machine_contract("numerology", CONTRAST_NUMEROLOGY)
    saturn = load_reference_machine_contract("astrology", CONTRAST_ASTRO)

    _assert_contrast_profile(hermit, label=CONTRAST_TAROT)
    _assert_contrast_profile(seven, label=CONTRAST_NUMEROLOGY)
    _assert_contrast_profile(saturn, label=CONTRAST_ASTRO)


def test_contrast_set_differs_from_anchor_on_action_axis():
    anchor_actions = [
        load_reference_machine_contract("tarot", ANCHOR_TAROT).machine_contract.vector.action_reflection,
        load_reference_machine_contract("numerology", ANCHOR_NUMEROLOGY).machine_contract.vector.action_reflection,
        _compose_planet_sign_test_helper(ANCHOR_PLANET, ANCHOR_SIGN)["action_reflection"],
    ]
    contrast_actions = [
        load_reference_machine_contract("tarot", CONTRAST_TAROT).machine_contract.vector.action_reflection,
        load_reference_machine_contract("numerology", CONTRAST_NUMEROLOGY).machine_contract.vector.action_reflection,
        load_reference_machine_contract("astrology", CONTRAST_ASTRO).machine_contract.vector.action_reflection,
    ]
    assert min(anchor_actions) > max(contrast_actions), (
        "anchor and contrast must be separable on action_reflection"
    )


def test_compose_helper_is_not_persisted_composite_entity():
    """Mars + Aries exist only as atoms in DATA/reference; compose lives in this test module."""
    mars = load_reference_machine_contract("astrology", ANCHOR_PLANET)
    aries = load_reference_machine_contract("astrology", ANCHOR_SIGN)
    assert mars.entity_code == "astrology.planet.mars"
    assert aries.entity_code == "astrology.sign.aries"
    composed = _compose_planet_sign_test_helper(ANCHOR_PLANET, ANCHOR_SIGN)
    assert composed["action_reflection"] > 0.7
