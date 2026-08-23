"""Library Scale V1 — coverage contract for locked engines.

Not a pair catalog. Not Layer 5 essays. Not runtime / LLM / Today wiring.
SoT: docs/astrology/LIBRARY_SCALE_V1.md
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Iterator, Mapping

from todayflow_backend.knowledge.il2_composition_v1 import (
    LAYER5_DECISIONS,
    compose_aspect_pair,
    compose_planet_at_angle,
    compose_planet_in_house,
    compose_planet_in_sign,
    compose_transit_through_house,
    compose_transit_to_natal,
)
from todayflow_backend.knowledge.il3_interpretation_v1 import SkyFact, interpret
from todayflow_backend.knowledge.il4_expression_v1 import ExpressionPack, express

WIRE_CONTRACT = (
    "calc SkyFact → IL-2 compose → IL-3 interpret → IL-4 express(surface)"
)

EXPECTED_COVERED = {
    "planet_in_sign": 84,
    "planet_in_house": 84,
    "planet_at_angle": 14,
    "aspect_pair": 105,
    "transit_to_natal": 245,
    "transit_through_house": 84,
}
EXPECTED_COVERED_TOTAL = 616
EXPECTED_GOLD_COMPOSED = 43
EXPECTED_GOLD_CANDIDATE = 12

MISSING_EXAMPLES = (
    SkyFact("transit_to_natal", ("astro.object.pluto", "astro.object.sun", "astro.aspect.square")),
    SkyFact("planet_at_angle", ("astro.object.mars", "astro.object.dsc")),
    SkyFact("planet_in_sign", ("astro.object.uranus", "astro.sign.aries")),
)


@dataclass(frozen=True)
class CoverageReport:
    by_construction: Mapping[str, int]
    total: int
    gold_composed: int
    gold_candidate: int
    wire_contract: str = WIRE_CONTRACT
    person_id: None = None
    user_relevance: None = None
    catalog_records: int = 0


def _ids(catalog: Mapping[str, dict], type_name: str) -> tuple[str, ...]:
    return tuple(
        sorted(object_id for object_id, obj in catalog.items() if obj["type"] == type_name)
    )


def covered_facts(catalog: Mapping[str, dict]) -> Iterator[SkyFact]:
    planets = _ids(catalog, "celestial_object")
    signs = _ids(catalog, "sign")
    houses = _ids(catalog, "house")
    aspects = _ids(catalog, "aspect")
    angles = _ids(catalog, "angle")
    for planet in planets:
        for sign in signs:
            yield SkyFact("planet_in_sign", (planet, sign))
        for house in houses:
            yield SkyFact("planet_in_house", (planet, house))
            yield SkyFact("transit_through_house", (planet, house))
        for angle in angles:
            yield SkyFact("planet_at_angle", (planet, angle))
        for natal in planets:
            for aspect in aspects:
                yield SkyFact("transit_to_natal", (planet, natal, aspect))
    for left, right in combinations(planets, 2):
        for aspect in aspects:
            yield SkyFact("aspect_pair", (left, right, aspect))


def _compose(catalog: Mapping[str, dict], fact: SkyFact):
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
        return compose_transit_to_natal(catalog, parts[0], parts[1], parts[2])
    if construction == "transit_through_house":
        return compose_transit_through_house(catalog, parts[0], parts[1])
    raise ValueError(f"unknown_construction:{construction}")


def coverage_counts(catalog: Mapping[str, dict]) -> dict[str, int]:
    counts = {name: 0 for name in EXPECTED_COVERED}
    for fact in covered_facts(catalog):
        counts[fact.construction] += 1
    return counts


def every_covered_cell_composes(catalog: Mapping[str, dict]) -> bool:
    for fact in covered_facts(catalog):
        if _compose(catalog, fact).status != "composed":
            return False
    return True


def _gold_fact(parts: tuple[str, ...]) -> SkyFact:
    kind = parts[0]
    if kind == "planet_in_sign":
        return SkyFact("planet_in_sign", (f"astro.object.{parts[1]}", f"astro.sign.{parts[2]}"))
    if kind == "planet_in_house":
        return SkyFact("planet_in_house", (f"astro.object.{parts[1]}", f"astro.house.{parts[2]}"))
    if kind == "natal_aspect":
        return SkyFact(
            "aspect_pair",
            (f"astro.object.{parts[1]}", f"astro.object.{parts[2]}", f"astro.aspect.{parts[3]}"),
        )
    if kind == "transit_to_natal":
        return SkyFact(
            "transit_to_natal",
            (f"astro.object.{parts[1]}", f"astro.object.{parts[2]}", f"astro.aspect.{parts[3]}"),
        )
    if kind == "transit_through_house":
        return SkyFact(
            "transit_through_house",
            (f"astro.object.{parts[1]}", f"astro.house.{parts[2]}"),
        )
    raise ValueError(f"unknown_gold:{kind}")


def gold_matches_engines(catalog: Mapping[str, dict]) -> bool:
    for parts, decision in LAYER5_DECISIONS.items():
        frame = _compose(catalog, _gold_fact(parts))
        if decision == "composed" and frame.status != "composed":
            return False
        if decision == "candidate_missing_atom" and frame.status != "refused":
            return False
    return True


def report(catalog: Mapping[str, dict]) -> CoverageReport:
    composed = sum(1 for decision in LAYER5_DECISIONS.values() if decision == "composed")
    candidate = sum(
        1 for decision in LAYER5_DECISIONS.values() if decision == "candidate_missing_atom"
    )
    counts = coverage_counts(catalog)
    return CoverageReport(
        by_construction=counts,
        total=sum(counts.values()),
        gold_composed=composed,
        gold_candidate=candidate,
        wire_contract=WIRE_CONTRACT,
        person_id=None,
        user_relevance=None,
        catalog_records=0,
    )


def sample_pack(catalog: Mapping[str, dict], surface: str = "profile") -> ExpressionPack:
    """One fact per construction through IL-2 → IL-3 → IL-4. Not a catalog."""
    facts = (
        SkyFact("planet_in_sign", ("astro.object.mars", "astro.sign.aries")),
        SkyFact("planet_in_house", ("astro.object.mars", "astro.house.01")),
        SkyFact("planet_at_angle", ("astro.object.mars", "astro.object.asc")),
        SkyFact("aspect_pair", ("astro.object.mars", "astro.object.saturn", "astro.aspect.square")),
        SkyFact(
            "transit_to_natal",
            ("astro.object.saturn", "astro.object.venus", "astro.aspect.square"),
        ),
        SkyFact("transit_through_house", ("astro.object.saturn", "astro.house.10")),
        SkyFact(
            "transit_to_natal",
            ("astro.object.pluto", "astro.object.sun", "astro.aspect.square"),
        ),
    )
    return express(interpret(catalog, facts), surface)


def runtime_is_not_wired(src_root: Path) -> bool:
    """Production code outside knowledge/ must not import IL engines except the attach gateway."""
    banned = (
        "il2_composition_v1",
        "il3_interpretation_v1",
        "il4_expression_v1",
        "library_scale_v1",
        "calc_il_wire_v1",
    )
    knowledge = (src_root / "knowledge").resolve()
    attach_gateway = (src_root / "services" / "il4_surface_attach_v1.py").resolve()
    consume_module = (src_root / "services" / "il4_editorial_consume_v1.py").resolve()
    polish_module = (src_root / "services" / "today_meaning_polish_v1.py").resolve()
    attach_consumers = {
        (src_root / "services" / "day_story_wire_v1.py").resolve(),
        (src_root / "services" / "profile_contract_v1.py").resolve(),
        (src_root / "services" / "compatibility_llm.py").resolve(),
        (src_root / "services" / "generation_orchestrator.py").resolve(),
    }
    consume_consumers = {
        (src_root / "services" / "day_scenario_native_llm_c1.py").resolve(),
        (src_root / "services" / "profile_contract_v1.py").resolve(),
        (src_root / "services" / "compatibility_llm.py").resolve(),
    }
    polish_consumers = {
        (src_root / "services" / "day_scenario_native_llm_c1.py").resolve(),
    }
    for path in src_root.rglob("*.py"):
        resolved = path.resolve()
        if knowledge in resolved.parents or resolved == knowledge:
            continue
        if resolved == attach_gateway or resolved == consume_module or resolved == polish_module:
            continue
        text = path.read_text(encoding="utf-8")
        if "calc_il_wire_v1" in text:
            return False
        if "il4_surface_attach_v1" in text and resolved not in attach_consumers:
            return False
        if "il4_editorial_consume_v1" in text and resolved not in consume_consumers:
            return False
        if "today_meaning_polish_v1" in text and resolved not in polish_consumers:
            return False
        if any(name in text for name in banned):
            return False
    return True
