"""1.3.112 IL-4 surface attach — product LLM inputs read IL-4 packs. Not public JSON. Not `active`."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import jsonschema

from todayflow_backend.knowledge.il2_composition_v1 import load_objects
from todayflow_backend.knowledge.library_scale_v1 import runtime_is_not_wired
from todayflow_backend.services.il4_surface_attach_v1 import (
    attach_from_celestial_ephemeris,
    attach_from_chart_pair,
    attach_from_profile_input,
    attach_il4_expression_pack,
    chart_input_from_any,
)

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "schemas" / "astrology_interpretation_v1.schema.json"
OBJECTS = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"
ATTACH = ROOT / "docs" / "astrology" / "IL4_SURFACE_ATTACH_V1.md"
WIRE = ROOT / "docs" / "astrology" / "CALC_IL_WIRE_V1.md"
IL = ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md"
INVENTORY = ROOT / "docs" / "astrology" / "KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md"
HANDOFF = ROOT / "docs" / "astrology" / "IL1_HANDOFF.md"
TRACKER = ROOT / "docs" / "PRODUCT_EXECUTION_TRACKER.md"
GATEWAY = ROOT / "backend" / "src" / "todayflow_backend" / "services" / "il4_surface_attach_v1.py"
DAY_WIRE = ROOT / "backend" / "src" / "todayflow_backend" / "services" / "day_story_wire_v1.py"
PROFILE = ROOT / "backend" / "src" / "todayflow_backend" / "services" / "profile_contract_v1.py"
COMPAT = ROOT / "backend" / "src" / "todayflow_backend" / "services" / "compatibility_llm.py"


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


def test_il4_surface_attach_v1():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    load_objects(OBJECTS)

    assert len(payload["objects"]) == 38
    assert all(obj["status"] == "draft" for obj in payload["objects"])

    params = inspect.signature(attach_il4_expression_pack).parameters
    for forbidden in ("user", "person", "goals", "character", "relevance", "llm"):
        assert forbidden not in params

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

    today = attach_il4_expression_pack(surface="today", natal=natal, transit=transit)
    profile = attach_il4_expression_pack(surface="profile", natal=natal, transit=transit)
    compatibility = attach_il4_expression_pack(surface="compatibility", natal=natal, transit=transit)

    assert today is not None
    assert profile is not None
    assert compatibility is not None
    assert today["surface"] == "today"
    assert today["tone"] == "direct_grounded"
    assert profile["tone"] == "structural"
    assert compatibility["tone"] == "relational"
    assert today["meaning_source"] == "il3_themes"
    assert len(today["lines"]) == 1
    assert len(profile["lines"]) >= len(today["lines"])
    assert today["lines"][0]["band"] == "transit"
    assert "text" in today["lines"][0]
    assert "act" in today["lines"][0]["text"]

    eph = {
        "natal": {
            "role": "natal",
            "bodies": {
                "Mars": {"body": "Mars", "longitude": 1.0, "sign": "Aries"},
                "Saturn": {"body": "Saturn", "longitude": 271.0, "sign": "Capricorn"},
                "Venus": {"body": "Venus", "longitude": 91.0, "sign": "Cancer"},
                "Ascendant": {"body": "Ascendant", "longitude": 0.0, "sign": "Aries"},
            },
            "houses": _equal_houses(0.0),
        },
        "transit_noon": {
            "role": "transit_noon",
            "bodies": {"Saturn": {"body": "Saturn", "longitude": 181.0, "sign": "Libra"}},
            "houses": {},
        },
    }
    from_celestial = attach_from_celestial_ephemeris({"ephemeris": eph}, surface="today")
    assert from_celestial is not None
    assert from_celestial["surface"] == "today"

    from_profile = attach_from_profile_input({"natal": natal}, surface="profile")
    assert from_profile is not None
    assert from_profile["surface"] == "profile"

    from_pair = attach_from_chart_pair(natal, transit, surface="compatibility")
    assert from_pair is not None
    assert from_pair["surface"] == "compatibility"

    assert chart_input_from_any(None) is None
    assert attach_il4_expression_pack(surface="today", natal={"positions": []}) is None

    src = GATEWAY.read_text(encoding="utf-8")
    assert "openai" not in src.lower()
    assert "swisseph" not in src.lower()
    assert "calc_il_wire_v1" in src

    src_root = ROOT / "backend" / "src" / "todayflow_backend"
    assert runtime_is_not_wired(src_root)
    assert "il4_surface_attach_v1" in DAY_WIRE.read_text(encoding="utf-8")
    assert "il4_expression_pack" in DAY_WIRE.read_text(encoding="utf-8")
    assert "il4_surface_attach_v1" in PROFILE.read_text(encoding="utf-8")
    assert "il4_expression_pack" in PROFILE.read_text(encoding="utf-8")
    assert "il4_surface_attach_v1" in COMPAT.read_text(encoding="utf-8")
    assert "il4_expression_pack" in COMPAT.read_text(encoding="utf-8")

    rules = ATTACH.read_text(encoding="utf-8")
    assert "## Architecture impact" in rules
    assert "1.3.112" in rules
    assert "product surfaces" in rules.lower()
    assert "public contract changed?** no" in rules.lower() or "Public contract changed?** no" in rules
    assert "Today prompts" in rules or "meaning SoT" in rules

    assert "1.3.111" in WIRE.read_text(encoding="utf-8")
    assert "**Версия:** 1.3.112" in IL.read_text(encoding="utf-8")
    assert "### 6.66" in IL.read_text(encoding="utf-8")

    inventory = INVENTORY.read_text(encoding="utf-8")
    assert "40. Attach IL-4 to product surfaces" in inventory
    assert "✅ 1.3.112" in inventory
    assert "KC-C-ATTACH" in inventory

    next_block = HANDOFF.read_text(encoding="utf-8").split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.112" in next_block or "surface attach" in next_block.lower()
    assert "1.3.111" in next_block

    tracker = TRACKER.read_text(encoding="utf-8")
    now = tracker.split("**NOW (FOUNDATION")[1].split("**PAUSED")[0]
    assert "1.3.112" in now or "attach IL-4" in now.lower()
    assert "1.3.111" in now
