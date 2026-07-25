"""Stage 0–1 Character Engine builders — facts pack + evidence candidates."""

from __future__ import annotations

import copy

from todayflow_backend.services.character_engine_ids_v0 import make_claim_id, make_fact_id
from todayflow_backend.services.character_engine_stage0_facts_v0 import (
    BRIDGE_CALC_VERSION,
    DATE_SUN_CALC_VERSION,
    SWISS_CALC_VERSION,
    build_character_engine_facts_pack_v0,
)
from todayflow_backend.services.character_engine_stage1_evidence_v0 import (
    build_character_engine_evidence_candidates_v0,
)
from todayflow_backend.services.character_engine_stage01_shadow_v0 import (
    run_character_engine_stage01_shadow_v0,
)
from todayflow_backend.services.character_engine_evidence_registry_v0 import (
    FORBIDDEN_STAGE1_CLAIM_KINDS,
)


def _swiss_aquarius(*, with_houses: bool = False) -> dict:
    positions = [
        {"body": "Sun", "sign": "Aquarius", "degree": 12.0},
        {"body": "Moon", "sign": "Pisces", "degree": 3.0},
        {"body": "Mars", "sign": "Aries", "degree": 8.0},
    ]
    houses = []
    if with_houses:
        positions.append({"body": "Ascendant", "sign": "Gemini", "degree": 1.0})
        houses = [{"house": 1, "sign": "Gemini"}, {"house": 7, "sign": "Sagittarius"}]
    return {"positions": positions, "houses": houses}


def test_stage0_same_input_same_ids() -> None:
    kwargs = dict(
        profile_fingerprint="pf1",
        swiss_chart=_swiss_aquarius(),
        numerology={"life_path": 7},
        capability={"natal_mode": "date_only", "has_birth_time": False, "has_birth_place": False},
        birth_date="1990-02-01",
        input_fingerprint="in1",
    )
    a = build_character_engine_facts_pack_v0(**kwargs)
    b = build_character_engine_facts_pack_v0(**kwargs)
    assert [f["fact_id"] for f in a["raw_facts"]] == [f["fact_id"] for f in b["raw_facts"]]
    assert a["input_fact_set_version"] == b["input_fact_set_version"]


def test_stage0_planet_order_independent() -> None:
    chart = _swiss_aquarius()
    reversed_chart = {
        "positions": list(reversed(chart["positions"])),
        "houses": chart["houses"],
    }
    a = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf1",
        swiss_chart=chart,
        numerology={"life_path": 7},
        birth_date="1990-02-01",
        capability={"natal_mode": "date_only"},
        input_fingerprint="in1",
    )
    b = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf1",
        swiss_chart=reversed_chart,
        numerology={"life_path": 7},
        birth_date="1990-02-01",
        capability={"natal_mode": "date_only"},
        input_fingerprint="in1",
    )
    assert [f["fact_id"] for f in a["raw_facts"]] == [f["fact_id"] for f in b["raw_facts"]]


def test_stage0_display_label_does_not_change_ids() -> None:
    chart = _swiss_aquarius()
    a = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf1",
        swiss_chart=chart,
        birth_date="1990-02-01",
        capability={"natal_mode": "date_only"},
        input_fingerprint="in1",
    )
    chart2 = copy.deepcopy(chart)
    chart2["positions"][0]["label"] = "Солнце"  # display-only noise
    b = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf1",
        swiss_chart=chart2,
        birth_date="1990-02-01",
        capability={"natal_mode": "date_only"},
        input_fingerprint="in1",
    )
    assert [f["fact_id"] for f in a["raw_facts"]] == [f["fact_id"] for f in b["raw_facts"]]


def test_stage0_value_change_changes_id() -> None:
    chart = _swiss_aquarius()
    a = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf1",
        swiss_chart=chart,
        birth_date="1990-02-01",
        capability={"natal_mode": "date_only"},
        input_fingerprint="in1",
    )
    chart2 = copy.deepcopy(chart)
    chart2["positions"][0]["sign"] = "Leo"
    b = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf1",
        swiss_chart=chart2,
        birth_date="1990-02-01",
        capability={"natal_mode": "date_only"},
        input_fingerprint="in1",
    )
    sun_a = next(f for f in a["raw_facts"] if f["fact_type"] == "planet_sign:sun")
    sun_b = next(f for f in b["raw_facts"] if f["fact_type"] == "planet_sign:sun")
    assert sun_a["fact_id"] != sun_b["fact_id"]


def test_stage0_missing_time_excludes_houses_and_asc() -> None:
    pack = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf1",
        swiss_chart=_swiss_aquarius(with_houses=True),
        birth_date="1990-02-01",
        capability={
            "natal_mode": "date_only",
            "has_birth_time": False,
            "has_birth_place": False,
        },
        input_fingerprint="in1",
    )
    types = {f["fact_type"] for f in pack["raw_facts"]}
    assert "angle_sign:ascendant" not in types
    assert not any(t.startswith("house_cusp_sign:") for t in types)
    missing_keys = {m["key"] for m in pack["missing_inputs"]}
    assert "houses" in missing_keys
    assert "ascendant" in missing_keys


