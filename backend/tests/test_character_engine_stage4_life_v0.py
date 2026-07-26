"""Stage 4 life_bundle — expand-only contract validation."""

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
)
from todayflow_backend.services.character_engine_stage4_life_v0 import (
    SCENE_KINDS,
    build_character_engine_life_bundle_v0,
)
from todayflow_backend.services.character_engine_stage4_shadow_v0 import (
    run_character_engine_stage4_shadow_v0,
)
from todayflow_backend.services.character_engine_profile_consumption_v0 import (
    apply_character_engine_profile_consumption_v0,
)


def _aquarius_prereqs():
    facts = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf_s4",
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
        input_fingerprint="in_s4",
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
            "source_roles": [{"role": "dominant_mechanism", "claim_id": primary["claim_id"]}],
            "selection_rationale": "test_fixture",
        },
    )
    claim_id = identity["identity_core"]["primary_claim_id"]
    thesis = identity["identity_core"]["thesis_key"]
    engine = {
        slot: {
            "surface_text": f"Проявление ядра в зоне {slot} — тест.",
            "expansion_because": f"Это проявление {thesis}, потому что тест.",
            "supporting_claim_ids": [claim_id],
        }
        for slot in ENGINE_SLOTS
    }
    stage3 = build_character_engine_internal_engine_v0(
        facts_pack=facts,
        evidence=evidence,
        identity=identity,
        llm_raw={
            "status": "grounded",
            "identity_thesis_echo": thesis,
            "internal_engine": engine,
            "primary_tension": {
                "thesis_key": "autonomy_vs_contact",
                "surface_text": "Пока ты держишь дистанцию, жизнь не двигается.",
                "expansion_because": f"Это проявление {thesis}, потому что ловушка того же ядра.",
                "supporting_claim_ids": [claim_id],
            },
            "secondary_tensions": [],
            "selection_rationale": "test",
        },
    )
    return facts, evidence, identity, stage3


def _grounded_life_raw(identity: dict, stage3: dict) -> dict:
    thesis = identity["identity_core"]["thesis_key"]
    claim_id = identity["identity_core"]["primary_claim_id"]
    return {
        "status": "grounded",
        "identity_thesis_echo": thesis,
        "scenes": [
            {
                "scene_kind": "intimacy",
                "surface_text": "В близости Stage4 intimacy — тест.",
                "expansion_because": f"Это проявление {thesis}, потому что intimacy.",
                "supporting_claim_ids": [claim_id],
                "rooted_in": "primary_tension",
            },
            {
                "scene_kind": "responsibility",
                "surface_text": "В ответственности Stage4 — тест.",
                "expansion_because": f"Это проявление {thesis}, потому что duty.",
                "supporting_claim_ids": [claim_id],
                "rooted_in": "decision",
            },
            {
                "scene_kind": "risk",
                "surface_text": "Риск Stage4 money proxy — тест.",
                "expansion_because": f"Это проявление {thesis}, потому что risk.",
                "supporting_claim_ids": [claim_id],
                "rooted_in": "risk",
            },
        ],
        "potential": {
            "surface_text": "Потенциал Stage4 — тест.",
            "expansion_because": f"Это проявление {thesis}, потому что growth.",
            "supporting_claim_ids": [claim_id],
        },
        "blind_spots": [
            {
                "surface_text": "Слепое пятно Stage4 — тест.",
                "expansion_because": f"Это проявление {thesis}, потому что blind.",
                "supporting_claim_ids": [claim_id],
            }
        ],
        "selection_rationale": "test",
    }


def test_stage4_prompt_registered() -> None:
    system, version = get_prompt("profile.character_engine.stage4.v1", locale="ru")
    assert "scene_kind" in system or "scenes" in system.lower()
    assert version == "1.0.0"
    assert "intimacy" in system


def test_stage4_grounded_expand_only() -> None:
    facts, evidence, identity, stage3 = _aquarius_prereqs()
    out = build_character_engine_life_bundle_v0(
        facts_pack=facts,
        evidence=evidence,
        identity=identity,
        stage3=stage3,
        llm_raw=_grounded_life_raw(identity, stage3),
    )
    assert out["status"] == "grounded"
    assert len(out["scenes"]) >= 1
    assert all(s["scene_kind"] in SCENE_KINDS for s in out["scenes"])
    assert all(s.get("scene_id") for s in out["scenes"])
    assert out["potential"]["surface_text"].startswith("Потенциал")
    assert out["validation"]["expand_only"] is True


