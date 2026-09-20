"""Stage 3 Internal Engine — expand-only contract validation."""

from __future__ import annotations

from todayflow_backend.prompts.registry_v1 import get_prompt
from todayflow_backend.services.character_engine_stage0_facts_v0 import (
    build_character_engine_facts_pack_v0,
)
from todayflow_backend.services.character_engine_stage1_evidence_v0 import (
    build_character_engine_evidence_candidates_v0,
)
from todayflow_backend.services.character_engine_stage2_identity_v0 import (
    build_character_engine_identity_core_v0,
)
from todayflow_backend.services.character_engine_stage3_internal_v0 import (
    ENGINE_SLOTS,
    build_character_engine_internal_engine_v0,
    honest_cost_from_axis_v0,
)
from todayflow_backend.services.character_engine_stage3_shadow_v0 import (
    run_character_engine_stage3_shadow_v0,
)
from todayflow_backend.services.character_engine_profile_consumption_v0 import (
    apply_character_engine_profile_consumption_v0,
)


def _aquarius_stage2():
    facts = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf_s3",
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
        input_fingerprint="in_s3",
    )
    evidence = build_character_engine_evidence_candidates_v0(facts)
    primary = next(c for c in evidence["claims"] if c["thesis_key"] == "autonomy_high")
    other_ids = [c["claim_id"] for c in evidence["claims"] if c["claim_id"] != primary["claim_id"]]
    identity = build_character_engine_identity_core_v0(
        facts_pack=facts,
        evidence=evidence,
        llm_raw={
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
            "selection_rationale": "test_fixture",
        },
    )
    return facts, evidence, identity


def _grounded_llm_raw(identity: dict, evidence: dict) -> dict:
    thesis = identity["identity_core"]["thesis_key"]
    claim_id = identity["identity_core"]["primary_claim_id"]
    engine = {
        slot: {
            "surface_text": f"Проявление ядра в зоне {slot} — тест.",
            "expansion_because": f"Это проявление {thesis}, потому что тест.",
            "supporting_claim_ids": [claim_id],
        }
        for slot in ENGINE_SLOTS
    }
    return {
        "status": "grounded",
        "identity_thesis_echo": thesis,
        "internal_engine": engine,
        "primary_tension": {
            "thesis_key": "autonomy_vs_contact",
            "surface_text": "Пока ты держишь дистанцию, жизнь не двигается — Stage3 trap.",
            "expansion_because": f"Это проявление {thesis}, потому что ловушка того же ядра.",
            "supporting_claim_ids": [claim_id],
        },
        "secondary_tensions": [],
        "selection_rationale": "test",
    }


def test_stage3_prompt_registered() -> None:
    system, version = get_prompt("profile.character_engine.stage3.v1", locale="ru")
    assert "Identity Core" in system or "ядро" in system.lower()
    assert "нельзя" in system.lower() or "Never" in system
    assert version == "1.0.1"


def test_stage3_grounded_expand_only() -> None:
    facts, evidence, identity = _aquarius_stage2()
    assert identity["status"] == "grounded"
    out = build_character_engine_internal_engine_v0(
        facts_pack=facts,
        evidence=evidence,
        identity=identity,
        llm_raw=_grounded_llm_raw(identity, evidence),
    )
    assert out["status"] == "grounded"
    assert out["identity_thesis"] == identity["identity_core"]["thesis_key"]
    assert set(out["internal_engine"].keys()) == set(ENGINE_SLOTS)
    assert out["primary_tension"]["surface_text"].startswith("Пока ты держишь")
    assert out["validation"]["no_core_rewrite"] is True
    assert out["validation"]["expand_only"] is True


def test_stage3_rejects_identity_rewrite() -> None:
    facts, evidence, identity = _aquarius_stage2()
    raw = _grounded_llm_raw(identity, evidence)
    # Distinct from autonomy core — must never pass as echo.
    raw["identity_thesis_echo"] = "builds_through_earth_stability"
    out = build_character_engine_internal_engine_v0(
        facts_pack=facts,
        evidence=evidence,
        identity=identity,
        llm_raw=raw,
    )
    assert out["status"] == "insufficient_internal_engine"
    codes = [e.get("code") for e in (out.get("diagnostics") or {}).get("contract_errors") or []]
    assert "identity_thesis_rewrite_forbidden" in codes


def test_stage3_rejects_unknown_claim() -> None:
    facts, evidence, identity = _aquarius_stage2()
    raw = _grounded_llm_raw(identity, evidence)
    raw["primary_tension"]["supporting_claim_ids"] = ["claim:deadbeefdeadbeefdeadbeef"]
    out = build_character_engine_internal_engine_v0(
        facts_pack=facts,
        evidence=evidence,
        identity=identity,
        llm_raw=raw,
    )
    assert out["status"] == "insufficient_internal_engine"


def test_stage3_deterministic_fallback(monkeypatch) -> None:
    facts, evidence, identity = _aquarius_stage2()
    monkeypatch.setattr(
        "todayflow_backend.services.character_engine_stage3_internal_v0.is_llm_chat_configured",
        lambda: False,
    )
    out = build_character_engine_internal_engine_v0(
        facts_pack=facts, evidence=evidence, identity=identity
    )
    assert out["status"] == "grounded"
    assert out["validation"].get("deterministic_fallback") is True
    assert out["primary_tension"]["surface_text"]
    assert out["identity_thesis"] == identity["identity_core"]["thesis_key"]


