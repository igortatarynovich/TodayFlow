"""B1.11 — Evolution → Practice Selector filter tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache, load_evolution_cd_v1
from todayflow_backend.data.evolution_product_effects_loader import clear_evolution_product_effects_cache
from todayflow_backend.services.evolution_effect_consumer_map_v1 import (
    CONSUMER_PRACTICE_SELECTOR,
    extract_evolution_effect_consumer_slice_v1,
)
from todayflow_backend.services.evolution_effect_runtime_policy_v1 import (
    build_evolution_effect_runtime_policy_v1,
)
from todayflow_backend.services.evolution_practice_selector_filter_v1 import (
    BLOCK_COMPLEXITY_ABOVE_STAGE,
    BLOCK_DURATION_ABOVE_CAP,
    BLOCK_PATH_THEME_NOT_ALLOWED,
    BLOCK_SAFETY_NOTE_REQUIRED,
    COMPLEXITY_ADVANCED,
    COMPLEXITY_BEGINNER,
    COMPLEXITY_INTERMEDIATE,
    ENTITY_TYPE_CYCLE,
    ENTITY_TYPE_HABIT,
    ENTITY_TYPE_PRACTICE,
    ENTITY_TYPE_RITUAL,
    EVOLUTION_PRACTICE_SELECTOR_FILTER_V1_CONTRACT,
    EVOLUTION_PRACTICE_SELECTOR_FILTER_V1_KEYS,
    build_evolution_practice_selector_filter_v1,
    validate_evolution_practice_selector_filter_v1,
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


def _policy_for_stage(cd: dict, stage: str, **policy_kwargs):
    progress_by_stage = {
        "seeker": {
            "confirmed_patterns": 0,
            "completed_cycles": 0,
            "reflection_events": 3,
            "active_days": 7,
            "signal_counts": {},
            "confidence": 0.4,
        },
        "observer": {
            "confirmed_patterns": 1,
            "completed_cycles": 0,
            "reflection_events": 8,
            "active_days": 14,
            "signal_counts": {},
            "confidence": 0.5,
        },
        "practitioner": {
            "confirmed_patterns": 2,
            "completed_cycles": 1,
            "reflection_events": 12,
            "active_days": 30,
            "signal_counts": {"practice_completed": 5},
            "confidence": 0.6,
        },
        "architect": {
            "confirmed_patterns": 5,
            "completed_cycles": 3,
            "reflection_events": 21,
            "active_days": 120,
            "signal_counts": {"confirmed_pattern": 2},
            "confidence": 0.75,
        },
    }
    state = build_evolution_user_state_v1(
        user_id="user-1",
        current_stage=stage,
        stage_started_at="2026-05-01T00:00:00Z",
        active_path_themes=["discipline"],
        completed_path_themes=[],
        progress_snapshot=progress_by_stage[stage],
        evolution_score_snapshot=100 if stage == "seeker" else 420,
        last_evaluated_at="2026-06-01T09:00:00Z",
        cd=cd,
    )
    return build_evolution_effect_runtime_policy_v1(
        evolution_user_state=state,
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
        **policy_kwargs,
    )


@pytest.fixture
def seeker_slice(cd: dict) -> dict:
    return extract_evolution_effect_consumer_slice_v1(
        _policy_for_stage(cd, "seeker"),
        CONSUMER_PRACTICE_SELECTOR,
    )


@pytest.fixture
def observer_slice(cd: dict) -> dict:
    return extract_evolution_effect_consumer_slice_v1(
        _policy_for_stage(cd, "observer"),
        CONSUMER_PRACTICE_SELECTOR,
    )


@pytest.fixture
def practitioner_slice(cd: dict) -> dict:
    return extract_evolution_effect_consumer_slice_v1(
        _policy_for_stage(cd, "practitioner"),
        CONSUMER_PRACTICE_SELECTOR,
    )


@pytest.fixture
def architect_slice(cd: dict) -> dict:
    return extract_evolution_effect_consumer_slice_v1(
        _policy_for_stage(
            cd,
            "architect",
            source_systems_ready={"calendar_intelligence": True, "share_features": True},
        ),
        CONSUMER_PRACTICE_SELECTOR,
    )


@pytest.fixture
def mentor_like_slice(architect_slice: dict) -> dict:
    slice_payload = copy.deepcopy(architect_slice)
    slice_payload["current_stage"] = "mentor"
    return slice_payload


def _candidate(**overrides):
    base = {
        "candidate_id": "practice:breathing",
        "entity_type": ENTITY_TYPE_PRACTICE,
        "code": "breathing",
        "complexity_level": COMPLEXITY_BEGINNER,
        "path_themes": ["discipline"],
        "duration_minutes": 5,
        "practice_pack_tier": "starter",
        "safety_note_required": False,
        "has_definition": True,
    }
    base.update(overrides)
    return base


def _path_context():
    return {"active_path_themes": ["discipline"]}


def test_seeker_blocks_advanced_candidates(seeker_slice: dict) -> None:
    candidates = [
        _candidate(),
        _candidate(
            candidate_id="practice:visualization",
            code="visualization",
            complexity_level=COMPLEXITY_ADVANCED,
            duration_minutes=8,
            practice_pack_tier="advanced",
        ),
    ]
    result = build_evolution_practice_selector_filter_v1(
        candidates,
        evolution_slice=seeker_slice,
        path_context=_path_context(),
    )

    allowed_ids = {item["candidate_id"] for item in result["filtered_candidates"]}
    blocked = {item["candidate_id"]: item["reason"] for item in result["blocked_candidates"]}

    assert "practice:breathing" in allowed_ids
    assert blocked["practice:visualization"] == BLOCK_COMPLEXITY_ABOVE_STAGE


def test_seeker_allows_simple_practice(seeker_slice: dict) -> None:
    result = build_evolution_practice_selector_filter_v1(
        [_candidate()],
        evolution_slice=seeker_slice,
        path_context=_path_context(),
    )

    assert len(result["filtered_candidates"]) == 1
    assert result["filtered_candidates"][0]["code"] == "breathing"


def test_observer_allows_simple_habit(observer_slice: dict) -> None:
    candidates = [
        _candidate(
            candidate_id="habit:daily_breathing",
            entity_type=ENTITY_TYPE_HABIT,
            code="daily_breathing",
            duration_minutes=10,
        )
    ]
    result = build_evolution_practice_selector_filter_v1(
        candidates,
        evolution_slice=observer_slice,
        path_context=_path_context(),
    )

    assert len(result["filtered_candidates"]) == 1
    assert result["filtered_candidates"][0]["entity_type"] == ENTITY_TYPE_HABIT


def test_practitioner_allows_ritual(practitioner_slice: dict) -> None:
    candidates = [
        _candidate(
            candidate_id="ritual:morning_grounding_ritual",
            entity_type=ENTITY_TYPE_RITUAL,
            code="morning_grounding_ritual",
            complexity_level=COMPLEXITY_BEGINNER,
            duration_minutes=15,
        )
    ]
    result = build_evolution_practice_selector_filter_v1(
        candidates,
        evolution_slice=practitioner_slice,
        path_context=_path_context(),
    )

    assert len(result["filtered_candidates"]) == 1
    assert result["filtered_candidates"][0]["entity_type"] == ENTITY_TYPE_RITUAL


def test_architect_allows_cycle(architect_slice: dict) -> None:
    candidates = [
        _candidate(
            candidate_id="cycle:twenty_one_day_discipline_cycle",
            entity_type=ENTITY_TYPE_CYCLE,
            code="twenty_one_day_discipline_cycle",
            complexity_level=COMPLEXITY_INTERMEDIATE,
            duration_minutes=30,
            cycle_length_days=21,
            practice_pack_tier="advanced",
        )
    ]
    result = build_evolution_practice_selector_filter_v1(
        candidates,
        evolution_slice=architect_slice,
        path_context=_path_context(),
    )

    assert len(result["filtered_candidates"]) == 1
    assert result["filtered_candidates"][0]["entity_type"] == ENTITY_TYPE_CYCLE


def test_path_theme_not_allowed_blocks_candidate(seeker_slice: dict) -> None:
    candidates = [
        _candidate(path_themes=["spirituality"]),
    ]
    result = build_evolution_practice_selector_filter_v1(
        candidates,
        evolution_slice=seeker_slice,
        path_context=_path_context(),
    )

    assert result["filtered_candidates"] == []
    assert result["blocked_candidates"][0]["reason"] == BLOCK_PATH_THEME_NOT_ALLOWED


def test_duration_above_cap_blocks_candidate(seeker_slice: dict) -> None:
    candidates = [
        _candidate(duration_minutes=25),
    ]
    result = build_evolution_practice_selector_filter_v1(
        candidates,
        evolution_slice=seeker_slice,
        path_context=_path_context(),
    )

    assert result["filtered_candidates"] == []
    assert result["blocked_candidates"][0]["reason"] == BLOCK_DURATION_ABOVE_CAP


def test_safety_required_blocks_candidate(mentor_like_slice: dict) -> None:
    candidates = [
        _candidate(
            candidate_id="practice:ascetic_boundary",
            complexity_level=COMPLEXITY_ADVANCED,
            duration_minutes=20,
            practice_pack_tier="advanced",
            safety_note_required=True,
        )
    ]
    result = build_evolution_practice_selector_filter_v1(
        candidates,
        evolution_slice=mentor_like_slice,
        path_context=_path_context(),
    )

    assert result["safety_notes_required"] is True
    assert result["filtered_candidates"] == []
    assert result["blocked_candidates"][0]["reason"] == BLOCK_SAFETY_NOTE_REQUIRED


def test_no_final_selection_performed(seeker_slice: dict) -> None:
    result = build_evolution_practice_selector_filter_v1(
        [_candidate()],
        evolution_slice=seeker_slice,
        path_context=_path_context(),
    )

    assert result["selection_performed"] is False
    assert len(result["filtered_candidates"]) >= 1


def test_mutation_flags_false(seeker_slice: dict) -> None:
    result = build_evolution_practice_selector_filter_v1(
        [_candidate()],
        evolution_slice=seeker_slice,
        path_context=_path_context(),
    )

    assert result["selection_performed"] is False
    assert result["recommendation_created"] is False


def test_output_shape_stable(architect_slice: dict) -> None:
    result = build_evolution_practice_selector_filter_v1(
        [_candidate(entity_type=ENTITY_TYPE_PRACTICE)],
        evolution_slice=architect_slice,
        path_context=_path_context(),
    )

    assert result["contract_version"] == EVOLUTION_PRACTICE_SELECTOR_FILTER_V1_CONTRACT
    assert set(result.keys()) == EVOLUTION_PRACTICE_SELECTOR_FILTER_V1_KEYS
    assert validate_evolution_practice_selector_filter_v1(result) == []
