"""1.3.107 IL-2 composition rules — weights, conflict, merge. Not a pair catalog. Not freeze reopen."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from todayflow_backend.knowledge.il2_composition_v1 import (
    LAYER5_DECISIONS,
    ROLE_WEIGHTS,
    compose_aspect_pair,
    compose_planet_at_angle,
    compose_planet_in_house,
    compose_planet_in_sign,
    compose_transit_through_house,
    compose_transit_to_natal,
    house1_is_not_asc,
    house10_is_not_mc,
    interaction_is_not_relation,
    jobs_are_partitioned,
    layer5_decision,
    lemmas_copied_verbatim,
    load_objects,
    mc_is_not_career,
    occupancy_is_not_conjunction,
    two_constructions_stay_two,
)

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "schemas" / "astrology_interpretation_v1.schema.json"
OBJECTS = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"
RULES = ROOT / "docs" / "astrology" / "IL2_COMPOSITION_RULES_V1.md"
FREEZE = ROOT / "docs" / "astrology" / "KNOWLEDGE_CORE_V1_FREEZE.md"
INVENTORY = ROOT / "docs" / "astrology" / "KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md"
IL = ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md"
ACM = ROOT / "docs" / "ASTROLOGY_COMPOSITION_MODEL.md"
HANDOFF = ROOT / "docs" / "astrology" / "IL1_HANDOFF.md"
TRACKER = ROOT / "docs" / "PRODUCT_EXECUTION_TRACKER.md"
ATOMIC_SMOKE = ROOT / "docs" / "astrology" / "ATOMIC_CANON_COMPOSITION_SMOKE_V1.md"

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


def test_il2_composition_rules_v1():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    catalog = load_objects(OBJECTS)

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
    assert all(obj["status"] == "draft" for obj in payload["objects"])
    assert all(obj["status"] != "active" for obj in payload["objects"])
    assert "astro.object.uranus" not in catalog
    assert "astro.object.dsc" not in catalog

    mars_aries = compose_planet_in_sign(catalog, "astro.object.mars", "astro.sign.aries")
    mars_first = compose_planet_in_house(catalog, "astro.object.mars", "astro.house.01")
    mars_asc = compose_planet_at_angle(catalog, "astro.object.mars", "astro.object.asc")
    mars_saturn = compose_aspect_pair(
        catalog, "astro.object.mars", "astro.object.saturn", "astro.aspect.square"
    )
    venus_cap = compose_planet_in_sign(
        catalog, "astro.object.venus", "astro.sign.capricorn"
    )
    moon_fourth = compose_planet_in_house(
        catalog, "astro.object.moon", "astro.house.04"
    )
    mars_mc = compose_planet_at_angle(catalog, "astro.object.mars", "astro.object.mc")
    mars_tenth = compose_planet_in_house(catalog, "astro.object.mars", "astro.house.10")
    saturn_transit = compose_transit_to_natal(
        catalog, "astro.object.saturn", "astro.object.venus", "astro.aspect.square"
    )
    saturn_h10 = compose_transit_through_house(
        catalog, "astro.object.saturn", "astro.house.10"
    )

    assert mars_aries.status == "composed"
    assert mars_aries.jobs["what"].lemmas == tuple(MARS_FUNCTION)
    assert mars_aries.jobs["how"].lemmas == tuple(ARIES_MANNER)
    assert mars_aries.weights == ROLE_WEIGHTS["planet_in_sign"]
    assert mars_aries.essay is None
    assert jobs_are_partitioned(mars_aries)
    assert lemmas_copied_verbatim(mars_aries, catalog)

    assert venus_cap.jobs["what"].lemmas == tuple(VENUS_FUNCTION)
    assert venus_cap.jobs["how"].lemmas == tuple(CAPRICORN_MANNER)
    assert moon_fourth.jobs["what"].lemmas == tuple(MOON_FUNCTION)
    assert moon_fourth.jobs["where"].lemmas == tuple(FOURTH_ARENA)
    assert mars_first.jobs["where"].lemmas == tuple(FIRST_ARENA)
    assert mars_tenth.jobs["where"].lemmas == tuple(TENTH_ARENA)
    assert mars_asc.jobs["orientation"].lemmas == tuple(ASC_ORIENTATION)
    assert mars_mc.jobs["orientation"].lemmas == tuple(MC_ORIENTATION)
    assert mars_saturn.jobs["what_b"].lemmas == tuple(SATURN_FUNCTION)
    assert mars_saturn.jobs["relation"].lemmas == tuple(SQUARE_RELATION)
    assert mars_saturn.weights == {"what_a": 0.50, "what_b": 0.50}
    assert saturn_transit.temporal_class == "transit"
    assert saturn_transit.jobs["relation"].lemmas == tuple(SQUARE_RELATION)
    assert saturn_h10.temporal_class == "transit"
    assert saturn_h10.jobs["where"].lemmas == tuple(TENTH_ARENA)

    assert two_constructions_stay_two(mars_aries, mars_first)
    assert two_constructions_stay_two(mars_first, mars_asc)
    assert two_constructions_stay_two(mars_saturn, mars_asc)
    assert occupancy_is_not_conjunction(mars_first, mars_saturn)
    assert house1_is_not_asc(mars_first, mars_asc)
    assert house10_is_not_mc(mars_tenth, mars_mc)
    assert mc_is_not_career(mars_mc)
    assert interaction_is_not_relation(
        catalog, "astro.aspect.trine", "astro.aspect.sextile"
    )
    assert "how" not in mars_first.jobs
    assert "where" not in mars_aries.jobs
    assert "orientation" not in mars_first.jobs
    assert "relation" not in mars_asc.jobs

    refused = compose_planet_in_sign(
        catalog, "astro.object.uranus", "astro.sign.aries"
    )
    assert refused.status == "refused"
    assert "missing_atom" in refused.reason
    assert refused.jobs == {}
    refused_pluto = compose_aspect_pair(
        catalog, "astro.object.mars", "astro.object.pluto", "astro.aspect.square"
    )
    assert refused_pluto.status == "refused"
    refused_dsc = compose_planet_at_angle(
        catalog, "astro.object.mars", "astro.object.dsc"
    )
    assert refused_dsc.status == "refused"

    assert layer5_decision("planet_in_sign", "mars", "cancer") == "composed"
    assert layer5_decision("planet_in_house", "mars", "01") == "composed"
    assert layer5_decision("natal_aspect", "mars", "saturn", "square") == "composed"
    assert layer5_decision("natal_aspect", "mars", "pluto", "square") == (
        "candidate_missing_atom"
    )
    assert layer5_decision("transit_to_natal", "pluto", "sun", "square") == (
        "candidate_missing_atom"
    )
    assert "composed" in LAYER5_DECISIONS.values()
    assert "candidate_missing_atom" in LAYER5_DECISIONS.values()
    assert all(
        decision in {"composed", "candidate_missing_atom"}
        for decision in LAYER5_DECISIONS.values()
    )

    rules = RULES.read_text(encoding="utf-8")
    assert "## Architecture impact" in rules
    assert "role weights" in rules.lower() or "Role weights" in rules
    assert "Occupancy ≠ conjunction" in rules
    assert "House 1 ≠ ASC" in rules
    assert "MC ≠ career" in rules
    assert "`interaction` ≠ `relation`" in rules or "interaction ≠ relation" in rules
    assert "pair catalog" in rules.lower()
    assert "canonical v2" in rules
    assert "IL-3" in rules
    assert "1.3.107" in rules
    assert "0.55" in rules and "0.45" in rules

    freeze = FREEZE.read_text(encoding="utf-8")
    assert "**FROZEN**" in freeze
    assert "IL-3" in freeze

    inventory = INVENTORY.read_text(encoding="utf-8")
    assert "35. IL-2 composition rules" in inventory
    assert "✅ 1.3.107" in inventory
    assert "NEXT" not in inventory.split("35. IL-2 composition rules")[1].split("\n")[0]
    assert "KC-C-RULES" in inventory

    canon = IL.read_text(encoding="utf-8")
    assert "**Версия:** 1.3.111" in canon
    assert "### 6.61 IL-2 composition rules" in canon or "### 6.61 IL-2 composition rules" in canon
    assert canon.count("**Версия:**") == 1

    acm = ACM.read_text(encoding="utf-8")
    assert "IL2_COMPOSITION_RULES_V1" in acm

    next_block = HANDOFF.read_text(encoding="utf-8").split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.107" in next_block
    assert "IL-2" in next_block
    assert "IL-3" in next_block
    assert "1.3.106" in next_block
    for ver in (
        "1.3.82",
        "1.3.93",
        "1.3.98",
        "1.3.104",
        "1.3.105",
        "1.3.106",
    ):
        assert ver in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "STOP Angles" in next_block
    assert "classification-complete" in next_block

    tracker = TRACKER.read_text(encoding="utf-8")
    now = tracker.split("**NOW (FOUNDATION")[1].split("**PAUSED")[0]
    assert "1.3.107" in now
    assert "IL-2" in now
    assert "IL-3" in now
    assert "1.3.106" in now
    assert "FREEZE" in now
    assert "38 draft / 0 `active`" in now or "38 draft / 0 active" in now

    smoke = ATOMIC_SMOKE.read_text(encoding="utf-8")
    assert "1.3.105" in smoke
    assert "IL-2" in smoke
    assert "STOP Angles" in smoke
