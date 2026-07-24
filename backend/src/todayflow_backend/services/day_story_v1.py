"""Day Story v1 — single editorial artifact for Today (canonical narrative).

Pipeline (PR-3 / explainable canon):
  sources → deterministic interpretation (evidence/claims) → prose (LLM or fallback)
  → phrase gate → today_contract_v1

Downstream: today_contract_v1, legacy guide/spheres payloads — derived without extra LLM.

Canon: SCREEN_CONTRACTS_V1 §3 · TODAY_LANGUAGE_V1 · EXPLAINABLE_COMPUTATION · PIM learning.
"""

from __future__ import annotations

import json
import re
from datetime import date
from typing import Any, Literal

from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_plain,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_default_chat_model,
    resolve_max_tokens,
)
from todayflow_backend.services.day_story_interpretation_v1 import (
    DAY_STORY_CALCULATION_VERSION,
    DAY_STORY_INTERPRETATION_V1,
    build_day_story_interpretation_v1,
)
from todayflow_backend.services.day_story_phrase_gate_v1 import day_story_passes_phrase_gate
from todayflow_backend.services.today_contract_assembler_v1 import (
    TODAY_CONTRACT_V1_CONTRACT,
    TODAY_CONTRACT_V1_VERSION,
)
from todayflow_backend.services.today_contract_fallbacks_v1 import DOMAIN_FALLBACKS_V1
from todayflow_backend.services.today_contract_text_quality_v1 import (
    apply_text_quality_gate_to_contract,
)

DAY_STORY_V1_CONTRACT = "day_story_v1"
DAY_STORY_PROMPT_VER = "day-story-v1.3-narrative-guide"

PracticeKind = Literal["promise", "ascetic", "affirmation", "practice", "none"]

_DOMAIN_IDS = ("relationships", "money_work", "family")

_DAY_STORY_SYS_RU = """Ты — литературный автор TodayFlow: пишешь живое повествование дня только по evidence.

Смысл дня УЖЕ вычислен в interpretation (evidence + derived_claims). Твоя задача — связный рассказ дня
(небо → ход → опоры), человеческим языком. Нельзя придумывать новый смысл, астро-связи или сферы.

Вход — JSON:
- interpretation: evidence[], derived_claims[], domains_present, limitations, day_sky, day_foundation, day_personal
- day_foundation: astro + lunar layers + essence (Суть дня) — objective plot; write story from this first
- day_personal: soft L3 (house rulers, time lords / Firdaria, HD channels) — only via matching derived_claims
- day_sky / talisman_reasons — готовые факты неба и why цвета/камня (если есть)
- day_engine_brief, ritual_context, user_core, rhythm_context, intent

Правила (жёстко):
- prose ТОЛЬКО поверх interpretation.derived_claims и evidence;
- личные soft-сигналы (управители домов, Firdaria, каналы HD) — только если есть claim.personal.*;
- domains.* только для id из interpretation.domains_present; иначе domains = {};
- карта/число — только если есть во входе; не пересказывай их отдельным абзацем;
- цвет / камень / практика: объясняй (talisman.note, practice_recommendation.reason, supports_story)
  ТОЛЬКО если есть matching claim (kind support / sky / claim.talisman.*); иначе эти поля = "";
- не сочиняй «потому что Меркурий → зелёный» без claim;
- не начинай почти каждое предложение глаголом-командой (Направить / Выбери / Опирайся / Держи);
- не повторяй один смысл в разных полях разными словами;
- story — 3–5 предложений со сменой ритма, как абзац из книги;
- supports_story — короткий абзац «Твой ход» (цвет/опора/практика), только по claims; иначе "";
- direction / advantage / abstain — наблюдения, не чек-лист;
- today_move / primary_action — практическая мысль человеческим тоном («Если успеешь…»), не «Выбери…»;
- do / avoid — короткие наблюдения (не список императивов).

СТРУКТУРА (обязательна для story, не опция):
- Возьми ИЗ ВСЕХ входных фактов (аспекты, фаза Луны, лунный день, управитель недели, натальные
  слои) РОВНО 2–3 самых значимых для сегодня. Остальные факты — не упоминай вообще, даже вскользь,
  даже одним словом. Один Sun-Mars ИЛИ Луна-фаза ИЛИ weekday ruler — не всё сразу.
- story = одна сцена на этих 2–3 фактах, не перечисление; между фактами — причинная связь
  («Х создаёт давление, поэтому Y»), не «также», «кроме того», «в картине дня».
- Ровно одна «ловушка дня» — конкретный момент, где легко перепутать один импульс с другим
  (например: пауза ≠ бездействие; напор ≠ грубость) — не общее предостережение.
- Никогда не повторяй факт (например «управитель дня недели»), который уже назван в другом
  поле ответа этого же JSON — каждый факт встречается ровно один раз во всём объекте.
- today_move — конкретный, представимый образ (что сделать/надеть/сказать), не абстрактный совет.

Запрещены штампы и пустые формулы:
«Сегодня сильнее», «Опирайся на это», «Зона риска», «Направить внимание», «Не распыляйся»,
«довериться потоку», «устойчивость через ритм», «один важный разговор», «одно дело до конца»,
«мягко проявить себя», «выбрать главное», «вселенная», «позволь себе», «важно помнить».

Тон: умный спокойный наставник. Без драмы и без телеграм-бота из однострочных абзацев.

Верни только JSON:
{
  "theme": "string",
  "direction": "string",
  "story": "string",
  "do": ["string","string"],
  "avoid": ["string","string"],
  "advantage": "string",
  "abstain": "string",
  "today_move": "string",
  "global_period": "string",
  "development_point": "string",
  "primary_action": "string",
  "domains": {
    "<только domains_present>": {"status":"string","opportunity":"string","risk":"string","action":"string"}
  },
  "talisman": {"color":"string","stone":"string","note":"string"},
  "practice_recommendation": {"kind":"promise|ascetic|affirmation|practice|none","text":"string","reason":"string"},
  "supports_story": "string",
  "evening_closure": "string",
  "symbolic_note": "string"
}
"""


