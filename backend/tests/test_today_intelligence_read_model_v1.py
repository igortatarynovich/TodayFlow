"""S1.1 — Today Intelligence Read Model tests."""

from __future__ import annotations

import json

import pytest

from todayflow_backend.data.day_content_registry_loader import clear_day_content_registry_cache
from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache, load_evolution_cd_v1
from todayflow_backend.data.evolution_product_effects_loader import clear_evolution_product_effects_cache
from todayflow_backend.data.reference_machine_loader import clear_reference_machine_cache
from todayflow_backend.services.day_model_v1_active_knowledge import (
    DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_aggregator import aggregate_day_model_v1
from todayflow_backend.services.day_model_v1_content_assembler import assemble_day_content_package_v1
from todayflow_backend.services.day_model_v1_content_mapper import (
    map_day_model_interpretation_to_content_keys,
)
from todayflow_backend.services.day_model_v1_content_resolver import (
    resolve_content_entries_from_mapping,
)
from todayflow_backend.services.day_model_v1_interpreter import interpret_day_model_v1
from todayflow_backend.services.day_model_v1_knowledge_candidate import KNOWLEDGE_TYPE_BEHAVIOR
from todayflow_backend.services.day_model_v1_knowledge_context_selection import (
    select_knowledge_context_v1,
)
from todayflow_backend.services.day_model_v1_personalization_usage_gate import (
    PERSONALIZATION_USAGE_GATE_V1_CONTRACT,
    USAGE_DECISION_ALLOW,
    USAGE_DECISION_DENY,
)
from todayflow_backend.services.evolution_day_presentation_envelope_v1 import (
    ANSWER_DEPTH_MINIMAL,
    ANSWER_DEPTH_NORMAL,
    TONE_SIMPLE,
    TONE_STRATEGIC,
    wire_guide_decision_with_evolution_presentation_v1,
)
from todayflow_backend.services.evolution_effect_consumer_map_v1 import (
    CONSUMER_DAY_ENGINE,
    extract_evolution_effect_consumer_slice_v1,
)
from todayflow_backend.services.evolution_effect_runtime_policy_v1 import (
    build_evolution_effect_runtime_policy_v1,
)
from todayflow_backend.services.evolution_user_state_v1 import build_evolution_user_state_v1
from todayflow_backend.services.today_intelligence_read_model_v1 import (
    KNOWLEDGE_SUMMARY_STATUS_ACTIVE,
    KNOWLEDGE_SUMMARY_STATUS_DENIED,
    KNOWLEDGE_SUMMARY_STATUS_EMPTY,
    TODAY_INTELLIGENCE_READ_MODEL_V1_CONTRACT,
    TODAY_INTELLIGENCE_READ_MODEL_V1_KEYS,
    VISIBILITY_MINIMAL,
    VISIBILITY_STANDARD,
    build_today_intelligence_read_model_from_presentation_wiring_v1,
    build_today_intelligence_read_model_v1,
    validate_today_intelligence_read_model_v1,
)
from tests.test_cross_domain_machine_validation import (
    ANCHOR_NUMEROLOGY,
    ANCHOR_PLANET,
    ANCHOR_SIGN,
    ANCHOR_TAROT,
)


@pytest.fixture(autouse=True)
def _clear_caches():
    clear_reference_machine_cache()
    clear_day_content_registry_cache()
    clear_evolution_cd_cache()
    clear_evolution_product_effects_cache()
    yield
    clear_reference_machine_cache()
    clear_day_content_registry_cache()
    clear_evolution_cd_cache()
    clear_evolution_product_effects_cache()


@pytest.fixture
def cd() -> dict:
    return load_evolution_cd_v1()


@pytest.fixture
def seeker_day_engine_slice(cd: dict) -> dict:
    state = build_evolution_user_state_v1(
        user_id="user-s11",
        current_stage="seeker",
        stage_started_at="2026-05-01T00:00:00Z",
        active_path_themes=["discipline"],
        completed_path_themes=[],
        progress_snapshot={
            "confirmed_patterns": 0,
            "completed_cycles": 0,
            "reflection_events": 3,
            "active_days": 7,
            "signal_counts": {},
            "confidence": 0.4,
        },
        evolution_score_snapshot=50,
        last_evaluated_at="2026-06-01T09:00:00Z",
        cd=cd,
    )
    policy = build_evolution_effect_runtime_policy_v1(
        evolution_user_state=state,
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-s11:2026-06-01T09:00:00Z",
    )
    return extract_evolution_effect_consumer_slice_v1(policy, CONSUMER_DAY_ENGINE)


def _legacy_day_model_v0() -> dict:
    return {
        "contract_version": "day_model_v0",
        "vector": {"direction": "growth", "summary": "grow"},
        "tempo": {"label": "steady", "summary": "steady day"},
        "risk": {"summary": "overload risk"},
        "strategy": {"summary": "one focus", "one_focus": "finish"},
        "scales": {"direction": "growth", "tempo": "steady"},
        "gate": {"vector_defined": True, "risk_defined": True},
    }


def _active_knowledge(**overrides):
    base = {
        "contract_version": DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
        "knowledge_id": "know-s11-001",
        "source_knowledge_candidate_id": "kcand-s11-001",
        "knowledge_type": KNOWLEDGE_TYPE_BEHAVIOR,
        "claim": "responds_to_action_mode:single_step",
        "confidence": 0.8,
        "evidence_count": 7,
        "evidence_window_days": 21,
        "evidence_signal_ids": [f"lsig-{i}" for i in range(7)],
        "source_pattern_id": "pat-s11-001",
        "status": "active",
        "created_at": "2026-05-31T12:00:00Z",
        "last_confirmed_at": "2026-05-31T12:00:00Z",
        "expires_at": None,
        "review_required": False,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_update_allowed": False,
    }
    base.update(overrides)
    return base


def _allow_gate(**overrides):
    base = {
        "contract_version": PERSONALIZATION_USAGE_GATE_V1_CONTRACT,
        "usage_gate_id": "pug-s11-001",
        "surface": "day_guidance_card",
        "decision": USAGE_DECISION_ALLOW,
        "reason": "test",
        "allowed_fact_count": 1,
        "safe_personalization_summary": ["prefers short action hints"],
        "context_slice_id": "kctx-s11-001",
        "personalization_id": "pers-s11-001",
        "llm_gate_context_depth": "standard",
        "traceability": {},
        "status": "ready",
        "created_at": "2026-06-01T09:00:00Z",
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_model_update_allowed": False,
    }
    base.update(overrides)
    return base


def _deny_gate(**overrides):
    return _allow_gate(decision=USAGE_DECISION_DENY, reason="surface_not_eligible", **overrides)


def _full_p1_pipeline():
    dm = aggregate_day_model_v1(
        tarot_entity_code=ANCHOR_TAROT,
        numerology_entity_code=ANCHOR_NUMEROLOGY,
        astrology_planet_code=ANCHOR_PLANET,
        astrology_sign_code=ANCHOR_SIGN,
    )
    interpretation = interpret_day_model_v1(dm)
    mapping = map_day_model_interpretation_to_content_keys(interpretation)
    resolution = resolve_content_entries_from_mapping(mapping)
    package = assemble_day_content_package_v1(interpretation, mapping, resolution)
    return dm, interpretation, mapping, package


def test_legacy_day_model_valid_read_model() -> None:
    read_model = build_today_intelligence_read_model_v1(
        user_id="user-s11",
        date="2026-05-31",
        day_model=_legacy_day_model_v0(),
    )

    assert read_model["contract_version"] == TODAY_INTELLIGENCE_READ_MODEL_V1_CONTRACT
    assert read_model["day_model_snapshot_id"].startswith("snap-")
    assert read_model["interpretation_id"] is None
    assert read_model["content_package_id"] is None
    assert read_model["evolution_stage"] is None
    assert read_model["answer_depth_cap"] == ANSWER_DEPTH_MINIMAL
    assert validate_today_intelligence_read_model_v1(read_model) == []


def test_knowledge_summary_included_when_gate_allows() -> None:
    context_slice = select_knowledge_context_v1([_active_knowledge()], target_surface="day_guidance_card")

    read_model = build_today_intelligence_read_model_v1(
        user_id="user-s11",
        date="2026-05-31",
        day_model=_legacy_day_model_v0(),
        knowledge_context_slice=context_slice,
        personalization_gate=_allow_gate(context_slice_id=context_slice["context_slice_id"]),
    )

    summary = read_model["knowledge_context_summary"]
    assert summary["status"] == KNOWLEDGE_SUMMARY_STATUS_ACTIVE
    assert summary["fact_types"] == ["behavior"]
    assert read_model["knowledge_fact_count"] == 1
    assert read_model["personalization_active"] is True
    assert "claim" not in json.dumps(read_model)


def test_evolution_envelope_included(seeker_day_engine_slice: dict) -> None:
    dm, interpretation, mapping, package = _full_p1_pipeline()
    wired = wire_guide_decision_with_evolution_presentation_v1(
        {"contract_version": "guide_decision_v0", "locale": "ru", "anchors": {}},
        evolution_slice=seeker_day_engine_slice,
        day_model=dm,
    )
    envelope = wired["evolution_day_presentation_envelope"]

    read_model = build_today_intelligence_read_model_v1(
        user_id="user-s11",
        date="2026-05-31",
        day_model=dm,
        interpretation=interpretation,
        content_mapping=mapping,
        content_package=package,
        presentation_envelope=envelope,
    )

    assert read_model["evolution_stage"] == "seeker"
    assert read_model["answer_depth_cap"] == ANSWER_DEPTH_MINIMAL
    assert read_model["tone_policy"] == TONE_SIMPLE
    assert read_model["available_surfaces"] == envelope["surface_priority_hints"]
    assert "interpretation_cap" not in read_model
    assert "blocked_effects" not in read_model


def test_no_full_policies_exposed(seeker_day_engine_slice: dict) -> None:
    read_model = build_today_intelligence_read_model_from_presentation_wiring_v1(
        user_id="user-s11",
        date="2026-05-31",
        day_model=_legacy_day_model_v0(),
        wired_guide_decision=wire_guide_decision_with_evolution_presentation_v1(
            {"contract_version": "guide_decision_v0", "locale": "ru", "anchors": {}},
            evolution_slice=seeker_day_engine_slice,
            day_model=_legacy_day_model_v0(),
        ),
    )

    payload = json.dumps(read_model)
    for forbidden in (
        "effect_limits",
        "allowed_effects",
        "consumer_slice",
        "blocked_effects",
        "interpretation_cap",
        "envelope_id",
    ):
        assert forbidden not in payload


def test_no_active_knowledge_claims_exposed() -> None:
    context_slice = select_knowledge_context_v1([_active_knowledge()], target_surface="day_guidance_card")

    read_model = build_today_intelligence_read_model_v1(
        user_id="user-s11",
        date="2026-05-31",
        day_model=_legacy_day_model_v0(),
        knowledge_context_slice=context_slice,
        personalization_gate=_allow_gate(context_slice_id=context_slice["context_slice_id"]),
    )

    payload = json.dumps(read_model)
    assert "responds_to_action_mode" not in payload
    assert "selected_facts" not in payload
    assert "confidence" not in payload


def test_no_llm_traces_exposed() -> None:
    dm, interpretation, mapping, package = _full_p1_pipeline()
    read_model = build_today_intelligence_read_model_v1(
        user_id="user-s11",
        date="2026-05-31",
        day_model=dm,
        interpretation=interpretation,
        content_mapping=mapping,
        content_package=package,
    )

    payload = json.dumps(read_model)
    for forbidden in ("llm_trace", "prompt", "generation_id", "render_id", "evaluation_id"):
        assert forbidden not in payload


def test_no_recommendation_fields() -> None:
    read_model = build_today_intelligence_read_model_v1(
        user_id="user-s11",
        date="2026-05-31",
        day_model=_legacy_day_model_v0(),
    )

    payload = json.dumps(read_model)
    for forbidden in ("recommendation", "next_best_action", "ranking"):
        assert forbidden not in payload


def test_no_commerce_fields() -> None:
    read_model = build_today_intelligence_read_model_v1(
        user_id="user-s11",
        date="2026-05-31",
        day_model=_legacy_day_model_v0(),
    )

    payload = json.dumps(read_model)
    for forbidden in ("commerce", "sku", "purchase_prompt", "checkout", "pricing"):
        assert forbidden not in payload


def test_visibility_applied(seeker_day_engine_slice: dict, cd: dict) -> None:
    state = build_evolution_user_state_v1(
        user_id="user-s11",
        current_stage="architect",
        stage_started_at="2026-05-01T00:00:00Z",
        active_path_themes=["discipline"],
        completed_path_themes=[],
        progress_snapshot={
            "confirmed_patterns": 5,
            "completed_cycles": 3,
            "reflection_events": 21,
            "active_days": 120,
            "signal_counts": {"confirmed_pattern": 2},
            "confidence": 0.75,
        },
        evolution_score_snapshot=420,
        last_evaluated_at="2026-06-01T09:00:00Z",
        cd=cd,
    )
    policy = build_evolution_effect_runtime_policy_v1(
        evolution_user_state=state,
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-s11:2026-06-01T09:00:00Z",
        source_systems_ready={"calendar_intelligence": True, "share_features": True},
    )
    architect_slice = extract_evolution_effect_consumer_slice_v1(policy, CONSUMER_DAY_ENGINE)
    wired = wire_guide_decision_with_evolution_presentation_v1(
        {"contract_version": "guide_decision_v0", "locale": "ru", "anchors": {}},
        evolution_slice=architect_slice,
    )
    envelope = wired["evolution_day_presentation_envelope"]

    read_model = build_today_intelligence_read_model_v1(
        user_id="user-s11",
        date="2026-05-31",
        day_model=_legacy_day_model_v0(),
        presentation_envelope=envelope,
    )

    assert read_model["visibility_level"] == VISIBILITY_STANDARD
    assert read_model["answer_depth_cap"] == ANSWER_DEPTH_NORMAL
    assert read_model["tone_policy"] == TONE_STRATEGIC
    assert read_model["available_surfaces"] == envelope["surface_priority_hints"]


def test_output_shape_stable() -> None:
    read_model = build_today_intelligence_read_model_v1(
        user_id="user-s11",
        date="2026-05-31",
        day_model=_legacy_day_model_v0(),
        read_model_id="tirm-stable-001",
        generated_at="2026-06-01T09:00:00Z",
    )

    assert set(read_model.keys()) == TODAY_INTELLIGENCE_READ_MODEL_V1_KEYS
    assert validate_today_intelligence_read_model_v1(read_model) == []

    again = build_today_intelligence_read_model_v1(
        user_id="user-s11",
        date="2026-05-31",
        day_model=_legacy_day_model_v0(),
        read_model_id="tirm-stable-001",
        generated_at="2026-06-01T09:00:00Z",
    )
    assert again == read_model


def test_personalization_gate_deny_hides_knowledge_summary() -> None:
    context_slice = select_knowledge_context_v1([_active_knowledge()], target_surface="day_guidance_card")

    read_model = build_today_intelligence_read_model_v1(
        user_id="user-s11",
        date="2026-05-31",
        day_model=_legacy_day_model_v0(),
        knowledge_context_slice=context_slice,
        personalization_gate=_deny_gate(context_slice_id=context_slice["context_slice_id"]),
    )

    assert read_model["knowledge_context_summary"]["status"] == KNOWLEDGE_SUMMARY_STATUS_DENIED
    assert read_model["knowledge_fact_count"] == 0
    assert read_model["personalization_active"] is False


def test_guidance_refs_from_content_mapping() -> None:
    dm, interpretation, mapping, package = _full_p1_pipeline()

    read_model = build_today_intelligence_read_model_v1(
        user_id="user-s11",
        date="2026-05-31",
        day_model=dm,
        interpretation=interpretation,
        content_mapping=mapping,
        content_package=package,
    )

    assert read_model["primary_guidance_ref"] == mapping["content_keys"]["strategy"]
    assert read_model["action_ref"] == mapping["content_keys"]["action_mode"]
    assert read_model["reflection_ref"] is not None
    assert read_model["interpretation_id"] is not None
    assert read_model["content_package_id"] is not None


def test_empty_knowledge_without_gate() -> None:
    read_model = build_today_intelligence_read_model_v1(
        user_id="user-s11",
        date="2026-05-31",
        day_model=_legacy_day_model_v0(),
    )

    assert read_model["knowledge_context_summary"]["status"] == KNOWLEDGE_SUMMARY_STATUS_EMPTY
    assert read_model["knowledge_fact_count"] == 0
    assert read_model["personalization_active"] is False
    assert read_model["visibility_level"] == VISIBILITY_MINIMAL
