"""Profile Information Contract — N=18 gate + K01/K02 occupancy coverage.

SoT: docs/profile/PROFILE_INFORMATION_CONTRACT_V1.md
"""

from __future__ import annotations

from pathlib import Path

from todayflow_backend.knowledge.il2_composition_v1 import (
    compose_planet_in_house,
    compose_planet_in_sign,
    load_objects,
)
from todayflow_backend.services.character_engine_identity_thesis_registry_v0 import (
    STAGE1_TO_IDENTITY_THESIS,
)
from todayflow_backend.services.character_engine_stage0_facts_v0 import (
    build_character_engine_facts_pack_v0,
)
from todayflow_backend.services.character_engine_stage1_evidence_v0 import (
    PIC_F as STAGE1_PIC_F,
)
from todayflow_backend.services.character_engine_stage1_evidence_v0 import (
    PIC_K as STAGE1_PIC_K,
)
from todayflow_backend.services.character_engine_stage1_evidence_v0 import (
    build_character_engine_evidence_candidates_v0,
)
from todayflow_backend.services.character_engine_stage2_identity_v0 import (
    PIC_F as STAGE2_PIC_F,
)
from todayflow_backend.services.character_engine_stage2_identity_v0 import (
    PIC_K as STAGE2_PIC_K,
)
from todayflow_backend.services.character_engine_stage2_identity_v0 import (
    build_character_engine_identity_core_v0,
)
from todayflow_backend.services.character_engine_profile_consumption_v0 import (
    apply_character_engine_profile_consumption_v0,
)
from todayflow_backend.services.profile_information_contract_v1 import (
    COVERAGE_STATUSES,
    KNOWLEDGE_TO_SLOT,
    PIC_COVERAGE,
    PIC_KNOWLEDGE_IDS,
    PROFILE_MEANING_PRODUCERS,
)

CE_ROOT = Path(__file__).resolve().parents[1] / "src" / "todayflow_backend" / "services"

CAPABILITY = {
    "natal_mode": "full",
    "has_name": True,
    "has_birth_time": True,
    "has_birth_place": True,
}

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
    roles = {
        str(row.get("claim_id")): str(row.get("role"))
        for row in (identity.get("source_roles") or [])
        if isinstance(row, dict)
    }
    occupancy = [
        c
        for c in (evidence.get("claims") or [])
        if isinstance(c, dict)
        and str(c.get("thesis_key") or "").startswith(("planet_in_sign:mars:", "planet_in_house:mars:"))
    ]
    return {
        "id": case["id"],
        "mars_fact_sign": (mars_value or {}).get("sign") if isinstance(mars_value, dict) else None,
        "mars_fact_house": (mars_value or {}).get("house") if isinstance(mars_value, dict) else None,
        "stage1_thesis_keys": sorted(claims),
        "identity_thesis": core.get("thesis_key"),
        "identity_surface": core.get("surface_text"),
        "qualifying_claim_ids": list(core.get("qualifying_claim_ids") or []),
        "occupancy_roles": [
            roles.get(str(c.get("claim_id")))
            for c in occupancy
            if str(c.get("claim_id")) in roles
        ],
        "deterministic": bool((identity.get("validation") or {}).get("deterministic_fallback")),
    }


def test_pic_n18_is_closed() -> None:
    assert PIC_KNOWLEDGE_IDS == tuple(f"K{i:02d}" for i in range(1, 19))
    assert len(set(PIC_KNOWLEDGE_IDS)) == 18
    for row in PROFILE_MEANING_PRODUCERS:
        for kid in row["pic_k"]:  # type: ignore[index]
            assert kid in PIC_KNOWLEDGE_IDS
    assert KNOWLEDGE_TO_SLOT["K13"] == ("P2.name_numerology",)
    assert KNOWLEDGE_TO_SLOT["K14"] == ("P2.correspondence",)


