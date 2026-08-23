"""1.3.106 Knowledge Core V1 FREEZE — stored primitives declared. Not IL-2. Not books. Not active."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "schemas" / "astrology_interpretation_v1.schema.json"
OBJECTS = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"
FREEZE = ROOT / "docs" / "astrology" / "KNOWLEDGE_CORE_V1_FREEZE.md"
INVENTORY = ROOT / "docs" / "astrology" / "KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md"
ATOMIC_SMOKE = ROOT / "docs" / "astrology" / "ATOMIC_CANON_COMPOSITION_SMOKE_V1.md"
IL = ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md"
HANDOFF = ROOT / "docs" / "astrology" / "IL1_HANDOFF.md"
TRACKER = ROOT / "docs" / "PRODUCT_EXECUTION_TRACKER.md"

MARS_FUNCTION = ["act", "pursue", "assert"]
VENUS_FUNCTION = ["attract", "value", "relate"]
SATURN_FUNCTION = ["limit", "structure", "mature"]
MOON_FUNCTION = ["feel", "respond", "protect"]
ARIES_MANNER = ["initiating", "direct", "headlong"]
CAPRICORN_MANNER = ["reserved", "disciplined", "structured"]
FIRST_ARENA = ["self-presentation", "appearance", "first-impression"]
FOURTH_ARENA = ["home", "family", "roots", "private-base"]
TENTH_ARENA = ["career", "public-role", "reputation", "calling"]
SQUARE_RELATION = ["friction", "blockage", "cross-purposes"]
ASC_ORIENTATION = ["doorway-meeting", "how-met", "automatic-response"]
MC_ORIENTATION = ["culmination", "outer-mark", "aiming"]


def _by_id(payload: dict) -> dict:
    return {obj["object_id"]: obj for obj in payload["objects"]}


def test_knowledge_core_v1_freeze():
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
    assert "astro.object.uranus" not in by_id
    assert "astro.object.neptune" not in by_id
    assert "astro.object.pluto" not in by_id
    assert "astro.object.dsc" not in by_id
    assert "astro.object.ic" not in by_id

    for obj in planets:
        assert obj["canon"]["core_function"]
    for obj in signs:
        assert obj["canon"]["manner"]
    for obj in houses:
        assert obj["canon"]["arena"]
    for obj in aspects:
        assert obj["canon"]["relation"]
    for obj in angles:
        assert obj["canon"]["orientation"]

    mars = by_id["astro.object.mars"]
    venus = by_id["astro.object.venus"]
    saturn = by_id["astro.object.saturn"]
    moon = by_id["astro.object.moon"]
    aries = by_id["astro.sign.aries"]
    capricorn = by_id["astro.sign.capricorn"]
    first = by_id["astro.house.01"]
    fourth = by_id["astro.house.04"]
    tenth = by_id["astro.house.10"]
    square = by_id["astro.aspect.square"]
    asc = by_id["astro.object.asc"]
    mc = by_id["astro.object.mc"]

    assert list(mars["canon"]["core_function"]) == MARS_FUNCTION
    assert list(venus["canon"]["core_function"]) == VENUS_FUNCTION
    assert list(saturn["canon"]["core_function"]) == SATURN_FUNCTION
    assert list(moon["canon"]["core_function"]) == MOON_FUNCTION
    assert list(aries["canon"]["manner"]) == ARIES_MANNER
    assert list(capricorn["canon"]["manner"]) == CAPRICORN_MANNER
    assert list(first["canon"]["arena"]) == FIRST_ARENA
    assert list(fourth["canon"]["arena"]) == FOURTH_ARENA
    assert list(tenth["canon"]["arena"]) == TENTH_ARENA
    assert list(square["canon"]["relation"]) == SQUARE_RELATION
    assert list(asc["canon"]["orientation"]) == ASC_ORIENTATION
    assert list(mc["canon"]["orientation"]) == MC_ORIENTATION
    assert set(first["canon"]["arena"]).isdisjoint(asc["canon"]["orientation"])
    assert "career" not in mc["canon"]["orientation"]

    freeze = FREEZE.read_text(encoding="utf-8")
    assert "Knowledge Core V1" in freeze
    assert "**FROZEN**" in freeze
    assert "five stored families = V1 atoms" in freeze.lower() or "Five stored families = V1 atoms" in freeze
    assert "38 draft / 0 `active`" in freeze or "38 draft / 0 active" in freeze
    assert "Uranus / Neptune / Pluto" in freeze
    assert "claims, no objects" in freeze
    assert "DSC / IC" in freeze
    assert "CORE" in freeze
    assert "not a product gate" in freeze.lower() or "not a gate" in freeze.lower()
    assert "candidates" in freeze
    assert "recognition check" in freeze
    assert "STOP Angles" in freeze
    assert "STOP Aspects" in freeze
    assert "STOP Houses" in freeze
    assert "STOP Signs" in freeze
    assert "Do **not** start CORE scoring" in freeze
    assert "Do **not** start ASC cookbooks" in freeze
    assert "classification-complete" in freeze
    assert "IL-2" in freeze
    assert "composition **rules**" in freeze or "composition rules" in freeze.lower()
    assert "canonical v2" in freeze
    assert "1.3.106" in freeze

    inventory = INVENTORY.read_text(encoding="utf-8")
    assert "34. Knowledge Core V1 FREEZE" in inventory
    assert "✅ 1.3.106" in inventory
    assert "NEXT" not in inventory.split("34. Knowledge Core V1 FREEZE")[1].split("\n")[0]
    assert "## Freeze (primitives)" in inventory
    assert "Layer 5 = candidates" in inventory or "Layer 5" in freeze

    canon = IL.read_text(encoding="utf-8")
    assert "**Версия:** 1.3.115" in canon
    assert "### 6.60 Knowledge Core V1 FREEZE" in canon
    assert canon.count("**Версия:**") == 1

    next_block = HANDOFF.read_text(encoding="utf-8").split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.106" in next_block
    assert "Knowledge Core V1 FREEZE" in next_block
    for ver in (
        "1.3.82",
        "1.3.83",
        "1.3.84",
        "1.3.85",
        "1.3.86",
        "1.3.87",
        "1.3.88",
        "1.3.89",
        "1.3.90",
        "1.3.91",
        "1.3.92",
        "1.3.93",
        "1.3.94",
        "1.3.95",
        "1.3.96",
        "1.3.97",
        "1.3.98",
        "1.3.99",
        "1.3.100",
        "1.3.101",
        "1.3.102",
        "1.3.103",
        "1.3.104",
        "1.3.105",
    ):
        assert ver in next_block
    assert "IL-2" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "Do **not** start ASC cookbooks" in next_block
    assert "STOP Angles" in next_block
    assert "STOP Aspects" in next_block
    assert "STOP Houses" in next_block
    assert "STOP Signs" in next_block

    tracker = TRACKER.read_text(encoding="utf-8")
    now = tracker.split("**NOW (FOUNDATION")[1].split("**PAUSED")[0]
    assert "1.3.106" in now
    assert "FREEZE" in now
    assert "IL-2" in now
    assert "38 draft / 0 `active`" in now or "38 draft / 0 active" in now

    smoke = ATOMIC_SMOKE.read_text(encoding="utf-8")
    assert "1.3.105" in smoke
    assert "STOP Angles" in smoke
