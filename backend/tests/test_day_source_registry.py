"""Tests for Day Source Registry + sources-backed Day Foundation."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.day_foundation_v1 import (
    DAY_FOUNDATION_CALC_VERSION,
    build_day_foundation_from_sources,
    build_day_foundation_v1,
)
from todayflow_backend.services.day_sources import DaySourceInputs, collect_foundation_sources
from todayflow_backend.services.day_sources.adapters.numerology import universal_day_number
from todayflow_backend.services.day_sources.inputs_from_profile import birth_date_from_core_profile
from todayflow_backend.services.day_sources.registry import default_registry
from todayflow_backend.services.day_sources.void_of_course import build_void_of_course_v0


def _sample_ce() -> dict:
    return {
        "lunar_phase": {
            "id": "waning",
            "name": "Убывающая луна",
            "themes": "отпускание лишнего",
            "guidance": "Отпускай лишнее, чтобы осталось главное.",
            "cycle_day": 22,
            "next_phase": {"name": "Новолуние", "in_days": 3},
        },
        "moon_sign": {"sign": "Sagittarius", "sign_ru": "Стрелец", "source": "transit_chart"},
        "ingresses": [
            {
                "planet": "Mercury",
                "planet_ru": "Меркурий",
                "sign_ru": "Рак",
                "story_ru": "Меркурий переходит в Рак — меняется тон разговоров.",
            },
            {
                "planet": "Moon",
                "planet_ru": "Луна",
                "sign_ru": "Стрелец",
                "story_ru": "Луна переходит в Стрелец — взгляд расширяется.",
            },
        ],
        "retrogrades": [],
        "sky_aspects": [
            {
                "id": "sun-trine-saturn",
                "title": "Солнце — тригон — Сатурн",
                "story_ru": "Структура дня поддерживает спокойные решения.",
            },
            {
                "id": "moon-square-mars",
                "title": "Луна — квадрат — Марс",
                "story_ru": "Эмоции быстрее, чем обычно, толкают к действию.",
            },
        ],
    }


def test_registry_lists_v1_families():
    reg = default_registry()
    ids = reg.list_families()
    assert ids == [
        "bazi",
        "chinese_metaphysics",
        "human_design",
        "kabbalah_letter",
        "mayan_calendars",
        "moon",
        "numerology",
        "personal_astrology",
        "planetary_hours",
        "seasonal_calendar",
        "vedic_panchanga",
        "vedic_personal",
        "weekday_ruler",
        "western_astrology",
    ]


def test_universal_day_canon_example():
    # 24.07.2026 → 2+4+0+7+2+0+2+6 = 23 → 5
    assert universal_day_number(date(2026, 7, 24)) == 5


def test_collect_without_celestial_keeps_date_families():
    bundle = collect_foundation_sources(
        DaySourceInputs(target_date=date(2026, 7, 24))
    )
    sources = bundle["sources"]
    assert sources["numerology"]["status"] == "ok"
    assert sources["numerology"]["payload"]["universal_day"] == 5
    assert sources["weekday_ruler"]["status"] == "ok"
    assert sources["weekday_ruler"]["payload"]["ruler_planet"] == "Venus"  # Friday
    assert sources["western_astrology"]["status"] == "unavailable"
    assert sources["moon"]["status"] == "unavailable"


def test_collect_with_celestial_splits_astro_and_moon():
    bundle = collect_foundation_sources(
        DaySourceInputs(
            target_date=date(2026, 7, 24),
            celestial_events=_sample_ce(),
        )
    )
    west = bundle["sources"]["western_astrology"]
    moon = bundle["sources"]["moon"]
    assert west["status"] == "ok"
    assert moon["status"] == "ok"
    assert any(i.get("planet") == "Mercury" for i in west["payload"]["ingresses"])
    assert any(i.get("planet") == "Moon" for i in moon["payload"]["ingresses"])
    assert all("Луна" not in (a.get("title") or "") for a in west["payload"]["sky_aspects"])


def test_personal_numerology_requires_birth_date():
    bundle = collect_foundation_sources(
        DaySourceInputs(
            target_date=date(2026, 7, 24),
            birth_date=date(1990, 3, 15),
        )
    )
    payload = bundle["sources"]["numerology"]["payload"]
    assert "personal_day" in payload
    assert "universal_day" in payload


def test_foundation_from_registry_bundle():
    bundle = collect_foundation_sources(
        DaySourceInputs(
            target_date=date(2026, 7, 24),
            celestial_events=_sample_ce(),
        )
    )
    f = build_day_foundation_from_sources(bundle)
    assert f["calculation_version"] == DAY_FOUNDATION_CALC_VERSION
    assert f["astro"]["summary_ru"]
    assert f["lunar"]["summary_ru"]
    assert f["numerology"]["universal_day"] == 5
    assert f["weekday"]["ruler_planet"] == "Venus"
    assert f["essence"]["story_ru"]
    assert "western_astrology" in f["source_inputs"]["ok_family_ids"]
    assert "moon" in f["source_inputs"]["ok_family_ids"]


def test_legacy_build_day_foundation_v1_compat():
    f = build_day_foundation_v1(_sample_ce(), target_date=date(2026, 7, 24))
    assert f["essence"]["theme"]
    empty = build_day_foundation_v1({}, target_date=date(2026, 7, 24))
    assert empty["essence"]["story_ru"] == ""
    assert empty["source_inputs"]["has_essence"] is False
    assert empty["numerology"]["universal_day"] == 5


def test_birth_date_from_core_profile():
    assert birth_date_from_core_profile({"astro": {"birth_date": "1990-03-15"}}) == date(
        1990, 3, 15
    )
    assert birth_date_from_core_profile({}) is None


def test_void_of_course_unavailable_without_timed_aspects():
    voc = build_void_of_course_v0(
        target_date=date(2026, 7, 24),
        ingresses=[
            {"planet": "Moon", "planet_ru": "Луна", "ingress_date": "2026-07-25"},
        ],
        timed_lunar_aspects=None,
    )
    assert voc["status"] == "unavailable"
    assert voc["unavailable_reason"] == "missing_aspect_timeline"
    assert voc["rule_id"] == "majors_only_v1"
    assert voc["next_moon_ingress_date"] == "2026-07-25"


def test_void_of_course_ok_with_timed_aspects():
    voc = build_void_of_course_v0(
        target_date=date(2026, 7, 24),
        ingresses=[{"planet": "Moon", "ingress_date": "2026-07-25"}],
        timed_lunar_aspects=[
            {
                "id": "moon-trine-venus",
                "exact_time": "2026-07-24T08:00:00",
            }
        ],
    )
    assert voc["status"] == "ok"
    assert voc["in_void_of_course"] is True
    assert voc["starts_at"].startswith("2026-07-24")
    assert voc["ends_at"] == "2026-07-25"


def test_foundation_voc_beat_when_in_void():
    ce = _sample_ce()
    ce["void_of_course"] = {
        "rule_id": "majors_only_v1",
        "status": "ok",
        "in_void_of_course": True,
        "starts_at": "2026-07-24T08:00:00",
        "ends_at": "2026-07-25",
    }
    f = build_day_foundation_v1(ce, target_date=date(2026, 7, 24))
    kinds = {b["kind"] for b in f["lunar"]["beats"]}
    assert "void_of_course" in kinds
    assert f["lunar"]["void_of_course"]["status"] == "ok"