def test_stage3_shadow_diagnostics_only(monkeypatch) -> None:
    monkeypatch.setattr(
        "todayflow_backend.services.character_engine_stage2_identity_v0.is_llm_chat_configured",
        lambda: False,
    )
    monkeypatch.setattr(
        "todayflow_backend.services.character_engine_stage3_internal_v0.is_llm_chat_configured",
        lambda: False,
    )
    art = run_character_engine_stage3_shadow_v0(
        profile_fingerprint="pf_s3",
        swiss_chart={
            "positions": [
                {"body": "Sun", "sign": "Aquarius", "degree": 12.0},
                {"body": "Moon", "sign": "Pisces", "degree": 3.0},
            ],
            "houses": [],
        },
        numerology={"life_path": 7},
        birth_date="1990-02-01",
        capability={"natal_mode": "date_only"},
    )
    assert art["character_engine_ready_published"] is False
    assert art["publish_mode"] == "diagnostics_only"
    assert art["stage3"]["status"] in {"grounded", "insufficient_internal_engine"}


def test_consumption_prefers_stage3_trap_and_decision(monkeypatch) -> None:
    monkeypatch.setattr(
        "todayflow_backend.services.character_engine_profile_consumption_v0."
        "character_engine_profile_consumption_enabled",
        lambda: True,
    )
    facts, evidence, identity = _aquarius_stage2()
    stage3 = build_character_engine_internal_engine_v0(
        facts_pack=facts,
        evidence=evidence,
        identity=identity,
        llm_raw=_grounded_llm_raw(identity, evidence),
    )
    payload = {
        "diagnostics": {
            "character_engine_stage2": {
                "stage0": facts,
                "stage1": evidence,
                "stage2": identity,
            },
            "character_engine_stage3": {"stage3": stage3},
        },
        "profile_contract_v1": {},
    }
    out = apply_character_engine_profile_consumption_v0(payload)
    cons = out["character_engine_consumption_v0"]
    assert cons["applied"] is True
    assert cons["insight_source"] == "omitted_no_grounded_aspect_tension"
    assert cons["decision_source"] == "stage3_internal_engine.decision"
    assert out["insight_nodes_v0"]["nodes"][0]["insight"] == ""
    assert "Stage3 trap" not in (out["insight_nodes_v0"]["nodes"][0].get("insight") or "")
    assert "зоне decision" in out["profile_contract_v1"]["decision_style"]


def test_stage3_path_axis_from_f08_not_identity_widgets() -> None:
    earth = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf_k04",
        swiss_chart={
            "positions": [
                {"body": "Sun", "sign": "Virgo", "degree": 15.0, "longitude": 165.0},
                {"body": "Moon", "sign": "Taurus", "degree": 10.0, "longitude": 40.0},
                {"body": "Mercury", "sign": "Virgo", "degree": 4.0, "longitude": 154.0},
                {"body": "Mars", "sign": "Cancer", "degree": 12.0, "longitude": 102.0},
            ],
            "houses": [],
        },
        numerology={"life_path": 7},
        capability={"natal_mode": "date_only", "has_name": True},
        birth_date="1991-09-08",
        input_fingerprint="in_k04",
    )
    evidence = build_character_engine_evidence_candidates_v0(earth)
    identity = build_character_engine_identity_core_v0(
        facts_pack=earth,
        evidence=evidence,
        deterministic_only=True,
    )
    out = build_character_engine_internal_engine_v0(
        facts_pack=earth,
        evidence=evidence,
        identity=identity,
        deterministic_only=True,
    )
    assert out["status"] == "grounded"
    assert set(out["internal_engine"].keys()) == set(ENGINE_SLOTS)
    axis = out["path_axis"]
    assert isinstance(axis, dict)
    assert axis["source"] == "stage0_element_balance"
    assert axis["thesis_key"] == "element_balance:earth"
    assert axis["sign"] == "taurus"
    assert axis["body"] == "moon"
    assert "slow-and-steady" in axis["surface_text"] or "steadfast" in axis["surface_text"]
    assert axis["slot"] == "decision"
    cost = honest_cost_from_axis_v0(
        axis=axis,
        insight="act ↔ limit — friction.",
        help_line=str(axis["surface_text"]),
    )
    assert cost is not None
    assert "immovable" in cost["surface_text"] or "over-holding" in cost["surface_text"]
    assert honest_cost_from_axis_v0(axis=axis, insight="", help_line=str(axis["surface_text"])) is None
    assert honest_cost_from_axis_v0(axis=axis, insight="act ↔ limit — friction.", help_line="") is None
    harmonic = {
        "source": "stage0_harmonic_aspect",
        "surface_text": "act / expand — easy-flow.",
        "sign": "",
    }
    assert honest_cost_from_axis_v0(
        axis=harmonic,
        insight="act ↔ limit — friction.",
        help_line="act / expand — easy-flow.",
    ) is None
