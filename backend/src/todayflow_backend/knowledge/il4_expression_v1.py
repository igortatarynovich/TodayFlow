"""IL-4 Expression — already ranked themes → surface voice packs.

Not meaning. Not user relevance. Not pair catalog. Not runtime / LLM / Today wiring.
SoT: docs/astrology/IL4_EXPRESSION_V1.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from todayflow_backend.knowledge.il2_composition_v1 import ComposedFrame, ROLE_WEIGHTS
from todayflow_backend.knowledge.il3_interpretation_v1 import RankedTheme, ThemeList

SURFACES = frozenset({"today", "profile", "compatibility"})

TONES = {
    "today": "direct_grounded",
    "profile": "structural",
    "compatibility": "relational",
}

JOB_ORDER = ("what", "what_a", "what_b", "how", "where", "relation", "orientation")


@dataclass(frozen=True)
class VoiceLine:
    rank: int
    band: str
    role: str
    construction: str
    jobs: Mapping[str, tuple[str, ...]]
    subject_jobs: tuple[str, ...]
    modifier_jobs: tuple[str, ...]
    text: str
    transiting_object_id: str | None = None
    natal_object_id: str | None = None


@dataclass(frozen=True)
class ExpressionPack:
    surface: str
    tone: str
    lines: tuple[VoiceLine, ...]
    dropped: tuple[ComposedFrame, ...]
    meaning_source: str = "il3_themes"
    person_id: None = None
    user_relevance: None = None
    llm_chose_meaning: None = None


def _jobs(frame: ComposedFrame) -> dict[str, tuple[str, ...]]:
    return {name: payload.lemmas for name, payload in frame.jobs.items()}


def _roles(frame: ComposedFrame) -> tuple[tuple[str, ...], tuple[str, ...]]:
    weights = dict(frame.weights) or dict(ROLE_WEIGHTS.get(frame.construction, {}))
    present = {name: weights[name] for name in weights if name in frame.jobs}
    if not present:
        return tuple(frame.jobs), ()
    peak = max(present.values())
    subjects = tuple(name for name, weight in present.items() if weight == peak)
    modifiers = tuple(name for name, weight in present.items() if weight < peak)
    return subjects, modifiers


def _text(jobs: Mapping[str, tuple[str, ...]], *, construction: str | None = None) -> str:
    parts = []
    for name in JOB_ORDER:
        lemmas = jobs.get(name)
        if not lemmas:
            continue
        label = name
        if construction == "transit_to_natal":
            if name == "what_a":
                label = "transiting"
            elif name == "what_b":
                label = "target"
            elif name == "where":
                label = "context"
        parts.append(f"{label}={' · '.join(lemmas)}")
    return "; ".join(parts)


def _line(theme: RankedTheme) -> VoiceLine:
    jobs = _jobs(theme.frame)
    subjects, modifiers = _roles(theme.frame)
    return VoiceLine(
        rank=theme.rank,
        band=theme.band,
        role=theme.role,
        construction=theme.frame.construction,
        jobs=jobs,
        subject_jobs=subjects,
        modifier_jobs=modifiers,
        text=_text(jobs, construction=theme.frame.construction),
        transiting_object_id=theme.frame.transiting_object_id,
        natal_object_id=theme.frame.natal_object_id,
    )


def express(themes: ThemeList, surface: str) -> ExpressionPack:
    """Voice IL-3 themes for one surface. No user / CE / goals / LLM arguments."""
    if surface not in SURFACES:
        raise ValueError(f"unknown_surface:{surface}")
    selected = themes.themes[:1] if surface == "today" else themes.themes
    return ExpressionPack(
        surface=surface,
        tone=TONES[surface],
        lines=tuple(_line(theme) for theme in selected),
        dropped=themes.dropped,
        meaning_source="il3_themes",
        person_id=None,
        user_relevance=None,
        llm_chose_meaning=None,
    )


def meaning_is_unchanged(pack: ExpressionPack, themes: ThemeList) -> bool:
    if pack.person_id is not None or pack.user_relevance is not None:
        return False
    if pack.llm_chose_meaning is not None:
        return False
    if pack.meaning_source != "il3_themes":
        return False
    by_rank = {theme.rank: theme for theme in themes.themes}
    for line in pack.lines:
        theme = by_rank.get(line.rank)
        if theme is None:
            return False
        if line.construction != theme.frame.construction:
            return False
        if line.band != theme.band or line.role != theme.role:
            return False
        for name, lemmas in line.jobs.items():
            payload = theme.frame.jobs.get(name)
            if payload is None or payload.lemmas != lemmas:
                return False
        if set(line.jobs) != set(theme.frame.jobs):
            return False
    return True


def two_constructions_stay_two(left: VoiceLine, right: VoiceLine) -> bool:
    return left.construction != right.construction and set(left.jobs) != set(right.jobs)