def test_pic_coverage_audit_covers_n18() -> None:
    assert len(PIC_COVERAGE) == 18
    assert tuple(row["pic_k"] for row in PIC_COVERAGE) == PIC_KNOWLEDGE_IDS
    for row in PIC_COVERAGE:
        assert row["status"] in COVERAGE_STATUSES
    by_id = {str(row["pic_k"]): row for row in PIC_COVERAGE}
    assert by_id["K02"]["status"] == "COMPLETE"
    assert by_id["K08"]["status"] == "COMPLETE"
    assert by_id["K11"]["status"] == "COMPLETE"
    assert by_id["K12"]["status"] == "COMPLETE"
    assert by_id["K13"]["status"] == "COMPLETE"
    assert by_id["K14"]["status"] == "COMPLETE"
    assert by_id["K17"]["status"] == "COMPLETE"
    assert by_id["K18"]["status"] == "COMPLETE"
    assert by_id["K05"]["status"] == "COMPLETE"
    assert by_id["K04"]["status"] == "COMPLETE"
    assert by_id["K09"]["status"] == "COMPLETE"
    assert by_id["K07"]["status"] == "COMPLETE"
    assert by_id["K06"]["status"] == "MISSING"


def test_pic_gate_meaning_producers_cite_k_and_f() -> None:
    assert STAGE1_PIC_K == ("K01", "K02", "K05")
    assert STAGE1_PIC_F == ("F03", "F06", "F07")
    assert STAGE2_PIC_K == ("K01", "K02")
    assert STAGE2_PIC_F == ("F03", "F06")
    registered = {str(row["module"]) for row in PROFILE_MEANING_PRODUCERS}
    for row in PROFILE_MEANING_PRODUCERS:
        module = str(row["module"])
        kids = tuple(row["pic_k"])  # type: ignore[arg-type]
        fids = tuple(row["pic_f"])  # type: ignore[arg-type]
        assert kids, module
        assert fids, module
        for kid in kids:
            assert kid in PIC_KNOWLEDGE_IDS
        path = CE_ROOT / f"{module}.py"
        text = path.read_text(encoding="utf-8")
        assert "PIC_K =" in text, module
        assert "PIC_F =" in text, module
        assert module in registered
    for path in sorted(CE_ROOT.glob("character_engine_stage[1-5]_*.py")):
        if path.name.endswith("_shadow_v0.py") or "staging_eval" in path.name:
            continue
        assert path.stem in registered, path.name
        text = path.read_text(encoding="utf-8")
        assert "PIC_K =" in text, path.name
        assert "PIC_F =" in text, path.name


def test_ce_may_import_il2_compose_only() -> None:
    forbidden = (
        "todayflow_backend.knowledge.il3_interpretation",
        "todayflow_backend.knowledge.il4_expression",
        "todayflow_backend.knowledge.calc_il_wire",
    )
    offenders: list[str] = []
    for path in sorted(CE_ROOT.glob("character_engine_*.py")):
        text = path.read_text(encoding="utf-8")
        if any(token in text for token in forbidden):
            offenders.append(path.name)
    assert offenders == []
    stage1 = (CE_ROOT / "character_engine_stage1_evidence_v0.py").read_text(encoding="utf-8")
    assert "compose_planet_in_sign" in stage1
    assert "compose_planet_in_house" in stage1
    assert "compose_aspect_pair" in stage1


def test_il2_atoms_exist_for_mars_sign_and_house() -> None:
    catalog = load_objects()
    sign_a = compose_planet_in_sign(catalog, "astro.object.mars", "astro.sign.cancer")
    house_a = compose_planet_in_house(catalog, "astro.object.mars", "astro.house.04")
    sign_b = compose_planet_in_sign(catalog, "astro.object.mars", "astro.sign.libra")
    house_b = compose_planet_in_house(catalog, "astro.object.mars", "astro.house.07")
    assert sign_a.status == "composed"
    assert house_a.status == "composed"
    assert sign_b.status == "composed"
    assert house_b.status == "composed"
    assert sign_a.jobs["how"].lemmas != sign_b.jobs["how"].lemmas
    assert house_a.jobs["where"].lemmas != house_b.jobs["where"].lemmas


