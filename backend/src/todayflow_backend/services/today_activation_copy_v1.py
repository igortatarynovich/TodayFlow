"""Shared Wave 2 activation copy — experiential RU, no planet/aspect jargon."""

from __future__ import annotations


def _norm(value: str) -> str:
    return (value or "").strip().lower()


def aspect_class_why_short(aspect: str) -> str:
    """VerdictStrip `why_short` — ≤ ~10 words RU."""
    asp = _norm(aspect)
    if asp in ("trine", "sextile"):
        return "Есть опора — можно опереться"
    if asp in ("square", "opposition", "quincunx"):
        return "Есть сопротивление — короче шаг"
    if asp == "conjunction":
        return "Тема сгущается — держи фокус"
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
