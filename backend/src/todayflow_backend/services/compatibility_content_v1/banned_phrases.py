"""Banned clichés, meta-language, harsh labels, gender hacks for Compatibility RU."""

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
    "токсичн",
    "llm",
    "промпт",
    "модель сгенер",
    "алгоритм",
    "расчёт показал",
    "по расчёту",
    # Harsh / demeaning (v1.1) — not colloquial «без истерик»
    "истеричка",
    "ты не истеричка",
    "ты истерик",
    "эмоциональная глухота",
    "на разрыв аорты",
    "разбежитесь, даже не начав",
    "война с миром",
)

# Whole-token meta labels (avoid false positives like «реакции,»).
BANNED_TOKEN_RE_RU: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?<![а-яёa-z])ии(?![а-яёa-z])", re.I),
    re.compile(r"(?<![a-z])ai(?![a-z])", re.I),
)

# Mechanical gender dual forms — never in user-facing copy.
GENDER_HACK_RE: tuple[re.Pattern[str], ...] = (
    re.compile(r"он\(а\)", re.I),
    re.compile(r"она\(он\)", re.I),
    re.compile(r"его\(её\)", re.I),
    re.compile(r"её\(его\)", re.I),
    re.compile(r"его\(ее\)", re.I),
    re.compile(r"ее\(его\)", re.I),
)

# Registered must not answer premium continue/verdict questions.
REGISTERED_PREMIUM_LEAK_RE: tuple[re.Pattern[str], ...] = (
    re.compile(r"продолжать смысла нет", re.I),
    re.compile(r"смысла нет продолжать", re.I),
    re.compile(r"не стоит продолжать", re.I),
    re.compile(r"стоит ли продолжать", re.I),
    re.compile(r"если думаешь[, ]*стоит ли продолжать", re.I),
    re.compile(r"готова ли ты к отношениям", re.I),
    re.compile(r"готов ли ты к отношениям", re.I),
    re.compile(r"разбежитесь", re.I),
    re.compile(r"вердикт\s*:", re.I),
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
        for pat in GENDER_HACK_RE:
            if pat.search(text or ""):
                hits.append(f"gender_hack:{pat.pattern}")
    return hits


def find_registered_premium_leaks(text: str) -> list[str]:
    hits: list[str] = []
    for pat in REGISTERED_PREMIUM_LEAK_RE:
        if pat.search(text or ""):
            hits.append(f"registered_premium_leak:{pat.pattern}")
    return hits
