"""Banned clichés / diagnoses / meta for Profile RU copy."""

from __future__ import annotations

import re

BANNED_PHRASES_RU: tuple[str, ...] = (
    "вам важно найти баланс",
    "ключ к гармонии",
    "позвольте себе",
    "будьте в потоке",
    "доверьтесь вселенной",
    "ресурсное состояние",
    "высокий вибрац",
    "кармическ",
    "нейротическ",
    "созависим",
    "пограничн",
    "биполяр",
    "депрессивн расстрой",
    "вы всегда",
    "вы никогда",
    "паспорт знака",
    "как типичный",
)

BANNED_TOKEN_RE: tuple[re.Pattern[str], ...] = (
    re.compile(r"он\(а\)", re.I),
    re.compile(r"его\(её\)", re.I),
)


def find_banned_hits(text: str) -> list[str]:
    raw = (text or "").lower()
    hits = [p for p in BANNED_PHRASES_RU if p in raw]
    for pat in BANNED_TOKEN_RE:
        if pat.search(text or ""):
            hits.append(f"gender_hack:{pat.pattern}")
    return hits


def find_depth_overclaims(text: str, *, source_depth: str) -> list[str]:
    blob = (text or "").lower()
    errs: list[str] = []
    if source_depth == "birth_data_only":
        for p in (
            "вы всегда в стрессе",
            "вы обычно откладываете",
            "в последние недели",
            "по вашим check-in",
            "из дневника видно",
        ):
            if p in blob:
                errs.append(f"depth_overclaim:{p}")
    if source_depth in ("birth_data_only", "onboarding_answers"):
        for p in ("в последние недели вы чаще", "повторяющийся паттерн последних"):
            if p in blob:
                errs.append(f"depth_overclaim:{p}")
    return errs
