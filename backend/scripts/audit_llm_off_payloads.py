"""Audit helper: print representative pre-LLM payloads for each surface."""

from __future__ import annotations

import json
from datetime import date

from todayflow_backend.services.astro import ChartResponse
from todayflow_backend.services.natal_facts_contract_v1 import (
    build_natal_facts_from_chart,
    generate_natal_facts,
)
from todayflow_backend.services.day_context import build_day_context_v0
from todayflow_backend.services.day_scenario_dramaturgy_brief_c4 import (
    build_day_dramaturgy_brief_c4,
)
from todayflow_backend.services.day_events_ranker_v1 import rank_day_events
from todayflow_backend.services.day_thesis_v1 import build_day_thesis_v1
from todayflow_backend.services.ritual_practice_selector_bridge_v1 import (
    select_practice_for_ritual,
)


def _sample_chart():
    return ChartResponse(
        mode="full",
        positions=[
            {"body": "Sun", "sign": "leo", "degree": 12.0, "longitude": 132.0, "house": 5, "retrograde": False},
            {"body": "Moon", "sign": "pisces", "degree": 8.0, "longitude": 338.0, "house": 12},
            {"body": "Mercury", "sign": "virgo", "degree": 2.0, "longitude": 152.0, "house": 6},
            {"body": "Venus", "sign": "libra", "degree": 15.0, "longitude": 195.0, "house": 7},
            {"body": "Mars", "sign": "scorpio", "degree": 20.0, "longitude": 230.0, "house": 8},
            {"body": "Saturn", "sign": "aquarius", "degree": 5.0, "longitude": 305.0, "house": 11},
        ],
        houses={
            "1": {"sign": "aries", "degree": 10.0, "longitude": 10.0},
            "4": {"sign": "cancer", "degree": 20.0, "longitude": 110.0},
            "7": {"sign": "libra", "degree": 10.0, "longitude": 190.0},
            "10": {"sign": "capricorn", "degree": 20.0, "longitude": 290.0},
        },
        metadata={"aspects": []},
    )


def profile_natal_facts_payload():
    chart = _sample_chart()
    facts = build_natal_facts_from_chart(chart, mode="full")
    return {
        "surface": "Profile / natal_facts",
        "source": "birth data → Swiss Ephemeris (astro.py) → ChartResponse → build_natal_facts_from_chart",
        "llm_call": False,
        "payload": facts,
    }


def my_day_signal_payload():
    foundation = {
        "contract_version": "day_scenario_v1",
        "personal_natal_activations": [
            {
                "id": "act-1",
                "transiting_planet": "Saturn",
                "aspect": "square",
                "natal_point": "Moon",
                "orb_deg": 2.1,
                "strength": 0.8,
                "domain": "relationships",
                "text": "Saturn square Moon pressure on feelings",
            }
        ],
    }
    fusion = {
        "date": "2026-05-03",
        "scores": {},
        "cycle_context": {},
        "activity_context": {},
        "rhythm_context": {"goals": [], "habits": [], "ascetics": [], "diary": {"has_entry_today": False, "entries_last_7_days": 0}},
        "recommendations": [],
        "encouragement": "ok",
    }
    ctx = build_day_context_v0(
        target_date=date(2026, 5, 3),
        locale="ru",
        insight_depth_tier="free",
        core_profile=None,
        fusion_dump=fusion,
        daily_foundation=foundation,
    )
    return {
        "surface": "My Day / personal_day_signal",
        "source": "foundation.personal_natal_activations → today_domain_verdicts_v1.compute_domain_verdicts → select_personal_day_signal",
        "llm_call": False,
        "payload": ctx["layers"].get("personal_day_signal"),
    }


def today_primary_conflict_payload():
    pack = rank_day_events(
        [
            {
                "id": "moon-pisces",
                "kind": "moon_ingress",
                "title_ru": "Луна → Рыбы",
                "fact_ru": "Луна вошла в Рыбы — эмоции сильнее логики.",
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
            {
                "id": "venus-aspect",
                "kind": "aspect",
                "title_ru": "Венера аспект",
                "fact_ru": "Венера в мягком аспекте усиливает тему связей.",
                "priority_hint": "supporting",
            },
        ]
    )
    thesis = build_day_thesis_v1(day_events_pack=pack)
    interp = {"day_events_pack": pack, "day_thesis": thesis}
    pers = {
        "evidence_depth": "light_personalized",
        "sphere_selection": {
            "primary_candidates": ["relationships", "communication"],
            "allowed_spheres": ["relationships", "communication", "work_decisions"],
            "ranked_spheres": [
                {"sphere": "relationships", "score": 0.9, "reasons": ["head_topic"]},
                {"sphere": "communication", "score": 0.7, "reasons": ["driver"]},
            ],
        },
    }
    brief = build_day_dramaturgy_brief_c4(
        interpretation=interp,
        ritual_context={"tarot_name_ru": "Отшельник", "numerology_value": 7, "head_topic": "relationships"},
        personalization_pack=pers,
    )
    return {
        "surface": "Today / primary_conflict",
        "source": "rank_day_events → day_thesis_v1 → day_scenario_dramaturgy_brief_c4 (must_dramatize + primary_conflict)",
        "llm_call": False,
        "payload": {
            "must_dramatize": brief.get("must_dramatize"),
            "primary_conflict": brief.get("primary_conflict"),
            "scene_slots": brief.get("scene_slots"),
        },
    }


def ritual_practice_payload():
    rec = select_practice_for_ritual(
        ritual_context={"mood": "calm", "head_topic": "general", "tarot_name_ru": "Звезда", "numerology_value": 3},
        decision_engine={"hero": {"focus": "stabilize", "energy_label": "steady", "risk": "low"}},
    )
    return {
        "surface": "Ritual / practice_recommendation",
        "source": "ritual_context + decision_engine → build_ritual_practice_selection_context → rank_practice_selection_v1",
        "llm_call": False,
        "payload": rec,
    }


def evening_context_payload():
    foundation = {
        "contract_version": "day_scenario_v1",
        "spine": {
            "axis": "День про ясность в одном разговоре",
            "first_move": "Сформулировать позицию",
            "main_risk": "Согласиться слишком быстро",
        },
    }
    fusion = {
        "date": "2026-05-03",
        "scores": {},
        "cycle_context": {},
        "activity_context": {},
        "rhythm_context": {"goals": [], "habits": [], "ascetics": [], "diary": {"has_entry_today": False, "entries_last_7_days": 0}},
        "recommendations": [],
        "encouragement": "ok",
    }
    ctx = build_day_context_v0(
        target_date=date(2026, 5, 3),
        locale="ru",
        insight_depth_tier="free",
        core_profile=None,
        fusion_dump=fusion,
        daily_foundation=foundation,
    )
    return {
        "surface": "Evening / day_context layers",
        "source": "daily_foundation.spine + intent/day_model/guide_decision → evening_pack inherits same anchors",
        "llm_call": False,
        "payload": {
            "day_thesis": ctx["layers"].get("day_thesis"),
            "day_model": ctx["layers"].get("day_model"),
            "guide_decision": ctx["layers"].get("guide_decision"),
        },
    }


if __name__ == "__main__":
    results = [
        profile_natal_facts_payload(),
        my_day_signal_payload(),
        today_primary_conflict_payload(),
        ritual_practice_payload(),
        evening_context_payload(),
    ]
    print(json.dumps(results, ensure_ascii=False, indent=2))
