"""Anti double-influence: day_story LLM must not see card/number twice."""

from __future__ import annotations

from todayflow_backend.services.day_narrative_brief_v0 import (
    build_day_narrative_brief_v0,
    slim_day_engine_brief_for_story_llm,
)


def test_slim_strips_card_and_number_when_ritual_has_both():
    brief = build_day_narrative_brief_v0(
        foundation={"spine": {"day_axis": "Ось дня", "first_move": "Шаг"}},
        ritual={
            "tarot_main_id": "major_00",
            "tarot_name_ru": "Шут",
            "numerology_value": "7",
            "mood": "anxious",
            "head_topic": "работа",
        },
        fusion_scores={"energy": 45},
        intent_slice=None,
        locale="ru",
    )
    assert brief.get("thread_card")
    assert brief.get("thread_number")
    assert "карта" in (brief.get("anchor_summary") or "").lower()

    slim = slim_day_engine_brief_for_story_llm(
        brief, ritual_has_card=True, ritual_has_number=True
    )
    assert slim.get("thread_card") is None
    assert slim.get("thread_number") is None
    assert slim.get("symbol_source") == "ritual_context_only"
    anchor = (slim.get("anchor_summary") or "").lower()
    assert "карта дня" not in anchor
    assert "число дня" not in anchor
    assert "ось дня" in anchor or "шаг" in anchor or "настроение" in anchor


def test_slim_keeps_symbols_when_ritual_empty():
    brief = {
        "contract_version": "day_narrative_brief_v0",
        "anchor_summary": "Карта дня — Шут. Число дня — 7. Настроение тревожное.",
        "thread_card": "Шут",
        "thread_number": "7",
        "thread_mood": "тревожно",
    }
    slim = slim_day_engine_brief_for_story_llm(
        brief, ritual_has_card=False, ritual_has_number=False
    )
    assert slim.get("thread_card") == "Шут"
    assert slim.get("thread_number") == "7"
