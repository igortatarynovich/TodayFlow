"""guide_narrative_funnel_v0 — узкая воронка LLM для surface=guide (DE-13 v0).

Шаг 1: причинный синтез слоёв (астро + символ ритуала + профиль/намерение) — без полного UI JSON.
Шаг 3 (v4): ядро текста (headline, core_message, do/avoid, сигналы) из interpretation + day_model.
Шаг 2: только «спутники» (action_options, sphere_triad, why_astrological_layers, …).

При сбое шага 3 ядро подставляет сервер из ``guide_decision_v0`` (fallback в ``today_narrative``).
При любом сбое воронки вызывающий код откатывается на монолитный промпт guide.
"""

from __future__ import annotations

import json
import logging
import re
from time import perf_counter
from typing import Any, Callable

from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_plain,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_default_chat_model,
)
from todayflow_backend.services.llm_quality_policy_v1 import (
    funnel_step_max_tokens,
    user_json_char_budget,
)

logger = logging.getLogger(__name__)

FUNNEL_CONTRACT = "guide_narrative_funnel_v0"
INTERP_CONTRACT = "guide_funnel_interpretation_v0"
CORE_CONTRACT = "guide_funnel_core_text_v0"
SATELLITES_CONTRACT = "guide_funnel_satellites_v0"
# Регистрация в prompt_versions (module совпадает с today_narrative)
FUNNEL_PROMPT_VER_STEP1 = "today-narrative-funnel-v0-step1-interp"
FUNNEL_PROMPT_VER_STEP3 = "today-narrative-funnel-v0-step3-core"
FUNNEL_PROMPT_VER_STEP2 = "today-narrative-funnel-v0-step2-satellites-v2"
FUNNEL_CHILD_CHAIN_CONTRACT = "guide_funnel_child_chain_v0"


def funnel_system_prompts_for_locale(locale: str) -> tuple[str, str, str]:
    if _is_en_locale(locale):
        return _SYS_INTERP_EN, _SYS_CORE_EN, _SYS_SAT_EN
    return _SYS_INTERP_RU, _SYS_CORE_RU, _SYS_SAT_RU


def _parse_json_content(content: str) -> dict[str, Any] | None:
    raw = (content or "").strip()
    if not raw:
        return None
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
    if m:
        raw = m.group(1).strip()
    try:
        obj = json.loads(raw)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        return None


def _is_en_locale(locale: str) -> bool:
    return (locale or "").strip().lower().startswith("en")


def _openai_json_funnel(
    system: str,
    user: str,
    *,
    depth_level: str,
) -> dict[str, Any] | None:
    if not is_llm_chat_configured():
        return None
    client = get_openai_compatible_client()
    if client is None:
        return None
    dl = (depth_level or "normal").strip().lower()
    if dl not in ("quick", "normal", "deep"):
        dl = "normal"
    temperature = 0.45 if dl == "quick" else (0.52 if dl == "deep" else 0.5)

    content = chat_completion_plain(
        client,
        model=resolve_default_chat_model(),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        max_tokens=funnel_step_max_tokens(dl),
    )
    if not content:
        return None
    return _parse_json_content(content)


