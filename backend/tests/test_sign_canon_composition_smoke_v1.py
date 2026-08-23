"""1.3.88 Planet × Sign composition smoke — frames from stored sign.canon. Not IL-2."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "schemas" / "astrology_interpretation_v1.schema.json"
OBJECTS = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"
SMOKE = ROOT / "docs" / "astrology" / "SIGN_CANON_COMPOSITION_SMOKE_V1.md"
PRIOR = ROOT / "docs" / "astrology" / "PLANET_CANON_COMPOSITION_SMOKE_V1.md"
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

CAPRICORN_MANNER = ["reserved", "disciplined", "structured"]
CAPRICORN_EXCESS = ["withholding", "hardening"]
SCORPIO_MANNER = ["intense", "probing", "concentrated"]
ARIES_MANNER = ["initiating", "direct", "headlong"]


def _by_id(payload: dict) -> dict:
    return {obj["object_id"]: obj for obj in payload["objects"]}


def _planet_in_sign_frame(planet: dict, sign: dict) -> dict:
    manner = list(sign["canon"]["manner"])
    excess = list(sign["canon"]["excess"])
    determined = bool(manner)
    return {
        "type": "planet_in_sign",
        "planet_id": planet["object_id"],
        "sign_id": sign["object_id"],
        "function": list(planet["canon"]["core_function"]),
        "drive": list(planet["canon"]["drive"]),
        "manner": manner,
        "excess": excess,
        "modifier_labels": {
            "mode": sign["mode"],
            "element": sign["element"],
            "orientation": sign["orientation"],
        },
        "payload_determined": determined,
        "missing": None if determined else "sign_canon.manner_operator",
        "verdict": "PASS" if determined else "PARTIAL",
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


def test_sign_canon_composition_smoke_v1():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    by_id = _by_id(payload)

    venus = by_id["astro.object.venus"]
    mercury = by_id["astro.object.mercury"]
    mars = by_id["astro.object.mars"]
    moon = by_id["astro.object.moon"]
    capricorn = by_id["astro.sign.capricorn"]
    scorpio = by_id["astro.sign.scorpio"]
    aries = by_id["astro.sign.aries"]

    venus_cap = _planet_in_sign_frame(venus, capricorn)
    assert venus_cap["function"] == ["attract", "value", "relate"]
    assert venus_cap["manner"] == CAPRICORN_MANNER
    assert venus_cap["excess"] == CAPRICORN_EXCESS
    assert venus_cap["verdict"] == "PASS"
    assert venus_cap["missing"] is None
    assert venus_cap["payload_determined"] is True
    assert "practical" not in venus_cap["manner"]
    assert "ambition" not in venus_cap["manner"]
    assert venus_cap["modifier_labels"]["element"] == "earth"

    venus_sco = _planet_in_sign_frame(venus, scorpio)
    assert venus_sco["manner"] == SCORPIO_MANNER
    assert venus_sco["verdict"] == "PASS"
    assert venus_cap["manner"] != venus_sco["manner"]

    for planet in (venus, mercury, mars, moon):
        frame = _planet_in_sign_frame(planet, capricorn)
        assert frame["manner"] == CAPRICORN_MANNER
        assert frame["excess"] == CAPRICORN_EXCESS
        assert frame["verdict"] == "PASS"

    mars_aries = _planet_in_sign_frame(mars, aries)
    mars_cap = _planet_in_sign_frame(mars, capricorn)
    assert aries["mode"] == capricorn["mode"] == "cardinal"
    assert mars_aries["manner"] == ARIES_MANNER
    assert mars_cap["manner"] == CAPRICORN_MANNER
    assert "initiating" not in mars_cap["manner"]
    assert mars_aries["verdict"] == mars_cap["verdict"] == "PASS"

    manners = []
    for obj in payload["objects"]:
        if obj["type"] != "sign":
            continue
        for key in SIGN_LATER_INTERPRETIVE:
            assert key not in obj
        frame = _planet_in_sign_frame(venus, obj)
        assert frame["verdict"] == "PASS"
        assert frame["manner"]
        manners.append(tuple(frame["manner"]))
    assert len(manners) == 12
    assert len(set(manners)) == 12

    moon_fourth = _planet_in_house_frame(moon, by_id["astro.house.04"])
    assert moon_fourth["verdict"] == "PARTIAL"
    assert moon_fourth["house_arena_lemmas"] is None
    assert moon_fourth["missing"] == "house_canon.domain_lemmas"
    assert by_id["astro.house.04"]["canon"]["arena"] == [
        "home",
        "family",
        "roots",
        "private-base",
    ]

    smoke = SMOKE.read_text(encoding="utf-8")
    assert "Venus × Capricorn — **PASS**" in smoke
    assert "Venus × Scorpio — **PASS**" in smoke
    assert "Mercury / Mars / Moon × Capricorn — **PASS**" in smoke
    assert "Mars × Aries vs Mars × Capricorn — **PASS**" in smoke
    assert "Moon × 4th house — **PARTIAL**" in smoke
    assert "earth → practical" in smoke
    assert "Forbidden recovery" in smoke
    assert "STOP Signs" in smoke

    prior = PRIOR.read_text(encoding="utf-8")
    assert "Venus × Capricorn — **PARTIAL**" in prior

    canon = IL.read_text(encoding="utf-8")
    assert "**Версия:** 1.3.111" in canon
    assert "### 6.42 Planet × Sign composition smoke" in canon

    next_block = HANDOFF.read_text(encoding="utf-8").split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.88" in next_block
    assert "1.3.87" in next_block
    assert "1.3.85" in next_block
    assert "Planet × Sign" in next_block
    assert "House" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "STOP Signs" in next_block or "Stop Signs" in next_block or "STOP Signs" in HANDOFF.read_text(encoding="utf-8")
