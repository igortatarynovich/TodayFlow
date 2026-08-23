"""1.3.104 stored Planet × Angle composition smoke — frames from angle.canon.orientation. Not IL-2."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "schemas" / "astrology_interpretation_v1.schema.json"
OBJECTS = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"
SMOKE = ROOT / "docs" / "astrology" / "ANGLE_CANON_COMPOSITION_SMOKE_V1.md"
HOUSE_SMOKE = ROOT / "docs" / "astrology" / "HOUSE_CANON_COMPOSITION_SMOKE_V1.md"
IL = ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md"
HANDOFF = ROOT / "docs" / "astrology" / "IL1_HANDOFF.md"

ASC_ORIENTATION = ["doorway-meeting", "how-met", "automatic-response"]
MC_ORIENTATION = ["culmination", "outer-mark", "aiming"]
FIRST_ARENA = ["self-presentation", "appearance", "first-impression"]
TENTH_ARENA = ["career", "public-role", "reputation", "calling"]
MARS_FUNCTION = ["act", "pursue", "assert"]
VENUS_FUNCTION = ["attract", "value", "relate"]

ORIENTATION_FORBIDDEN = (
    "self-presentation",
    "appearance",
    "first-impression",
    "mask",
    "career",
    "public-role",
    "reputation",
    "calling",
    "profession",
    "personal-facing",
    "public-facing",
)


def _by_id(payload: dict) -> dict:
    return {obj["object_id"]: obj for obj in payload["objects"]}


def _planet_at_angle_frame(planet: dict, angle: dict) -> dict:
    orientation = list(angle["canon"]["orientation"])
    determined = bool(orientation)
    return {
        "type": "planet_at_angle",
        "planet_id": planet["object_id"],
        "angle_id": angle["object_id"],
        "function": list(planet["canon"]["core_function"]),
        "orientation": orientation,
        "payload_determined": determined,
        "missing": None if determined else "angle_canon.orientation",
        "verdict": "PASS" if determined else "PARTIAL",
    }


def _planet_in_house_frame(planet: dict, house: dict) -> dict:
    arena = list(house["canon"]["arena"])
    determined = bool(arena)
    return {
        "type": "planet_in_house",
        "planet_id": planet["object_id"],
        "house_id": house["object_id"],
        "function": list(planet["canon"]["core_function"]),
        "arena": arena,
        "payload_determined": determined,
        "missing": None if determined else "house_canon.arena",
        "verdict": "PASS" if determined else "PARTIAL",
    }


def test_angle_canon_composition_smoke_v1():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    by_id = _by_id(payload)

    mars = by_id["astro.object.mars"]
    venus = by_id["astro.object.venus"]
    asc = by_id["astro.object.asc"]
    mc = by_id["astro.object.mc"]
    first = by_id["astro.house.01"]
    tenth = by_id["astro.house.10"]

    mars_asc = _planet_at_angle_frame(mars, asc)
    assert mars_asc["function"] == MARS_FUNCTION
    assert mars_asc["orientation"] == ASC_ORIENTATION
    assert mars_asc["orientation"] == list(asc["canon"]["orientation"])
    assert mars_asc["verdict"] == "PASS"
    assert mars_asc["missing"] is None
    assert mars_asc["payload_determined"] is True
    assert mars_asc["type"] == "planet_at_angle"
    assert "story" not in mars_asc
    assert "essay" not in mars_asc

    venus_asc = _planet_at_angle_frame(venus, asc)
    assert venus_asc["function"] == VENUS_FUNCTION
    assert venus_asc["orientation"] == mars_asc["orientation"] == ASC_ORIENTATION
    assert venus_asc["verdict"] == "PASS"
    assert venus_asc["angle_id"] == mars_asc["angle_id"] == "astro.object.asc"

    mars_mc = _planet_at_angle_frame(mars, mc)
    assert mars_mc["function"] == mars_asc["function"]
    assert mars_mc["orientation"] == MC_ORIENTATION
    assert mars_asc["orientation"] != mars_mc["orientation"]
    assert "culmination" not in mars_asc["orientation"]
    assert "how-met" not in mars_mc["orientation"]
    assert mars_mc["verdict"] == "PASS"

    mars_first = _planet_in_house_frame(mars, first)
    assert mars_first["type"] == "planet_in_house"
    assert mars_first["function"] == MARS_FUNCTION
    assert mars_first["arena"] == FIRST_ARENA
    assert mars_first["verdict"] == "PASS"
    assert mars_asc["type"] != mars_first["type"]
    assert mars_asc["orientation"] != mars_first["arena"]
    assert set(mars_asc["orientation"]).isdisjoint(mars_first["arena"])

    mars_tenth = _planet_in_house_frame(mars, tenth)
    assert mars_tenth["arena"] == TENTH_ARENA
    assert mars_mc["orientation"] != mars_tenth["arena"]
    assert set(mars_mc["orientation"]).isdisjoint(mars_tenth["arena"])
    assert first["canon"] == {"arena": FIRST_ARENA}
    assert tenth["canon"] == {"arena": TENTH_ARENA}

    for obj in payload["objects"]:
        if obj["type"] != "angle":
            continue
        assert obj["status"] == "draft"
        assert obj["canon"]["orientation"]
        blob = " ".join(obj["canon"]["orientation"])
        for word in ORIENTATION_FORBIDDEN:
            assert word not in blob.split(), (obj["object_id"], word)
        frame = _planet_at_angle_frame(mars, obj)
        assert frame["verdict"] == "PASS"
        assert frame["orientation"] == list(obj["canon"]["orientation"])
        assert "arena" not in frame

    assert len([obj for obj in payload["objects"] if obj["type"] == "angle"]) == 2
    assert all(obj["status"] != "active" for obj in payload["objects"])

    smoke = SMOKE.read_text(encoding="utf-8")
    assert "Mars AT ASC — **PASS**" in smoke
    assert "Venus AT ASC — **PASS**" in smoke
    assert "Mars AT ASC ≠ Mars AT MC" in smoke
    assert "Mars AT ASC ≠ Mars IN 1st" in smoke
    assert "Mars AT MC ≠ Mars IN 10th" in smoke
    assert "Occupancy ≠ conjunction" in smoke
    assert "snapshot" in smoke.lower()
    assert "Forbidden recovery" in smoke
    assert "STOP Angles" in smoke
    assert "Mars rising means you look aggressive" in smoke
    assert "MC = career" in smoke
    assert "Planet in 1st = planet on ASC" in smoke

    prior_house = HOUSE_SMOKE.read_text(encoding="utf-8")
    assert "Moon × 4th house — **PASS**" in prior_house
    assert "STOP Houses" in prior_house

    canon = IL.read_text(encoding="utf-8")
    assert "**Версия:** 1.3.104" in canon
    assert "### 6.58 Planet × Angle composition smoke" in canon
    assert canon.count("**Версия:**") == 1

    next_block = HANDOFF.read_text(encoding="utf-8").split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.104" in next_block
    assert "1.3.103" in next_block
    assert "1.3.102" in next_block
    assert "1.3.101" in next_block
    assert "1.3.100" in next_block
    assert "1.3.99" in next_block
    assert "1.3.98" in next_block
    assert "Planet × Angle" in next_block or "Planet×Angle" in next_block
    assert "Planet × Aspect" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "STOP Angles" in next_block
    assert "STOP Aspects" in next_block
    assert "STOP Houses" in next_block
    assert "STOP Signs" in next_block
    assert "Do **not** start ASC cookbooks" in next_block
