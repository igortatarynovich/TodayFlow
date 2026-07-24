"""Tests for sun rise/set and planetary hours Source Families."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.day_foundation_v1 import build_day_foundation_v1
from todayflow_backend.services.day_sources import DaySourceInputs, collect_foundation_sources
from todayflow_backend.services.day_sources.adapters.planetary_hours import (
    build_planetary_hours_table,
)
from todayflow_backend.services.day_sources.registry import default_registry
from todayflow_backend.services.day_sources.sun_rise_set import sun_rise_set_local


def test_sun_rise_set_moscow_summer_reasonable():
    sun = sun_rise_set_local(
        date(2026, 7, 24),
        lat=55.75,
        lon=37.62,
        timezone_name="Europe/Moscow",
    )
    assert sun["day_length_minutes"] > 15 * 60  # long summer day
    assert sun["sunrise_local"] < sun["sunset_local"]
    assert "T" in sun["sunrise_local"]


def test_planetary_hours_table_has_24_and_day_ruler_friday():
    # 2026-07-24 is Friday → Venus
    table = build_planetary_hours_table(
        target_date=date(2026, 7, 24),
        lat=55.75,
        lon=37.62,
        timezone_name="Europe/Moscow",
    )
    assert len(table["hours"]) == 24
    assert table["day_ruler_planet"] == "Venus"
    assert table["hours"][0]["ruler_planet"] == "Venus"
    assert table["hours"][0]["period"] == "day"
    assert table["hours"][12]["period"] == "night"
    # Chaldean after Venus → Mercury
    assert table["hours"][1]["ruler_planet"] == "Mercury"


def test_registry_geo_families_unavailable_without_geo():
    bundle = collect_foundation_sources(DaySourceInputs(target_date=date(2026, 7, 24)))
    assert bundle["sources"]["planetary_hours"]["status"] == "unavailable"
    assert bundle["sources"]["seasonal_calendar"]["status"] == "unavailable"
    assert "missing_geo" in bundle["sources"]["planetary_hours"]["unavailable_reason"]


def test_registry_geo_families_ok_with_lat_lon():
    bundle = collect_foundation_sources(
        DaySourceInputs(
            target_date=date(2026, 7, 24),
            lat=55.75,
            lon=37.62,
            timezone="Europe/Moscow",
        )
    )
    assert bundle["sources"]["planetary_hours"]["status"] == "ok"
    assert bundle["sources"]["seasonal_calendar"]["status"] == "ok"
    assert len(bundle["sources"]["planetary_hours"]["payload"]["hours"]) == 24


def test_foundation_includes_planetary_hours_with_geo():
    f = build_day_foundation_v1(
        {},
        target_date=date(2026, 7, 24),
        lat=55.75,
        lon=37.62,
        timezone="Europe/Moscow",
    )
    assert f["planetary_hours"]["day_ruler_planet"] == "Venus"
    assert f["seasonal"]["season"] == "summer"
    assert f["source_inputs"]["has_planetary_hours"] is True


def test_registry_lists_includes_geo_families():
    ids = default_registry().list_families()
    assert "planetary_hours" in ids
    assert "seasonal_calendar" in ids
