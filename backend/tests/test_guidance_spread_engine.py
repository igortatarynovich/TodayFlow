"""Guidance spread session assembly (structure, question checks, strict card count on API)."""

from __future__ import annotations

from todayflow_backend.core import models as core_models
from todayflow_backend.services.guidance_spread_engine import (
    CLARIFICATION_GOALS,
    GUIDANCE_SPREAD_GOALS,
    assess_guidance_question,
    build_spread_schema,
    compose_guidance_clarification,
    compose_guidance_reading,
    position_weight,
    structural_spread_analysis,
)


def _sample_cards() -> list[core_models.TarotSpreadCard]:
    pos_a = core_models.TarotSpreadPosition(id="risk", title="Где риск", prompt="Риск?")
    pos_b = core_models.TarotSpreadPosition(id="best_action", title="Шаг", prompt="Шаг?")
    card_a = core_models.TarotCard(
        id=16,
        name="Башня",
        keywords=["обрыв", "ясность"],
        upright="u",
        reversed="r",
        correspondences={},
    )
    card_b = core_models.TarotCard(
        id=2,
        name="Жрица",
        keywords=["пауза"],
        upright="u2",
        reversed="r2",
        correspondences={},
    )
    return [
        core_models.TarotSpreadCard(position=pos_a, card=card_a, orientation="upright", meaning="m1"),
        core_models.TarotSpreadCard(position=pos_b, card=card_b, orientation="reversed", meaning="m2"),
    ]


def test_position_weight_prefers_risk_slots() -> None:
    assert position_weight("main_risk") > position_weight("present_line")


def test_assess_flags_fortune_telling_ru() -> None:
    out = assess_guidance_question("он вернётся ко мне?", memory_context=None, locale="ru")
    assert out["flags"]["fortune_telling_tone"] is True
    assert out.get("suggestion")


def test_structural_analysis_has_dominant() -> None:
    cards = _sample_cards()
    st = structural_spread_analysis(cards, locale="ru")
    assert st["dominant_card_name"] == "Башня"
    assert st["dominant_position_id"] == "risk"
    assert st["conflict_note"]


def test_compose_single_action_and_avoid() -> None:
    cards = _sample_cards()
    st = structural_spread_analysis(cards, locale="ru")
    assess = assess_guidance_question("что мне важно понять в этой ситуации сейчас?", memory_context=None, locale="ru")
    base = {
        "clarity": "x",
        "explanation": "y",
        "forecast": "z",
        "decision": "d",
        "today": "Сделай один маленький проверяемый шаг сегодня.",
    }
    remapped, interpretation = compose_guidance_reading(
        question="что мне важно понять в этой ситуации сейчас?",
        spread_id="guidance_relationship_five",
        spread_title="Отношения",
        cards=cards,
        lane="love",
        base_answer=base,
        core_profile=None,
        topic="relationships",
        user_intent="understand_situation",
        requested_depth="normal",
        question_assessment=assess,
        structural=st,
        learning_context=None,
        today_context=None,
        locale="ru",
    )
    assert remapped["today"] == interpretation["action"]
    assert interpretation["avoid"].lower().startswith("не делай")
    assert "опора вывода" in interpretation["why_outline"].lower() or "опора" in interpretation["why_outline"].lower()


def test_spread_schema_weights() -> None:
    cards = _sample_cards()
    schema = build_spread_schema("t", "T", cards)
    assert len(schema["positions"]) == 2
    assert schema["positions"][0]["id"] == "risk"
    assert schema["positions"][0]["weight"] == round(position_weight("risk"), 3)


def test_guidance_goals_frozen() -> None:
    assert "choose_action" in GUIDANCE_SPREAD_GOALS


def test_compose_guidance_clarification_single_action() -> None:
    cards = _sample_cards()[:1]
    remapped, interpretation = compose_guidance_clarification(
        parent_question="Что делать?",
        parent_summary="Был узел выбора.",
        clarification_goal="next_step",
        spread_title="Одна карта",
        cards=cards,
        lane="decision",
        base_answer={
            "clarity": "a",
            "explanation": "b",
            "forecast": "c",
            "decision": "Сравни два варианта по одному факту.",
            "today": "Запиши один следующий шаг.",
        },
        core_profile=None,
        topic=None,
        learning_context=None,
        locale="ru",
    )
    assert remapped["today"] == interpretation["action"]
    assert "уточнение" in interpretation["continue_hint"].lower()
    assert "next_step" in CLARIFICATION_GOALS
