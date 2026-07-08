"""P1.22 — Active knowledge runtime gate tests."""

from __future__ import annotations

import copy
from datetime import UTC, datetime

from todayflow_backend.services.day_model_v1_active_knowledge import (
    DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_active_knowledge_runtime_gate import (
    DAY_ACTIVE_KNOWLEDGE_RUNTIME_DECISION_V1_CONTRACT,
    DAY_ACTIVE_KNOWLEDGE_RUNTIME_DECISION_V1_KEYS,
    DECISION_ALLOW,
    DECISION_DENY,
    DENY_EXPIRED_KNOWLEDGE,
    DENY_INFLUENCE_TOO_HIGH,
    DENY_KNOWLEDGE_NOT_ACTIVE,
    DENY_SURFACE_NOT_COMPATIBLE,
    DENY_USAGE_FORBIDDEN,
    DENY_USAGE_NOT_ALLOWED,
    INFLUENCE_LOW,
    INFLUENCE_MEDIUM,
    try_decide_active_knowledge_runtime_v1,
    validate_day_active_knowledge_runtime_decision_v1,
)
from todayflow_backend.services.day_model_v1_active_knowledge_usage_policy import (
    USAGE_CONTENT_RANKING,
    USAGE_CONTEXT_SELECTION,
    USAGE_PROMPT_REFINEMENT,
    try_build_active_knowledge_usage_policy_v1,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import (
    KNOWLEDGE_TYPE_CONTENT_AFFINITY,
    KNOWLEDGE_TYPE_RESPONSE_STYLE,
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


def _policy_for(active):
    outcome = try_build_active_knowledge_usage_policy_v1(active)
    assert outcome["usage_policy"] is not None
    return outcome["usage_policy"]


def test_allowed_usage_compatible_surface_allow():
    active = _active_knowledge()
    policy = _policy_for(active)
    decision = try_decide_active_knowledge_runtime_v1(
        active,
        policy,
        surface="content_ranker",
        requested_usage=USAGE_CONTENT_RANKING,
        requested_influence=INFLUENCE_MEDIUM,
    )
    assert decision["decision"] == DECISION_ALLOW
    assert decision["allowed_influence_level"] == INFLUENCE_MEDIUM


def test_usage_not_in_policy_deny():
    active = _active_knowledge(
        knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
        claim="responds_to_surface:today_hero",
    )
    policy = _policy_for(active)
    decision = try_decide_active_knowledge_runtime_v1(
        active,
        policy,
        surface="reflection_card",
        requested_usage=USAGE_CONTENT_RANKING,
    )
    assert decision["decision"] == DECISION_DENY
    assert decision["reason"] == DENY_USAGE_NOT_ALLOWED


def test_forbidden_usage_deny():
    active = _active_knowledge()
    policy = _policy_for(active)
    broken_policy = copy.deepcopy(policy)
    broken_policy["forbidden_usages"] = list(broken_policy["forbidden_usages"]) + [
        USAGE_CONTENT_RANKING
    ]
    decision = try_decide_active_knowledge_runtime_v1(
        active,
        broken_policy,
        surface="content_ranker",
        requested_usage=USAGE_CONTENT_RANKING,
    )
    assert decision["decision"] == DECISION_DENY
    assert decision["reason"] == DENY_USAGE_FORBIDDEN


def test_influence_above_cap_deny():
    active = _active_knowledge(
        knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
        claim="risk_response_tolerance:positive",
    )
    policy = _policy_for(active)
    assert policy["max_influence_level"] == INFLUENCE_LOW
    decision = try_decide_active_knowledge_runtime_v1(
        active,
        policy,
        surface="today_hero",
        requested_usage="surface_priority_hint",
        requested_influence=INFLUENCE_MEDIUM,
    )
    assert decision["decision"] == DECISION_DENY
    assert decision["reason"] == DENY_INFLUENCE_TOO_HIGH


def test_incompatible_surface_deny():
    active = _active_knowledge()
    policy = _policy_for(active)
    decision = try_decide_active_knowledge_runtime_v1(
        active,
        policy,
        surface="today_hero",
        requested_usage=USAGE_CONTENT_RANKING,
    )
    assert decision["decision"] == DECISION_DENY
    assert decision["reason"] == DENY_SURFACE_NOT_COMPATIBLE


def test_expired_knowledge_deny():
    active = _active_knowledge(expires_at="2026-05-01T12:00:00Z")
    policy = _policy_for(active)
    decision = try_decide_active_knowledge_runtime_v1(
        active,
        policy,
        surface="content_ranker",
        requested_usage=USAGE_CONTENT_RANKING,
        now=datetime(2026, 5, 31, 12, 0, 0, tzinfo=UTC),
    )
    assert decision["decision"] == DECISION_DENY
    assert decision["reason"] == DENY_EXPIRED_KNOWLEDGE


def test_non_active_knowledge_deny():
    active = _active_knowledge(status="revoked")
    policy = _policy_for(_active_knowledge())
    decision = try_decide_active_knowledge_runtime_v1(
        active,
        policy,
        surface="content_ranker",
        requested_usage=USAGE_CONTENT_RANKING,
    )
    assert decision["decision"] == DECISION_DENY
    assert decision["reason"] == DENY_KNOWLEDGE_NOT_ACTIVE


def test_sensitive_claim_deny():
    active = _active_knowledge(claim="personality_trait:disciplined")
    policy = copy.deepcopy(_policy_for(_active_knowledge()))
    policy["claim"] = active["claim"]
    decision = try_decide_active_knowledge_runtime_v1(
        active,
        policy,
        surface="content_ranker",
        requested_usage=USAGE_CONTENT_RANKING,
    )
    assert decision["decision"] == DECISION_DENY
    assert decision["reason"] in {"invalid_claim", "sensitive_claim"}


def test_mutation_flags_always_false():
    active = _active_knowledge()
    policy = _policy_for(active)
    decision = try_decide_active_knowledge_runtime_v1(
        active,
        policy,
        surface="content_ranker",
        requested_usage=USAGE_CONTENT_RANKING,
    )
    assert decision["profile_update_allowed"] is False
    assert decision["memory_update_allowed"] is False
    assert decision["ranking_update_allowed"] is False


def test_output_shape_stable():
    active = _active_knowledge(
        knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
        claim="responds_to_surface:today_hero",
    )
    policy = _policy_for(active)
    decision = try_decide_active_knowledge_runtime_v1(
        active,
        policy,
        surface="day_guidance_card",
        requested_usage=USAGE_PROMPT_REFINEMENT,
    )
    assert decision["contract_version"] == DAY_ACTIVE_KNOWLEDGE_RUNTIME_DECISION_V1_CONTRACT
    assert set(decision.keys()) == set(DAY_ACTIVE_KNOWLEDGE_RUNTIME_DECISION_V1_KEYS)
    assert decision["traceability"]["knowledge_id"] == active["knowledge_id"]
    assert validate_day_active_knowledge_runtime_decision_v1(
        decision, active_knowledge=active, usage_policy=policy
    ) == []


def test_guidance_card_context_selection_allow():
    active = _active_knowledge()
    policy = _policy_for(active)
    decision = try_decide_active_knowledge_runtime_v1(
        active,
        policy,
        surface="day_guidance_card",
        requested_usage=USAGE_CONTEXT_SELECTION,
    )
    assert decision["decision"] == DECISION_ALLOW