def test_ce_stage0_keeps_mars_sign_and_house_value() -> None:
    hop_a = _ce_hop(CHART_A)
    hop_b = _ce_hop(CHART_B)
    assert hop_a["mars_fact_sign"] == "cancer"
    assert hop_a["mars_fact_house"] == 4
    assert hop_b["mars_fact_sign"] == "libra"
    assert hop_b["mars_fact_house"] == 7


def test_k01_k02_preserve_f03_f06_mars_occupancy() -> None:
    hop_a = _ce_hop(CHART_A)
    hop_b = _ce_hop(CHART_B)
    keys_a = " ".join(hop_a["stage1_thesis_keys"])
    keys_b = " ".join(hop_b["stage1_thesis_keys"])
    assert "planet_in_sign:mars:cancer" in hop_a["stage1_thesis_keys"]
    assert "planet_in_house:mars:04" in hop_a["stage1_thesis_keys"]
    assert "planet_in_sign:mars:libra" in hop_b["stage1_thesis_keys"]
    assert "planet_in_house:mars:07" in hop_b["stage1_thesis_keys"]
    assert hop_a["stage1_thesis_keys"] != hop_b["stage1_thesis_keys"]
    assert hop_a["identity_surface"] != hop_b["identity_surface"]
    assert hop_a["identity_thesis"] == hop_b["identity_thesis"] == "builds_through_analysis"
    assert hop_a["qualifying_claim_ids"]
    assert hop_b["qualifying_claim_ids"]
    assert hop_a["occupancy_roles"]
    assert hop_b["occupancy_roles"]
    assert all(role == "qualifier" for role in hop_a["occupancy_roles"])
    assert all(role == "qualifier" for role in hop_b["occupancy_roles"])
    surface_a = hop_a["identity_surface"] or ""
    surface_b = hop_b["identity_surface"] or ""
    assert "holding" in surface_a or "home" in surface_a
    assert "close" in surface_a
    assert "balancing" in surface_b or "partnership" in surface_b
    assert keys_a != keys_b
    assert hop_a["deterministic"] is True
    registry = set(STAGE1_TO_IDENTITY_THESIS)
    assert set(hop_a["stage1_thesis_keys"]) & registry
    assert set(hop_b["stage1_thesis_keys"]) & registry


def test_k05_f07_aspect_pair_wires_to_insight(monkeypatch) -> None:
    monkeypatch.setattr(
        "todayflow_backend.services.character_engine_profile_consumption_v0.settings",
        type("S", (), {"character_engine_profile_consumption": True})(),
    )
    facts = build_character_engine_facts_pack_v0(
        profile_fingerprint="k05_e2e",
        swiss_chart={
            "positions": [
                {"body": "Sun", "sign": "Virgo", "degree": 15.0, "longitude": 165.0},
                {"body": "Mars", "sign": "Aries", "degree": 0.0, "longitude": 0.0},
                {"body": "Saturn", "sign": "Cancer", "degree": 0.0, "longitude": 90.0},
            ],
            "houses": [],
        },
        numerology={"life_path": 7},
        capability={"natal_mode": "date_only", "has_name": True},
        birth_date="1991-09-08",
        input_fingerprint="k05_e2e",
    )
    evidence = build_character_engine_evidence_candidates_v0(facts)
    identity = build_character_engine_identity_core_v0(
        facts_pack=facts,
        evidence=evidence,
        deterministic_only=True,
    )
    tensions = [
        c
        for c in (evidence.get("claims") or [])
        if isinstance(c, dict)
        and c.get("claim_kind") == "tension"
        and str(c.get("thesis_key") or "").startswith("aspect_pair:")
    ]
    assert len(tensions) == 1
    payload = {
        "diagnostics": {
            "character_engine_stage2": {
                "stage0": facts,
                "stage1": evidence,
                "stage2": identity,
            }
        },
        "profile_contract_v1": {},
        "numerology": {"life_path": 7},
        "portrait_why_v0": {
            "selected_by": [],
            "portrait_influenced_by": [
                {"id": "sun", "class": "portrait_influenced_by", "label": "Солнце в Деве"}
            ],
        },
    }
    out = apply_character_engine_profile_consumption_v0(payload)
    insight = out["insight_nodes_v0"]["nodes"][0]["insight"]
    assert "↔" in insight
    assert "act" in insight
    assert "limit" in insight
    assert "дистанцию" not in insight
    assert out["character_engine_consumption_v0"]["insight_source"] == "stage1_aspect_pair"
    why = out["portrait_why_v0"]
    assert [str(r.get("id")) for r in why.get("selected_by") or []] == ["life_path"]
    hop_a = _ce_hop(CHART_A)
    omit_tensions = [k for k in hop_a["stage1_thesis_keys"] if k.startswith("aspect_pair:")]
    assert omit_tensions == []


