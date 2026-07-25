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

# Theme ranges for majors — facts for LLM (central / light / shadow), not user paragraphs.
_MAJOR_THEMES: dict[int, dict[str, Any]] = {
    0: {
        "name": "Шут",
        "central": "новый шаг в неизвестное",
        "light": ["открытость опыту", "эксперимент", "свобода от старого сценария", "лёгкость старта"],
        "shadow": ["импульсивность", "отсутствие подготовки", "прыжок ради снятия тревоги"],
        "up": ["новый шаг", "открытость неизвестному", "эксперимент", "свобода от старого сценария"],
        "rev": ["импульсивность", "отсутствие подготовки", "прыжок ради снятия тревоги"],
    },
    1: {"name": "Маг", "central": "сбор ресурсов в одно действие", "light": ["фокус", "воля", "инструменты в руках"], "shadow": ["рассеянность", "манипуляция", "сомнение в влиянии"], "up": ["ресурсы в руках", "фокус", "действие через волю"], "rev": ["рассеянность", "сомнение в влиянии", "манипуляция"]},
    2: {"name": "Верховная Жрица", "central": "знание под поверхностью", "light": ["интуиция", "пауза", "тишина"], "shadow": ["закрытость", "недоверие к сигналу", "молчание вместо ясности"], "up": ["внутреннее знание", "пауза", "невидимое"], "rev": ["недоверие к интуиции", "закрытость", "игнор сигнала"]},
    3: {"name": "Императрица", "central": "опора и рост", "light": ["забота", "плодородие", "телесность"], "shadow": ["истощение", "перегруз заботой"], "up": ["опора", "забота", "рост", "телесность"], "rev": ["истощение", "отдавать больше, чем получать"]},
    4: {"name": "Император", "central": "структура и границы", "light": ["порядок", "ответственность", "ясные правила"], "shadow": ["жёсткость", "контроль вместо диалога"], "up": ["структура", "границы", "ответственность"], "rev": ["жёсткость", "контроль вместо диалога"]},
    5: {"name": "Иерофант", "central": "ценности и правила", "light": ["свои принципы", "учение", "опора на смысл"], "shadow": ["догма", "чужие «как надо»"], "up": ["ценности", "традиции", "свои правила"], "rev": ["чужие «как надо»", "догма"]},
    6: {"name": "Влюблённые", "central": "честный выбор сердца", "light": ["союз", "согласование", "назвать желание"], "shadow": ["колебание", "страх выбора"], "up": ["честный выбор сердца", "союз", "согласование"], "rev": ["колебание", "страх назвать желание"]},
    7: {"name": "Колесница", "central": "движение к цели", "light": ["направление", "воля", "прогресс"], "shadow": ["спешка", "гонка без паузы"], "up": ["движение вперёд", "направление", "воля"], "rev": ["спешка", "гонка без паузы"]},
    8: {"name": "Сила", "central": "мягкая устойчивость", "light": ["терпение", "владение собой", "мужество без давления"], "shadow": ["срыв", "сомнение в выдержке"], "up": ["мягкая устойчивость", "терпение", "владение собой"], "rev": ["срыв", "сомнение в выдержке"]},
    9: {"name": "Отшельник", "central": "своя правда в тишине", "light": ["уединение", "ясность наедине с собой"], "shadow": ["изоляция от правды", "уход от контакта"], "up": ["уединение", "своя правда", "тишина"], "rev": ["изоляция от правды", "уход от контакта"]},
    10: {"name": "Колесо Фортуны", "central": "сдвиг цикла", "light": ["перемена фазы", "окно возможности"], "shadow": ["застревание", "страх, что ничего не изменится"], "up": ["сдвиг цикла", "перемена фазы"], "rev": ["застревание", "страх, что ничего не изменится"]},
    11: {"name": "Справедливость", "central": "честный учёт последствий", "light": ["баланс", "ясность фактов"], "shadow": ["холодная правота", "самооправдание"], "up": ["честный взгляд", "последствия", "баланс"], "rev": ["холодная правота", "самооправдание"]},
    12: {"name": "Повешенный", "central": "другой угол зрения", "light": ["пауза ради ясности", "смена перспективы"], "shadow": ["ожидание, что решат другие", "застревание"], "up": ["другой угол", "пауза ради ясности"], "rev": ["ожидание, что решат другие", "застревание"]},
    13: {"name": "Смерть", "central": "завершение формы", "light": ["освобождение", "переход"], "shadow": ["цепляние за старое", "страх пустоты"], "up": ["завершение этапа", "освобождение формы"], "rev": ["цепляние за старое", "страх пустоты"]},
    14: {"name": "Умеренность", "central": "смешивание без крайностей", "light": ["баланс", "ровный темп"], "shadow": ["качели всё или ничего"], "up": ["баланс", "ровный темп"], "rev": ["крайности", "качели всё или ничего"]},
    15: {
        "name": "Дьявол",
        "central": "привязанность и привычный сценарий",
        "light": ["узнать петлю", "увидеть скрытую выгоду"],
        "shadow": ["зависимость", "страх потери", "сложно заметить удержание"],
        "up": ["зависимость", "привязанность", "страх потери", "привычный сценарий", "скрытая выгода оставаться"],
        "rev": ["петля видна", "возможен первый шаг к выходу"],
    },
    16: {"name": "Башня", "central": "трещина в мнимой надёжности", "light": ["место для правды", "освобождение"], "shadow": ["страх перемены", "шок"], "up": ["трещина в старом", "внезапная правда"], "rev": ["страх перемены сильнее самой перемены"]},
    17: {"name": "Звезда", "central": "тонкая надежда после усталости", "light": ["восстановление", "ориентир"], "shadow": ["сомнение в восстановлении"], "up": ["надежда", "восстановление", "тонкий ориентир"], "rev": ["сомнение в восстановлении"]},
    18: {
        "name": "Луна",
        "central": "туман и неясность",
        "light": ["назвать страх", "заметить скрытое"],
        "shadow": ["додумывание", "принять желание за факт"],
        "up": ["туман", "страх", "неясность", "нужно назвать то, что пугает"],
        "rev": ["туман рассеивается", "скрытое становится заметнее", "риск принять желание за факт"],
    },
    19: {"name": "Солнце", "central": "ясность и видимость", "light": ["тепло", "простота правды"], "shadow": ["страх уязвимости", "сдержанная радость"], "up": ["ясность", "видимость", "тепло"], "rev": ["сдержанная ясность", "страх уязвимости"]},
    20: {"name": "Суд", "central": "зов к итогу", "light": ["ответить на назревшее", "подвести черту"], "shadow": ["откладывание разговора с собой"], "up": ["итог", "зов", "ответ на назревшее"], "rev": ["откладывание разговора с собой"]},
    21: {"name": "Мир", "central": "завершение дуги", "light": ["принятие итога", "целостность"], "shadow": ["формально закрыто, внутри незавершённость"], "up": ["завершение дуги", "принятие итога"], "rev": ["формально закрыто, внутри незавершённость"]},
}

