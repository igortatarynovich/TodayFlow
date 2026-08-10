"""InterpretationOrchestrator — do_focus must not leak element_focus catalog."""

from __future__ import annotations

from todayflow_backend.services.interpretation_orchestrator import InterpretationOrchestrator


def test_do_focus_not_seeded_from_element_focus_air():
    orch = InterpretationOrchestrator()
    out = orch.build_daily_guidance(
        core_profile={
            "baseline": {
                "element_focus": "Мышление и ясные формулировки",
                "rhythm_style": "Переключение без потери нити",
            },
            "numerology": {"life_path": 5},
        },
        numerology={"dayNumber": 3},
        needs=None,
    )
    do = str(out.get("do_focus") or "")
    assert "Мышление и ясные формулировки" not in do
    assert "мышление" not in do.lower()
    assert do  # still actionable
    assert out.get("focus") == "Переключение без потери нити"
    assert "baseline_element_focus" not in (out.get("rules_applied") or [])


def test_do_focus_default_without_profile():
    orch = InterpretationOrchestrator()
    out = orch.build_daily_guidance(core_profile=None, numerology=None, needs=None)
    assert out["do_focus"] == "Один короткий осознанный шаг"