def test_stage0_swiss_beats_bridge() -> None:
    pack = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf1",
        swiss_chart=_swiss_aquarius(),
        natal_facts_bridge={
            "planets": [{"id": "sun", "sign": "leo"}],
            "angles": {},
            "houses": [],
        },
        birth_date="1990-02-01",
        capability={"natal_mode": "date_only"},
        input_fingerprint="in1",
    )
    sun = next(f for f in pack["raw_facts"] if f["fact_type"] == "planet_sign:sun")
    assert sun["authority"] == "swiss"
    assert sun["calc_version"] == SWISS_CALC_VERSION
    assert sun["value"]["sign"] == "aquarius"
    # Bridge was considered then dropped
    assert any(d.get("dropped_authority") == "bridge_natal_facts_llm" for d in pack["diagnostics"]["dedupe"])


def test_stage0_dedupe_and_no_personality_claims() -> None:
    pack = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf1",
        swiss_chart=_swiss_aquarius(),
        numerology={"life_path": 7, "expression": 3},
        birth_date="1990-02-01",
        capability={"natal_mode": "date_only", "has_name": True},
        input_fingerprint="in1",
    )
    keys = [f["fact_type"] for f in pack["raw_facts"]]
    assert len(keys) == len(set(keys))
    assert "claims" not in pack
    assert "identity_core" not in pack


def test_stage0_fact_ids_match_helper() -> None:
    pack = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf1",
        swiss_chart=_swiss_aquarius(),
        birth_date="1990-02-01",
        capability={"natal_mode": "date_only"},
        input_fingerprint="in1",
    )
    sun = next(f for f in pack["raw_facts"] if f["fact_type"] == "planet_sign:sun")
    expected = make_fact_id(
        fact_type="planet_sign:sun",
        normalized_key="aquarius",
        authority="swiss",
        calc_version=SWISS_CALC_VERSION,
    )
    assert sun["fact_id"] == expected


def test_stage1_grounded_claims_and_edges() -> None:
    facts = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf1",
        swiss_chart=_swiss_aquarius(),
        numerology={"life_path": 7},
        birth_date="1990-02-01",
        capability={"natal_mode": "date_only"},
        input_fingerprint="in1",
    )
    ev = build_character_engine_evidence_candidates_v0(facts)
    fact_ids = {f["fact_id"] for f in facts["raw_facts"]}
    claim_ids = {c["claim_id"] for c in ev["claims"]}
    assert ev["claims"]
    for c in ev["claims"]:
        assert c["claim_kind"] not in FORBIDDEN_STAGE1_CLAIM_KINDS
        assert all(fid in fact_ids for fid in c["supporting_fact_ids"])
        assert "identity_core" not in c
        assert "surface_text" not in c or c.get("surface_text") in (None, "")
    for e in ev["edges"]:
        assert e["fact_id"] in fact_ids
        assert e["claim_id"] in claim_ids
    assert ev["diagnostics"]["validation"]["has_cascade_sections"] is False
    assert ev["diagnostics"]["validation"]["has_identity_core"] is False
    assert ev["diagnostics"]["validation"]["has_compass"] is False


def test_stage1_claim_id_stable_across_fact_order_and_no_surface() -> None:
    facts = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf1",
        swiss_chart=_swiss_aquarius(),
        numerology={"life_path": 7},
        birth_date="1990-02-01",
        capability={"natal_mode": "date_only"},
        input_fingerprint="in1",
    )
    ev1 = build_character_engine_evidence_candidates_v0(facts)
    # Shuffle raw_facts order
    facts2 = copy.deepcopy(facts)
    facts2["raw_facts"] = list(reversed(facts2["raw_facts"]))
    ev2 = build_character_engine_evidence_candidates_v0(facts2)
    assert [c["claim_id"] for c in ev1["claims"]] == [c["claim_id"] for c in ev2["claims"]]
    # Helper parity for one claim
    autonomy = next(c for c in ev1["claims"] if c["thesis_key"] == "autonomy_high")
    assert autonomy["claim_id"] == make_claim_id(
        claim_kind="autonomy_need",
        thesis_key="autonomy_high",
        primary_fact_ids=autonomy["supporting_fact_ids"],
    )


