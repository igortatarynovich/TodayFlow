"""1.3.110 Library Scale V1 — coverage contract. Not pair catalog. Not freeze/IL-2/IL-3/IL-4 reopen."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import jsonschema

from todayflow_backend.knowledge.il2_composition_v1 import (
    LAYER5_DECISIONS,
    house1_is_not_asc,
    load_objects,
    mc_is_not_career,
    occupancy_is_not_conjunction,
)
from todayflow_backend.knowledge.il3_interpretation_v1 import SkyFact, interpret
from todayflow_backend.knowledge.il4_expression_v1 import meaning_is_unchanged, two_constructions_stay_two
from todayflow_backend.knowledge.library_scale_v1 import (
    EXPECTED_COVERED,
    EXPECTED_COVERED_TOTAL,
    EXPECTED_GOLD_CANDIDATE,
    EXPECTED_GOLD_COMPOSED,
    MISSING_EXAMPLES,
    WIRE_CONTRACT,
    every_covered_cell_composes,
    gold_matches_engines,
    report,
    runtime_is_not_wired,
    sample_pack,
)

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "schemas" / "astrology_interpretation_v1.schema.json"
OBJECTS = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"
SCALE = ROOT / "docs" / "astrology" / "LIBRARY_SCALE_V1.md"
IL4 = ROOT / "docs" / "astrology" / "IL4_EXPRESSION_V1.md"
IL3 = ROOT / "docs" / "astrology" / "IL3_INTERPRETATION_ENGINE_V1.md"
IL2 = ROOT / "docs" / "astrology" / "IL2_COMPOSITION_RULES_V1.md"
FREEZE = ROOT / "docs" / "astrology" / "KNOWLEDGE_CORE_V1_FREEZE.md"
INVENTORY = ROOT / "docs" / "astrology" / "KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md"
IL = ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md"
ACM = ROOT / "docs" / "ASTROLOGY_COMPOSITION_MODEL.md"
HANDOFF = ROOT / "docs" / "astrology" / "IL1_HANDOFF.md"
TRACKER = ROOT / "docs" / "PRODUCT_EXECUTION_TRACKER.md"
ATOMIC_SMOKE = ROOT / "docs" / "astrology" / "ATOMIC_CANON_COMPOSITION_SMOKE_V1.md"

MARS_FUNCTION = ["act", "pursue", "assert"]
ARIES_MANNER = ["initiating", "direct", "headlong"]
FIRST_ARENA = ["self-presentation", "appearance", "first-impression"]
TENTH_ARENA = ["career", "public-role", "reputation", "calling"]
SQUARE_RELATION = ["friction", "blockage", "cross-purposes"]
ASC_ORIENTATION = ["doorway-meeting", "how-met", "automatic-response"]
MC_ORIENTATION = ["culmination", "outer-mark", "aiming"]


def test_library_scale_v1():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    catalog = load_objects(OBJECTS)

    assert len(payload["objects"]) == 38
    assert all(obj["status"] == "draft" for obj in payload["objects"])
    assert all(obj["status"] != "active" for obj in payload["objects"])
    assert "astro.object.uranus" not in catalog
    assert "astro.object.neptune" not in catalog
    assert "astro.object.pluto" not in catalog
    assert "astro.object.dsc" not in catalog
    assert "astro.object.ic" not in catalog

    params = inspect.signature(report).parameters
    assert "user" not in params
    assert "person" not in params
    assert "goals" not in params
    assert "character" not in params
    assert "relevance" not in params
    assert "llm" not in params

    coverage = report(catalog)
    assert coverage.by_construction == EXPECTED_COVERED
    assert coverage.total == EXPECTED_COVERED_TOTAL
    assert coverage.gold_composed == EXPECTED_GOLD_COMPOSED
    assert coverage.gold_candidate == EXPECTED_GOLD_CANDIDATE
    assert coverage.catalog_records == 0
    assert coverage.person_id is None
    assert coverage.user_relevance is None
    assert coverage.wire_contract == WIRE_CONTRACT
    assert sum(1 for d in LAYER5_DECISIONS.values() if d == "composed") == 43
    assert sum(1 for d in LAYER5_DECISIONS.values() if d == "candidate_missing_atom") == 12
    assert every_covered_cell_composes(catalog)
    assert gold_matches_engines(catalog)

    for fact in MISSING_EXAMPLES:
        themes = interpret(catalog, [fact])
        assert themes.themes == ()
        assert len(themes.dropped) == 1
        assert themes.dropped[0].status == "refused"

    pack = sample_pack(catalog, "profile")
    today = sample_pack(catalog, "today")
    themes = interpret(
        catalog,
        [
            SkyFact("planet_in_sign", ("astro.object.mars", "astro.sign.aries")),
            SkyFact("planet_in_house", ("astro.object.mars", "astro.house.01")),
            SkyFact("planet_at_angle", ("astro.object.mars", "astro.object.asc")),
            SkyFact(
                "aspect_pair",
                ("astro.object.mars", "astro.object.saturn", "astro.aspect.square"),
            ),
            SkyFact(
                "transit_to_natal",
                ("astro.object.saturn", "astro.object.venus", "astro.aspect.square"),
            ),
            SkyFact("transit_through_house", ("astro.object.saturn", "astro.house.10")),
            SkyFact(
                "transit_to_natal",
                ("astro.object.pluto", "astro.object.sun", "astro.aspect.square"),
            ),
        ],
    )
    assert meaning_is_unchanged(pack, themes)
    assert meaning_is_unchanged(today, themes)
    assert len(today.lines) == 1
    assert today.lines[0].band == "transit"
    assert len(pack.lines) == 6
    assert len(pack.dropped) == 1

    sign = next(line for line in pack.lines if line.construction == "planet_in_sign")
    house = next(line for line in pack.lines if line.construction == "planet_in_house")
    angle = next(line for line in pack.lines if line.construction == "planet_at_angle")
    aspect = next(line for line in pack.lines if line.construction == "aspect_pair")
    through = next(line for line in pack.lines if line.construction == "transit_through_house")
    assert sign.jobs["what"] == tuple(MARS_FUNCTION)
    assert sign.jobs["how"] == tuple(ARIES_MANNER)
    assert house.jobs["where"] == tuple(FIRST_ARENA)
    assert angle.jobs["orientation"] == tuple(ASC_ORIENTATION)
    assert aspect.jobs["relation"] == tuple(SQUARE_RELATION)
    assert through.jobs["where"] == tuple(TENTH_ARENA)
    assert "career" not in angle.jobs["orientation"]
    assert tuple(MC_ORIENTATION) != tuple(TENTH_ARENA)
    assert two_constructions_stay_two(house, angle)
    assert two_constructions_stay_two(house, aspect)

    mars_house = next(t.frame for t in themes.themes if t.frame.construction == "planet_in_house")
    mars_aspect = next(t.frame for t in themes.themes if t.frame.construction == "aspect_pair")
    mars_angle = next(t.frame for t in themes.themes if t.frame.construction == "planet_at_angle")
    assert occupancy_is_not_conjunction(mars_house, mars_aspect)
    assert house1_is_not_asc(mars_house, mars_angle)
    assert mc_is_not_career(mars_angle) or "career" not in mars_angle.jobs["orientation"].lemmas

    src = ROOT / "backend" / "src" / "todayflow_backend"
    assert runtime_is_not_wired(src)
    engine = (src / "knowledge" / "library_scale_v1.py").read_text(encoding="utf-8")
    assert "openai" not in engine.lower()
    assert "anthropic" not in engine.lower()
    assert "chat.completions" not in engine

    scale = SCALE.read_text(encoding="utf-8")
    assert "## Architecture impact" in scale
    assert "pair catalog" in scale.lower()
    assert "canonical v2" in scale
    assert "1.3.110" in scale
    assert "**616**" in scale
    assert "wire calc" in scale.lower() or "Wire contract" in scale
    assert "Occupancy ≠ conjunction" in scale or "occupancy ≠ conjunction" in scale.lower()
    assert "House 1 ≠ ASC" in scale
    assert "MC ≠ career" in scale
    assert "Today prompts" in scale or "Today meaning" in scale

    freeze = FREEZE.read_text(encoding="utf-8")
    assert "**FROZEN**" in freeze
    assert "1.3.110" in freeze or "library scale" in freeze.lower()

    inventory = INVENTORY.read_text(encoding="utf-8")
    assert "38. Library scale" in inventory
    assert "✅ 1.3.110" in inventory
    assert "NEXT" not in inventory.split("38. Library scale")[1].split("\n")[0]
    assert "KC-C-SCALE" in inventory

    canon = IL.read_text(encoding="utf-8")
    assert "**Версия:** 1.3.111" in canon
    assert "### 6.64 Library scale" in canon
    assert canon.count("**Версия:**") == 1

    acm = ACM.read_text(encoding="utf-8")
    assert "LIBRARY_SCALE_V1" in acm

    for locked in (IL4.read_text(encoding="utf-8"), IL3.read_text(encoding="utf-8"), IL2.read_text(encoding="utf-8")):
        assert "1.3.110" in locked or "library scale" in locked.lower()

    next_block = HANDOFF.read_text(encoding="utf-8").split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.110" in next_block
    assert "library scale" in next_block.lower()
    assert "wire calc" in next_block.lower()
    assert "1.3.109" in next_block
    assert "1.3.108" in next_block
    assert "1.3.107" in next_block
    assert "1.3.106" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "STOP Angles" in next_block
    assert "classification-complete" in next_block

    tracker = TRACKER.read_text(encoding="utf-8")
    now = tracker.split("**NOW (FOUNDATION")[1].split("**PAUSED")[0]
    assert "1.3.110" in now
    assert "library scale" in now.lower()
    assert "1.3.109" in now
    assert "1.3.108" in now
    assert "1.3.107" in now
    assert "1.3.106" in now
    assert "38 draft / 0 `active`" in now or "38 draft / 0 active" in now

    smoke = ATOMIC_SMOKE.read_text(encoding="utf-8")
    assert "1.3.105" in smoke
    assert "1.3.110" in smoke or "library scale" in smoke.lower()
    assert "STOP Angles" in smoke
