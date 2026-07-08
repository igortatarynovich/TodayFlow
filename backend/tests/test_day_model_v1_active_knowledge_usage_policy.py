"""P1.21 — Active knowledge usage policy tests."""

from __future__ import annotations

import copy

from todayflow_backend.services.day_model_v1_active_knowledge import (
    DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_active_knowledge_usage_policy import (
    DAY_ACTIVE_KNOWLEDGE_USAGE_POLICY_V1_CONTRACT,
    DAY_ACTIVE_KNOWLEDGE_USAGE_POLICY_V1_KEYS,
    FORBIDDEN_USAGE_TYPES,
    INFLUENCE_HIGH,
    INFLUENCE_LOW,
    INFLUENCE_MEDIUM,
    POLICY_RESULT_CREATED,
    POLICY_RESULT_REJECTED,
    USAGE_CONTENT_RANKING,
    USAGE_CONTEXT_SELECTION,
    USAGE_PROMPT_REFINEMENT,
    USAGE_SURFACE_PRIORITY,
    try_build_active_knowledge_usage_policy_v1,
    validate_day_active_knowledge_usage_policy_v1,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import (
    KNOWLEDGE_TYPE_BEHAVIOR,
    KNOWLEDGE_TYPE_CONTENT_AFFINITY,
    KNOWLEDGE_TYPE_RESPONSE_STYLE,
    KNOWLEDGE_TYPE_TIMING,
)


def _active_knowledge(**overrides):
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


def test_active_knowledge_creates_usage_policy():
    active = _active_knowledge()
    outcome = try_build_active_knowledge_usage_policy_v1(active)
    assert outcome["result"] == POLICY_RESULT_CREATED
    policy = outcome["usage_policy"]
    assert policy is not None
    assert policy["knowledge_id"] == active["knowledge_id"]


def test_non_active_knowledge_rejected():
    active = copy.deepcopy(_active_knowledge())
    active["status"] = "expired"
    outcome = try_build_active_knowledge_usage_policy_v1(active)
    assert outcome["result"] == POLICY_RESULT_REJECTED
    assert outcome["usage_policy"] is None


def test_content_affinity_allowed_context_and_ranking():
    active = _active_knowledge(knowledge_type=KNOWLEDGE_TYPE_CONTENT_AFFINITY)
    policy = try_build_active_knowledge_usage_policy_v1(active)["usage_policy"]
    assert policy is not None
    assert USAGE_CONTEXT_SELECTION in policy["allowed_usages"]
    assert USAGE_CONTENT_RANKING in policy["allowed_usages"]
    assert policy["max_influence_level"] == INFLUENCE_MEDIUM


def test_response_style_allows_prompt_refinement():
    active = _active_knowledge(
        knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
        claim="responds_to_surface:today_hero",
    )
    policy = try_build_active_knowledge_usage_policy_v1(active)["usage_policy"]
    assert policy is not None
    assert USAGE_PROMPT_REFINEMENT in policy["allowed_usages"]
    assert USAGE_CONTEXT_SELECTION in policy["allowed_usages"]


def test_timing_allows_context_and_surface_priority():
    active = _active_knowledge(
        knowledge_type=KNOWLEDGE_TYPE_TIMING,
        claim="responds_to_tempo:steady",
    )
    policy = try_build_active_knowledge_usage_policy_v1(active)["usage_policy"]
    assert policy is not None
    assert USAGE_CONTEXT_SELECTION in policy["allowed_usages"]
    assert USAGE_SURFACE_PRIORITY in policy["allowed_usages"]


def test_forbidden_usages_always_present():
    policy = try_build_active_knowledge_usage_policy_v1(_active_knowledge())["usage_policy"]
    assert policy is not None
    assert FORBIDDEN_USAGE_TYPES.issubset(set(policy["forbidden_usages"]))


def test_mutation_flags_always_false():
    policy = try_build_active_knowledge_usage_policy_v1(_active_knowledge())["usage_policy"]
    assert policy is not None
    assert policy["profile_update_allowed"] is False
    assert policy["memory_update_allowed"] is False
    assert policy["ranking_update_allowed"] is False


def test_requires_runtime_gate_always_true():
    policy = try_build_active_knowledge_usage_policy_v1(_active_knowledge())["usage_policy"]
    assert policy is not None
    assert policy["requires_runtime_gate"] is True


def test_high_influence_rejected():
    policy = try_build_active_knowledge_usage_policy_v1(_active_knowledge())["usage_policy"]
    assert policy is not None
    broken = copy.deepcopy(policy)
    broken["max_influence_level"] = INFLUENCE_HIGH
    assert "high influence not allowed" in validate_day_active_knowledge_usage_policy_v1(broken)


def test_output_shape_stable():
    active = _active_knowledge()
    policy = try_build_active_knowledge_usage_policy_v1(active)["usage_policy"]
    assert policy is not None
    assert policy["contract_version"] == DAY_ACTIVE_KNOWLEDGE_USAGE_POLICY_V1_CONTRACT
    assert set(policy.keys()) == set(DAY_ACTIVE_KNOWLEDGE_USAGE_POLICY_V1_KEYS)
    assert validate_day_active_knowledge_usage_policy_v1(policy, active_knowledge=active) == []


def test_risk_claim_capped_at_low_influence():
    active = _active_knowledge(
        knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
        claim="risk_response_tolerance:positive",
    )
    policy = try_build_active_knowledge_usage_policy_v1(active)["usage_policy"]
    assert policy is not None
    assert policy["max_influence_level"] == INFLUENCE_LOW


def test_behavior_influence_medium():
    active = _active_knowledge(
        knowledge_type=KNOWLEDGE_TYPE_BEHAVIOR,
        claim="responds_to_action_mode:complete_task",
    )
    policy = try_build_active_knowledge_usage_policy_v1(active)["usage_policy"]
    assert policy is not None
    assert policy["max_influence_level"] == INFLUENCE_MEDIUM
