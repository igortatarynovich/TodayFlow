"""P1.24 — Hint package application contract tests."""

from __future__ import annotations

import copy

from todayflow_backend.services.day_model_v1_active_knowledge import (
    DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_active_knowledge_hint_package import (
    HINT_PACKAGE_RESULT_CREATED,
    try_build_active_knowledge_hint_package_v1,
)
from todayflow_backend.services.day_model_v1_active_knowledge_runtime_gate import (
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
from todayflow_backend.services.day_model_v1_hint_application import (
    APPLICATION_MODE_ADJUST_TONE,
    APPLICATION_MODE_BOOST,
    APPLICATION_MODE_DELAY,
    APPLICATION_MODE_INCLUDE,
    APPLICATION_MODE_LOWER,
    APPLICATION_RESULT_APPLIED,
    APPLICATION_RESULT_REJECTED,
    CONSUMER_CACHE_REUSE,
    CONSUMER_CONTENT_RANKER,
    CONSUMER_CONTEXT_SELECTOR,
    CONSUMER_PROMPT_BUILDER,
    CONSUMER_SURFACE_PRIORITIZER,
    DAY_HINT_APPLICATION_RESULT_V1_CONTRACT,
    DAY_HINT_APPLICATION_RESULT_V1_KEYS,
    try_apply_hint_package_v1,
    validate_day_hint_application_result_v1,
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


def _hint_package(active, *, surface, requested_usage):
    policy = try_build_active_knowledge_usage_policy_v1(active)["usage_policy"]
    decision = try_decide_active_knowledge_runtime_v1(
        active,
        policy,
        surface=surface,
        requested_usage=requested_usage,
    )
    assert decision["decision"] == "allow"
    outcome = try_build_active_knowledge_hint_package_v1(active, policy, decision)
    assert outcome["result"] == HINT_PACKAGE_RESULT_CREATED
    return outcome["hint_package"]


def _apply(pkg, *, consumer, mode, before=None, after=None):
    before_state = before or {"items": ["a", "b"], "score": 0.5}
    after_state = after or {"items": ["a", "b", "c"], "score": 0.7}
    return try_apply_hint_package_v1(
        pkg,
        consumer=consumer,
        application_mode=mode,
        before_state=before_state,
        after_state=after_state,
    )


def test_context_hint_context_selector_allowed():
    pkg = _hint_package(_active(), surface="day_guidance_card", requested_usage=USAGE_CONTEXT_SELECTION)
    outcome = _apply(pkg, consumer=CONSUMER_CONTEXT_SELECTOR, mode=APPLICATION_MODE_INCLUDE)
    assert outcome["result"] == APPLICATION_RESULT_APPLIED
    result = outcome["application_result"]
    assert result is not None
    assert result["consumer"] == CONSUMER_CONTEXT_SELECTOR
    assert result["hint_type"] == "context"
    assert result["applied"] is True


def test_prompt_hint_prompt_builder_allowed():
    active = _active(
        knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
        claim="responds_to_surface:today_hero",
    )
    pkg = _hint_package(active, surface="day_guidance_card", requested_usage=USAGE_PROMPT_REFINEMENT)
    outcome = _apply(pkg, consumer=CONSUMER_PROMPT_BUILDER, mode=APPLICATION_MODE_ADJUST_TONE)
    assert outcome["result"] == APPLICATION_RESULT_APPLIED
    assert outcome["application_result"]["consumer"] == CONSUMER_PROMPT_BUILDER


def test_cache_hint_cache_reuse_allowed():
    active = _active(
        knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
        claim="responds_to_surface:today_hero",
    )
    pkg = _hint_package(active, surface="cache_layer", requested_usage=USAGE_CACHE_REUSE)
    outcome = _apply(pkg, consumer=CONSUMER_CACHE_REUSE, mode=APPLICATION_MODE_INCLUDE)
    assert outcome["result"] == APPLICATION_RESULT_APPLIED
    assert outcome["application_result"]["consumer"] == CONSUMER_CACHE_REUSE


def test_ranking_hint_content_ranker_allowed():
    pkg = _hint_package(_active(), surface="content_ranker", requested_usage=USAGE_CONTENT_RANKING)
    outcome = _apply(pkg, consumer=CONSUMER_CONTENT_RANKER, mode=APPLICATION_MODE_BOOST)
    assert outcome["result"] == APPLICATION_RESULT_APPLIED
    assert outcome["application_result"]["consumer"] == CONSUMER_CONTENT_RANKER


def test_surface_priority_hint_surface_prioritizer_allowed():
    active = _active(
        knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
        claim="responds_to_surface:today_hero",
    )
    pkg = _hint_package(active, surface="today_hero", requested_usage=USAGE_SURFACE_PRIORITY)
    outcome = _apply(pkg, consumer=CONSUMER_SURFACE_PRIORITIZER, mode=APPLICATION_MODE_DELAY)
    assert outcome["result"] == APPLICATION_RESULT_APPLIED
    assert outcome["application_result"]["consumer"] == CONSUMER_SURFACE_PRIORITIZER


def test_wrong_consumer_rejected():
    pkg = _hint_package(_active(), surface="content_ranker", requested_usage=USAGE_CONTENT_RANKING)
    outcome = _apply(pkg, consumer=CONSUMER_CONTEXT_SELECTOR, mode=APPLICATION_MODE_BOOST)
    assert outcome["result"] == APPLICATION_RESULT_REJECTED
    assert outcome["application_result"] is None


def test_already_applied_hint_rejected():
    pkg = _hint_package(_active(), surface="content_ranker", requested_usage=USAGE_CONTENT_RANKING)
    applied_pkg = copy.deepcopy(pkg)
    applied_pkg["applied"] = True
    outcome = _apply(applied_pkg, consumer=CONSUMER_CONTENT_RANKER, mode=APPLICATION_MODE_BOOST)
    assert outcome["result"] == APPLICATION_RESULT_REJECTED
    assert "already applied" in outcome["reasons"][0]


def test_missing_before_after_hashes_invalid():
    pkg = _hint_package(_active(), surface="content_ranker", requested_usage=USAGE_CONTENT_RANKING)
    outcome = try_apply_hint_package_v1(
        pkg,
        consumer=CONSUMER_CONTENT_RANKER,
        application_mode=APPLICATION_MODE_BOOST,
        before_state={},
        after_state={"score": 0.7},
    )
    assert outcome["result"] == APPLICATION_RESULT_REJECTED

    bad_result = {
        "contract_version": DAY_HINT_APPLICATION_RESULT_V1_CONTRACT,
        "application_id": "happ-test",
        "hint_package_id": pkg["hint_package_id"],
        "consumer": CONSUMER_CONTENT_RANKER,
        "surface": pkg["surface"],
        "hint_type": "ranking",
        "applied": True,
        "application_mode": APPLICATION_MODE_BOOST,
        "influence_level": pkg["influence_level"],
        "before_snapshot_hash": "",
        "after_snapshot_hash": "snap-abc",
        "changes_summary": "ranking:boost:claim=x",
        "traceability": {
            "knowledge_id": pkg["knowledge_id"],
            "runtime_decision_id": pkg["runtime_decision_id"],
            "policy_id": pkg["usage_policy_id"],
        },
        "created_at": "2026-05-31T12:00:00Z",
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_model_update_allowed": False,
    }
    errors = validate_day_hint_application_result_v1(bad_result, hint_package=pkg)
    assert any("before_snapshot_hash" in e for e in errors)


def test_mutation_flags_always_false():
    pkg = _hint_package(_active(), surface="content_ranker", requested_usage=USAGE_CONTENT_RANKING)
    outcome = _apply(pkg, consumer=CONSUMER_CONTENT_RANKER, mode=APPLICATION_MODE_LOWER)
    result = outcome["application_result"]
    assert result["profile_update_allowed"] is False
    assert result["memory_update_allowed"] is False
    assert result["ranking_model_update_allowed"] is False


def test_forbidden_operation_rejected():
    pkg = _hint_package(_active(), surface="content_ranker", requested_usage=USAGE_CONTENT_RANKING)
    outcome = try_apply_hint_package_v1(
        pkg,
        consumer=CONSUMER_CONTENT_RANKER,
        application_mode="change_strategy",
        before_state={"score": 0.5},
        after_state={"score": 0.7},
    )
    assert outcome["result"] == APPLICATION_RESULT_REJECTED
    assert "forbidden" in outcome["reasons"][0]


def test_output_shape_stable():
    pkg = _hint_package(_active(), surface="content_ranker", requested_usage=USAGE_CONTENT_RANKING)
    outcome = _apply(pkg, consumer=CONSUMER_CONTENT_RANKER, mode=APPLICATION_MODE_BOOST)
    result = outcome["application_result"]
    assert result["contract_version"] == DAY_HINT_APPLICATION_RESULT_V1_CONTRACT
    assert set(result.keys()) == set(DAY_HINT_APPLICATION_RESULT_V1_KEYS)
    assert result["before_snapshot_hash"].startswith("snap-")
    assert result["after_snapshot_hash"].startswith("snap-")
    assert validate_day_hint_application_result_v1(result, hint_package=pkg) == []
    assert pkg["applied"] is False
