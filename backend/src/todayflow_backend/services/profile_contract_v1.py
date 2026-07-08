"""Profile Contract v1 — single editorial portrait for Profile (canonical artifact).

One LLM call (or deterministic fallback) → identity, strengths, styles, living patterns.
Backward compat: maps to legacy `interpretation` + `daily_interpretation`.

Canon: SCREEN_CONTRACTS_V1 §4 · PROFILE_SCREEN_MASTER · PIM via generation_logs.
"""

from __future__ import annotations

import json
import re
from typing import Any

from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_plain,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_default_chat_model,
    resolve_max_tokens,
)

PROFILE_CONTRACT_V1 = "profile_contract_v1"
PROFILE_CONTRACT_PROMPT_VER = "profile-contract-v1"

_PROFILE_SYS_RU = """Ты пишешь **единый портрет человека** для TodayFlow (русский язык).

Вход — JSON с ядром профиля: имя, знак, нумерология, baseline, living (сигналы, инсайты).

Задача: **одна связная карта личности** — без штампов, без «вселенная/поток», без паспорта знака как единственного смысла.

Поля (каждое — свой ракурс, без дословных повторов):
- identity_core — 2–3 предложения: кто этот человек в жизни, не только знак
- strengths — ≥3 конкретных сильных сторон (короткие фразы)
- growth_zones — ≥3 зон внимания (не stigma, без морали)
- relationship_style — как строит близость, границы, конфликт
- money_style — отношение к деньгам, риск, ценность
- decision_style — как выбирает, что тормозит, что ускоряет
- recurring_patterns — ≥1 повторяющийся паттерн из living/signals (или честная нейтральная формулировка если данных мало)
- living_changes — что меняется сейчас (1–2 предложения) или null если активности мало

Верни только JSON:
{
  "identity_core": "string",
  "strengths": ["string","string","string"],
  "growth_zones": ["string","string","string"],
  "relationship_style": "string",
  "money_style": "string",
  "decision_style": "string",
  "recurring_patterns": ["string"],
  "living_changes": "string|null"
}
"""


def _clip(text: str, limit: int) -> str:
    t = re.sub(r"\s+", " ", str(text or "").strip())
    if len(t) <= limit:
        return t
    return t[: limit - 1].rstrip() + "…"


def _parse_json_content(raw: str) -> dict[str, Any] | None:
    text = (raw or "").strip()
    if not text:
        return None
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