def _clip(text: str, limit: int) -> str:
    t = re.sub(r"\s+", " ", str(text or "").strip())
    if len(t) <= limit:
        return t
    cut = t[: limit - 1]
    last_space = cut.rfind(" ")
    if last_space > 0:
        cut = cut[:last_space]
    return cut.rstrip() + "…"


def _voice_soften_line(text: str) -> str:
    """Turn command-lead brief lines into observations — same meaning, no new claims."""
    t = re.sub(r"\s+", " ", str(text or "").strip())
    if not t:
        return t
    low = t.lower()
    if low.startswith("выбери один короткий шаг"):
        return "Если успеешь закрыть одну важную вещь до обеда, остаток дня обычно идёт легче."
    if re.match(r"^выбери\s+", t, flags=re.I):
        rest = re.sub(r"^выбери\s+", "", t, count=1, flags=re.I)
        return f"Имеет смысл взять {rest[0].lower() + rest[1:]}" if rest else t
    if re.match(r"^сделай\s+", t, flags=re.I):
        rest = re.sub(r"^сделай\s+", "", t, count=1, flags=re.I)
        return f"Имеет смысл {rest[0].lower() + rest[1:]}" if rest else t
    if re.match(r"^направить\s+", t, flags=re.I):
        rest = re.sub(r"^направить\s+", "", t, count=1, flags=re.I)
        return f"День легче, когда внимание уходит на {rest[0].lower() + rest[1:]}" if rest else t
    if re.match(r"^опирайся\s+на\s+", t, flags=re.I):
        rest = re.sub(r"^опирайся\s+на\s+(это[:\s]*)?", "", t, count=1, flags=re.I)
        return rest[:1].upper() + rest[1:] if rest else t
    if "не распыляйся" in low:
        return re.sub(r"не\s+распыляйся[^.]*\.?", "Параллельные входы сегодня скорее шумят.", t, flags=re.I)
    if re.match(r"^держи\s+", t, flags=re.I):
        rest = re.sub(r"^держи\s+", "", t, count=1, flags=re.I)
        return f"Проще, когда день держит {rest[0].lower() + rest[1:]}" if rest else t
    return t


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


