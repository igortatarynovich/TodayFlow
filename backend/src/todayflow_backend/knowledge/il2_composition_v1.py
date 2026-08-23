"""IL-2 composition rules — lemma frames from frozen atoms.

Not a pair catalog. Not Layer 5 essays. Not runtime / LLM / Today wiring.
SoT: docs/astrology/IL2_COMPOSITION_RULES_V1.md
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[4]
OBJECTS = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"

JOBS = ("what", "how", "where", "relation", "orientation")

FAMILY_SLOT_JOB = {
    "celestial_object": ("core_function", "what"),
    "sign": ("manner", "how"),
    "house": ("arena", "where"),
    "aspect": ("relation", "relation"),
    "angle": ("orientation", "orientation"),
}

ROLE_WEIGHTS: dict[str, dict[str, float]] = {
    "planet_in_sign": {"what": 0.55, "how": 0.45},
    "planet_in_house": {"what": 0.55, "where": 0.45},
    "planet_at_angle": {"what": 0.55, "orientation": 0.45},
    "aspect_pair": {"what_a": 0.50, "what_b": 0.50},
    "transit_to_natal": {"what_a": 0.50, "what_b": 0.50},
    "transit_through_house": {"what": 0.55, "where": 0.45},
}

MISSING_ATOM_IDS = frozenset(
    {
        "astro.object.uranus",
        "astro.object.neptune",
        "astro.object.pluto",
        "astro.object.dsc",
        "astro.object.ic",
    }
)

# Layer 5 gold (IL §8) → composed where Sun–Saturn atoms exist; else candidate.
LAYER5_DECISIONS: dict[tuple[str, ...], str] = {
    ("planet_in_sign", "moon", "scorpio"): "composed",
    ("planet_in_sign", "moon", "capricorn"): "composed",
    ("planet_in_sign", "saturn", "aries"): "composed",
    ("planet_in_sign", "saturn", "cancer"): "composed",
    ("planet_in_sign", "venus", "capricorn"): "composed",
    ("planet_in_sign", "venus", "aries"): "composed",
    ("planet_in_sign", "mars", "cancer"): "composed",
    ("planet_in_sign", "mars", "libra"): "composed",
    ("planet_in_sign", "sun", "pisces"): "composed",
    ("planet_in_sign", "mercury", "pisces"): "composed",
    ("planet_in_house", "saturn", "07"): "composed",
    ("planet_in_house", "saturn", "10"): "composed",
    ("planet_in_house", "saturn", "04"): "composed",
    ("planet_in_house", "moon", "07"): "composed",
    ("planet_in_house", "moon", "10"): "composed",
    ("planet_in_house", "moon", "12"): "composed",
    ("planet_in_house", "venus", "07"): "composed",
    ("planet_in_house", "venus", "02"): "composed",
    ("planet_in_house", "mars", "01"): "composed",
    ("planet_in_house", "mars", "10"): "composed",
    ("planet_in_house", "sun", "10"): "composed",
    ("natal_aspect", "moon", "saturn", "square"): "composed",
    ("natal_aspect", "moon", "saturn", "opposition"): "composed",
    ("natal_aspect", "moon", "saturn", "conjunction"): "composed",
    ("natal_aspect", "venus", "saturn", "square"): "composed",
    ("natal_aspect", "venus", "saturn", "opposition"): "composed",
    ("natal_aspect", "mars", "saturn", "square"): "composed",
    ("natal_aspect", "sun", "saturn", "square"): "composed",
    ("natal_aspect", "sun", "saturn", "conjunction"): "composed",
    ("natal_aspect", "venus", "mars", "conjunction"): "composed",
    ("natal_aspect", "moon", "pluto", "square"): "candidate_missing_atom",
    ("natal_aspect", "venus", "pluto", "square"): "candidate_missing_atom",
    ("natal_aspect", "mars", "pluto", "square"): "candidate_missing_atom",
    ("natal_aspect", "mercury", "neptune", "square"): "candidate_missing_atom",
    ("natal_aspect", "mars", "uranus", "square"): "candidate_missing_atom",
    ("transit_to_natal", "saturn", "venus", "square"): "composed",
    ("transit_to_natal", "saturn", "moon", "square"): "composed",
    ("transit_to_natal", "saturn", "sun", "square"): "composed",
    ("transit_to_natal", "saturn", "mars", "square"): "composed",
    ("transit_to_natal", "saturn", "venus", "opposition"): "composed",
    ("transit_to_natal", "saturn", "moon", "opposition"): "composed",
    ("transit_to_natal", "saturn", "sun", "conjunction"): "composed",
    ("transit_to_natal", "saturn", "moon", "conjunction"): "composed",
    ("transit_to_natal", "jupiter", "sun", "trine"): "composed",
    ("transit_to_natal", "jupiter", "saturn", "square"): "composed",
    ("transit_to_natal", "uranus", "moon", "square"): "candidate_missing_atom",
    ("transit_to_natal", "uranus", "venus", "opposition"): "candidate_missing_atom",
    ("transit_to_natal", "neptune", "venus", "square"): "candidate_missing_atom",
    ("transit_to_natal", "pluto", "sun", "square"): "candidate_missing_atom",
    ("transit_to_natal", "pluto", "venus", "square"): "candidate_missing_atom",
    ("transit_through_house", "saturn", "07"): "composed",
    ("transit_through_house", "saturn", "10"): "composed",
    ("transit_through_house", "jupiter", "10"): "composed",
    ("transit_through_house", "uranus", "07"): "candidate_missing_atom",
    ("transit_through_house", "pluto", "01"): "candidate_missing_atom",
}


@dataclass(frozen=True)
class JobPayload:
    object_id: str
    lemmas: tuple[str, ...]
    family: str
    slot: str


@dataclass(frozen=True)
class ComposedFrame:
    construction: str
    jobs: Mapping[str, JobPayload]
    weights: Mapping[str, float]
    status: str
    reason: str | None = None
    temporal_class: str | None = None
    essay: None = None
    source: str = "stored_canon"


def load_objects(path: Path | None = None) -> dict[str, dict[str, Any]]:
    payload = json.loads((path or OBJECTS).read_text(encoding="utf-8"))
    return {obj["object_id"]: obj for obj in payload["objects"]}


def _lemmas(obj: dict[str, Any]) -> tuple[str, ...]:
    family = obj["type"]
    slot, _job = FAMILY_SLOT_JOB[family]
    return tuple(obj["canon"][slot])


def _job(obj: dict[str, Any]) -> JobPayload:
    family = obj["type"]
    slot, _job = FAMILY_SLOT_JOB[family]
    return JobPayload(
        object_id=obj["object_id"],
        lemmas=tuple(obj["canon"][slot]),
        family=family,
        slot=slot,
    )


def _missing(*object_ids: str) -> str | None:
    for object_id in object_ids:
        if object_id in MISSING_ATOM_IDS:
            return object_id
    return None


def _refused(construction: str, reason: str, temporal_class: str | None = None) -> ComposedFrame:
    return ComposedFrame(
        construction=construction,
        jobs={},
        weights={},
        status="refused",
        reason=reason,
        temporal_class=temporal_class,
        essay=None,
    )


def compose_planet_in_sign(
    catalog: Mapping[str, dict[str, Any]], planet_id: str, sign_id: str
) -> ComposedFrame:
    missing = _missing(planet_id, sign_id)
    if missing:
        return _refused("planet_in_sign", f"missing_atom:{missing}")
    planet, sign = catalog[planet_id], catalog[sign_id]
    return ComposedFrame(
        construction="planet_in_sign",
        jobs={"what": _job(planet), "how": _job(sign)},
        weights=ROLE_WEIGHTS["planet_in_sign"],
        status="composed",
        temporal_class="natal",
    )


def compose_planet_in_house(
    catalog: Mapping[str, dict[str, Any]], planet_id: str, house_id: str
) -> ComposedFrame:
    missing = _missing(planet_id)
    if missing:
        return _refused("planet_in_house", f"missing_atom:{missing}")
    planet, house = catalog[planet_id], catalog[house_id]
    return ComposedFrame(
        construction="planet_in_house",
        jobs={"what": _job(planet), "where": _job(house)},
        weights=ROLE_WEIGHTS["planet_in_house"],
        status="composed",
        temporal_class="natal",
    )


def compose_planet_at_angle(
    catalog: Mapping[str, dict[str, Any]], planet_id: str, angle_id: str
) -> ComposedFrame:
    missing = _missing(planet_id, angle_id)
    if missing:
        return _refused("planet_at_angle", f"missing_atom:{missing}")
    planet, angle = catalog[planet_id], catalog[angle_id]
    return ComposedFrame(
        construction="planet_at_angle",
        jobs={"what": _job(planet), "orientation": _job(angle)},
        weights=ROLE_WEIGHTS["planet_at_angle"],
        status="composed",
        temporal_class="natal",
    )


def compose_aspect_pair(
    catalog: Mapping[str, dict[str, Any]],
    planet_a_id: str,
    planet_b_id: str,
    aspect_id: str,
    *,
    construction: str = "aspect_pair",
    temporal_class: str = "natal",
) -> ComposedFrame:
    missing = _missing(planet_a_id, planet_b_id)
    if missing:
        return _refused(construction, f"missing_atom:{missing}", temporal_class)
    planet_a, planet_b, aspect = (
        catalog[planet_a_id],
        catalog[planet_b_id],
        catalog[aspect_id],
    )
    return ComposedFrame(
        construction=construction,
        jobs={
            "what_a": _job(planet_a),
            "what_b": _job(planet_b),
            "relation": _job(aspect),
        },
        weights=ROLE_WEIGHTS[construction],
        status="composed",
        temporal_class=temporal_class,
    )


def compose_transit_to_natal(
    catalog: Mapping[str, dict[str, Any]],
    transiting_id: str,
    natal_id: str,
    aspect_id: str,
) -> ComposedFrame:
    return compose_aspect_pair(
        catalog,
        transiting_id,
        natal_id,
        aspect_id,
        construction="transit_to_natal",
        temporal_class="transit",
    )


def compose_transit_through_house(
    catalog: Mapping[str, dict[str, Any]], planet_id: str, house_id: str
) -> ComposedFrame:
    missing = _missing(planet_id)
    if missing:
        return _refused("transit_through_house", f"missing_atom:{missing}", "transit")
    planet, house = catalog[planet_id], catalog[house_id]
    return ComposedFrame(
        construction="transit_through_house",
        jobs={"what": _job(planet), "where": _job(house)},
        weights=ROLE_WEIGHTS["transit_through_house"],
        status="composed",
        temporal_class="transit",
    )


def jobs_are_partitioned(frame: ComposedFrame) -> bool:
    if frame.status != "composed":
        return False
    bags = [set(payload.lemmas) for payload in frame.jobs.values()]
    for i, left in enumerate(bags):
        for right in bags[i + 1 :]:
            if left & right:
                return False
    return True


def occupancy_is_not_conjunction(
    house_frame: ComposedFrame, aspect_frame: ComposedFrame
) -> bool:
    return (
        house_frame.construction == "planet_in_house"
        and aspect_frame.construction == "aspect_pair"
        and house_frame.jobs["where"].slot == "arena"
        and aspect_frame.jobs["relation"].slot == "relation"
        and set(house_frame.jobs["where"].lemmas).isdisjoint(
            aspect_frame.jobs["relation"].lemmas
        )
    )


def house1_is_not_asc(house_frame: ComposedFrame, angle_frame: ComposedFrame) -> bool:
    return (
        house_frame.jobs["where"].object_id == "astro.house.01"
        and angle_frame.jobs["orientation"].object_id == "astro.object.asc"
        and set(house_frame.jobs["where"].lemmas).isdisjoint(
            angle_frame.jobs["orientation"].lemmas
        )
    )


def house10_is_not_mc(house_frame: ComposedFrame, angle_frame: ComposedFrame) -> bool:
    return (
        house_frame.jobs["where"].object_id == "astro.house.10"
        and angle_frame.jobs["orientation"].object_id == "astro.object.mc"
        and set(house_frame.jobs["where"].lemmas).isdisjoint(
            angle_frame.jobs["orientation"].lemmas
        )
    )


def mc_is_not_career(angle_frame: ComposedFrame) -> bool:
    return "career" not in angle_frame.jobs["orientation"].lemmas


def interaction_is_not_relation(
    catalog: Mapping[str, dict[str, Any]], left_id: str, right_id: str
) -> bool:
    left, right = catalog[left_id], catalog[right_id]
    return left["interaction"] == right["interaction"] and list(
        left["canon"]["relation"]
    ) != list(right["canon"]["relation"])


def two_constructions_stay_two(
    left: ComposedFrame, right: ComposedFrame
) -> bool:
    return left.construction != right.construction and left.jobs.keys() != right.jobs.keys()


def layer5_decision(*parts: str) -> str:
    return LAYER5_DECISIONS[tuple(parts)]


def lemmas_copied_verbatim(frame: ComposedFrame, catalog: Mapping[str, dict[str, Any]]) -> bool:
    if frame.status != "composed":
        return False
    for payload in frame.jobs.values():
        if payload.lemmas != _lemmas(catalog[payload.object_id]):
            return False
    return True
