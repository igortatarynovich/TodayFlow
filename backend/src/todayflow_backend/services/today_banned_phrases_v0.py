"""Banned internal jargon / meta labels for Today narrative surfaces (RU)."""

from __future__ import annotations

import re

BANNED_PHRASES_RU: tuple[str, ...] = (
    "общий фон дня",
    "тема «общий фон дня»",
    "тема \"общий фон дня\"",
    "тема «в голове»",
    "тема \"в голове\"",
    "head_topic",
    "day_engine_brief",
    "funnel_interpretation",
    "guide_decision",
    "day_model_v0",
    "contract_version",
    "anchor_summary",
    "алгоритм",
    "движок расчёта",
    "llm",
    "промпт",
)

BANNED_TOKEN_RE_RU: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?<![а-яёa-z])api(?![а-яёa-z])", re.I),
)


def find_banned_hits(text: str) -> list[str]:
    t = (text or "").strip()
    if not t:
        return []
    low = t.lower()
    hits: list[str] = []
    for phrase in BANNED_PHRASES_RU:
        if phrase.lower() in low:
            hits.append(phrase)
    for rx in BANNED_TOKEN_RE_RU:
        if rx.search(t):
            hits.append(rx.pattern)
    return hits


def scrub_banned_phrases(text: str) -> str:
    """Lightweight scrub for known internal labels leaking into user copy."""
    out = text or ""
    for phrase in BANNED_PHRASES_RU:
        if not phrase:
            continue
        out = re.sub(re.escape(phrase), "", out, flags=re.I)
    out = re.sub(r"тема\s*[«\"]\s*[»\"]", "", out, flags=re.I)
    out = re.sub(r"[«\"]\s*[»\"]", "", out)
    out = re.sub(r"\s{2,}", " ", out)
    out = re.sub(r"\s+([.,;:!?])", r"\1", out)
    return out.strip(" -—–")
