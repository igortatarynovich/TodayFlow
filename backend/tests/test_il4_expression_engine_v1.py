"""1.3.109 IL-4 Expression — voice for already chosen themes. Not meaning. Not freeze/IL-2/IL-3 reopen."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import jsonschema

from todayflow_backend.knowledge.il2_composition_v1 import load_objects
from todayflow_backend.knowledge.il3_interpretation_v1 import SkyFact, interpret
from todayflow_backend.knowledge.il4_expression_v1 import (
    express,
    meaning_is_unchanged,
    two_constructions_stay_two,
)

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "schemas" / "astrology_interpretation_v1.schema.json"
OBJECTS = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"
RULES = ROOT / "docs" / "astrology" / "IL4_EXPRESSION_V1.md"
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
SQUARE_RELATION = ["friction", "blockage", "cross-purposes"]
ASC_ORIENTATION = ["doorway-meeting", "how-met", "automatic-response"]


def test_il4_expression_engine_v1():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    catalog = load_objects(OBJECTS)

    assert len(payload["objects"]) == 38
    assert all(obj["status"] == "draft" for obj in payload["objects"])
    assert all(obj["status"] != "active" for obj in payload["objects"])

    params = inspect.signature(express).parameters
    assert "user" not in params
    assert "person" not in params
    assert "goals" not in params
    assert "character" not in params
    assert "relevance" not in params
    assert "llm" not in params

    natal_house = SkyFact("planet_in_house", ("astro.object.mars", "astro.house.01"))
    natal_sign = SkyFact("planet_in_sign", ("astro.object.mars", "astro.sign.aries"))
    natal_asc = SkyFact("planet_at_angle", ("astro.object.mars", "astro.object.asc"))
    natal_square = SkyFact(
        "aspect_pair",
        ("astro.object.mars", "astro.object.saturn", "astro.aspect.square"),
    )
    transit = SkyFact(
        "transit_to_natal",
        ("astro.object.saturn", "astro.object.venus", "astro.aspect.square"),
    )
    missing = SkyFact(
        "transit_to_natal",
        ("astro.object.pluto", "astro.object.sun", "astro.aspect.square"),
    )

    themes = interpret(
        catalog,
        [natal_sign, natal_house, natal_asc, natal_square, transit, missing],
    )
    today = express(themes, "today")
    profile = express(themes, "profile")
    compatibility = express(themes, "compatibility")

    assert meaning_is_unchanged(today, themes)
    assert meaning_is_unchanged(profile, themes)
    assert meaning_is_unchanged(compatibility, themes)
    assert today.llm_chose_meaning is None
    assert today.person_id is None
    assert today.user_relevance is None
    assert today.meaning_source == "il3_themes"
    assert today.tone == "direct_grounded"
    assert profile.tone == "structural"
    assert compatibility.tone == "relational"

    assert len(today.lines) == 1
    assert today.lines[0].role == "primary"
    assert today.lines[0].band == "transit"
    assert today.lines[0].construction == "transit_to_natal"
    assert len(profile.lines) == 5
    assert [line.construction for line in profile.lines] == [
        theme.frame.construction for theme in themes.themes
    ]
    assert today.lines[0].jobs == profile.lines[0].jobs
    assert profile.lines[0].jobs == compatibility.lines[0].jobs
    assert len(today.dropped) == 1
    assert today.dropped[0].status == "refused"

    house = next(line for line in profile.lines if line.construction == "planet_in_house")
    angle = next(line for line in profile.lines if line.construction == "planet_at_angle")
    aspect = next(line for line in profile.lines if line.construction == "aspect_pair")
    sign = next(line for line in profile.lines if line.construction == "planet_in_sign")
    assert two_constructions_stay_two(house, angle)
    assert two_constructions_stay_two(house, aspect)
    assert sign.jobs["what"] == tuple(MARS_FUNCTION)
    assert sign.jobs["how"] == tuple(ARIES_MANNER)
    assert house.jobs["where"] == tuple(FIRST_ARENA)
    assert angle.jobs["orientation"] == tuple(ASC_ORIENTATION)
    assert aspect.jobs["relation"] == tuple(SQUARE_RELATION)
    assert "career" not in angle.jobs["orientation"]
    assert "how" not in house.jobs
    assert "orientation" not in house.jobs
    assert "where" not in angle.jobs
    assert "act" in sign.text
    assert "initiating" in sign.text
    assert sign.subject_jobs == ("what",)
    assert sign.modifier_jobs == ("how",)
    assert "relation" in aspect.text

    engine = (
        ROOT / "backend" / "src" / "todayflow_backend" / "knowledge" / "il4_expression_v1.py"
    ).read_text(encoding="utf-8")
    assert "openai" not in engine.lower()
    assert "anthropic" not in engine.lower()
    assert "chat.completions" not in engine

    rules = RULES.read_text(encoding="utf-8")
    assert "## Architecture impact" in rules
    assert "user relevance" in rules.lower()
    assert "pair catalog" in rules.lower()
    assert "canonical v2" in rules
    assert "library scale" in rules.lower()
    assert "1.3.109" in rules
    assert "Occupancy ≠ conjunction" in rules or "occupancy ≠ conjunction" in rules.lower()
    assert "House 1 ≠ ASC" in rules
    assert "MC ≠ career" in rules

    freeze = FREEZE.read_text(encoding="utf-8")
    assert "**FROZEN**" in freeze
    assert "library scale" in freeze.lower() or "IL-4" in freeze

    inventory = INVENTORY.read_text(encoding="utf-8")
    assert "37. IL-4 Expression" in inventory
    assert "✅ 1.3.109" in inventory
    assert "NEXT" not in inventory.split("37. IL-4 Expression")[1].split("\n")[0]
    assert "KC-C-EXPR" in inventory

    canon = IL.read_text(encoding="utf-8")
    assert "**Версия:** 1.3.111" in canon
    assert "### 6.63 IL-4 Expression" in canon
    assert canon.count("**Версия:**") == 1

    acm = ACM.read_text(encoding="utf-8")
    assert "IL4_EXPRESSION_V1" in acm

    il3 = IL3.read_text(encoding="utf-8")
    assert "1.3.109" in il3 or "library scale" in il3.lower()

    il2 = IL2.read_text(encoding="utf-8")
    assert "1.3.109" in il2 or "IL-4" in il2

    next_block = HANDOFF.read_text(encoding="utf-8").split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.109" in next_block
    assert "IL-4" in next_block
    assert "library scale" in next_block.lower()
    assert "1.3.108" in next_block
    assert "1.3.107" in next_block
    assert "1.3.106" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "STOP Angles" in next_block
    assert "classification-complete" in next_block
    assert "user relevance" in next_block.lower() or "user Relevance" in next_block

    tracker = TRACKER.read_text(encoding="utf-8")
    now = tracker.split("**NOW (FOUNDATION")[1].split("**PAUSED")[0]
    assert "1.3.109" in now
    assert "IL-4" in now
    assert "1.3.108" in now
    assert "1.3.107" in now
    assert "FREEZE" in now
    assert "1.3.106" in now
    assert "38 draft / 0 `active`" in now or "38 draft / 0 active" in now

    smoke = ATOMIC_SMOKE.read_text(encoding="utf-8")
    assert "1.3.105" in smoke
    assert "IL-4" in smoke
    assert "STOP Angles" in smoke
