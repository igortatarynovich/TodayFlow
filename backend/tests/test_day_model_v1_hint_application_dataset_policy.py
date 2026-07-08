"""P1.25 — Hint application dataset policy tests."""

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
    CONSUMER_CACHE_REUSE,
    CONSUMER_CONTENT_RANKER,
    CONSUMER_CONTEXT_SELECTOR,
    CONSUMER_PROMPT_BUILDER,
    CONSUMER_SURFACE_PRIORITIZER,
    try_apply_hint_package_v1,
)
from todayflow_backend.services.day_model_v1_hint_application_dataset_policy import (
    DATASET_POLICY_RESULT_CREATED,
    DATASET_STATUS_CANDIDATE,
    DATASET_STATUS_REJECTED,
    DATASET_STATUS_RUNTIME_TRACE_ONLY,
    DAY_HINT_APPLICATION_DATASET_POLICY_V1_CONTRACT,
    DAY_HINT_APPLICATION_DATASET_POLICY_V1_KEYS,
    REASON_FORBIDDEN_OPERATION,
    REASON_INSUFFICIENT_REUSE_EVIDENCE,
    REASON_MISSING_DOWNSTREAM_REACTION,
    REASON_MISSING_SNAPSHOT_TRACE,
    REASON_MISSING_USER_REACTION,
    REASON_MUTATION_ATTEMPT,
    REASON_VALID_APPLICATION,
    try_build_hint_application_dataset_policy_v1,
    validate_day_hint_application_dataset_policy_v1,
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


def _pipeline(active, *, surface, requested_usage, consumer, mode):
    policy = try_build_active_knowledge_usage_policy_v1(active)["usage_policy"]
    decision = try_decide_active_knowledge_runtime_v1(
        active,
        policy,
        surface=surface,
        requested_usage=requested_usage,
    )
    assert decision["decision"] == "allow"
    pkg_outcome = try_build_active_knowledge_hint_package_v1(active, policy, decision)
    assert pkg_outcome["result"] == HINT_PACKAGE_RESULT_CREATED
    pkg = pkg_outcome["hint_package"]
    app_outcome = try_apply_hint_package_v1(
        pkg,
        consumer=consumer,
        application_mode=mode,
        before_state={"items": ["a"], "score": 0.5},
        after_state={"items": ["a", "b"], "score": 0.7},
    )
    assert app_outcome["result"] == APPLICATION_RESULT_APPLIED
    return active, pkg, app_outcome["application_result"]


def _policy(active, app_result, pkg, **kwargs):
    return try_build_hint_application_dataset_policy_v1(
        app_result,
        pkg,
        active,
        **kwargs,
    )


def test_valid_prompt_hint_application_candidate_requires_review():
    active, pkg, app = _pipeline(
        _active(
            knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
            claim="responds_to_surface:today_hero",
        ),
        surface="day_guidance_card",
        requested_usage=USAGE_PROMPT_REFINEMENT,
        consumer=CONSUMER_PROMPT_BUILDER,
        mode=APPLICATION_MODE_ADJUST_TONE,
    )
    outcome = _policy(active, app, pkg)
    assert outcome["result"] == DATASET_POLICY_RESULT_CREATED
    pol = outcome["dataset_policy"]
    assert pol["dataset_status"] == DATASET_STATUS_CANDIDATE
    assert pol["candidate_reason"] == REASON_VALID_APPLICATION
    assert pol["requires_review"] is True
    assert pol["requires_reaction_evidence"] is True
    assert pol["requires_quality_evaluation"] is True


def test_valid_context_hint_candidate():
    active, pkg, app = _pipeline(
        _active(),
        surface="day_guidance_card",
        requested_usage=USAGE_CONTEXT_SELECTION,
        consumer=CONSUMER_CONTEXT_SELECTOR,
        mode=APPLICATION_MODE_INCLUDE,
    )
    outcome = _policy(active, app, pkg)
    pol = outcome["dataset_policy"]
    assert pol["dataset_status"] == DATASET_STATUS_CANDIDATE
    assert pol["requires_review"] is False


def test_cache_hint_runtime_trace_only_without_reuse_evidence():
    active, pkg, app = _pipeline(
        _active(
            knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
            claim="responds_to_surface:today_hero",
        ),
        surface="cache_layer",
        requested_usage=USAGE_CACHE_REUSE,
        consumer=CONSUMER_CACHE_REUSE,
        mode=APPLICATION_MODE_INCLUDE,
    )
    outcome = _policy(active, app, pkg, reuse_success_evidence=False)
    pol = outcome["dataset_policy"]
    assert pol["dataset_status"] == DATASET_STATUS_RUNTIME_TRACE_ONLY
    assert pol["candidate_reason"] == REASON_INSUFFICIENT_REUSE_EVIDENCE


def test_ranking_hint_runtime_trace_only_without_downstream_reaction():
    active, pkg, app = _pipeline(
        _active(),
        surface="content_ranker",
        requested_usage=USAGE_CONTENT_RANKING,
        consumer=CONSUMER_CONTENT_RANKER,
        mode=APPLICATION_MODE_BOOST,
    )
    outcome = _policy(active, app, pkg, downstream_reaction_evidence=False)
    pol = outcome["dataset_policy"]
    assert pol["dataset_status"] == DATASET_STATUS_RUNTIME_TRACE_ONLY
    assert pol["candidate_reason"] == REASON_MISSING_DOWNSTREAM_REACTION


def test_surface_priority_runtime_trace_only_without_reaction():
    active, pkg, app = _pipeline(
        _active(
            knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
            claim="responds_to_surface:today_hero",
        ),
        surface="today_hero",
        requested_usage=USAGE_SURFACE_PRIORITY,
        consumer=CONSUMER_SURFACE_PRIORITIZER,
        mode=APPLICATION_MODE_DELAY,
    )
    outcome = _policy(active, app, pkg, user_reaction_evidence=False)
    pol = outcome["dataset_policy"]
    assert pol["dataset_status"] == DATASET_STATUS_RUNTIME_TRACE_ONLY
    assert pol["candidate_reason"] == REASON_MISSING_USER_REACTION


def test_missing_before_after_hash_rejected():
    active, pkg, app = _pipeline(
        _active(),
        surface="content_ranker",
        requested_usage=USAGE_CONTENT_RANKING,
        consumer=CONSUMER_CONTENT_RANKER,
        mode=APPLICATION_MODE_LOWER,
    )
    bad_app = copy.deepcopy(app)
    bad_app["before_snapshot_hash"] = ""
    outcome = _policy(active, bad_app, pkg)
    pol = outcome["dataset_policy"]
    assert pol["dataset_status"] == DATASET_STATUS_REJECTED
    assert pol["candidate_reason"] == REASON_MISSING_SNAPSHOT_TRACE


def test_forbidden_operation_rejected():
    active, pkg, app = _pipeline(
        _active(),
        surface="content_ranker",
        requested_usage=USAGE_CONTENT_RANKING,
        consumer=CONSUMER_CONTENT_RANKER,
        mode=APPLICATION_MODE_BOOST,
    )
    bad_app = copy.deepcopy(app)
    bad_app["application_mode"] = "change_strategy"
    outcome = _policy(active, bad_app, pkg)
    pol = outcome["dataset_policy"]
    assert pol["dataset_status"] == DATASET_STATUS_REJECTED
    assert pol["candidate_reason"] == REASON_FORBIDDEN_OPERATION


def test_mutation_attempt_rejected():
    active, pkg, app = _pipeline(
        _active(),
        surface="content_ranker",
        requested_usage=USAGE_CONTENT_RANKING,
        consumer=CONSUMER_CONTENT_RANKER,
        mode=APPLICATION_MODE_BOOST,
    )
    bad_app = copy.deepcopy(app)
    bad_app["profile_update_allowed"] = True
    outcome = _policy(active, bad_app, pkg)
    pol = outcome["dataset_policy"]
    assert pol["dataset_status"] == DATASET_STATUS_REJECTED
    assert pol["candidate_reason"] == REASON_MUTATION_ATTEMPT


def test_training_use_allowed_always_false():
    active, pkg, app = _pipeline(
        _active(),
        surface="day_guidance_card",
        requested_usage=USAGE_CONTEXT_SELECTION,
        consumer=CONSUMER_CONTEXT_SELECTOR,
        mode=APPLICATION_MODE_INCLUDE,
    )
    outcome = _policy(active, app, pkg)
    assert outcome["dataset_policy"]["training_use_allowed"] is False


def test_output_shape_stable():
    active, pkg, app = _pipeline(
        _active(),
        surface="day_guidance_card",
        requested_usage=USAGE_CONTEXT_SELECTION,
        consumer=CONSUMER_CONTEXT_SELECTOR,
        mode=APPLICATION_MODE_INCLUDE,
    )
    outcome = _policy(active, app, pkg)
    pol = outcome["dataset_policy"]
    assert pol["contract_version"] == DAY_HINT_APPLICATION_DATASET_POLICY_V1_CONTRACT
    assert set(pol.keys()) == set(DAY_HINT_APPLICATION_DATASET_POLICY_V1_KEYS)
    assert validate_day_hint_application_dataset_policy_v1(
        pol,
        application_result=app,
        hint_package=pkg,
        active_knowledge=active,
    ) == []