_SUIT_THEMES: dict[str, dict[str, Any]] = {
    "wands": {
        "summary": "инициатива, воля, действие, импульс",
        "light": ["старт", "энергия", "защита своего направления"],
        "shadow": ["перегорание", "спешка", "разброс сил"],
        "element": "fire",
    },
    "cups": {
        "summary": "чувства, близость, эмоциональная опора",
        "light": ["контакт", "эмпатия", "честное чувство"],
        "shadow": ["идеализация", "закрытость", "размытые границы"],
        "element": "water",
    },
    "swords": {
        "summary": "мышление, конфликт, решение, ясность, тревога, слова и границы",
        "light": ["ясная формулировка", "границы", "решение на фактах"],
        "shadow": ["ментальный шум", "резкость", "прокрутки"],
        "element": "air",
    },
    "pentacles": {
        "summary": "материальная опора, труд, стабильность, практический результат",
        "light": ["база", "навык", "приземлённый шаг"],
        "shadow": ["застревание в безопасности", "откладывание ради комфорта"],
        "element": "earth",
    },
}

_ELEMENT_RU = {"fire": "огонь", "water": "вода", "air": "воздух", "earth": "земля"}

_DOMAIN_QUESTION_LENS: dict[str, str] = {
    "work": "читай через роль, условия, границы, стабильность и темп решения о работе",
    "work_change": "читай через выбор уйти/остаться, критерии и страх ошибки",
    "relationships": "читай через близость, границы, честность желания и динамику двоих",
    "money": "читай через риск, опору, цену выбора и спокойствие вокруг денег",
    "decision": "читай через критерии выбора, цену каждого пути и готовность действовать",
    "conflict": "читай через то, что защищают стороны, и что можно назвать без обвинения",
    "family": "читай через границы, долг и мягкий контакт",
    "growth": "читай через маленький честный шаг роста, не большой смысл",
    "inner_state": "читай через состояние, ресурс и то, что сейчас требует опоры",
    "general": "читай через конкретный вопрос человека, не общий прогноз",
}

