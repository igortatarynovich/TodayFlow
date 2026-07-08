"""B1.9 — Evolution → Context Selector wiring tests."""

from __future__ import annotations

import copy
from datetime import UTC, datetime

import pytest

from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache, load_evolution_cd_v1
from todayflow_backend.data.evolution_product_effects_loader import clear_evolution_product_effects_cache
from todayflow_backend.services.day_model_v1_active_knowledge import DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT
from todayflow_backend.services.day_model_v1_knowledge_context_selection import (
    HARD_CAP_DEFAULT,
    KNOWLEDGE_CONTEXT_SLICE_V1_CONTRACT,
    select_knowledge_context_v1,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import KNOWLEDGE_TYPE_CONTENT_AFFINITY
from todayflow_backend.services.evolution_context_selector_wiring_v1 import (
    EXCLUSION_EVOLUTION_CAP,
    KNOWLEDGE_CONTEXT_SLICE_V1_WITH_EVOLUTION_KEYS,
    select_knowledge_context_with_evolution_v1,
    validate_evolution_context_selector_wiring_v1,
)
from todayflow_backend.services.evolution_effect_consumer_map_v1 import (
    CONSUMER_CONTEXT_SELECTOR,
    extract_evolution_effect_consumer_slice_v1,
)
from todayflow_backend.services.evolution_effect_runtime_policy_v1 import (
    build_evolution_effect_runtime_policy_v1,
)
from todayflow_backend.services.evolution_user_state_v1 import build_evolution_user_state_v1

NOW = datetime(2026, 5, 31, 12, 0, 0, tzinfo=UTC)


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
def seeker_context_slice(cd: dict) -> dict:
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
    return extract_evolution_effect_consumer_slice_v1(policy, CONSUMER_CONTEXT_SELECTOR)


@pytest.fixture
def architect_context_slice(cd: dict) -> dict:
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
    return extract_evolution_effect_consumer_slice_v1(policy, CONSUMER_CONTEXT_SELECTOR)


def _active(**overrides):
    base = {
        "contract_version": DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
        "knowledge_id": "know-test-001",
        "source_knowledge_candidate_id": "kcand-test-001",
        "knowledge_type": KNOWLEDGE_TYPE_CONTENT_AFFINITY,
        "claim": "prefers_content_key_group:day.guidance",
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
    base.update(overrides)
    return base


def _pool(count: int):
    claim_specs = [
        ("know-0", "prefers_content_key_group:day.topic0"),
        ("know-1", "responds_to_surface:day_guidance"),
        ("know-2", "responds_to_tempo:slow"),
        ("know-3", "prefers_action_card:stretch"),
        ("know-4", "risk_response_tolerance:medium"),
        ("know-5", "prefers_content_key_group:day.topic5"),
    ]
    return [
        _active(knowledge_id=knowledge_id, claim=claim)
        for knowledge_id, claim in claim_specs[:count]
    ]


def _selected_ids(context_slice: dict) -> list[str]:
    return [fact["knowledge_id"] for fact in context_slice["selected_facts"]]


def test_no_slice_legacy_selection_unchanged() -> None:
    pool = _pool(2)
    day_context = {"content_keys": ["day.topic0", "day.guidance"]}
    base = select_knowledge_context_v1(
        pool,
        day_context=day_context,
        target_surface="day_guidance_card",
        now=NOW,
        context_slice_id="kctx-test-fixed",
    )
    wired = select_knowledge_context_with_evolution_v1(
        pool,
        day_context=day_context,
        target_surface="day_guidance_card",
        evolution_slice=None,
        now=NOW,
        context_slice_id="kctx-test-fixed",
    )

    assert _selected_ids(wired) == _selected_ids(base)
    assert wired["soft_cap"] == base["soft_cap"]
    assert wired["hard_cap"] == base["hard_cap"]
    assert wired["final_scores"] == base["final_scores"]
    assert wired["evolution_slice_applied"] is False
    assert wired["evolution_cap_reason"] == "no_evolution_slice"


def test_seeker_caps_selected_facts(seeker_context_slice: dict) -> None:
    pool = _pool(4)
    wired = select_knowledge_context_with_evolution_v1(
        pool,
        day_context={"content_keys": ["day.topic0", "day.guidance", "slow", "stretch"]},
        target_surface="day_guidance_card",
        evolution_slice=seeker_context_slice,
        now=NOW,
    )

    assert wired["evolution_slice_applied"] is True
    assert wired["evolution_ak_cap"] == 0
    assert wired["selected_facts"] == []
    assert wired["hard_cap"] == 0


def test_architect_allows_up_to_five_but_does_not_force_five(architect_context_slice: dict) -> None:
    pool = _pool(2)
    wired = select_knowledge_context_with_evolution_v1(
        pool,
        day_context={"content_keys": ["day.topic0", "day.guidance"]},
        target_surface="day_guidance_card",
        evolution_slice=architect_context_slice,
        now=NOW,
    )

    assert wired["evolution_ak_cap"] == 4
    assert len(wired["selected_facts"]) == 2
    assert wired["evolution_expansion_allowed"] is True


def test_stage_cap_never_exceeds_a1_1_hard_cap(architect_context_slice: dict) -> None:
    pool = _pool(6)
    wired = select_knowledge_context_with_evolution_v1(
        pool,
        day_context={
            "content_keys": ["day.topic0", "day.guidance", "slow", "stretch", "medium", "day.topic5"]
        },
        target_surface="day_guidance_card",
        evolution_slice=architect_context_slice,
        hard_cap=6,
        now=NOW,
    )

    assert wired["hard_cap"] <= HARD_CAP_DEFAULT
    assert len(wired["selected_facts"]) <= HARD_CAP_DEFAULT
    assert len(wired["selected_facts"]) <= wired["evolution_ak_cap"]


def test_memory_window_cap_applied(architect_context_slice: dict) -> None:
    pool = [_active()]
    wired = select_knowledge_context_with_evolution_v1(
        pool,
        day_context={"content_keys": ["day.guidance"]},
        target_surface="day_guidance_card",
        evolution_slice=architect_context_slice,
        now=NOW,
    )

    assert wired["evolution_memory_window_days"] == 90


def test_invalid_slice_ignored_with_trace(seeker_context_slice: dict) -> None:
    pool = _pool(2)
    day_context = {"content_keys": ["day.topic0", "day.guidance"]}
    base = select_knowledge_context_v1(
        pool,
        day_context=day_context,
        target_surface="day_guidance_card",
        now=NOW,
    )
    invalid = copy.deepcopy(seeker_context_slice)
    invalid["effect_limits"] = "not-an-object"

    wired = select_knowledge_context_with_evolution_v1(
        pool,
        day_context=day_context,
        target_surface="day_guidance_card",
        evolution_slice=invalid,
        now=NOW,
    )

    assert _selected_ids(wired) == _selected_ids(base)
    assert wired["evolution_slice_applied"] is False
    assert wired["evolution_cap_reason"] == "ignored:invalid_slice_payload"


def test_full_policy_rejected_or_ignored(cd: dict) -> None:
    pool = _pool(2)
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

    wired = select_knowledge_context_with_evolution_v1(
        pool,
        day_context={"content_keys": ["day.topic0", "day.topic1"]},
        target_surface="day_guidance_card",
        evolution_slice=full_policy,
        now=NOW,
    )

    assert wired["evolution_slice_applied"] is False
    assert wired["evolution_cap_reason"] == "ignored:full_policy_not_accepted"


def test_evolution_cannot_increase_selected_facts_beyond_eligible(
    architect_context_slice: dict,
) -> None:
    pool = _pool(3)
    day_context = {"content_keys": ["day.topic0", "day.guidance", "slow"]}
    base = select_knowledge_context_v1(
        pool,
        day_context=day_context,
        target_surface="day_guidance_card",
        now=NOW,
    )
    wired = select_knowledge_context_with_evolution_v1(
        pool,
        day_context=day_context,
        target_surface="day_guidance_card",
        evolution_slice=architect_context_slice,
        now=NOW,
    )

    assert len(wired["selected_facts"]) <= len(base["selected_facts"])


def test_excluded_facts_get_reason_evolution_cap(seeker_context_slice: dict) -> None:
    pool = _pool(3)
    wired = select_knowledge_context_with_evolution_v1(
        pool,
        day_context={"content_keys": ["day.topic0", "day.guidance", "slow"]},
        target_surface="day_guidance_card",
        evolution_slice=seeker_context_slice,
        now=NOW,
    )

    assert wired["selected_facts"] == []
    assert any(
        entry.get("reason") == EXCLUSION_EVOLUTION_CAP
        for entry in wired["excluded_facts"]
        if isinstance(entry, dict)
    )


def test_output_shape_stable(architect_context_slice: dict) -> None:
    pool = [_active()]
    wired = select_knowledge_context_with_evolution_v1(
        pool,
        day_context={"content_keys": ["day.guidance"]},
        target_surface="day_guidance_card",
        evolution_slice=architect_context_slice,
        now=NOW,
    )

    assert wired["contract_version"] == KNOWLEDGE_CONTEXT_SLICE_V1_CONTRACT
    assert set(wired.keys()) == KNOWLEDGE_CONTEXT_SLICE_V1_WITH_EVOLUTION_KEYS
    assert validate_evolution_context_selector_wiring_v1(wired) == []
