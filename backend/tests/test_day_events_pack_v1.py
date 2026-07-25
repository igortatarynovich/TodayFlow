"""Tests for day_events_pack_v1 + day_events_ranker_v1."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.day_events_pack_v1 import (
    build_day_events_pack_v1,
    collect_raw_day_events,
    slim_day_events_for_llm,
)
from todayflow_backend.services.day_events_ranker_v1 import event_strength, rank_day_events


def test_ranker_picks_one_to_three_drivers():
    events = [
        {"id": "a", "kind": "station_direct", "title_ru": "Меркурий direct", "fact_ru": "Выход из Rx"},
        {"id": "b", "kind": "moon_ingress", "title_ru": "Луна → Стрелец", "fact_ru": "Ингресс"},
        {"id": "c", "kind": "calendar", "title_ru": "День года", "fact_ru": "200", "priority_hint": "ambient"},
        {"id": "d", "kind": "lunar_aspect", "title_ru": "Луна квадрат Плутон", "fact_ru": "Накал", "orb_delta": 0.4},
        {"id": "e", "kind": "solar_daylight", "title_ru": "Свет", "fact_ru": "восход", "priority_hint": "ambient"},
    ]
    pack = rank_day_events(events)
    assert pack["contract_version"] == "day_events_pack_v1"
    assert 1 <= len(pack["ranked_drivers"]) <= 3
    assert "a" in pack["ranked_drivers"]
    assert "c" in pack["ambient"]
    assert all(isinstance(e.get("strength"), float) for e in pack["events"])


def test_station_stronger_than_calendar():
    assert event_strength({"kind": "station_direct"}) > event_strength({"kind": "calendar", "priority_hint": "ambient"})


def test_pack_includes_cycle_station_on_july_24():
    ce = {
        "lunar_phase": {
            "id": "waxing",
            "name": "Растущая",
            "guidance": "набирай темп",
            "next_phase": {"name": "Полнолуние", "date": "2026-07-29", "in_days": 5},
        },
        "moon_sign": {"sign": "Sagittarius", "sign_ru": "Стрелец"},
        "ingresses": [
            {
                "planet": "Moon",
                "planet_ru": "Луна",
                "sign": "Sagittarius",
                "sign_ru": "Стрелец",
                "ingress_date": "2026-07-24",
                "exact_time": "2026-07-24T15:30:00+00:00",
                "story_ru": "Луна переходит в Стрелец",
            }
        ],
        "timed_lunar_aspects": [],
        "sky_aspects": [],
        "retrogrades": [],
        "personal_transits": [],
    }
    pack = build_day_events_pack_v1(ce, target_date=date(2026, 7, 24))
    kinds = {e["kind"] for e in pack["events"]}
    assert "station_direct" in kinds or "moon_ingress" in kinds
    assert "cycle-mercury_station_direct_summer" in {e["id"] for e in pack["events"]}
    assert pack["ranked_drivers"]
    slim = slim_day_events_for_llm(pack)
    assert slim["drivers"]
    assert len(slim["drivers"]) <= 3


def test_pack_mars_rx_edge_july_20():
    pack = build_day_events_pack_v1({}, target_date=date(2026, 7, 20))
    ids = {e["id"] for e in pack["events"]}
    assert "cycle-mars_retrograde_window_summer-start" in ids
    assert pack["ranked_drivers"]


def test_collect_raw_dedupes():
    ce = {
        "ingresses": [
            {
                "planet": "Mercury",
                "planet_ru": "Меркурий",
                "sign": "Leo",
                "sign_ru": "Лев",
                "ingress_date": "2026-07-24",
                "story_ru": "Меркурий входит в Лев",
            }
        ]
    }
    raw = collect_raw_day_events(ce, target_date=date(2026, 7, 24))
    ids = [e["id"] for e in raw]
    assert len(ids) == len(set(ids))
