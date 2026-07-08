"""P0.1.3 — Growth slot: skill/quality to develop today, not energy observation."""

from __future__ import annotations

import re

from todayflow_backend.services.today_contract_fallbacks_v1 import DEVELOPMENT_POINT_FALLBACK
from todayflow_backend.services.today_contract_text_quality_v1 import (
    accept_narrative_source,
    is_profile_trait_text,
    _slots_too_similar,
    truncate_sentences,
    MAX_GROWTH_CHARS,
)

_OBSERVATION_MARKERS = (
    "энергия —",
    "энергия -",
    "про сон",
    "нагрузку",
    "эмоциональный фон",
    "тело просит",
    "состояние —",
    "состояние -",
    "это про",
    "день отмечает",
    "отмечает импульс",
    "гороскоп и чек-ин",
    "фокус дня про",
    "ресурс",
    "выдержит ресурс",
)

_GROWTH_SKILL_MARKERS = (
    "тренируй",
    "замечай",
    "замечать",
    "полезно",
    "развивай",
    "учись",
    "практикуй",
    "способность",
    "навык",
    "качество",
    "держать один",
    "завершать начатое",
    "не ускоря",
)

_PERIOD_GROWTH_THEMES: tuple[tuple[str, str], ...] = (
    ("устойчив", "Сегодня полезно замечать момент, когда ты начинаешь ускоряться из тревоги."),
    ("ритм", "Сегодня тренируй способность держать один ритм вместо постоянного переключения."),
    ("последователь", "Сегодня полезнее завершать начатое, чем искать новые идеи."),
    ("ясност", "Сегодня тренируй ясность: одна прямая фраза лучше, чем серия намёков."),
    ("контакт", "Сегодня полезно говорить прямо, а не угадывать настроение другого человека."),
    ("заверш", "Сегодня тренируй завершение — один закрытый шаг важнее пяти начатых."),
    ("фокус", "Сегодня полезно удерживать один фокус, когда появляется желание схватить всё."),
    ("импульс", "Сегодня тренируй паузу перед импульсивным решением или тратой."),
    ("спокойн", "Сегодня полезно замедляться, когда тело просит скачок."),
)

_OBSERVATION_PRO_RE = re.compile(r"[-—]\s*про\s+", re.I)


def is_observation_not_growth(text: str | None) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    low = t.lower()
    if any(m in low for m in _OBSERVATION_MARKERS):
        return True
    if _OBSERVATION_PRO_RE.search(low):
        return True
    if low.startswith(("тело ", "энергия ", "сон ", "настроение ")) and "тренируй" not in low:
        return True
    return False


def is_growth_skill_text(text: str | None) -> bool:
    t = (text or "").strip()
    if not t or is_profile_trait_text(t) or is_observation_not_growth(t):
        return False
    low = t.lower()
    if any(m in low for m in _GROWTH_SKILL_MARKERS):
        return True
    if low.startswith(("сегодня полезно", "сегодня тренируй", "сегодня учись")):
        return True
    return False


def accept_growth_source(text: str | None) -> str:
    t = accept_narrative_source(text)
    if not t or not is_growth_skill_text(t):
        return ""
    return truncate_sentences(t, 1, MAX_GROWTH_CHARS)


def synthesize_growth_from_period(period: str) -> str:
    low = (period or "").lower()
    for theme, template in _PERIOD_GROWTH_THEMES:
        if theme in low:
            return template
    return DEVELOPMENT_POINT_FALLBACK


def resolve_development_point(period: str, raw_candidate: str) -> str:
    candidate = accept_growth_source(raw_candidate)
    if not candidate:
        candidate = synthesize_growth_from_period(period)
    p = truncate_sentences((period or "").strip(), 2, 200)
    g = truncate_sentences(candidate, 1, MAX_GROWTH_CHARS)
    if _slots_too_similar(p, g):
        return synthesize_growth_from_period(period)
    if is_profile_trait_text(g) or is_observation_not_growth(g):
        return synthesize_growth_from_period(period)
    return g
