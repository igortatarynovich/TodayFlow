"""Tests for vedic_personal (gochara + Vimshottari dasha)."""

from __future__ import annotations

from datetime import date, time

from todayflow_backend.services.day_personal_v1 import build_day_personal_v1
from todayflow_backend.services.day_sources import DaySourceInputs, collect_personal_sources
from todayflow_backend.services.day_sources.registry import default_registry
from todayflow_backend.services.day_sources.vedic_personal import (
    build_vedic_personal_payload,
    natal_moon_ref,
    vimshottari_at,
)
from todayflow_backend.services.day_story_interpretation_v1 import (
    build_day_story_interpretation_v1,
)


def test_natal_moon_has_nakshatra_and_lord():
    natal = natal_moon_ref(date(1990, 3, 15))
    assert 0 <= natal["nakshatra"]["index"] <= 26
    assert natal["lord"] in {
        "ketu",
        "venus",
        "sun",
        "moon",
        "mars",
        "rahu",
        "jupiter",
        "saturn",
        "mercury",
    }
    assert natal["sign_ru"]


def test_vimshottari_balance_and_current_md():
    natal = natal_moon_ref(date(1990, 3, 15))
    dasha = vimshottari_at(date(1990, 3, 15), date(2026, 7, 24), natal)
    assert dasha["balance_years"] > 0
    assert dasha["mahadasha"]["lord_ru"]
    assert dasha["antardasha"]["lord_ru"]
    assert dasha["mahadasha"]["start"] <= "2026-07-24" <= dasha["mahadasha"]["end"]


def test_vedic_personal_registered_not_in_foundation():
    reg = default_registry()
    spec = reg.get("vedic_personal")
    assert spec is not None
    assert spec.in_foundation is False
    assert spec.in_personal is True


def test_unavailable_without_birth():
    bundle = collect_personal_sources(DaySourceInputs(target_date=date(2026, 7, 24)))
    assert bundle["sources"]["vedic_personal"]["status"] == "unavailable"
    assert bundle["sources"]["vedic_personal"]["unavailable_reason"] == "missing_birth_date"


def test_gochara_and_dasha_payload():
    payload = build_vedic_personal_payload(
        date(2026, 7, 24),
        date(1990, 3, 15),
        has_birth_time=True,
        has_birth_place=True,
    )
    assert "gochara" in payload["capability_ids"]
    assert "dasha" in payload["capability_ids"]
    assert 1 <= payload["gochara"]["transit_moon"]["house_from_natal_moon"] <= 12
    assert payload["depth"] == "chandra_lagna_time_known"
    assert payload["beats"]


def test_day_personal_and_interpretation():
    personal = build_day_personal_v1(
        {},
        target_date=date(2026, 7, 24),
        birth_date=date(1990, 3, 15),
        birth_time=time(10, 0),
        birth_lat=55.75,
        birth_lon=37.62,
    )
    assert personal["source_inputs"]["has_vedic_personal"] is True
    assert personal["vedic_personal"]["dasha"]["mahadasha"]["lord"]

    interp = build_day_story_interpretation_v1(
        day_engine_brief={"anchor_summary": "Ось.", "do_hint": "Шаг.", "avoid_hint": "Стоп."},
        celestial_events={},
        target_date=date(2026, 7, 24),
        birth_date=date(1990, 3, 15),
    )
    claim_ids = {c["id"] for c in interp["derived_claims"]}
    assert any(i.startswith("claim.personal.vedic.") for i in claim_ids)
