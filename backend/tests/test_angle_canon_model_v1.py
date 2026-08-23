"""1.3.99 Angle Canon model — parent 1–4. Not fill. Not objects."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "schemas" / "astrology_interpretation_v1.schema.json"
OBJECTS = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"
MODEL = ROOT / "docs" / "astrology" / "ANGLE_CANON_MODEL_V1.md"
IL = ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md"
HANDOFF = ROOT / "docs" / "astrology" / "IL1_HANDOFF.md"
INVENTORY = ROOT / "docs" / "astrology" / "KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md"
PARENT = ROOT / "docs" / "KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md"


def test_angle_canon_model_v1():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    ids = {obj["object_id"] for obj in payload["objects"]}
    assert len(payload["objects"]) == 38
    assert all(obj["status"] != "active" for obj in payload["objects"])

    model = MODEL.read_text(encoding="utf-8")
    assert "orientation locus" in model.lower() or "Orientation locus" in model
    assert "Routing anchors" in model
    assert "Rejected" in model
    assert "Projection points" in model
    assert "Public–private" in model or "public–private" in model
    assert "ASC ≠ House 1" in model
    assert "MC ≠ House 10" in model
    assert "Named Canon slots" in model
    assert "Unspecified" in model
    assert "Do not copy" in model or "do not copy" in model.lower() or "slots unspecified" in model.lower()
    assert "arena" in model
    assert "manner" in model
    assert "final atomic smoke" in model.lower()
    assert "Mainstream Angle Semantic Map" in model
    assert "Not fill" in model or "not fill" in model.lower()

    canon = IL.read_text(encoding="utf-8")
    assert "**Версия:** 1.3.104" in canon
    assert "### 6.53 Angle Canon model" in canon
    assert "### Architecture impact — 1.3.99 Angle Canon model" in canon
    assert canon.count("**Версия:**") == 1

    inventory = INVENTORY.read_text(encoding="utf-8")
    assert "orientation-locus type locked 1.3.99" in inventory
    assert "28. Mainstream Angle Semantic Map" in inventory
    assert "NEED_MODEL; parent 1–4" not in inventory.split("27. ASC/MC")[1].split("28.")[0]

    parent = PARENT.read_text(encoding="utf-8")
    assert "1.3.99" in parent
    assert "orientation loci" in parent.lower() or "Angle Canon model" in parent

    next_block = HANDOFF.read_text(encoding="utf-8").split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.99" in next_block
    assert "1.3.98" in next_block
    assert "1.3.97" in next_block
    assert "Mainstream Angle Semantic Map" in next_block
    assert "orientation" in next_block.lower()
    assert "Planet × Aspect" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "STOP Aspects" in next_block
    assert "STOP Houses" in next_block
    assert "STOP Signs" in next_block
    assert "Do **not** start ASC cookbooks" in next_block
    assert "NEED_MODEL" not in next_block