def _domain_lens(raw: Any, *, evidence_status: str = "present") -> dict[str, str]:
    src = raw if isinstance(raw, dict) else {}
    if evidence_status == "absent":
        return {
            "status": "",
            "opportunity": "",
            "risk": "",
            "action": "",
            "evidence_status": "absent",
        }
    return {
        "status": _clip(str(src.get("status") or ""), 320),
        "opportunity": _clip(str(src.get("opportunity") or ""), 320),
        "risk": _clip(str(src.get("risk") or ""), 320),
        "action": _clip(str(src.get("action") or ""), 280),
        "evidence_status": "present",
    }


def _empty_domain_lens() -> dict[str, str]:
    return _domain_lens({}, evidence_status="absent")


def attach_day_story_trace(
    story: dict[str, Any],
    interpretation: dict[str, Any],
    *,
    used_fallback: bool = False,
    prompt_version: str = DAY_STORY_PROMPT_VER,
    model_version: str = "",
) -> dict[str, Any]:
    """Stamp explainable trace onto the story artifact (kitchen, not marketing UI)."""
    out = dict(story)
    out["trace"] = {
        "contract_version": DAY_STORY_V1_CONTRACT,
        "calculation_version": interpretation.get("calculation_version") or DAY_STORY_CALCULATION_VERSION,
        "interpretation_version": interpretation.get("contract_version") or DAY_STORY_INTERPRETATION_V1,
        "prompt_version": prompt_version,
        "model_version": model_version or ("fallback" if used_fallback else ""),
        "source_inputs": interpretation.get("source_inputs") or {},
        "evidence": interpretation.get("evidence") or [],
        "derived_claims": interpretation.get("derived_claims") or [],
        "confidence": interpretation.get("confidence"),
        "limitations": list(interpretation.get("limitations") or []),
        "fingerprint": interpretation.get("fingerprint") or "",
        "domains_present": list(interpretation.get("domains_present") or []),
        "domains_absent": list(interpretation.get("domains_absent") or []),
        "used_fallback": bool(used_fallback),
    }
    if used_fallback:
        lim = out["trace"]["limitations"]
        note = "История собрана детерминированным fallback без LLM."
        if note not in lim:
            lim.append(note)
    foundation = interpretation.get("day_foundation")
    if isinstance(foundation, dict):
        out["day_foundation"] = foundation
        out["trace"]["day_foundation"] = {
            "calculation_version": foundation.get("calculation_version"),
            "essence": foundation.get("essence"),
            "source_inputs": foundation.get("source_inputs"),
            "astro_summary": (foundation.get("astro") or {}).get("summary_ru"),
            "lunar_summary": (foundation.get("lunar") or {}).get("summary_ru"),
        }
    personal = interpretation.get("day_personal")
    if isinstance(personal, dict):
        out["day_personal"] = personal
        out["trace"]["day_personal"] = {
            "calculation_version": personal.get("calculation_version"),
            "summary_ru": personal.get("summary_ru"),
            "source_inputs": personal.get("source_inputs"),
        }
    return out


