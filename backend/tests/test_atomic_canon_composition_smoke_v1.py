"""1.3.105 final atomic smoke — five stored families, operators discriminate. Not IL-2. Not freeze."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "schemas" / "astrology_interpretation_v1.schema.json"
OBJECTS = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"
SMOKE = ROOT / "docs" / "astrology" / "ATOMIC_CANON_COMPOSITION_SMOKE_V1.md"
ANGLE_SMOKE = ROOT / "docs" / "astrology" / "ANGLE_CANON_COMPOSITION_SMOKE_V1.md"
ASPECT_SMOKE = ROOT / "docs" / "astrology" / "ASPECT_CANON_COMPOSITION_SMOKE_V1.md"
HOUSE_SMOKE = ROOT / "docs" / "astrology" / "HOUSE_CANON_COMPOSITION_SMOKE_V1.md"
SIGN_SMOKE = ROOT / "docs" / "astrology" / "SIGN_CANON_COMPOSITION_SMOKE_V1.md"
IL = ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md"
HANDOFF = ROOT / "docs" / "astrology" / "IL1_HANDOFF.md"

MARS_FUNCTION = ["act", "pursue", "assert"]
VENUS_FUNCTION = ["attract", "value", "relate"]
SATURN_FUNCTION = ["limit", "structure", "mature"]
MOON_FUNCTION = ["feel", "respond", "protect"]
ARIES_MANNER = ["initiating", "direct", "headlong"]
CAPRICORN_MANNER = ["reserved", "disciplined", "structured"]
FIRST_ARENA = ["self-presentation", "appearance", "first-impression"]
FOURTH_ARENA = ["home", "family", "roots", "private-base"]
SQUARE_RELATION = ["friction", "blockage", "cross-purposes"]
ASC_ORIENTATION = ["doorway-meeting", "how-met", "automatic-response"]


def _by_id(payload: dict) -> dict:
    return {obj["object_id"]: obj for obj in payload["objects"]}


def test_atomic_canon_composition_smoke_v1():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    by_id = _by_id(payload)

    planets = [obj for obj in payload["objects"] if obj["type"] == "celestial_object"]
    signs = [obj for obj in payload["objects"] if obj["type"] == "sign"]
    houses = [obj for obj in payload["objects"] if obj["type"] == "house"]
    aspects = [obj for obj in payload["objects"] if obj["type"] == "aspect"]
    angles = [obj for obj in payload["objects"] if obj["type"] == "angle"]

    assert len(payload["objects"]) == 38
    assert len(planets) == 7
    assert len(signs) == 12
    assert len(houses) == 12
    assert len(aspects) == 5
    assert len(angles) == 2
    assert all(obj["status"] != "active" for obj in payload["objects"])
    assert all(obj["status"] == "draft" for obj in payload["objects"])

    for obj in planets:
        assert obj["canon"]["core_function"]
    for obj in signs:
        assert obj["canon"]["manner"]
    for obj in houses:
        assert obj["canon"]["arena"]
    for obj in aspects:
        assert obj["canon"]["relation"]
        assert "interaction" in obj
    for obj in angles:
        assert obj["canon"]["orientation"]
        assert "arena" not in obj["canon"]

    mars = by_id["astro.object.mars"]
    venus = by_id["astro.object.venus"]
    saturn = by_id["astro.object.saturn"]
    moon = by_id["astro.object.moon"]
    aries = by_id["astro.sign.aries"]
    capricorn = by_id["astro.sign.capricorn"]
    first = by_id["astro.house.01"]
    fourth = by_id["astro.house.04"]
    square = by_id["astro.aspect.square"]
    trine = by_id["astro.aspect.trine"]
    sextile = by_id["astro.aspect.sextile"]
    asc = by_id["astro.object.asc"]

    mars_aries = {
        "type": "planet_in_sign",
        "function": list(mars["canon"]["core_function"]),
        "manner": list(aries["canon"]["manner"]),
    }
    mars_first = {
        "type": "planet_in_house",
        "function": list(mars["canon"]["core_function"]),
        "arena": list(first["canon"]["arena"]),
    }
    mars_asc = {
        "type": "planet_at_angle",
        "function": list(mars["canon"]["core_function"]),
        "orientation": list(asc["canon"]["orientation"]),
    }
    mars_saturn_square = {
        "type": "aspect_pair",
        "function_a": list(mars["canon"]["core_function"]),
        "function_b": list(saturn["canon"]["core_function"]),
        "relation": list(square["canon"]["relation"]),
    }

    assert mars_aries["function"] == MARS_FUNCTION
    assert mars_aries["manner"] == ARIES_MANNER
    assert mars_first["arena"] == FIRST_ARENA
    assert mars_asc["orientation"] == ASC_ORIENTATION
    assert mars_saturn_square["relation"] == SQUARE_RELATION
    assert mars_saturn_square["function_b"] == SATURN_FUNCTION

    assert mars_aries["type"] != mars_first["type"] != mars_asc["type"] != mars_saturn_square["type"]
    assert set(mars_aries["manner"]).isdisjoint(mars_first["arena"])
    assert set(mars_first["arena"]).isdisjoint(mars_asc["orientation"])
    assert set(mars_saturn_square["relation"]).isdisjoint(mars_asc["orientation"])
    assert "story" not in mars_aries
    assert "essay" not in mars_asc

    venus_cap = {
        "type": "planet_in_sign",
        "function": list(venus["canon"]["core_function"]),
        "manner": list(capricorn["canon"]["manner"]),
    }
    moon_fourth = {
        "type": "planet_in_house",
        "function": list(moon["canon"]["core_function"]),
        "arena": list(fourth["canon"]["arena"]),
    }
    assert venus_cap["function"] == VENUS_FUNCTION
    assert venus_cap["manner"] == CAPRICORN_MANNER
    assert moon_fourth["function"] == MOON_FUNCTION
    assert moon_fourth["arena"] == FOURTH_ARENA

    assert trine["interaction"] == sextile["interaction"] == "flow"
    assert list(trine["canon"]["relation"]) != list(sextile["canon"]["relation"])
    assert aries["element"] == "fire"
    assert "earth" not in aries["canon"]["manner"]
    assert first["canon"] == {"arena": FIRST_ARENA}

    smoke = SMOKE.read_text(encoding="utf-8")
    assert "Mars IN Aries — **PASS**" in smoke
    assert "Venus × Capricorn — **PASS**" in smoke
    assert "Moon × 4th house — **PASS**" in smoke
    assert "Mars □ Saturn — **PASS**" in smoke
    assert "Mars AT ASC — **PASS**" in smoke
    assert "Mars IN Aries ≠ Mars IN 1st" in smoke
    assert "Mars IN 1st ≠ Mars AT ASC" in smoke
    assert "Occupancy ≠ conjunction" in smoke
    assert "Planet + Sign + House + Aspect + Angle, all stored" in smoke
    assert "five stored" in smoke
    assert "Forbidden recovery" in smoke
    assert "Knowledge Core V1 FREEZE" in smoke
    assert "STOP Angles" in smoke
    assert "Mars in Aries means you look aggressive" in smoke
    assert "Planet in 1st = planet on ASC" in smoke
    assert "MC = career" in smoke

    assert "Mars AT ASC — **PASS**" in ANGLE_SMOKE.read_text(encoding="utf-8")
    assert "STOP Angles" in ANGLE_SMOKE.read_text(encoding="utf-8")
    aspect_smoke = ASPECT_SMOKE.read_text(encoding="utf-8")
    assert "STOP Aspects" in aspect_smoke
    assert "Moon × 4th house — **PASS**" in HOUSE_SMOKE.read_text(encoding="utf-8")
    assert "Venus × Capricorn — **PASS**" in SIGN_SMOKE.read_text(encoding="utf-8")

    canon = IL.read_text(encoding="utf-8")
    assert "**Версия:** 1.3.107" in canon
    assert "### 6.59 Final atomic smoke" in canon
    assert canon.count("**Версия:**") == 1

    next_block = HANDOFF.read_text(encoding="utf-8").split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.105" in next_block
    assert "1.3.104" in next_block
    assert "1.3.103" in next_block
    assert "1.3.102" in next_block
    assert "1.3.101" in next_block
    assert "1.3.100" in next_block
    assert "1.3.99" in next_block
    assert "1.3.98" in next_block
    assert "Planet × Angle" in next_block or "Planet×Angle" in next_block
    assert "Planet × Aspect" in next_block
    assert "final atomic smoke" in next_block.lower() or "1.3.105" in next_block
    assert "Knowledge Core V1 FREEZE" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "STOP Angles" in next_block
    assert "STOP Aspects" in next_block
    assert "STOP Houses" in next_block
    assert "STOP Signs" in next_block
    assert "Do **not** start ASC cookbooks" in next_block
