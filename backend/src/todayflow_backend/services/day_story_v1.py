"""Day Story v1 — single editorial artifact for Today (canonical narrative).

One LLM call (or deterministic fallback) produces the full day story:
theme, direction, story, do/avoid, domains, talisman, practice recommendation.

Downstream: today_contract_v1, legacy guide/spheres payloads — derived without extra LLM.

Canon: SCREEN_CONTRACTS_V1 §3 · TODAY_LANGUAGE_V1 · PIM learning via generation_logs.
"""

from __future__ import annotations

import json
import re
from typing import Any, Literal

from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_plain,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_default_chat_model,
    resolve_max_tokens,
)
from todayflow_backend.services.today_contract_assembler_v1 import (
    TODAY_CONTRACT_V1_CONTRACT,
    TODAY_CONTRACT_V1_VERSION,
)
from todayflow_backend.services.today_contract_fallbacks_v1 import DOMAIN_FALLBACKS_V1
from todayflow_backend.services.today_contract_text_quality_v1 import (
    apply_text_quality_gate_to_contract,
)

DAY_STORY_V1_CONTRACT = "day_story_v1"
DAY_STORY_PROMPT_VER = "day-story-v1.1"

PracticeKind = Literal["promise", "ascetic", "affirmation", "practice", "none"]

_DOMAIN_IDS = ("relationships", "money_work", "family")

