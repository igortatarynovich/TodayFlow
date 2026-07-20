"""Surface disclosure funnel — multi-step without live LLM."""

from __future__ import annotations

from typing import Any

from todayflow_backend.core.config import settings
from todayflow_backend.services.surface_disclosure_funnel_v0 import (
    DAY_LAYER_PERSONALIZE_CONTRACT,
    SPHERES_MAP_CONTRACT,
    run_surface_disclosure_funnel_v0,
)


def _fake_openai_factory(responses: list[dict[str, Any]]):
    calls: list[tuple[str, str]] = []

    def _fn(system: str, user: str, *, depth_level: str = "normal") -> dict[str, Any] | None:
        calls.append((system[:40], user[:40]))
        if not responses:
            return None
        return responses.pop(0)

    return _fn, calls


def test_day_layer_funnel_two_steps(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_quality_mode", "rich")
    step1 = {
        "contract_version": DAY_LAYER_PERSONALIZE_CONTRACT,
        "what_lands": "Сегодня важно не разгонять второй приоритет без времени.",
        "soft_edge": "Риск — взять ещё одну задачу «на автомате».",
        "micro_move": "Перед согласием назвать срок вслух.",
        "life_now_angle": "Неделя про ясный один фокус.",
        "question_tone": "Как сейчас с ресурсом на лишние обещания?",
        "avoid_echo_of_guide": "Не копировать headline с Главного.",
    }
    step2 = {
        "nudge_message": "Перед новым «да» назови срок — иначе день расползётся.",
        "nudge_cta_label": "Один шаг",
        "personal_insight_title": "Лишний шаг сегодня",
        "personal_insight_body": "Тезис дня про ясный фокус. Лишний запрос легко съест ресурс, если не назвать границу.",
        "personal_insight_chips": ["граница", "срок"],
        "mini_decision_caption": "Ещё одно обещание без слота в календаре.",
        "question_of_day_prompt": "Где сегодня легче сказать «не сейчас»?",
        "life_now_weekly": "Неделя держится на одном главном.",
        "life_now_discipline": "Дисциплина — в коротком «нет» вовремя.",
    }
    fn, calls = _fake_openai_factory([step1, step2])
    payload, meta = run_surface_disclosure_funnel_v0(
        "day_layer",
        fn,
        locale_value="ru",
        depth_norm="normal",
        user_pack={"prior_thesis": "Ясный фокус", "user_core": {}},
    )
    assert meta["failed"] is False
    assert len(calls) == 2
    assert payload is not None
    assert payload["nudge_message"].startswith("Перед новым")
    assert "disclosure_step1" not in payload


def test_spheres_funnel_shape(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_quality_mode", "rich")
    step1 = {
        "contract_version": SPHERES_MAP_CONTRACT,
        "day_thread": "День про прямой разговор и один фокус.",
        "spheres": {
            "love": {"stance": "up", "angle": "Сказать прямо, не угадывать.", "rhythm_hook": None},
            "family": {"stance": "neutral", "angle": "Короткий check-in без разбора.", "rhythm_hook": None},
            "career": {"stance": "up", "angle": "Один приоритет в списке.", "rhythm_hook": "цель недели"},
            "money": {"stance": "down", "angle": "Не обещать трату импульсом.", "rhythm_hook": None},
        },
    }
    step2 = {
        "page_intro": "Сферы продолжают тезис дня — один фокус и прямые слова.",
        "thesis_reminder": "Не плодить второй приоритет.",
        "scenario_tie_ins": {
            "love": "Скажи прямо, чего ждёшь сегодня.",
            "family": "Короткий check-in без разбора дня.",
            "career": "Оставь в списке один главный блок.",
            "money": "Любую трату отложи на вечерний просмотр.",
        },
    }
    fn, _ = _fake_openai_factory([step1, step2])
    payload, meta = run_surface_disclosure_funnel_v0(
        "spheres",
        fn,
        locale_value="ru",
        depth_norm="normal",
        user_pack={"prior_thesis": "фокус"},
    )
    assert meta["failed"] is False
    assert payload["scenario_tie_ins"]["career"]


def test_economize_skips_funnel(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_quality_mode", "economize")
    fn, calls = _fake_openai_factory([{"x": 1}])
    payload, meta = run_surface_disclosure_funnel_v0(
        "evening",
        fn,
        locale_value="ru",
        depth_norm="normal",
        user_pack={},
    )
    assert payload is None
    assert meta.get("reason") == "quality_mode_economize"
    assert calls == []
