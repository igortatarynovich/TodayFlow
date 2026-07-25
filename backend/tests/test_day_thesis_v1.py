"""Tests for day_thesis_v1 (replaces primary_conflict as machine plot)."""

from __future__ import annotations

from todayflow_backend.services.day_events_ranker_v1 import rank_day_events
from todayflow_backend.services.day_thesis_v1 import build_day_thesis_v1, conflict_label


def test_station_direct_clarity_thesis():
    pack = rank_day_events(
        [
            {
                "id": "merc-direct",
                "kind": "station_direct",
                "title_ru": "Меркурий direct",
                "fact_ru": "Меркурий разворачивается в директное движение.",
                "body": "Mercury",
                "priority_hint": "primary",
            }
        ]
    )
    thesis = build_day_thesis_v1(day_events_pack=pack)
    assert thesis["family"] == "communication"
    assert thesis["variant"] == "clarity_returns_after_delay"
    assert thesis["mode"] == "transition"
    assert "ясности" in thesis["label_ru"].lower() or "ясност" in thesis["label_ru"].lower()
    assert "merc-direct" in thesis["driver_ids"]


def test_mixed_signals_truth_without_filter():
    pack = rank_day_events(
        [
            {
                "id": "merc-direct",
                "kind": "station_direct",
                "title_ru": "Меркурий direct",
                "fact_ru": "Меркурий разворачивается.",
                "priority_hint": "primary",
            },
            {
                "id": "moon-pluto",
                "kind": "lunar_aspect",
                "title_ru": "Луна квадрат Плутон",
                "fact_ru": "Луна — квадрат — Плутон.",
                "orb_delta": 0.4,
                "priority_hint": "primary",
            },
        ]
    )
    thesis = build_day_thesis_v1(
        day_events_pack=pack,
        day_model={"tension": {"summary": "Высокий накал и давление"}, "risk": {"summary": "Риск срыва"}},
    )
    assert thesis["variant"] == "truth_without_filter"


def test_composition_emitted_for_station_and_ingress():
    pack = rank_day_events(
        [
            {
                "id": "a",
                "kind": "station_direct",
                "title_ru": "Меркурий",
                "fact_ru": "direct",
                "priority_hint": "primary",
            },
            {
                "id": "b",
                "kind": "moon_ingress",
                "title_ru": "Луна → Стрелец",
                "fact_ru": "ingress",
                "priority_hint": "primary",
            },
        ]
    )
    assert pack.get("compositions")
    assert pack["compositions"][0]["relationship"] in {
        "reinforcing",
        "escalating",
        "counterbalancing",
        "transition",
    }


def test_legacy_conflict_label():
    assert "ясн" in conflict_label("clarity_return").lower() or "ясност" in conflict_label(
        "communication.clarity_returns_after_delay"
    ).lower()
