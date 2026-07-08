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
                f"Карта дня — «{card}»: символ, который ты выбрала в ритуале; держи его в голове при шагах дня."
                if not en
                else f"Day card — «{card}»: the symbol you picked in the ritual; keep it in mind for your steps.",
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
                f"Число дня — {num}: задаёт ритм «коротких циклов»; не распыляйся на десять параллельных входов."
                if not en
                else f"Day number — {num}: short cycles; avoid ten parallel pushes.",
                260,
            )
        )
    if mood:
        parts.append(
            _clip(
                f"Настроение в чек-ине: «{mood}» — тон дня лучше подстроить под это, без самообмана."
                if not en
                else f"Mood from check-in: «{mood}» — keep the day’s tone aligned, without pretending.",
                220,
            )
        )
    if head_topic:
        parts.append(
            _clip(
                f"Тема «в голове»: {head_topic} — учитывай при выборе приоритетного шага."
                if not en
                else f"Head topic: {head_topic} — weigh it when you pick your main step.",
                200,
            )
        )
    if intent_line and (not head_topic or intent_line.lower() != head_topic.lower()):
        parts.append(_clip(intent_line, 360))

    if not parts:
        parts.append(
            "Сегодня опирайся на ось дня из гороскопа и на один завершённый шаг — без лишнего героизма."
            if not en
            else "Lean on the day’s spine from the forecast and one finished step — no extra heroics."
        )

    anchor = " ".join(parts)
    anchor = _clip(re.sub(r"\s+", " ", anchor), 520)

    do_hint = _clip(first_move or axis or ("One clear step today." if en else "Один ясный шаг сегодня."), 280)
    avoid_hint = _clip(dne or main_risk or ("Do not add new promises without time." if en else "Не брать новые обещания без времени."), 280)

    if 40 <= en_score <= 65:
        tempo = "Energy around mid — steady pace, no sharp pivots." if en else "Ресурс около среднего — темп спокойный, без резких разворотов."
    elif en_score < 40:
        tempo = "Energy is below mid — shorten the must-do list to one main item." if en else "Ресурс ниже середины — сократи список «надо» и оставь одно главное."
    else:
        tempo = "Energy is above mid — you can move, but do not trade clarity for speed." if en else "Ресурс выше середины — можно двигаться, но не разменивай ясность на скорость."

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
