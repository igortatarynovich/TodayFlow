from __future__ import annotations

from typing import Any

import json

from todayflow_backend.services.guide_narrative_funnel_v0 import (
    CORE_CONTRACT,
    INTERP_CONTRACT,
    SATELLITES_CONTRACT,
    run_guide_narrative_funnel_v0,
)


def _interp_ok() -> dict[str, Any]:
    return {
        "contract_version": INTERP_CONTRACT,
        "what_happens": "Сегодня день толкает вперёд по стержню, а символы усиливают темп.",
        "where_conflict": "Натяжение между импульсом действовать и ограниченным ресурсом тела.",
        "where_you_break": "Ты откроешь много задач и начнёшь переключаться без завершения.",
        "what_works": "Одна начатая задача доведена до конца без переключений.",
        "one_concrete_move": "Выбери одну начатую задачу и закрой её за один заход.",
        "why_layers": [
            "Луна и стержень дня усиливают срочность и эмоциональный фон.",
            "Карта и число задают импульс движения и желание быстрого результата.",
            "Настроение и тема в голове сужают, какой риск для тебя реалистичен.",
        ],
        "avoid_hints": [
            "Не начинай новые задачи с нуля.",
            "Не отвечай сразу на все входящие.",
            "Не пытайся догнать день множеством стартов.",
        ],
    }


def _core_ok() -> dict[str, Any]:
    return {
        "contract_version": CORE_CONTRACT,
        "headline": "Один фокус на день без распыления по параллельным стартам.",
        "subline": "Стержень и символы ритуала просят завершить одну линию, а не открыть новые фронты.",
        "energy_line": "Ресурса хватает на один качественный блок внимания без героизма.",
        "focus_line": "Выбери одну начатую задачу и доведи её до конца.",
        "risk_line": "Распыление",
        "risk_detail": "Если потянуться за всем сразу, к вечеру будет ощущение «ничего не закрыто».",
        "core_message": {
            "body": "Сегодня легко уйти в срочное и потерять нить главного. Лучше выбрать одну задачу и довести её.",
            "risk": "Перегруз ответами «да» всем подряд.",
            "best_move": "Один завершённый шаг даст больше спокойствия, чем десять начатых.",
        },
        "do_items": [
            "Закрыть одну начатую задачу до конца",
            "Зафиксировать результат в Flow или дневнике",
            "Сделать паузу перед следующим входящим",
        ],
        "avoid_items": [
            "Не начинай новые задачи с нуля",
            "Не отвечай сразу на все входящие",
            "Не пытайся догнать день множеством стартов",
        ],
    }


def _sat_ok() -> dict[str, Any]:
    return {
        "contract_version": SATELLITES_CONTRACT,
        "header_disclaimer": "Здесь только ваш день по профилю и контексту. Совместимости — отдельный сервис.",
        "context_for_next_surfaces": "Тезис дня: сузиться и завершить одну линию. Сферы и углубление продолжают эту ось без нового приоритета.",
        "pattern_insight": "",
        "life_context_insight": "",
        "why_astrological_layers": [
            {"kind": "lunar_context", "anchor": "Полнолуние", "detail": "Усиливает эмоциональную срочность и реакции на входящие."},
            {"kind": "daily_spine", "anchor": "Стержень дня", "detail": "Просит завершения вместо распыления по параллельным стартам."},
            {"kind": "profile_prism", "anchor": "Ритм", "detail": "Твоему профилю проще держать фокус через один закрытый блок."},
        ],
        "action_options": [
            {"title": "Закрой одну начатую задачу до конца", "reason": "Снимает ощущение хаоса к середине дня."},
            {"title": "Отложи ответы на входящие на один слот", "reason": "Снижает переключения без потери контроля."},
            {"title": "Зафиксируй один результат в дневнике или Flow", "reason": "Закрепляет завершение как факт дня."},
        ],
        "sphere_triad": [
            {"area": "work", "stance": "up", "line": "Работа — лучшее окно, если не открывать пятый фронт параллельно."},
            {"area": "love", "stance": "down", "line": "Отношения — не разгоняй тяжёлые разговоры; коротко и по делу."},
            {"area": "money", "stance": "neutral", "line": "Деньги — без быстрых обязательств; проверь цифры один раз."},
        ],
        "support_hooks": ["Если есть цель в Flow — один шаг по ней сегодня.", "Или 5 минут тишины перед следующим входящим."],
    }


def test_run_guide_narrative_funnel_v0_success() -> None:
    calls: list[str] = []

    def fake_openai(system: str, user: str, *, depth_level: str = "normal") -> dict[str, Any] | None:
        calls.append(depth_level)
        if len(calls) == 1:
            return _interp_ok()
        if len(calls) == 2:
            return _core_ok()
        return _sat_ok()

    guide_user = {
        "ritual_context": {"tarot_name_ru": "Колесница", "numerology_value": "19", "mood": "устало"},
        "day_model": {"vector": {"summary": "движение"}},
        "day_engine_brief": {"contract_version": "day_narrative_brief_v0"},
        "guide_decision": {"contract_version": "guide_decision_v0", "headline": "x"},
        "daily_foundation": {"spine": {"day_axis": "тест"}},
        "user_core": {"living_summary": "склонен перегружаться"},
    }
    sat, interp, core, meta = run_guide_narrative_funnel_v0(
        fake_openai,
        locale_value="ru",
        tier_norm="free",
        depth_norm="normal",
        guide_user=guide_user,
        foundation={"spine": {"day_axis": "ось"}},
        fusion_for_prompt={"rhythm_context": {"goals": []}},
    )
    assert meta.get("failed") is False
    assert interp and interp.get("contract_version") == INTERP_CONTRACT
    assert core and core.get("contract_version") == CORE_CONTRACT
    assert sat and sat.get("funnel_contract")
    assert "action_options" in sat
    assert calls[0] == "quick"
    assert calls[1] == "normal"
    assert calls[2] == "normal"


