"""1.3.108 IL-3 Interpretation Engine — sky-internal theme rank. Not user relevance. Not freeze/IL-2 reopen."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import jsonschema

from todayflow_backend.knowledge.il2_composition_v1 import load_objects
from todayflow_backend.knowledge.il3_interpretation_v1 import (
    SkyFact,
    interpret,
    rank_is_sky_internal,
    two_constructions_stay_two,
)

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "schemas" / "astrology_interpretation_v1.schema.json"
OBJECTS = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"
RULES = ROOT / "docs" / "astrology" / "IL3_INTERPRETATION_ENGINE_V1.md"
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


def test_il3_interpretation_engine_v1():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    catalog = load_objects(OBJECTS)

    assert len(payload["objects"]) == 38
    assert all(obj["status"] == "draft" for obj in payload["objects"])
    assert all(obj["status"] != "active" for obj in payload["objects"])

    params = inspect.signature(interpret).parameters
    assert "user" not in params
    assert "person" not in params
    assert "goals" not in params
    assert "character" not in params
    assert "relevance" not in params

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

    result = interpret(
        catalog,
        [natal_sign, natal_house, natal_asc, natal_square, transit, missing],
    )
    assert rank_is_sky_internal(result)
    assert result.essay is None
    assert result.person_id is None
    assert result.user_relevance is None
    assert len(result.dropped) == 1
    assert result.dropped[0].status == "refused"
    assert "missing_atom" in (result.dropped[0].reason or "")

    assert len(result.themes) == 5
    assert result.themes[0].role == "primary"
    assert result.themes[0].band == "transit"
    assert result.themes[0].frame.construction == "transit_to_natal"
    assert all(theme.role == "supporting" for theme in result.themes[1:])
    assert all(theme.band == "natal" for theme in result.themes[1:])
    assert [theme.frame.construction for theme in result.themes[1:]] == [
        "planet_in_sign",
        "planet_in_house",
        "planet_at_angle",
        "aspect_pair",
    ]

    house_theme = next(t for t in result.themes if t.frame.construction == "planet_in_house")
    angle_theme = next(t for t in result.themes if t.frame.construction == "planet_at_angle")
    aspect_theme = next(t for t in result.themes if t.frame.construction == "aspect_pair")
    sign_theme = next(t for t in result.themes if t.frame.construction == "planet_in_sign")
    assert two_constructions_stay_two(house_theme, angle_theme)
    assert two_constructions_stay_two(house_theme, aspect_theme)
    assert sign_theme.frame.jobs["what"].lemmas == tuple(MARS_FUNCTION)
    assert sign_theme.frame.jobs["how"].lemmas == tuple(ARIES_MANNER)
    assert house_theme.frame.jobs["where"].lemmas == tuple(FIRST_ARENA)
    assert angle_theme.frame.jobs["orientation"].lemmas == tuple(ASC_ORIENTATION)
    assert aspect_theme.frame.jobs["relation"].lemmas == tuple(SQUARE_RELATION)
    assert "career" not in angle_theme.frame.jobs["orientation"].lemmas
    assert "how" not in house_theme.frame.jobs
    assert "orientation" not in house_theme.frame.jobs
    assert "where" not in angle_theme.frame.jobs

    rules = RULES.read_text(encoding="utf-8")
    assert "## Architecture impact" in rules
    assert "user relevance" in rules.lower()
    assert "pair catalog" in rules.lower()
    assert "canonical v2" in rules
    assert "IL-4" in rules
    assert "1.3.108" in rules
    assert "Occupancy ≠ conjunction" in rules or "occupancy ≠ conjunction" in rules.lower()
    assert "House 1 ≠ ASC" in rules
    assert "MC ≠ career" in rules

    freeze = FREEZE.read_text(encoding="utf-8")
    assert "**FROZEN**" in freeze
    assert "IL-4" in freeze

    inventory = INVENTORY.read_text(encoding="utf-8")
    assert "36. IL-3 Interpretation Engine" in inventory
    assert "✅ 1.3.108" in inventory
    assert "NEXT" not in inventory.split("36. IL-3 Interpretation Engine")[1].split("\n")[0]
    assert "KC-C-ENGINE" in inventory

    canon = IL.read_text(encoding="utf-8")
    assert "**Версия:** 1.3.112" in canon
    assert "### 6.62 IL-3 Interpretation Engine" in canon
    assert canon.count("**Версия:**") == 1

    acm = ACM.read_text(encoding="utf-8")
    assert "IL3_INTERPRETATION_ENGINE_V1" in acm

    il2 = IL2.read_text(encoding="utf-8")
    assert "1.3.108" in il2 or "IL-4" in il2

    next_block = HANDOFF.read_text(encoding="utf-8").split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.108" in next_block
    assert "IL-3" in next_block
    assert "IL-4" in next_block
    assert "1.3.107" in next_block
    assert "1.3.106" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "STOP Angles" in next_block
    assert "classification-complete" in next_block
    assert "user relevance" in next_block.lower() or "user Relevance" in next_block

    tracker = TRACKER.read_text(encoding="utf-8")
    now = tracker.split("**NOW (FOUNDATION")[1].split("**PAUSED")[0]
    assert "1.3.108" in now
    assert "IL-3" in now
    assert "IL-4" in now
    assert "1.3.107" in now
    assert "FREEZE" in now
    assert "1.3.106" in now
    assert "38 draft / 0 `active`" in now or "38 draft / 0 active" in now

    smoke = ATOMIC_SMOKE.read_text(encoding="utf-8")
    assert "1.3.105" in smoke
    assert "IL-3" in smoke
    assert "STOP Angles" in smoke
