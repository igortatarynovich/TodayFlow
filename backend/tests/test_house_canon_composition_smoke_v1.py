"""1.3.93 Planet × House composition smoke — frames from stored house.canon.arena. Not IL-2."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "schemas" / "astrology_interpretation_v1.schema.json"
OBJECTS = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"
SMOKE = ROOT / "docs" / "astrology" / "HOUSE_CANON_COMPOSITION_SMOKE_V1.md"
SIGN_SMOKE = ROOT / "docs" / "astrology" / "SIGN_CANON_COMPOSITION_SMOKE_V1.md"
PLANET_SMOKE = ROOT / "docs" / "astrology" / "PLANET_CANON_COMPOSITION_SMOKE_V1.md"
IL = ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md"
HANDOFF = ROOT / "docs" / "astrology" / "IL1_HANDOFF.md"

FOURTH_ARENA = ["home", "family", "roots", "private-base"]
TENTH_ARENA = ["career", "public-role", "reputation", "calling"]
MOON_FUNCTION = ["feel", "respond", "protect"]
MARS_FUNCTION = ["act", "pursue", "assert"]
VENUS_FUNCTION = ["attract", "value", "relate"]


def _by_id(payload: dict) -> dict:
    return {obj["object_id"]: obj for obj in payload["objects"]}


def _planet_in_house_frame(planet: dict, house: dict) -> dict:
    arena = list(house["canon"]["arena"])
    determined = bool(arena)
    return {
        "type": "planet_in_house",
        "planet_id": planet["object_id"],
        "house_id": house["object_id"],
        "function": list(planet["canon"]["core_function"]),
        "drive": list(planet["canon"]["drive"]),
        "arena": arena,
        "lilly_domain": house.get("domain"),
        "payload_determined": determined,
        "missing": None if determined else "house_canon.arena",
        "verdict": "PASS" if determined else "PARTIAL",
    }


def test_house_canon_composition_smoke_v1():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    by_id = _by_id(payload)

    moon = by_id["astro.object.moon"]
    mars = by_id["astro.object.mars"]
    venus = by_id["astro.object.venus"]
    fourth = by_id["astro.house.04"]
    tenth = by_id["astro.house.10"]

    moon_fourth = _planet_in_house_frame(moon, fourth)
    assert moon_fourth["function"] == MOON_FUNCTION
    assert moon_fourth["arena"] == FOURTH_ARENA
    assert moon_fourth["verdict"] == "PASS"
    assert moon_fourth["missing"] is None
    assert moon_fourth["payload_determined"] is True
    assert "seek" not in " ".join(moon_fourth["arena"])
    assert "emotional" not in " ".join(moon_fourth["arena"])
    assert fourth["domain"] == "father, land, hidden things, and endings"
    assert moon_fourth["lilly_domain"] == fourth["domain"]
    assert "father" not in moon_fourth["arena"]

    moon_tenth = _planet_in_house_frame(moon, tenth)
    assert moon_tenth["function"] == MOON_FUNCTION
    assert moon_tenth["arena"] == TENTH_ARENA
    assert moon_tenth["verdict"] == "PASS"
    assert moon_fourth["arena"] != moon_tenth["arena"]
    assert "home" not in moon_tenth["arena"]
    assert "career" not in moon_fourth["arena"]

    mars_fourth = _planet_in_house_frame(mars, fourth)
    venus_fourth = _planet_in_house_frame(venus, fourth)
    assert mars_fourth["function"] == MARS_FUNCTION
    assert venus_fourth["function"] == VENUS_FUNCTION
    assert mars_fourth["arena"] == venus_fourth["arena"] == FOURTH_ARENA
    assert mars_fourth["verdict"] == venus_fourth["verdict"] == "PASS"

    arenas = []
    for obj in payload["objects"]:
        if obj["type"] != "house":
            continue
        assert "canon" in obj
        assert obj["canon"]["arena"]
        frame = _planet_in_house_frame(moon, obj)
        assert frame["verdict"] == "PASS"
        arenas.append(tuple(frame["arena"]))
    assert len(arenas) == 12
    assert len(set(arenas)) == 12

    for obj in payload["objects"]:
        if obj["type"] == "aspect":
            assert obj["canon"]["relation"]
            assert obj["interaction"] in ("merging", "friction", "flow", "polarization")

    smoke = SMOKE.read_text(encoding="utf-8")
    assert "Moon × 4th house — **PASS**" in smoke
    assert "Moon × 10th house — **PASS**" in smoke
    assert "Mars / Venus × 4th — **PASS**" in smoke
    assert "snapshot" in smoke.lower()
    assert "Forbidden recovery" in smoke
    assert "STOP Houses" in smoke
    assert "seek emotional security at home" in smoke

    prior_sign = SIGN_SMOKE.read_text(encoding="utf-8")
    assert "Moon × 4th house — **PARTIAL**" in prior_sign
    prior_planet = PLANET_SMOKE.read_text(encoding="utf-8")
    assert "Moon × 4th house — **PARTIAL**" in prior_planet

    canon = IL.read_text(encoding="utf-8")
    assert "**Версия:** 1.3.116" in canon
    assert "### 6.47 Planet × House composition smoke" in canon

    next_block = HANDOFF.read_text(encoding="utf-8").split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.93" in next_block
    assert "1.3.94" in next_block
    assert "Planet × House" in next_block
    assert "Mainstream Aspect" in next_block or "Aspect Semantic Map" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "STOP Houses" in next_block
    assert "STOP Signs" in next_block
