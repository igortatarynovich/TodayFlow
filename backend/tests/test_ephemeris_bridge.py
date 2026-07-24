"""Tests for Swiss/AstroService ephemeris bridge."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.day_sources.ephemeris_bridge import (
    ascendant_from_snapshot,
    normalize_positions,
    resolve_body_longitude,
    snapshot_from_positions,
)
from todayflow_backend.services.day_sources.human_design import bodygraph_soft, transit_gates_for_day
from todayflow_backend.services.day_sources.time_lords import build_time_lords


def test_normalize_adds_earth_from_sun():
    bodies = normalize_positions(
        [{"body": "Sun", "longitude": 10.0}, {"body": "Moon", "longitude": 100.0}]
    )
    assert bodies["Sun"]["longitude"] == 10.0
    assert abs(bodies["Earth"]["longitude"] - 190.0) < 1e-9


def test_normalize_maps_rising_to_ascendant():
    bodies = normalize_positions([{"body": "rising", "longitude": 95.5}])
    assert abs(bodies["Ascendant"]["longitude"] - 95.5) < 1e-9


def test_resolve_prefers_swiss_snapshot():
    snap = snapshot_from_positions(
        [{"body": "Mars", "longitude": 123.4}],
        as_of=date(2026, 7, 24),
        role="transit_noon",
    )
    eph = {"transit_noon": snap, "natal": None}
    resolved = resolve_body_longitude("Mars", date(2026, 7, 24), ephemeris=eph, role="transit")
    assert resolved["source"] == "astro_service_swiss"
    assert abs(resolved["longitude"] - 123.4) < 1e-9


def test_resolve_falls_back_to_mean():
    resolved = resolve_body_longitude("Sun", date(2026, 7, 24), ephemeris=None, role="transit")
    assert resolved["source"] == "mean_longitude_soft"
    assert 0.0 <= resolved["longitude"] < 360.0


def test_resolve_design_role_uses_design_snapshot():
    design = snapshot_from_positions(
        [{"body": "Sun", "longitude": 200.0}],
        as_of=date(1990, 1, 16),
        role="design_minus_88d",
    )
    eph = {"design_minus_88d": design}
    resolved = resolve_body_longitude("Sun", date(1990, 1, 16), ephemeris=eph, role="design")
    assert resolved["source"] == "astro_service_swiss"
    assert abs(resolved["longitude"] - 200.0) < 1e-9


def test_ascendant_from_rising_position():
    snap = snapshot_from_positions(
        [{"body": "rising", "longitude": 12.3}],
        as_of=date(1990, 3, 15),
        role="natal",
    )
    assert abs(ascendant_from_snapshot(snap) - 12.3) < 1e-9


def test_hd_transit_uses_swiss_when_injected():
    eph = {
        "transit_noon": snapshot_from_positions(
            [
                {"body": "Sun", "longitude": 302.0},  # gate 41 zone
                {"body": "Moon", "longitude": 0.0},
                {"body": "Mercury", "longitude": 10.0},
                {"body": "Venus", "longitude": 20.0},
                {"body": "Mars", "longitude": 30.0},
                {"body": "Jupiter", "longitude": 40.0},
                {"body": "Saturn", "longitude": 50.0},
                {"body": "Uranus", "longitude": 60.0},
                {"body": "Neptune", "longitude": 70.0},
                {"body": "Pluto", "longitude": 80.0},
            ],
            as_of=date(2026, 7, 24),
            role="transit_noon",
        )
    }
    transit = transit_gates_for_day(date(2026, 7, 24), ephemeris=eph)
    assert transit["ephemeris_source"] == "astro_service_swiss"
    assert transit["depth"] == "full_planet_set_swiss_noon"
    assert transit["sun"]["gate"] == 41


def test_bodygraph_uses_design_swiss_walk():
    natal = snapshot_from_positions(
        [
            {"body": "Sun", "longitude": 10.0},
            {"body": "Moon", "longitude": 40.0},
            {"body": "Mercury", "longitude": 15.0},
            {"body": "Venus", "longitude": 20.0},
            {"body": "Mars", "longitude": 25.0},
            {"body": "Jupiter", "longitude": 30.0},
            {"body": "Saturn", "longitude": 35.0},
            {"body": "Uranus", "longitude": 45.0},
            {"body": "Neptune", "longitude": 50.0},
            {"body": "Pluto", "longitude": 55.0},
        ],
        as_of=date(1990, 3, 15),
        role="natal",
    )
    design = snapshot_from_positions(
        [
            {"body": "Sun", "longitude": 302.0},
            {"body": "Moon", "longitude": 100.0},
            {"body": "Mercury", "longitude": 110.0},
            {"body": "Venus", "longitude": 120.0},
            {"body": "Mars", "longitude": 130.0},
            {"body": "Jupiter", "longitude": 140.0},
            {"body": "Saturn", "longitude": 150.0},
            {"body": "Uranus", "longitude": 160.0},
            {"body": "Neptune", "longitude": 170.0},
            {"body": "Pluto", "longitude": 180.0},
        ],
        as_of=date(1989, 12, 17),
        role="design_minus_88d",
    )
    bg = bodygraph_soft(
        date(1990, 3, 15),
        has_birth_time=True,
        has_birth_place=True,
        ephemeris={"natal": natal, "design_minus_88d": design},
    )
    assert bg["approximation"] == "design_minus_88d_swiss_walk"
    assert bg["ephemeris_source"]["design"] == "astro_service_swiss"
    assert bg["design"]["sun"]["gate"] == 41
    assert "design_swiss" in bg["depth"]


def test_time_lords_swiss_timed_lots():
    natal = snapshot_from_positions(
        [
            {"body": "Sun", "longitude": 20.0},
            {"body": "Moon", "longitude": 80.0},
            {"body": "rising", "longitude": 100.0},
        ],
        as_of=date(1990, 3, 15),
        role="natal",
    )
    pack = build_time_lords(
        date(1990, 3, 15),
        date(2026, 7, 24),
        birth_time=None,
        ephemeris={"natal": natal},
    )
    assert pack["depth"] == "firdaria_zr_fortune_spirit_swiss"
    assert "swiss_timed_lots" in pack["systems_available"]
    assert pack["zodiacal_releasing"]["lot"]["method"].endswith("_swiss")
    # day sect default: Fortune = ASC + Moon − Sun = 100 + 80 − 20 = 160
    assert abs(pack["zodiacal_releasing"]["lot"]["longitude"] - 160.0) < 1e-3
    assert abs(pack["zodiacal_releasing_spirit"]["lot"]["longitude"] - 40.0) < 1e-3