def test_stage4_rejects_identity_rewrite() -> None:
    facts, evidence, identity, stage3 = _aquarius_prereqs()
    raw = _grounded_life_raw(identity, stage3)
    raw["identity_thesis_echo"] = "builds_through_earth_stability"
    out = build_character_engine_life_bundle_v0(
        facts_pack=facts,
        evidence=evidence,
        identity=identity,
        stage3=stage3,
        llm_raw=raw,
    )
    assert out["status"] == "insufficient_life_bundle"
    codes = [e.get("code") for e in (out.get("diagnostics") or {}).get("contract_errors") or []]
    assert "identity_thesis_rewrite_forbidden" in codes


def test_stage4_rejects_invalid_scene_kind() -> None:
    facts, evidence, identity, stage3 = _aquarius_prereqs()
    raw = _grounded_life_raw(identity, stage3)
    raw["scenes"][0]["scene_kind"] = "career"
    out = build_character_engine_life_bundle_v0(
        facts_pack=facts,
        evidence=evidence,
        identity=identity,
        stage3=stage3,
        llm_raw=raw,
    )
    assert out["status"] == "insufficient_life_bundle"


def test_stage4_deterministic_fallback(monkeypatch) -> None:
    facts, evidence, identity, stage3 = _aquarius_prereqs()
    monkeypatch.setattr(
        "todayflow_backend.services.character_engine_stage4_life_v0.is_llm_chat_configured",
        lambda: False,
    )
    out = build_character_engine_life_bundle_v0(
        facts_pack=facts, evidence=evidence, identity=identity, stage3=stage3
    )
    assert out["status"] == "grounded"
    assert out["validation"].get("deterministic_fallback") is True
    assert out["scenes"]


def test_stage4_shadow_diagnostics_only(monkeypatch) -> None:
    monkeypatch.setattr(
        "todayflow_backend.services.character_engine_stage2_identity_v0.is_llm_chat_configured",
        lambda: False,
    )
    monkeypatch.setattr(
        "todayflow_backend.services.character_engine_stage3_internal_v0.is_llm_chat_configured",
        lambda: False,
    )
    monkeypatch.setattr(
        "todayflow_backend.services.character_engine_stage4_life_v0.is_llm_chat_configured",
        lambda: False,
    )
    art = run_character_engine_stage4_shadow_v0(
        profile_fingerprint="pf_s4",
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
    assert art["stage4"]["status"] in {"grounded", "insufficient_life_bundle"}


def test_consumption_prefers_stage4_scenes(monkeypatch) -> None:
    monkeypatch.setattr(
        "todayflow_backend.services.character_engine_profile_consumption_v0."
        "character_engine_profile_consumption_enabled",
        lambda: True,
    )
    facts, evidence, identity, stage3 = _aquarius_prereqs()
    stage4 = build_character_engine_life_bundle_v0(
        facts_pack=facts,
        evidence=evidence,
        identity=identity,
        stage3=stage3,
        llm_raw=_grounded_life_raw(identity, stage3),
    )
    payload = {
        "diagnostics": {
            "character_engine_stage2": {
                "stage0": facts,
                "stage1": evidence,
                "stage2": identity,
            },
            "character_engine_stage3": {"stage3": stage3},
            "character_engine_stage4": {"stage4": stage4},
        },
        "profile_contract_v1": {},
    }
    out = apply_character_engine_profile_consumption_v0(payload)
    cons = out["character_engine_consumption_v0"]
    assert cons["applied"] is True
    assert cons["relationship_source"] == "stage4_scene.intimacy"
    assert cons["money_source"] == "stage4_scene.resource_proxy"
    assert cons["growth_source"] == "stage4_potential"
    assert "Stage4 intimacy" in out["profile_contract_v1"]["relationship_style"]
    assert "Потенциал Stage4" in out["profile_contract_v1"]["growth_zones"][0]
