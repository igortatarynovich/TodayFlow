"""D2 — weighted style-bucket scoring for life_spheres projector.

Replaces first-match keyword classification.
"""

from __future__ import annotations

import re
from typing import Any

# Preferred bucket lists per sphere (order = tie-break).
LOVE_BUCKETS = ("care", "clarity", "autonomy", "depth", "pace", "general")
MONEY_BUCKETS = ("security", "structure", "exchange", "growth", "general")
DECISIONS_BUCKETS = ("speed", "structure", "consensus", "analysis", "general")

# cue → (bucket, weight). Longer / more specific cues listed first for scanning.
# Negative weights reduce a bucket when conflict phrases appear.
_CUE_TABLE: list[tuple[str, str, int]] = [
    # --- decisions: conflict & speed before bare «анализ» ---
    ("скорость важнее", "speed", 3),
    ("важнее долгого анализа", "speed", 3),
    ("важнее анализа", "speed", 3),
    ("без зависания", "speed", 2),
    ("не зависать", "speed", 2),
    ("важнее анализа", "analysis", -3),
    ("долгого анализа", "analysis", -2),
    ("без зависания", "analysis", -2),
    ("не зависать", "analysis", -2),
    ("скорость", "speed", 2),
    ("быстр", "speed", 1),
    ("сразу", "speed", 1),
    ("да/нет", "speed", 1),
    ("анализ", "analysis", 1),
    ("разбор", "analysis", 1),
    ("взвес", "analysis", 1),
    ("критер", "structure", 2),  # criterion frame → structure unless analysis-only
    ("дедлайн", "structure", 2),
    ("рамк", "structure", 2),
    ("структур", "structure", 2),
    ("письмен", "structure", 1),
    ("соглас", "consensus", 2),
    ("вместе", "consensus", 1),
    ("мнен", "consensus", 1),
    # --- love ---
    ("тёпл", "care", 2),
    ("тепл", "care", 2),
    ("забот", "care", 2),
    ("поддерж", "care", 2),
    ("мягк", "care", 1),
    ("ясн", "clarity", 2),
    ("прям", "clarity", 2),
    ("честн", "clarity", 2),
    ("предсказ", "clarity", 2),
    ("без намёк", "clarity", 1),
    ("автоном", "autonomy", 3),
    ("пространств", "autonomy", 2),
    ("границ", "autonomy", 2),
    ("без провер", "autonomy", 2),
    ("глубин", "depth", 2),
    ("смысл", "depth", 1),
    ("медленн", "pace", 2),
    ("медлен", "pace", 2),
    ("свой темп", "pace", 2),
    ("темп", "pace", 1),
    ("ритм", "pace", 1),
    # --- money ---
    ("безопас", "security", 2),
    ("устойчив", "security", 2),
    ("стабил", "security", 2),
    ("запас", "security", 2),
    ("структур", "structure", 2),
    ("порядок", "structure", 2),
    ("учёт", "structure", 2),
    ("правил", "structure", 1),
    ("регуляр", "structure", 1),
    ("обмен", "exchange", 2),
    ("ценност", "exchange", 1),
    ("цена", "exchange", 1),
    ("вклад", "exchange", 1),
    ("рост", "growth", 2),
    ("смел", "growth", 1),
    ("расширен", "growth", 1),
    ("риск", "growth", 1),
]


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def score_style_buckets(
    style: str,
    *,
    allowed: tuple[str, ...],
) -> dict[str, Any]:
    """Return primary/secondary buckets + score trace."""
    text = _norm(style)
    scores: dict[str, int] = {b: 0 for b in allowed if b != "general"}
    hits: list[dict[str, Any]] = []
    matched_spans: set[tuple[int, int]] = set()

    # Prefer longer cues first
    cues = sorted(_CUE_TABLE, key=lambda x: len(x[0]), reverse=True)
    for cue, bucket, weight in cues:
        if bucket not in scores and bucket != "general":
            continue
        if bucket not in scores:
            continue
        start = 0
        while True:
            idx = text.find(cue, start)
            if idx < 0:
                break
            span = (idx, idx + len(cue))
            # Allow same span to apply to different buckets (e.g. conflict ±),
            # but not duplicate same cue+bucket.
            key = (idx, bucket, cue)
            if any(h.get("_key") == key for h in hits):
                start = idx + 1
                continue
            scores[bucket] = scores.get(bucket, 0) + weight
            hits.append(
                {
                    "cue": cue,
                    "bucket": bucket,
                    "weight": weight,
                    "_key": key,
                }
            )
            matched_spans.add(span)
            start = idx + len(cue)

    # Clean keys for meta
    for h in hits:
        h.pop("_key", None)

    ranked = sorted(
        ((b, s) for b, s in scores.items() if b in allowed),
        key=lambda x: (-x[1], allowed.index(x[0]) if x[0] in allowed else 99),
    )
    if not ranked or ranked[0][1] <= 0:
        primary = "general" if "general" in allowed else (allowed[0] if allowed else "general")
        secondary = None
    else:
        primary = ranked[0][0]
        secondary = ranked[1][0] if len(ranked) > 1 and ranked[1][1] > 0 else None

    return {
        "primary": primary,
        "secondary": secondary,
        "scores": {b: scores.get(b, 0) for b in scores},
        "hits": hits,
    }


def classify_style_scored(style: str, *, domain: str) -> dict[str, Any]:
    allowed = {
        "love": LOVE_BUCKETS,
        "money": MONEY_BUCKETS,
        "decisions": DECISIONS_BUCKETS,
    }.get(domain, ("general",))
    result = score_style_buckets(style, allowed=allowed)
    result["domain"] = domain
    return result
