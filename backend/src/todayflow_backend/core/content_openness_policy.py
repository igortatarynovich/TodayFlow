"""Content voice policy: open, direct, useful. Safety rails stay internal — never in user copy."""

from __future__ import annotations

import re

_WS_RE = re.compile(r"\s+")

# Phrases that read as editorial meta-disclaimers, not substance for the user.
META_EDITORIAL_NEEDLES: tuple[str, ...] = (
    "без пошлости",
    "без вульгарности",
    "без стыда и клише",
    "не нормативный текст",
    "не медицинский и не нормативный",
    "не медицинский текст",
    "правила редактуры",
    "без порно",
    "не объясняй правила",
    "не упоминай правила",
    "no vulgarity",
    "no shame, no clich",
    "kept respectful",
    "not porn",
    "not clinical",
    "not moralizing",
    "editorial rules",
    "never mention editorial",
    "without euphemisms",
    "internal only",
    "не цитируй их в ответе",
)

LLM_USER_VOICE_RU = """Голос для пользователя:
— открыто, прямо и по делу; называй вещи своими именами
— практические рекомендации там, где они помогают (секс, границы, деньги, конфликты)
— уважение к согласию и выбору; без морализаторства и без стыда
— только содержание: не объясняй правила, запреты или «мы не делаем X»"""

LLM_USER_VOICE_EN = """User-facing voice:
— open, direct, concrete; call things by their names
— practical recommendations where they help (sex, boundaries, money, conflict)
— respect consent and choice; no moralizing, no shame framing
— substance only: never explain editorial rules, bans, or meta disclaimers"""

LLM_SAFETY_BOUNDARY_RU = """Внутренние границы (не цитировать в тексте):
— без порнографии и откровенно грубой лексики
— без опасных, вредительских или манипулятивных советов
— без медицинских диагнозов и юридических инструкций; при необходимости — одна нейтральная отсылка к специалисту"""

LLM_SAFETY_BOUNDARY_EN = """Internal boundaries (never quote in output):
— no pornography or crude vulgar language
— no dangerous, harmful, or manipulative advice
— no medical diagnoses or legal instructions; if needed, one neutral line to seek a professional"""

LLM_ANTI_ESOTERIC_RU = (
    "Стиль (внутренне): без эзотерических штампов — энергия, вибрации, вселенная, космос, мистика."
)
LLM_ANTI_ESOTERIC_EN = (
    "Style (internal): avoid esoteric filler — energy, vibration, universe, cosmos, mysticism."
)


def strip_meta_editorial_phrases(text: str | None) -> str:
    """Drop sentences that leak editorial bans/disclaimers into user-facing copy."""
    raw = (text or "").strip()
    if not raw:
        return ""
    low = raw.lower()
    if not any(n in low for n in META_EDITORIAL_NEEDLES):
        return raw
    parts = re.split(r"(?<=[.!?])\s+", raw)
    kept: list[str] = []
    for part in parts:
        pl = part.strip()
        if not pl:
            continue
        if any(n in pl.lower() for n in META_EDITORIAL_NEEDLES):
            continue
        kept.append(pl)
    out = " ".join(kept).strip()
    return _WS_RE.sub(" ", out).strip() if out else raw
