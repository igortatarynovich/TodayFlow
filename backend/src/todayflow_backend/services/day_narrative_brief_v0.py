"""Детерминированная «опора дня» до LLM: связка ритуала, оси foundation и intent (RU/EN)."""

from __future__ import annotations

import re
from typing import Any

from todayflow_backend.services.day_logic_shared_v0 import (
    clip_day_logic_text as _clip,
    foundation_spine_dict,
    fusion_energy_score_int,
    ritual_core_fields,
    spine_text_fields,
)

# id чек-ина настроения (ритуал) → человекочитаемо для RU-копирайта «Опора дня»
_MOOD_ID_RU: dict[str, str] = {
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

# head_topic из честного шага / фокуса → RU (не сырой slug вроде general/body)
_HEAD_TOPIC_SLUG_RU: dict[str, str] = {
    "general": "общий фон дня",
    "body": "тело и энергия",
    "money": "деньги",
    "dialogue": "общение и контакт",
    "family": "семья и дом",
    "career": "работа и дела",
    "love": "близость и отношения",
}


def _display_mood_for_brief(mood: str, *, en: bool) -> str:
    t = (mood or "").strip()
    if not t:
        return t
    if en:
        return t
    low = t.lower()
    return _MOOD_ID_RU.get(low, t)


def _display_head_topic_for_brief(topic: str, *, en: bool) -> str:
    t = (topic or "").strip()
    if not t:
        return t
    if en:
        return t
    low = t.lower()
    return _HEAD_TOPIC_SLUG_RU.get(low, t)


def build_day_narrative_brief_v0(
    *,
    foundation: dict[str, Any] | None,
    ritual: dict[str, Any] | None,
    fusion_scores: dict[str, Any] | None,
    intent_slice: dict[str, Any] | None,
    locale: str,
) -> dict[str, Any]:
    """
    Возвращает объект для `payload.day_engine_brief` и для user JSON guide (`day_engine_brief`).
    Не вызывает LLM. Паритет: те же данные на web/iOS из одного API.
    """
    en = (locale or "").strip().lower().startswith("en")
    spine = foundation_spine_dict(foundation)
    sf = spine_text_fields(spine)
    axis = sf["axis"]
    first_move = sf["first_move"]
    main_risk = sf["main_risk"]
    dne = sf["do_not_enter"]

    rc = ritual_core_fields(ritual)
    card = rc["tarot_name_ru"]
    tid = rc["tarot_main_id"]
    num = rc["numerology_value"]
    mood = _display_mood_for_brief(rc["mood"], en=en)
    head_topic = _display_head_topic_for_brief(rc["head_topic"], en=en)

    en_score = fusion_energy_score_int(fusion_scores)

    intent_line = ""
    if isinstance(intent_slice, dict):
        intent_line = str(intent_slice.get("what_matters_line") or "").strip()

    parts: list[str] = []
    if axis:
        parts.append(_clip(axis, 220) if not en else _clip(axis, 240))
    if card:
        parts.append(
            _clip(
                f"Карта дня — «{card}»: символ из ритуала, который мягко окрашивает сегодняшние шаги."
                if not en
                else f"Day card — «{card}»: the ritual symbol that quietly colors today’s steps.",
                320,
            )
        )
    elif isinstance(tid, int) and tid > 0:
        parts.append(
            "Карта дня выбрана в ритуале — смысл дня строится вокруг этого символа."
            if not en
            else "You picked a day card in the ritual — the day lines up around that symbol."
        )
    if num:
        parts.append(
            _clip(
                f"Число дня — {num}: ритм коротких циклов; десять параллельных входов сегодня скорее шумят, чем помогают."
                if not en
                else f"Day number — {num}: short cycles; ten parallel pushes usually add noise.",
                260,
            )
        )
    if mood:
        parts.append(
            _clip(
                f"Настроение в чек-ине: «{mood}» — тон дня честнее держать рядом с этим, без самообмана."
                if not en
                else f"Mood from check-in: «{mood}» — the day’s tone is clearer when it stays honest.",
                220,
            )
        )
    if head_topic:
        parts.append(
            _clip(
                f"Тема «в голове»: {head_topic} — она уже намекает, куда уйдёт главный вес дня."
                if not en
                else f"Head topic: {head_topic} — it already hints where the day’s weight will land.",
                200,
            )
        )
    if intent_line and (not head_topic or intent_line.lower() != head_topic.lower()):
        parts.append(_clip(intent_line, 360))

    if not parts:
        parts.append(
            "День проще держать вокруг одной ясной оси и одного завершённого шага — без лишнего героизма."
            if not en
            else "The day is easier around one clear spine and one finished step — no extra heroics."
        )

    anchor = " ".join(parts)
    anchor = _clip(re.sub(r"\s+", " ", anchor), 520)

    do_hint = _clip(
        first_move
        or axis
        or ("One clear step today usually beats a long list." if en else "Один ясный шаг сегодня обычно стоит дороже длинного списка."),
        280,
    )
    avoid_hint = _clip(
        dne
        or main_risk
        or (
            "New promises without time tend to turn into noise."
            if en
            else "Новые обещания без времени сегодня легко превращаются в шум."
        ),
        280,
    )

    if 40 <= en_score <= 65:
        tempo = (
            "Energy around mid — a steady pace fits better than sharp pivots."
            if en
            else "Ресурс около среднего — спокойный темп подходит лучше резких разворотов."
        )
    elif en_score < 40:
        tempo = (
            "Energy is below mid — a shorter must-do list leaves more room to breathe."
            if en
            else "Ресурс ниже середины — короткий список «надо» оставляет больше воздуха."
        )
    else:
        tempo = (
            "Energy is above mid — movement is fine if clarity stays ahead of speed."
            if en
            else "Ресурс выше середины — движение уместно, пока ясность остаётся впереди скорости."
        )

    return {
        "contract_version": "day_narrative_brief_v0",
        "anchor_summary": anchor,
        "thread_card": _clip(card, 120) if card else None,
        "thread_number": num[:24] if num else None,
        "thread_mood": _clip(mood, 80) if mood else None,
        "thread_head_topic": _clip(head_topic, 120) if head_topic else None,
        "do_hint": do_hint,
        "avoid_hint": avoid_hint,
        "tempo_hint": tempo,
        "energy_score_hint": en_score,
    }


def slim_day_engine_brief_for_story_llm(
    brief: dict[str, Any] | None,
    *,
    ritual_has_card: bool,
    ritual_has_number: bool,
) -> dict[str, Any]:
    """Drop card/number prose from brief when ritual_context already carries them (anti double-weight)."""
    if not isinstance(brief, dict):
        return {}
    out = dict(brief)
    if ritual_has_card:
        out["thread_card"] = None
    if ritual_has_number:
        out["thread_number"] = None
    anchor = str(out.get("anchor_summary") or "")
    if ritual_has_card:
        anchor = re.sub(
            r"(Карта дня[^.]*\.|Day card[^.]*\.|You picked a day card[^.]*\.)\s*",
            "",
            anchor,
            flags=re.I,
        )
    if ritual_has_number:
        anchor = re.sub(
            r"(Число дня[^.]*\.|Day number[^.]*\.)\s*",
            "",
            anchor,
            flags=re.I,
        )
    out["anchor_summary"] = _clip(re.sub(r"\s+", " ", anchor).strip(), 520)
    out["symbol_source"] = "ritual_context_only"
    return out
