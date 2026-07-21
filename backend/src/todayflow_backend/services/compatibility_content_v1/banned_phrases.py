"""Banned clichés and meta-language for Compatibility RU copy."""

from __future__ import annotations

import re

BANNED_PHRASES_RU: tuple[str, ...] = (
    "вам важно найти баланс",
    "важно найти баланс",
    "ключ к гармонии",
    "ключ к успеху",
    "позвольте себе",
    "это союз двух разных энергий",
    "союз двух разных энергий",
    "при открытом общении всё возможно",
    "при открытом общении",
    "будьте в потоке",
    "доверьтесь вселенной",
    "слушайте энергию",
    "энергетический обмен",
    "ресурсное состояние",
    "высокий вибрац",
    "кармическ",
    "предназначен",
    "фатально",
    "судьба решила",
    "вам стоит поработать над собой",
    "нейротическ",
    "созависим",
    "токсичн",  # as clinical label dump — UI may use carefully elsewhere
    "llm",
    "промпт",
    "модель сгенер",
    "алгоритм",
    "расчёт показал",
    "по расчёту",
)

# Whole-token meta labels (avoid false positives like «реакции,»).
BANNED_TOKEN_RE_RU: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?<![а-яёa-z])ии(?![а-яёa-z])", re.I),
    re.compile(r"(?<![a-z])ai(?![a-z])", re.I),
)

BANNED_PHRASES_EN: tuple[str, ...] = (
    "find the balance",
    "key to harmony",
    "allow yourself",
    "two different energies",
    "with open communication anything is possible",
    "trust the universe",
    "listen to the energy",
    "llm",
    "prompt",
    "algorithm",
)


def find_banned_hits(text: str, *, locale: str = "ru") -> list[str]:
    raw = (text or "").lower()
    ru = not (locale or "ru").lower().startswith("en")
    phrases = BANNED_PHRASES_RU if ru else BANNED_PHRASES_EN
    hits: list[str] = []
    for p in phrases:
        if p in raw:
            hits.append(p)
    if ru:
        for pat in BANNED_TOKEN_RE_RU:
            if pat.search(raw):
                hits.append(pat.pattern)
    return hits
