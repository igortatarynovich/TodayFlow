"""IL-3 Interpretation Engine — sky facts → ranked astrological themes.

Person-blind. Not user relevance. Not pair catalog. Not runtime / LLM / Today wiring.
SoT: docs/astrology/IL3_INTERPRETATION_ENGINE_V1.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from todayflow_backend.knowledge.il2_composition_v1 import (
    ComposedFrame,
    compose_aspect_pair,
    compose_planet_at_angle,
    compose_planet_in_house,
    compose_planet_in_sign,
    compose_transit_through_house,
    compose_transit_to_natal,
)

TRANSIT_CONSTRUCTIONS = frozenset({"transit_to_natal", "transit_through_house"})


@dataclass(frozen=True)
class SkyFact:
    construction: str
    parts: tuple[str, ...]


@dataclass(frozen=True)
class RankedTheme:
    rank: int
    band: str
    role: str
    frame: ComposedFrame
    sky_index: int


@dataclass(frozen=True)
class ThemeList:
    themes: tuple[RankedTheme, ...]
    dropped: tuple[ComposedFrame, ...]
    essay: None = None
    person_id: None = None
    user_relevance: None = None


def _compose(catalog: Mapping[str, dict], fact: SkyFact) -> ComposedFrame:
    construction, parts = fact.construction, fact.parts
    if construction == "planet_in_sign":
        return compose_planet_in_sign(catalog, parts[0], parts[1])
    if construction == "planet_in_house":
        return compose_planet_in_house(catalog, parts[0], parts[1])
    if construction == "planet_at_angle":
        return compose_planet_at_angle(catalog, parts[0], parts[1])
    if construction == "aspect_pair":
        return compose_aspect_pair(catalog, parts[0], parts[1], parts[2])
    if construction == "transit_to_natal":
        if len(parts) == 4:
            return compose_transit_to_natal(catalog, parts[0], parts[1], parts[2], parts[3])
        return compose_transit_to_natal(catalog, parts[0], parts[1], parts[2])
    if construction == "transit_through_house":
        return compose_transit_through_house(catalog, parts[0], parts[1])
    raise ValueError(f"unknown_construction:{construction}")


def _band(frame: ComposedFrame) -> str:
    if frame.temporal_class == "transit" or frame.construction in TRANSIT_CONSTRUCTIONS:
        return "transit"
    return "natal"


def interpret(catalog: Mapping[str, dict], facts: Sequence[SkyFact]) -> ThemeList:
    """Rank IL-2 frames for this sky. No user / CE / goals arguments."""
    composed: list[tuple[int, ComposedFrame]] = []
    dropped: list[ComposedFrame] = []
    for index, fact in enumerate(facts):
        frame = _compose(catalog, fact)
        if frame.status == "composed":
            composed.append((index, frame))
        else:
            dropped.append(frame)

    composed.sort(key=lambda item: (0 if _band(item[1]) == "transit" else 1, item[0]))

    themes: list[RankedTheme] = []
    for rank, (sky_index, frame) in enumerate(composed, start=1):
        themes.append(
            RankedTheme(
                rank=rank,
                band=_band(frame),
                role="primary" if rank == 1 else "supporting",
                frame=frame,
                sky_index=sky_index,
            )
        )
    return ThemeList(
        themes=tuple(themes),
        dropped=tuple(dropped),
        essay=None,
        person_id=None,
        user_relevance=None,
    )


def two_constructions_stay_two(left: RankedTheme, right: RankedTheme) -> bool:
    return (
        left.frame.construction != right.frame.construction
        and left.frame.jobs.keys() != right.frame.jobs.keys()
    )


def rank_is_sky_internal(result: ThemeList) -> bool:
    if result.person_id is not None or result.user_relevance is not None:
        return False
    if result.essay is not None:
        return False
    bands = [theme.band for theme in result.themes]
    if "transit" in bands and "natal" in bands:
        last_transit = max(i for i, band in enumerate(bands) if band == "transit")
        first_natal = min(i for i, band in enumerate(bands) if band == "natal")
        if last_transit > first_natal:
            return False
    return True
