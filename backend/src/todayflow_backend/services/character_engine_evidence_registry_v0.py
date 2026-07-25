"""Deterministic Evidence candidate registry for Character Engine Stage 1.

Rules emit stable claim_kind + thesis_key — LLM must not invent thesis_key later.
No identity_core / scenes / compass / career|love|money roots.

Staging eval v0 (2026-07-25): narrowed OR-on-life-path matches — autonomy/analysis
require sun pattern; life_path only strengthens. Dropped redundant air-sun direction
claim (overlapped autonomy for Aquarius). See CHARACTER_ENGINE_STAGE01_STAGING_EVAL_V0.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from todayflow_backend.services.character_engine_stage0_facts_v0 import element_for_sign


@dataclass(frozen=True)
class EvidenceRule:
    rule_key: str
    claim_kind: str
    thesis_key: str
    capability_floor: str
    confidence: str
    match: Callable[[dict[str, dict[str, Any]]], bool]
    supporting_fact_types: tuple[str, ...]
    edge_type: str = "supports"
    strengthen_fact_types: tuple[str, ...] = ()
    qualify_fact_types: tuple[str, ...] = ()
    contradict_fact_types: tuple[str, ...] = ()


def _sign_of(facts_by_type: dict[str, dict[str, Any]], fact_type: str) -> str | None:
    row = facts_by_type.get(fact_type)
    if not row:
        return None
    value = row.get("value")
    if isinstance(value, dict):
        return str(value.get("sign") or "").strip().lower() or None
    return str(value).strip().lower() or None


def _number_of(facts_by_type: dict[str, dict[str, Any]], fact_type: str) -> int | None:
    row = facts_by_type.get(fact_type)
    if not row:
        return None
    try:
        return int(row.get("value"))
    except (TypeError, ValueError):
        return None


_AUTONOMY_SUNS = frozenset({"aquarius", "aries", "sagittarius"})
_ANALYSIS_SUNS = frozenset({"virgo", "capricorn", "scorpio"})
_STRUCTURE_PATHS = frozenset({4, 8, 22})


def _rule_autonomy(facts: dict[str, dict[str, Any]]) -> bool:
    # Sun pattern required — life_path alone must not mint autonomy for most charts.
    return _sign_of(facts, "planet_sign:sun") in _AUTONOMY_SUNS


def _rule_analysis(facts: dict[str, dict[str, Any]]) -> bool:
    return _sign_of(facts, "planet_sign:sun") in _ANALYSIS_SUNS


def _rule_emotional_water(facts: dict[str, dict[str, Any]]) -> bool:
    moon = _sign_of(facts, "planet_sign:moon")
    return element_for_sign(moon) == "water"


def _rule_freedom_vs_stability(facts: dict[str, dict[str, Any]]) -> bool:
    if not _rule_autonomy(facts):
        return False
    moon = _sign_of(facts, "planet_sign:moon")
    lp = _number_of(facts, "life_path_number")
    moon_el = element_for_sign(moon)
    return moon_el in {"earth", "water"} or (lp in _STRUCTURE_PATHS)


EVIDENCE_RULES_V0: tuple[EvidenceRule, ...] = (
    EvidenceRule(
        rule_key="autonomy_need_v0",
        claim_kind="autonomy_need",
        thesis_key="autonomy_high",
        capability_floor="date_only",
        confidence="medium",
        match=_rule_autonomy,
        supporting_fact_types=("planet_sign:sun",),
        strengthen_fact_types=("planet_sign:mars", "life_path_number"),
    ),
    EvidenceRule(
        rule_key="analysis_before_action_v0",
        claim_kind="mechanism",
        thesis_key="analysis_before_action",
        capability_floor="date_only",
        confidence="medium",
        match=_rule_analysis,
        supporting_fact_types=("planet_sign:sun",),
        strengthen_fact_types=("life_path_number", "planet_sign:mars"),
    ),
    EvidenceRule(
        rule_key="emotional_sensitivity_water_moon_v0",
        claim_kind="emotional_sensitivity",
        thesis_key="emotional_sensitivity_high",
        capability_floor="date_only",
        confidence="medium",
        match=_rule_emotional_water,
        supporting_fact_types=("planet_sign:moon",),
        qualify_fact_types=("planet_sign:sun",),
    ),
    EvidenceRule(
        rule_key="freedom_vs_stability_v0",
        claim_kind="tension",
        thesis_key="freedom_vs_stability",
        capability_floor="date_only",
        confidence="medium",
        match=_rule_freedom_vs_stability,
        supporting_fact_types=("planet_sign:sun", "planet_sign:moon"),
        edge_type="supports",
        qualify_fact_types=("life_path_number",),
    ),
    EvidenceRule(
        rule_key="ascendant_air_presence_v0",
        claim_kind="presence",
        thesis_key="presence_through_air_asc",
        capability_floor="full_natal",
        confidence="medium",
        match=lambda facts: element_for_sign(_sign_of(facts, "angle_sign:ascendant")) == "air",
        supporting_fact_types=("angle_sign:ascendant",),
        qualify_fact_types=("planet_sign:sun",),
        contradict_fact_types=("planet_sign:saturn",),
    ),
)


# Forbidden as Stage 1 claim_kind roots (asserted in tests).
FORBIDDEN_STAGE1_CLAIM_KINDS = frozenset(
    {
        "career",
        "relationships",
        "relationship",
        "money",
        "identity_core",
        "life_spheres",
    }
)

CLAIM_SEMANTIC_FAMILY: dict[str, str] = {
    "autonomy_high": "autonomy",
    "analysis_before_action": "analysis_mechanism",
    "emotional_sensitivity_high": "emotional_depth",
    "freedom_vs_stability": "freedom_stability_tension",
    "presence_through_air_asc": "presence_style",
}
