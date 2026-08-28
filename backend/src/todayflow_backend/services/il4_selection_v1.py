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

# Topic relevance is outside IL-3. The maps below are deterministic,
# product-side heuristics that connect IL-3 object ids (planets, houses, angles,
# signs) to ProfileTopicDomain. They are reproducible, do not overwrite IL-3
# meaning, and are intentionally kept separate from the interpretation canon.
_T = ProfileTopicDomain

ASTRO_OBJECT_TOPIC_MAP: dict[str, tuple[_T, ...]] = {
    # Planets
    "astro.object.sun": (_T.WORK, _T.BODY_ENERGY, _T.HABITS_DISCIPLINE),
    "astro.object.moon": (_T.RELATIONSHIPS, _T.FAMILY, _T.INNER_STATE, _T.BODY_ENERGY, _T.HABITS_DISCIPLINE),
    "astro.object.mercury": (_T.DECISION, _T.WORK, _T.RELATIONSHIPS),
    "astro.object.venus": (_T.RELATIONSHIPS, _T.INTIMACY, _T.MONEY),
    "astro.object.mars": (_T.BODY_ENERGY, _T.WORK, _T.INTIMACY, _T.DECISION, _T.HABITS_DISCIPLINE),
    "astro.object.jupiter": (_T.MONEY, _T.WORK, _T.DECISION, _T.RELATIONSHIPS),
    "astro.object.saturn": (_T.WORK, _T.MONEY, _T.FAMILY, _T.HABITS_DISCIPLINE, _T.DECISION),
    "astro.object.uranus": (_T.DECISION, _T.INNER_STATE, _T.WORK, _T.BODY_ENERGY),
    "astro.object.neptune": (_T.INNER_STATE, _T.RELATIONSHIPS),
    "astro.object.pluto": (_T.INNER_STATE, _T.INTIMACY, _T.MONEY),
    # Angles
    "astro.object.asc": (_T.BODY_ENERGY, _T.INNER_STATE, _T.WORK, _T.DECISION),
    "astro.object.mc": (_T.WORK, _T.MONEY, _T.FAMILY),
    "astro.object.dsc": (_T.RELATIONSHIPS, _T.INTIMACY),
    "astro.object.ic": (_T.FAMILY, _T.INNER_STATE),
}

_HOUSE_TOPICS: dict[int, tuple[_T, ...]] = {
    1: (_T.BODY_ENERGY, _T.INNER_STATE, _T.DECISION),
    2: (_T.MONEY,),
    3: (_T.DECISION, _T.RELATIONSHIPS),
    4: (_T.FAMILY, _T.INNER_STATE),
    5: (_T.INTIMACY, _T.RELATIONSHIPS, _T.INNER_STATE),
    6: (_T.WORK, _T.BODY_ENERGY, _T.HABITS_DISCIPLINE),
    7: (_T.RELATIONSHIPS, _T.INTIMACY),
    8: (_T.INTIMACY, _T.MONEY, _T.INNER_STATE),
    9: (_T.DECISION, _T.WORK, _T.INNER_STATE),
    10: (_T.WORK, _T.MONEY, _T.FAMILY),
    11: (_T.RELATIONSHIPS, _T.WORK, _T.INNER_STATE),
    12: (_T.INNER_STATE,),
}
for _n, _topics in _HOUSE_TOPICS.items():
    ASTRO_OBJECT_TOPIC_MAP[f"astro.house.{_n:02d}"] = _topics

