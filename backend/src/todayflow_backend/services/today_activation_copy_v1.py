"""Shared Wave 2 activation copy — experiential RU, no planet/aspect jargon."""

from __future__ import annotations

# Soft support (trine/sextile) — domain-distinct so four spheres never collapse
# to one identical «Есть опора» line.
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
    if asp in ("trine", "sextile"):
        return DOMAIN_SOFT_WHY_RU.get(d, "Есть опора — можно опереться")
    if asp in ("square", "opposition", "quincunx"):
        return DOMAIN_HARD_WHY_RU.get(d, "Есть сопротивление — короче шаг")
    if asp == "conjunction":
        return DOMAIN_FOCUS_WHY_RU.get(d, "Тема сгущается — держи фокус")
    return "Сигнал есть — без лишнего шума"


def aspect_class_label_short(aspect: str) -> str:
    """GlanceTimeline `label_short` — ≤ ~4 words RU."""
    asp = _norm(aspect)
    if asp in ("trine", "sextile"):
        return "Есть опора"
    if asp in ("square", "opposition", "quincunx"):
        return "Короче шаг"
    if asp == "conjunction":
        return "Тема сгущается"
    return "Сигнал дня"
