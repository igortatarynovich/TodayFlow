"""P1.26 — Dataset candidate promotion gate tests."""

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
    USAGE_CONTENT_RANKING,
    USAGE_CONTEXT_SELECTION,
    USAGE_PROMPT_REFINEMENT,
    try_build_active_knowledge_usage_policy_v1,
)
from todayflow_backend.services.day_model_v1_hint_application import (
    APPLICATION_MODE_ADJUST_TONE,
    APPLICATION_MODE_BOOST,
    APPLICATION_MODE_INCLUDE,
    APPLICATION_RESULT_APPLIED,
    CONSUMER_CONTENT_RANKER,
    CONSUMER_CONTEXT_SELECTOR,
    CONSUMER_PROMPT_BUILDER,
    try_apply_hint_package_v1,
)
from todayflow_backend.services.day_model_v1_hint_application_dataset_policy import (
    DATASET_POLICY_RESULT_CREATED,
    DATASET_STATUS_CANDIDATE,
    DATASET_STATUS_REJECTED,
    DATASET_STATUS_RUNTIME_TRACE_ONLY,
    try_build_hint_application_dataset_policy_v1,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import (
    KNOWLEDGE_TYPE_CONTENT_AFFINITY,
    KNOWLEDGE_TYPE_RESPONSE_STYLE,
)
from todayflow_backend.services.day_model_v1_training_example_approval import (
    APPROVAL_STATUS_APPROVED,
    APPROVAL_STATUS_NOT_READY,
    APPROVAL_STATUS_REJECTED,
    DAY_TRAINING_EXAMPLE_APPROVAL_V1_CONTRACT,
    DAY_TRAINING_EXAMPLE_APPROVAL_V1_KEYS,
    PROMOTION_RESULT_APPROVED,
    PROMOTION_RESULT_NOT_READY,
    PROMOTION_RESULT_REJECTED,
    REASON_ALL_GATES_PASSED,
    REASON_DATASET_POLICY_REJECTED,
    REASON_FORBIDDEN_OPERATION,
    REASON_MUTATION_ATTEMPT,
    REASON_MISSING_REACTION_EVIDENCE,
    REASON_QUALITY_NOT_PASSED,
    REASON_REVIEW_NOT_APPROVED,
    REASON_RUNTIME_TRACE_NOT_PROMOTABLE,
    try_promote_dataset_candidate_v1,
    validate_day_training_example_approval_v1,
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


def _full_chain(active, *, surface, requested_usage, consumer, mode, **policy_kwargs):
    usage_policy = try_build_active_knowledge_usage_policy_v1(active)["usage_policy"]
    decision = try_decide_active_knowledge_runtime_v1(
        active,
        usage_policy,
        surface=surface,
        requested_usage=requested_usage,
    )
    assert decision["decision"] == "allow"
    pkg = try_build_active_knowledge_hint_package_v1(active, usage_policy, decision)[
        "hint_package"
    ]
    app = try_apply_hint_package_v1(
        pkg,
        consumer=consumer,
        application_mode=mode,
        before_state={"items": ["a"], "score": 0.5},
        after_state={"items": ["a", "b"], "score": 0.7},
    )["application_result"]
    ds = try_build_hint_application_dataset_policy_v1(
        app,
        pkg,
        active,
        **policy_kwargs,
    )["dataset_policy"]
    return active, pkg, app, ds


def _promote(active, pkg, app, ds, **kwargs):
    return try_promote_dataset_candidate_v1(
        ds,
        app,
        pkg,
        active,
        **kwargs,
    )


def test_candidate_with_all_evidence_approved():
    active, pkg, app, ds = _full_chain(
        _active(),
        surface="day_guidance_card",
        requested_usage=USAGE_CONTEXT_SELECTION,
        consumer=CONSUMER_CONTEXT_SELECTOR,
        mode=APPLICATION_MODE_INCLUDE,
    )
    assert ds["dataset_status"] == DATASET_STATUS_CANDIDATE
    outcome = _promote(
        active,
        pkg,
        app,
        ds,
        reaction_evidence={"present": True, "reaction_type": "positive_engagement"},
    )
    assert outcome["result"] == PROMOTION_RESULT_APPROVED
    ex = outcome["training_example"]
    assert ex["approval_status"] == APPROVAL_STATUS_APPROVED
    assert ex["approval_reason"] == REASON_ALL_GATES_PASSED
    assert ex["training_use_allowed"] is True


def test_runtime_trace_only_rejected():
    active, pkg, app, ds = _full_chain(
        _active(),
        surface="content_ranker",
        requested_usage=USAGE_CONTENT_RANKING,
        consumer=CONSUMER_CONTENT_RANKER,
        mode=APPLICATION_MODE_BOOST,
        downstream_reaction_evidence=False,
    )
    assert ds["dataset_status"] == DATASET_STATUS_RUNTIME_TRACE_ONLY
    outcome = _promote(
        active,
        pkg,
        app,
        ds,
        reaction_evidence={"present": True},
        quality_evidence={"passed": True},
        review_approved=True,
    )
    assert outcome["result"] == PROMOTION_RESULT_REJECTED
    assert outcome["training_example"]["approval_status"] == APPROVAL_STATUS_REJECTED
    assert outcome["training_example"]["approval_reason"] == REASON_RUNTIME_TRACE_NOT_PROMOTABLE


def test_rejected_policy_rejected():
    active, pkg, app, ds = _full_chain(
        _active(),
        surface="content_ranker",
        requested_usage=USAGE_CONTENT_RANKING,
        consumer=CONSUMER_CONTENT_RANKER,
        mode=APPLICATION_MODE_BOOST,
    )
    bad_app = copy.deepcopy(app)
    bad_app["application_mode"] = "change_strategy"
    ds_outcome = try_build_hint_application_dataset_policy_v1(bad_app, pkg, active)
    ds = ds_outcome["dataset_policy"]
    assert ds["dataset_status"] == DATASET_STATUS_REJECTED
    outcome = _promote(active, pkg, bad_app, ds)
    assert outcome["result"] == PROMOTION_RESULT_REJECTED
    assert outcome["training_example"]["approval_reason"] == REASON_DATASET_POLICY_REJECTED


def test_missing_reaction_evidence_not_ready():
    active, pkg, app, ds = _full_chain(
        _active(),
        surface="day_guidance_card",
        requested_usage=USAGE_CONTEXT_SELECTION,
        consumer=CONSUMER_CONTEXT_SELECTOR,
        mode=APPLICATION_MODE_INCLUDE,
    )
    outcome = _promote(active, pkg, app, ds, reaction_evidence=None)
    assert outcome["result"] == PROMOTION_RESULT_NOT_READY
    assert outcome["training_example"]["approval_status"] == APPROVAL_STATUS_NOT_READY
    assert outcome["training_example"]["approval_reason"] == REASON_MISSING_REACTION_EVIDENCE


def test_missing_quality_evaluation_not_ready():
    active, pkg, app, ds = _full_chain(
        _active(
            knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
            claim="responds_to_surface:today_hero",
        ),
        surface="day_guidance_card",
        requested_usage=USAGE_PROMPT_REFINEMENT,
        consumer=CONSUMER_PROMPT_BUILDER,
        mode=APPLICATION_MODE_ADJUST_TONE,
    )
    outcome = _promote(
        active,
        pkg,
        app,
        ds,
        reaction_evidence={"present": True, "reaction_type": "completed_read"},
        quality_evidence=None,
        review_approved=True,
    )
    assert outcome["result"] == PROMOTION_RESULT_NOT_READY
    assert outcome["training_example"]["approval_reason"] == REASON_QUALITY_NOT_PASSED


def test_review_required_not_approved_not_ready():
    active, pkg, app, ds = _full_chain(
        _active(
            knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
            claim="responds_to_surface:today_hero",
        ),
        surface="day_guidance_card",
        requested_usage=USAGE_PROMPT_REFINEMENT,
        consumer=CONSUMER_PROMPT_BUILDER,
        mode=APPLICATION_MODE_ADJUST_TONE,
    )
    outcome = _promote(
        active,
        pkg,
        app,
        ds,
        reaction_evidence={"present": True, "reaction_type": "completed_read"},
        quality_evidence={"passed": True, "score": 0.9},
        review_approved=False,
    )
    assert outcome["result"] == PROMOTION_RESULT_NOT_READY
    assert outcome["training_example"]["approval_reason"] == REASON_REVIEW_NOT_APPROVED


def test_forbidden_operation_rejected():
    active, pkg, app, ds = _full_chain(
        _active(),
        surface="day_guidance_card",
        requested_usage=USAGE_CONTEXT_SELECTION,
        consumer=CONSUMER_CONTEXT_SELECTOR,
        mode=APPLICATION_MODE_INCLUDE,
    )
    bad_app = copy.deepcopy(app)
    bad_app["application_mode"] = "change_strategy"
    outcome = _promote(
        active,
        pkg,
        bad_app,
        ds,
        reaction_evidence={"present": True},
    )
    assert outcome["result"] == PROMOTION_RESULT_REJECTED
    assert outcome["training_example"]["approval_reason"] == REASON_FORBIDDEN_OPERATION


def test_mutation_attempt_rejected():
    active, pkg, app, ds = _full_chain(
        _active(),
        surface="day_guidance_card",
        requested_usage=USAGE_CONTEXT_SELECTION,
        consumer=CONSUMER_CONTEXT_SELECTOR,
        mode=APPLICATION_MODE_INCLUDE,
    )
    bad_app = copy.deepcopy(app)
    bad_app["memory_update_allowed"] = True
    outcome = _promote(
        active,
        pkg,
        bad_app,
        ds,
        reaction_evidence={"present": True},
    )
    assert outcome["result"] == PROMOTION_RESULT_REJECTED
    assert outcome["training_example"]["approval_reason"] == REASON_MUTATION_ATTEMPT


def test_training_use_allowed_true_only_when_approved():
    active, pkg, app, ds = _full_chain(
        _active(),
        surface="day_guidance_card",
        requested_usage=USAGE_CONTEXT_SELECTION,
        consumer=CONSUMER_CONTEXT_SELECTOR,
        mode=APPLICATION_MODE_INCLUDE,
    )
    not_ready = _promote(active, pkg, app, ds)
    assert not_ready["training_example"]["training_use_allowed"] is False

    approved = _promote(
        active,
        pkg,
        app,
        ds,
        reaction_evidence={"present": True, "reaction_type": "positive_engagement"},
    )
    assert approved["training_example"]["training_use_allowed"] is True


def test_output_shape_stable():
    active, pkg, app, ds = _full_chain(
        _active(),
        surface="day_guidance_card",
        requested_usage=USAGE_CONTEXT_SELECTION,
        consumer=CONSUMER_CONTEXT_SELECTOR,
        mode=APPLICATION_MODE_INCLUDE,
    )
    outcome = _promote(
        active,
        pkg,
        app,
        ds,
        reaction_evidence={"present": True, "reaction_type": "positive_engagement"},
    )
    ex = outcome["training_example"]
    assert ex["contract_version"] == DAY_TRAINING_EXAMPLE_APPROVAL_V1_CONTRACT
    assert set(ex.keys()) == set(DAY_TRAINING_EXAMPLE_APPROVAL_V1_KEYS)
    assert validate_day_training_example_approval_v1(
        ex,
        dataset_policy=ds,
        application_result=app,
        hint_package=pkg,
    ) == []
