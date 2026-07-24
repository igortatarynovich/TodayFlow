"""Tests for Swiss/AstroService ephemeris bridge."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.day_sources.ephemeris_bridge import (
    normalize_positions,
    resolve_body_longitude,
    snapshot_from_positions,
)
from todayflow_backend.services.day_sources.human_design import transit_gates_for_day


def test_normalize_adds_earth_from_sun():
    bodies = normalize_positions(
        [{"body": "Sun", "longitude": 10.0}, {"body": "Moon", "longitude": 100.0}]
    )
    assert bodies["Sun"]["longitude"] == 10.0
    assert abs(bodies["Earth"]["longitude"] - 190.0) < 1e-9


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