_SYS_INTERP_RU = """Ты — шаг 1 воронки экрана «Главное» TodayFlow. Возвращай ТОЛЬКО один JSON без markdown.

Задача: связать в ОДНУ причинную картину три слоя из входного JSON:
(1) астрология/стержень дня — daily_foundation, day_model (в т.ч. temporal), day_engine_brief;
(2) символика ритуала — карта, число, настроение, head_topic;
(3) человек — visible_profile, intent, короткий user_core_excerpt;
(4) при наличии day_history — вчера/неделя и reflection_excerpt: одна мягкая нить «продолжение vs разрыв», без сырых баллов и без дословной цитаты вечернего текста.

Правила:
- Каждое текстовое поле — конкретика дня, не общие аффирмации. Запрещены пустые пары существительных («смысл и коммуникация», «пространство и контакт»).
- Обязательна причинность: «что усиливает день» vs «что в тебе/ресурсе даёт натяжение».
- why_layers: ровно 3 короткие строки — каждая явно опирается на разные входы (луна/стержень; карта+число; настроение или профиль).
- avoid_hints: 3 строки — запреты с глаголами (чего не делать сегодня), приземлённо.

Ответ строго по схеме:
{
  "contract_version": "guide_funnel_interpretation_v0",
  "what_happens": "string — 2–4 предложения: что за день по слоям",
  "where_conflict": "string — 1–3 предложения: главное натяжение",
  "where_you_break": "string — 2–3 предложения: где человек чаще ломается сегодня",
  "what_works": "string — 1–3 предложения: что реально сработает (не «будь собой»)",
  "one_concrete_move": "string — один выполнимый ход, глагол + объект",
  "why_layers": ["строка","строка","строка"],
  "avoid_hints": ["строка","строка","строка"]
}
"""

_SYS_INTERP_EN = """You are step 1 of the TodayFlow «Main» screen funnel. Return ONLY one JSON object, no markdown.

Task: merge three layers from the input JSON into ONE causal picture:
(1) astrology / day spine — daily_foundation, day_model (incl. temporal), day_engine_brief;
(2) ritual symbolism — card, number, mood, head_topic;
(3) the person — visible_profile, intent, short user_core_excerpt;
(4) when day_history is present — yesterday/week and reflection_excerpt: one soft continuity thread, no raw scores, no verbatim evening quote.

Rules:
- Every field must be specific to today; no empty noun-pair headlines.
- Include tension: what the day amplifies vs what bandwidth/patterns constrain.
- why_layers: exactly 3 short strings, each anchored in different inputs (moon/spine; card+number; mood or profile).
- avoid_hints: 3 lines — clear «do not» actions with verbs.

Schema:
{
  "contract_version": "guide_funnel_interpretation_v0",
  "what_happens": "string",
  "where_conflict": "string",
  "where_you_break": "string",
  "what_works": "string",
  "one_concrete_move": "string",
  "why_layers": ["string","string","string"],
  "avoid_hints": ["string","string","string"]
}
"""

_SYS_CORE_RU = """Ты — шаг 3 воронки «Главное» TodayFlow. Возвращай ТОЛЬКО один JSON без markdown.

Задача: развернуть funnel_interpretation в пользовательское **ядро экрана** — headline, subline, core_message, do/avoid, сигналы ресурса и риска.

На входе: funnel_interpretation (шаг 1), guide_decision (серверные якоря day_model — не противоречь оси дня), day_model, day_engine_brief, ritual_context.

Правила:
- Сохрани причинность interpretation: what_happens → where_conflict → where_you_break → what_works → one_concrete_move.
- headline — одна строка, ≥12 символов, без пустых пар существительных.
- subline — 1–2 предложения, конкретика дня.
- core_message — объект с обязательным body (2–4 предложения); опционально risk, best_move; без «энергий» и пустых лозунгов.
- do_items и avoid_items — ровно по 3 строки с глаголами; avoid согласуй с avoid_hints из interpretation.
- energy_line, focus_line, risk_line, risk_detail — коротко, бытовым языком, согласованы с day_model.risk/strategy если есть.
- Не возвращай action_options, sphere_triad, why_astrological_layers — их делает шаг 2.

Схема:
{
  "contract_version": "guide_funnel_core_text_v0",
  "headline": "string",
  "subline": "string",
  "energy_line": "string",
  "focus_line": "string",
  "risk_line": "string",
  "risk_detail": "string",
  "core_message": {"body": "string", "risk": "string", "best_move": "string"},
  "do_items": ["строка","строка","строка"],
  "avoid_items": ["строка","строка","строка"]
}
"""