def validate_profile_contract_v1(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("contract_version") != PROFILE_CONTRACT_V1:
        errors.append("invalid contract_version")
    if not str(payload.get("identity_core") or "").strip():
        errors.append("identity_core empty")
    for key in ("strengths", "growth_zones", "recurring_patterns"):
        items = payload.get(key)
        if not isinstance(items, list) or len(items) < 1:
            errors.append(f"{key} must be non-empty list")
    for key in ("relationship_style", "money_style", "decision_style"):
        if not str(payload.get(key) or "").strip():
            errors.append(f"{key} empty")
    return errors


def _normalize_profile_contract(raw: dict[str, Any], *, profile_snapshot_version: str = "") -> dict[str, Any]:
    strengths = raw.get("strengths") if isinstance(raw.get("strengths"), list) else []
    growth = raw.get("growth_zones") if isinstance(raw.get("growth_zones"), list) else []
    patterns = raw.get("recurring_patterns") if isinstance(raw.get("recurring_patterns"), list) else []
    living_changes = raw.get("living_changes")
    if living_changes is not None:
        living_changes = _clip(str(living_changes), 480) or None

    return {
        "contract_version": PROFILE_CONTRACT_V1,
        "identity_core": _clip(raw.get("identity_core"), 720),
        "strengths": [_clip(str(x), 200) for x in strengths if str(x).strip()][:6],
        "growth_zones": [_clip(str(x), 200) for x in growth if str(x).strip()][:6],
        "relationship_style": _clip(raw.get("relationship_style"), 520),
        "money_style": _clip(raw.get("money_style"), 520),
        "decision_style": _clip(raw.get("decision_style"), 520),
        "recurring_patterns": [_clip(str(x), 240) for x in patterns if str(x).strip()][:4],
        "living_changes": living_changes,
        "profile_snapshot_version": profile_snapshot_version or PROFILE_CONTRACT_PROMPT_VER,
    }


def enrich_profile_contract_living(
    contract: dict[str, Any],
    *,
    living: dict[str, Any] | None,
) -> dict[str, Any]:
    """Deterministic fill for recurring_patterns / living_changes from living context."""
    out = dict(contract)
    live = living if isinstance(living, dict) else {}
    summary = str(live.get("summary") or "").strip()
    signal = live.get("signal_profile") if isinstance(live.get("signal_profile"), dict) else {}
    weekly = live.get("weekly_state") if isinstance(live.get("weekly_state"), dict) else {}
    insights = live.get("recent_insights") if isinstance(live.get("recent_insights"), list) else []

    patterns = out.get("recurring_patterns") if isinstance(out.get("recurring_patterns"), list) else []
    if not patterns:
        hints: list[str] = []
        dom_focus = weekly.get("dominant_question_focus")
        if dom_focus:
            hints.append(_clip(f"Часто возвращается тема: {dom_focus}", 240))
        yes_days = int(weekly.get("ritual_feedback_yes_days") or 0)
        no_days = int(weekly.get("ritual_feedback_no_days") or 0)
        if yes_days >= 2:
            hints.append("Ритуал дня чаще закрывается с ощущением «получилось».")
        elif no_days >= 2:
            hints.append("Несколько дней подряд день закрывается с ощущением «не дотянул» — стоит смягчить план.")
        if not hints and summary:
            hints.append(_clip(summary.split(".")[0], 240))
        if not hints:
            hints.append("Пока мало данных — паттерны проявятся после нескольких дней в приложении.")
        out["recurring_patterns"] = hints[:3]

    if not out.get("living_changes"):
        parts: list[str] = []
        if weekly.get("integration_text"):
            parts.append(_clip(str(weekly["integration_text"]), 320))
        elif insights:
            first = insights[0] if isinstance(insights[0], dict) else {}
            if first.get("text"):
                parts.append(_clip(str(first["text"]), 320))
        elif summary:
            parts.append(_clip(summary, 320))
        if parts:
            out["living_changes"] = parts[0]
    return out


def profile_contract_to_legacy_interpretation(contract: dict[str, Any]) -> dict[str, Any]:
    """Map profile_contract_v1 → legacy interpretation shape for Today/clients."""
    strengths = contract.get("strengths") if isinstance(contract.get("strengths"), list) else []
    growth = contract.get("growth_zones") if isinstance(contract.get("growth_zones"), list) else []
    return {
        "identity": contract.get("identity_core") or "",
        "strengths": strengths,
        "watchouts": growth,
        "life_areas": {
            "love": contract.get("relationship_style") or "",
            "career": contract.get("decision_style") or "",
            "money": contract.get("money_style") or "",
            "family": contract.get("relationship_style") or "",
            "decisions": contract.get("decision_style") or "",
        },
    }


def profile_contract_to_daily_interpretation(contract: dict[str, Any]) -> dict[str, Any]:
    identity = str(contract.get("identity_core") or "")
    rel = str(contract.get("relationship_style") or "")
    money = str(contract.get("money_style") or "")
    decision = str(contract.get("decision_style") or "")
    return {
        "daily_lenses": {
            "general": _clip(identity, 360),
            "love": _clip(rel, 300),
            "family": _clip(rel, 300),
            "career": _clip(decision, 300),
            "money": _clip(money, 300),
        }
    }


def profile_contract_from_legacy_interpretation(
    interpretation: dict[str, Any] | None,
    *,
    living: dict[str, Any] | None = None,
    profile_snapshot_version: str = "legacy-map",
) -> dict[str, Any]:
    """Derive contract from old snapshot interpretation (no LLM)."""
    interp = interpretation if isinstance(interpretation, dict) else {}
    la = interp.get("life_areas") if isinstance(interp.get("life_areas"), dict) else {}
    strengths = interp.get("strengths") if isinstance(interp.get("strengths"), list) else []
    watchouts = interp.get("watchouts") if isinstance(interp.get("watchouts"), list) else []
    raw = {
        "identity_core": interp.get("identity") or "",
        "strengths": strengths or ["Устойчивость", "Внимание к деталям", "Способность доводить начатое"],
        "growth_zones": watchouts or ["Распыление", "Импульсивные решения", "Уход от прямого разговора"],
        "relationship_style": la.get("love") or "",
        "money_style": la.get("money") or "",
        "decision_style": la.get("decisions") or la.get("career") or "",
        "recurring_patterns": [],
        "living_changes": None,
    }
    contract = _normalize_profile_contract(raw, profile_snapshot_version=profile_snapshot_version)
    return enrich_profile_contract_living(contract, living=living)


def build_profile_contract_fallback_v1(
    profile_input: dict[str, Any],
    *,
    living: dict[str, Any] | None = None,
) -> dict[str, Any]:
    baseline = profile_input.get("baseline") if isinstance(profile_input.get("baseline"), dict) else {}
    astro = profile_input.get("astro") if isinstance(profile_input.get("astro"), dict) else {}
    person = profile_input.get("person") if isinstance(profile_input.get("person"), dict) else {}
    name = str(person.get("display_name") or person.get("first_name") or "Вы").strip()
    sign = str(astro.get("sun_sign") or astro.get("label") or "ваш знак").strip()
    archetype = str(baseline.get("archetype") or "свой ритм").strip()
    raw = {
        "identity_core": (
            f"{name}, у вас свой устойчивый ритм ({archetype}). "
            f"Знак {sign} задаёт тон, но важнее то, как вы распределяете внимание в реальной жизни."
        ),
        "strengths": [
            "Способность держать линию, когда появляется ясный приоритет",
            "Внимание к людям и контексту",
            "Умение замечать, что реально работает",
        ],
        "growth_zones": [
            "Распыление на второй приоритет без времени",
            "Уход в контроль, когда темп ускоряется",
            "Откладывание прямого разговора",
        ],
        "relationship_style": "Близость строите через честность и предсказуемость — важно не угадывать, а говорить прямо.",
        "money_style": "Деньги для вас — про ценность и спокойствие: лучше один ясный шаг, чем импульсивное обещание.",
        "decision_style": "Решения созревают, когда есть факт и один критерий — тормозит лишний шум, ускоряет конкретный дедлайн.",
        "recurring_patterns": [],
        "living_changes": None,
    }
    contract = _normalize_profile_contract(raw)
    return enrich_profile_contract_living(contract, living=living)


def call_profile_contract_llm_v1(user_json: dict[str, Any], *, locale: str = "ru") -> dict[str, Any] | None:
    if not is_llm_chat_configured():
        return None
    client = get_openai_compatible_client()
    if client is None:
        return None
    system = _PROFILE_SYS_RU if locale.lower().startswith("ru") else _PROFILE_SYS_RU
    content = chat_completion_plain(
        client,
        model=resolve_default_chat_model(),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user_json, ensure_ascii=False)[:10000]},
        ],
        temperature=0.48,
        max_tokens=resolve_max_tokens(1600),
    )
    if not content:
        return None
    parsed = _parse_json_content(content)
    if not parsed:
        return None
    return _normalize_profile_contract(parsed)


def build_profile_portrait_v1(
    *,
    profile_input: dict[str, Any],
    living: dict[str, Any] | None,
    locale: str = "ru",
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], bool]:
    """
    Returns (profile_contract_v1, interpretation, daily_interpretation, used_fallback).
    Single artifact path with legacy shim.
    """
    llm_pack = {
        "person": profile_input.get("person"),
        "astro": profile_input.get("astro"),
        "numerology": profile_input.get("numerology"),
        "baseline": profile_input.get("baseline"),
        "living": living,
        "locale": locale,
    }
    contract = call_profile_contract_llm_v1(llm_pack, locale=locale)
    used_fallback = contract is None
    if contract is None:
        contract = build_profile_contract_fallback_v1(profile_input, living=living)
    else:
        contract = enrich_profile_contract_living(contract, living=living)
        if validate_profile_contract_v1(contract):
            contract = build_profile_contract_fallback_v1(profile_input, living=living)
            used_fallback = True

    interpretation = profile_contract_to_legacy_interpretation(contract)
    daily = profile_contract_to_daily_interpretation(contract)
    return contract, interpretation, daily, used_fallback
