"""Tarot Interpretation Engine — deterministic Context Pack + gates.

Canon: docs/tarot/TAROT_INTERPRETATION_ENGINE_V1.md

Prose author is LLM (tarot_interpretation_llm_v1). This module only:
- resolves cards,
- builds factual context pack,
- blocks unresolved,
- provides thin emergency fallback.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any, TypedDict

from todayflow_backend.core import models
from todayflow_backend.data import astrology as astrology_ref

logger = logging.getLogger(__name__)

SYNTHESIS_MODE_LLM = "tarot_llm_v1"
SYNTHESIS_MODE_FALLBACK = "tarot_fallback_v1"
SYNTHESIS_MODE_BLOCKED = "unresolved_blocked"
STATUS_OK = "ok"
STATUS_UNRESOLVED = "unresolved_cards"
STATUS_LLM_UNAVAILABLE = "llm_unavailable"

CHOICE_SPREAD_IDS = frozenset({"guidance_choice_two", "choice"})

# Theme ranges for majors — facts for LLM, not finished user paragraphs.
_MAJOR_THEMES: dict[int, dict[str, Any]] = {
    0: {
        "name": "Шут",
        "up": ["новый шаг", "открытость неизвестному", "эксперимент", "свобода от старого сценария"],
        "rev": ["импульсивность", "отсутствие подготовки", "прыжок ради снятия тревоги"],
    },
    1: {"name": "Маг", "up": ["ресурсы в руках", "фокус", "действие через волю"], "rev": ["рассеянность", "сомнение в влиянии", "манипуляция"]},
    2: {"name": "Верховная Жрица", "up": ["внутреннее знание", "пауза", "невидимое"], "rev": ["недоверие к интуиции", "закрытость", "игнор сигнала"]},
    3: {"name": "Императрица", "up": ["опора", "забота", "рост", "телесность"], "rev": ["истощение", "отдавать больше, чем получать"]},
    4: {"name": "Император", "up": ["структура", "границы", "ответственность"], "rev": ["жёсткость", "контроль вместо диалога"]},
    5: {"name": "Иерофант", "up": ["ценности", "традиции", "свои правила"], "rev": ["чужие «как надо»", "догма"]},
    6: {"name": "Влюблённые", "up": ["честный выбор сердца", "союз", "согласование"], "rev": ["колебание", "страх назвать желание"]},
    7: {"name": "Колесница", "up": ["движение вперёд", "направление", "воля"], "rev": ["спешка", "гонка без паузы"]},
    8: {"name": "Сила", "up": ["мягкая устойчивость", "терпение", "владение собой"], "rev": ["срыв", "сомнение в выдержке"]},
    9: {"name": "Отшельник", "up": ["уединение", "своя правда", "тишина"], "rev": ["изоляция от правды", "уход от контакта"]},
    10: {"name": "Колесо Фортуны", "up": ["сдвиг цикла", "перемена фазы"], "rev": ["застревание", "страх, что ничего не изменится"]},
    11: {"name": "Справедливость", "up": ["честный взгляд", "последствия", "баланс"], "rev": ["холодная правота", "самооправдание"]},
    12: {"name": "Повешенный", "up": ["другой угол", "пауза ради ясности"], "rev": ["ожидание, что решат другие", "застревание"]},
    13: {"name": "Смерть", "up": ["завершение этапа", "освобождение формы"], "rev": ["цепляние за старое", "страх пустоты"]},
    14: {"name": "Умеренность", "up": ["баланс", "ровный темп"], "rev": ["крайности", "качели всё или ничего"]},
    15: {
        "name": "Дьявол",
        "up": ["зависимость", "привязанность", "страх потери", "привычный сценарий", "скрытая выгода оставаться"],
        "rev": ["петля видна", "возможен первый шаг к выходу"],
    },
    16: {"name": "Башня", "up": ["трещина в старом", "внезапная правда"], "rev": ["страх перемены сильнее самой перемены"]},
    17: {"name": "Звезда", "up": ["надежда", "восстановление", "тонкий ориентир"], "rev": ["сомнение в восстановлении"]},
    18: {
        "name": "Луна",
        "up": ["туман", "страх", "неясность", "нужно назвать то, что пугает"],
        "rev": ["туман рассеивается", "скрытое становится заметнее", "риск принять желание за факт"],
    },
    19: {"name": "Солнце", "up": ["ясность", "видимость", "тепло"], "rev": ["сдержанная ясность", "страх уязвимости"]},
    20: {"name": "Суд", "up": ["итог", "зов", "ответ на назревшее"], "rev": ["откладывание разговора с собой"]},
    21: {"name": "Мир", "up": ["завершение дуги", "принятие итога"], "rev": ["формально закрыто, внутри незавершённость"]},
}

_SUIT_THEMES: dict[str, str] = {
    "wands": "инициатива, воля, действие, импульс; в тени — перегорание и спешка",
    "cups": "чувства, близость, эмоциональная опора; в тени — идеализация и закрытость",
    "swords": "мышление, конфликт, решение, ясность, тревога, слова и границы",
    "pentacles": "материальная опора, труд, стабильность, практический результат; в тени — застревание в безопасности",
}

_POSITION_ROLE_BY_ID: dict[str, str] = {
    "a_gives": "gain",
    "b_gives": "gain",
    "option_a": "gain",
    "option_b": "gain",
    "a_risk": "risk",
    "b_risk": "risk",
    "risk": "risk",
    "obstacle": "risk",
    "fear": "risk",
    "block": "risk",
    "weights": "weights",
    "core": "weights",
    "you": "weights",
    "best_step": "step",
    "next_step": "step",
    "advice": "step",
    "step": "step",
    "future": "step",
    "outcome": "step",
}

_ROLE_INSTRUCTION: dict[str, str] = {
    "gain": "Позиция про то, что даёт путь / ресурс / облегчение — не совет «сделай так».",
    "risk": "Позиция про конкретную опасность выбранного пути — не совет и не мораль.",
    "weights": "Позиция про то, что нельзя игнорировать при решении.",
    "step": "Позиция про действие в реальности — не описание настроения.",
    "neutral": "Читай через prompt позиции.",
}


class UnresolvedCard(TypedDict):
    card_id: int
    position_id: str
    reason: str


@lru_cache(maxsize=1)
def _deck_by_id() -> dict[int, dict[str, Any]]:
    return {int(c["id"]): c for c in astrology_ref.tarot_full_deck()}


def position_role(position_id: str | None) -> str:
    pid = (position_id or "").strip().lower()
    if pid in _POSITION_ROLE_BY_ID:
        return _POSITION_ROLE_BY_ID[pid]
    if any(x in pid for x in ("risk", "fear", "obstacle", "block", "caution")):
        return "risk"
    if any(x in pid for x in ("give", "gain", "resource", "open", "benefit")):
        return "gain"
    if any(x in pid for x in ("step", "advice", "next", "action")):
        return "step"
    if any(x in pid for x in ("weight", "core", "consider", "important")):
        return "weights"
    return "neutral"


def spread_kind(spread_id: str | None) -> str:
    sid = (spread_id or "").strip().lower()
    if sid in CHOICE_SPREAD_IDS:
        return "choice"
    if sid in {"one_card", "card_of_day", "daily"}:
        return "one_card"
    if "relationship" in sid or "love" in sid:
        return "relationship"
    return "general"


def collect_unresolved(cards: list[models.TarotSpreadCard]) -> list[UnresolvedCard]:
    unresolved: list[UnresolvedCard] = []
    deck = _deck_by_id()
    for card in cards:
        pid = card.position.id if card.position else ""
        row = deck.get(int(card.card.id))
        if not row or not str(row.get("name_ru") or "").strip():
            unresolved.append(
                {
                    "card_id": int(card.card.id),
                    "position_id": pid,
                    "reason": "card_id_not_in_full_deck_or_missing_name_ru",
                }
            )
            logger.error(
                "tarot_mapping_error card_id=%s position_id=%s reason=unresolved",
                card.card.id,
                pid,
            )
    return unresolved


def _meaning_range(card_id: int, row: dict[str, Any]) -> dict[str, Any]:
    if int(card_id) in _MAJOR_THEMES:
        major = _MAJOR_THEMES[int(card_id)]
        return {
            "upright_themes": list(major["up"]),
            "reversed_themes": list(major["rev"]),
            "catalog_upright": str(row.get("upright") or ""),
            "catalog_reversed": str(row.get("reversed") or ""),
            "keywords": list(row.get("keywords") or []),
        }
    return {
        "upright_themes": list(row.get("keywords") or [])[:6],
        "reversed_themes": list(row.get("keywords") or [])[:6],
        "catalog_upright": str(row.get("upright") or ""),
        "catalog_reversed": str(row.get("reversed") or ""),
        "keywords": list(row.get("keywords") or []),
    }


def _display_name(card_id: int, orientation: str, row: dict[str, Any]) -> str:
    if int(card_id) in _MAJOR_THEMES:
        name = str(_MAJOR_THEMES[int(card_id)]["name"])
    else:
        name = str(row.get("name_ru") or "").strip()
    if (orientation or "").strip().lower() == "reversed":
        return f"{name} (перевёрнутый)"
    return name


def build_card_insights(cards: list[models.TarotSpreadCard]) -> list[models.TarotCardInsight] | None:
    """Insights for UI strip — name + short theme line from pack facts (not LLM prose)."""
    if collect_unresolved(cards):
        return None
    deck = _deck_by_id()
    insights: list[models.TarotCardInsight] = []
    for card in cards:
        pid = card.position.id if card.position else ""
        label = (card.position.title if card.position and card.position.title else pid) or "Позиция"
        row = deck[int(card.card.id)]
        orient = (card.orientation or "upright").strip().lower()
        name = _display_name(card.card.id, orient, row)
        rng = _meaning_range(card.card.id, row)
        themes = rng["reversed_themes"] if orient == "reversed" else rng["upright_themes"]
        line = ", ".join(str(t) for t in themes[:4]) if themes else str(rng.get("catalog_upright") or "")[:120]
        insights.append(
            models.TarotCardInsight(
                position_label=label.strip(),
                card_name_ru=name,
                card_id=int(card.card.id),
                orientation="reversed" if orient == "reversed" else "upright",
                line=line,
            )
        )
    return insights


def profile_relevant_fragment(experience_slice: dict | None) -> tuple[dict[str, str], str | None]:
    """One short relevant profile field for the pack — never a full paste paragraph."""
    if not isinstance(experience_slice, dict):
        return {}, None
    for key in ("decision_style", "identity_line", "motivation", "communication_style"):
        raw = experience_slice.get(key)
        if isinstance(raw, str) and raw.strip():
            text = raw.strip()[:220]
            return {key: text}, text
    return {}, None


def build_context_pack(
    spread: models.TarotSpreadResult,
    *,
    question: str | None = None,
    concern_domain: str | None = None,
    experience_slice: dict | None = None,
) -> dict[str, Any] | None:
    """Deterministic facts for LLM. None if unresolved cards."""
    cards = spread.cards or []
    unresolved = collect_unresolved(cards)
    if unresolved:
        return None

    deck = _deck_by_id()
    kind = spread_kind(spread.spread_id)
    profile_frag, lens = profile_relevant_fragment(experience_slice)

    pack_cards: list[dict[str, Any]] = []
    for idx, card in enumerate(cards):
        row = deck[int(card.card.id)]
        pid = (card.position.id if card.position else "") or ""
        role = position_role(pid)
        orient = (card.orientation or "upright").strip().lower()
        suit = str(row.get("suit") or "") or None
        card_type = str(row.get("type") or ("major" if int(card.card.id) <= 21 else "minor"))
        neighbors: list[str] = []
        if idx > 0:
            prev = cards[idx - 1]
            neighbors.append(_display_name(prev.card.id, prev.orientation, deck[int(prev.card.id)]))
        if idx + 1 < len(cards):
            nxt = cards[idx + 1]
            neighbors.append(_display_name(nxt.card.id, nxt.orientation, deck[int(nxt.card.id)]))

        pack_cards.append(
            {
                "card_id": int(card.card.id),
                "name_ru": _display_name(card.card.id, orient, row),
                "name_en": str(row.get("name") or card.card.name or ""),
                "arcana": card_type,
                "suit": suit,
                "suit_themes": _SUIT_THEMES.get((suit or "").lower()) if suit else None,
                "orientation": "reversed" if orient == "reversed" else "upright",
                "position_id": pid,
                "position_title": (card.position.title if card.position else "") or pid,
                "position_prompt": (card.position.prompt if card.position else None),
                "position_role": role,
                "position_role_instruction": _ROLE_INSTRUCTION.get(role, _ROLE_INSTRUCTION["neutral"]),
                "meaning_range": _meaning_range(card.card.id, row),
                "neighbors": neighbors,
            }
        )

    return {
        "question": (question or "").strip(),
        "spread_id": spread.spread_id,
        "spread_title": spread.title,
        "spread_kind": kind,
        "concern_domain": (concern_domain or "").strip(),
        "profile_relevant": profile_frag,
        "profile_lens": lens,
        "cards": pack_cards,
        "response_shape": {
            "blocks": ["symbols_overview", "question_story", "direct_answer", "next_step"],
            "choice_compare": kind == "choice",
            "voice": "person-not-system",
            "locale": "ru",
        },
    }


def technical_fallback_reading(*, unresolved: list[UnresolvedCard]) -> models.TarotSpreadReading:
    n = len(unresolved)
    ids = ", ".join(str(u["card_id"]) for u in unresolved[:6]) or "—"
    meaning = (
        "Расклад собран, но часть карт не удалось надёжно распознать для интерпретации. "
        "Полноценный ответ сейчас не публикуем — лучше открыть карты ещё раз или пересобрать расклад."
    )
    return models.TarotSpreadReading(
        meaning=meaning,
        synthesis_why=(
            f"Технический сбой сопоставления карт ({n}): id {ids}. "
            "Это не значение расклада — narrative заблокирован."
        ),
        insight_holding=None,
        insight_shifting=None,
        insight_attention=None,
        today_suggestion="Открой расклад снова или выбери карты заново.",
        follow_up_prompt="Что сделать дальше?",
        follow_up_chips=[
            models.TarotFollowUpChip(id="redraw", label="Пересобрать расклад"),
            models.TarotFollowUpChip(id="retry", label="Открыть снова"),
        ],
        card_insights=[],
        next_step="Открой расклад снова или выбери карты заново.",
        actions_today=["Открой расклад снова или выбери карты заново."],
    )


def thin_fallback_from_pack(pack: dict[str, Any]) -> dict[str, str]:
    """Emergency prose when LLM unavailable — factual, not fake tarot voice."""
    q = pack.get("question") or "твой вопрос"
    names = [c.get("name_ru") for c in pack.get("cards") or [] if c.get("name_ru")]
    named = ", ".join(names[:4]) if names else "карты расклада"
    symbols = (
        f"В раскладе: {named}. "
        "Каждая карта несёт свой диапазон смыслов с учётом позиции и ориентации — "
        "полный живой разбор сейчас недоступен."
    )
    story = (
        f"По вопросу «{q}» карты задают рамку через позиции расклада. "
        "Без языковой модели нельзя честно собрать единую картину — только факты колоды."
    )
    answer = (
        f"Пока нет полного интерпретационного слоя: опирайся на вопрос «{q}» "
        "и на то, какая позиция откликается сильнее, без категоричных выводов."
    )
    step = "Запиши одним предложением, что в раскладе отозвалось сильнее всего — и один маленький шаг на сегодня."
    return {
        "symbols_overview": symbols,
        "question_story": story,
        "direct_answer": answer,
        "next_step": step,
    }


def reading_from_interpretation(
    *,
    interpretation: dict[str, str],
    card_insights: list[models.TarotCardInsight],
    follow_up_chips: list[models.TarotFollowUpChip],
    follow_up_prompt: str,
    profile_lens: str | None,
    profile_lens_applied: bool,
    choice_story: dict[str, Any] | None = None,
) -> models.TarotSpreadReading:
    direct = interpretation.get("direct_answer") or ""
    story = interpretation.get("question_story") or ""
    symbols = interpretation.get("symbols_overview") or ""
    step = interpretation.get("next_step") or ""
    # Keep synthesis_why = question story; stash symbols on reading via meta.
    reading = models.TarotSpreadReading(
        meaning=direct,
        synthesis_why=story,
        insight_holding=interpretation.get("holding") or None,
        insight_shifting=interpretation.get("shifting") or None,
        insight_attention=None,  # never paste profile here
        today_suggestion=step,
        follow_up_prompt=follow_up_prompt,
        follow_up_chips=follow_up_chips,
        card_insights=card_insights,
        next_step=step,
        actions_today=[step] if step else [],
        profile_lens=profile_lens,
        profile_lens_applied=profile_lens_applied,
    )
    reading.__dict__["_symbols_overview"] = symbols
    if choice_story:
        reading.__dict__["_choice_story"] = choice_story
    return reading