_SYS_CORE_EN = """You are step 3 of the TodayFlow «Main» funnel. Return ONLY one JSON object, no markdown.

Task: expand funnel_interpretation into the screen **core** — headline, subline, core_message, do/avoid, energy/focus/risk lines.

Inputs: funnel_interpretation (step 1), guide_decision (server day_model anchors — do not contradict the day's axis), day_model, day_engine_brief, ritual_context.

Rules:
- Keep interpretation causality: what_happens → conflict → break pattern → what_works → one_concrete_move.
- headline: one line, ≥12 chars, no empty noun pairs.
- subline: 1–2 sentences, specific to today.
- core_message: object with required body; optional risk, best_move; plain language.
- do_items and avoid_items: exactly 3 strings each with verbs; avoid aligns with interpretation.avoid_hints.
- energy_line, focus_line, risk_line, risk_detail: short, grounded; align with day_model risk/strategy when present.
- Do NOT return action_options, sphere_triad, or why_astrological_layers — step 2 handles those.

Schema:
{
  "contract_version": "guide_funnel_core_text_v0",
  "headline": "string",
  "subline": "string",
  "energy_line": "string",
  "focus_line": "string",
  "risk_line": "string",
  "risk_detail": "string",
  "core_message": {"body": "string", "risk": "string", "best_move": "string"},
  "do_items": ["string","string","string"],
  "avoid_items": ["string","string","string"]
}
"""

_SYS_SAT_RU = """Ты — шаг 2 воронки «Главное» TodayFlow. Возвращай ТОЛЬКО один JSON без markdown.

На входе: funnel_interpretation (шаг 1), funnel_core_text (шаг 3 — ядро экрана), guide_decision (серверные якоря — не противоречь),
ritual_context, day_model, insight_depth_tier, user_core_excerpt, fusion.rhythm_context (если есть).

Сгенерируй только спутниковые поля. Ядро (headline, core_message и т.д.) уже в funnel_core_text — не дублируй и не возвращай их.

Правила:
- action_options: ровно 3 элемента; каждый — объект {title, reason?, estimated_minutes?, entity_kind?}; title — глагол + что сделать; согласуй с funnel_core_text.core_message / interpretation.one_concrete_move.
- sphere_triad: ровно 3 объекта, area по разу work, love, money; stance up|down|neutral; line — одна приземлённая строка с глаголом или чётким ориентиром.
- why_astrological_layers: 3–6 объектов {kind, anchor, detail}; kind из: natal_angle|natal_luminary|natal_personal|natal_aspect|daily_spine|lunar_context|profile_prism; разверни funnel_interpretation.why_layers в конкретные anchor+detail; не дублируй дословно headline из funnel_core_text.
- support_hooks: 1–2 строки; опирайся на rhythm_context (цели/привычки/дневник) — не выдумывай факты.
- context_for_next_surfaces: 4–8 предложений — единый тезис для вкладок «сферы» и углубления.
- header_disclaimer: как в текущем продукте — экран про личный день, не про совместимость.
- insight_depth_tier: если free — pattern_insight и life_context_insight пустые строки ""; если pro — pattern_insight 1–2 предложения, life_context ""; если premium — оба блока по 1–2 предложения.

Запрещены slug'и API (general, neutral как метка оси) в пользовательском тексте.

Схема ответа:
{
  "contract_version": "guide_funnel_satellites_v0",
  "header_disclaimer": "string",
  "context_for_next_surfaces": "string",
  "pattern_insight": "string",
  "life_context_insight": "string",
  "why_astrological_layers": [{"kind":"daily_spine","anchor":"…","detail":"…"}],
  "action_options": [{"title":"…","reason":"…"}],
  "sphere_triad": [{"area":"work","stance":"up","line":"…"}],
  "support_hooks": ["строка"]
}
"""

