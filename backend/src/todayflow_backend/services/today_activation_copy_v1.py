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


# Body tone for Glance labels — experiential, no planet names in output.
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


def aspect_class_label_short(aspect: str, planet: str | None = None) -> str:
    """GlanceTimeline `label_short` — ≤ ~4 words RU; distinct by body+aspect class."""
    asp = _norm(aspect)
    tone = _BODY_TONE_RU.get(_norm(planet or ""), "")
    if aspect_is_harmonious(asp):
        if tone == "контакт":
            return "Контакт мягче"
        if tone == "импульс":
            return "Ход легче"
        if tone == "настроение":
            return "Настроение ровнее"
        if tone == "слова":
            return "Слова легче"
        if tone:
            return f"{tone.capitalize()} в опоре"
        return "Есть опора"
    if aspect_is_challenging(asp):
        if tone == "импульс":
            return "Импульс острее"
        if tone == "контакт":
            return "Контакт жёстче"
        if tone == "настроение":
            return "Настроение вразнос"
        if tone == "слова":
            return "Слова режут"
        if tone == "границы":
            return "Границы давят"
        if tone:
            return f"{tone.capitalize()} в трении"
        return "Короче шаг"
    if asp == "conjunction":
        if tone == "импульс":
            return "Импульс сгущается"
        if tone == "слова":
            return "Слова сгущаются"
        if tone:
            return f"{tone.capitalize()} сгущается"
        return "Тема сгущается"
    if tone:
        return f"Окно: {tone}"
    return "Окно дня"
