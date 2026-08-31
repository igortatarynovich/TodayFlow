"""Profile Decode IL-3 usage audit harness — Phase 2.6 preparation.

Does not call K3. Builds a deterministic synthetic IL-4 profile pack and
provides evaluators that measure which lines/themes a response (K3 or mock)
cited, ignored, or competed with.

SoT: docs/audits/PROFILE_SELECTION_K3_AUDIT_HARNESS_2026-08-29.md
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from todayflow_backend.profile_engine.models import ProfileTopicDomain
from todayflow_backend.services.il4_selection_v1 import _topics_for_line


# Basic English + Russian markers for the most common object ids.
# Heuristic: enough to catch citations in K3 responses without perfect lemmatization.
_OBJECT_ID_MARKERS: dict[str, tuple[str, ...]] = {
    "astro.object.sun": ("sun", "солнце"),
    "astro.object.moon": ("moon", "луна"),
    "astro.object.mercury": ("mercury", "меркурий"),
    "astro.object.venus": ("venus", "венера"),
    "astro.object.mars": ("mars", "марс"),
    "astro.object.jupiter": ("jupiter", "юпитер"),
    "astro.object.saturn": ("saturn", "сатурн"),
    "astro.object.uranus": ("uranus", "уран"),
    "astro.object.neptune": ("neptune", "нептун"),
    "astro.object.pluto": ("pluto", "плутон"),
    "astro.object.asc": ("asc", "ascedant", "асцендент"),
    "astro.object.mc": ("mc", "midheaven"),
    "astro.object.dsc": ("dsc", "descendant"),
    "astro.object.ic": ("ic"),
}

_SIGN_MARKERS: dict[str, tuple[str, ...]] = {
    "astro.sign.aries": ("aries", "овен"),
    "astro.sign.taurus": ("taurus", "телец"),
    "astro.sign.gemini": ("gemini", "близнецы"),
    "astro.sign.cancer": ("cancer", "рак"),
    "astro.sign.leo": ("leo", "лев"),
    "astro.sign.virgo": ("virgo", "дева"),
    "astro.sign.libra": ("libra", "весы"),
    "astro.sign.scorpio": ("scorpio", "скорпион"),
    "astro.sign.sagittarius": ("sagittarius", "стрелец"),
    "astro.sign.capricorn": ("capricorn", "козерог"),
    "astro.sign.aquarius": ("aquarius", "водолей"),
    "astro.sign.pisces": ("pisces", "рыбы"),
}


def _house_id_markers(house_id: str) -> tuple[str, ...]:
    try:
        n = int(house_id.split(".")[-1])
    except (TypeError, ValueError):
        return ()
    if not 1 <= n <= 12:
        return ()
    ordinals = {1: "1st", 2: "2nd", 3: "3rd"}
    ordinal = ordinals.get(n, f"{n}th")
    return (
        f"{n} дом",
        f"{n}-м дом",
        f"{ordinal} house",
        f"house {n}",
        f"house_{n:02d}",
        f"astro.house.{n:02d}",
    )


_MARKERS_LOOKUP: dict[str, tuple[str, ...]] = {**_OBJECT_ID_MARKERS, **_SIGN_MARKERS}


def _markers_for_object_id(obj_id: str) -> tuple[str, ...]:
    if obj_id.startswith("astro.house."):
        return _house_id_markers(obj_id)
    return _MARKERS_LOOKUP.get(obj_id, ())


def _collect_object_ids(line: Mapping[str, Any]) -> set[str]:
    found: set[str] = set()
    jobs = line.get("jobs")
    if not isinstance(jobs, Mapping):
        return found
    for payload in jobs.values():
        if isinstance(payload, str):
            found.add(payload)
        elif isinstance(payload, Sequence) and not isinstance(payload, str):
            for item in payload:
                if isinstance(item, str):
                    found.add(item)
    return found


def _line_markers(
    line: Mapping[str, Any],
    *,
    object_match: bool = True,
    text_match: bool = True,
) -> set[str]:
    """Return lowercase citation markers for a line."""
    markers: set[str] = set()
    if object_match:
        for obj_id in _collect_object_ids(line):
            markers.update(m.lower() for m in _markers_for_object_id(obj_id))
    if text_match:
        text = str(line.get("text") or "").lower()
        if text:
            markers.add(text)
            # also add each word
            markers.update(text.split())
    return markers


def _cited(response_text: str, markers: set[str]) -> bool:
    normalized = str(response_text or "").lower()
    if not normalized or not markers:
        return False
    for marker in markers:
        if not marker:
            continue
        # Word boundary for short tokens (planet names, house numbers), otherwise substring.
        pattern = re.escape(marker)
        if len(marker) <= 15:
            regex = r"(?:^|\W|_)" + pattern + r"(?:$|\W|_)"
        else:
            regex = pattern
        if re.search(regex, normalized):
            return True
    return False


def make_synthetic_profile_pack(
    lines: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return a deterministic 24-line natal profile pack for audit fixtures.

    The pack mirrors the shape produced by the IL-4 surface attach gateway
    after `select_themes(surface="profile")`. Lines are natal-only, ranked,
    and each carries a unique combination of object ids so per-line citation is
    measurable.
    """
    if lines is None:
        lines = _default_natal_lines()
    return {
        "surface": "profile",
        "tone": "structural",
        "meaning_source": "il3_themes",
        "lines": [dict(line) for line in lines],
        "dropped": [],
    }