_SYS_SAT_EN = """You are step 2 of the TodayFlow «Main» funnel. Return ONLY one JSON object, no markdown.

Inputs: funnel_interpretation, funnel_core_text (step 3 core — already written), guide_decision (server anchors — do not contradict),
ritual_context, day_model, insight_depth_tier, user_core_excerpt, fusion.rhythm_context if present.

Generate ONLY satellite fields. Core fields live in funnel_core_text — do NOT return or duplicate them.

Rules:
- action_options: exactly 3 items; each {title, reason?, estimated_minutes?, entity_kind?}; align with funnel_core_text.core_message and interpretation.one_concrete_move.
- sphere_triad: exactly 3 objects, areas work, love, money each once; stance up|down|neutral; line is one concrete line with a verb or clear steer.
- why_astrological_layers: 3–6 {kind, anchor, detail}; kinds: natal_angle|natal_luminary|natal_personal|natal_aspect|daily_spine|lunar_context|profile_prism; expand interpretation.why_layers into concrete anchors.
- support_hooks: 1–2 strings from rhythm_context facts only.
- context_for_next_surfaces: 4–8 sentences — one thesis for spheres/deepen.
- header_disclaimer: this screen is about the user's personal day, not compatibility with others.
- Tier: free → pattern_insight and life_context_insight ""; pro → pattern filled; premium → both.

Schema:
{
  "contract_version": "guide_funnel_satellites_v0",
  "header_disclaimer": "string",
  "context_for_next_surfaces": "string",
  "pattern_insight": "string",
  "life_context_insight": "string",
  "why_astrological_layers": [{"kind":"daily_spine","anchor":"…","detail":"…"}],
  "action_options": [{"title":"…","reason":"…"}],
  "sphere_triad": [{"area":"work","stance":"up","line":"…"}],
  "support_hooks": ["string"]
}
"""


