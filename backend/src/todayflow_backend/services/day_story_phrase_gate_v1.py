"""Runtime coherence / grounding gate for day_story_v1.

Narrow contract gate — NOT today_language_quality_v1 (blocked until TL-1 calibration).
Checks: required fields, grounding to evidence, thesis→expect→trap→do/avoid coherence,
empty-formula chrome. Does NOT score «cinematic» quality.
"""

from __future__ import annotations

from typing import Any

# Canon empty formulas — reject chrome, not editorial voice.
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
        "headline_anchor",
        "primary_conflict",
        "events_lead",
        "expect",
        "trap",
        "direction",
        "story",
        "advantage",
        "abstain",
        "today_move",
        "vibe_closing",
        "global_period",
        "development_point",
        "primary_action",
        "evening_closure",
        "symbolic_note",
        "supports_story",
    ):
        val = str(story.get(key) or "").strip()
        if val:
            out.append((key, val))
    thesis = story.get("day_thesis")
    if isinstance(thesis, dict):
        lab = str(thesis.get("label_ru") or thesis.get("label") or "").strip()
        if lab:
            out.append(("day_thesis.label_ru", lab))
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


def find_structural_gaps(story: dict[str, Any]) -> list[str]:
    """Required editorial slots when story body is present."""
    gaps: list[str] = []
    story_body = str(story.get("story") or "").strip()
    if not story_body:
        return gaps
    thesis = story.get("day_thesis") if isinstance(story.get("day_thesis"), dict) else {}
    label = str(thesis.get("label_ru") or story.get("primary_conflict") or "").strip()
    if not label:
        gaps.append("day_thesis_missing")
    if not str(story.get("expect") or "").strip() and not str(story.get("direction") or "").strip():
        gaps.append("expect_missing")
    if not str(story.get("trap") or "").strip() and not str(story.get("abstain") or "").strip():
        gaps.append("trap_missing")
    # events_lead soft — prefer present but not hard-fail (ambient-only days)
    if not str(story.get("events_lead") or "").strip():
        gaps.append("events_lead_missing")
    return gaps


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
    """Coherence gate: empty formulas + hard structural gaps. events_lead is soft."""
    hits = find_empty_formula_hits(story, locale=locale)
    hard = [g for g in find_structural_gaps(story) if g != "events_lead_missing"]
    all_hits = hits + [f"structure:{g}" for g in hard]
    return (len(hits) == 0 and len(hard) == 0, all_hits)