_PROFILE_KEYS_BY_DOMAIN: dict[str, tuple[str, ...]] = {
    "work": ("decision_style", "motivation", "helps"),
    "work_change": ("decision_style", "motivation", "helps"),
    "relationships": ("communication_style", "conflict_style", "decision_style"),
    "money": ("decision_style", "motivation", "helps"),
    "decision": ("decision_style", "motivation", "conflict_style"),
    "conflict": ("conflict_style", "communication_style", "decision_style"),
    "family": ("communication_style", "decision_style", "helps"),
    "growth": ("motivation", "identity_line", "decision_style"),
    "inner_state": ("energy_source", "helps", "decision_style"),
    "general": ("decision_style", "motivation", "communication_style"),
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


def infer_question_domain(question: str | None, concern_domain: str | None) -> str:
    domain = (concern_domain or "").strip().lower()
    if domain in _DOMAIN_QUESTION_LENS:
        return domain
    text = (question or "").strip().lower()
    if any(w in text for w in ("работ", "карьер", "увольн", "начальник", "коллег")):
        if any(w in text for w in ("менять", "сменить", "уйти", "остаться", "проясн")):
            return "work_change"
        return "work"
    if any(w in text for w in ("отношен", "партнёр", "партнер", "любов", "бывш")):
        return "relationships"
    if any(w in text for w in ("деньг", "доход", "финанс", "трат")):
        return "money"
    if any(w in text for w in ("выбор", "решени", "стоит ли", " или ")):
        return "decision"
    if any(w in text for w in ("конфликт", "ссор", "спор")):
        return "conflict"
    if any(w in text for w in ("семь", "родител", "ребён", "ребен")):
        return "family"
    if any(w in text for w in ("тревог", "апати", "настроен", "устала", "устал")):
        return "inner_state"
    return "general"


def _meaning_range(card_id: int, row: dict[str, Any]) -> dict[str, Any]:
    corr = row.get("correspondences") if isinstance(row.get("correspondences"), dict) else {}
    element = str(corr.get("element") or "") or None
    keywords = [str(k).strip() for k in (row.get("keywords") or []) if str(k).strip()]
    catalog_up = str(row.get("upright") or "").strip()
    catalog_rev = str(row.get("reversed") or "").strip()

    if int(card_id) in _MAJOR_THEMES:
        major = _MAJOR_THEMES[int(card_id)]
        return {
            "central_symbol": str(major.get("central") or major["name"]),
            "light_side": list(major.get("light") or major["up"]),
            "shadow_side": list(major.get("shadow") or major["rev"]),
            "upright_themes": list(major["up"]),
            "reversed_themes": list(major["rev"]),
            "upright_meaning": catalog_up,
            "reversed_meaning": catalog_rev,
            "keywords": keywords or list(major["up"])[:4],
            "element": element,
            "element_ru": _ELEMENT_RU.get(element or "", None),
        }

    suit = str(row.get("suit") or "").lower()
    suit_meta = _SUIT_THEMES.get(suit) or {}
    central = keywords[0] if keywords else str(row.get("name_ru") or row.get("name") or "тема карты")
    return {
        "central_symbol": central,
        "light_side": list(suit_meta.get("light") or keywords[:3]),
        "shadow_side": list(suit_meta.get("shadow") or keywords[:3]),
        "upright_themes": keywords[:6] or list(suit_meta.get("light") or []),
        "reversed_themes": list(suit_meta.get("shadow") or keywords[:6]),
        "upright_meaning": catalog_up,
        "reversed_meaning": catalog_rev,
        "keywords": keywords,
        "element": element or suit_meta.get("element"),
        "element_ru": _ELEMENT_RU.get(str(element or suit_meta.get("element") or ""), None),
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
        line = ", ".join(str(t) for t in themes[:4]) if themes else str(rng.get("upright_meaning") or "")[:120]
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


def _clip_profile_value(raw: Any, *, max_len: int = 180) -> str | None:
    if isinstance(raw, list):
        parts = [str(x).strip() for x in raw if str(x).strip()]
        if not parts:
            return None
        text = "; ".join(parts[:3])
    elif isinstance(raw, str):
        text = raw.strip()
    else:
        return None
    if not text:
        return None
    return text[:max_len].rstrip()


def profile_relevant_fragment(
    experience_slice: dict | None,
    *,
    question: str | None = None,
    concern_domain: str | None = None,
) -> tuple[dict[str, str], str | None]:
    """Select short domain-relevant profile fields — never a natal dump."""
    if not isinstance(experience_slice, dict):
        return {}, None
    domain = infer_question_domain(question, concern_domain)
    keys = _PROFILE_KEYS_BY_DOMAIN.get(domain, _PROFILE_KEYS_BY_DOMAIN["general"])
    out: dict[str, str] = {}
    for key in keys:
        clipped = _clip_profile_value(experience_slice.get(key))
        if clipped:
            out[key] = clipped
        if len(out) >= 2:
            break
    if not out:
        for key in ("decision_style", "motivation", "communication_style"):
            clipped = _clip_profile_value(experience_slice.get(key))
            if clipped:
                out[key] = clipped
                break
    lens = next(iter(out.values()), None)
    return out, lens


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
    domain = infer_question_domain(question, concern_domain)
    profile_frag, lens = profile_relevant_fragment(
        experience_slice,
        question=question,
        concern_domain=concern_domain,
    )

    pack_cards: list[dict[str, Any]] = []
    for idx, card in enumerate(cards):
        row = deck[int(card.card.id)]
        pid = (card.position.id if card.position else "") or ""
        role = position_role(pid)
        orient = (card.orientation or "upright").strip().lower()
        suit = str(row.get("suit") or "") or None
        card_type = str(row.get("type") or ("major" if int(card.card.id) <= 21 else "minor"))
        suit_meta = _SUIT_THEMES.get((suit or "").lower()) if suit else None
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
                "suit_themes": (suit_meta or {}).get("summary") if suit_meta else None,
                "suit_light": (suit_meta or {}).get("light") if suit_meta else None,
                "suit_shadow": (suit_meta or {}).get("shadow") if suit_meta else None,
                "orientation": "reversed" if orient == "reversed" else "upright",
                "position_id": pid,
                "position_title": (card.position.title if card.position else "") or pid,
                "position_prompt": (card.position.prompt if card.position else None),
                "position_role": role,
                "position_role_instruction": _ROLE_INSTRUCTION.get(role, _ROLE_INSTRUCTION["neutral"]),
                "meaning_range": _meaning_range(card.card.id, row),
                "question_lens": _DOMAIN_QUESTION_LENS.get(domain, _DOMAIN_QUESTION_LENS["general"]),
                "neighbors": neighbors,
            }
        )

    return {
        "question": (question or "").strip(),
        "spread_id": spread.spread_id,
        "spread_title": spread.title,
        "spread_kind": kind,
        "concern_domain": (concern_domain or "").strip(),
        "question_domain": domain,
        "profile_relevant": profile_frag,
        "profile_lens": lens,
        "cards": pack_cards,
        "response_shape": {
            "blocks": ["symbols_overview", "question_story", "direct_answer", "next_step"],
            "choice_compare": kind == "choice",
            "voice": "person-not-system",
            "locale": "ru",
            "order": "conflict_first_then_answer",
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
    """Honest emergency fallback — base card facts only, no fake synthesis."""
    lines: list[str] = []
    for card in pack.get("cards") or []:
        if not isinstance(card, dict):
            continue
        name = str(card.get("name_ru") or "").strip()
        pos = str(card.get("position_title") or card.get("position_id") or "").strip()
        rng = card.get("meaning_range") if isinstance(card.get("meaning_range"), dict) else {}
        orient = str(card.get("orientation") or "upright")
        themes = rng.get("reversed_themes") if orient == "reversed" else rng.get("upright_themes")
        theme_s = ", ".join(str(t) for t in (themes or [])[:3])
        central = str(rng.get("central_symbol") or "").strip()
        bit = f"{name}"
        if pos:
            bit += f" · {pos}"
        if central:
            bit += f" — {central}"
        if theme_s:
            bit += f" ({theme_s})"
        lines.append(bit)
    listed = "; ".join(lines[:6]) if lines else "карты расклада"
    notice = (
        "Не удалось собрать полноценную интерпретацию. "
        "Ниже — только базовые значения карт без персонального синтеза."
    )
    return {
        "symbols_overview": f"{notice} {listed}.",
        "question_story": notice,
        "direct_answer": notice,
        "next_step": "Открой расклад снова позже — без синтеза лучше не принимать решение только по списку карт.",
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
