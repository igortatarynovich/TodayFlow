"""Tests for soft holidays + name_numbers Day Source capabilities."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.day_foundation_v1 import build_day_foundation_v1
from todayflow_backend.services.day_personal_v1 import (
    build_day_personal_v1,
    personal_to_interpretation_claims,
)
from todayflow_backend.services.day_sources import DaySourceInputs, collect_foundation_sources
from todayflow_backend.services.day_sources.holidays import holidays_for_date
from todayflow_backend.services.day_sources.name_numbers import (
    build_name_numbers_payload,
    normalize_name_for_numbers,
)


def test_ru_victory_day_holiday():
    pack = holidays_for_date(date(2026, 5, 9), locale="ru")
    assert pack["is_holiday"] is True
    assert pack["today"][0]["id"] == "victory_day"


def test_seasonal_ok_without_geo_includes_holidays():
    bundle = collect_foundation_sources(DaySourceInputs(target_date=date(2026, 6, 12), locale="ru"))
    seasonal = bundle["sources"]["seasonal_calendar"]
    assert seasonal["status"] == "ok"
    assert "holidays" in seasonal["capability_ids"]
    assert seasonal["payload"]["holidays"]["is_holiday"] is True
    assert seasonal["payload"]["sun"] is None


def test_foundation_wires_holiday():
    f = build_day_foundation_v1({}, target_date=date(2026, 3, 8), locale="ru")
    assert f["seasonal"]["holidays"]["is_holiday"] is True
    assert "женск" in (f["seasonal"]["summary_ru"] or "").lower()


def test_name_normalize_cyrillic():
    assert normalize_name_for_numbers("Анна") == "Anna"
    assert "A" in normalize_name_for_numbers("Яна").upper()


def test_name_numbers_expression():
    pack = build_name_numbers_payload("Anna")
    assert pack is not None
    assert pack["status"] == "ok"
    assert pack["expression"]["value"] in {1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33}
    assert pack["school_canon"] == "pythagorean_latin_v0_via_ru_translit"


def test_day_personal_wires_name_numbers():
    idle = build_day_personal_v1({}, target_date=date(2026, 7, 24))
    assert idle["source_inputs"]["has_name_numbers"] is False

    active = build_day_personal_v1(
        {},
        target_date=date(2026, 7, 24),
        birth_name="Игорь",
    )
    assert active["source_inputs"]["has_name_numbers"] is True
    assert active["name_numbers"]["expression"]["value"]
    claims = personal_to_interpretation_claims(active)
    assert any(c["id"].startswith("claim.personal.name_numbers.") for c in claims)
