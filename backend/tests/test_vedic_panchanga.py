"""Tests for vedic_panchanga Source Family."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.day_foundation_v1 import build_day_foundation_v1
from todayflow_backend.services.day_sources import DaySourceInputs, collect_foundation_sources
from todayflow_backend.services.day_sources.panchanga import (
    AYANAMSHA_ID,
    compute_panchanga_core,
    build_panchanga_payload,
)
from todayflow_backend.services.day_sources.registry import default_registry


def test_panchanga_core_ranges():
    core = compute_panchanga_core(date(2026, 7, 24))
    assert core["ayanamsha"]["id"] == AYANAMSHA_ID
    assert 1 <= core["tithi"]["number"] <= 30
    assert 1 <= core["nakshatra"]["number"] <= 27
    assert 1 <= core["yoga"]["number"] <= 27
    assert core["nakshatra"]["pada"] in {1, 2, 3, 4}
    assert core["vara"]["ruler_planet"] == "Venus"  # Friday
    assert core["tithi"]["name_ru"]
    assert core["nakshatra"]["name_ru"]


def test_panchanga_muhurta_with_geo():
    payload = build_panchanga_payload(
        date(2026, 7, 24),
        lat=55.75,
        lon=37.62,
        timezone_name="Europe/Moscow",
    )
    assert "muhurta_intervals" in payload["capability_ids"]
    assert payload["muhurta"]["rahu_kala"]["start_local"]
    assert payload["muhurta"]["yamaganda"]["name_ru"] == "Ямаганда"


def test_panchanga_without_geo_skips_muhurta():
    payload = build_panchanga_payload(date(2026, 7, 24))
    assert "muhurta_intervals" not in payload["capability_ids"]
    assert payload["muhurta"] is None


def test_registry_and_foundation_include_panchanga():
    assert "vedic_panchanga" in default_registry().list_families()
    bundle = collect_foundation_sources(DaySourceInputs(target_date=date(2026, 7, 24)))
    assert bundle["sources"]["vedic_panchanga"]["status"] == "ok"
    f = build_day_foundation_v1({}, target_date=date(2026, 7, 24))
    assert f["panchanga"]["tithi"]["number"]
    assert f["source_inputs"]["has_panchanga"] is True
    assert "Lahiri" in f["panchanga"]["summary_ru"] or "титхи" in f["panchanga"]["summary_ru"]
