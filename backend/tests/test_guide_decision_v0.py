from __future__ import annotations

from todayflow_backend.services.day_model_v0 import build_day_model_v0
from todayflow_backend.services.guide_decision_v0 import build_guide_decision_v0


def test_guide_decision_uses_ritual_and_day_model_not_empty_nouns():
    foundation = {
        "spine": {
            "day_axis": "День про завершение висящих линий, а не про новые обещания.",
            "first_move": "Закрой один блок, который уже открыт.",
            "main_risk": "Параллельные задачи без финиша.",
            "do_not_enter": "Не заходить в линию general если это хаос.",
        },
        "celestial_events": {"lunar_phase": {"name": "полнолуние"}},
    }
    ritual = {
        "tarot_name_ru": "Колесница",
        "numerology_value": "19",
        "mood": "устало",
        "head_topic": "тело",
    }
    dm = build_day_model_v0(
        foundation=foundation,
        ritual=ritual,
        fusion_scores={"energy": 55, "focus": 50, "emotional_balance": 50},
        intent_slice=None,
        internal_profile=None,
        locale="ru",
    )
    uc = {"baseline": {"rhythm_style": "склонность брать много и недоделывать"}}
    gd = build_guide_decision_v0(
        day_model=dm,
        ritual=ritual,
        foundation=foundation,
        user_core=uc,
        fusion_scores={"energy": 55},
        locale="ru",
    )
    assert gd["contract_version"] == "guide_decision_v0"
    hl = gd["headline"]
    assert "Колесница" in hl or "число" in hl or "заверш" in hl.lower()
    assert "смысл и коммуникация" not in hl.lower()
    body = str(gd["core_message"]["body"])
    assert "Колесница" in body or "19" in body
    assert "полнолуние" in body.lower()
    assert "устал" in body.lower()
    assert "Где ты сломаешься" in body or "сломаешься" in body
    assert "general" not in body.lower()
    av = gd["avoid_items"]
    assert any("с нуля" in x.lower() or "обещан" in x.lower() for x in av)
