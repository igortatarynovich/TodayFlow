"""Tests for bazi personal Source Family (clashes + pillars)."""

from __future__ import annotations

from datetime import date, time

from todayflow_backend.services.day_personal_v1 import build_day_personal_v1
from todayflow_backend.services.day_sources import DaySourceInputs, collect_personal_sources
from todayflow_backend.services.day_sources.bazi import (
    build_bazi_personal_payload,
    chinese_solar_year,
    year_pillar_for_date,
)
from todayflow_backend.services.day_sources.registry import default_registry
from todayflow_backend.services.day_story_interpretation_v1 import (
    build_day_story_interpretation_v1,
)


def test_1984_is_jia_zi_year():
    # After Lichun 1984 → Jia-Zi year.
    pillar = year_pillar_for_date(date(1984, 3, 1))
    assert pillar["label_zh"] == "甲子"
    assert chinese_solar_year(date(1984, 2, 3)) == 1983


def test_2024_wood_dragon_year():
    pillar = year_pillar_for_date(date(2024, 6, 1))
    assert pillar["stem"]["id"] == "jia"
    assert pillar["branch"]["animal"] == "dragon"


def test_bazi_registered_not_in_foundation():
    reg = default_registry()
    spec = reg.get("bazi")
    assert spec is not None
    assert spec.in_foundation is False
    assert spec.in_personal is True


def test_bazi_unavailable_without_birth():
    bundle = collect_personal_sources(DaySourceInputs(target_date=date(2026, 7, 24)))
    assert bundle["sources"]["bazi"]["status"] == "unavailable"
    assert bundle["sources"]["bazi"]["unavailable_reason"] == "missing_birth_date"


def test_bazi_ok_with_birth_and_clash_or_summary():
    payload = build_bazi_personal_payload(
        date(2026, 7, 24),
        date(1990, 3, 15),
        birth_time=time(14, 30),
    )
    assert "clashes" in payload["capability_ids"]
    assert "bazi" in payload["capability_ids"]
    assert payload["depth"] == "four_pillars"
    assert payload["pillars"]["birth_hour"]["label_zh"]
    assert payload["summary_ru"]


def test_day_personal_and_interpretation_include_bazi():
    personal = build_day_personal_v1(
        {},
        target_date=date(2026, 7, 24),
        birth_date=date(1990, 3, 15),
    )
    assert personal["source_inputs"]["has_bazi"] is True
    assert personal["bazi"]["pillars"]["birth_year"]["branch"]["animal"]

    interp = build_day_story_interpretation_v1(
        day_engine_brief={"anchor_summary": "Ось.", "do_hint": "Шаг.", "avoid_hint": "Стоп."},
        celestial_events={},
        target_date=date(2026, 7, 24),
        birth_date=date(1990, 3, 15),
    )
    assert interp["source_inputs"]["has_day_personal"] is True
    claim_ids = {c["id"] for c in interp["derived_claims"]}
    assert any(i.startswith("claim.personal.bazi.") for i in claim_ids)
