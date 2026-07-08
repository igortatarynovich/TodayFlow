"""B1.10 — Evolution Day Presentation Envelope tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache, load_evolution_cd_v1
from todayflow_backend.data.evolution_product_effects_loader import clear_evolution_product_effects_cache
from todayflow_backend.services.day_model_v1_active_knowledge import DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT
from todayflow_backend.services.day_model_v1_day_engine_knowledge_integration import (
    try_build_day_engine_knowledge_input_v1,
)
from todayflow_backend.services.day_model_v1_day_engine_knowledge_wiring import (
    WIRING_RESULT_APPLIED,
    extract_day_model_core_snapshot,
    try_apply_day_engine_knowledge_v1,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import KNOWLEDGE_TYPE_BEHAVIOR
from todayflow_backend.services.day_model_v1_knowledge_context_selection import (
    select_knowledge_context_v1,
)
from todayflow_backend.services.evolution_day_presentation_envelope_v1 import (
    ANSWER_DEPTH_MINIMAL,
    ANSWER_DEPTH_NORMAL,
    EVOLUTION_DAY_PRESENTATION_ENVELOPE_V1_CONTRACT,
    EVOLUTION_DAY_PRESENTATION_ENVELOPE_V1_KEYS,
    FORBIDDEN_ENVELOPE_MUTATION_FIELDS,
    TONE_SIMPLE,
    TONE_STRATEGIC,
    attach_evolution_day_presentation_envelope_v1,
    extract_guide_decision_semantic_snapshot,
    validate_evolution_day_presentation_envelope_v1,
    validate_guide_decision_with_evolution_presentation_envelope_v1,
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


@pytest.fixture(autouse=True)
def _clear_caches() -> None:
    clear_evolution_cd_cache()
    clear_evolution_product_effects_cache()
    yield
    clear_evolution_cd_cache()
    clear_evolution_product_effects_cache()


@pytest.fixture
def cd() -> dict:
    return load_evolution_cd_v1()


@pytest.fixture
def seeker_day_engine_slice(cd: dict) -> dict:
    state = build_evolution_user_state_v1(
        user_id="user-1",
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
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
    )
    return extract_evolution_effect_consumer_slice_v1(policy, CONSUMER_DAY_ENGINE)


@pytest.fixture
def architect_day_engine_slice(cd: dict) -> dict:
    state = build_evolution_user_state_v1(
        user_id="user-1",
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
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
        source_systems_ready={
            "calendar_intelligence": True,
            "share_features": True,
        },
    )
    return extract_evolution_effect_consumer_slice_v1(policy, CONSUMER_DAY_ENGINE)


def _minimal_guide_decision(**overrides):
    base = {
        "contract_version": "guide_decision_v0",
        "locale": "ru",
        "headline": "Test headline",
        "subline": "Subline text",
        "core_message": {"body": "body", "risk": "risk", "best_move": "move"},
        "do_items": ["step one", "step two", "step three"],
        "avoid_items": ["avoid one", "avoid two", "avoid three"],
        "energy_line": "energy",
        "focus_line": "focus",
        "risk_line": "risk",
        "risk_detail": "detail",
        "anchors": {"tempo": "steady", "day_direction": "growth"},
    }
    base.update(overrides)
    return base


def _minimal_day_model():
    return {
        "contract_version": "day_model_v0",
        "vector": {"direction": "growth", "summary": "grow"},
        "tempo": {"label": "steady", "summary": "steady day"},
        "risk": {"summary": "overload risk"},
        "strategy": {"summary": "one focus", "one_focus": "finish"},
        "scales": {"direction": "growth", "tempo": "steady"},
        "gate": {"vector_defined": True, "risk_defined": True},
    }


def _knowledge_input():
    active = {
        "contract_version": DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
        "knowledge_id": "know-test-001",
        "source_knowledge_candidate_id": "kcand-test-001",
        "knowledge_type": KNOWLEDGE_TYPE_BEHAVIOR,
        "claim": "responds_to_action_mode:single_step",
        "confidence": 0.8,
        "evidence_count": 7,
        "evidence_window_days": 21,
        "evidence_signal_ids": [f"lsig-{i}" for i in range(7)],
        "source_pattern_id": "pat-test-001",
        "status": "active",
        "created_at": "2026-05-31T12:00:00Z",
        "last_confirmed_at": "2026-05-31T12:00:00Z",
        "expires_at": None,
        "review_required": False,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_update_allowed": False,
    }
    context_slice = select_knowledge_context_v1([active], target_surface="day_guidance_card")
    outcome = try_build_day_engine_knowledge_input_v1(
        context_slice,
        day_model_snapshot=extract_day_model_core_snapshot(_minimal_day_model()),
    )
    assert outcome["knowledge_input"] is not None
    return outcome["knowledge_input"]


def test_no_slice_legacy_day_engine_unchanged() -> None:
    guide = _minimal_guide_decision()
    day_model = _minimal_day_model()
    semantic_before = extract_guide_decision_semantic_snapshot(guide)
    dm_before = extract_day_model_core_snapshot(day_model)

    wired = wire_guide_decision_with_evolution_presentation_v1(
        guide,
        evolution_slice=None,
        day_model=day_model,
    )

    assert extract_guide_decision_semantic_snapshot(wired) == semantic_before
    assert extract_day_model_core_snapshot(day_model) == dm_before
    envelope = wired["evolution_day_presentation_envelope"]
    assert envelope["source_evolution_slice_id"] is None
    assert envelope["blocked_effects"] == ["ignored:no_evolution_slice"]
    assert envelope["source_day_model_hash"] is not None


def test_seeker_shallow_depth_simple_tone(seeker_day_engine_slice: dict) -> None:
    wired = wire_guide_decision_with_evolution_presentation_v1(
        _minimal_guide_decision(),
        evolution_slice=seeker_day_engine_slice,
        day_model=_minimal_day_model(),
    )
    envelope = wired["evolution_day_presentation_envelope"]

    assert envelope["source_evolution_slice_id"] == seeker_day_engine_slice["slice_id"]
    assert envelope["evolution_stage"] == "seeker"
    assert envelope["answer_depth_cap"] == ANSWER_DEPTH_MINIMAL
    assert envelope["tone_policy"] == TONE_SIMPLE
    assert envelope["interpretation_cap"] == 0


def test_architect_deeper_envelope_no_daymodel_mutation(architect_day_engine_slice: dict) -> None:
    guide = _minimal_guide_decision()
    day_model = _minimal_day_model()
    dm_before = extract_day_model_core_snapshot(day_model)

    wired = wire_guide_decision_with_evolution_presentation_v1(
        guide,
        evolution_slice=architect_day_engine_slice,
        day_model=day_model,
    )
    envelope = wired["evolution_day_presentation_envelope"]

    assert envelope["answer_depth_cap"] == ANSWER_DEPTH_NORMAL
    assert envelope["interpretation_cap"] == 4
    assert envelope["tone_policy"] == TONE_STRATEGIC
    assert any("answer_depth" in item for item in envelope["blocked_effects"])
    assert envelope["core_daymodel_mutated"] is False
    assert extract_day_model_core_snapshot(day_model) == dm_before
    assert extract_guide_decision_semantic_snapshot(wired) == extract_guide_decision_semantic_snapshot(
        guide
    )


def test_interpretation_cap_applied(architect_day_engine_slice: dict) -> None:
    wired = wire_guide_decision_with_evolution_presentation_v1(
        _minimal_guide_decision(),
        evolution_slice=architect_day_engine_slice,
    )
    envelope = wired["evolution_day_presentation_envelope"]

    assert envelope["interpretation_cap"] == 4
    assert architect_day_engine_slice["effect_limits"]["max_context_lines"] == 4


def test_surface_priority_hints_advisory_only(architect_day_engine_slice: dict) -> None:
    guide = _minimal_guide_decision()
    wired = wire_guide_decision_with_evolution_presentation_v1(
        guide,
        evolution_slice=architect_day_engine_slice,
    )
    envelope = wired["evolution_day_presentation_envelope"]

    assert envelope["surface_priority_hints"] == [
        "day_guidance_card",
        "action_card",
        "reflection_card",
    ]
    assert wired["anchors"] == guide["anchors"]


def test_invalid_slice_ignored_with_trace(seeker_day_engine_slice: dict) -> None:
    guide = _minimal_guide_decision()
    invalid = copy.deepcopy(seeker_day_engine_slice)
    invalid["effect_limits"] = "not-an-object"

    wired = attach_evolution_day_presentation_envelope_v1(guide, invalid)
    envelope = wired["evolution_day_presentation_envelope"]

    assert extract_guide_decision_semantic_snapshot(wired) == extract_guide_decision_semantic_snapshot(
        guide
    )
    assert envelope["source_evolution_slice_id"] is None
    assert envelope["blocked_effects"] == ["ignored:invalid_slice_payload"]


def test_full_policy_rejected_or_ignored(cd: dict) -> None:
    state = build_evolution_user_state_v1(
        user_id="user-1",
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
    full_policy = build_evolution_effect_runtime_policy_v1(
        evolution_user_state=state,
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
    )

    wired = wire_guide_decision_with_evolution_presentation_v1(
        _minimal_guide_decision(),
        evolution_slice=full_policy,
    )
    envelope = wired["evolution_day_presentation_envelope"]

    assert envelope["source_evolution_slice_id"] is None
    assert envelope["blocked_effects"] == ["ignored:full_policy_not_accepted"]


def test_knowledge_input_and_evolution_slice_coexist(architect_day_engine_slice: dict) -> None:
    guide = _minimal_guide_decision()
    knowledge_input = _knowledge_input()
    day_model = _minimal_day_model()

    knowledge_outcome = try_apply_day_engine_knowledge_v1(
        knowledge_input,
        guide,
        day_model=day_model,
    )
    assert knowledge_outcome["result"] == WIRING_RESULT_APPLIED
    knowledge_guide = knowledge_outcome["wiring_result"]["guide_decision_with_knowledge"]

    wired = wire_guide_decision_with_evolution_presentation_v1(
        knowledge_guide,
        evolution_slice=architect_day_engine_slice,
        day_model=day_model,
        knowledge_input=knowledge_input,
    )

    assert len(wired["do_items"]) == 1
    assert wired["knowledge_hints"] is not None
    envelope = wired["evolution_day_presentation_envelope"]
    assert envelope["source_evolution_slice_id"] is not None
    assert envelope["tone_policy"] == TONE_STRATEGIC
    assert envelope["knowledge_coexistence_trace"]["integration_id"] is not None


def test_core_daymodel_mutated_false(architect_day_engine_slice: dict) -> None:
    wired = wire_guide_decision_with_evolution_presentation_v1(
        _minimal_guide_decision(),
        evolution_slice=architect_day_engine_slice,
        day_model=_minimal_day_model(),
    )

    assert wired["evolution_day_presentation_envelope"]["core_daymodel_mutated"] is False


def test_output_shape_stable(architect_day_engine_slice: dict) -> None:
    wired = wire_guide_decision_with_evolution_presentation_v1(
        _minimal_guide_decision(),
        evolution_slice=architect_day_engine_slice,
        day_model=_minimal_day_model(),
    )
    envelope = wired["evolution_day_presentation_envelope"]

    assert envelope["contract_version"] == EVOLUTION_DAY_PRESENTATION_ENVELOPE_V1_CONTRACT
    assert set(envelope.keys()) == EVOLUTION_DAY_PRESENTATION_ENVELOPE_V1_KEYS
    assert validate_evolution_day_presentation_envelope_v1(envelope) == []
    assert validate_guide_decision_with_evolution_presentation_envelope_v1(wired) == []


def test_envelope_rejects_forbidden_mutation_fields() -> None:
    envelope = {
        "contract_version": EVOLUTION_DAY_PRESENTATION_ENVELOPE_V1_CONTRACT,
        "envelope_id": "edpe-test",
        "source_day_model_hash": None,
        "source_evolution_slice_id": None,
        "evolution_stage": None,
        "answer_depth_cap": None,
        "tone_policy": None,
        "interpretation_cap": None,
        "surface_priority_hints": [],
        "knowledge_coexistence_trace": None,
        "blocked_effects": [],
        "core_daymodel_mutated": False,
        "created_at": "2026-06-01T09:00:00Z",
        "vector": {"direction": "growth"},
    }
    errors = validate_evolution_day_presentation_envelope_v1(envelope)
    assert any("forbidden envelope mutation fields" in error for error in errors)
    assert "vector" in FORBIDDEN_ENVELOPE_MUTATION_FIELDS
