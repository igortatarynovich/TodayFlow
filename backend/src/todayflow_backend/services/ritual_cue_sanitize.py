"""Нормализация текстов ритуала/гороскопа для UI. Паритет с frontend `ritualCueSanitizer.ts` и iOS `TodayRitualCueSanitizer.swift`."""

from __future__ import annotations

import copy
import re
from typing import Any

_SLUG_TO_RU: dict[str, str] = {
    "general": "общий фон дня",
    "love": "любовь и близость",
    "relations": "отношения",
    "career": "работа и карьера",
    "work": "работа и карьера",
    "money": "деньги и границы",
    "family": "семья и дом",
    "home": "семья и дом",
    "body": "тело и восстановление",
    "health": "тело и восстановление",
    "dialogue": "общение и контакт",
    "communication": "общение и контакт",
    "decision": "решение, которое надо принять",
    "identity": "линия про себя",
    "self": "линия про себя",
}

# Паритет `day_narrative_brief_v0` (head_topic в брифе) — приоритетнее общих линий сфер для slug темы «в голове».
_HEAD_TOPIC_SLUG_RU: dict[str, str] = {
    "general": "общий фон дня",
    "body": "тело и энергия",
    "money": "деньги",
    "dialogue": "общение и контакт",
    "family": "семья и дом",
    "career": "работа и дела",
    "love": "близость и отношения",
}

# id настроения чек-ина → RU (как `day_narrative_brief_v0._MOOD_ID_RU`).
_MOOD_SLUG_TO_RU: dict[str, str] = {
    "calm": "спокойно",
    "anxious": "тревожно",
    "tired": "устало",
    "driven": "в драйве",
    "irritated": "раздражённо",
    "other": "другое",
    "motivated": "в драйве",
    "confused": "неясно",
    "quiet_wish": "хочется тишины",
    "move_wish": "хочется движения",
    "heavy": "тяжело",
    "hopeful": "с надеждой",
    "distant": "на дистанции",
}

_QUOTED_SERVICE_SLUG_TO_RU: dict[str, str] = {**_SLUG_TO_RU, **_HEAD_TOPIC_SLUG_RU, **_MOOD_SLUG_TO_RU}

# Кавычки + типографские «»; service slug латиницей (настроение / head_topic / линия сферы).
_QUOTED_EN_SERVICE_SLUG_RE = re.compile(
    r"""(?:['"]|«)([a-z][a-z0-9_]{0,31})(?:['"]|»)""",
    re.IGNORECASE,
)

_TOPIC_LABELS_NOT_ACTIONS: frozenset[str] = frozenset(
    {
        "смысл и коммуникация",
        "смысл и коммуникации",
        "смысл и коммуникацию",
        "общий фокус дня",
        "общий фон дня",
        "общение и контакт",
        # O3: абстрактные «заголовки» day_layer / рубрики без прикладного смысла
        "смысл дня",
        "контекст дня",
        "рамка дня",
        "общая картина",
        "картина дня",
        "настрой на день",
        "тональность дня",
        "вектор дня",
        "форма дня",
        "сигнал дня",
        "паттерн дня",
    }
)


def is_ru_abstract_topic_headline(text: str | None) -> bool:
    """True, если строка — только тема/рубрика, а не конкретный заголовок (O3, паритет guide headline gate)."""
    t = (text or "").strip().lower()
    if not t:
        return True
    return t in _TOPIC_LABELS_NOT_ACTIONS

_JUNK_FOCUS: frozenset[str] = frozenset(
    {
        "general",
        "overall",
        "mixed",
        "none",
        "other",
        "default",
        "общее",
        "прочее",
        "другое",
        "без фокуса",
    }
)

_QUOTED_SLUG = re.compile(r"['«]([a-z][a-z0-9_]{0,24})['»]", re.IGNORECASE)


def humanize_focus_slug_for_ui(slug: str) -> str:
    k = (slug or "").strip().lower()
    if k in _SLUG_TO_RU:
        return _SLUG_TO_RU[k]
    if re.fullmatch(r"[a-z][a-z0-9_]{0,22}", k):
        return "узкая тема дня"
    return (slug or "").strip()