def validate_day_story_v1(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("contract_version") != DAY_STORY_V1_CONTRACT:
        errors.append("invalid contract_version")
    for key in ("theme", "direction", "story", "advantage", "abstain", "today_move", "global_period"):
        if not str(payload.get(key) or "").strip():
            errors.append(f"missing or empty: {key}")
    for key in ("do", "avoid"):
        items = payload.get(key)
        if not isinstance(items, list) or len(items) < 2:
            errors.append(f"{key} must be list with >=2 items")
    domains = payload.get("domains")
    if not isinstance(domains, dict):
        errors.append("domains must be object")
    else:
        for did, lens in domains.items():
            if did not in _DOMAIN_IDS:
                errors.append(f"unknown domain: {did}")
                continue
            if not isinstance(lens, dict):
                errors.append(f"domains.{did} must be object")
                continue
            if str(lens.get("evidence_status") or "present") == "absent":
                continue
            for slot in ("status", "opportunity", "risk", "action"):
                if not str(lens.get(slot) or "").strip():
                    errors.append(f"domains.{did}.{slot} empty")
    trace = payload.get("trace")
    if not isinstance(trace, dict):
        errors.append("trace missing")
    else:
        if not isinstance(trace.get("evidence"), list):
            errors.append("trace.evidence missing")
        if not isinstance(trace.get("derived_claims"), list):
            errors.append("trace.derived_claims missing")
        if trace.get("confidence") is None:
            errors.append("trace.confidence missing")
        if not isinstance(trace.get("limitations"), list):
            errors.append("trace.limitations missing")
        if not str(trace.get("calculation_version") or "").strip():
            errors.append("trace.calculation_version missing")
    ok_phrase, phrase_hits = day_story_passes_phrase_gate(payload)
    if not ok_phrase:
        errors.append(f"empty_formula_hits: {phrase_hits[:5]}")
    return errors


def _normalize_day_story_payload(
    raw: dict[str, Any],
    *,
    domains_present: list[str] | None = None,
) -> dict[str, Any]:
    domains_in = raw.get("domains") if isinstance(raw.get("domains"), dict) else {}
    talisman_in = raw.get("talisman") if isinstance(raw.get("talisman"), dict) else {}
    practice_in = (
        raw.get("practice_recommendation")
        if isinstance(raw.get("practice_recommendation"), dict)
        else {}
    )
    kind = str(practice_in.get("kind") or "none").strip().lower()
    if kind not in ("promise", "ascetic", "affirmation", "practice", "none"):
        kind = "none"

    do_raw = raw.get("do") if isinstance(raw.get("do"), list) else []
    avoid_raw = raw.get("avoid") if isinstance(raw.get("avoid"), list) else []

    allowed = set(domains_present) if domains_present is not None else set(_DOMAIN_IDS)
    domains_out: dict[str, Any] = {}
    for did in _DOMAIN_IDS:
        if did not in allowed:
            continue
        if did not in domains_in:
            continue
        lens = _domain_lens(domains_in.get(did), evidence_status="present")
        if not any(str(lens.get(s) or "").strip() for s in ("status", "opportunity", "risk", "action")):
            continue
        domains_out[did] = lens

    out: dict[str, Any] = {
        "contract_version": DAY_STORY_V1_CONTRACT,
        "theme": _clip(raw.get("theme"), 240),
        "direction": _clip(raw.get("direction"), 480),
        "story": _clip(raw.get("story"), 1200),
        "do": [_clip(str(x), 200) for x in do_raw if str(x).strip()][:4],
        "avoid": [_clip(str(x), 200) for x in avoid_raw if str(x).strip()][:4],
        "advantage": _clip(raw.get("advantage"), 360),
        "abstain": _clip(raw.get("abstain"), 360),
        "today_move": _clip(raw.get("today_move"), 280),
        "global_period": _clip(raw.get("global_period") or raw.get("theme"), 360),
        "development_point": _clip(raw.get("development_point"), 360),
        "primary_action": _clip(raw.get("primary_action") or raw.get("today_move"), 280),
        "domains": domains_out,
        "talisman": {
            "color": _clip(talisman_in.get("color"), 80),
            "stone": _clip(talisman_in.get("stone"), 80),
            "note": _clip(talisman_in.get("note"), 200),
        },
        "practice_recommendation": {
            "kind": kind,
            "text": _clip(practice_in.get("text"), 240),
            "reason": _clip(practice_in.get("reason"), 240),
        },
        "evening_closure": _clip(raw.get("evening_closure"), 400),
        "symbolic_note": _clip(raw.get("symbolic_note"), 400),
        "supports_story": _clip(raw.get("supports_story"), 480),
    }
    if not out["primary_action"]:
        out["primary_action"] = out["today_move"]
    return out


def build_day_story_fallback_v1(
    *,
    day_engine_brief: dict[str, Any] | None,
    color: str = "",
    stone: str = "",
    locale: str = "ru",
    interpretation: dict[str, Any] | None = None,
    fingerprint: str | None = None,
    ritual_context: dict[str, Any] | None = None,
    intent_slice: dict[str, Any] | None = None,
    celestial_events: dict[str, Any] | None = None,
    color_symbol: dict[str, Any] | None = None,
    stone_symbol: dict[str, Any] | None = None,
    target_date: date | None = None,
    birth_date: date | None = None,
) -> dict[str, Any]:
    """Deterministic story from interpretation + brief when LLM unavailable."""
    interp = interpretation or build_day_story_interpretation_v1(
        day_engine_brief=day_engine_brief,
        ritual_context=ritual_context,
        intent_slice=intent_slice,
        color=color,
        stone=stone,
        celestial_events=celestial_events,
        color_symbol=color_symbol,
        stone_symbol=stone_symbol,
        fingerprint=fingerprint,
        locale=locale,
        target_date=target_date,
        birth_date=birth_date,
    )
    brief = day_engine_brief if isinstance(day_engine_brief, dict) else {}
    interp_essence = (
        (interp.get("day_foundation") or {}).get("essence")
        if isinstance(interp.get("day_foundation"), dict)
        else {}
    )
    essence_theme = str((interp_essence or {}).get("theme") or "").strip()
    essence_story = str((interp_essence or {}).get("story_ru") or "").strip()

    anchor = _voice_soften_line(
        str(
            essence_theme
            or brief.get("anchor_summary")
            or "День проще держать, когда ясно одно маленькое дело, а не весь общий фон."
        )
    )
    do_hint = _voice_soften_line(
        str(
            brief.get("do_hint")
            or "Если успеешь закрыть одну важную вещь до обеда, остаток дня обычно идёт легче."
        )
    )
    avoid_hint = _voice_soften_line(
        str(
            brief.get("avoid_hint")
            or "Лишние обещания сегодня легко превратятся в шум — лучше не раздувать список."
        )
    )
    tempo = _voice_soften_line(
        str(
            brief.get("tempo_hint")
            or "Темп лучше ровный: без рывков и без ощущения, что надо успеть всё сразу."
        )
    )
    theme = _clip(essence_theme or (anchor.split(".")[0] if "." in anchor else anchor), 200)
    story = _clip(essence_story or f"{anchor} {tempo} {do_hint}", 900)

    present = list(interp.get("domains_present") or [])
    domains: dict[str, Any] = {}
    for did in present:
        domains[did] = {
            "status": _clip(theme, 200),
            "opportunity": _clip(do_hint, 200),
            "risk": _clip(avoid_hint, 200),
            "action": _clip(do_hint, 200),
            "evidence_status": "present",
        }

    support_claims = [
        str(c.get("text") or "").strip()
        for c in (interp.get("derived_claims") or [])
        if isinstance(c, dict) and str(c.get("kind") or "") == "support" and str(c.get("text") or "").strip()
    ]
    color_why = next(
        (
            str(c.get("text") or "").strip()
            for c in (interp.get("derived_claims") or [])
            if isinstance(c, dict) and str(c.get("id") or "") == "claim.talisman.color_why"
        ),
        "",
    )
    supports_story = _clip(" ".join(support_claims[:2]), 480) if support_claims else ""
    talisman_note = _clip(color_why, 200) if color_why else ""

    payload = _normalize_day_story_payload(
        {
            "theme": theme,
            "direction": tempo,
            "story": story,
            "do": [
                do_hint,
                "После главного шага имеет смысл коротко заметить, стало ли спокойнее.",
            ],
            "avoid": [
                avoid_hint,
                "Второй приоритет без времени почти всегда крадёт ясность у первого.",
            ],
            "advantage": do_hint,
            "abstain": avoid_hint,
            "today_move": do_hint,
            "global_period": theme,
            "development_point": "Замечать, что реально двигает день, а что только шум.",
            "primary_action": do_hint,
            "domains": domains,
            "talisman": {
                "color": color if color else "",
                "stone": stone if stone else "",
                "note": talisman_note,
            },
            "practice_recommendation": {"kind": "none", "text": "", "reason": ""},
            "supports_story": supports_story,
            "evening_closure": "К вечеру достаточно коротко отметить, что получилось — без жёсткой самооценки.",
            "symbolic_note": "",
        },
        domains_present=present,
    )
    return attach_day_story_trace(
        payload,
        interp,
        used_fallback=True,
        prompt_version=DAY_STORY_PROMPT_VER,
        model_version="fallback",
    )


def build_day_story_llm_input(
    *,
    day_engine_brief: dict[str, Any] | None,
    ritual_context: dict[str, Any] | None,
    user_core_slim: dict[str, Any] | None,
    intent_slice: dict[str, Any] | None,
    behavior_patterns: dict[str, Any] | None,
    rhythm_context: dict[str, Any] | None,
    color: str = "",
    stone: str = "",
    locale: str = "ru",
    interpretation: dict[str, Any] | None = None,
    celestial_events: dict[str, Any] | None = None,
    color_symbol: dict[str, Any] | None = None,
    stone_symbol: dict[str, Any] | None = None,
    target_date: date | None = None,
    birth_date: date | None = None,
) -> dict[str, Any]:
    color_sym = color_symbol if isinstance(color_symbol, dict) else {}
    stone_sym = stone_symbol if isinstance(stone_symbol, dict) else {}
    interp = interpretation or build_day_story_interpretation_v1(
        day_engine_brief=day_engine_brief,
        ritual_context=ritual_context,
        intent_slice=intent_slice,
        rhythm_context=rhythm_context,
        color=color,
        stone=stone,
        celestial_events=celestial_events,
        color_symbol=color_sym or None,
        stone_symbol=stone_sym or None,
        locale=locale,
        target_date=target_date,
        birth_date=birth_date,
    )
    day_sky = interp.get("day_sky") if isinstance(interp.get("day_sky"), dict) else {}
    talisman_reasons: dict[str, Any] = {}
    if color_sym or color:
        talisman_reasons["color"] = {
            "name": str(color_sym.get("name") or color or "").strip(),
            "story_ru": str(color_sym.get("story_ru") or "").strip(),
            "benefit_ru": str(color_sym.get("benefit_ru") or "").strip(),
            "avoid_color_ru": str(color_sym.get("avoid_color_ru") or "").strip(),
            "avoid_why_ru": str(color_sym.get("avoid_why_ru") or "").strip(),
        }
    if stone_sym or stone:
        talisman_reasons["stone"] = {
            "name": str(stone_sym.get("name") or stone or "").strip(),
            "story_ru": str(stone_sym.get("story_ru") or "").strip(),
        }
    pack: dict[str, Any] = {
        "locale": locale,
        "interpretation": interp,
        "day_engine_brief": day_engine_brief,
        "ritual_context": ritual_context or {},
        "user_core": user_core_slim or {},
        "talisman_inputs": {"color": color, "stone": stone},
        "day_sky": day_sky,
        "talisman_reasons": talisman_reasons,
    }
    if isinstance(interp.get("day_foundation"), dict):
        pack["day_foundation"] = interp["day_foundation"]
    if isinstance(interp.get("day_personal"), dict):
        pack["day_personal"] = interp["day_personal"]
    if intent_slice:
        pack["intent"] = intent_slice
    if behavior_patterns and behavior_patterns.get("total_events"):
        pack["behavior_patterns"] = behavior_patterns
    if rhythm_context:
        pack["rhythm_context"] = rhythm_context
    return pack


def call_day_story_llm_v1(
    user_json: dict[str, Any],
    *,
    locale: str = "ru",
    interpretation: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if not is_llm_chat_configured():
        return None
    client = get_openai_compatible_client()
    if client is None:
        return None
    system = _DAY_STORY_SYS_RU
    content = chat_completion_plain(
        client,
        model=resolve_default_chat_model(),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user_json, ensure_ascii=False)[:14000]},
        ],
        temperature=0.52,
        max_tokens=resolve_max_tokens(1800),
    )
    if not content:
        return None
    parsed = _parse_json_content(content)
    if not parsed:
        return None
    interp = interpretation or (
        user_json.get("interpretation") if isinstance(user_json.get("interpretation"), dict) else {}
    )
    present = list((interp or {}).get("domains_present") or [])
    normalized = _normalize_day_story_payload(parsed, domains_present=present)
    ok_phrase, _hits = day_story_passes_phrase_gate(normalized, locale=locale)
    if not ok_phrase:
        return None
    model_name = ""
    try:
        model_name = str(resolve_default_chat_model() or "")
    except Exception:
        model_name = ""
    return attach_day_story_trace(
        normalized,
        interp if isinstance(interp, dict) else {},
        used_fallback=False,
        prompt_version=DAY_STORY_PROMPT_VER,
        model_version=model_name,
    )


