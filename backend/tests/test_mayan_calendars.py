"""Tests for mayan_calendars Source Family."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.day_foundation_v1 import build_day_foundation_v1
from todayflow_backend.services.day_sources import DaySourceInputs, collect_foundation_sources
from todayflow_backend.services.day_sources.mayan_calendars import (
    build_dreamspell,
    build_mayan_calendars_payload,
    build_tzolkin_haab,
    days_since_maya_epoch,
)
from todayflow_backend.services.day_sources.registry import default_registry


def test_2012_baktun_turn_is_4_ajaw():
    # GMT: 2012-12-21 = 13.0.0.0.0 = 4 Ajaw 3 Kankin.
    d = date(2012, 12, 21)
    assert days_since_maya_epoch(d) == 1872000
    classical = build_tzolkin_haab(d)
    assert classical["tzolkin"]["number"] == 4
    assert classical["tzolkin"]["sign_id"] == "ahau"
    assert classical["haab"]["month_id"] == "kankin"
    assert classical["haab"]["day"] == 3
    assert classical["long_count"]["label"] == "13.0.0.0.0"


def test_dreamspell_epoch_is_kin_1():
    ds = build_dreamspell(date(1987, 7, 26))
    assert ds["kin"] == 1
    assert ds["seal"]["id"] == "dragon"
    assert ds["tone"]["id"] == "magnetic"
    assert ds["not_classical_tzolkin"] is True


def test_capabilities_remain_separate():
    payload = build_mayan_calendars_payload(date(2026, 7, 24))
    assert payload["capability_ids"] == ["tzolkin_haab", "dreamspell"]
    assert payload["tzolkin_haab"]["capability_id"] == "tzolkin_haab"
    assert payload["dreamspell"]["capability_id"] == "dreamspell"
    # Different numbering systems must not share seal/sign ids.
    assert payload["tzolkin_haab"]["tzolkin"]["sign_id"] != payload["dreamspell"]["seal"]["id"]


def test_registry_and_foundation_include_mayan():
    assert "mayan_calendars" in default_registry().list_families()
    bundle = collect_foundation_sources(DaySourceInputs(target_date=date(2026, 7, 24)))
    assert bundle["sources"]["mayan_calendars"]["status"] == "ok"
    f = build_day_foundation_v1({}, target_date=date(2026, 7, 24))
    assert f["mayan"]["tzolkin_haab"]["tzolkin"]["label"]
    assert f["mayan"]["dreamspell"]["kin"]
    assert f["source_inputs"]["has_mayan"] is True
