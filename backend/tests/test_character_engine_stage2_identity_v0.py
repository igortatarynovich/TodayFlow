"""Stage 2 Identity Core — LLM contract validation (structure/provenance only)."""

from __future__ import annotations

from todayflow_backend.services.character_engine_ids_v0 import make_claim_id
from todayflow_backend.services.character_engine_identity_thesis_registry_v0 import (
    normalize_identity_thesis_key,
)
from todayflow_backend.services.character_engine_stage0_facts_v0 import (
    build_character_engine_facts_pack_v0,
)
from todayflow_backend.services.character_engine_stage01_staging_eval_v0 import (
    evaluate_stage01_staging_v0,
)
from todayflow_backend.services.character_engine_stage1_evidence_v0 import (
    build_character_engine_evidence_candidates_v0,
)
from todayflow_backend.services.character_engine_stage2_identity_v0 import (
    build_character_engine_identity_core_v0,
    build_stage2_context_pack,
)
from todayflow_backend.services.character_engine_stage2_shadow_v0 import (
    run_character_engine_stage2_shadow_v0,
)
from todayflow_backend.prompts.registry_v1 import get_prompt


def _aquarius_inputs():
    facts = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf_s2",
        swiss_chart={
            "positions": [
                {"body": "Sun", "sign": "Aquarius", "degree": 12.0},
                {"body": "Moon", "sign": "Pisces", "degree": 3.0},
                {"body": "Mars", "sign": "Aries", "degree": 8.0},
            ],
            "houses": [],
        },
        numerology={"life_path": 7},
        birth_date="1990-02-01",
        capability={"natal_mode": "date_only", "has_name": True},
        input_fingerprint="in_s2",
    )
    evidence = build_character_engine_evidence_candidates_v0(facts)
    return facts, evidence


def test_stage01_staging_eval_gates_pass() -> None:
    report = evaluate_stage01_staging_v0()
    assert report["gate_pass"] is True


def test_stage2_prompt_registered() -> None:
    system, version = get_prompt("profile.character_engine.stage2.v1", locale="ru")
    assert "Identity Core" in system or "ядро личности" in system
    assert version == "1.1.1"


def test_stage2_context_pack_excludes_legacy_roots() -> None:
    facts, evidence = _aquarius_inputs()
    pack = build_stage2_context_pack(facts_pack=facts, evidence=evidence)
    assert "profile_contract_v1" in pack["forbidden_inputs"]
    assert pack["allowed_primary_claim_ids"]
    assert all(c.get("claim_id") for c in pack["claims"])


def test_stage2_grounded_contract_from_llm_json() -> None:
    facts, evidence = _aquarius_inputs()
    primary = next(c for c in evidence["claims"] if c["thesis_key"] == "autonomy_high")
    other_ids = [c["claim_id"] for c in evidence["claims"] if c["claim_id"] != primary["claim_id"]]
    llm_raw = {
        "status": "grounded",
        "identity_core": {
            "primary_claim_id": primary["claim_id"],
            "thesis_key": "autonomy_high",
            "surface_text": "Строит жизнь через собственную систему и независимость.",
            "supporting_claim_ids": [primary["claim_id"], *other_ids[:1]],
            "qualifying_claim_ids": other_ids[1:2],
            "contradicting_claim_ids": [],
            "confidence": "medium",
        },
        "source_roles": [
            {"role": "dominant_mechanism", "claim_id": primary["claim_id"]},
        ],
        "selection_rationale": "autonomy claim dominates with water moon as qualifier",
    }
    identity = build_character_engine_identity_core_v0(
        facts_pack=facts, evidence=evidence, llm_raw=llm_raw
    )
    assert identity["status"] == "grounded"
    core = identity["identity_core"]
    assert core["thesis_key"] == normalize_identity_thesis_key("autonomy_high")
    assert core["primary_claim_id"] == primary["claim_id"]
    assert identity["validation"]["refs_resolve"] is True
    assert identity["validation"]["no_invented_claims"] is True
    assert "scenes" not in identity
    assert "compass" not in identity


def test_stage2_rejects_invented_claim_id() -> None:
    facts, evidence = _aquarius_inputs()
    primary = evidence["claims"][0]
    identity = build_character_engine_identity_core_v0(
        facts_pack=facts,
        evidence=evidence,
        llm_raw={
            "status": "grounded",
            "identity_core": {
                "primary_claim_id": "claim:deadbeefdeadbeefdeadbeef",
                "thesis_key": primary["thesis_key"],
                "surface_text": "x",
                "supporting_claim_ids": [],
                "qualifying_claim_ids": [],
                "contradicting_claim_ids": [],
                "confidence": "low",
            },
            "source_roles": [],
            "selection_rationale": "bad",
        },
    )
    assert identity["status"] == "insufficient_identity_core"
    assert identity["identity_core"] is None
    assert any(e["code"] == "primary_claim_unknown" for e in identity["diagnostics"]["contract_errors"])


