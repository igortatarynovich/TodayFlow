"""Shared Wave 2 activation copy — experiential RU, no planet/aspect jargon."""

from __future__ import annotations

from todayflow_backend.data.foundation_constants_v1 import (
    aspect_is_challenging,
    aspect_is_harmonious,
)

# Soft support — domain-distinct so four spheres never collapse
# to one identical «Есть опора» line. Class from foundation aspect_character.
DOMAIN_SOFT_WHY_RU = {
    "work": "В деле есть опора — можно опереться",
    "money": "В ресурсах тише — без резких ходов",
    "relationships": "В контакте мягче — есть на что опереться",
    "energy": "В теле ровнее — можно опереться на ритм",
}

DOMAIN_HARD_WHY_RU = {
    "work": "В деле сопротивление — короче шаг",
    "money": "В ресурсах трение — короче шаг",
    "relationships": "В контакте острее — короче шаг",
    "energy": "В теле плотнее — короче шаг",
}

DOMAIN_FOCUS_WHY_RU = {
    "work": "Тема дела сгущается — держи фокус",
    "money": "Тема ресурсов сгущается — держи фокус",
    "relationships": "Тема контакта сгущается — держи фокус",
    "energy": "Тема тела сгущается — держи фокус",
}


def _norm(value: str) -> str:
    return (value or "").strip().lower()


def aspect_class_why_short(aspect: str, domain: str | None = None) -> str:
    """VerdictStrip `why_short` — ≤ ~10 words RU; domain keeps spheres distinct."""
    asp = _norm(aspect)
    d = _norm(domain) if domain else ""
    if aspect_is_harmonious(asp):
        return DOMAIN_SOFT_WHY_RU.get(d, "Есть опора — можно опереться")
    if aspect_is_challenging(asp):
        return DOMAIN_HARD_WHY_RU.get(d, "Есть сопротивление — короче шаг")
    if asp == "conjunction":
        return DOMAIN_FOCUS_WHY_RU.get(d, "Тема сгущается — держи фокус")
    return "Сигнал есть — без лишнего шума"


# Body tone → activity-lane fill-empty for glance (Kimi is SoT for title/detail).
_BODY_TONE_RU = {
    "sun": "ясность",
    "moon": "настроение",
    "mercury": "слова",
    "venus": "контакт",
    "mars": "импульс",
    "jupiter": "размах",
    "saturn": "границы",
    "uranus": "сдвиг",
    "neptune": "туман",
    "pluto": "глубина",
}

# Activity windows — fill-empty only when Kimi cache miss.
_WINDOW_FOR_RU = {
    "ясность": "Ясность — решения",
    "настроение": "Отдых и пауза",
    "слова": "Диалоги и письма",
    "контакт": "Живой контакт",
    "импульс": "Короткие задачи",
    "размах": "Крупный шаг",
    "границы": "Порядок и стоп",
    "сдвиг": "Смена курса",
    "туман": "Без жёстких решений",
    "глубина": "Глубокая тема",
}


def aspect_class_label_short(aspect: str, planet: str | None = None) -> str:
    """GlanceTimeline bank fill-empty — activity lane by body; valence carries soft/hard."""
    asp = _norm(aspect)
    tone = _BODY_TONE_RU.get(_norm(planet or ""), "")
    if tone:
        return _WINDOW_FOR_RU.get(tone, f"Тема: {tone}")
    if aspect_is_harmonious(asp):
        return "Есть опора"
    if aspect_is_challenging(asp):
        return "Короче шаг"
    if asp == "conjunction":
        return "Тема сгущается"
    return "Сигнал дня"
