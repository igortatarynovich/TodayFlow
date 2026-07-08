"""Чистая логика номера дома без вызова Swiss Ephemeris."""

from todayflow_astro.core import models
from todayflow_astro.services.engine import AstroEngine


def test_house_equal_30_degree_segments():
    cusps = [i * 30.0 for i in range(12)]
    assert AstroEngine._house_for_longitude(15.0, cusps) == 1
    assert AstroEngine._house_for_longitude(45.0, cusps) == 2
    assert AstroEngine._house_for_longitude(359.9, cusps) == 12


def test_house_wraps_across_aries_pisces_boundary():
    cusps = [350.0, 20.0, 50.0, 80.0, 110.0, 140.0, 170.0, 200.0, 230.0, 260.0, 290.0, 320.0]
    assert AstroEngine._house_for_longitude(355.0, cusps) == 1
    assert AstroEngine._house_for_longitude(10.0, cusps) == 1
    assert AstroEngine._house_for_longitude(25.0, cusps) == 2


def test_with_house_without_cusps_leaves_house_none():
    """unknown_time charts have no cusp_longitudes; south_node must not call _house_for_longitude."""
    pos = models.PlanetPosition(
        body="south_node",
        sign="Aries",
        degree=1.0,
        longitude=15.0,
    )
    assert AstroEngine._with_house(pos, None).house is None
    assert AstroEngine._with_house(pos, []).house is None
