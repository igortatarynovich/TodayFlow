"""Tests for day_scenario_v1 — B1 engine (foundation, chorus, conflict, scenes)."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.day_events_ranker_v1 import rank_day_events
from todayflow_backend.services.day_scenario_v1 import (
    DAY_SCENARIO_V1_CONTRACT,
    build_day_scenario_v1,
    build_interpretive_chorus_v1,
    build_scenario_conflict_v1,
    build_scenario_foundation_v1,
    validate_day_scenario_v1,
)
from todayflow_backend.services.day_story_interpretation_v1 import build_day_story_interpretation_v1
from todayflow_backend.services.day_thesis_v1 import build_day_thesis_v1


def _pack_merc_moon():
    return rank_day_events(
        [
            {
                "id": "merc-direct",
                "kind": "station_direct",
                "title_ru": "Меркурий разворачивается в директ",
                "fact_ru": "Меркурий разворачивается в директное движение.",
                "body": "Mercury",
                "priority_hint": "primary",
            },
            {
                "id": "moon-pisces",
                "kind": "moon_ingress",
                "title_ru": "Луна → Рыбы",
                "fact_ru": "Луна вошла в Рыбы.",
                "body": "Moon",
                "sign": "Pisces",
                "priority_hint": "primary",
            },
        ]
    )


def test_scenario_builds_one_conflict_from_drivers_not_card_alone():
    pack = _pack_merc_moon()
    thesis = build_day_thesis_v1(day_events_pack=pack)
    ritual = {
        "tarot_name_ru": "Отшельник",
        "tarot_main_id": "09",
        "numerology_value": 7,
        "head_topic": "relationships",
    }
    interp = build_day_story_interpretation_v1(
        day_engine_brief={
            "anchor_summary": "Ось дня — ясность без сглаживания.",
            "do_hint": "Сказать прямо.",
            "avoid_hint": "Не соглашаться сразу.",
            "thread_head_topic": "relationships",
        },
        ritual_context=ritual,
        celestial_events={"day_events_pack": pack, "lunar_phase": {"name": "Растущая луна"}},
        day_thesis=thesis,
        target_date=date(2026, 7, 24),
        birth_date=date(1990, 3, 15),
    )
    scenario = build_day_scenario_v1(
        interpretation=interp,
        day_events_pack=pack,
        day_thesis=thesis,
        ritual_context=ritual,
    )
    assert scenario["contract_version"] == DAY_SCENARIO_V1_CONTRACT
    assert scenario["runtime_sot"] is False
    assert validate_day_scenario_v1(scenario) == []

    conflict = scenario["conflict"]
    assert conflict["short_name"]
    assert conflict["driver_ids"]
    assert "merc-direct" in conflict["driver_ids"] or "moon-pisces" in conflict["driver_ids"]
    assert conflict["opposing_forces"]["a"]
    assert conflict["opposing_forces"]["b"]
    assert "day_card" in conflict["chorus_references"]
    assert "day_number" in conflict["chorus_references"]

    # Card/number explain, do not replace drivers
    foundation = scenario["foundation"]
    assert foundation["tarot_card"]["name"] == "Отшельник"
    assert foundation["day_number"]["value"] == 7
    assert foundation["ranked_drivers"]


def test_chorus_names_moon_card_number():
    pack = _pack_merc_moon()
    thesis = build_day_thesis_v1(day_events_pack=pack)
    foundation = build_scenario_foundation_v1(
        day_events_pack=pack,
        ritual_context={"tarot_name_ru": "Отшельник", "numerology_value": 7},
    )
    conflict = build_scenario_conflict_v1(foundation=foundation, day_thesis=thesis)
    chorus = build_interpretive_chorus_v1(
        foundation=foundation,
        conflict_label=conflict["short_name"],
    )
    astro_blob = " ".join(v.get("named_factor") or "" for v in chorus["astrology"])
    assert "Рыб" in astro_blob or "Меркурий" in astro_blob or "Луна" in astro_blob
    assert chorus["day_card"]["named_factor"].startswith("Карта дня")
    assert "Отшельник" in chorus["day_card"]["named_factor"]
    assert chorus["day_card"]["must_not_invent_second_plot"] is True
    assert chorus["day_number"]["named_factor"].startswith("Число дня")
    assert chorus["day_number"]["tempo"]  # 7 → глубина
    assert chorus["parallel_forecast_forbidden"] is True


def test_scenes_are_relevant_and_serve_conflict():
    pack = _pack_merc_moon()
    thesis = build_day_thesis_v1(day_events_pack=pack)
    ritual = {"tarot_name_ru": "Отшельник", "numerology_value": 7, "head_topic": "relationships"}
    interp = build_day_story_interpretation_v1(
        day_engine_brief={
            "anchor_summary": "Ось.",
            "do_hint": "Шаг.",
            "avoid_hint": "Не спеши.",
            "thread_head_topic": "relationships",
        },
        ritual_context=ritual,
        celestial_events={"day_events_pack": pack},
        day_thesis=thesis,
        target_date=date(2026, 7, 24),
        birth_date=date(1990, 3, 15),
    )
    scenario = build_day_scenario_v1(
        interpretation=interp,
        day_events_pack=pack,
        day_thesis=thesis,
        ritual_context=ritual,
    )
    scenes = scenario["scenes"]
    assert 1 <= len(scenes) <= 4
    labels = {s["serves_conflict"] for s in scenes}
    assert labels == {scenario["conflict"]["short_name"]}
    spheres = {s["sphere"] for s in scenes}
    # relationships topic should pull relationship/communication spheres
    assert spheres & {"relationships", "communication", "work_decisions"}
    for s in scenes:
        assert s["scene_id"].startswith("scene.")
        assert s["opportunity"]
        assert s["trap"]
        assert s["chorus_references"]


def test_props_deferred_in_b1():
    pack = _pack_merc_moon()
    thesis = build_day_thesis_v1(day_events_pack=pack)
    scenario = build_day_scenario_v1(day_events_pack=pack, day_thesis=thesis)
    assert scenario["props"]["status"] == "deferred_to_b2"
    assert scenario["props"]["color"] is None
    assert scenario["projections"]["status"] == "deferred_to_b3"


def test_validate_rejects_empty_conflict_name():
    pack = _pack_merc_moon()
    scenario = build_day_scenario_v1(day_events_pack=pack)
    scenario["conflict"]["short_name"] = ""
    assert "conflict_missing_short_name" in validate_day_scenario_v1(scenario)
