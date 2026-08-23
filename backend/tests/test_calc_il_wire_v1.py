"""1.3.111 calc → IL wire. Snapshots to IL-4 packs. Not Swiss. Not Today prompts. Not `active`."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import jsonschema

from todayflow_backend.knowledge.calc_il_wire_v1 import skyfacts_from_calc, wire_calc_to_il
from todayflow_backend.knowledge.il2_composition_v1 import (
    house1_is_not_asc,
    house10_is_not_mc,
    load_objects,
    mc_is_not_career,
    occupancy_is_not_conjunction,
    two_constructions_stay_two as il2_two,
)
from todayflow_backend.knowledge.il3_interpretation_v1 import interpret, rank_is_sky_internal
from todayflow_backend.knowledge.il4_expression_v1 import meaning_is_unchanged

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "schemas" / "astrology_interpretation_v1.schema.json"
OBJECTS = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1" / "objects_v1.json"
WIRE = ROOT / "docs" / "astrology" / "CALC_IL_WIRE_V1.md"
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
ENGINE = ROOT / "backend" / "src" / "todayflow_backend" / "knowledge" / "calc_il_wire_v1.py"

MARS_FUNCTION = ("act", "pursue", "assert")
ARIES_MANNER = ("initiating", "direct", "headlong")
FIRST_ARENA = ("self-presentation", "appearance", "first-impression")
TENTH_ARENA = ("career", "public-role", "reputation", "calling")
SQUARE_RELATION = ("friction", "blockage", "cross-purposes")
ASC_ORIENTATION = ("doorway-meeting", "how-met", "automatic-response")
MC_ORIENTATION = ("culmination", "outer-mark", "aiming")


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


def _chart(positions: list[dict], houses: dict | None = None) -> dict:
    return {"positions": positions, "houses": houses or {}}


def test_calc_il_wire_v1():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    catalog = load_objects(OBJECTS)

    assert len(payload["objects"]) == 38
    assert all(obj["status"] == "draft" for obj in payload["objects"])
    assert all(obj["status"] != "active" for obj in payload["objects"])

    params = inspect.signature(wire_calc_to_il).parameters
    for forbidden in ("user", "person", "goals", "character", "relevance", "llm"):
        assert forbidden not in params

    natal = _chart(
        [
            _pos("mars", "Aries", 1.0, 1),
            _pos("saturn", "Capricorn", 271.0, 10),
            _pos("venus", "Cancer", 91.0, 4),
            _pos("uranus", "Aries", 15.0, 1),
            _pos("rising", "Aries", 0.0),
        ],
        _equal_houses(0.0),
    )
    transit = _chart(
        [
            _pos("saturn", "Libra", 181.0),
            _pos("uranus", "Libra", 200.0),
        ]
    )

    facts = skyfacts_from_calc(natal, transit)
    kinds = [fact.construction for fact in facts]
    assert kinds.index("transit_to_natal") < kinds.index("planet_in_sign")
    assert any(
        fact.construction == "transit_to_natal"
        and fact.parts
        == ("astro.object.saturn", "astro.object.venus", "astro.aspect.square")
        for fact in facts
    )
    assert any(
        fact.construction == "transit_through_house"
        and fact.parts == ("astro.object.saturn", "astro.house.07")
        for fact in facts
    )
    assert any(
        fact.construction == "planet_at_angle"
        and fact.parts == ("astro.object.mars", "astro.object.asc")
        for fact in facts
    )
    assert any(
        fact.construction == "planet_at_angle"
        and fact.parts == ("astro.object.saturn", "astro.object.mc")
        for fact in facts
    )
    assert any(fact.parts[0] == "astro.object.uranus" for fact in facts)
    assert all("dsc" not in part and ".ic" not in part for fact in facts for part in fact.parts)
    assert not any(part == "astro.object.rising" for fact in facts for part in fact.parts)

    occupancy = skyfacts_from_calc(
        _chart(
            [_pos("mars", "Aries", 20.0, 1), _pos("rising", "Aries", 0.0)],
            _equal_houses(0.0),
        )
    )
    assert any(
        fact.construction == "planet_in_house"
        and fact.parts == ("astro.object.mars", "astro.house.01")
        for fact in occupancy
    )
    assert not any(fact.construction == "planet_at_angle" for fact in occupancy)
    assert not any(
        fact.construction == "aspect_pair" and "astro.aspect.conjunction" in fact.parts
        for fact in occupancy
    )

    tenth = skyfacts_from_calc(
        _chart(
            [_pos("saturn", "Capricorn", 290.0, 10), _pos("rising", "Aries", 0.0)],
            _equal_houses(0.0),
        )
    )
    assert any(
        fact.construction == "planet_in_house"
        and fact.parts == ("astro.object.saturn", "astro.house.10")
        for fact in tenth
    )
    assert not any(
        fact.construction == "planet_at_angle" and fact.parts[1] == "astro.object.mc"
        for fact in tenth
    )

    themes = interpret(catalog, facts)
    today = wire_calc_to_il(natal, transit=transit, surface="today", catalog=catalog)
    profile = wire_calc_to_il(natal, transit=transit, surface="profile", catalog=catalog)
    compatibility = wire_calc_to_il(
        natal, transit=transit, surface="compatibility", catalog=catalog
    )

    assert rank_is_sky_internal(themes)
    assert meaning_is_unchanged(today, themes)
    assert meaning_is_unchanged(profile, themes)
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
    assert len(profile.lines) == len(themes.themes)
    assert [line.construction for line in profile.lines] == [
        theme.frame.construction for theme in themes.themes
    ]
    assert len(compatibility.lines) == len(profile.lines)
    assert any(frame.status == "refused" for frame in today.dropped)
    assert any("missing_atom" in (frame.reason or "") for frame in today.dropped)

    house = next(
        theme
        for theme in themes.themes
        if theme.frame.construction == "planet_in_house"
        and theme.frame.jobs["what"].lemmas == MARS_FUNCTION
    )
    angle = next(
        theme
        for theme in themes.themes
        if theme.frame.construction == "planet_at_angle"
        and theme.frame.jobs["orientation"].lemmas == ASC_ORIENTATION
    )
    tenth_theme = next(
        theme
        for theme in themes.themes
        if theme.frame.construction == "planet_in_house"
        and theme.frame.jobs["where"].lemmas == TENTH_ARENA
    )
    mc_theme = next(
        theme
        for theme in themes.themes
        if theme.frame.construction == "planet_at_angle"
        and theme.frame.jobs["orientation"].lemmas == MC_ORIENTATION
    )
    sign = next(
        theme
        for theme in themes.themes
        if theme.frame.construction == "planet_in_sign"
        and theme.frame.jobs["what"].lemmas == MARS_FUNCTION
    )
    aspect = next(theme for theme in themes.themes if theme.frame.construction == "aspect_pair")
    assert il2_two(house.frame, angle.frame)
    assert house1_is_not_asc(house.frame, angle.frame)
    assert house10_is_not_mc(tenth_theme.frame, mc_theme.frame)
    assert mc_is_not_career(mc_theme.frame)
    assert occupancy_is_not_conjunction(house.frame, aspect.frame)
    assert sign.frame.jobs["how"].lemmas == ARIES_MANNER
    assert house.frame.jobs["where"].lemmas == FIRST_ARENA
    assert aspect.frame.jobs["relation"].lemmas == SQUARE_RELATION
    assert "how" not in house.frame.jobs
    assert "orientation" not in house.frame.jobs
    assert "where" not in angle.frame.jobs

    sign_line = next(
        line
        for line in profile.lines
        if line.construction == "planet_in_sign" and line.jobs["what"] == MARS_FUNCTION
    )
    assert "act" in sign_line.text
    assert "initiating" in sign_line.text

    unknown = skyfacts_from_calc(
        _chart([_pos("mars", "Aries", 1.0), _pos("saturn", "Capricorn", 271.0)])
    )
    assert any(fact.construction == "planet_in_sign" for fact in unknown)
    assert any(fact.construction == "aspect_pair" for fact in unknown)
    assert not any(fact.construction == "planet_in_house" for fact in unknown)
    assert not any(fact.construction == "planet_at_angle" for fact in unknown)

    source = ENGINE.read_text(encoding="utf-8")
    assert "openai" not in source.lower()
    assert "anthropic" not in source.lower()
    assert "chat.completions" not in source
    assert "swisseph" not in source.lower()
    assert "today_prompt" not in source

    after = json.loads(OBJECTS.read_text(encoding="utf-8"))
    assert all(obj["status"] == "draft" for obj in after["objects"])
    assert all(obj["status"] != "active" for obj in after["objects"])

    rules = WIRE.read_text(encoding="utf-8")
    assert "## Architecture impact" in rules
    assert "product surfaces" in rules.lower()
    assert "pair catalog" in rules.lower()
    assert "canonical v2" in rules
    assert "1.3.111" in rules
    assert "Occupancy ≠ conjunction" in rules or "occupancy ≠ conjunction" in rules.lower()
    assert "House 1 ≠ ASC" in rules
    assert "MC ≠ career" in rules
    assert "House 10 ≠ MC" in rules

    assert "1.3.111" in SCALE.read_text(encoding="utf-8")
    freeze = FREEZE.read_text(encoding="utf-8")
    assert "**FROZEN**" in freeze
    assert "1.3.111" in freeze

    inventory = INVENTORY.read_text(encoding="utf-8")
    assert "39. Wire calc → IL" in inventory
    assert "✅ 1.3.111" in inventory
    assert "NEXT" not in inventory.split("39. Wire calc → IL")[1].split("\n")[0]
    assert "KC-C-WIRE" in inventory

    canon = IL.read_text(encoding="utf-8")
    assert "**Версия:** 1.3.111" in canon
    assert "### 6.65" in canon
    assert canon.count("**Версия:**") == 1

    assert "CALC_IL_WIRE_V1" in ACM.read_text(encoding="utf-8")

    next_block = HANDOFF.read_text(encoding="utf-8").split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.111" in next_block
    assert "1.3.110" in next_block
    assert "library scale" in next_block.lower()
    assert "1.3.109" in next_block
    assert "IL-4" in next_block
    assert "1.3.108" in next_block
    assert "1.3.107" in next_block
    assert "1.3.106" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "STOP Angles" in next_block
    assert "classification-complete" in next_block
    assert "user relevance" in next_block.lower() or "user Relevance" in next_block
    assert "product surfaces" in next_block.lower() or "attach IL-4" in next_block.lower()

    tracker = TRACKER.read_text(encoding="utf-8")
    now = tracker.split("**NOW (FOUNDATION")[1].split("**PAUSED")[0]
    assert "1.3.111" in now
    assert "1.3.110" in now
    assert "1.3.109" in now
    assert "IL-4" in now
    assert "1.3.108" in now
    assert "1.3.107" in now
    assert "FREEZE" in now
    assert "1.3.106" in now
    assert "38 draft / 0 `active`" in now or "38 draft / 0 active" in now

    smoke = ATOMIC_SMOKE.read_text(encoding="utf-8")
    assert "1.3.105" in smoke
    assert "1.3.111" in smoke
    assert "STOP Angles" in smoke

    assert "1.3.111" in IL4.read_text(encoding="utf-8")
    assert "1.3.111" in IL3.read_text(encoding="utf-8")
    assert "1.3.111" in IL2.read_text(encoding="utf-8")