def _slim_foundation_for_funnel(foundation: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(foundation, dict):
        return {}
    spine = foundation.get("spine")
    ce = foundation.get("celestial_events")
    out: dict[str, Any] = {}
    if isinstance(spine, dict):
        out["spine"] = spine
    if isinstance(ce, dict):
        out["celestial_events"] = ce
    return out


def _user_core_excerpt(uc: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(uc, dict):
        return {}
    astro = uc.get("astro") if isinstance(uc.get("astro"), dict) else {}
    nc = uc.get("natal_chart") if isinstance(uc.get("natal_chart"), dict) else {}
    base = uc.get("baseline") if isinstance(uc.get("baseline"), dict) else {}
    return {
        "living_summary": (str(uc.get("living_summary") or "").strip()[:400]),
        "baseline_rhythm_style": (str(base.get("rhythm_style") or "").strip()[:320]),
        "sun_sign": (str(astro.get("sun_sign") or "").strip()[:40]),
        "natal_chart_available": bool(nc.get("available")),
    }


def _slim_day_history_for_funnel(h: dict[str, Any] | None) -> dict[str, Any] | None:
    """DE-13 v1: компактный temporal slice для шага 1 (не вся серия 7d)."""
    if not isinstance(h, dict) or h.get("contract_version") != "day_history_v0":
        return None
    y = h.get("yesterday")
    if not isinstance(y, dict):
        return None
    out: dict[str, Any] = {
        "contract_version": "day_history_funnel_slice_v0",
        "yesterday_date": y.get("date"),
        "fusion_score_delta_vs_yesterday": h.get("fusion_score_delta_vs_yesterday"),
        "fusion_score_delta_trustworthy": h.get("fusion_score_delta_trustworthy"),
        "meaning_active": y.get("meaning_active"),
        "meaning_completions_total": y.get("meaning_completions_total"),
        "reflection_excerpt": y.get("reflection_excerpt"),
    }
    if h.get("trailing_7d_summary_trustworthy") is not False:
        summ = h.get("trailing_7d_summary")
        if isinstance(summ, dict):
            out["trailing_7d_summary"] = summ
    return out


def _build_step1_user_json(guide_user: dict[str, Any], *, foundation: dict[str, Any] | None) -> str:
    dm = guide_user.get("day_model") if isinstance(guide_user.get("day_model"), dict) else {}
    temporal = dm.get("temporal") if isinstance(dm, dict) else None
    pack = {
        "contract_version": "guide_funnel_step1_input_v0",
        "ritual_context": guide_user.get("ritual_context"),
        "day_model": guide_user.get("day_model"),
        "day_model_temporal": temporal if isinstance(temporal, dict) else None,
        "day_history": _slim_day_history_for_funnel(
            guide_user.get("day_history") if isinstance(guide_user.get("day_history"), dict) else None
        ),
        "day_engine_brief": guide_user.get("day_engine_brief"),
        "guide_decision": guide_user.get("guide_decision"),
        "daily_foundation": _slim_foundation_for_funnel(
            guide_user.get("daily_foundation") if isinstance(guide_user.get("daily_foundation"), dict) else foundation
        ),
        "visible_profile": guide_user.get("visible_profile"),
        "intent": guide_user.get("intent"),
        "user_core_excerpt": _user_core_excerpt(guide_user.get("user_core") if isinstance(guide_user.get("user_core"), dict) else None),
    }
    return json.dumps(pack, ensure_ascii=False)[: user_json_char_budget()]


def _build_step3_user_json(
    guide_user: dict[str, Any],
    interpretation: dict[str, Any],
) -> str:
    pack = {
        "contract_version": "guide_funnel_step3_input_v0",
        "funnel_interpretation": interpretation,
        "guide_decision": guide_user.get("guide_decision"),
        "day_model": guide_user.get("day_model"),
        "day_engine_brief": guide_user.get("day_engine_brief"),
        "ritual_context": guide_user.get("ritual_context"),
        "intent": guide_user.get("intent"),
        "user_core_excerpt": _user_core_excerpt(
            guide_user.get("user_core") if isinstance(guide_user.get("user_core"), dict) else None
        ),
    }
    return json.dumps(pack, ensure_ascii=False)[: user_json_char_budget()]


def _build_step2_user_json(
    guide_user: dict[str, Any],
    interpretation: dict[str, Any],
    *,
    tier_norm: str,
    fusion_for_prompt: dict[str, Any],
    funnel_core: dict[str, Any] | None = None,
) -> str:
    rc = fusion_for_prompt.get("rhythm_context") if isinstance(fusion_for_prompt, dict) else {}
    pack = {
        "contract_version": "guide_funnel_step2_input_v0",
        "insight_depth_tier": tier_norm,
        "funnel_interpretation": interpretation,
        "funnel_core_text": funnel_core,
        "guide_decision": guide_user.get("guide_decision"),
        "ritual_context": guide_user.get("ritual_context"),
        "day_model": guide_user.get("day_model"),
        "day_history": _slim_day_history_for_funnel(
            guide_user.get("day_history") if isinstance(guide_user.get("day_history"), dict) else None
        ),
        "user_core_excerpt": _user_core_excerpt(guide_user.get("user_core") if isinstance(guide_user.get("user_core"), dict) else None),
        "fusion": {"rhythm_context": rc if isinstance(rc, dict) else {}},
    }
    return json.dumps(pack, ensure_ascii=False)[: user_json_char_budget()]


def _interpretation_ok(d: dict[str, Any] | None) -> bool:
    if not isinstance(d, dict):
        return False
    if str(d.get("contract_version") or "").strip() != INTERP_CONTRACT:
        return False
    for k in (
        "what_happens",
        "where_conflict",
        "where_you_break",
        "what_works",
        "one_concrete_move",
    ):
        if len(str(d.get(k) or "").strip()) < 12:
            return False
    wl = d.get("why_layers")
    if not isinstance(wl, list) or len(wl) < 3:
        return False
    if any(len(str(x or "").strip()) < 8 for x in wl[:3]):
        return False
    ah = d.get("avoid_hints")
    if not isinstance(ah, list) or len(ah) < 3:
        return False
    if any(len(str(x or "").strip()) < 6 for x in ah[:3]):
        return False
    return True


def _core_message_body_ok(cm: Any) -> bool:
    if isinstance(cm, dict):
        body = str(cm.get("body") or "").strip()
        return len(body) >= 12
    return len(str(cm or "").strip()) >= 12


def _core_text_ok(d: dict[str, Any] | None) -> bool:
    if not isinstance(d, dict):
        return False
    if str(d.get("contract_version") or "").strip() != CORE_CONTRACT:
        return False
    for k in ("subline", "energy_line", "focus_line", "risk_line", "risk_detail"):
        if len(str(d.get(k) or "").strip()) < 8:
            return False
    if len(str(d.get("headline") or "").strip()) < 12:
        return False
    if not _core_message_body_ok(d.get("core_message")):
        return False
    for key in ("do_items", "avoid_items"):
        rows = d.get(key)
        if not isinstance(rows, list) or len(rows) != 3:
            return False
        if any(len(str(x or "").strip()) < 6 for x in rows):
            return False
    return True


def _satellites_shape_ok(d: dict[str, Any] | None) -> bool:
    if not isinstance(d, dict):
        return False
    if str(d.get("contract_version") or "").strip() != SATELLITES_CONTRACT:
        return False
    for k in ("header_disclaimer", "context_for_next_surfaces"):
        if len(str(d.get(k) or "").strip()) < 16:
            return False
    why = d.get("why_astrological_layers")
    if not isinstance(why, list) or len(why) < 3:
        return False
    for item in why[:6]:
        if not isinstance(item, dict):
            return False
        if len(str(item.get("anchor") or "").strip()) < 2:
            return False
        if len(str(item.get("detail") or "").strip()) < 10:
            return False
    ao = d.get("action_options")
    if not isinstance(ao, list) or len(ao) != 3:
        return False
    for x in ao:
        title = ""
        if isinstance(x, dict):
            title = str(x.get("title") or x.get("label") or "").strip()
        else:
            title = str(x or "").strip()
        if len(title) < 6:
            return False
    st = d.get("sphere_triad")
    if not isinstance(st, list) or len(st) != 3:
        return False
    need = {"work", "love", "money"}
    seen: set[str] = set()
    for item in st:
        if not isinstance(item, dict):
            return False
        a = str(item.get("area") or "").strip().lower()
        stance = str(item.get("stance") or "").strip().lower()
        line = str(item.get("line") or "").strip()
        if a not in need or stance not in ("up", "down", "neutral") or len(line) < 8:
            return False
        seen.add(a)
    if seen != need:
        return False
    sh = d.get("support_hooks")
    if not isinstance(sh, list) or not any(str(x or "").strip() for x in sh):
        return False
    return True


def is_funnel_interpretation_valid(d: dict[str, Any] | None) -> bool:
    """DE-13 v2: публичная проверка для cache reuse step1."""
    return _interpretation_ok(d)


def is_funnel_satellites_valid(d: dict[str, Any] | None) -> bool:
    """DE-13 v2: публичная проверка для cache reuse step2."""
    return _satellites_shape_ok(d)


def is_funnel_core_text_valid(d: dict[str, Any] | None) -> bool:
    """DE-13 v4: публичная проверка для cache reuse step3."""
    return _core_text_ok(d)


def slim_funnel_interpretation_for_child(d: dict[str, Any] | None) -> dict[str, Any] | None:
    """DE-13 v3: урезанная interpretation для day_layer / spheres / evening / deepen."""
    if not _interpretation_ok(d):
        return None
    keys = (
        "contract_version",
        "what_happens",
        "where_conflict",
        "where_you_break",
        "what_works",
        "one_concrete_move",
        "why_layers",
        "avoid_hints",
    )
    return {k: d[k] for k in keys if k in d}


def run_guide_narrative_funnel_v0(
    openai_json: Callable[..., dict[str, Any] | None],
    *,
    locale_value: str,
    tier_norm: str,
    depth_norm: str,
    guide_user: dict[str, Any],
    foundation: dict[str, Any] | None,
    fusion_for_prompt: dict[str, Any],
    cached_interpretation: dict[str, Any] | None = None,
    cached_core_text: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None, dict[str, Any]]:
    """Возвращает (satellites_payload | None, interpretation | None, core | None, meta).

    meta: failed, step{1,2,3}_ms, step{1,3}_cache_hit, user_json_step{1,2,3}, system previews.
    """
    en = _is_en_locale(locale_value)
    sys1, sys3, sys2 = funnel_system_prompts_for_locale(locale_value)
    u1 = _build_step1_user_json(guide_user, foundation=foundation)
    r1: dict[str, Any] | None = None
    step1_ms = 0
    step1_cache_hit = False
    if cached_interpretation is not None and _interpretation_ok(cached_interpretation):
        r1 = cached_interpretation
        step1_cache_hit = True
    else:
        t0 = perf_counter()
        r1 = openai_json(sys1, u1, depth_level="quick")
        step1_ms = int((perf_counter() - t0) * 1000)
    base_meta: dict[str, Any] = {
        "failed": True,
        "step1_ms": step1_ms,
        "step2_ms": 0,
        "step3_ms": 0,
        "step1_cache_hit": step1_cache_hit,
        "step3_cache_hit": False,
        "user_json_step1": u1,
        "user_json_step2": "",
        "user_json_step3": "",
        "system_prompt_step1_preview": sys1[:280],
        "system_prompt_step2_preview": sys2[:280],
        "system_prompt_step3_preview": sys3[:280],
    }
    if not _interpretation_ok(r1):
        logger.info("guide_narrative_funnel_v0: step1 failed or invalid")
        return None, None, None, base_meta

    u3 = _build_step3_user_json(guide_user, r1)
    base_meta["user_json_step3"] = u3
    r3: dict[str, Any] | None = None
    step3_ms = 0
    step3_cache_hit = False
    if cached_core_text is not None and _core_text_ok(cached_core_text):
        r3 = cached_core_text
        step3_cache_hit = True
    else:
        t3 = perf_counter()
        r3 = openai_json(sys3, u3, depth_level=depth_norm)
        step3_ms = int((perf_counter() - t3) * 1000)
    base_meta["step3_ms"] = step3_ms
    base_meta["step3_cache_hit"] = step3_cache_hit
    core_out = r3 if _core_text_ok(r3) else None

    u2 = _build_step2_user_json(
        guide_user,
        r1,
        tier_norm=tier_norm,
        fusion_for_prompt=fusion_for_prompt,
        funnel_core=core_out,
    )
    base_meta["user_json_step2"] = u2
    t1 = perf_counter()
    r2 = openai_json(sys2, u2, depth_level=depth_norm)
    step2_ms = int((perf_counter() - t1) * 1000)
    base_meta["step2_ms"] = step2_ms
    if not _satellites_shape_ok(r2):
        logger.info("guide_narrative_funnel_v0: step2 failed or invalid")
        return None, r1, core_out, base_meta

    satellites = {k: v for k, v in r2.items() if k != "contract_version"}
    satellites["funnel_contract"] = FUNNEL_CONTRACT
    base_meta["failed"] = False
    return satellites, r1, core_out, base_meta


def funnel_openai_json_adapter(
    system: str,
    user: str,
    *,
    depth_level: str = "normal",
) -> dict[str, Any] | None:
    """Тонкий адаптер с отдельными max_tokens для воронки (тесты могут подменять модуль целиком)."""
    return _openai_json_funnel(system, user, depth_level=depth_level)