def replace_quoted_en_slugs_for_ru_display(text: str | None) -> str:
    """O5: в RU-тексте не оставляем сырые 'tired' / 'general' в кавычках — подмена на человекочитаемые подписи."""

    def repl(m: re.Match[str]) -> str:
        slug = (m.group(1) or "").strip().lower()
        label = _QUOTED_SERVICE_SLUG_TO_RU.get(slug)
        if label:
            return f"«{label}»"
        return m.group(0)

    raw = (text or "").strip()
    if not raw:
        return ""
    return _QUOTED_EN_SERVICE_SLUG_RE.sub(repl, raw)


def is_discardable_morning_focus(focus: str | None) -> bool:
    t = (focus or "").strip().lower()
    if len(t) < 2:
        return True
    if t in _JUNK_FOCUS:
        return True
    if re.fullmatch(r"[a-z_]{1,20}", t):
        return True
    return False


def is_garbage_ritual_action_cue(line: str | None) -> bool:
    raw = (line or "").strip()
    if not raw:
        return True
    if is_discardable_morning_focus(raw):
        return True
    t = raw.lower()
    if t in _TOPIC_LABELS_NOT_ACTIONS:
        return True
    if len(t) <= 32 and re.fullmatch(r"[ \n_a-z]+", t):
        return True
    return False


def repair_ritual_do_not_enter_line(raw: str | None) -> str:
    t = replace_quoted_en_slugs_for_ru_display(raw)
    if not t:
        return ""
    m = _QUOTED_SLUG.search(t)
    if m:
        slug = (m.group(1) or "").strip().lower()
        topic_junk = _JUNK_FOCUS | {
            "general",
            "overall",
            "dialogue",
            "communication",
            "mixed",
            "none",
        }
        if slug in topic_junk:
            return (
                "Осторожнее, если день начинает скатываться в хаос, резкие реакции и потерю своего ритма — "
                "держи одну линию, не хватайся за всё сразу."
            )
        label = humanize_focus_slug_for_ui(slug)
        return (
            f"Осторожнее с темой «{label}», если она начинает проживаться как хаос, "
            "резкие реакции и потеря своего ритма."
        )
    if re.search(r"general", t, re.IGNORECASE) and re.search(r"лини(ю|я)", t, re.IGNORECASE):
        return (
            "Осторожнее, если день начинает скатываться в хаос, резкие реакции и потерю своего ритма — "
            "держи одну линию, не хватайся за всё сразу."
        )
    return t


def _sanitize_scenario_item(item: Any) -> Any:
    if not isinstance(item, dict):
        return item
    sc = dict(item)
    title = str(sc.get("title") or "").strip()
    slug = str(sc.get("slug") or "").strip()
    if not title and slug:
        sc["title"] = humanize_focus_slug_for_ui(slug)
    return sc


