"""P1.23 — Active knowledge hint package tests."""

from __future__ import annotations

import copy

from todayflow_backend.services.day_model_v1_active_knowledge import (
    DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_active_knowledge_hint_package import (
    DAY_ACTIVE_KNOWLEDGE_HINT_PACKAGE_V1_CONTRACT,
    DAY_ACTIVE_KNOWLEDGE_HINT_PACKAGE_V1_KEYS,
    FORBIDDEN_OPERATIONS,
    HINT_PACKAGE_RESULT_CREATED,
    HINT_PACKAGE_RESULT_REJECTED,
    HINT_TYPE_CACHE,
    HINT_TYPE_CONTEXT,
    HINT_TYPE_PROMPT,
    HINT_TYPE_RANKING,
    HINT_TYPE_SURFACE_PRIORITY,
    try_build_active_knowledge_hint_package_v1,
    validate_day_active_knowledge_hint_package_v1,
)
from todayflow_backend.services.day_model_v1_active_knowledge_runtime_gate import (
    DECISION_DENY,
    try_decide_active_knowledge_runtime_v1,
)
from todayflow_backend.services.day_model_v1_active_knowledge_usage_policy import (
    USAGE_CACHE_REUSE,
    USAGE_CONTENT_RANKING,
    USAGE_CONTEXT_SELECTION,
    USAGE_PROMPT_REFINEMENT,
    USAGE_SURFACE_PRIORITY,
    try_build_active_knowledge_usage_policy_v1,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import (
    KNOWLEDGE_TYPE_CONTENT_AFFINITY,
    KNOWLEDGE_TYPE_RESPONSE_STYLE,
)


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


def _policy(active):
    return try_build_active_knowledge_usage_policy_v1(active)["usage_policy"]


def _allow(active, *, surface, requested_usage):
    policy = _policy(active)
    decision = try_decide_active_knowledge_runtime_v1(
        active,
        policy,
        surface=surface,
        requested_usage=requested_usage,
    )
    assert decision["decision"] == "allow"
    return policy, decision


def _build(active, surface, requested_usage):
    policy, decision = _allow(active, surface=surface, requested_usage=requested_usage)
    return try_build_active_knowledge_hint_package_v1(active, policy, decision)


def test_runtime_allow_creates_hint_package():
    outcome = _build(_active(), "content_ranker", USAGE_CONTENT_RANKING)
    assert outcome["result"] == HINT_PACKAGE_RESULT_CREATED
    pkg = outcome["hint_package"]
    assert pkg is not None
    assert pkg["status"] == "ready"
    assert pkg["applied"] is False


def test_runtime_deny_no_package():
    active = _active()
    policy = _policy(active)
    decision = try_decide_active_knowledge_runtime_v1(
        active,
        policy,
        surface="today_hero",
        requested_usage=USAGE_CONTENT_RANKING,
    )
    assert decision["decision"] == DECISION_DENY
    outcome = try_build_active_knowledge_hint_package_v1(active, policy, decision)
    assert outcome["result"] == HINT_PACKAGE_RESULT_REJECTED
    assert outcome["hint_package"] is None


def test_context_selection_maps_to_context_hint():
    pkg = _build(_active(), "day_guidance_card", USAGE_CONTEXT_SELECTION)["hint_package"]
    assert pkg is not None
    assert pkg["hint_type"] == HINT_TYPE_CONTEXT
    assert "include" in pkg["allowed_operations"]


def test_prompt_refinement_maps_to_prompt_hint():
    active = _active(
        knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
        claim="responds_to_surface:today_hero",
    )
    pkg = _build(active, "day_guidance_card", USAGE_PROMPT_REFINEMENT)["hint_package"]
    assert pkg is not None
    assert pkg["hint_type"] == HINT_TYPE_PROMPT
    assert "adjust_tone" in pkg["allowed_operations"]


def test_cache_reuse_maps_to_cache_hint():
    active = _active(
        knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
        claim="responds_to_surface:today_hero",
    )
    pkg = _build(active, "cache_layer", USAGE_CACHE_REUSE)["hint_package"]
    assert pkg is not None
    assert pkg["hint_type"] == HINT_TYPE_CACHE


def test_content_ranking_maps_to_ranking_hint():
    pkg = _build(_active(), "content_ranker", USAGE_CONTENT_RANKING)["hint_package"]
    assert pkg is not None
    assert pkg["hint_type"] == HINT_TYPE_RANKING


def test_surface_priority_maps_to_surface_priority_hint():
    active = _active(
        knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
        claim="responds_to_surface:today_hero",
    )
    pkg = _build(active, "today_hero", USAGE_SURFACE_PRIORITY)["hint_package"]
    assert pkg is not None
    assert pkg["hint_type"] == HINT_TYPE_SURFACE_PRIORITY


def test_forbidden_operations_always_present():
    pkg = _build(_active(), "content_ranker", USAGE_CONTENT_RANKING)["hint_package"]
    assert pkg is not None
    assert FORBIDDEN_OPERATIONS.issubset(set(pkg["forbidden_operations"]))


def test_applied_always_false():
    pkg = _build(_active(), "content_ranker", USAGE_CONTENT_RANKING)["hint_package"]
    assert pkg is not None
    assert pkg["applied"] is False


def test_sensitive_and_prose_claim_rejected():
    sensitive = _active(claim="personality_trait:disciplined")
    policy = _policy(_active())
    policy = copy.deepcopy(policy)
    policy["claim"] = sensitive["claim"]
    decision = try_decide_active_knowledge_runtime_v1(
        sensitive,
        policy,
        surface="content_ranker",
        requested_usage=USAGE_CONTENT_RANKING,
    )
    if decision["decision"] == "allow":
        outcome = try_build_active_knowledge_hint_package_v1(sensitive, policy, decision)
        assert outcome["result"] == HINT_PACKAGE_RESULT_REJECTED
    else:
        assert decision["decision"] == DECISION_DENY

    prose = _active(claim="user prefers morning guidance")
    _, allow_decision = _allow(_active(), surface="content_ranker", requested_usage=USAGE_CONTENT_RANKING)
    outcome = try_build_active_knowledge_hint_package_v1(prose, policy, allow_decision)
    assert outcome["result"] == HINT_PACKAGE_RESULT_REJECTED
    assert outcome["hint_package"] is None


def test_output_shape_stable():
    active = _active()
    policy, decision = _allow(active, surface="content_ranker", requested_usage=USAGE_CONTENT_RANKING)
    outcome = try_build_active_knowledge_hint_package_v1(active, policy, decision)
    pkg = outcome["hint_package"]
    assert pkg is not None
    assert pkg["contract_version"] == DAY_ACTIVE_KNOWLEDGE_HINT_PACKAGE_V1_CONTRACT
    assert set(pkg.keys()) == set(DAY_ACTIVE_KNOWLEDGE_HINT_PACKAGE_V1_KEYS)
    assert validate_day_active_knowledge_hint_package_v1(
        pkg,
        active_knowledge=active,
        usage_policy=policy,
        runtime_decision=decision,
    ) == []
