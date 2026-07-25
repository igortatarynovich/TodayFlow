"""Runtime must not fill formula bank into user-facing day_story slots."""

from __future__ import annotations

from todayflow_backend.services.day_story_v1 import (
    INTERPRETATION_UNAVAILABLE_RU,
    build_day_story_fallback_v1,
)


def test_fallback_leaves_editorial_slots_empty():
    story = build_day_story_fallback_v1(
        day_engine_brief={
            "anchor_summary": "Сегодня — один ясный шаг.",
            "do_hint": "Выбери одну задачу",
            "avoid_hint": "Не подписывайся на новое",
            "tempo_hint": "Ровный темп",
            "thread_head_topic": "career",
        },
        ritual_context={"head_topic": "career"},
        fingerprint="fp-no-formula",
    )
    assert story.get("interpretation_status") == "unavailable"
    assert INTERPRETATION_UNAVAILABLE_RU in str(story.get("interpretation_unavailable_message") or "")
    assert not str(story.get("expect") or "").strip()
    assert not str(story.get("trap") or "").strip()
    assert not (story.get("do") or [])
    assert not (story.get("avoid") or [])
    # Engine brief hints must not become user prose on this path.
    assert "Выбери одну задачу" not in str(story.get("today_move") or "")
    assert "довериться потоку" not in str(story.get("story") or "").lower()