def _default_natal_lines() -> list[dict[str, Any]]:
    planets = (
        "sun",
        "moon",
        "mercury",
        "venus",
        "mars",
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
        "pluto",
    )
    signs = (
        "aries",
        "taurus",
        "gemini",
        "cancer",
        "leo",
        "virgo",
        "libra",
        "scorpio",
        "sagittarius",
        "capricorn",
    )
    houses = list(range(1, 13))
    lines: list[dict[str, Any]] = []

    for i, planet in enumerate(planets):
        # planet_in_house
        house = houses[i % 12]
        lines.append(
            {
                "rank": len(lines) + 1,
                "band": "natal",
                "role": "primary" if i == 0 else "supporting",
                "construction": "planet_in_house",
                "jobs": {
                    "what": [f"astro.object.{planet}"],
                    "where": [f"astro.house.{house:02d}"],
                },
                "text": f"{planet.title()} in {house}th house",
            }
        )
        # planet_in_sign
        sign = signs[i % 12]
        lines.append(
            {
                "rank": len(lines) + 1,
                "band": "natal",
                "role": "supporting",
                "construction": "planet_in_sign",
                "jobs": {
                    "what": [f"astro.object.{planet}"],
                    "how": [f"astro.sign.{sign}"],
                },
                "text": f"{planet.title()} in {sign}",
            }
        )

    # A few natal aspects to make the pack closer to real IL-4 output.
    aspects = (
        ("sun", "moon", "trine"),
        ("mercury", "mars", "square"),
        ("venus", "saturn", "opposition"),
        ("jupiter", "pluto", "conjunction"),
    )
    for a, b, aspect in aspects:
        lines.append(
            {
                "rank": len(lines) + 1,
                "band": "natal",
                "role": "supporting",
                "construction": "aspect_pair",
                "jobs": {
                    "what_a": [f"astro.object.{a}"],
                    "what_b": [f"astro.object.{b}"],
                    "relation": [f"astro.aspect.{aspect}"],
                },
                "text": f"{a.title()} {aspect} {b.title()}",
            }
        )

    return lines


def evaluate_citation(
    response_text: str,
    pack: Mapping[str, Any],
    *,
    object_match: bool = True,
    text_match: bool = True,
) -> dict[str, Any]:
    """Compare a K3/mocked response against the IL-4 pack and return citation stats.

    Returns:
        - total_lines, cited_count, ignored_count, coverage_ratio
        - cited: list of cited line dicts
        - ignored: list of ignored line dicts
        - cited_by_topic / ignored_by_topic: counts per ProfileTopicDomain
        - topic_coverage_ratio: cited / (cited + ignored) per topic
    """
    lines = [line for line in pack.get("lines") or [] if isinstance(line, Mapping)]
    cited: list[dict[str, Any]] = []
    ignored: list[dict[str, Any]] = []
    line_details: list[dict[str, Any]] = []

    for line in lines:
        markers = _line_markers(line, object_match=object_match, text_match=text_match)
        is_cited = _cited(response_text, markers)
        record = {
            "rank": line.get("rank"),
            "text": line.get("text"),
            "cited": is_cited,
            "markers": sorted(markers),
            "topics": sorted(t.value for t in _topics_for_line(line)),
        }
        line_details.append(record)
        if is_cited:
            cited.append(record)
        else:
            ignored.append(record)

    total = len(lines)
    coverage_ratio = (len(cited) / total) if total else 0.0

    all_topics = set(ProfileTopicDomain) - {ProfileTopicDomain.GENERAL}
    cited_by_topic: dict[str, int] = {t.value: 0 for t in all_topics}
    ignored_by_topic: dict[str, int] = {t.value: 0 for t in all_topics}
    for record in cited:
        for topic_value in record["topics"]:
            if topic_value in cited_by_topic:
                cited_by_topic[topic_value] += 1
    for record in ignored:
        for topic_value in record["topics"]:
            if topic_value in ignored_by_topic:
                ignored_by_topic[topic_value] += 1

    topic_coverage_ratio: dict[str, float] = {}
    for topic_value in cited_by_topic:
        denom = cited_by_topic[topic_value] + ignored_by_topic[topic_value]
        topic_coverage_ratio[topic_value] = (
            cited_by_topic[topic_value] / denom if denom else 0.0
        )

    return {
        "total_lines": total,
        "cited_count": len(cited),
        "ignored_count": len(ignored),
        "coverage_ratio": coverage_ratio,
        "cited": cited,
        "ignored": ignored,
        "line_details": line_details,
        "cited_by_topic": cited_by_topic,
        "ignored_by_topic": ignored_by_topic,
        "topic_coverage_ratio": topic_coverage_ratio,
    }


def audit_report(
    response_text: str,
    pack: Mapping[str, Any] | None = None,
    *,
    response_source: str = "k3",
) -> dict[str, Any]:
    """High-level report for the tracker / release plan."""
    pack = pack if pack is not None else make_synthetic_profile_pack()
    evaluation = evaluate_citation(response_text, pack)
    return {
        "response_source": response_source,
        "pack_shape": {
            "surface": pack.get("surface"),
            "tone": pack.get("tone"),
            "line_count": evaluation["total_lines"],
        },
        "summary": {
            "cited": evaluation["cited_count"],
            "ignored": evaluation["ignored_count"],
            "coverage_ratio": round(evaluation["coverage_ratio"], 3),
            "topic_coverage_ratio": {
                k: round(v, 3) for k, v in evaluation["topic_coverage_ratio"].items()
            },
        },
        "ignored_lines": [
            {"rank": line["rank"], "text": line["text"], "topics": line["topics"]}
            for line in evaluation["ignored"]
        ],
    }
