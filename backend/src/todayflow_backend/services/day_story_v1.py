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
from todayflow_backend.services.day_story_value_gate_v1 import apply_day_story_value_gate
from todayflow_backend.services.today_contract_assembler_v1 import (
    TODAY_CONTRACT_V1_CONTRACT,
    TODAY_CONTRACT_V1_VERSION,
)
from todayflow_backend.services.today_contract_fallbacks_v1 import DOMAIN_FALLBACKS_V1
from todayflow_backend.services.today_contract_text_quality_v1 import (
    apply_text_quality_gate_to_contract,
)

DAY_STORY_V1_CONTRACT = "day_story_v1"
DAY_STORY_PROMPT_VER = "day-story-v1.10-no-formula-runtime"

INTERPRETATION_UNAVAILABLE_RU = (
    "Мы не смогли подготовить персональную интерпретацию дня. "
    "Попробуйте обновить экран через несколько минут."
)

PracticeKind = Literal["promise", "ascetic", "affirmation", "practice", "none"]

_DOMAIN_IDS = ("relationships", "money_work", "family")

_DAY_STORY_SYS_RU = """Ты — литературный редактор TodayFlow: пишешь единую историю дня только по evidence.

Смысл дня УЖЕ вычислен в interpretation (evidence + derived_claims + day_thesis + day_events_pack).
Твоя задача — связный рассказ дня (небо → ожидание → ловушка → ход → вайб), человеческим языком.
Нельзя придумывать новый смысл, астро-связи, события или сферы.

Вход — JSON:
- interpretation: evidence[], derived_claims[], domains_present, limitations, day_sky, day_foundation,
  day_personal, day_thesis {family, variant, mode, label_ru, driver_ids, composition_ids},
  day_events_pack / day_sky.day_events_pack
- day_foundation: astro + lunar layers + essence — objective plot
- day_personal: soft L3 — only via matching derived_claims
- day_engine_brief, ritual_context, user_core, rhythm_context, intent

Правила (жёстко):
- prose ТОЛЬКО поверх interpretation.derived_claims и evidence;
- личные soft-сигналы — только если есть claim.personal.*;
- domains.* только для id из interpretation.domains_present; иначе domains = {};
- карта/число — только если есть во входе;
- цвет / камень / практика — только при matching claim; иначе "";
- не начинай почти каждое предложение глаголом-командой;
- не повторяй один смысл в разных полях;

КАНОН «ОДИН СЮЖЕТ (day_thesis)»:
- interpretation.day_thesis — единственная центральная идея дня (family/variant/mode/label_ru).
  Не каждый день — конфликт: mode может быть conflict|opportunity|transition|recovery|stability.
- Вокруг тезиса — РОВНО драйверы из ranked_drivers / claim.day.driver.* (1–3 факта).
  Остальные события неба НЕ упоминай в events_lead.
- ambient из pack можно использовать только в vibe_closing (если явно в evidence).
- Не пиши пять тем. Один thesis → разные грани в разных полях.

СТРУКТУРА ПОЛЕЙ (обязательна):
- day_thesis — объект: скопируй family, variant, mode, label_ru, driver_ids, composition_ids из interpretation.
- primary_conflict — УСТАРЕВШИЙ alias: строка = day_thesis.label_ru (для совместимости).
- events_lead — 1 абзац: названные 1–3 драйвера и причинная связь.
- expect — чего ожидать сегодня в быту (сцена), только из drivers + claims.
- trap — одна ловушка / точка срыва (даже если mode != conflict — мягкая оговорка).
- story — 3–5 предложений на тех же драйверах (не dump слотов).
- do / avoid — следствия того же thesis и драйверов; конкретные действия с объектами.
- headline_anchor — образ-заголовок (может совпасть с label_ru); БЕЗ эмодзи.
- vibe_closing — 2–3 бытовых штриха; можно из drivers + approved ambient.
- development_point — личный soft-клейм → бытовой смысл, иначе "".
- Не подставляй универсальные шаблоны и готовые «формулы дня». Если evidence не хватает для слота — оставь слот пустой строкой / [].

Запрещены штампы:
«Сегодня сильнее», «Опирайся на это», «Зона риска», «Направить внимание», «Не распыляйся»,
«довериться потоку», «устойчивость через ритм», «один важный разговор», «одно дело до конца»,
«мягко проявить себя», «выбрать главное», «вселенная», «позволь себе», «важно помнить».

Тон: редакционный вайб TodayFlow — конкретика, энергия, узнаваемая сцена. Без драмы телеграм-оракула
и без канцелярита «спокойного наставника». Без эмодзи в JSON.

Верни только JSON:
{
  "theme": "string",
  "headline_anchor": "string — образ-заголовок дня, без эмодзи",
  "day_thesis": {
    "family": "string",
    "variant": "string",
    "mode": "conflict|opportunity|transition|recovery|stability",
    "label_ru": "string",
    "driver_ids": ["string"],
    "composition_ids": ["string"]
  },
  "primary_conflict": "string — alias = day_thesis.label_ru",
  "events_lead": "string — 1 абзац про 1–3 драйвера",
  "expect": "string — чего ожидать",
  "trap": "string — ловушка / оговорка дня",
  "direction": "string",
  "story": "string",
  "do": ["string","string"],
  "avoid": ["string","string"],
  "advantage": "string",
  "abstain": "string",
  "today_move": "string",
  "vibe_closing": "string — 2–3 штриха через «;» (или собери из vibe_strokes)",
  "vibe_strokes": ["string", "string"],
  "editorial": {"exemplar_id": "string", "strong_pattern_ids": ["SP-001"]},
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
        "primary_conflict": interpretation.get("primary_conflict"),
        "day_thesis": interpretation.get("day_thesis"),
        "day_events_pack": interpretation.get("day_events_pack"),
    }
    editorial = story.get("editorial") if isinstance(story.get("editorial"), dict) else None
    if editorial:
        out["editorial"] = editorial
        out["trace"]["editorial"] = editorial
    if used_fallback:
        lim = out["trace"]["limitations"]
        note = (
            "Персональная интерпретация недоступна: показаны только вычисляемые факты дня "
            "(без шаблонного prose)."
        )
        if note not in lim:
            lim.append(note)
        out["trace"]["interpretation_status"] = "unavailable"
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

    unavailable = str(payload.get("interpretation_status") or "").strip() == "unavailable"
    if unavailable:
        # Facts-only shell: machine thesis + optional events_lead; no canned prose required.
        thesis = payload.get("day_thesis") if isinstance(payload.get("day_thesis"), dict) else {}
        label = str(
            thesis.get("label_ru")
            or payload.get("primary_conflict")
            or payload.get("theme")
            or ""
        ).strip()
        if not label:
            errors.append("unavailable_missing_thesis_label")
        if not str(payload.get("interpretation_unavailable_message") or "").strip():
            errors.append("unavailable_missing_message")
    else:
        # Full interpretation: editorial slots carry the plot; story is optional when expect+trap exist.
        required = ("theme", "direction", "advantage", "abstain", "today_move", "global_period")
        for key in required:
            if not str(payload.get(key) or "").strip():
                errors.append(f"missing or empty: {key}")
        has_editorial = bool(str(payload.get("expect") or "").strip()) and bool(
            str(payload.get("trap") or payload.get("abstain") or "").strip()
        )
        if not has_editorial and not str(payload.get("story") or "").strip():
            errors.append("missing or empty: story")
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
            if unavailable or str(lens.get("evidence_status") or "present") == "absent":
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
    if not unavailable:
        scrubbed = apply_day_story_value_gate(payload)
        ok_phrase, phrase_hits = day_story_passes_phrase_gate(scrubbed)
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

    # Normalize day_thesis object
    thesis_in = raw.get("day_thesis") if isinstance(raw.get("day_thesis"), dict) else {}
    thesis_label = _clip(
        thesis_in.get("label_ru")
        or thesis_in.get("label")
        or raw.get("primary_conflict")
        or raw.get("headline_anchor")
        or raw.get("theme"),
        96,
    )
    day_thesis = {
        "family": _clip(thesis_in.get("family") or "momentum", 40),
        "variant": _clip(thesis_in.get("variant") or "steady_productive_rhythm", 64),
        "mode": _clip(thesis_in.get("mode") or "stability", 32),
        "label_ru": thesis_label,
        "driver_ids": [
            str(x).strip()
            for x in (thesis_in.get("driver_ids") or [])
            if str(x).strip()
        ][:3],
        "composition_ids": [
            str(x).strip()
            for x in (thesis_in.get("composition_ids") or [])
            if str(x).strip()
        ][:3],
    }

    out: dict[str, Any] = {
        "contract_version": DAY_STORY_V1_CONTRACT,
        "theme": _clip(raw.get("theme"), 240),
        "headline_anchor": _clip(raw.get("headline_anchor") or thesis_label or raw.get("theme"), 96),
        "day_thesis": day_thesis,
        "primary_conflict": thesis_label,  # deprecated alias
        "events_lead": _clip(raw.get("events_lead"), 480),
        "expect": _clip(raw.get("expect"), 400),
        "trap": _clip(raw.get("trap"), 360),
        "direction": _clip(raw.get("direction"), 480),
        "story": _clip(raw.get("story"), 1200),
        "do": [_clip(str(x), 200) for x in do_raw if str(x).strip()][:4],
        "avoid": [_clip(str(x), 200) for x in avoid_raw if str(x).strip()][:4],
        "advantage": _clip(raw.get("advantage"), 360),
        "abstain": _clip(raw.get("abstain"), 360),
        "today_move": _clip(raw.get("today_move"), 280),
        "vibe_closing": _clip(raw.get("vibe_closing"), 280),
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
    strokes_raw = raw.get("vibe_strokes")
    strokes: list[str] = []
    if isinstance(strokes_raw, list):
        strokes = [_clip(str(x), 80) for x in strokes_raw if str(x).strip()][:4]
    if not strokes and out["vibe_closing"]:
        strokes = [
            part.strip()
            for part in out["vibe_closing"].split(";")
            if part.strip()
        ][:4]
    if strokes:
        out["vibe_strokes"] = strokes
        if not out["vibe_closing"]:
            out["vibe_closing"] = _clip("; ".join(strokes), 280)
    editorial_in = raw.get("editorial") if isinstance(raw.get("editorial"), dict) else None
    if editorial_in:
        sp = [
            str(x).strip()
            for x in (editorial_in.get("strong_pattern_ids") or [])
            if str(x).strip().startswith("SP-")
        ][:4]
        editorial_out: dict[str, Any] = {
            "exemplar_id": _clip(editorial_in.get("exemplar_id"), 64),
            "strong_pattern_ids": sp,
        }
        if editorial_in.get("runtime_source"):
            editorial_out["runtime_source"] = _clip(editorial_in.get("runtime_source"), 40)
        if editorial_in.get("formula_bank"):
            editorial_out["formula_bank"] = _clip(editorial_in.get("formula_bank"), 40)
        out["editorial"] = editorial_out
    if not out["primary_action"]:
        out["primary_action"] = out["today_move"]
    if not out["headline_anchor"] and thesis_label:
        out["headline_anchor"] = thesis_label
    if not out["trap"] and out["abstain"]:
        out["trap"] = out["abstain"]
    if not out["abstain"] and out["trap"]:
        out["abstain"] = out["trap"]
    if not out["expect"] and out["direction"]:
        out["expect"] = out["direction"]
    if str(raw.get("interpretation_status") or "").strip() == "unavailable":
        out["interpretation_status"] = "unavailable"
        out["interpretation_unavailable_message"] = _clip(
            raw.get("interpretation_unavailable_message") or INTERPRETATION_UNAVAILABLE_RU,
            320,
        )
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
    """Facts-only shell when LLM is unavailable — never invent canned day prose.

    Keeps machine thesis + sky driver facts. Leaves expect/trap/do/avoid/vibe empty.
    Formula bank is QA/golden only and must not appear on this path.
    """
    _ = locale, ritual_context, intent_slice  # reserved for future fact projection
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

    conflict = interp.get("day_thesis") if isinstance(interp.get("day_thesis"), dict) else {}
    if not conflict:
        conflict = interp.get("primary_conflict") if isinstance(interp.get("primary_conflict"), dict) else {}
        if isinstance(conflict.get("day_thesis"), dict):
            conflict = conflict["day_thesis"]
    conflict_label = str(conflict.get("label_ru") or conflict.get("label") or "").strip()

    pack = interp.get("day_events_pack") if isinstance(interp.get("day_events_pack"), dict) else {}
    by_id = {
        str(e.get("id")): e
        for e in (pack.get("events") or [])
        if isinstance(e, dict) and e.get("id")
    }
    driver_facts: list[str] = []
    for did in conflict.get("driver_ids") or pack.get("ranked_drivers") or []:
        ev = by_id.get(str(did))
        if not ev:
            continue
        fact = str(ev.get("fact_ru") or ev.get("title_ru") or "").strip()
        if fact:
            driver_facts.append(fact)
        if len(driver_facts) >= 3:
            break
    events_lead = _clip(" ".join(driver_facts), 480)

    foundation = interp.get("day_foundation") if isinstance(interp.get("day_foundation"), dict) else {}
    essence = foundation.get("essence") if isinstance(foundation.get("essence"), dict) else {}
    essence_theme = str(essence.get("theme") or "").strip()
    theme = _clip(conflict_label or essence_theme, 200)

    day_thesis_payload = {
        "family": conflict.get("family") or "momentum",
        "variant": conflict.get("variant") or "steady_productive_rhythm",
        "mode": conflict.get("mode") or "stability",
        "label_ru": conflict_label or theme,
        "driver_ids": list(conflict.get("driver_ids") or pack.get("ranked_drivers") or [])[:3],
        "composition_ids": list(conflict.get("composition_ids") or [])[:3],
    }

    # Domains stay marked present when interpretation had them, but without invented copy.
    present = list(interp.get("domains_present") or [])
    domains: dict[str, Any] = {
        did: {
            "status": "",
            "opportunity": "",
            "risk": "",
            "action": "",
            "evidence_status": "present",
        }
        for did in present
        if did in _DOMAIN_IDS
    }

    color_why = next(
        (
            str(c.get("text") or "").strip()
            for c in (interp.get("derived_claims") or [])
            if isinstance(c, dict) and str(c.get("id") or "") == "claim.talisman.color_why"
        ),
        "",
    )

    raw_story: dict[str, Any] = {
        "interpretation_status": "unavailable",
        "interpretation_unavailable_message": INTERPRETATION_UNAVAILABLE_RU,
        "theme": theme,
        "headline_anchor": conflict_label or theme,
        "day_thesis": day_thesis_payload,
        "primary_conflict": conflict_label or theme,
        "events_lead": events_lead,
        "expect": "",
        "trap": "",
        "direction": "",
        "story": "",
        "do": [],
        "avoid": [],
        "advantage": "",
        "abstain": "",
        "today_move": "",
        "vibe_closing": "",
        "vibe_strokes": [],
        "global_period": theme,
        "development_point": "",
        "primary_action": "",
        "domains": domains,
        "talisman": {
            "color": color if color else "",
            "stone": stone if stone else "",
            "note": _clip(color_why, 200) if color_why else "",
        },
        "practice_recommendation": {"kind": "none", "text": "", "reason": ""},
        "supports_story": "",
        "evening_closure": "",
        "symbolic_note": "",
        "editorial": {
            "runtime_source": "facts_only",
            "formula_bank": "qa_only",
        },
    }

    payload = _normalize_day_story_payload(
        apply_day_story_value_gate(raw_story),
        domains_present=present,
    )
    # Preserve unavailable markers after normalize/gate.
    payload["interpretation_status"] = "unavailable"
    payload["interpretation_unavailable_message"] = INTERPRETATION_UNAVAILABLE_RU
    payload["expect"] = ""
    payload["trap"] = ""
    payload["direction"] = ""
    payload["story"] = ""
    payload["do"] = []
    payload["avoid"] = []
    payload["advantage"] = ""
    payload["abstain"] = ""
    payload["today_move"] = ""
    payload["primary_action"] = ""
    payload["vibe_closing"] = ""
    payload["vibe_strokes"] = []
    payload["development_point"] = ""
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
    thesis = interp.get("day_thesis") if isinstance(interp.get("day_thesis"), dict) else None
    if thesis:
        pack["day_thesis"] = thesis
    # editorial_formula bank is QA/golden only — never inject ready-made prose into LLM runtime.
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
    max_attempts: int = 2,
) -> dict[str, Any] | None:
    """Generate day_story via LLM. Retries once on empty/invalid; never fills formula prose."""
    from todayflow_backend.services.day_story_capture_session_v0 import get_day_story_capture_session

    if not is_llm_chat_configured():
        return None
    client = get_openai_compatible_client()
    if client is None:
        return None
    system = _DAY_STORY_SYS_RU
    interp = interpretation or (
        user_json.get("interpretation") if isinstance(user_json.get("interpretation"), dict) else {}
    )
    present = list((interp or {}).get("domains_present") or [])
    attempts = max(1, min(int(max_attempts or 1), 3))
    user_full = json.dumps(user_json, ensure_ascii=False)
    user_sent = user_full[:14000]
    model_name = ""
    try:
        model_name = str(resolve_default_chat_model() or "")
    except Exception:
        model_name = ""

    capture = get_day_story_capture_session()
    if capture is not None:
        capture.record_prompt(
            system=system,
            user_full=user_full,
            user_sent=user_sent,
            prompt_version=DAY_STORY_PROMPT_VER,
            model=model_name or None,
        )

    for attempt_idx in range(attempts):
        content = chat_completion_plain(
            client,
            model=resolve_default_chat_model(),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_sent},
            ],
            temperature=0.52,
            max_tokens=resolve_max_tokens(1800),
        )
        if not content:
            if capture is not None:
                capture.record_attempt(
                    attempt_index=attempt_idx,
                    raw_response=None,
                    parsed=None,
                    after_normalize=None,
                    after_gate=None,
                    status="empty_response",
                    reject_reason="empty_llm_content",
                )
            continue
        parsed = _parse_json_content(content)
        if not parsed:
            if capture is not None:
                capture.record_attempt(
                    attempt_index=attempt_idx,
                    raw_response=content,
                    parsed=None,
                    after_normalize=None,
                    after_gate=None,
                    status="parse_fail",
                    reject_reason="json_parse_failed",
                )
            continue
        # Keep LLM thesis if present; else inherit from interpretation.
        if not isinstance(parsed.get("day_thesis"), dict) and isinstance(
            (interp or {}).get("day_thesis"), dict
        ):
            parsed["day_thesis"] = interp["day_thesis"]
        after_normalize = _normalize_day_story_payload(parsed, domains_present=present)
        after_gate = _normalize_day_story_payload(
            apply_day_story_value_gate(after_normalize),
            domains_present=present,
        )
        after_gate["interpretation_status"] = "ok"
        after_gate.pop("interpretation_unavailable_message", None)
        ok_phrase, phrase_hits = day_story_passes_phrase_gate(after_gate, locale=locale)
        if not ok_phrase:
            if capture is not None:
                capture.record_attempt(
                    attempt_index=attempt_idx,
                    raw_response=content,
                    parsed=parsed,
                    after_normalize=after_normalize,
                    after_gate=after_gate,
                    phrase_ok=False,
                    phrase_hits=list(phrase_hits or []),
                    status="phrase_gate_reject",
                    reject_reason="phrase_gate",
                )
            continue
        if not str(after_gate.get("expect") or "").strip() and not str(after_gate.get("trap") or "").strip():
            # Too thin — retry rather than ship hollow slots or formula filler.
            if capture is not None:
                capture.record_attempt(
                    attempt_index=attempt_idx,
                    raw_response=content,
                    parsed=parsed,
                    after_normalize=after_normalize,
                    after_gate=after_gate,
                    phrase_ok=True,
                    phrase_hits=list(phrase_hits or []),
                    status="too_thin",
                    reject_reason="empty_expect_and_trap",
                )
            continue
        if capture is not None:
            capture.record_attempt(
                attempt_index=attempt_idx,
                raw_response=content,
                parsed=parsed,
                after_normalize=after_normalize,
                after_gate=after_gate,
                phrase_ok=True,
                phrase_hits=list(phrase_hits or []),
                status="accepted",
            )
        return attach_day_story_trace(
            after_gate,
            interp if isinstance(interp, dict) else {},
            used_fallback=False,
            prompt_version=DAY_STORY_PROMPT_VER,
            model_version=model_name,
        )
    return None


def day_story_to_today_contract_v1(
    story: dict[str, Any],
    *,
    generation_id: str | None = None,
    progress: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Map day_story_v1 → today_contract_v1 (direct, no legacy assembler)."""
    domains_in = story.get("domains") if isinstance(story.get("domains"), dict) else {}
    trace = story.get("trace") if isinstance(story.get("trace"), dict) else {}
    unavailable = str(story.get("interpretation_status") or "").strip() == "unavailable"
    present = set(trace.get("domains_present") or domains_in.keys())
    domains_out: dict[str, Any] = {}
    for did in _DOMAIN_IDS:
        if unavailable:
            domains_out[did] = _empty_domain_lens()
        elif did in present and did in domains_in:
            domains_out[did] = _domain_lens(domains_in.get(did), evidence_status="present")
        else:
            domains_out[did] = _empty_domain_lens()

    day_story_out = {
        "contract_version": DAY_STORY_V1_CONTRACT,
        "interpretation_status": "unavailable" if unavailable else str(story.get("interpretation_status") or "ok"),
        "interpretation_unavailable_message": (
            str(story.get("interpretation_unavailable_message") or INTERPRETATION_UNAVAILABLE_RU).strip()
            if unavailable
            else None
        ),
        "theme": story.get("theme"),
        "headline_anchor": story.get("headline_anchor") or story.get("theme"),
        "day_thesis": story.get("day_thesis") if isinstance(story.get("day_thesis"), dict) else None,
        "primary_conflict": story.get("primary_conflict")
        or ((story.get("day_thesis") or {}).get("label_ru") if isinstance(story.get("day_thesis"), dict) else None)
        or story.get("headline_anchor")
        or story.get("theme"),
        "events_lead": story.get("events_lead") or "",
        "expect": "" if unavailable else (story.get("expect") or story.get("direction") or ""),
        "trap": "" if unavailable else (story.get("trap") or story.get("abstain") or ""),
        "direction": "" if unavailable else story.get("direction"),
        "story": "" if unavailable else story.get("story"),
        "do": [] if unavailable else story.get("do"),
        "avoid": [] if unavailable else story.get("avoid"),
        "advantage": "" if unavailable else story.get("advantage"),
        "abstain": "" if unavailable else story.get("abstain"),
        "today_move": "" if unavailable else story.get("today_move"),
        "vibe_closing": "" if unavailable else (story.get("vibe_closing") or ""),
        "vibe_strokes": []
        if unavailable
        else (
            list(story.get("vibe_strokes") or [])
            if isinstance(story.get("vibe_strokes"), list)
            else []
        ),
        "editorial": story.get("editorial") if isinstance(story.get("editorial"), dict) else None,
        "talisman": None if unavailable else story.get("talisman"),
        "practice_recommendation": None if unavailable else story.get("practice_recommendation"),
        "symbolic_note": "" if unavailable else story.get("symbolic_note"),
        "supports_story": "" if unavailable else (story.get("supports_story") or ""),
        "evening_closure": "" if unavailable else (story.get("evening_closure") or ""),
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
        "interpretive_chorus": (
            story.get("interpretive_chorus")
            if isinstance(story.get("interpretive_chorus"), dict)
            else None
        ),
        "day_scenario": (
            story.get("day_scenario") if isinstance(story.get("day_scenario"), dict) else None
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
    if unavailable:
        progress_out["interpretation_status"] = "unavailable"

    contract = {
        "contract_version": TODAY_CONTRACT_V1_CONTRACT,
        "version": TODAY_CONTRACT_V1_VERSION,
        "global_context": {
            "period": (story.get("global_period") or story.get("theme") or "") if not unavailable else (story.get("theme") or "")
        },
        "personal_growth": {
            "development_point": "" if unavailable else (story.get("development_point") or "")
        },
        "domains": domains_out,
        "primary_action": "" if unavailable else (story.get("primary_action") or story.get("today_move") or ""),
        "progress": progress_out,
        "generation_id": generation_id or "",
        "day_story": day_story_out,
    }
    if unavailable:
        # Do not fill DOMAIN_FALLBACKS / period templates over an honest unavailable shell.
        return contract
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
        "headline": story.get("primary_conflict") or story.get("headline_anchor") or story.get("theme"),
        "subline": story.get("expect") or story.get("direction"),
        "energy_line": story.get("advantage"),
        "focus_line": story.get("direction"),
        "risk_line": _clip(str(avoid_items[0] if avoid_items else story.get("trap") or story.get("abstain")), 120),
        "risk_detail": story.get("trap") or story.get("abstain"),
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
