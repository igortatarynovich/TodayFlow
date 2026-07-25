"""Tests for day_scenario → day_story wire projection (Phase B3)."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.day_events_ranker_v1 import rank_day_events
from todayflow_backend.services.day_scenario_project_v1 import (
    LEGACY_NON_SOT,
    PROJECTION_MAP,
    project_day_scenario_onto_day_story_v1,
)
from todayflow_backend.services.day_scenario_v1 import build_day_scenario_v1
from todayflow_backend.services.day_story_interpretation_v1 import build_day_story_interpretation_v1
from todayflow_backend.services.day_story_v1 import (
    build_day_story_fallback_v1,
    day_story_to_today_contract_v1,
)
from todayflow_backend.services.day_thesis_v1 import build_day_thesis_v1


def _pack():
    return rank_day_events(
        [
            {
                "id": "moon-pisces",
                "kind": "moon_ingress",
                "title_ru": "Луна → Рыбы",
                "fact_ru": "Луна вошла в Рыбы.",
                "body": "Moon",
                "sign": "Pisces",
                "priority_hint": "primary",
            },
            {
                "id": "merc-direct",
                "kind": "station_direct",
                "title_ru": "Меркурий direct",
                "fact_ru": "Меркурий разворачивается в директ.",
                "priority_hint": "primary",
            },
        ]
    )


def _scenario_and_fallback():
    pack = _pack()
    thesis = build_day_thesis_v1(day_events_pack=pack)
    ritual = {
        "tarot_name_ru": "Отшельник",
        "numerology_value": 7,
        "head_topic": "relationships",
    }
    interp = build_day_story_interpretation_v1(
        day_engine_brief={
            "anchor_summary": "Ось.",
            "do_hint": "Шаг.",
            "avoid_hint": "Не соглашайся сразу.",
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
    story = build_day_story_fallback_v1(
        day_engine_brief={"anchor_summary": "Ось.", "do_hint": "Шаг.", "avoid_hint": "Стоп."},
        color="Лазурь",
        interpretation=interp,
        celestial_events={"day_events_pack": pack},
        ritual_context=ritual,
        target_date=date(2026, 7, 24),
        birth_date=date(1990, 3, 15),
    )
    return story, scenario, interp


def test_projection_recovers_unavailable_with_scenario_editorial():
    story, scenario, _ = _scenario_and_fallback()
    assert story.get("interpretation_status") == "unavailable"
    projected = project_day_scenario_onto_day_story_v1(story, scenario)
    assert projected["interpretation_status"] == "ok"
    assert projected["expect"]
    assert projected["trap"]
    assert projected["do"]
    assert projected["talisman"]["color"] == scenario["props"]["color"]["name"]
    assert projected["talisman"].get("origin_scene_id")
    assert projected["practice_recommendation"]["kind"] == "affirmation"
    assert projected["day_scenario"]["runtime_sot"] is True
    assert projected["interpretive_chorus"]["day_card"]["named"]
    assert "Отшельник" in projected["interpretive_chorus"]["day_card"]["named"]
    assert projected["editorial"]["runtime_source"] == "day_scenario_v1"
    contract = day_story_to_today_contract_v1(projected)
    assert contract["day_story"]["interpretation_status"] == "ok"
    assert contract["day_story"]["expect"]
    assert contract["day_story"].get("day_scenario")
    assert contract["day_story"].get("interpretive_chorus")
    from todayflow_backend.services.day_story_v1 import validate_day_story_v1

    assert validate_day_story_v1(projected) == []


def test_projection_does_not_wipe_llm_expect():
    story, scenario, _ = _scenario_and_fallback()
    story["interpretation_status"] = "ok"
    story.pop("interpretation_unavailable_message", None)
    story["expect"] = "LLM expect: появится письмо, на которое захочется ответить сразу."
    story["trap"] = "LLM trap: согласиться ради тишины."
    story["do"] = ["LLM do: сначала черновик."]
    projected = project_day_scenario_onto_day_story_v1(story, scenario)
    assert projected["expect"].startswith("LLM expect")
    assert projected["trap"].startswith("LLM trap")
    assert projected["do"][0].startswith("LLM do")
    # Color still from scenario
    assert projected["talisman"]["color"] == scenario["props"]["color"]["name"]


def test_missing_scenes_keeps_unavailable():
    story, scenario, _ = _scenario_and_fallback()
    scenario["scenes"] = []
    projected = project_day_scenario_onto_day_story_v1(story, scenario)
    assert projected["interpretation_status"] == "unavailable"
    assert projected.get("day_scenario")
    assert projected.get("editorial", {}).get("runtime_source") == "scenario_meta_only"


def test_projection_map_documents_legacy():
    assert "talisman.color" in PROJECTION_MAP
    assert any("formula" in x for x in LEGACY_NON_SOT)