def test_stage2_rejects_thesis_mismatch() -> None:
    facts, evidence = _aquarius_inputs()
    primary = next(c for c in evidence["claims"] if c["thesis_key"] == "autonomy_high")
    identity = build_character_engine_identity_core_v0(
        facts_pack=facts,
        evidence=evidence,
        llm_raw={
            "status": "grounded",
            "identity_core": {
                "primary_claim_id": primary["claim_id"],
                "thesis_key": "invented_free_thesis",
                "surface_text": "x",
                "supporting_claim_ids": [primary["claim_id"]],
                "qualifying_claim_ids": [],
                "contradicting_claim_ids": [],
                "confidence": "medium",
            },
            "source_roles": [],
            "selection_rationale": "bad thesis",
        },
    )
    assert identity["status"] == "insufficient_identity_core"
    assert any(e["code"] == "thesis_mismatch_primary" for e in identity["diagnostics"]["contract_errors"])


def test_stage2_surface_change_does_not_change_id() -> None:
    facts, evidence = _aquarius_inputs()
    primary = next(c for c in evidence["claims"] if c["thesis_key"] == "autonomy_high")
    base = {
        "status": "grounded",
        "identity_core": {
            "primary_claim_id": primary["claim_id"],
            "thesis_key": "autonomy_high",
            "surface_text": "Первая формулировка.",
            "supporting_claim_ids": [primary["claim_id"]],
            "qualifying_claim_ids": [],
            "contradicting_claim_ids": [],
            "confidence": "medium",
        },
        "source_roles": [{"role": "dominant_mechanism", "claim_id": primary["claim_id"]}],
        "selection_rationale": "ok",
    }
    a = build_character_engine_identity_core_v0(facts_pack=facts, evidence=evidence, llm_raw=base)
    base2 = {
        **base,
        "identity_core": {**base["identity_core"], "surface_text": "Совсем другая формулировка."},
    }
    b = build_character_engine_identity_core_v0(facts_pack=facts, evidence=evidence, llm_raw=base2)
    assert a["identity_core"]["claim_id"] == b["identity_core"]["claim_id"]
    expected = make_claim_id(
        claim_kind="identity_core",
        thesis_key=a["identity_core"]["thesis_key"],
        primary_fact_ids=a["identity_core"]["supporting_fact_ids"],
    )
    assert a["identity_core"]["claim_id"] == expected


def test_stage2_insufficient_when_no_claims() -> None:
    facts = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf_empty",
        swiss_chart={
            "positions": [
                {"body": "Sun", "sign": "Leo", "degree": 1.0},
                {"body": "Moon", "sign": "Aries", "degree": 2.0},
                {"body": "Mars", "sign": "Virgo", "degree": 3.0},
            ],
            "houses": [],
        },
        numerology={"life_path": 9},
        birth_date="1988-08-15",
        capability={"natal_mode": "date_only"},
        input_fingerprint="in_empty",
    )
    evidence = build_character_engine_evidence_candidates_v0(facts)
    identity = build_character_engine_identity_core_v0(facts_pack=facts, evidence=evidence)
    assert evidence["claims"] == []
    assert identity["status"] == "insufficient_identity_core"
    assert identity["identity_core"] is None


def test_stage2_model_insufficient_accepted() -> None:
    facts, evidence = _aquarius_inputs()
    identity = build_character_engine_identity_core_v0(
        facts_pack=facts,
        evidence=evidence,
        llm_raw={
            "status": "insufficient_identity_core",
            "identity_core": None,
            "source_roles": [],
            "selection_rationale": "evidence too thin for one core",
        },
    )
    assert identity["status"] == "insufficient_identity_core"
    assert identity["validation"]["required_fields_ok"] is True


def test_stage2_shadow_diagnostics_only() -> None:
    art = run_character_engine_stage2_shadow_v0(
        profile_fingerprint="pf_s2",
        swiss_chart={
            "positions": [
                {"body": "Sun", "sign": "Virgo", "degree": 10.0},
                {"body": "Moon", "sign": "Capricorn", "degree": 2.0},
            ],
            "houses": [],
        },
        numerology={"life_path": 4},
        birth_date="1985-09-10",
        capability={"natal_mode": "date_only"},
    )
    assert art["character_engine_ready_published"] is False
    assert art["publish_mode"] == "diagnostics_only"
    # Without LLM in test env → deterministic grounded (or insufficient if no claims)
    assert art["stage2"]["status"] in {"grounded", "insufficient_identity_core"}
    assert "cascade" not in art["stage2"]


def test_stage2_deterministic_fallback_when_llm_missing(monkeypatch) -> None:
    facts, evidence = _aquarius_inputs()
    monkeypatch.setattr(
        "todayflow_backend.services.character_engine_stage2_identity_v0.is_llm_chat_configured",
        lambda: False,
    )
    identity = build_character_engine_identity_core_v0(facts_pack=facts, evidence=evidence)
    assert identity["status"] == "grounded"
    assert identity["identity_core"]["thesis_key"] == "builds_through_autonomy"
    assert "автоном" in identity["identity_core"]["surface_text"].lower()
    assert identity["validation"].get("deterministic_fallback") is True