_DAY_STORY_SYS_RU = """Ты пишешь **одну связную историю дня** для TodayFlow (русский язык).

Вход — JSON с фактами: day_engine_brief (ось дня, mood, goals), ritual_context (карта/число только если раскрыты), профиль (сжато), rhythm_context, intent, behavior_patterns, daily_foundation.

Роли источников:
- основа дня = пользователь + mood + goals + ось foundation;
- карта и число из ritual_context — только дополнение, не доминируют;
- не дублируй карту/число: они уже в ritual_context; не пересказывай их отдельным абзацем и не усиливай дважды;
- не выдумывай факты, события, имена и даты, которых нет во входе;
- если карты или числа нет во входе — не упоминай их.

Задача: **один авторский текст**, без повторов между полями. Каждое поле — свой ракурс:
- theme — одна строка, суть дня (не пара абстрактных существительных)
- direction — куда направить внимание (1–2 предложения)
- story — связный текст 3–5 предложений: что за день, почему так, что с человеком происходит
- do / avoid — по 3 пункта, глагол + конкретика
- advantage / abstain — где плюс дня / от чего воздержаться (по одному предложению)
- today_move — один выполнимый шаг сегодня
- domains.* — три жизненных домена (relationships, money_work, family): status, opportunity, risk, action — разные формулировки, не копируй story дословно
- practice_recommendation — одна рекомендация из rhythm_context: promise | ascetic | affirmation | practice | none + text + reason; если данных нет — kind none, text ""
- talisman — color и stone из входа или нейтральные подсказки дня; note — одна строка как носить/зачем

Тон: живой, человеческий, без «вселенная/поток», без приговора, без терапевтических клише («позволь себе», «важно помнить», «возможно, стоит»). Опирайся только на факты JSON.

Верни только JSON:
{
  "theme": "string",
  "direction": "string",
  "story": "string",
  "do": ["string","string","string"],
  "avoid": ["string","string","string"],
  "advantage": "string",
  "abstain": "string",
  "today_move": "string",
  "global_period": "string",
  "development_point": "string",
  "primary_action": "string",
  "domains": {
    "relationships": {"status":"string","opportunity":"string","risk":"string","action":"string"},
    "money_work": {"status":"string","opportunity":"string","risk":"string","action":"string"},
    "family": {"status":"string","opportunity":"string","risk":"string","action":"string"}
  },
  "talisman": {"color":"string","stone":"string","note":"string"},
  "practice_recommendation": {"kind":"promise|ascetic|affirmation|practice|none","text":"string","reason":"string"},
  "evening_closure": "string",
  "symbolic_note": "string"
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


def _domain_lens(raw: Any) -> dict[str, str]:
    src = raw if isinstance(raw, dict) else {}
    return {
        "status": _clip(str(src.get("status") or ""), 320),
        "opportunity": _clip(str(src.get("opportunity") or ""), 320),
        "risk": _clip(str(src.get("risk") or ""), 320),
        "action": _clip(str(src.get("action") or ""), 280),
    }


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
        for did in _DOMAIN_IDS:
            lens = domains.get(did)
            if not isinstance(lens, dict):
                errors.append(f"domains.{did} missing")
                continue
            for slot in ("status", "opportunity", "risk", "action"):
                if not str(lens.get(slot) or "").strip():
                    errors.append(f"domains.{did}.{slot} empty")
    return errors


def _normalize_day_story_payload(raw: dict[str, Any]) -> dict[str, Any]:
    domains_in = raw.get("domains") if isinstance(raw.get("domains"), dict) else {}
    talisman_in = raw.get("talisman") if isinstance(raw.get("talisman"), dict) else {}
    practice_in = raw.get("practice_recommendation") if isinstance(raw.get("practice_recommendation"), dict) else {}
    kind = str(practice_in.get("kind") or "none").strip().lower()
    if kind not in ("promise", "ascetic", "affirmation", "practice", "none"):
        kind = "none"

    do_raw = raw.get("do") if isinstance(raw.get("do"), list) else []
    avoid_raw = raw.get("avoid") if isinstance(raw.get("avoid"), list) else []

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
        "domains": {did: _domain_lens(domains_in.get(did)) for did in _DOMAIN_IDS},
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
) -> dict[str, Any]:
    """Deterministic story from day_engine_brief when LLM unavailable."""
    brief = day_engine_brief if isinstance(day_engine_brief, dict) else {}
    anchor = str(brief.get("anchor_summary") or "Сегодня — один ясный приоритет и спокойный темп.")
    do_hint = str(brief.get("do_hint") or "Сделай один главный шаг и зафиксируй результат.")
    avoid_hint = str(brief.get("avoid_hint") or "Не распыляйся на лишние обещания.")
    tempo = str(brief.get("tempo_hint") or "Держи ровный темп.")
    theme = _clip(anchor.split(".")[0] if "." in anchor else anchor, 200)
    story = _clip(f"{anchor} {tempo}", 900)

    generic_domain = {
        "status": _clip(theme, 200),
        "opportunity": _clip(do_hint, 200),
        "risk": _clip(avoid_hint, 200),
        "action": _clip(do_hint, 200),
    }
    return _normalize_day_story_payload(
        {
            "theme": theme,
            "direction": tempo,
            "story": story,
            "do": [do_hint, "Проверить состояние после главного шага", "Оставить время на паузу"],
            "avoid": [avoid_hint, "Не брать второй приоритет без времени", "Не форсировать темп"],
            "advantage": do_hint,
            "abstain": avoid_hint,
            "today_move": do_hint,
            "global_period": theme,
            "development_point": "Замечать, что реально двигает день, а что только шум.",
            "primary_action": do_hint,
            "domains": {
                "relationships": dict(generic_domain),
                "money_work": dict(generic_domain),
                "family": dict(generic_domain),
            },
            "talisman": {"color": color or "спокойный нейтральный", "stone": stone or "—", "note": ""},
            "practice_recommendation": {"kind": "none", "text": "", "reason": ""},
            "evening_closure": "Коротко отметь, что получилось — без самооценки.",
            "symbolic_note": "",
        }
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
) -> dict[str, Any]:
    pack: dict[str, Any] = {
        "locale": locale,
        "day_engine_brief": day_engine_brief,
        "ritual_context": ritual_context or {},
        "user_core": user_core_slim or {},
        "talisman_inputs": {"color": color, "stone": stone},
    }
    if intent_slice:
        pack["intent"] = intent_slice
    if behavior_patterns and behavior_patterns.get("total_events"):
        pack["behavior_patterns"] = behavior_patterns
    if rhythm_context:
        pack["rhythm_context"] = rhythm_context
    return pack


def call_day_story_llm_v1(user_json: dict[str, Any], *, locale: str = "ru") -> dict[str, Any] | None:
    if not is_llm_chat_configured():
        return None
    client = get_openai_compatible_client()
    if client is None:
        return None
    system = _DAY_STORY_SYS_RU if locale.lower().startswith("ru") else _DAY_STORY_SYS_RU
    content = chat_completion_plain(
        client,
        model=resolve_default_chat_model(),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user_json, ensure_ascii=False)[:12000]},
        ],
        temperature=0.52,
        max_tokens=resolve_max_tokens(1800),
    )
    if not content:
        return None
    parsed = _parse_json_content(content)
    if not parsed:
        return None
    return _normalize_day_story_payload(parsed)


def day_story_to_today_contract_v1(
    story: dict[str, Any],
    *,
    generation_id: str | None = None,
    progress: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Map day_story_v1 → today_contract_v1 (direct, no legacy assembler)."""
    domains = story.get("domains") if isinstance(story.get("domains"), dict) else {}
    contract = {
        "contract_version": TODAY_CONTRACT_V1_CONTRACT,
        "version": TODAY_CONTRACT_V1_VERSION,
        "global_context": {"period": story.get("global_period") or story.get("theme")},
        "personal_growth": {"development_point": story.get("development_point") or ""},
        "domains": {did: _domain_lens(domains.get(did)) for did in _DOMAIN_IDS},
        "primary_action": story.get("primary_action") or story.get("today_move") or "",
        "progress": progress if isinstance(progress, dict) else {},
        "generation_id": generation_id or "",
        "day_story": {
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
        },
    }
    return apply_text_quality_gate_to_contract(contract, DOMAIN_FALLBACKS_V1)


def day_story_to_legacy_narrative(story: dict[str, Any], *, generation_id: str | None = None) -> dict[str, Any]:
    """Derive legacy guide/spheres/day_layer/evening payloads — no LLM."""
    domains = story.get("domains") if isinstance(story.get("domains"), dict) else {}
    rel = _domain_lens(domains.get("relationships"))
    mw = _domain_lens(domains.get("money_work"))
    fam = _domain_lens(domains.get("family"))
    do_items = story.get("do") if isinstance(story.get("do"), list) else []
    avoid_items = story.get("avoid") if isinstance(story.get("avoid"), list) else []
    practice = story.get("practice_recommendation") if isinstance(story.get("practice_recommendation"), dict) else {}

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

    narrative: dict[str, Any] = {
        "guide": {"generation_id": generation_id or "", "payload": guide},
        "spheres": {"payload": spheres},
        "day_layer": {"payload": day_layer},
        "evening": {"payload": evening},
        "day_story": story,
    }
    return narrative
