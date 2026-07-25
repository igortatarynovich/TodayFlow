"""Editorial formula bank for day_story fallback — RULE_005 slot fill.

Keyed by day_thesis family.variant. Source: TODAY_LANGUAGE_STRONG_PATTERNS_V0
exemplars A–C. Not TL-1 quality scoring — deterministic scene/trap/do/avoid/vibe.
"""

from __future__ import annotations

from typing import Any

# family.variant → editorial slots (RU). events_lead stays driver-projected.
_FORMULAS: dict[str, dict[str, Any]] = {
    # Exemplar A — День возвращения ясности
    "communication.clarity_returns_after_delay": {
        "exemplar_id": "editorial_A_clarity_return",
        "theme": "День возвращения ясности",
        "headline_anchor": "День возвращения ясности",
        "expect": (
            "Ментальный шум стихает: письма, планы и недописанные черновики снова двигаются."
        ),
        "trap": "На радостях сказать лишнее или включить режим «знайки».",
        "do": [
            "Отправь отложенные черновики или забронируй то, что давно висело.",
            "Выдели один блок на новое — урок, маршрут, короткую практику.",
        ],
        "avoid": [
            "Не читай нотаций и не поправляй чужие формулировки «для ясности».",
            "Не открывай второй фронт, пока не закрыт один ясный шаг.",
        ],
        "vibe_closing": "Спонтанность; смех над старыми фейлами; быстрые ответы без лишней важности.",
        "development_point": "Замечать, где ясность уже есть — и не добивать её контролем.",
    },
    # Exemplar B — День неожиданных поворотов
    "change.sudden_turns": {
        "exemplar_id": "editorial_B_sudden_turns",
        "theme": "День неожиданных поворотов",
        "headline_anchor": "День неожиданных поворотов",
        "expect": "Смена планов, эмоции через край, всплывшие тайны или резкий поворот темы.",
        "trap": "Сжечь мосты из упрямства — ответить так, что потом не развернуть.",
        "do": [
            "Оставь запас гибкости в расписании и в формулировках.",
            "Сбрось напряжение через тело или короткое творчество, прежде чем решать.",
        ],
        "avoid": [
            "Не принимай импульсивных необратимых решений в пике эмоции.",
            "Не спорь «до победы», если ставка — сохранить мост.",
        ],
        "vibe_closing": "Неожиданные новости; наушники на максимум; философский взгляд на сюрпризы.",
        "development_point": "Учиться разворачиваться без самоуничтожения старых связей.",
    },
    # Exemplar C — День выбора
    "decision.stop_pleasing_everyone": {
        "exemplar_id": "editorial_C_day_of_choice",
        "theme": "День выбора",
        "headline_anchor": "День выбора",
        "expect": "Стена компромисса и одновременно луч удачи — если сделать один реальный шаг.",
        "trap": "Сидеть на двух стульях до выгорания, угождая всем сразу.",
        "do": [
            "Сделай первый реальный шаг к цели ближайших выходных или недели.",
            "Скажи одно честное «да» или «нет» — без сглаживания до пустоты.",
        ],
        "avoid": [
            "Не пытайся всем угодить — сегодня это крадёт выбор.",
            "Не откладывай решение «ещё на чуть-чуть», если цена уже ясна.",
        ],
        "vibe_closing": "Продуктивность среди недели; хорошие новости на почте; вовремя сказать «хватит».",
        "development_point": "Выбирать одно направление вместо вечного балансирования.",
    },
    "decision.one_clear_yes": {
        "exemplar_id": "editorial_C_one_clear_yes",
        "theme": "День одного ясного «да»",
        "headline_anchor": "Одно ясное «да»",
        "expect": "Появляется окно, где достаточно одного чёткого согласия — без длинного списка условий.",
        "trap": "Размыть «да» оговорками, пока оно снова не станет «может быть».",
        "do": [
            "Скажи одно ясное «да» там, где уже достаточно фактов.",
            "Закрой мелкий контур сразу после согласия — письмо, бронь, время в календаре.",
        ],
        "avoid": [
            "Не добавляй третий вариант «на всякий случай».",
            "Не прячь решение за вежливой неопределённостью.",
        ],
        "vibe_closing": "Короткий ответ; спокойная уверенность; меньше переговоров с собой.",
        "development_point": "Практиковать согласие без бесконечного согласования с воображаемой аудиторией.",
    },
}


def formula_key(family: str | None, variant: str | None) -> str:
    return f"{(family or '').strip()}.{(variant or '').strip()}"


def lookup_editorial_formula(
    *,
    family: str | None = None,
    variant: str | None = None,
    day_thesis: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Return a shallow copy of the formula row, or None if no bank hit."""
    fam = family
    var = variant
    if isinstance(day_thesis, dict):
        fam = fam or day_thesis.get("family")
        var = var or day_thesis.get("variant")
    row = _FORMULAS.get(formula_key(str(fam or ""), str(var or "")))
    if not row:
        return None
    return {
        "exemplar_id": row["exemplar_id"],
        "theme": row["theme"],
        "headline_anchor": row["headline_anchor"],
        "expect": row["expect"],
        "trap": row["trap"],
        "do": list(row["do"]),
        "avoid": list(row["avoid"]),
        "vibe_closing": row["vibe_closing"],
        "development_point": row["development_point"],
    }


def list_editorial_formula_keys() -> list[str]:
    return sorted(_FORMULAS.keys())
