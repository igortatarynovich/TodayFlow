"""1.3.98 stored Planet × Aspect composition smoke — frames from aspect.canon.relation. Not IL-2."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "schemas" / "astrology_interpretation_v1.schema.json"
OBJECTS = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"
SMOKE = ROOT / "docs" / "astrology" / "ASPECT_CANON_COMPOSITION_SMOKE_V1.md"
PRIOR = ROOT / "docs" / "astrology" / "PLANET_CANON_COMPOSITION_SMOKE_V1.md"
IL = ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md"
HANDOFF = ROOT / "docs" / "astrology" / "IL1_HANDOFF.md"

SQUARE_RELATION = ["friction", "blockage", "cross-purposes"]
OPPOSITION_RELATION = ["polarity", "facing", "the-other"]
TRINE_RELATION = ["easy-flow", "support", "natural-ease"]
SEXTILE_RELATION = ["ease-with-participation", "directed-potential", "cooperation"]
CONJUNCTION_RELATION = ["blend", "fuse", "immediate-connection"]

MARS_FUNCTION = ["act", "pursue", "assert"]
SATURN_FUNCTION = ["limit", "structure", "mature"]
VENUS_FUNCTION = ["attract", "value", "relate"]
JUPITER_FUNCTION = ["expand", "believe"]
SUN_FUNCTION = ["identify", "vitalize", "will"]
MERCURY_FUNCTION = ["think", "communicate", "learn"]

TOPOLOGY_FORBIDDEN = (
    "growth",
    "luck",
    "outcome",
    "success",
    "failure",
    "good",
    "bad",
    "harmonious",
    "difficult",
    "challenge",
    "opportunity",
    "stronger",
)


def _by_id(payload: dict) -> dict:
    return {obj["object_id"]: obj for obj in payload["objects"]}


def _aspect_pair_frame(planet_a: dict, planet_b: dict, aspect: dict) -> dict:
    relation = list(aspect["canon"]["relation"])
    determined = bool(relation)
    return {
        "type": "aspect_pair",
        "planet_a_id": planet_a["object_id"],
        "planet_b_id": planet_b["object_id"],
        "aspect_id": aspect["object_id"],
        "function_a": list(planet_a["canon"]["core_function"]),
        "function_b": list(planet_b["canon"]["core_function"]),
        "relation": relation,
        "legacy_interaction": aspect["interaction"],
        "payload_determined": determined,
        "missing": None if determined else "aspect_canon.relation",
        "verdict": "PASS" if determined else "PARTIAL",
    }


def _bogus_interaction_frame(aspect: dict) -> dict:
    return {"relation": [aspect["interaction"]]}


def test_aspect_canon_composition_smoke_v1():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    by_id = _by_id(payload)

    mars = by_id["astro.object.mars"]
    saturn = by_id["astro.object.saturn"]
    venus = by_id["astro.object.venus"]
    jupiter = by_id["astro.object.jupiter"]
    sun = by_id["astro.object.sun"]
    mercury = by_id["astro.object.mercury"]
    square = by_id["astro.aspect.square"]
    opposition = by_id["astro.aspect.opposition"]
    trine = by_id["astro.aspect.trine"]
    sextile = by_id["astro.aspect.sextile"]
    conjunction = by_id["astro.aspect.conjunction"]

    mars_square = _aspect_pair_frame(mars, saturn, square)
    assert mars_square["function_a"] == MARS_FUNCTION
    assert mars_square["function_b"] == SATURN_FUNCTION
    assert mars_square["relation"] == SQUARE_RELATION
    assert mars_square["relation"] == list(square["canon"]["relation"])
    assert mars_square["legacy_interaction"] == "friction"
    assert mars_square["relation"] != [mars_square["legacy_interaction"]]
    assert mars_square["verdict"] == "PASS"
    assert mars_square["missing"] is None
    assert mars_square["payload_determined"] is True
    assert "story" not in mars_square
    assert "essay" not in mars_square

    venus_square = _aspect_pair_frame(venus, saturn, square)
    assert venus_square["function_a"] == VENUS_FUNCTION
    assert venus_square["function_b"] == SATURN_FUNCTION
    assert venus_square["relation"] == mars_square["relation"] == SQUARE_RELATION
    assert venus_square["verdict"] == "PASS"
    assert venus_square["aspect_id"] == mars_square["aspect_id"] == "astro.aspect.square"

    mars_opposition = _aspect_pair_frame(mars, saturn, opposition)
    assert mars_opposition["function_a"] == mars_square["function_a"]
    assert mars_opposition["function_b"] == mars_square["function_b"]
    assert mars_opposition["relation"] == OPPOSITION_RELATION
    assert mars_opposition["legacy_interaction"] == "polarization"
    assert mars_square["relation"] != mars_opposition["relation"]
    assert "friction" not in mars_opposition["relation"]
    assert "the-other" not in mars_square["relation"]
    assert mars_opposition["verdict"] == "PASS"

    venus_trine = _aspect_pair_frame(venus, mars, trine)
    venus_sextile = _aspect_pair_frame(venus, mars, sextile)
    assert venus_trine["function_a"] == venus_sextile["function_a"] == VENUS_FUNCTION
    assert venus_trine["function_b"] == venus_sextile["function_b"] == MARS_FUNCTION
    assert venus_trine["legacy_interaction"] == venus_sextile["legacy_interaction"] == "flow"
    assert venus_trine["relation"] == TRINE_RELATION
    assert venus_sextile["relation"] == SEXTILE_RELATION
    assert venus_trine["relation"] != venus_sextile["relation"]
    assert "flow" not in venus_trine["relation"]
    assert "flow" not in venus_sextile["relation"]
    assert "natural-ease" in venus_trine["relation"]
    assert "natural-ease" not in venus_sextile["relation"]
    assert "ease-with-participation" in venus_sextile["relation"]
    assert "ease-with-participation" not in venus_trine["relation"]
    assert _bogus_interaction_frame(trine)["relation"] == _bogus_interaction_frame(sextile)["relation"] == ["flow"]
    assert venus_trine["verdict"] == venus_sextile["verdict"] == "PASS"

    sun_conjunction = _aspect_pair_frame(sun, mercury, conjunction)
    jupiter_trine = _aspect_pair_frame(jupiter, sun, trine)
    assert sun_conjunction["function_a"] == SUN_FUNCTION
    assert sun_conjunction["function_b"] == MERCURY_FUNCTION
    assert sun_conjunction["relation"] == CONJUNCTION_RELATION
    assert jupiter_trine["function_a"] == JUPITER_FUNCTION
    assert jupiter_trine["relation"] == TRINE_RELATION
    assert sun_conjunction["relation"] != jupiter_trine["relation"]
    assert sun_conjunction["legacy_interaction"] == "merging"
    assert "harmonious" not in " ".join(sun_conjunction["relation"])
    assert "difficult" not in " ".join(sun_conjunction["relation"])
    assert sun_conjunction["verdict"] == jupiter_trine["verdict"] == "PASS"

    for obj in payload["objects"]:
        if obj["type"] != "aspect":
            continue
        assert obj["status"] == "draft"
        assert obj["canon"]["relation"]
        blob = " ".join(obj["canon"]["relation"])
        for word in TOPOLOGY_FORBIDDEN:
            assert word not in blob.split(), (obj["object_id"], word)
        frame = _aspect_pair_frame(mars, saturn, obj)
        assert frame["verdict"] == "PASS"
        assert frame["relation"] == list(obj["canon"]["relation"])
        assert frame["relation"] != [obj["interaction"]]

    assert "astro.object.asc" not in by_id
    assert "astro.object.mc" not in by_id

    smoke = SMOKE.read_text(encoding="utf-8")
    assert "Mars □ Saturn — **PASS**" in smoke
    assert "Venus □ Saturn — **PASS**" in smoke
    assert "Square ≠ Opposition" in smoke
    assert "Trine ≠ Sextile" in smoke
    assert "Conjunction ≠ Trine" in smoke
    assert "interaction=flow" in smoke
    assert "snapshot" in smoke.lower()
    assert "Forbidden recovery" in smoke
    assert "STOP Aspects" in smoke
    assert "delayed action that makes you grow" in smoke
    assert "Trine = luck" in smoke

    prior = PRIOR.read_text(encoding="utf-8")
    assert "Mars □ Saturn — **PASS**" in prior
    assert "square `interaction`: `friction`" in prior

    canon = IL.read_text(encoding="utf-8")
    assert "**Версия:** 1.3.100" in canon
    assert "### 6.52 Planet × Aspect composition smoke" in canon

    next_block = HANDOFF.read_text(encoding="utf-8").split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.98" in next_block
    assert "1.3.97" in next_block
    assert "1.3.96" in next_block
    assert "1.3.95" in next_block
    assert "1.3.94" in next_block
    assert "1.3.93" in next_block
    assert "1.3.92" in next_block
    assert "1.3.91" in next_block
    assert "1.3.90" in next_block
    assert "Planet × Aspect" in next_block
    assert "Aspect Canon fill" in next_block
    assert "House Canon fill" in next_block
    assert "House Canon storage" in next_block
    assert "ASC/MC" in next_block or "ASC" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "STOP Aspects" in next_block
    assert "STOP Houses" in next_block
    assert "STOP Signs" in next_block
