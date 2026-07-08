"""Reference loaders for canonical astrology data."""

from __future__ import annotations

import json
import os
from datetime import date, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List


# Monorepo: DATA/ at repository root (same layout as numerology reference).
DEFAULT_DATA_ROOT = Path(__file__).resolve().parents[4] / "DATA"
DATA_DIR = Path(os.getenv("TODAYFLOW_DATA_DIR", DEFAULT_DATA_ROOT)) / "astrology_reference"


@lru_cache(maxsize=1)
def _load_json(filename: str) -> List[Dict[str, Any]]:
    file_path = DATA_DIR / filename
    with file_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def zodiac_signs() -> List[Dict[str, Any]]:
    """Return list of zodiac sign metadata."""
    return _load_json("zodiac_signs.json")


def planets() -> List[Dict[str, Any]]:
    """Return list of planet metadata."""
    return _load_json("planets.json")


def houses() -> List[Dict[str, Any]]:
    """Return list of house metadata."""
    return _load_json("houses.json")


def aspects() -> List[Dict[str, Any]]:
    """Return list of aspect metadata."""
    return _load_json("aspects.json")


def aspect_relations() -> List[Dict[str, Any]]:
    """Return metadata linking body pairs to axes/context."""
    return _load_json("aspect_relations.json")


def relationship_aspect_meanings() -> List[Dict[str, Any]]:
    """Return relationship-focused meanings for key aspect pairs."""
    return _load_json("relationship_aspect_meanings.json")


def planet_in_sign_relationships() -> List[Dict[str, Any]]:
    """Return relationship meanings for planet-in-sign placements."""
    return _load_json("planet_in_sign_relationships.json")


def planet_in_house_relationships() -> List[Dict[str, Any]]:
    """Return relationship meanings for planet overlays in houses."""
    return _load_json("planet_in_house_relationships.json")


def relationship_modes() -> List[Dict[str, Any]]:
    """Return product modes for relationship interpretation."""
    return _load_json("relationship_modes.json")


def moon_phases() -> List[Dict[str, Any]]:
    """Return lunar phase metadata."""
    return _load_json("moon_phases.json")


def tarot_major_arcana() -> List[Dict[str, Any]]:
    """Reference deck for major arcana cards."""
    return _load_json("tarot_major_arcana.json")


def mantras() -> List[Dict[str, Any]]:
    """Mantra inventory for guided practices."""
    return _load_json("mantras.json")


def rituals() -> List[Dict[str, Any]]:
    """Ritual inventory (herbs, instructions, pairings)."""
    return _load_json("rituals.json")


def tarot_spreads() -> List[Dict[str, Any]]:
    """Tarot spread templates (positions + prompts)."""
    return _load_json("tarot_spreads.json")


def planetary_cycles() -> List[Dict[str, Any]]:
    """Planetary ingress/aspect/station events."""
    return _load_json("planetary_cycles.json")


def check_ins() -> List[Dict[str, Any]]:
    """Guided check-in prompts tied to axes/mantras/rituals."""
    return _load_json("check_ins.json")


def ep_facets() -> List[Dict[str, Any]]:
    """Facets for Emotional Patterns."""
    return _load_json("ep_facets.json")


def weekly_insights() -> List[Dict[str, Any]]:
    """Weekly/lunar insights tied to phases and axes."""
    return _load_json("weekly_insights.json")


def cross_domain_bridges() -> List[Dict[str, Any]]:
    """Cross-domain bridge metadata."""
    return _load_json("cross_domain_bridges.json")


def sign_for_iso_date(value: str) -> Dict[str, Any] | None:
    """Resolve zodiac metadata for an ISO YYYY-MM-DD string."""
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None
    return sign_for_date(parsed)


def sign_for_date(day: date) -> Dict[str, Any] | None:
    """Resolve zodiac metadata for a datetime.date."""
    for record in zodiac_signs():
        start = _to_date(record["start"], day.year)
        end = _to_date(record["end"], day.year)
        if start <= end:
            in_range = start <= day <= end
        else:
            # Capricorn/Aquarius ranges that wrap around year end
            in_range = day >= start or day <= end
        if in_range:
            return record
    return None


def lookup_sign_metadata(sign_name: str) -> Dict[str, Any] | None:
    """Return metadata for a sign name/id."""
    normalized = sign_name.strip().lower()
    for record in zodiac_signs():
        if record["id"] == normalized or record["name"].lower() == normalized:
            return record
    return None


def lookup_planet_metadata(planet_name: str) -> Dict[str, Any] | None:
    """Return metadata for a planet name/id."""
    normalized = planet_name.strip().lower()
    for record in planets():
        if record["id"] == normalized or record["name"].lower() == normalized:
            return record
    return None


def lookup_house_metadata(house_id: int) -> Dict[str, Any] | None:
    """Return metadata for a house number."""
    for record in houses():
        if int(record.get("id", 0)) == int(house_id):
            return record
    return None


def lookup_aspect_metadata(aspect_id: str) -> Dict[str, Any] | None:
    """Return metadata for an aspect id."""
    normalized = aspect_id.strip().lower()
    for record in aspects():
        if record.get("id", "").lower() == normalized:
            return record
    return None


def lookup_relationship_aspect_meaning(left: str, right: str) -> Dict[str, Any] | None:
    """Return relationship meaning for a planet pair, regardless of order."""
    normalized_left = left.strip().lower()
    normalized_right = right.strip().lower()
    for record in relationship_aspect_meanings():
        pair_left = str(record.get("left") or "").strip().lower()
        pair_right = str(record.get("right") or "").strip().lower()
        if (pair_left, pair_right) == (normalized_left, normalized_right) or (pair_left, pair_right) == (normalized_right, normalized_left):
            return record
    return None


def lookup_planet_in_sign_relationship(planet_name: str, sign_name: str) -> Dict[str, Any] | None:
    """Return relationship meaning for planet in sign."""
    planet_normalized = planet_name.strip().lower()
    sign_normalized = sign_name.strip().lower()
    for record in planet_in_sign_relationships():
        if str(record.get("planet") or "").strip().lower() == planet_normalized and str(record.get("sign") or "").strip().lower() == sign_normalized:
            return record
    return None


def lookup_planet_in_house_relationship(planet_name: str, house_id: int) -> Dict[str, Any] | None:
    """Return relationship meaning for planet overlay in a house."""
    planet_normalized = planet_name.strip().lower()
    for record in planet_in_house_relationships():
        if str(record.get("planet") or "").strip().lower() == planet_normalized and int(record.get("house") or 0) == int(house_id):
            return record
    return None


def lookup_relationship_mode(mode_id: str) -> Dict[str, Any] | None:
    """Return metadata for a relationship interpretation mode."""
    normalized = mode_id.strip().lower()
    for record in relationship_modes():
        if str(record.get("id") or "").strip().lower() == normalized:
            return record
    return None


def _to_date(mm_dd: str, year: int) -> date:
    month, day = map(int, mm_dd.split("-"))
    return date(year, month, day)