CHART_FIRE = {
    "id": "aries_fire_stack",
    "mars_sign": "Leo",
    "mars_house": 5,
    "chart": {
        "positions": [
            {"body": "Sun", "sign": "Aries", "degree": 10.0, "longitude": 10.0, "house": 5},
            {"body": "Moon", "sign": "Leo", "degree": 8.0, "longitude": 128.0, "house": 5},
            {"body": "Mercury", "sign": "Aries", "degree": 4.0, "longitude": 4.0, "house": 5},
            {"body": "Mars", "sign": "Leo", "degree": 20.0, "longitude": 140.0, "house": 5},
            {"body": "Ascendant", "sign": "Gemini", "degree": 2.0, "longitude": 62.0},
            {"body": "rising", "sign": "Gemini", "degree": 2.0, "longitude": 62.0},
        ],
        "houses": {f"house_{i}": {"longitude": (62.0 + (i - 1) * 30.0) % 360.0} for i in range(1, 13)},
    },
}


def _consume_chart(case: dict, monkeypatch) -> dict:
    monkeypatch.setattr(
        "todayflow_backend.services.character_engine_profile_consumption_v0.settings",
        type("S", (), {"character_engine_profile_consumption": True})(),
    )
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
    payload = {
        "diagnostics": {
            "character_engine_stage2": {
                "stage0": facts,
                "stage1": evidence,
                "stage2": identity,
            }
        },
        "profile_contract_v1": {},
        "numerology": {"life_path": 7},
        "portrait_why_v0": {
            "selected_by": [],
            "portrait_influenced_by": [
                {"id": "sun", "class": "portrait_influenced_by", "label": "Солнце"}
            ],
        },
    }
    return apply_character_engine_profile_consumption_v0(payload)


def test_k04_one_internal_engine_axis_from_f08(monkeypatch) -> None:
    earth = _consume_chart(CHART_A, monkeypatch)
    fire = _consume_chart(CHART_FIRE, monkeypatch)
    earth_help = earth["insight_nodes_v0"]["nodes"][0]["help"]
    fire_help = fire["insight_nodes_v0"]["nodes"][0]["help"]
    assert earth_help
    assert fire_help
    assert earth_help != fire_help
    assert "slow-and-steady" in earth_help or "steadfast" in earth_help or "patient" in earth_help
    assert "central" in fire_help or "warm" in fire_help or "displayed" in fire_help
    assert "дистанцию" not in earth_help
    assert "дистанцию" not in fire_help
    assert earth["character_engine_consumption_v0"]["help_source"] == "stage0_element_balance"
    assert fire["character_engine_consumption_v0"]["help_source"] == "stage0_element_balance"
    assert isinstance(earth_help, str)
    assert "perception" not in earth_help
    assert "burnout" not in earth_help
    earth_facts = earth["diagnostics"]["character_engine_stage2"]["stage0"]["raw_facts"]
    balance = next(row for row in earth_facts if row.get("fact_type") == "element_balance")
    assert balance["value"]["dominant_element"] == "earth"
    assert not isinstance(earth["insight_nodes_v0"]["nodes"][0].get("help"), list)


