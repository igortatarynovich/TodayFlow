"""Utilities for text quality checks to reduce generic/template output."""

from __future__ import annotations

import re
from typing import Iterable


_WS_RE = re.compile(r"\s+")
_WORD_RE = re.compile(r"[A-Za-zА-Яа-яЁё0-9-]+", re.UNICODE)


# Пустые placeholder'ы и generic wellness-spam — блокируем post-validation.
# Фразы про фокус/ритм/шум («не распыляйся», «лишний шум») — допустимы,
# когда они опираются на контекст дня; их запрет только в LLM-промптах как «голые» клише.
DEAD_PATTERNS = (
    "тема дня формируется",
    "практическая сцена формируется",
    "обрати внимание на текущий момент",
    "слушай себя",
    "действуй осознанно",
    "избегай импульсивных решений",
    "все будет хорошо",
    "всё будет хорошо",
    "вселенная на твоей стороне",
    "вселенная на моей стороне",
    "просто доверься",
)

ACTION_VERBS = (
    "сделай",
    "запиши",
    "выбери",
    "сформулируй",
    "проверь",
    "заверши",
    "отложи",
    "ограничи",
    "спроси",
    "назови",
    "начни",
    "останови",
    "закрой",
    "попроси",
)


def normalize_text(text: str) -> str:
    return _WS_RE.sub(" ", (text or "")).strip()


def word_list(text: str) -> list[str]:
    return [w.lower() for w in _WORD_RE.findall(text or "")]


def contains_dead_pattern(text: str) -> bool:
    normalized = normalize_text(text).lower()
    return any(pattern in normalized for pattern in DEAD_PATTERNS)


def has_action_verb(text: str) -> bool:
    normalized = normalize_text(text).lower()
    return any(verb in normalized for verb in ACTION_VERBS)


def is_meaningful_sentence(text: str, *, min_words: int = 5) -> tuple[bool, str | None]:
    normalized = normalize_text(text)
    if not normalized:
        return False, "пустая строка"

    if contains_dead_pattern(normalized):
        return False, "шаблонная формулировка"

    words = word_list(normalized)
    if len(words) < min_words:
        return False, f"слишком коротко (меньше {min_words} слов)"

    unique_ratio = len(set(words)) / max(1, len(words))
    if unique_ratio < 0.5:
        return False, "низкое разнообразие слов"

    return True, None


def find_duplicate_lines(lines: Iterable[str]) -> bool:
    seen: set[str] = set()
    for line in lines:
        normalized = normalize_text(line).lower()
        if not normalized:
            continue
        if normalized in seen:
            return True
        seen.add(normalized)
    return False
