"""1.3.102 Angle Canon fill. Two orientation packs. Origin direct. Not objects."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "schemas" / "astrology_interpretation_v1.schema.json"
OBJECTS = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"
FILL = ROOT / "docs" / "astrology" / "ANGLE_CANON_V1.md"
GRAMMAR = ROOT / "docs" / "astrology" / "ANGLE_CANON_GRAMMAR_V1.md"
IL = ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md"
HANDOFF = ROOT / "docs" / "astrology" / "IL1_HANDOFF.md"
INVENTORY = ROOT / "docs" / "astrology" / "KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md"


def _orientation_line(section: str) -> str:
    return section.split("```text")[1].split("```")[0]


def test_angle_canon_v1_fill():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    ids = {obj["object_id"] for obj in payload["objects"]}
    assert len(payload["objects"]) == 38
    assert "astro.object.asc" in ids
    assert "astro.object.mc" in ids
    assert all(obj["status"] != "active" for obj in payload["objects"])

    packs = FILL.read_text(encoding="utf-8")
    assert "Not JSON" in packs or "not JSON" in packs
    assert "direct" in packs
    assert "direct-secondary" in packs
    assert "forbidden here" in packs.lower() or "**forbidden here**" in packs
    assert "Five gates" in packs or "five gates" in packs.lower()
    assert "Collision control" in packs or "collision vs House 1/10" in packs.lower()
    assert "inherited automatically" in packs.lower() or "not the source" in packs.lower()
    assert "### ASC" in packs
    assert "### MC" in packs
    assert "| doorway-meeting | orientation | direct |" in packs
    assert "| how-met | orientation | direct |" in packs
    assert "| automatic-response | orientation | direct |" in packs
    assert "| culmination | orientation | direct |" in packs
    assert "| outer-mark | orientation | direct |" in packs
    assert "| aiming | orientation | direct |" in packs

    asc = packs.split("### ASC")[1].split("### MC")[0]
    asc_line = _orientation_line(asc)
    assert "doorway-meeting" in asc_line
    assert "how-met" in asc_line
    assert "automatic-response" in asc_line
    for forbidden in (
        "appearance",
        "first-impression",
        "self-presentation",
        "mask",
        "career",
        "reputation",
        "calling",
        "personal-facing",
    ):
        assert forbidden not in asc_line

    mc = packs.split("### MC")[1].split("## 3.")[0]
    mc_line = _orientation_line(mc)
    assert "culmination" in mc_line
    assert "outer-mark" in mc_line
    assert "aiming" in mc_line
    for forbidden in (
        "career",
        "public-role",
        "reputation",
        "calling",
        "profession",
        "appearance",
        "first-impression",
        "public-facing",
    ):
        assert forbidden not in mc_line

    assert "Mars AT ASC" in packs
    assert "Mars AT MC" in packs
    assert "Venus AT ASC" in packs
    assert "Mars IN House 1" in packs
    assert "Mars IN House 10" in packs
    assert "planet can occupy House 1 without conjuncting ASC" in packs
    assert "storage/materialization" in packs or "Storage / materialization" in packs
    assert "STOP Angles" in packs

    grammar = GRAMMAR.read_text(encoding="utf-8")
    assert "Angle Canon fill" in grammar
    assert "`orientation`" in grammar

    canon = IL.read_text(encoding="utf-8")
    assert "**Версия:** 1.3.109" in canon
    assert "### 6.56 Angle Canon fill" in canon
    assert canon.count("**Версия:**") == 1

    inventory = INVENTORY.read_text(encoding="utf-8")
    assert "30. Angle Canon fill" in inventory
    assert "✅ 1.3.102" in inventory.split("30. Angle Canon fill")[1].split("31.")[0]
    assert "✅ 1.3.103" in inventory.split("31. Angle Canon storage")[1].split("32.")[0]
    assert "✅ 1.3.104" in inventory.split("32.")[1].split("33.")[0]
    assert "✅ 1.3.105" in inventory.split("33.")[1].split("34.")[0]
    assert "NEXT" in inventory.split("34.")[1].split("```")[0]

    next_block = HANDOFF.read_text(encoding="utf-8").split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.105" in next_block
    assert "1.3.104" in next_block
    assert "1.3.103" in next_block
    assert "1.3.102" in next_block
    assert "1.3.101" in next_block
    assert "1.3.100" in next_block
    assert "1.3.99" in next_block
    assert "1.3.98" in next_block
    assert "storage" in next_block.lower() or "materialization" in next_block.lower()
    assert "Mainstream Angle" in next_block
    assert "Planet × Aspect" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "STOP Aspects" in next_block
    assert "STOP Houses" in next_block
    assert "STOP Signs" in next_block
    assert "Do **not** start ASC cookbooks" in next_block
