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
    assert "profections" in personal["personal_astrology"]["capability_ids"]
    assert personal["personal_astrology"]["profections"]["annual"]["house"]
    assert personal["personal_astrology"]["beats"][0]["title"]


def test_profections_without_transits():
    personal = build_day_personal_v1(
        {},
        target_date=date(2026, 7, 24),
        birth_date=date(1990, 3, 15),
    )
    assert personal["source_inputs"]["has_personal_astrology"] is True
    pa = personal["personal_astrology"]
    assert "profections" in pa["capability_ids"]
    assert "secondary_progressions" in pa["capability_ids"]
    assert "solar_arc" in pa["capability_ids"]
    assert "solar_return" in pa["capability_ids"]
    assert "lunar_return" in pa["capability_ids"]
    assert pa["profections"]["depth"] == "solar_proxy"
    assert 1 <= pa["profections"]["annual"]["house"] <= 12
    assert pa["secondary_progressions"]["progressed"]["sun"]["sign_ru"]
    assert pa["solar_arc"]["arc_degrees"] >= 0
    assert pa["solar_return"]["return_date"]
    assert pa["lunar_return"]["return_date"]


def test_progressions_and_solar_arc_math():
    from todayflow_backend.services.day_sources.progressions import (
        build_progressions_pack,
        progressed_calendar_date,
    )

    birth = date(1990, 3, 15)
    on = date(2026, 7, 24)
    pack = build_progressions_pack(birth, on)
    # ~36.35 years → progressed date ~36 days after birth
    assert pack["secondary_progressions"]["progressed_date"] == progressed_calendar_date(
        birth, on
    ).isoformat()
    assert abs(pack["solar_arc"]["arc_degrees"] - 36.0) < 5.0
    timed = build_progressions_pack(
        birth,
        on,
        birth_time=time(14, 30),
        birth_lat=55.75,
        birth_lon=37.62,
        timezone_name="Europe/Moscow",
    )
    assert timed["secondary_progressions"]["depth"] == "sun_moon_asc_soft"
    assert timed["solar_arc"]["bodies"]["ascendant"]["sign_ru"]


def test_solar_and_lunar_returns():
    from todayflow_backend.services.day_sources.returns import (
        build_returns_pack,
        find_solar_return_date,
    )

    birth = date(1990, 3, 15)
    on = date(2026, 7, 24)
    sr_d, _lon, err = find_solar_return_date(birth, 2026)
    assert sr_d.month in (3, 4)  # near birthday
    assert err < 1.0  # noon search within ~1°

    pack = build_returns_pack(birth, on)
    assert pack["solar_return"]["period_year"] == 2026
    assert pack["solar_return"]["days_since_return"] >= 0
    assert pack["solar_return"]["days_until_next"] > 0
    assert pack["lunar_return"]["days_since_return"] >= 0
    assert pack["lunar_return"]["days_until_next"] >= 0
    # Last lunar return should be on/before target; next after.
    assert pack["lunar_return"]["return_date"] <= on.isoformat()
    assert pack["lunar_return"]["next_return_date"] > on.isoformat()

    timed = build_returns_pack(
        birth,
        on,
        birth_time=time(14, 30),
        birth_lat=55.75,
        birth_lon=37.62,
        timezone_name="Europe/Moscow",
    )
    assert timed["solar_return"]["depth"] == "sun_moon_asc_soft"
    assert timed["solar_return"]["return_chart_soft"]["ascendant"]["sign_ru"]
    assert timed["lunar_return"]["return_chart_soft"]["ascendant"]["sign_ru"]


def test_profections_asc_when_time_and_place():
    from todayflow_backend.services.day_sources.profections import build_profections

    prof = build_profections(
        date(1990, 3, 15),
        date(2026, 7, 24),
        birth_time=time(14, 30),
        birth_lat=55.75,
        birth_lon=37.62,
        timezone_name="Europe/Moscow",
    )
    assert prof["depth"] == "asc_whole_sign"
    assert prof["annual"]["lord_ru"]
    assert prof["monthly"]["house"]


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
    assert "profections" in personal["personal_astrology"]["capability_ids"]
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
