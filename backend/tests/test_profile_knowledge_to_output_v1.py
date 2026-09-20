"""Profile knowledge-to-output — natal facts through IL and Character Engine.

Not a new SoT. Not a pair catalog. Not P1 library fill.
Pass bound: one real construction (Mars × sign × house) must remain distinguishable
from calculated natal through IL composition and Character Engine evidence.

Today this file records:
- IL does compose distinct Mars frames.
- Character Engine Stage 0 still holds the Mars sign/house in the fact value.
- Stage 1 / Identity Core collapse same-Sun charts to the same thesis.
- character_engine_* does not import IL.

The xfail is the wire to invert: IL constructions in Stage 1 claims.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from todayflow_backend.knowledge.calc_il_wire_v1 import skyfacts_from_calc, wire_calc_to_il
from todayflow_backend.services.character_engine_stage0_facts_v0 import (
    build_character_engine_facts_pack_v0,
)
from todayflow_backend.services.character_engine_stage1_evidence_v0 import (
    build_character_engine_evidence_candidates_v0,
)
from todayflow_backend.services.character_engine_stage2_identity_v0 import (
    build_character_engine_identity_core_v0,
)

CE_ROOT = Path(__file__).resolve().parents[1] / "src" / "todayflow_backend" / "services"

CAPABILITY = {
    "natal_mode": "full",
    "has_name": True,
    "has_birth_time": True,
    "has_birth_place": True,
}

# Same Sun (Virgo) / Moon (Taurus) / ASC (Gemini). Only Mars sign + house differ.
# Mars is not fire, so Stage 1 drive_through_fire_mars does not fire.
CHART_A = {
    "id": "virgo_mars_cancer_h4",
    "mars_sign": "Cancer",
    "mars_house": 4,
    "chart": {
        "positions": [
            {"body": "Sun", "sign": "Virgo", "degree": 15.0, "longitude": 165.0, "house": 6},
            {"body": "Moon", "sign": "Taurus", "degree": 10.0, "longitude": 40.0, "house": 2},
            {"body": "Mercury", "sign": "Virgo", "degree": 4.0, "longitude": 154.0, "house": 6},
            {"body": "Mars", "sign": "Cancer", "degree": 12.0, "longitude": 102.0, "house": 4},
            {"body": "Ascendant", "sign": "Gemini", "degree": 2.0, "longitude": 62.0},
            {"body": "rising", "sign": "Gemini", "degree": 2.0, "longitude": 62.0},
        ],
        "houses": {f"house_{i}": {"longitude": (62.0 + (i - 1) * 30.0) % 360.0} for i in range(1, 13)},
    },
}

CHART_B = {
    "id": "virgo_mars_libra_h7",
    "mars_sign": "Libra",
    "mars_house": 7,
    "chart": {
        "positions": [
            {"body": "Sun", "sign": "Virgo", "degree": 15.0, "longitude": 165.0, "house": 6},
            {"body": "Moon", "sign": "Taurus", "degree": 10.0, "longitude": 40.0, "house": 2},
            {"body": "Mercury", "sign": "Virgo", "degree": 4.0, "longitude": 154.0, "house": 6},
            {"body": "Mars", "sign": "Libra", "degree": 12.0, "longitude": 192.0, "house": 7},
            {"body": "Ascendant", "sign": "Gemini", "degree": 2.0, "longitude": 62.0},
            {"body": "rising", "sign": "Gemini", "degree": 2.0, "longitude": 62.0},
        ],
        "houses": {f"house_{i}": {"longitude": (62.0 + (i - 1) * 30.0) % 360.0} for i in range(1, 13)},
    },
}


def _il_mars_keys(chart: dict) -> set[tuple[str, tuple[str, ...]]]:
    keys: set[tuple[str, tuple[str, ...]]] = set()
    for fact in skyfacts_from_calc(chart):
        if "mars" not in " ".join(fact.parts).lower():
            continue
        keys.add((fact.construction, fact.parts))
    return keys


def _ce_hop(case: dict) -> dict:
    facts = build_character_engine_facts_pack_v0(
        profile_fingerprint=case["id"],
        swiss_chart=case["chart"],
        numerology={"life_path": 7},
        capability=CAPABILITY,
        birth_date="1991-09-08",
        input_fingerprint=case["id"],
    )
    evidence = build_character_engine_evidence_candidates_v0(facts)
    identity = build_character_engine_identity_core_v0(
        facts_pack=facts,
        evidence=evidence,
        deterministic_only=True,
    )
    mars_fact = next(
        (
            row
            for row in facts.get("raw_facts") or []
            if isinstance(row, dict) and row.get("fact_type") == "planet_sign:mars"
        ),
        None,
    )
    mars_value = mars_fact.get("value") if isinstance(mars_fact, dict) else None
    claims = [
        str(c.get("thesis_key"))
        for c in (evidence.get("claims") or [])
        if isinstance(c, dict) and c.get("evidence_status") == "grounded"
    ]
    core = identity.get("identity_core") if isinstance(identity.get("identity_core"), dict) else {}
    validation = identity.get("validation") if isinstance(identity.get("validation"), dict) else {}
    return {
        "id": case["id"],
        "mars_fact_sign": (mars_value or {}).get("sign") if isinstance(mars_value, dict) else None,
        "mars_fact_house": (mars_value or {}).get("house") if isinstance(mars_value, dict) else None,
        "stage1_thesis_keys": sorted(claims),
        "identity_thesis": core.get("thesis_key"),
        "identity_surface": core.get("surface_text"),
        "deterministic": bool(validation.get("deterministic_fallback")),
    }


def test_il_composes_distinct_mars_sign_and_house() -> None:
    keys_a = _il_mars_keys(CHART_A["chart"])
    keys_b = _il_mars_keys(CHART_B["chart"])
    assert ("planet_in_sign", ("astro.object.mars", "astro.sign.cancer")) in keys_a
    assert ("planet_in_house", ("astro.object.mars", "astro.house.04")) in keys_a
    assert ("planet_in_sign", ("astro.object.mars", "astro.sign.libra")) in keys_b
    assert ("planet_in_house", ("astro.object.mars", "astro.house.07")) in keys_b
    assert keys_a != keys_b

    pack_a = wire_calc_to_il(CHART_A["chart"], surface="profile")
    pack_b = wire_calc_to_il(CHART_B["chart"], surface="profile")
    assert pack_a.meaning_source == "il3_themes"
    assert pack_a.llm_chose_meaning is None
    texts_a = {line.text for line in pack_a.lines}
    texts_b = {line.text for line in pack_b.lines}
    assert texts_a != texts_b


def test_ce_stage0_keeps_mars_sign_and_house_value() -> None:
    hop_a = _ce_hop(CHART_A)
    hop_b = _ce_hop(CHART_B)
    assert hop_a["mars_fact_sign"] == "cancer"
    assert hop_a["mars_fact_house"] == 4
    assert hop_b["mars_fact_sign"] == "libra"
    assert hop_b["mars_fact_house"] == 7


def test_character_engine_modules_do_not_import_il() -> None:
    offenders: list[str] = []
    for path in sorted(CE_ROOT.glob("character_engine_*.py")):
        text = path.read_text(encoding="utf-8")
        if "todayflow_backend.knowledge" in text or "il2_composition" in text or "calc_il_wire" in text:
            offenders.append(path.name)
    assert offenders == []


def test_same_sun_different_mars_identity_collapses() -> None:
    hop_a = _ce_hop(CHART_A)
    hop_b = _ce_hop(CHART_B)
    assert hop_a["stage1_thesis_keys"] == hop_b["stage1_thesis_keys"]
    assert hop_a["identity_thesis"] == hop_b["identity_thesis"]
    assert hop_a["identity_surface"] == hop_b["identity_surface"]
    assert hop_a["identity_thesis"] == "builds_through_analysis"
    assert hop_a["identity_surface"] == (
        "Ты строишь через анализ до шага — сначала понять устройство, потом выбрать."
    )
    assert hop_a["deterministic"] is True
    assert "cancer" not in (hop_a["identity_surface"] or "").lower()
    assert "libra" not in (hop_b["identity_surface"] or "").lower()
    assert "mars" not in (hop_a["identity_surface"] or "").lower()


@pytest.mark.xfail(strict=True, reason="Profile knowledge-to-output: IL constructions not in CE Stage 1 yet")
def test_il_mars_constructions_reach_stage1_claims() -> None:
    hop_a = _ce_hop(CHART_A)
    hop_b = _ce_hop(CHART_B)
    blob_a = " ".join(hop_a["stage1_thesis_keys"]).lower()
    blob_b = " ".join(hop_b["stage1_thesis_keys"]).lower()
    assert hop_a["stage1_thesis_keys"] != hop_b["stage1_thesis_keys"]
    assert "cancer" in blob_a or "house.04" in blob_a or "mars" in blob_a
    assert "libra" in blob_b or "house.07" in blob_b or "mars" in blob_b
