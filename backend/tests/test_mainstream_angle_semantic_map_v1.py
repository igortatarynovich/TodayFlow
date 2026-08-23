"""1.3.100 Mainstream Angle Semantic Map. Concept families. No ingest. No objects. No Canon slots."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "schemas" / "astrology_interpretation_v1.schema.json"
OBJECTS = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"
ANGLE_MAP = ROOT / "docs" / "astrology" / "MAINSTREAM_ANGLE_SEMANTIC_MAP_V1.md"
MODEL = ROOT / "docs" / "astrology" / "ANGLE_CANON_MODEL_V1.md"
IL = ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md"
HANDOFF = ROOT / "docs" / "astrology" / "IL1_HANDOFF.md"


def test_mainstream_angle_semantic_map_v1():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    ids = {obj["object_id"] for obj in payload["objects"]}
    assert len(payload["objects"]) == 38
    assert all(obj["status"] != "active" for obj in payload["objects"])

    angle_map = ANGLE_MAP.read_text(encoding="utf-8")
    assert "Astrology.com" in angle_map
    assert "Astrodienst" in angle_map
    assert "Cafe Astrology" in angle_map
    assert "concept family" in angle_map.lower() or "concept families" in angle_map.lower()
    assert "Not JSON" in angle_map or "not JSON" in angle_map
    assert "House 1 / House 10 vocabulary is not proof" in angle_map
    assert "Angular strength / prominence is not meaning" in angle_map
    assert "Planet conjunct ASC / MC" in angle_map
    assert "doorway-meeting" in angle_map
    assert "personal-facing" in angle_map
    assert "culmination / height" in angle_map
    assert "public-facing" in angle_map
    assert "House 1 collision" in angle_map
    assert "House 10 collision" in angle_map
    assert "planet can occupy House 1 without conjuncting ASC" in angle_map
    assert "deletion test" in angle_map.lower()
    assert "STOP Angles" in angle_map
    assert "stored Planet×Angle smoke" in angle_map or "stored Planet×Angle" in angle_map
    assert "Angle Canon Grammar" in angle_map or "Angle Canon grammar" in angle_map
    for heading in ("### ASC", "### MC"):
        assert heading in angle_map
    assert "**Include**" in angle_map
    assert "**Exclude**" in angle_map
    assert "rising-sign portraits" in angle_map.lower() or "twelve rising" in angle_map.lower()
    assert "MC-in-sign" in angle_map

    model = MODEL.read_text(encoding="utf-8")
    assert "orientation locus" in model.lower() or "Orientation locus" in model
    assert "stored Planet×Angle smoke" in model or "STOP Angles" in model

    canon = IL.read_text(encoding="utf-8")
    assert "**Версия:** 1.3.106" in canon
    assert "### 6.54 Mainstream Angle Semantic Map" in canon
    assert canon.count("**Версия:**") == 1

    next_block = HANDOFF.read_text(encoding="utf-8").split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.100" in next_block
    assert "1.3.99" in next_block
    assert "1.3.98" in next_block
    assert "Mainstream Angle" in next_block
    assert "Angle Canon" in next_block or "Angle Canon grammar" in next_block
    assert "Planet × Aspect" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "STOP Aspects" in next_block
    assert "STOP Houses" in next_block
    assert "STOP Signs" in next_block
    assert "Do **not** start ASC cookbooks" in next_block