def sanitize_daily_horoscope_payload(payload: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(payload)
    spine = out.get("spine")
    if isinstance(spine, dict):
        s = dict(spine)
        for key in ("day_axis", "first_move", "main_risk", "best_mode", "do_not_enter"):
            v = s.get(key)
            if isinstance(v, str) and v.strip():
                s[key] = replace_quoted_en_slugs_for_ru_display(v)
        dne = s.get("do_not_enter")
        if isinstance(dne, str):
            s["do_not_enter"] = repair_ritual_do_not_enter_line(dne)
        fm = s.get("first_move")
        if isinstance(fm, str) and is_garbage_ritual_action_cue(fm):
            s["first_move"] = ""
        out["spine"] = s
    scenarios = out.get("scenarios")
    if isinstance(scenarios, list):
        out["scenarios"] = [_sanitize_scenario_item(x) for x in scenarios]
    return out


def sanitize_daily_recommendations_payload(rec: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(rec)
    for key in ("what_to_do", "what_to_avoid", "key_focus"):
        v = out.get(key)
        if isinstance(v, str) and v.strip():
            out[key] = replace_quoted_en_slugs_for_ru_display(v)
    wtd = out.get("what_to_do")
    if isinstance(wtd, str) and is_garbage_ritual_action_cue(wtd.strip()):
        out["what_to_do"] = ""
    return out


# --- LLM meta-commentary (must not reach user-facing Today copy) -----------------

_LLM_META_NEEDLES: tuple[str, ...] = (
    "не дублирую",
    "не дублируем",
    "я не дублиру",
    "чтобы экран не перегруж",
    "экран не перегружа",
    "карта и число остаются",
    "не дублирую их",
    "не дублируем их",
    "в сводке и в",
    "чтобы не перегруж",
    # O10: типичные мета-фразы про формат / объём / «не повторяю блоки»
    "чтобы не дублировать",
    "не дублирую информацию",
    "не дублируем информацию",
    "не повторяю блок",
    "не повторяю уже сказанное",
    "как просили в промпте",
    "как указано в задании",
    "в рамках формата ответа",
    "по требованиям к ответу",
    "согласно инструкции для модели",
    "убираю дублирование",
    "исключил дублирование",
    "дублирование с предыдущим",
    "уже было в предыдущем блоке",
    "из предыдущего абзаца",
    "as per the prompt",
    "as instructed, i will not",
    "i won't repeat the",
    "to avoid duplication",
    "avoiding repeating",
    "not repeating the card",
    "not repeating the number",
)


def strip_llm_meta_commentary(text: str | None) -> str:
    """Drop sentences that read as model/system commentary, not day guidance."""
    from todayflow_backend.core.content_openness_policy import strip_meta_editorial_phrases

    raw = (text or "").strip()
    if not raw:
        return ""
    low = raw.lower()
    if not any(n in low for n in _LLM_META_NEEDLES):
        return strip_meta_editorial_phrases(raw)
    parts = re.split(r"(?<=[.!?])\s+", raw)
    kept: list[str] = []
    for p in parts:
        pl = p.strip()
        if not pl:
            continue
        pll = pl.lower()
        if any(n in pll for n in _LLM_META_NEEDLES):
            continue
        kept.append(pl)
    out = " ".join(kept).strip()
    return strip_meta_editorial_phrases(out)


def strip_meta_from_guide_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Apply :func:`strip_llm_meta_commentary` to common guide narrative string fields."""
    out = copy.deepcopy(payload)
    str_keys_top = (
        "headline",
        "subline",
        "energy_line",
        "focus_line",
        "risk_line",
        "risk_detail",
        "header_disclaimer",
        "context_for_next_surfaces",
        "pattern_insight",
        "life_context_insight",
    )
    for k in str_keys_top:
        v = out.get(k)
        if isinstance(v, str):
            out[k] = strip_llm_meta_commentary(v)
    for k in ("do_items", "avoid_items", "support_hooks"):
        xs = out.get(k)
        if isinstance(xs, list):
            out[k] = [strip_llm_meta_commentary(x) if isinstance(x, str) else x for x in xs]
    cm = out.get("core_message")
    if isinstance(cm, str):
        out["core_message"] = strip_llm_meta_commentary(cm)
    elif isinstance(cm, dict):
        c2 = dict(cm)
        for sk in ("headline", "body", "risk", "best_move", "main_text", "message", "first_move", "action_hint"):
            if isinstance(c2.get(sk), str):
                c2[sk] = strip_llm_meta_commentary(str(c2[sk]))
        out["core_message"] = c2
    ao = out.get("action_options")
    if isinstance(ao, list):
        new_ao: list[Any] = []
        for it in ao:
            if isinstance(it, str):
                new_ao.append(strip_llm_meta_commentary(it))
            elif isinstance(it, dict):
                d2 = dict(it)
                if isinstance(d2.get("title"), str):
                    d2["title"] = strip_llm_meta_commentary(str(d2["title"]))
                if isinstance(d2.get("reason"), str):
                    d2["reason"] = strip_llm_meta_commentary(str(d2["reason"]))
                new_ao.append(d2)
            else:
                new_ao.append(it)
        out["action_options"] = new_ao
    st = out.get("sphere_triad")
    if isinstance(st, list):
        new_st: list[Any] = []
        for it in st:
            if isinstance(it, dict):
                d2 = dict(it)
                if isinstance(d2.get("line"), str):
                    d2["line"] = strip_llm_meta_commentary(str(d2["line"]))
                new_st.append(d2)
            else:
                new_st.append(it)
        out["sphere_triad"] = new_st
    layers = out.get("why_astrological_layers")
    if isinstance(layers, list):
        new_layers: list[Any] = []
        for it in layers:
            if isinstance(it, dict):
                d2 = dict(it)
                if isinstance(d2.get("detail"), str):
                    d2["detail"] = strip_llm_meta_commentary(str(d2["detail"]))
                if isinstance(d2.get("anchor"), str):
                    d2["anchor"] = strip_llm_meta_commentary(str(d2["anchor"]))
                new_layers.append(d2)
            else:
                new_layers.append(it)
        out["why_astrological_layers"] = new_layers
    return out