CHART_K09 = {
    "id": "earth_tilt_mars_saturn_square",
    "chart": {
        "positions": [
            {"body": "Sun", "sign": "Virgo", "degree": 15.0, "longitude": 165.0},
            {"body": "Moon", "sign": "Taurus", "degree": 10.0, "longitude": 40.0},
            {"body": "Mercury", "sign": "Virgo", "degree": 4.0, "longitude": 154.0},
            {"body": "Mars", "sign": "Aries", "degree": 0.0, "longitude": 0.0},
            {"body": "Saturn", "sign": "Cancer", "degree": 0.0, "longitude": 90.0},
        ],
        "houses": [],
    },
}


def test_k09_honest_cost_fill_empty_from_k04_k05(monkeypatch) -> None:
    out = _consume_chart(CHART_K09, monkeypatch)
    node = out["insight_nodes_v0"]["nodes"][0]
    insight = node["insight"]
    help_line = node["help"]
    cons = out["character_engine_consumption_v0"]
    assert "↔" in insight
    assert "act" in insight
    assert "limit" in insight
    assert "immovable" in insight or "over-holding" in insight
    assert cons["insight_source"] == "stage1_aspect_pair"
    assert cons["help_source"] == "stage0_element_balance"
    assert cons["cost_source"] == "sign_excess_of_k04_axis"
    assert "slow-and-steady" in help_line or "steadfast" in help_line or "patient" in help_line
    assert "immovable" not in help_line
    assert "over-holding" not in help_line
    assert "дистанцию" not in insight
    assert "дистанцию" not in help_line
    earth_only = _consume_chart(CHART_A, monkeypatch)
    assert earth_only["character_engine_consumption_v0"]["cost_source"] == "omitted_no_grounded_honest_cost"
    assert "immovable" not in (earth_only["insight_nodes_v0"]["nodes"][0].get("help") or "")


def test_k07_path_spheres_from_f06_house_arena(monkeypatch) -> None:
    home = _consume_chart(CHART_A, monkeypatch)
    pair = _consume_chart(CHART_B, monkeypatch)
    date_only = _consume_chart(CHART_K09, monkeypatch)
    fire = _consume_chart(CHART_FIRE, monkeypatch)
    home_spheres = home["profile_contract_v1"].get("life_spheres") or {}
    pair_spheres = pair["profile_contract_v1"].get("life_spheres") or {}
    fire_spheres = fire["profile_contract_v1"].get("life_spheres") or {}
    assert home["character_engine_consumption_v0"]["sphere_source"] == "f06_house_arena"
    assert pair["character_engine_consumption_v0"]["sphere_source"] == "f06_house_arena"
    assert date_only["character_engine_consumption_v0"]["sphere_source"] == "omitted_no_grounded_f06"
    assert date_only["profile_contract_v1"].get("life_spheres") in ({}, None)
    assert len(home_spheres) <= 2
    assert len(pair_spheres) <= 2
    assert set(home_spheres) != set(pair_spheres)
    assert "family" in home_spheres
    assert "love" in pair_spheres
    assert "home" in (home_spheres["family"].get("need") or "") or "family" in (
        home_spheres["family"].get("need") or ""
    )
    assert "partnership" in (pair_spheres["love"].get("need") or "")
    assert "ясность своего контура" not in str(home_spheres)
    assert "ясность своего контура" not in str(pair_spheres)
    assert "дистанцию" not in str(home_spheres)
    home_help = home["insight_nodes_v0"]["nodes"][0]["help"]
    pair_help = pair["insight_nodes_v0"]["nodes"][0]["help"]
    assert home["character_engine_consumption_v0"]["help_source"] == "stage0_element_balance"
    assert pair["character_engine_consumption_v0"]["help_source"] == "stage0_element_balance"
    assert home_help == pair_help
    for row in home_spheres.values():
        assert home_help not in (row.get("how") or "")
        assert home_help not in (row.get("need") or "")
    assert "love" in fire_spheres
    assert len(fire_spheres) <= 2
    houses = (home.get("character_engine_house_lines_v0") or {}).get("houses") or {}
    assert "1" in houses
    assert houses["1"].get("how")
