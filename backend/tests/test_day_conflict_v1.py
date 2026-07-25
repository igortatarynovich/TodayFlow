"""Legacy primary_conflict wrapper — prefer day_thesis_v1 tests."""

from __future__ import annotations

from todayflow_backend.services.day_conflict_v1 import conflict_label, pick_primary_conflict
from todayflow_backend.services.day_events_ranker_v1 import rank_day_events


def test_station_direct_picks_clarity_return():
    pack = rank_day_events(
        [
            {
                "id": "merc-direct",
                "kind": "station_direct",
                "title_ru": "Меркурий direct",
                "fact_ru": "Меркурий выходит из ретрограда в Льве.",
                "priority_hint": "primary",
            }
        ]
    )
    conflict = pick_primary_conflict(day_events_pack=pack)
    assert conflict["id"] == "communication.clarity_returns_after_delay"
    assert conflict["day_thesis"]["mode"] == "transition"
    assert "merc-direct" in conflict["driver_ids"]


def test_uranus_hint_picks_sudden_turns():
    pack = rank_day_events(
        [
            {
                "id": "moon-uranus",
                "kind": "lunar_aspect",
                "title_ru": "Луна — оппозиция — Уран",
                "fact_ru": "Луна напротив Урана — внезапные повороты.",
                "orb_delta": 0.5,
                "priority_hint": "primary",
            }
        ]
    )
    conflict = pick_primary_conflict(day_events_pack=pack)
    assert conflict["id"] == "change.sudden_turns"
    assert conflict_label(conflict["id"])
