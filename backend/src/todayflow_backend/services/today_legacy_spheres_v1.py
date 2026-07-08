"""Build legacy spheres input for today_contract assembler — parity with frontend `buildTodayFourAreas`."""

from __future__ import annotations

from typing import Any

from todayflow_backend.services.today_contract_fallbacks_v1 import (
    RELATIONSHIPS_OPPORTUNITY_FALLBACK,
    RELATIONSHIPS_RISK_FALLBACK,
    MONEY_WORK_OPPORTUNITY_FALLBACK,
    MONEY_WORK_RISK_FALLBACK,
    DEVELOPMENT_POINT_FALLBACK,
)


def _clean(raw: str | None) -> str:
    return (raw or "").strip()


def _pick_narrative(payload: dict[str, Any] | None, keys: tuple[str, ...]) -> str:
    if not payload:
        return ""
    for key in keys:
        v = payload.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def _pick_scenario(scenarios: list[Any] | None, slugs: tuple[str, ...]) -> dict[str, Any]:
    if not isinstance(scenarios, list):
        return {}
    for slug in slugs:
        for item in scenarios:
            if isinstance(item, dict) and str(item.get("slug") or "").lower() == slug:
                return item
    return {}


def _scenario_parts(scenario: dict[str, Any]) -> tuple[str, str]:
    if not scenario:
        return "", ""
    focus = _clean(scenario.get("focus") if isinstance(scenario.get("focus"), str) else None)
    summary = _clean(scenario.get("summary") if isinstance(scenario.get("summary"), str) else None)
    title = _clean(scenario.get("title") if isinstance(scenario.get("title"), str) else None)
    headline = focus or title
    detail = summary if summary and summary != focus else ""
    return headline, detail


def _clamp_score(value: float, default: int) -> int:
    if not isinstance(value, (int, float)) or not value:
        return default
    return min(96, max(28, round(value)))


def build_legacy_spheres_input(
    *,
    fusion: dict[str, Any] | None,
    morning_ritual: dict[str, Any] | None,
    spheres_narrative: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Minimal love/work/money/energy spheres for assembler source priority."""
    morning = morning_ritual or {}
    horoscope = morning.get("daily_horoscope") if isinstance(morning.get("daily_horoscope"), dict) else {}
    scenarios = horoscope.get("scenarios") if isinstance(horoscope.get("scenarios"), list) else []
    spine = horoscope.get("spine") if isinstance(horoscope.get("spine"), dict) else {}
    rec = morning.get("daily_recommendations") if isinstance(morning.get("daily_recommendations"), dict) else {}

    scores = fusion.get("scores") if isinstance(fusion, dict) and isinstance(fusion.get("scores"), dict) else {}
    energy_s = float(scores.get("energy") or 72)
    focus_s = float(scores.get("focus") or 68)
    balance_s = float(scores.get("emotional_balance") or 68)

    love_score = _clamp_score(min(100, energy_s + 4), 72)
    work_score = _clamp_score(focus_s * 0.7 + 25, 68)
    money_score = _clamp_score((energy_s + focus_s) / 2 + 8, 64)
    energy_score = _clamp_score((energy_s + balance_s + focus_s) / 3, 74)

    best_mode = _clean(spine.get("best_mode") if isinstance(spine.get("best_mode"), str) else None)
    first_move = _clean(spine.get("first_move") if isinstance(spine.get("first_move"), str) else None)
    what_to_avoid = _clean(rec.get("what_to_avoid") if isinstance(rec.get("what_to_avoid"), str) else None)

    love_sc = _scenario_parts(_pick_scenario(scenarios, ("love",)))
    work_sc = _scenario_parts(_pick_scenario(scenarios, ("career", "work")))
    money_sc = _scenario_parts(_pick_scenario(scenarios, ("money",)))

    narrative = spheres_narrative or {}

    return {
        "love": {
            "score": love_score,
            "todayHeadline": love_sc[0],
            "todayDetail": love_sc[1],
            "insight": _pick_narrative(narrative, ("love_insight", "relationships_insight"))
            or RELATIONSHIPS_OPPORTUNITY_FALLBACK,
            "watch": RELATIONSHIPS_RISK_FALLBACK,
            "reason": _pick_narrative(narrative, ("love_reason", "relationships_reason", "relationship_reason")),
        },
        "work": {
            "score": work_score,
            "todayHeadline": work_sc[0],
            "todayDetail": work_sc[1],
            "insight": _pick_narrative(narrative, ("work_insight", "career_insight", "purpose_insight"))
            or MONEY_WORK_OPPORTUNITY_FALLBACK,
            "watch": "Сложное лучше расписать или взять в один спокойный слот.",
            "reason": first_move or "Фокус на завершении одной рабочей линии.",
        },
        "money": {
            "score": money_score,
            "todayHeadline": money_sc[0],
            "todayDetail": money_sc[1],
            "insight": _pick_narrative(narrative, ("money_insight", "wealth_insight", "resource_insight"))
            or "Полезно отличить спешку от того, что правда нужно — и не кормить шум.",
            "watch": MONEY_WORK_RISK_FALLBACK,
            "reason": what_to_avoid or "Фокус на границах и импульсе в тратах.",
        },
        "energy": {
            "score": energy_score,
            "todayHeadline": best_mode or "Темп и ресурс",
            "todayDetail": "",
            "insight": best_mode or DEVELOPMENT_POINT_FALLBACK,
            "watch": "Сон, еда и вода — раньше новых обещаний кому-то.",
            "reason": _pick_narrative(narrative, ("energy_reason", "body_reason", "state_reason"))
            or "Энергия — про сон, нагрузку и эмоциональный фон.",
        },
    }