SIGN_TOPIC_MAP: dict[str, tuple[_T, ...]] = {
    "astro.sign.aries": (_T.BODY_ENERGY, _T.DECISION),
    "astro.sign.taurus": (_T.MONEY, _T.BODY_ENERGY),
    "astro.sign.gemini": (_T.DECISION, _T.RELATIONSHIPS),
    "astro.sign.cancer": (_T.FAMILY, _T.INNER_STATE),
    "astro.sign.leo": (_T.RELATIONSHIPS, _T.INTIMACY, _T.BODY_ENERGY),
    "astro.sign.virgo": (_T.WORK, _T.BODY_ENERGY, _T.HABITS_DISCIPLINE),
    "astro.sign.libra": (_T.RELATIONSHIPS, _T.INTIMACY, _T.DECISION),
    "astro.sign.scorpio": (_T.INTIMACY, _T.MONEY, _T.INNER_STATE),
    "astro.sign.sagittarius": (_T.DECISION, _T.INNER_STATE),
    "astro.sign.capricorn": (_T.WORK, _T.MONEY, _T.HABITS_DISCIPLINE),
    "astro.sign.aquarius": (_T.DECISION, _T.RELATIONSHIPS, _T.INNER_STATE),
    "astro.sign.pisces": (_T.INNER_STATE, _T.RELATIONSHIPS),
}

_TOPIC_TEXT_HINTS: dict[ProfileTopicDomain, tuple[str, ...]] = {
    _T.RELATIONSHIPS: ("relationship", "love", "partner", "partnership", "отношения", "любовь", "партнёр"),
    _T.INTIMACY: ("intimacy", "sex", "sexuality", "closeness", "близость", "сексуальность", "интим"),
    _T.MONEY: ("money", "finance", "wealth", "income", "деньги", "финансы", "доход"),
    _T.WORK: ("work", "career", "job", "profession", "работа", "карьера", "профессия"),
    _T.FAMILY: ("family", "home", "parent", "child", "род", "семья", "родители", "дом"),
    _T.BODY_ENERGY: ("body", "energy", "vitality", "health", "physical", "тело", "энергия", "здоровье"),
    _T.DECISION: ("decision", "choice", "judgment", "mind", "reasoning", "решение", "выбор", "мысль"),
    _T.INNER_STATE: ("inner", "emotion", "psyche", "unconscious", "spiritual", "внутренний", "психика", "духовный"),
    _T.HABITS_DISCIPLINE: ("habit", "discipline", "routine", "structure", "привычка", "дисциплина", "режим"),
}


_OBJECT_TOKENS: tuple[str, ...] = (
    "sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"
)
_ORDINAL_HOUSE_SUFFIXES: tuple[str, ...] = ("st", "nd", "rd", "th")


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
    for token in _OBJECT_TOKENS:
        if token in text:
            found.add(f"astro.object.{token}")
    for n in range(1, 13):
        house_id = f"astro.house.{n:02d}"
        if house_id in text:
            found.add(house_id)
        if f"house_{n:02d}" in text or f"house {n}" in text or f" {n} дом" in text:
            found.add(house_id)
        for suffix in _ORDINAL_HOUSE_SUFFIXES:
            if f"{n}{suffix} house" in text or f" {n}{suffix} house" in text:
                found.add(house_id)
    for token in ("asc", "ascedant", "асцендент"):
        if token in text:
            found.add("astro.object.asc")
    for token in ("mc", "midheaven"):
        if token in text:
            found.add("astro.object.mc")
    for sign in (
        "aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio",
        "sagittarius", "capricorn", "aquarius", "pisces",
    ):
        if sign in text:
            found.add(f"astro.sign.{sign}")
    return found


def _topics_for_line(line: Mapping[str, Any]) -> set[ProfileTopicDomain]:
    """Return the set of ProfileTopicDomain a line is relevant to."""
    topics: set[ProfileTopicDomain] = set()
    for obj_id in _object_ids_from_line(line):
        if obj_id in ASTRO_OBJECT_TOPIC_MAP:
            topics.update(ASTRO_OBJECT_TOPIC_MAP[obj_id])
        elif obj_id in SIGN_TOPIC_MAP:
            topics.update(SIGN_TOPIC_MAP[obj_id])
    text = str(line.get("text") or "").lower()
    for topic, hints in _TOPIC_TEXT_HINTS.items():
        if any(hint in text for hint in hints):
            topics.add(topic)
    return topics


def _line_matches_topic(line: Mapping[str, Any], topic: ProfileTopicDomain) -> bool:
    if topic == ProfileTopicDomain.GENERAL:
        return True
    return topic in _topics_for_line(line)


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
