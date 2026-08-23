"""1.3.82 composition smoke-test — diagnostic frames from catalog atoms. Not IL-2."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "schemas" / "astrology_interpretation_v1.schema.json"
OBJECTS = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"
SMOKE = ROOT / "docs" / "astrology" / "PLANET_CANON_COMPOSITION_SMOKE_V1.md"
IL = ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md"
HANDOFF = ROOT / "docs" / "astrology" / "IL1_HANDOFF.md"

SIGN_LATER_INTERPRETIVE = (
    "motivation",
    "expression",
    "strengths",
    "excess",
    "deficiency",
    "behavioral_tendencies",
)


def _by_id(payload: dict) -> dict:
    return {obj["object_id"]: obj for obj in payload["objects"]}


def _aspect_pair_frame(left: dict, right: dict, aspect: dict) -> dict:
    return {
        "type": "aspect_pair",
        "left": {
            "object_id": left["object_id"],
            "core_function": list(left["canon"]["core_function"]),
            "drive": list(left["canon"]["drive"]),
        },
        "right": {
            "object_id": right["object_id"],
            "core_function": list(right["canon"]["core_function"]),
            "drive": list(right["canon"]["drive"]),
        },
        "operator": aspect["interaction"],
        "payload_determined": True,
        "manner": None,
        "missing": None,
        "verdict": "PASS",
    }


def _planet_in_sign_frame(planet: dict, sign: dict) -> dict:
    return {
        "type": "planet_in_sign",
        "function": list(planet["canon"]["core_function"]),
        "drive": list(planet["canon"]["drive"]),
        "modifier_labels": {
            "mode": sign["mode"],
            "element": sign["element"],
            "orientation": sign["orientation"],
        },
        "manner": None,
        "payload_determined": False,
        "missing": "sign_canon.manner_operator",
        "verdict": "PARTIAL",
    }


def _planet_in_house_frame(planet: dict, house: dict) -> dict:
    return {
        "type": "planet_in_house",
        "function": list(planet["canon"]["core_function"]),
        "drive": list(planet["canon"]["drive"]),
        "planet_domains": list(planet["canon"]["domains"]),
        "house_domain_present": "domain" in house,
        "house_domain_shape": "classical_prose" if isinstance(house.get("domain"), str) else None,
        "house_arena_lemmas": None,
        "payload_determined": False,
        "missing": "house_canon.domain_lemmas",
        "verdict": "PARTIAL",
    }


def test_composition_smoke_four_constructions():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    by_id = _by_id(payload)

    mars_saturn = _aspect_pair_frame(
        by_id["astro.object.mars"],
        by_id["astro.object.saturn"],
        by_id["astro.aspect.square"],
    )
    assert mars_saturn["operator"] == "friction"
    assert mars_saturn["left"]["core_function"] == ["act", "pursue", "assert"]
    assert mars_saturn["right"]["core_function"] == ["limit", "structure", "mature"]
    assert mars_saturn["verdict"] == "PASS"
    assert mars_saturn["missing"] is None

    venus_cap = _planet_in_sign_frame(by_id["astro.object.venus"], by_id["astro.sign.capricorn"])
    assert venus_cap["function"] == ["attract", "value", "relate"]
    assert venus_cap["modifier_labels"] == {
        "mode": "cardinal",
        "element": "earth",
        "orientation": "negative",
    }
    assert venus_cap["manner"] is None
    assert venus_cap["verdict"] == "PARTIAL"
    for key in SIGN_LATER_INTERPRETIVE:
        assert key not in by_id["astro.sign.capricorn"]

    moon_fourth = _planet_in_house_frame(by_id["astro.object.moon"], by_id["astro.house.04"])
    assert moon_fourth["function"] == ["feel", "respond", "protect"]
    assert moon_fourth["planet_domains"] == ["emotions", "needs", "security", "the-familiar"]
    assert moon_fourth["house_arena_lemmas"] is None
    assert moon_fourth["house_domain_shape"] == "classical_prose"
    assert moon_fourth["verdict"] == "PARTIAL"
    assert isinstance(by_id["astro.house.04"]["domain"], str)

    jupiter_sun = _aspect_pair_frame(
        by_id["astro.object.jupiter"],
        by_id["astro.object.sun"],
        by_id["astro.aspect.trine"],
    )
    assert jupiter_sun["operator"] == "flow"
    assert "meaning" in jupiter_sun["left"]["drive"]
    assert "purpose" in jupiter_sun["right"]["drive"]
    assert "purpose" not in jupiter_sun["left"]["drive"]
    assert jupiter_sun["payload_determined"] is True
    assert jupiter_sun["verdict"] == "PASS"

    assert by_id["astro.object.mars"]["function"] != "act"
    assert "heating" in by_id["astro.object.mars"]["function"]

    smoke = SMOKE.read_text(encoding="utf-8")
    assert "Mars □ Saturn — **PASS**" in smoke
    assert "Venus × Capricorn — **PARTIAL**" in smoke
    assert "Moon × 4th house — **PARTIAL**" in smoke
    assert "Jupiter △ Sun — **PASS**" in smoke
    assert "Sign Canon **manner operator**" in smoke
    assert "House Canon" in smoke
    assert "Forbidden recovery" in smoke
    assert "**Verdict:** PASS" in smoke
    assert "**Verdict:** PARTIAL" in smoke

    canon = IL.read_text(encoding="utf-8")
    assert "**Версия:** 1.3.114" in canon
    assert "### 6.36 Planet Canon composition smoke" in canon
    next_block = HANDOFF.read_text(encoding="utf-8").split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.82" in next_block
    assert "1.3.83" in next_block
    assert "1.3.84" in next_block
    assert "1.3.85" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "Sign Canon" in next_block
