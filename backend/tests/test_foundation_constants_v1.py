"""Foundation constants v1 DATA pack — locks L1–L3."""

from __future__ import annotations

from todayflow_backend.data import foundation_constants_v1 as fc


def test_pack_validates():
    assert fc.validate_foundation_constants_v1() == []


def test_l1_modern_vs_classical_rulers():
    assert fc.sign_ruler("scorpio", mode="modern") == "pluto"
    assert fc.sign_ruler("scorpio", mode="classical") == "mars"
    assert fc.sign_ruler("aquarius", mode="modern") == "uranus"
    assert fc.sign_ruler("aquarius", mode="classical") == "saturn"
    assert fc.sign_ruler("pisces", mode="modern") == "neptune"
    assert fc.sign_ruler("pisces", mode="classical") == "jupiter"
    assert fc.sign_ruler("aries") == "mars"


def test_l2_dual_natural_houses():
    merc = fc.planets_by_id()["mercury"]
    assert merc["natural_houses"] == [3, 6]
    assert merc["natural_house_primary"] == 3
    mars = fc.planets_by_id()["mars"]
    assert mars["natural_houses"] == [1, 8]
    assert mars["natural_house_primary"] == 1


def test_l3_outers_not_for_formulas():
    assert fc.calibrated_dignity("sun") is not None
    assert fc.calibrated_dignity("uranus") is None
    assert fc.calibrated_dignity("neptune") is None
    assert fc.calibrated_dignity("pluto") is None


def test_aspect_lookup_no_quincunx():
    assert "quincunx" not in fc.aspects_by_id()
    assert fc.aspect_character("trine") == "harmonious"
    assert fc.aspects_by_id()["conjunction"]["orb"] == 8
