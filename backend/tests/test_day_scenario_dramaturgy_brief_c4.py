"""Phase C4 — dramaturgy brief builder + protected user-message format."""

from __future__ import annotations

from todayflow_backend.services.day_events_ranker_v1 import rank_day_events
from todayflow_backend.services.day_scenario_dramaturgy_brief_c4 import (
    CONTRACT_VERSION,
    build_day_dramaturgy_brief_c4,
    format_native_user_message_c4,
    slim_interpretation_for_native_llm,
)
from todayflow_backend.services.day_scenario_native_llm_c1 import NATIVE_PROMPT_VERSION
from todayflow_backend.services.day_thesis_v1 import build_day_thesis_v1


def _pack():
    return rank_day_events(
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


def test_brief_must_dramatize_from_ranked_drivers():
    pack = _pack()
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
    assert brief["contract_version"] == CONTRACT_VERSION
    assert brief["pipeline"].startswith("facts→brief")
    ids = [r["id"] for r in brief["must_dramatize"]]
    assert "moon-pisces" in ids
    assert "merc-direct" in ids
    assert brief["act_iii_registry_label"]["role"] == "registry_seed_only_not_plot"
    assert brief["act_iii_registry_label"]["label_ru"]
    assert brief["scene_slots"][0]["sphere"] == "relationships"
    assert brief["scene_slots"][0]["dramatize_from_driver_id"] == brief["must_dramatize"][0]["id"]
    assert brief["scene_slots"][0]["dramatize_from_driver_id"] in ids


def test_slim_interpretation_demotes_thesis_and_pack():
    pack = _pack()
    thesis = build_day_thesis_v1(day_events_pack=pack)
    interp = {
        "day_events_pack": pack,
        "day_thesis": thesis,
        "day_personal": {"huge": "x" * 5000},
    }
    brief = build_day_dramaturgy_brief_c4(interpretation=interp)
    slim = slim_interpretation_for_native_llm(interp, brief=brief)
    assert "day_personal" not in slim
    assert slim["day_thesis"]["role"] == "see_dramaturgy_brief.act_iii_registry_label"
    assert slim["day_events_pack"]["contract_version"] == "day_events_pack_v1_slim_c4"
    assert "moon-pisces" in slim["day_events_pack"]["ranked_drivers"]


def test_format_protects_brief_under_truncation():
    brief = {
        "contract_version": CONTRACT_VERSION,
        "must_dramatize": [{"id": "moon-pisces", "fact_ru": "Луна вошла в Рыбы."}],
        "act_iii_registry_label": {"label_ru": "Прямота без фильтра", "role": "registry_seed_only_not_plot"},
    }
    context = {"interpretation": {"noise": "Y" * 20000}, "personalization_evidence": {"x": 1}}
    full, sent = format_native_user_message_c4(brief=brief, context=context, max_chars=2500)
    assert "DRAMATURGY_BRIEF" in sent
    assert "moon-pisces" in sent
    assert "Прямота без фильтра" in sent
    assert "registry_seed_only_not_plot" in sent
    assert len(sent) <= 2500
    assert len(full) > len(sent)


def test_native_prompt_version_c4():
    assert NATIVE_PROMPT_VERSION == "day-scenario-native-c5.5"


def test_format_prepends_il4_meaning_block():
    brief = {
        "contract_version": CONTRACT_VERSION,
        "must_dramatize": [{"id": "moon-pisces", "fact_ru": "Луна вошла в Рыбы."}],
    }
    meaning = "=== IL4_MEANING (protected) ===\nlemma: attract · value\n"
    _full, sent = format_native_user_message_c4(
        brief=brief,
        context={"x": 1},
        max_chars=8000,
        meaning_block=meaning,
    )
    assert sent.startswith("=== IL4_MEANING")
    assert sent.index("IL4_MEANING") < sent.index("DRAMATURGY_BRIEF")