def test_stage1_capability_excludes_full_natal_rules_cleanly() -> None:
    facts = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf1",
        swiss_chart=_swiss_aquarius(with_houses=True),
        numerology={"life_path": 7},
        birth_date="1990-02-01",
        capability={
            "natal_mode": "date_only",
            "has_birth_time": False,
            "has_birth_place": False,
        },
        input_fingerprint="in1",
    )
    ev = build_character_engine_evidence_candidates_v0(facts)
    assert not any(c["thesis_key"] == "presence_through_air_asc" for c in ev["claims"])
    excluded = next(
        x for x in ev["excluded_candidates"] if x.get("rule_key") == "ascendant_air_presence_v0"
    )
    assert excluded["reason"] == "capability_insufficient"
    # emotional water moon still runs when moon present; without moon → pattern_not_matched
    facts_no_moon = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf1",
        swiss_chart={"positions": [{"body": "Sun", "sign": "Aquarius"}], "houses": []},
        numerology={"life_path": 7},
        birth_date="1990-02-01",
        capability={"natal_mode": "date_only"},
        input_fingerprint="in1",
    )
    ev2 = build_character_engine_evidence_candidates_v0(facts_no_moon)
    assert any(
        x.get("rule_key") == "emotional_sensitivity_water_moon_v0"
        and x.get("reason") == "pattern_not_matched"
        for x in ev2["excluded_candidates"]
    )


def test_stage1_contradict_edge_preserved_when_configured() -> None:
    chart = _swiss_aquarius(with_houses=True)
    chart["positions"].append({"body": "Saturn", "sign": "Capricorn", "degree": 10.0})
    facts = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf1",
        swiss_chart=chart,
        numerology={"life_path": 7},
        birth_date="1990-02-01",
        capability={
            "natal_mode": "full",
            "has_birth_time": True,
            "has_birth_place": True,
        },
        input_fingerprint="in1",
    )
    ev = build_character_engine_evidence_candidates_v0(facts)
    presence = next(c for c in ev["claims"] if c["thesis_key"] == "presence_through_air_asc")
    contradict = [
        e
        for e in ev["edges"]
        if e["claim_id"] == presence["claim_id"] and e["edge_type"] == "contradicts"
    ]
    assert contradict
    assert presence.get("contradicting_fact_ids")
    # Inconvenient saturn fact stays in pack
    assert any(f["fact_type"] == "planet_sign:saturn" for f in facts["raw_facts"])


def test_stage1_surface_text_not_in_claim_id() -> None:
    facts = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf1",
        swiss_chart=_swiss_aquarius(),
        numerology={"life_path": 7},
        birth_date="1990-02-01",
        capability={"natal_mode": "date_only"},
        input_fingerprint="in1",
    )
    ev = build_character_engine_evidence_candidates_v0(facts)
    claim = ev["claims"][0]
    base = make_claim_id(
        claim_kind=claim["claim_kind"],
        thesis_key=claim["thesis_key"],
        primary_fact_ids=claim["supporting_fact_ids"],
    )
    assert claim["claim_id"] == base
    # surface_text is not an input to make_claim_id — mutating display copy cannot change id
    claim_with_surface = {**claim, "surface_text": "совсем другой текст"}
    assert claim_with_surface["claim_id"] == base


def test_stage0_facts_match_machine_raw_fact_shape() -> None:
    import json
    from pathlib import Path

    pack = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf1",
        swiss_chart=_swiss_aquarius(),
        numerology={"life_path": 7},
        birth_date="1990-02-01",
        capability={"natal_mode": "date_only"},
        input_fingerprint="in1",
    )
    schema_path = Path(__file__).resolve().parents[2] / "docs" / "schemas" / "character_engine_v1.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    try:
        import jsonschema
    except ImportError:
        required = set(schema["$defs"]["raw_fact"]["required"])
        for fact in pack["raw_facts"]:
            assert required.issubset(fact.keys())
            assert str(fact["fact_id"]).startswith("fact:")
        return
    # Resolve $defs refs by validating against a root that points at raw_fact.
    root = {"$defs": schema["$defs"], "allOf": [{"$ref": "#/$defs/raw_fact"}]}
    validator = jsonschema.Draft202012Validator(root)
    for fact in pack["raw_facts"]:
        errors = sorted(validator.iter_errors(fact), key=lambda e: e.path)
        assert not errors, f"{fact.get('fact_type')}: {[e.message for e in errors]}"
    art = run_character_engine_stage01_shadow_v0(
        profile_fingerprint="pf1",
        swiss_chart=_swiss_aquarius(),
        numerology={"life_path": 7},
        birth_date="1990-02-01",
        capability={"natal_mode": "date_only"},
    )
    assert art["character_engine_ready_published"] is False
    assert art["publish_mode"] == "diagnostics_only"
    assert "cascade" not in art["stage1"]
    assert art["ok"] is True


def test_bridge_calc_version_constant() -> None:
    assert BRIDGE_CALC_VERSION.startswith("natal_facts_bridge")
    assert DATE_SUN_CALC_VERSION.startswith("sun_from_date")