def day_story_to_today_contract_v1(
    story: dict[str, Any],
    *,
    generation_id: str | None = None,
    progress: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Map day_story_v1 → today_contract_v1 (direct, no legacy assembler)."""
    domains_in = story.get("domains") if isinstance(story.get("domains"), dict) else {}
    trace = story.get("trace") if isinstance(story.get("trace"), dict) else {}
    present = set(trace.get("domains_present") or domains_in.keys())
    domains_out: dict[str, Any] = {}
    for did in _DOMAIN_IDS:
        if did in present and did in domains_in:
            domains_out[did] = _domain_lens(domains_in.get(did), evidence_status="present")
        else:
            domains_out[did] = _empty_domain_lens()

    day_story_out = {
        "contract_version": DAY_STORY_V1_CONTRACT,
        "theme": story.get("theme"),
        "direction": story.get("direction"),
        "story": story.get("story"),
        "do": story.get("do"),
        "avoid": story.get("avoid"),
        "advantage": story.get("advantage"),
        "abstain": story.get("abstain"),
        "today_move": story.get("today_move"),
        "talisman": story.get("talisman"),
        "practice_recommendation": story.get("practice_recommendation"),
        "symbolic_note": story.get("symbolic_note"),
        "supports_story": story.get("supports_story") or "",
        "day_foundation": (
            (story.get("trace") or {}).get("day_foundation")
            if isinstance(story.get("trace"), dict)
            else None
        )
        or story.get("day_foundation"),
        "day_personal": (
            story.get("day_personal")
            if isinstance(story.get("day_personal"), dict)
            else (
                (story.get("trace") or {}).get("day_personal")
                if isinstance(story.get("trace"), dict)
                and isinstance((story.get("trace") or {}).get("day_personal"), dict)
                else None
            )
        ),
        "trace": trace,
    }
    progress_out = dict(progress) if isinstance(progress, dict) else {}
    if trace:
        progress_out.setdefault("story_confidence", trace.get("confidence"))
        progress_out.setdefault("story_limitations", trace.get("limitations") or [])
        progress_out.setdefault("domains_present", trace.get("domains_present") or [])
        progress_out.setdefault("domains_absent", trace.get("domains_absent") or [])
        if trace.get("fingerprint"):
            progress_out.setdefault("story_interpretation_fingerprint", trace.get("fingerprint"))

    contract = {
        "contract_version": TODAY_CONTRACT_V1_CONTRACT,
        "version": TODAY_CONTRACT_V1_VERSION,
        "global_context": {"period": story.get("global_period") or story.get("theme")},
        "personal_growth": {"development_point": story.get("development_point") or ""},
        "domains": domains_out,
        "primary_action": story.get("primary_action") or story.get("today_move") or "",
        "progress": progress_out,
        "generation_id": generation_id or "",
        "day_story": day_story_out,
    }
    return apply_text_quality_gate_to_contract(
        contract,
        DOMAIN_FALLBACKS_V1,
        skip_absent_domains=True,
    )


def day_story_to_legacy_narrative(story: dict[str, Any], *, generation_id: str | None = None) -> dict[str, Any]:
    """Derive legacy guide/spheres/day_layer/evening payloads — no LLM."""
    domains = story.get("domains") if isinstance(story.get("domains"), dict) else {}
    rel = _domain_lens(domains.get("relationships")) if "relationships" in domains else _empty_domain_lens()
    mw = _domain_lens(domains.get("money_work")) if "money_work" in domains else _empty_domain_lens()
    fam = _domain_lens(domains.get("family")) if "family" in domains else _empty_domain_lens()
    do_items = story.get("do") if isinstance(story.get("do"), list) else []
    avoid_items = story.get("avoid") if isinstance(story.get("avoid"), list) else []
    practice = (
        story.get("practice_recommendation")
        if isinstance(story.get("practice_recommendation"), dict)
        else {}
    )

    guide: dict[str, Any] = {
        "headline": story.get("theme"),
        "subline": story.get("direction"),
        "energy_line": story.get("advantage"),
        "focus_line": story.get("direction"),
        "risk_line": _clip(str(avoid_items[0] if avoid_items else story.get("abstain")), 120),
        "risk_detail": story.get("abstain"),
        "do_items": do_items[:3],
        "avoid_items": avoid_items[:3],
        "header_disclaimer": "Это про ваш личный день, не про совместимость с другими.",
        "context_for_next_surfaces": story.get("story"),
        "pattern_insight": "",
        "life_context_insight": "",
        "core_message": {"body": story.get("story"), "best_move": story.get("today_move")},
        "action_options": [
            story.get("today_move"),
            str(practice.get("text") or "") if practice.get("text") else do_items[1] if len(do_items) > 1 else "",
            do_items[2] if len(do_items) > 2 else "",
        ],
        "sphere_triad": [
            {"area": "work", "stance": "up", "line": mw.get("action") or mw.get("opportunity")},
            {"area": "love", "stance": "neutral", "line": rel.get("action") or rel.get("opportunity")},
            {"area": "money", "stance": "neutral", "line": mw.get("status") or mw.get("risk")},
        ],
        "support_hooks": [x for x in [practice.get("text"), story.get("primary_action")] if x][:2],
        "day_story_source": DAY_STORY_V1_CONTRACT,
    }

    spheres = {
        "page_intro": story.get("story"),
        "thesis_reminder": story.get("theme"),
        "scenario_tie_ins": {
            "love": rel.get("action") or rel.get("opportunity"),
            "family": fam.get("action") or fam.get("opportunity"),
            "career": mw.get("action") or mw.get("opportunity"),
            "money": mw.get("opportunity") or mw.get("status"),
        },
    }

    day_layer = {
        "nudge_message": story.get("today_move"),
        "nudge_cta_label": "Сделать шаг",
        "personal_insight_title": story.get("theme"),
        "personal_insight_body": story.get("story"),
        "personal_insight_chips": do_items[:3],
        "mini_decision_caption": avoid_items[0] if avoid_items else story.get("abstain"),
        "question_of_day_prompt": story.get("direction"),
        "life_now_weekly": "",
        "life_now_discipline": story.get("development_point") or "",
    }

    evening = {
        "panel_intro": story.get("evening_closure") or "Коротко закрой день: что получилось, что отпустить.",
        "outlook_preamble": story.get("story"),
        "closure_invitation": story.get("evening_closure") or "Одна строка — чем день запомнился.",
    }

    return {
        "guide": {"generation_id": generation_id or "", "payload": guide},
        "spheres": {"payload": spheres},
        "day_layer": {"payload": day_layer},
        "evening": {"payload": evening},
        "day_story": story,
    }
