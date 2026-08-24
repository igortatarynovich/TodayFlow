"""1.3.114 Today meaning polish — native astrology chorus binds to IL-4 packs."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from todayflow_backend.knowledge.il2_composition_v1 import load_objects
from todayflow_backend.knowledge.library_scale_v1 import runtime_is_not_wired
from todayflow_backend.services.day_scenario_native_llm_c1 import NATIVE_PROMPT_VERSION
from todayflow_backend.services.il4_surface_attach_v1 import attach_il4_expression_pack
from todayflow_backend.services.today_meaning_polish_v1 import (
    POLISH_INSTRUCTION_RU,
    augment_native_system,
    fill_empty_astrology_chorus,
    reject_invalid_native,
)

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "schemas" / "astrology_interpretation_v1.schema.json"
OBJECTS = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"
POLISH = ROOT / "docs" / "today" / "TODAY_MEANING_POLISH_V1.md"
CONSUME = ROOT / "docs" / "astrology" / "IL4_EDITORIAL_CONSUME_V1.md"
IL = ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md"
INVENTORY = ROOT / "docs" / "astrology" / "KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md"
HANDOFF = ROOT / "docs" / "astrology" / "IL1_HANDOFF.md"
TRACKER = ROOT / "docs" / "PRODUCT_EXECUTION_TRACKER.md"
MODULE = ROOT / "backend" / "src" / "todayflow_backend" / "services" / "today_meaning_polish_v1.py"
NATIVE = ROOT / "backend" / "src" / "todayflow_backend" / "services" / "day_scenario_native_llm_c1.py"


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


def test_today_meaning_polish_v1():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    load_objects(OBJECTS)

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
    assert pack is not None

    system = augment_native_system("base", pack, locale="ru")
    assert POLISH_INSTRUCTION_RU in system
    assert augment_native_system("base", None) == "base"

    assert reject_invalid_native({"interpretive_chorus": {"astrology": []}}, pack) == "empty_astrology_chorus"
    assert (
        reject_invalid_native(
            {"interpretive_chorus": {"astrology": [{"named_factor": "x", "human_meaning": ""}]}},
            pack,
        )
        == "empty_astrology_chorus"
    )
    assert (
        reject_invalid_native(
            {"interpretive_chorus": {"astrology": [{"named_factor": "x", "human_meaning": "ok"}]}},
            pack,
        )
        is None
    )
    assert reject_invalid_native({"interpretive_chorus": {"astrology": []}}, None) is None

    filled = fill_empty_astrology_chorus({"interpretive_chorus": {"astrology": []}}, pack)
    astro = filled["interpretive_chorus"]["astrology"]
    assert astro and astro[0]["human_meaning"] == pack["lines"][0]["text"]

    kept = fill_empty_astrology_chorus(
        {"interpretive_chorus": {"astrology": [{"human_meaning": "already phrased"}]}},
        pack,
    )
    assert kept["interpretive_chorus"]["astrology"][0]["human_meaning"] == "already phrased"

    src = MODULE.read_text(encoding="utf-8")
    assert "calc_il_wire_v1" not in src
    assert "openai" not in src.lower()

    src_root = ROOT / "backend" / "src" / "todayflow_backend"
    assert runtime_is_not_wired(src_root)
    native_src = NATIVE.read_text(encoding="utf-8")
    assert "today_meaning_polish_v1" in native_src
    assert NATIVE_PROMPT_VERSION == "day-scenario-native-c5.3"

    rules = POLISH.read_text(encoding="utf-8")
    assert "## Architecture impact" in rules
    assert "1.3.114" in rules
    assert "Public contract changed?** no" in rules
    assert "1.3.113" in CONSUME.read_text(encoding="utf-8")

    assert "**Версия:** 1.3.116" in IL.read_text(encoding="utf-8")
    assert "### 6.68" in IL.read_text(encoding="utf-8")

    inventory = INVENTORY.read_text(encoding="utf-8")
    assert "42. Today meaning polish" in inventory
    assert "✅ 1.3.114" in inventory

    handoff = HANDOFF.read_text(encoding="utf-8")
    assert "1.3.114" in handoff or "Today meaning polish" in handoff

    tracker = TRACKER.read_text(encoding="utf-8")
    assert "1.3.114" in tracker or "Today meaning polish" in tracker
