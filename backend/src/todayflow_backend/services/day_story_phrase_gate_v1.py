"""Runtime phrase gate for day_story_v1 — empty formulas banned beyond prompt text."""

from __future__ import annotations

import re
from typing import Any

# Canon empty formulas (EXPLAINABLE_COMPUTATION) — reject in user-facing story fields.
EMPTY_FORMULA_PHRASES_RU: tuple[str, ...] = (
    "довериться потоку",
    "доверься потоку",
    "устойчивость через ритм",
    "мягко проявить себя",
    "удерживать внутреннюю опору",
    "выбрать главное",
    "один важный разговор",
    "одно дело до конца",
    "позволь себе",
    "важно помнить",
    "возможно, стоит",
    "вселенная",
    "в потоке",
    "избегать: семья",
    "избегать: работа",
    "можно: работа",
    "можно: семья",
    # Checklist / template chrome (Voice canon §0)
    "сегодня сильнее",
    "опирайся на это",
    "опирайся на",
    "зона риска",
    "направить внимание",
    "не распыляйся",
    "держи фокус",
    "чего ждать",
    "чего не ждать",
    "где осторожнее",
    "также поддержано",
    "выбери один короткий шаг",
)

EMPTY_FORMULA_PHRASES_EN: tuple[str, ...] = (
    "trust the flow",
    "go with the flow",
    "resilience through rhythm",
    "gently express yourself",
    "hold your inner support",
    "choose what matters",
    "one important conversation",
    "one thing to the end",
    "allow yourself",
    "the universe",
)


def _collect_user_facing_strings(story: dict[str, Any]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for key in (
        "theme",
        "direction",
        "story",
        "advantage",
        "abstain",
        "today_move",
        "global_period",
        "development_point",
        "primary_action",
        "evening_closure",
        "symbolic_note",
    ):
        val = str(story.get(key) or "").strip()
        if val:
            out.append((key, val))
    for key in ("do", "avoid"):
        items = story.get(key)
        if isinstance(items, list):
            for i, item in enumerate(items):
                text = str(item or "").strip()
                if text:
                    out.append((f"{key}[{i}]", text))
    domains = story.get("domains")
    if isinstance(domains, dict):
        for did, lens in domains.items():
            if not isinstance(lens, dict):
                continue
            if str(lens.get("evidence_status") or "") == "absent":
                continue
            for slot in ("status", "opportunity", "risk", "action"):
                text = str(lens.get(slot) or "").strip()
                if text:
                    out.append((f"domains.{did}.{slot}", text))
    return out


def find_empty_formula_hits(story: dict[str, Any], *, locale: str = "ru") -> list[str]:
    phrases = EMPTY_FORMULA_PHRASES_RU
    if (locale or "").lower().startswith("en"):
        phrases = EMPTY_FORMULA_PHRASES_EN
    hits: list[str] = []
    for path, text in _collect_user_facing_strings(story):
        low = text.lower()
        for phrase in phrases:
            if phrase in low:
                hits.append(f"{path}: «{phrase}»")
    return hits


def day_story_passes_phrase_gate(story: dict[str, Any], *, locale: str = "ru") -> tuple[bool, list[str]]:
    hits = find_empty_formula_hits(story, locale=locale)
    return (len(hits) == 0, hits)