def test_run_guide_narrative_funnel_v0_fails_step1() -> None:
    def bad(_s: str, _u: str, *, depth_level: str = "normal") -> dict[str, Any] | None:
        return {"contract_version": "wrong"}

    sat, interp, core, meta = run_guide_narrative_funnel_v0(
        bad,
        locale_value="ru",
        tier_norm="free",
        depth_norm="normal",
        guide_user={"user_core": {}},
        foundation=None,
        fusion_for_prompt={},
    )
    assert meta.get("failed") is True
    assert sat is None
    assert interp is None
    assert core is None


def test_run_guide_narrative_funnel_v0_step1_includes_day_history_slice() -> None:
    captured: list[str] = []

    def fake_openai(system: str, user: str, *, depth_level: str = "normal") -> dict[str, Any] | None:
        captured.append(user)
        n = len(captured)
        if n == 1:
            return _interp_ok()
        if n == 2:
            return _core_ok()
        return _sat_ok()

    day_history = {
        "contract_version": "day_history_v0",
        "yesterday": {
            "date": "2026-05-09",
            "meaning_active": True,
            "reflection_excerpt": {
                "contract_version": "day_connection_excerpt_v0",
                "evening_reflection": "Закрыл одну линию",
                "has_reflection": True,
            },
        },
        "fusion_score_delta_trustworthy": True,
        "fusion_score_delta_vs_yesterday": {"energy": 5, "emotional_balance": 0, "focus": 0},
    }
    guide_user = {
        "ritual_context": {"mood": "спокойное"},
        "day_model": {"temporal": {"summary": "Ресурс выше вчера"}},
        "day_history": day_history,
        "guide_decision": {"contract_version": "guide_decision_v0"},
        "user_core": {},
    }
    sat, _, _, meta = run_guide_narrative_funnel_v0(
        fake_openai,
        locale_value="ru",
        tier_norm="free",
        depth_norm="normal",
        guide_user=guide_user,
        foundation=None,
        fusion_for_prompt={},
    )
    assert meta.get("failed") is False
    assert sat is not None
    step1 = json.loads(captured[0])
    assert step1.get("day_history", {}).get("contract_version") == "day_history_funnel_slice_v0"
    assert step1.get("day_model_temporal", {}).get("summary")
    step3 = json.loads(captured[1])
    assert step3.get("funnel_interpretation", {}).get("contract_version") == INTERP_CONTRACT
    step2 = json.loads(captured[2])
    assert step2.get("funnel_core_text", {}).get("contract_version") == CORE_CONTRACT
    assert step2.get("guide_decision", {}).get("contract_version") == "guide_decision_v0"


def test_run_guide_narrative_funnel_v0_reuses_cached_interpretation() -> None:
    calls: list[str] = []

    def fake_openai(system: str, user: str, *, depth_level: str = "normal") -> dict[str, Any] | None:
        calls.append(depth_level)
        if len(calls) == 1:
            return _core_ok()
        return _sat_ok()

    sat, interp, core, meta = run_guide_narrative_funnel_v0(
        fake_openai,
        locale_value="ru",
        tier_norm="free",
        depth_norm="normal",
        guide_user={"guide_decision": {"contract_version": "guide_decision_v0"}, "user_core": {}},
        foundation=None,
        fusion_for_prompt={},
        cached_interpretation=_interp_ok(),
    )
    assert meta.get("failed") is False
    assert meta.get("step1_cache_hit") is True
    assert meta.get("step1_ms") == 0
    assert len(calls) == 2
    assert calls[0] == "normal"
    assert interp and interp.get("contract_version") == INTERP_CONTRACT
    assert core and core.get("contract_version") == CORE_CONTRACT
    assert sat and sat.get("funnel_contract")


def test_run_guide_narrative_funnel_v0_reuses_cached_core_text() -> None:
    calls: list[str] = []

    def fake_openai(system: str, user: str, *, depth_level: str = "normal") -> dict[str, Any] | None:
        calls.append(depth_level)
        if len(calls) == 1:
            return _interp_ok()
        return _sat_ok()

    sat, _, core, meta = run_guide_narrative_funnel_v0(
        fake_openai,
        locale_value="ru",
        tier_norm="free",
        depth_norm="normal",
        guide_user={"guide_decision": {"contract_version": "guide_decision_v0"}, "user_core": {}},
        foundation=None,
        fusion_for_prompt={},
        cached_core_text=_core_ok(),
    )
    assert meta.get("failed") is False
    assert meta.get("step3_cache_hit") is True
    assert meta.get("step3_ms") == 0
    assert len(calls) == 2
    assert core and core.get("contract_version") == CORE_CONTRACT
    assert sat and sat.get("funnel_contract")
