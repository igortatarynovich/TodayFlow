"""Tarot Interpretation Engine v1 — resolve cards, block unresolved, compare choice paths.

Canon: docs/tarot/TAROT_INTERPRETATION_ENGINE_V1.md
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any, TypedDict

from todayflow_backend.core import models
from todayflow_backend.data import astrology as astrology_ref

logger = logging.getLogger(__name__)

SYNTHESIS_MODE_OK = "interpretation_engine_v1"
SYNTHESIS_MODE_BLOCKED = "unresolved_blocked"
STATUS_OK = "ok"
STATUS_UNRESOLVED = "unresolved_cards"

CHOICE_SPREAD_IDS = frozenset({"guidance_choice_two", "choice"})

# Curated major voice (0–21). Minors use suit × role templates — never "Аркан".
_MAJOR_SPEAK: dict[int, dict[str, str]] = {
    0: {"name": "Шут", "up": "можно сделать шаг без гарантии идеального исхода — это не безрассудство, а честность", "rev": "импульсивный шаг ради снятия тревоги, а не ради ясности"},
    1: {"name": "Маг", "up": "всё нужное для решения уже в твоих руках — осталось собрать внимание в один ход", "rev": "силы разбросаны: ты сомневаешься, что можешь повлиять на ситуацию"},
    2: {"name": "Верховная Жрица", "up": "ответ уже внутри — его не принесут извне, только услышат", "rev": "ты слышишь ответ, но не даёшь себе в него поверить"},
    3: {"name": "Императрица", "up": "сейчас важна забота и опора — не награда «потом», а база для решения", "rev": "истощение: ты отдаёшь больше, чем получаешь обратно"},
    4: {"name": "Император", "up": "нужны ясные границы и структура — они защищают, а не давят", "rev": "жёсткость как броня: контроль вместо живого разговора с собой"},
    5: {"name": "Иерофант", "up": "опора на свои ценности важнее, чем чужие «как надо»", "rev": "ты повторяешь чужие правила вместо собственного выбора"},
    6: {"name": "Влюблённые", "up": "дело в честном выборе сердца — назвать, чего ты хочешь", "rev": "колебание: страшно назвать желание вслух, даже себе"},
    7: {"name": "Колесница", "up": "можно двигаться вперёд — направление уже почти ясно", "rev": "гонка без паузы: спешка маскирует страх остановиться"},
    8: {"name": "Сила", "up": "мягкая устойчивость: держать себя, не подавляя чувства", "rev": "срыв терпения или сомнение, что выдержишь"},
    9: {"name": "Отшельник", "up": "нужно время побыть с собой — в шуме ответ не слышен", "rev": "изоляция как способ не встречаться с правдой"},
    10: {"name": "Колесо Фортуны", "up": "цикл уже сдвинулся — ты не в той же точке, что месяц назад", "rev": "ощущение застревания: страх, что ничего не изменится"},
    11: {"name": "Справедливость", "up": "нужен честный взгляд на то, что произошло — без самооправданий", "rev": "холодная правота вместо признания того, что болит"},
    12: {"name": "Повешенный", "up": "пауза, чтобы увидеть иначе — не заморозка, а другой угол", "rev": "застревание в ожидании, что кто-то другой всё решит"},
    13: {"name": "Смерть", "up": "этап завершается — прежнюю форму не вернуть, и это освобождает", "rev": "цепляние за старое из страха пустоты"},
    14: {"name": "Умеренность", "up": "нужен баланс и ровный темп — не крайности", "rev": "качели «всё или ничего» забирают ясность"},
    15: {"name": "Дьявол", "up": "удерживает не человек — привычный сценарий, который сложно заметить", "rev": "петля видна: первый шаг к выходу уже возможен"},
    16: {"name": "Башня", "up": "то, что казалось надёжным, уже трещит — и это высвобождает место для правды", "rev": "страх перемены сильнее, чем сама перемена"},
    17: {"name": "Звезда", "up": "тонкая надежда после усталости — восстановление возможно", "rev": "сомнение, что восстановление вообще реально"},
    18: {"name": "Луна", "up": "неясность нельзя торопить — сначала назвать страх", "rev": "путаешь свои ожидания с реальностью"},
    19: {"name": "Солнце", "up": "ясность близко — правда уже становится видимой", "rev": "радость или ясность сдерживаются: страшно быть уязвимым"},
    20: {"name": "Суд", "up": "момент честно подвести итог и откликнуться на зов внутри", "rev": "ты откладываешь разговор с собой — хотя ответ уже назрел"},
    21: {"name": "Мир", "up": "дуга завершается — можно выдохнуть и принять итог", "rev": "формально всё закрыто, но внутри — незавершённость"},
}

_SUIT_SPEAK: dict[str, dict[str, dict[str, str]]] = {
    "wands": {
        "gain": {
            "up": "даёт импульс и пространство начать движение своими силами",
            "rev": "обещает облегчение через действие, но импульс пока размыт",
        },
        "risk": {
            "up": "риск перегореть или шагать раньше фактов",
            "rev": "риск застрять в раздражении без реального хода",
        },
        "weights": {
            "up": "важно учитывать, куда уходит твоя воля — в ясность или в борьбу",
            "rev": "важно не путать усталость от давления с отсутствием желания",
        },
        "step": {
            "up": "сделай один конкретный ход, который проверяет направление на практике",
            "rev": "сначала сузь фокус: один шаг, без разгона на десять фронтов",
        },
        "neutral": {
            "up": "здесь звучит тема инициативы и живого движения",
            "rev": "здесь звучит тема рассеянной энергии и недозрелого старта",
        },
    },
    "cups": {
        "gain": {
            "up": "даёт доступ к чувствам и более честной эмоциональной опоре",
            "rev": "может дать облегчение, но через избегание настоящих чувств",
        },
        "risk": {
            "up": "риск раствориться в чужих ожиданиях или идеализировать исход",
            "rev": "риск закрыться и читать догадки вместо живого контакта",
        },
        "weights": {
            "up": "важно учитывать, что решение проходит через чувство, а не только расчёт",
            "rev": "важно не принимать решение из пустоты или обиды",
        },
        "step": {
            "up": "назови одно чувство вслух — себе или в разговоре — без требования ответа",
            "rev": "вернись к одному простому контакту с собой, прежде чем решать за всех",
        },
        "neutral": {
            "up": "здесь звучит тема чувств и близости к себе",
            "rev": "здесь звучит тема эмоциональной блокировки",
        },
    },
    "swords": {
        "gain": {
            "up": "даёт ясность мысли, границы и честную формулировку",
            "rev": "может дать мнимую ясность — слова без опоры в фактах",
        },
        "risk": {
            "up": "риск ранить себя или других холодной «правдой»",
            "rev": "риск запутаться в сценариях тревоги и прокрутках",
        },
        "weights": {
            "up": "важно учитывать цену сказанного — и цену недосказанного",
            "rev": "важно не принимать решение только из страха ошибиться словами",
        },
        "step": {
            "up": "запиши один ясный критерий или один прямой вопрос — без лишней драмы",
            "rev": "останови прокрутку: одно предложение факта вместо десяти гипотез",
        },
        "neutral": {
            "up": "здесь звучит тема ясности, границ и слов",
            "rev": "здесь звучит тема ментального шума и сомнений",
        },
    },
    "pentacles": {
        "gain": {
            "up": "даёт опору в материальном: стабильность, навыки, практический результат",
            "rev": "может выглядеть как опора, но держится на привычке, а не на живом смысле",
        },
        "risk": {
            "up": "риск застрять в безопасности ценой роста",
            "rev": "риск потерять опору или недооценить практическую цену выбора",
        },
        "weights": {
            "up": "важно учитывать ресурсы: время, деньги, силы тела",
            "rev": "важно не игнорировать практическую сторону ради красивой идеи",
        },
        "step": {
            "up": "сделай один приземлённый шаг: цифра, срок, разговор об условиях",
            "rev": "проверь одну практическую деталь, прежде чем обещать себе большой поворот",
        },
        "neutral": {
            "up": "здесь звучит тема опоры, труда и материальной реальности",
            "rev": "здесь звучит тема нестабильной опоры или отложенной заботы о базе",
        },
    },
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


class UnresolvedCard(TypedDict):
    card_id: int
    position_id: str
    reason: str


class ResolvedSpeak(TypedDict):
    card_id: int
    name_ru: str
    orientation: str
    line: str
    position_id: str
    position_label: str
    role: str
    suit: str | None
    card_type: str


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


def _orient_key(orientation: str) -> str:
    return "rev" if (orientation or "").strip().lower() == "reversed" else "up"


def resolve_card_speak(
    card_id: int,
    orientation: str,
    *,
    position_id: str | None = None,
) -> ResolvedSpeak | None:
    """Resolve name_ru + speak line. None = unresolved (never invent «Аркан»)."""
    deck = _deck_by_id()
    row = deck.get(int(card_id))
    if not row:
        return None

    name_ru = str(row.get("name_ru") or "").strip()
    if not name_ru:
        return None

    orient = _orient_key(orientation)
    role = position_role(position_id)
    card_type = str(row.get("type") or ("major" if int(card_id) <= 21 else "minor"))
    suit = str(row.get("suit") or "") or None

    if int(card_id) in _MAJOR_SPEAK:
        major = _MAJOR_SPEAK[int(card_id)]
        name_ru = major["name"]
        line = major["rev" if orient == "rev" else "up"]
    else:
        suit_key = (suit or "pentacles").lower()
        suit_bank = _SUIT_SPEAK.get(suit_key) or _SUIT_SPEAK["pentacles"]
        role_bank = suit_bank.get(role) or suit_bank["neutral"]
        line = role_bank.get(orient) or role_bank.get("up") or ""
        # Light keyword tint when present (RU keywords in full deck).
        kws = [str(k).strip() for k in (row.get("keywords") or []) if str(k).strip()]
        if kws and role in {"gain", "risk", "neutral"}:
            tint = kws[0]
            if tint.lower() not in line.lower():
                line = f"{line} — через тему «{tint}»"

    if orient == "rev":
        display = f"{name_ru} (перевёрнутый)"
    else:
        display = name_ru

    return {
        "card_id": int(card_id),
        "name_ru": display,
        "orientation": "reversed" if orient == "rev" else "upright",
        "line": line,
        "position_id": (position_id or "").strip(),
        "position_label": "",
        "role": role,
        "suit": suit,
        "card_type": card_type,
    }


def collect_unresolved(cards: list[models.TarotSpreadCard]) -> list[UnresolvedCard]:
    unresolved: list[UnresolvedCard] = []
    for card in cards:
        pid = card.position.id if card.position else ""
        resolved = resolve_card_speak(card.card.id, card.orientation, position_id=pid)
        if resolved is None:
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


def build_card_insights(cards: list[models.TarotSpreadCard]) -> list[models.TarotCardInsight] | None:
    """Return insights or None if any card unresolved."""
    if collect_unresolved(cards):
        return None
    insights: list[models.TarotCardInsight] = []
    for card in cards:
        pid = card.position.id if card.position else ""
        label = (card.position.title if card.position and card.position.title else pid) or "Позиция"
        resolved = resolve_card_speak(card.card.id, card.orientation, position_id=pid)
        assert resolved is not None
        insights.append(
            models.TarotCardInsight(
                position_label=label.strip(),
                card_name_ru=resolved["name_ru"],
                card_id=resolved["card_id"],
                orientation=resolved["orientation"],
                line=resolved["line"],
            )
        )
    return insights


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
            "Это не значение расклада — это сигнал, что narrative заблокирован."
        ),
        insight_holding=None,
        insight_shifting=None,
        insight_attention=None,
        today_suggestion="Открой расклад снова или выбери карты заново — без полного набора имён ответ был бы пустым.",
        follow_up_prompt="Что сделать дальше?",
        follow_up_chips=[
            models.TarotFollowUpChip(id="redraw", label="Пересобрать расклад"),
            models.TarotFollowUpChip(id="retry", label="Открыть снова"),
        ],
        card_insights=[],
        manifestation="",
        caution="",
        next_step="Открой расклад снова или выбери карты заново.",
        actions_today=["Открой расклад снова или выбери карты заново."],
        self_question=None,
        profile_lens=None,
        profile_lens_applied=False,
    )


def _by_position(
    cards: list[models.TarotSpreadCard],
    insights: list[models.TarotCardInsight],
) -> dict[str, tuple[models.TarotSpreadCard, models.TarotCardInsight]]:
    out: dict[str, tuple[models.TarotSpreadCard, models.TarotCardInsight]] = {}
    for card, insight in zip(cards, insights):
        pid = (card.position.id if card.position else "").strip().lower()
        if pid:
            out[pid] = (card, insight)
    return out


def _label_options_from_question(question: str | None) -> tuple[str, str]:
    q = (question or "").strip()
    low = q.lower()
    if "менять работ" in low or "сменить работ" in low or "уйти" in low:
        if "проясн" in low or "остат" in low or "здесь" in low:
            return "сменить работу", "сначала прояснить ситуацию здесь"
    if " или " in low:
        parts = q.split(" или ", 1)
        a = parts[0].rstrip("?». ").strip(" «")
        b = parts[1].rstrip("?». ").strip(" «")
        if 3 < len(a) < 80 and 3 < len(b) < 80:
            return a, b
    return "вариант A", "вариант B"


def compose_choice_story(
    *,
    question: str | None,
    cards: list[models.TarotSpreadCard],
    insights: list[models.TarotCardInsight],
    concern_domain: str | None = None,
) -> dict[str, Any]:
    """Build comparative choice reading fields."""
    by_pos = _by_position(cards, insights)
    opt_a, opt_b = _label_options_from_question(question)

    def _get(*ids: str) -> models.TarotCardInsight | None:
        for i in ids:
            hit = by_pos.get(i)
            if hit:
                return hit[1]
        return None

    a_gain = _get("a_gives", "option_a")
    a_risk = _get("a_risk")
    b_gain = _get("b_gives", "option_b")
    b_risk = _get("b_risk")
    weights = _get("weights", "core")
    best = _get("best_step", "next_step", "advice", "step")

    # Fall back to order if ids differ (legacy `choice` spread).
    ordered = list(insights)
    if a_gain is None and len(ordered) > 0:
        a_gain = ordered[0]
    if a_risk is None and len(ordered) > 1:
        a_risk = ordered[1]
    if b_gain is None and len(ordered) > 2:
        b_gain = ordered[2]
    if b_risk is None and len(ordered) > 3:
        b_risk = ordered[3]
    if weights is None and len(ordered) > 4:
        weights = ordered[4]
    if best is None and len(ordered) > 5:
        best = ordered[5]

    a_gain_line = a_gain.line if a_gain else "путь пока не прочитан"
    a_risk_line = a_risk.line if a_risk else "риск пока не назван"
    b_gain_line = b_gain.line if b_gain else "путь пока не прочитан"
    b_risk_line = b_risk.line if b_risk else "риск пока не назван"
    tension_line = weights.line if weights else "решение осложняет то, что сложно назвать вслух"
    step_line = best.line if best else "нужен один небольшой шаг в реальности, не только в голове"

    a_name = a_gain.card_name_ru if a_gain else "карта"
    a_risk_name = a_risk.card_name_ru if a_risk else "карта"
    b_name = b_gain.card_name_ru if b_gain else "карта"
    b_risk_name = b_risk.card_name_ru if b_risk else "карта"
    w_name = weights.card_name_ru if weights else "карта"
    s_name = best.card_name_ru if best else "карта"

    option_a_summary = (
        f"Путь «{opt_a}»: {a_name} показывает, что он может дать — {a_gain_line}. "
        f"Риск ({a_risk_name}): {a_risk_line}."
    )
    option_b_summary = (
        f"Путь «{opt_b}»: {b_name} показывает, что он открывает — {b_gain_line}. "
        f"Риск ({b_risk_name}): {b_risk_line}."
    )

    # Lean: don't urge blind exit when Moon-rev / fog on A-gain and Devil on weights.
    foggy_a = a_gain is not None and a_gain.card_id == 18 and a_gain.orientation == "reversed"
    attachment = weights is not None and weights.card_id == 15
    fool_step = best is not None and best.card_id == 0

    if foggy_a and attachment:
        direct = (
            f"Сейчас карты скорее не советуют резкий уход вслепую по пути «{opt_a}». "
            f"Сначала стоит проверить, что именно в «{opt_b}» действительно не устраивает — "
            "среда, условия или накопившаяся неопределённость. "
            "Но прояснение не должно становиться бесконечным ожиданием: его задача — дать факты для следующего шага."
        )
    elif foggy_a:
        direct = (
            f"По вопросу о выборе между «{opt_a}» и «{opt_b}» расклад указывает: "
            "сначала отдели ожидания от фактов — иначе любой путь будет казаться туманным."
        )
    else:
        direct = (
            f"По выбору между «{opt_a}» и «{opt_b}» карты сравнивают два пути, а не выдают общий прогноз. "
            f"«{opt_a}» быстрее двигает ситуацию ({a_gain_line}), но несёт риск: {a_risk_line}. "
            f"«{opt_b}» даёт другое ({b_gain_line}), однако уязвим там, где {b_risk_line}."
        )

    story = (
        f"{option_a_summary} {option_b_summary} "
        f"{w_name} связывает расклад: {tension_line}. "
        f"Поэтому следующий ход через {s_name}: {step_line}."
    )

    if fool_step:
        next_step = (
            "До окончательного решения ответь на два вопроса: "
            f"(1) что должно измениться, чтобы «{opt_b}» имел смысл оставаться; "
            f"(2) какой минимальный шаг к «{opt_a}» можно сделать без немедленного разрыва. "
            "Один небольшой эксперимент в реальности важнее идеальной уверенности в голове."
        )
    else:
        next_step = (
            f"Сделай один практический шаг по линии {s_name}: {step_line}. "
            "Зафиксируй критерий, по которому поймёшь, что проверка состоялась."
        )

    domain = (concern_domain or "").strip().lower()
    if domain == "work" or "работ" in (question or "").lower():
        confidence = (
            "Это сравнение путей по картам — не приказ уволиться и не гарантия исхода."
        )
    else:
        confidence = "Это сравнение двух путей по раскладу — без фактов вне карт."

    holding = f"{w_name}: {tension_line}."
    shifting = (
        f"Контраст путей: «{opt_a}» — {a_gain_line}; «{opt_b}» — {b_gain_line}."
    )
    attention = (
        f"Заметь разницу рисков: в «{opt_a}» — {a_risk_line}; в «{opt_b}» — {b_risk_line}."
    )

    return {
        "direct_answer": direct,
        "story_narrative": story,
        "holding": holding,
        "shifting": shifting,
        "attention": attention,
        "today_suggestion": next_step,
        "choice_story": {
            "option_a_summary": option_a_summary,
            "option_a_gain": f"{a_name}: {a_gain_line}",
            "option_a_risk": f"{a_risk_name}: {a_risk_line}",
            "option_b_summary": option_b_summary,
            "option_b_gain": f"{b_name}: {b_gain_line}",
            "option_b_risk": f"{b_risk_name}: {b_risk_line}",
            "hidden_tension": holding,
            "recommended_next_step": next_step,
            "confidence_note": confidence,
        },
    }


def soft_profile_next_step(base: str, experience_slice: dict | None) -> tuple[str, str | None, bool]:
    """Optionally tint next step; never paste profile paragraph into the body."""
    if not isinstance(experience_slice, dict):
        return base, None, False
    lens = None
    for key in ("decision_style", "identity_line", "motivation", "communication_style"):
        raw = experience_slice.get(key)
        if isinstance(raw, str) and raw.strip():
            lens = raw.strip()[:280]
            break
    if not lens:
        return base, None, False

    low = lens.lower()
    if any(w in low for w in ("стратег", "расчёт", "анализ", "мыслител", "взвешива")):
        tint = (
            " Тебе может быть особенно трудно сделать шаг без полной определённости — "
            "поэтому здесь важен маленький проверяемый эксперимент, а не идеальная гарантия."
        )
    elif any(w in low for w in ("импульс", "быстр", "смел")):
        tint = " Имеет смысл не ускорять финал: сначала один проверяемый шаг."
    elif any(w in low for w in ("тело", "чувств", "эмпат", "сверя")):
        tint = (
            " Перед финальным выбором сверься с телесным откликом — "
            "и закрепи его одним маленьким шагом в реальности."
        )
    else:
        tint = " Сделай этот шаг достаточно маленьким, чтобы его можно было проверить без идеала."

    if tint.strip() and tint.strip() not in base:
        return f"{base.rstrip('.')}{tint}", lens, True
    return base, lens, True
