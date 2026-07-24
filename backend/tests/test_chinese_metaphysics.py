"""Tests for chinese_metaphysics Source Family."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.day_foundation_v1 import build_day_foundation_v1
from todayflow_backend.services.day_sources import DaySourceInputs, collect_foundation_sources
from todayflow_backend.services.day_sources.chinese_metaphysics import (
    build_chinese_day_payload,
    day_pillar_index,
    gan_zhi_from_index,
)
from todayflow_backend.services.day_sources.registry import default_registry


def test_epoch_is_jia_zi():
    assert day_pillar_index(date(1984, 2, 2)) == 0
    pillar = gan_zhi_from_index(0)
    assert pillar["label_zh"] == "甲子"
    assert pillar["stem"]["id"] == "jia"
    assert pillar["branch"]["id"] == "zi"


def test_chinese_day_payload_structure():
    payload = build_chinese_day_payload(date(2026, 7, 24))
    assert payload["gan_zhi_day"]["label_zh"]
    assert payload["five_elements_day"]["stem_element"] in {
        "wood",
        "fire",
        "earth",
        "metal",
        "water",
    }
    assert payload["jianchu_officer"]["id"] in {
        "establish",
        "remove",
        "full",
        "balance",
        "stable",
        "initiate",
        "destruction",
        "danger",
        "success",
        "receive",
        "open",
        "close",
    }
    assert payload["solar_term"]["name_ru"]
    assert payload["almanac_actions"]["suitable_ru"]
    assert "lucky_hours_directions" in payload["capability_ids"]
    lucky = payload["lucky_hours_directions"]
    assert lucky["directions"]["xi_shen"]["compass"]
    assert len(lucky["hours"]) == 12
    assert 0 <= payload["gan_zhi_day"]["cycle_index"] < 60


def test_registry_and_foundation_include_chinese():
    assert "chinese_metaphysics" in default_registry().list_families()
    bundle = collect_foundation_sources(DaySourceInputs(target_date=date(2026, 7, 24)))
    assert bundle["sources"]["chinese_metaphysics"]["status"] == "ok"
    f = build_day_foundation_v1({}, target_date=date(2026, 7, 24))
    assert f["chinese"]["gan_zhi_day"]["label_zh"]
    assert f["chinese"]["lucky_hours_directions"]["directions"]["xi_shen"]
    assert f["source_inputs"]["has_chinese"] is True
