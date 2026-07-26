"""Stage 5 assembly — deterministic Compass + legacy adapters."""

from __future__ import annotations

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
    build_character_engine_life_bundle_v0,
)
from todayflow_backend.services.character_engine_stage5_assembly_v0 import (
    ADAPTER_VERSION,
    COMPASS_SCHEMA,
    build_character_engine_assembly_v0,
)
from todayflow_backend.services.character_engine_profile_consumption_v0 import (
    apply_character_engine_profile_consumption_v0,
)


def _prereqs():
    facts = build_character_engine_facts_pack_v0(
        profile_fingerprint="pf_s5",
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
        input_fingerprint="in_s5",
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
                "qualifying_claim_ids": [],
                "contradicting_claim_ids": [],
                "confidence": "medium",
            },
            "source_roles": [{"role": "dominant_mechanism", "claim_id": primary["claim_id"]}],
            "selection_rationale": "test",
        },
    )
    claim_id = identity["identity_core"]["primary_claim_id"]
    thesis = identity["identity_core"]["thesis_key"]
    engine = {
        slot: {
            "surface_text": f"Проявление ядра в зоне {slot}.",
            "expansion_because": f"Это проявление {thesis}.",
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
                "expansion_because": f"Это проявление {thesis}.",
                "supporting_claim_ids": [claim_id],
            },
            "secondary_tensions": [],
            "selection_rationale": "test",
        },
    )
    stage4 = build_character_engine_life_bundle_v0(
        facts_pack=facts,
        evidence=evidence,
        identity=identity,
        stage3=stage3,
        llm_raw={
            "status": "grounded",
            "identity_thesis_echo": thesis,
            "scenes": [
                {
                    "scene_kind": "intimacy",
                    "surface_text": "В близости Stage5 intimacy.",
                    "expansion_because": f"Это проявление {thesis}.",
                    "supporting_claim_ids": [claim_id],
                    "rooted_in": "primary_tension",
                },
                {
                    "scene_kind": "risk",
                    "surface_text": "Риск Stage5 resource.",
                    "expansion_because": f"Это проявление {thesis}.",
                    "supporting_claim_ids": [claim_id],
                    "rooted_in": "risk",
                },
            ],
            "potential": {
                "surface_text": "Потенциал Stage5.",
                "expansion_because": f"Это проявление {thesis}.",
                "supporting_claim_ids": [claim_id],
            },
            "blind_spots": [
                {
                    "surface_text": "Слепое пятно Stage5.",
                    "expansion_because": f"Это проявление {thesis}.",
                    "supporting_claim_ids": [claim_id],
                }
            ],
            "selection_rationale": "test",
        },
    )
    return facts, evidence, identity, stage3, stage4


def test_stage5_grounded_assembly() -> None:
    _, _, identity, stage3, stage4 = _prereqs()
    out = build_character_engine_assembly_v0(
        identity=identity, stage3=stage3, stage4=stage4
    )
    assert out["status"] == "grounded"
    assert out["compass"]["schema_version"] == COMPASS_SCHEMA
    assert out["compass"]["items"]
    assert all(i.get("item_id") for i in out["compass"]["items"])
    assert out["legacy_map"]["adapter_version"] == ADAPTER_VERSION
    assert out["legacy_map"]["fields"]["decision_style"]["value"]
    assert out["legacy_map"]["fields"]["relationship_style"]["value"]
    assert out["validation"]["deterministic"] is True
    assert out["validation"]["ready_publish_blocked"] is True


def test_stage5_insufficient_without_stage4() -> None:
    _, _, identity, stage3, _ = _prereqs()
    out = build_character_engine_assembly_v0(
        identity=identity,
        stage3=stage3,
        stage4={"status": "insufficient_life_bundle"},
    )
    assert out["status"] == "insufficient_assembly"


def test_consumption_prefers_stage5_adapters(monkeypatch) -> None:
    monkeypatch.setattr(
        "todayflow_backend.services.character_engine_profile_consumption_v0."
        "character_engine_profile_consumption_enabled",
        lambda: True,
    )
    facts, evidence, identity, stage3, stage4 = _prereqs()
    stage5 = build_character_engine_assembly_v0(
        identity=identity, stage3=stage3, stage4=stage4
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
            "character_engine_stage5": {"stage5": stage5},
        },
        "profile_contract_v1": {},
    }
    out = apply_character_engine_profile_consumption_v0(payload)
    cons = out["character_engine_consumption_v0"]
    assert cons["applied"] is True
    assert cons["stage5_status"] == "grounded"
    assert cons["decision_source"] == "stage5_legacy_map.decision_style"
    assert cons["relationship_source"] == "stage5_legacy_map.relationship_style"
    assert "Stage5 intimacy" in out["profile_contract_v1"]["relationship_style"]
