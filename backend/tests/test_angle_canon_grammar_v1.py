"""1.3.101 Angle Canon grammar. One slot (orientation). Not fill. Not objects."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "schemas" / "astrology_interpretation_v1.schema.json"
OBJECTS = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"
GRAMMAR = ROOT / "docs" / "astrology" / "ANGLE_CANON_GRAMMAR_V1.md"
MODEL = ROOT / "docs" / "astrology" / "ANGLE_CANON_MODEL_V1.md"
ANGLE_MAP = ROOT / "docs" / "astrology" / "MAINSTREAM_ANGLE_SEMANTIC_MAP_V1.md"
IL = ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md"
HANDOFF = ROOT / "docs" / "astrology" / "IL1_HANDOFF.md"
INVENTORY = ROOT / "docs" / "astrology" / "KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md"


def test_angle_canon_grammar_v1():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    ids = {obj["object_id"] for obj in payload["objects"]}
    assert len(payload["objects"]) == 38
    assert all(obj["status"] != "active" for obj in payload["objects"])

    grammar = GRAMMAR.read_text(encoding="utf-8")
    assert "Not fill" in grammar or "not fill" in grammar.lower()
    assert "Not JSON" in grammar or "not JSON" in grammar
    assert "`orientation`" in grammar
    assert "One. Not two." in grammar or "one required slot" in grammar.lower()
    assert "Include-first" in grammar or "include-first" in grammar.lower()
    assert "collision-zone" in grammar.lower()
    assert "doorway-meeting" in grammar
    assert "how-met" in grammar
    assert "automatic-response" in grammar
    assert "culmination" in grammar
    assert "aiming" in grammar
    assert "appearance" in grammar
    assert "first-impression" in grammar
    assert "career" in grammar
    assert "reputation" in grammar
    assert "calling" in grammar
    assert "House.arena" in grammar or "house.1.arena" in grammar
    assert "without house.1.arena" in grammar
    assert "without house.10.arena" in grammar
    assert "planet can occupy House 1 without conjuncting ASC" in grammar
    assert "Negative control — Mars IN House 1" in grammar
    assert "Forbidden" in grammar
    assert "Surplus" in grammar
    assert "facing" in grammar.lower()
    assert "public–private" in grammar or "public-private" in grammar
    assert "Angle Canon fill" in grammar
    assert "STOP Angles" in grammar
    assert "stored Planet×Angle smoke" in grammar or "stored Planet×Angle" in grammar
    assert "This pass does not do" in grammar

    model = MODEL.read_text(encoding="utf-8")
    assert "orientation locus" in model.lower() or "Orientation locus" in model
    assert "`orientation`" in model or "orientation" in model

    angle_map = ANGLE_MAP.read_text(encoding="utf-8")
    assert "House 1 collision" in angle_map
    assert "House 10 collision" in angle_map

    canon = IL.read_text(encoding="utf-8")
    assert "**Версия:** 1.3.109" in canon
    assert "### 6.55 Angle Canon grammar" in canon
    assert canon.count("**Версия:**") == 1

    inventory = INVENTORY.read_text(encoding="utf-8")
    assert "29. Angle Canon grammar" in inventory
    assert "one slot (`orientation`)" in inventory.split("29. Angle Canon grammar")[1].split("30.")[0]
    assert "✅ 1.3.102" in inventory.split("30. Angle Canon fill")[1].split("31.")[0]

    next_block = HANDOFF.read_text(encoding="utf-8").split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.101" in next_block
    assert "1.3.100" in next_block
    assert "1.3.99" in next_block
    assert "1.3.98" in next_block
    assert "orientation" in next_block.lower()
    assert "Angle Canon fill" in next_block or "storage" in next_block.lower()
    assert "Mainstream Angle" in next_block
    assert "Planet × Aspect" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "STOP Aspects" in next_block
    assert "STOP Houses" in next_block
    assert "STOP Signs" in next_block
    assert "Do **not** start ASC cookbooks" in next_block
