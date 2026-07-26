"""Tests for day_scenario → day_story wire projection (Phase B5 exclusive SoT)."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.day_events_ranker_v1 import rank_day_events
from todayflow_backend.services.day_scenario_project_v1 import (
    LEGACY_NON_SOT,
    PROJECTION_MAP,
    PROJECTION_VERSION,
    project_day_scenario_onto_day_story_v1,
)
from todayflow_backend.services.day_scenario_v1 import build_day_scenario_v1
from todayflow_backend.services.day_story_interpretation_v1 import build_day_story_interpretation_v1
from todayflow_backend.services.day_story_v1 import (
    build_day_story_fallback_v1,
    day_story_to_today_contract_v1,
    validate_day_story_v1,
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
    assert projected["talisman"]["provenance"]["source_kind"] == "day_scenario_v1"
    assert projected["practice_recommendation"]["kind"] == "affirmation"
    assert projected["day_scenario"]["runtime_sot"] is True
    assert projected["interpretive_chorus"]["day_card"]["named"]
    assert "Отшельник" in projected["interpretive_chorus"]["day_card"]["named"]
    assert projected["editorial"]["runtime_source"] == "day_scenario_v1"
    assert projected["editorial"]["projection_version"] == PROJECTION_VERSION
    assert projected["editorial"]["slot_provenance"]["expect"]["origin_scene_id"]
    contract = day_story_to_today_contract_v1(projected)
    assert contract["day_story"]["interpretation_status"] == "ok"
    assert contract["day_story"]["expect"]
    assert contract["day_story"].get("day_scenario")
    assert contract["day_story"].get("interpretive_chorus")
    assert validate_day_story_v1(projected) == []


def test_projection_overwrites_llm_expect():
    """B5: scenario is exclusive SoT — LLM prose must not survive as meaning."""
    story, scenario, _ = _scenario_and_fallback()
    story["interpretation_status"] = "ok"
    story.pop("interpretation_unavailable_message", None)
    story["expect"] = "LLM expect: появится письмо, на которое захочется ответить сразу."
    story["trap"] = "LLM trap: согласиться ради тишины."
    story["do"] = ["LLM do: сначала черновик."]
    story["domains"] = {
        "relationships": {
            "status": "LLM status",
            "opportunity": "LLM opportunity prose that must not remain",
            "risk": "LLM risk",
            "action": "LLM action",
            "evidence_status": "present",
        }
    }
    projected = project_day_scenario_onto_day_story_v1(story, scenario)
    assert not str(projected["expect"]).startswith("LLM expect")
    assert not str(projected["trap"]).startswith("LLM trap")
    assert not str(projected["do"][0]).startswith("LLM do")
    assert projected["talisman"]["color"] == scenario["props"]["color"]["name"]
    rel = projected["domains"].get("relationships") or {}
    assert "LLM opportunity" not in str(rel.get("opportunity") or "")
    assert projected["editorial"]["runtime_source"] == "day_scenario_v1"
    assert projected["editorial"].get("scenario_overlay") is None


def test_missing_scenes_strips_legacy_and_keeps_unavailable():
    story, scenario, _ = _scenario_and_fallback()
    story["interpretation_status"] = "ok"
    story["expect"] = "Legacy expect that must disappear."
    story["trap"] = "Legacy trap."
    story["do"] = ["Legacy do"]
    story["talisman"] = {"color": "Каталожный", "note": "catalog why"}
    scenario["scenes"] = []
    projected = project_day_scenario_onto_day_story_v1(story, scenario)
    assert projected["interpretation_status"] == "unavailable"
    assert projected.get("expect") == ""
    assert projected.get("trap") == ""
    assert projected.get("do") == []
    assert projected.get("talisman") is None
    assert projected.get("day_scenario")
    assert projected.get("editorial", {}).get("runtime_source") == "scenario_meta_only"
    from todayflow_backend.services.today_contract_assembler_v1 import validate_today_contract_v1

    contract = day_story_to_today_contract_v1(projected, generation_id="scenario-meta")
    assert contract["day_story"]["interpretation_status"] == "unavailable"
    assert contract["day_story"]["expect"] == ""
    assert contract["day_story"]["talisman"] == {}
    assert validate_today_contract_v1(contract) == []


def test_no_scenario_is_facts_only_unavailable():
    from todayflow_backend.services.today_contract_assembler_v1 import validate_today_contract_v1

    story, _, _ = _scenario_and_fallback()
    story["expect"] = "Should vanish"
    projected = project_day_scenario_onto_day_story_v1(story, None)
    assert projected["interpretation_status"] == "unavailable"
    assert projected["expect"] == ""
    assert projected.get("day_scenario") is None
    assert projected["editorial"]["runtime_source"] == "facts_only_unavailable"
    contract = day_story_to_today_contract_v1(projected, generation_id="facts-only")
    assert contract["day_story"]["interpretation_status"] == "unavailable"
    assert validate_today_contract_v1(contract) == []


def test_props_require_origin_scene_id():
    _, scenario, _ = _scenario_and_fallback()
    assert scenario["props"]["color"]["origin_scene_id"]
    assert scenario["props"]["avoid_color"]["origin_scene_id"]
    for g in scenario["props"]["goals"]:
        assert g["origin_scene_id"]
    for a in scenario["props"]["affirmations"]:
        assert a["origin_scene_id"]


def test_projection_map_documents_legacy():
    assert "talisman.color" in PROJECTION_MAP
    assert any("formula" in x for x in LEGACY_NON_SOT)
    assert any("LLM" in x for x in LEGACY_NON_SOT)
