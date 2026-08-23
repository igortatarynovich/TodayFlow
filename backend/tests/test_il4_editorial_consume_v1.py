"""1.3.113 IL-4 editorial consume — generation phrases packs. Not public JSON. Not overwrite."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from todayflow_backend.knowledge.il2_composition_v1 import load_objects
from todayflow_backend.knowledge.library_scale_v1 import runtime_is_not_wired
from todayflow_backend.services.il4_editorial_consume_v1 import (
    CONSUME_INSTRUCTION_RU,
    augment_system_prompt,
    compact_meaning,
    fill_empty_slot,
    pack_present,
    protected_block,
    reject_invalid_output,
)
from todayflow_backend.services.il4_surface_attach_v1 import attach_il4_expression_pack

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "schemas" / "astrology_interpretation_v1.schema.json"
OBJECTS = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"
CONSUME = ROOT / "docs" / "astrology" / "IL4_EDITORIAL_CONSUME_V1.md"
ATTACH = ROOT / "docs" / "astrology" / "IL4_SURFACE_ATTACH_V1.md"
IL = ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md"
INVENTORY = ROOT / "docs" / "astrology" / "KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md"
HANDOFF = ROOT / "docs" / "astrology" / "IL1_HANDOFF.md"
TRACKER = ROOT / "docs" / "PRODUCT_EXECUTION_TRACKER.md"
MODULE = ROOT / "backend" / "src" / "todayflow_backend" / "services" / "il4_editorial_consume_v1.py"
NATIVE = ROOT / "backend" / "src" / "todayflow_backend" / "services" / "day_scenario_native_llm_c1.py"
PROFILE = ROOT / "backend" / "src" / "todayflow_backend" / "services" / "profile_contract_v1.py"
COMPAT = ROOT / "backend" / "src" / "todayflow_backend" / "services" / "compatibility_llm.py"
BRIEF = ROOT / "backend" / "src" / "todayflow_backend" / "services" / "day_scenario_dramaturgy_brief_c4.py"


def _pos(body: str, sign: str, longitude: float, house: int | None = None) -> dict:
    return {
        "body": body,
        "sign": sign,
        "degree": longitude % 30,
        "longitude": longitude,
        "house": house,
    }


def _equal_houses(asc: float = 0.0) -> dict:
    return {f"house_{i}": {"longitude": (asc + (i - 1) * 30) % 360} for i in range(1, 13)}


def test_il4_editorial_consume_v1():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    load_objects(OBJECTS)

    assert len(payload["objects"]) == 38
    assert all(obj["status"] == "draft" for obj in payload["objects"])

    natal = {
        "positions": [
            _pos("mars", "Aries", 1.0, 1),
            _pos("saturn", "Capricorn", 271.0, 10),
            _pos("venus", "Cancer", 91.0, 4),
            _pos("rising", "Aries", 0.0),
        ],
        "houses": _equal_houses(0.0),
    }
    transit = {"positions": [_pos("saturn", "Libra", 181.0)], "houses": {}}
    pack = attach_il4_expression_pack(surface="today", natal=natal, transit=transit)
    assert pack_present(pack)
    compact = compact_meaning(pack)
    assert compact is not None
    assert compact["meaning_source"] == "il3_themes"
    assert compact["lines"][0]["text"] == pack["lines"][0]["text"]
    assert "act" in compact["lines"][0]["text"]

    system = augment_system_prompt("base", pack, locale="ru")
    assert CONSUME_INSTRUCTION_RU in system
    assert augment_system_prompt("base", None) == "base"
    assert "IL4_MEANING" in protected_block(pack)

    filled = fill_empty_slot("", pack)
    assert filled == pack["lines"][0]["text"]
    assert fill_empty_slot("already phrased", pack) == "already phrased"

    assert reject_invalid_output({"conflict": {"title": "сцена"}}, pack) is None
    assert reject_invalid_output("", pack) == "empty_output"
    assert reject_invalid_output({"llm_chose_meaning": True}, pack) == "llm_chose_meaning"
    mutated = {"il4_expression_pack": {**pack, "lines": [{**pack["lines"][0], "text": "invented"}]}}
    assert reject_invalid_output(mutated, pack) == "mutated_pack_lemmas"
    refused = {
        "surface": "today",
        "lines": pack["lines"],
        "dropped": [{"construction": "transit_to_natal", "reason": "missing atom astro.object.uranus"}],
    }
    assert reject_invalid_output(
        {"interpretive_chorus": {"astrology": [{"named_factor": "uranus"}]}},
        refused,
    )

    src = MODULE.read_text(encoding="utf-8")
    assert "calc_il_wire_v1" not in src
    assert "openai" not in src.lower()
    assert "swisseph" not in src.lower()

    src_root = ROOT / "backend" / "src" / "todayflow_backend"
    assert runtime_is_not_wired(src_root)
    assert "il4_editorial_consume_v1" in NATIVE.read_text(encoding="utf-8")
    assert "il4_editorial_consume_v1" in PROFILE.read_text(encoding="utf-8")
    assert "il4_editorial_consume_v1" in COMPAT.read_text(encoding="utf-8")
    assert "meaning_block" in BRIEF.read_text(encoding="utf-8")

    rules = CONSUME.read_text(encoding="utf-8")
    assert "## Architecture impact" in rules
    assert "1.3.113" in rules
    assert "Public contract changed?** no" in rules
    assert "fill-empty" in rules.lower() or "Fill-empty" in rules or "fill empty" in rules.lower()
    assert "Today prompts" in rules or "meaning SoT" in rules
    assert "1.3.112" in ATTACH.read_text(encoding="utf-8")

    assert "**Версия:** 1.3.114" in IL.read_text(encoding="utf-8")
    assert "### 6.67" in IL.read_text(encoding="utf-8")

    inventory = INVENTORY.read_text(encoding="utf-8")
    assert "41. Consume IL-4 in editorial generation" in inventory
    assert "✅ 1.3.113" in inventory
    assert "42. Today meaning polish" in inventory
    assert "✅ 1.3.114" in inventory
    assert "KC-C-CONSUME" in inventory

    next_block = HANDOFF.read_text(encoding="utf-8").split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.113" in next_block or "editorial consume" in next_block.lower()
    assert "1.3.112" in next_block

    tracker = TRACKER.read_text(encoding="utf-8")
    now = tracker.split("**NOW (FOUNDATION")[1].split("**PAUSED")[0]
    assert "1.3.114" in now or "meaning polish" in now.lower()
    assert "1.3.113" in now or "consume" in now.lower()
