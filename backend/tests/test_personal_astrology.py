"""Tests for personal_astrology Source Family (L3)."""

from __future__ import annotations

from datetime import date, time

from todayflow_backend.services.day_personal_v1 import build_day_personal_v1
from todayflow_backend.services.day_sources import DaySourceInputs, collect_personal_sources
from todayflow_backend.services.day_sources.registry import default_registry
from todayflow_backend.services.day_story_interpretation_v1 import (
    build_day_story_interpretation_v1,
)


def _sample_ce_with_transits() -> dict:
    return {
        "personal_transits": [
            {
                "id": "pt-mars-square-sun",
                "transiting_planet": "Mars",
                "natal_planet": "Sun",
                "aspect": "square",
                "title": "Марс — квадрат — Солнце",
                "story_ru": "Личная энергия давит на самопрезентацию.",
                "strength": "strong",
            }
        ]
    }


def test_personal_astrology_registered_not_in_foundation():
    reg = default_registry()
    spec = reg.get("personal_astrology")
    assert spec is not None
    assert spec.in_foundation is False
    assert spec.in_personal is True
    assert "personal_astrology" not in [
        s.family_id for s in reg.resolve(DaySourceInputs(target_date=date(2026, 7, 24)), foundation_only=True)
    ]


def test_personal_unavailable_without_birth_and_transits():
    bundle = collect_personal_sources(DaySourceInputs(target_date=date(2026, 7, 24)))
    assert bundle["sources"]["personal_astrology"]["status"] == "unavailable"
    assert bundle["sources"]["personal_astrology"]["unavailable_reason"] == "missing_birth_date"


def test_personal_ok_with_transits_and_birth_date():
    personal = build_day_personal_v1(
        _sample_ce_with_transits(),
        target_date=date(2026, 7, 24),
        birth_date=date(1990, 3, 15),
    )
    assert personal["source_inputs"]["has_personal_astrology"] is True
    assert personal["personal_astrology"]["depth"] == "sign_level"
    assert personal["personal_astrology"]["beats"][0]["title"]


def test_personal_houses_depth_when_time_and_place():
    personal = build_day_personal_v1(
        _sample_ce_with_transits(),
        target_date=date(2026, 7, 24),
        birth_date=date(1990, 3, 15),
        birth_time=time(14, 30),
        birth_lat=55.75,
        birth_lon=37.62,
    )
    assert "transits_by_house" in personal["personal_astrology"]["capability_ids"]
    assert personal["personal_astrology"]["depth"] == "sign_level_time_known"


def test_interpretation_includes_personal_claims():
    interp = build_day_story_interpretation_v1(
        day_engine_brief={"anchor_summary": "Ось.", "do_hint": "Шаг.", "avoid_hint": "Стоп."},
        celestial_events=_sample_ce_with_transits(),
        target_date=date(2026, 7, 24),
        birth_date=date(1990, 3, 15),
    )
    assert interp["source_inputs"]["has_day_personal"] is True
    assert interp["day_personal"]["personal_astrology"]["beats"]
    claim_ids = {c["id"] for c in interp["derived_claims"]}
    assert any(i.startswith("claim.personal.astro.") for i in claim_ids)
