from __future__ import annotations

from todayflow_backend.services.day_narrative_brief_v0 import build_day_narrative_brief_v0


def test_day_narrative_brief_v0_ru_has_contract_and_bounded_anchor():
    b = build_day_narrative_brief_v0(
        foundation={"spine": {"day_axis": "Ось", "first_move": "Шаг", "do_not_enter": "Лишние обещания"}},
        ritual={"tarot_name_ru": "Сила", "numerology_value": "3", "mood": "усталость", "head_topic": "работа"},
        fusion_scores={"energy": 50},
        intent_slice={"what_matters_line": "Важно закрыть один тикет"},
        locale="ru",
    )
    assert b["contract_version"] == "day_narrative_brief_v0"
    assert isinstance(b["anchor_summary"], str) and len(b["anchor_summary"]) <= 520
    assert "Сила" in b["anchor_summary"] or "карта" in b["anchor_summary"].lower()
    assert b["do_hint"]
    assert b["avoid_hint"]
    assert b["tempo_hint"]


def test_day_narrative_brief_v0_localizes_mood_and_head_topic_slugs_ru():
    b = build_day_narrative_brief_v0(
        foundation={"spine": {"day_axis": "Ось"}},
        ritual={"tarot_name_ru": "Звезда", "numerology_value": "7", "mood": "tired", "head_topic": "body"},
        fusion_scores={"energy": 50},
        intent_slice=None,
        locale="ru",
    )
    s = b["anchor_summary"]
    assert "устало" in s
    assert "tired" not in s.lower()
    assert "тело и энергия" in s
    assert "body" not in s.lower()


def test_day_narrative_brief_v0_en_uses_latin_anchor():
    b = build_day_narrative_brief_v0(
        foundation={"spine": {"day_axis": "Hold one thread", "first_move": "Send the note"}},
        ritual=None,
        fusion_scores={"energy": 30},
        intent_slice=None,
        locale="en-US",
    )
    anchor = b["anchor_summary"]
    assert any(c.isalpha() and ord(c) < 128 for c in anchor)
    assert len(anchor) <= 520
    assert b["energy_score_hint"] == 30
