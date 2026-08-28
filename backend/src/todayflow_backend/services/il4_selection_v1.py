"""IL-4 deterministic theme selection — product-side filter on IL-3 ranked themes.

Not meaning SoT. Not inside IL-3. Operates on the IL-4 pack produced by the attach
gateway and selects the subset that reaches a given surface / topic.

SoT: docs/astrology/IL4_SURFACE_ATTACH_V1.md (gateway)
Audit: docs/audits/IL3_TO_SURFACE_PAYLOAD_AUDIT_2026-08-25.md
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from todayflow_backend.profile_engine.models import ProfileTopicDomain


_SURFACE_CAPS: dict[str, int | None] = {
    "today": 1,
    "profile": 24,
    "compatibility": 24,
}

# Topic relevance is outside IL-3. Heuristic: keywords that map IL-3 object ids to
# product topic domains. Kept minimal and explicit so selection is reproducible.
_TOPIC_KEYWORDS: dict[ProfileTopicDomain, tuple[str, ...]] = {
    ProfileTopicDomain.RELATIONSHIPS: (
        "astro.object.venus",
        "astro.object.mars",
        "astro.object.moon",
        "astro.house.07",
        "astro.house.05",
        "astro.house.03",
    ),
    ProfileTopicDomain.INTIMACY: (
        "astro.object.venus",
        "astro.object.mars",
        "astro.object.pluto",
        "astro.house.07",
        "astro.house.08",
    ),
    ProfileTopicDomain.MONEY: (
        "astro.object.saturn",
        "astro.object.jupiter",
        "astro.object.venus",
        "astro.house.02",
        "astro.house.08",
        "astro.house.10",
    ),
    ProfileTopicDomain.WORK: (
        "astro.object.sun",
        "astro.object.saturn",
        "astro.object.mars",
        "astro.object.jupiter",
        "astro.object.mercury",
        "astro.house.06",
        "astro.house.10",
    ),
    ProfileTopicDomain.FAMILY: (
        "astro.object.moon",
        "astro.object.saturn",
        "astro.house.04",
        "astro.house.03",
        "astro.house.10",
    ),
    ProfileTopicDomain.BODY_ENERGY: (
        "astro.object.mars",
        "astro.object.sun",
        "astro.object.moon",
        "astro.house.01",
        "astro.house.06",
    ),
    ProfileTopicDomain.DECISION: (
        "astro.object.mercury",
        "astro.object.mars",
        "astro.object.saturn",
        "astro.object.jupiter",
        "astro.house.03",
    ),
    ProfileTopicDomain.HABITS_DISCIPLINE: (
        "astro.object.saturn",
        "astro.object.mars",
        "astro.object.moon",
        "astro.house.06",
        "astro.house.10",
    ),
    ProfileTopicDomain.INNER_STATE: (
        "astro.object.moon",
        "astro.object.neptune",
        "astro.object.pluto",
        "astro.house.12",
        "astro.house.04",
    ),
}


def _object_ids_from_line(line: Mapping[str, Any]) -> set[str]:
    """Collect all IL-3 object ids from a line's jobs and text."""
    found: set[str] = set()
    jobs = line.get("jobs") if isinstance(line.get("jobs"), Mapping) else {}
    for job in jobs.values():
        if isinstance(job, str):
            found.add(job)
        elif isinstance(job, Sequence) and not isinstance(job, str):
            for item in job:
                if isinstance(item, str):
                    found.add(item)
    text = str(line.get("text") or "").lower()
    for token in ("venus", "mars", "moon", "saturn", "jupiter", "mercury", "sun"):
        if token in text:
            found.add(f"astro.object.{token}")
    for n in range(1, 13):
        if f"house {n}" in text or f"house_{n:02d}" in text or f" {n} дом" in text:
            found.add(f"astro.house.{n:02d}")
    return found


def _line_matches_topic(line: Mapping[str, Any], topic: ProfileTopicDomain) -> bool:
    if topic == ProfileTopicDomain.GENERAL:
        return True
    keywords = _TOPIC_KEYWORDS.get(topic)
    if not keywords:
        return True
    ids = _object_ids_from_line(line)
    return any(kw in ids or kw in str(line.get("text") or "").lower() for kw in keywords)


def _line_band(line: Mapping[str, Any]) -> str:
    return str(line.get("band") or "").strip().lower()


def _line_rank(line: Mapping[str, Any]) -> int:
    try:
        return int(line.get("rank") or 0)
    except (TypeError, ValueError):
        return 0


def select_themes(
    pack: Mapping[str, Any] | None,
    *,
    surface: str,
    topic: ProfileTopicDomain | None = None,
    max_themes: int | None = None,
) -> dict[str, Any] | None:
    """Return a deterministic IL-4 pack slice for `surface` and optional topic.

    Rules:
    - `today`: keep the single primary (rank 1) line; no transit/natal distinction.
    - `profile`: keep natal band only; apply topic filter; cap at `max_themes` (default 24).
    - `compatibility`: keep both natal and transit bands; apply topic filter; cap at 24.
    - `dropped` constructions are never forwarded to the selected LLM-facing pack.
    """
    if not pack or not isinstance(pack, Mapping):
        return None

    cap = max_themes if max_themes is not None else _SURFACE_CAPS.get(surface, 24)
    effective_topic = topic or ProfileTopicDomain.GENERAL

    lines = [line for line in pack.get("lines") or [] if isinstance(line, Mapping)]

    if surface == "today":
        selected = [line for line in lines if _line_rank(line) == 1]
        if not selected and lines:
            selected = [lines[0]]
        selected = selected[:1]
    else:
        if surface == "profile":
            lines = [line for line in lines if _line_band(line) == "natal"]
        if effective_topic != ProfileTopicDomain.GENERAL:
            lines = [line for line in lines if _line_matches_topic(line, effective_topic)]
        lines.sort(key=_line_rank)
        selected = lines[:cap] if cap is not None else lines

    selected_pack: dict[str, Any] = {
        "surface": pack.get("surface") or surface,
        "tone": pack.get("tone"),
        "meaning_source": pack.get("meaning_source") or "il3_themes",
        "lines": [dict(line) for line in selected],
    }
    # Preserve dropped refusals for output validation (they are still stripped
    # from the LLM-facing payload by `compact_meaning`).
    if pack.get("dropped"):
        selected_pack["dropped"] = list(pack.get("dropped"))  # type: ignore[arg-type]
    return selected_pack
