"""DE-6: intent_slice_v0 — компактный слой намерения для DayContext."""

from __future__ import annotations

from todayflow_backend.services.intent_slice_v0 import build_intent_layer_v0


def test_build_intent_layer_v0_empty_returns_none():
    assert build_intent_layer_v0(
        morning_intention=None,
        morning_focus=None,
        head_topic=None,
    ) is None


def test_build_intent_layer_v0_contract_and_caps():
    out = build_intent_layer_v0(
        morning_intention="  Сделать отчёт  ",
        morning_focus="фокус",
        head_topic="работа",
        question_of_day_answer="да",
        quick_decision_answer="yes",
    )
    assert out is not None
    assert out["contract_version"] == "intent_slice_v0"
    assert "отчёт" in (out.get("morning_intention") or "")
    assert out.get("morning_focus") == "фокус"
    assert out.get("head_topic") == "работа"
    assert out.get("what_matters_line")
    assert "Цель" in out["what_matters_line"]
