"""P1.27 — Training dataset registry tests."""

from __future__ import annotations

import copy

from todayflow_backend.services.day_model_v1_active_knowledge import (
    DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_active_knowledge_hint_package import (
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
    CONSUMER_CACHE_REUSE,
    CONSUMER_CONTENT_RANKER,
    CONSUMER_CONTEXT_SELECTOR,
    CONSUMER_PROMPT_BUILDER,
    CONSUMER_SURFACE_PRIORITIZER,
    try_apply_hint_package_v1,
)
from todayflow_backend.services.day_model_v1_hint_application_dataset_policy import (
    try_build_hint_application_dataset_policy_v1,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import (
    KNOWLEDGE_TYPE_CONTENT_AFFINITY,
    KNOWLEDGE_TYPE_RESPONSE_STYLE,
)
from todayflow_backend.services.day_model_v1_training_dataset_registry import (
    DATASET_DOMAIN_CACHE_REUSE,
    DATASET_DOMAIN_CONTEXT_SELECTION,
    DATASET_DOMAIN_DAY_MODEL,
    DATASET_DOMAIN_PROMPT_REFINEMENT,
    DATASET_DOMAIN_RANKING,
    DATASET_SPLIT_UNASSIGNED,
    DAY_TRAINING_DATASET_REGISTRY_ITEM_V1_CONTRACT,
    DAY_TRAINING_DATASET_REGISTRY_ITEM_V1_KEYS,
    EXAMPLE_TYPE_CACHE_HINT,
    EXAMPLE_TYPE_CONTEXT_HINT,
    EXAMPLE_TYPE_PROMPT_REFINEMENT,
    EXAMPLE_TYPE_RANKING_HINT,
    EXAMPLE_TYPE_SURFACE_PRIORITY_HINT,
    REGISTRY_RESULT_REGISTERED,
    REGISTRY_RESULT_REJECTED,
    try_register_training_example_v1,
    validate_day_training_dataset_registry_item_v1,
)
from todayflow_backend.services.day_model_v1_training_example_approval import (
    APPROVAL_STATUS_NOT_READY,
    APPROVAL_STATUS_REJECTED,
    PROMOTION_RESULT_APPROVED,
    try_promote_dataset_candidate_v1,
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


def _chain_to_promotion(active, *, surface, requested_usage, consumer, mode, **policy_kwargs):
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


def _approved(active, *, surface, requested_usage, consumer, mode, **policy_kwargs):
    active, pkg, app, ds = _chain_to_promotion(
        active,
        surface=surface,
        requested_usage=requested_usage,
        consumer=consumer,
        mode=mode,
        **policy_kwargs,
    )
    promo = try_promote_dataset_candidate_v1(
        ds,
        app,
        pkg,
        active,
        reaction_evidence={"present": True, "reaction_type": "positive_engagement"},
    )
    assert promo["result"] == PROMOTION_RESULT_APPROVED
    return active, pkg, app, promo["training_example"]


def _register(active, pkg, app, example):
    return try_register_training_example_v1(example, app, pkg, active)


def test_approved_example_registers_registry_item():
    active, pkg, app, example = _approved(
        _active(),
        surface="day_guidance_card",
        requested_usage=USAGE_CONTEXT_SELECTION,
        consumer=CONSUMER_CONTEXT_SELECTOR,
        mode=APPLICATION_MODE_INCLUDE,
    )
    outcome = _register(active, pkg, app, example)
    assert outcome["result"] == REGISTRY_RESULT_REGISTERED
    item = outcome["registry_item"]
    assert item is not None
    assert item["status"] == "registered"
    assert item["training_example_id"] == example["training_example_id"]


def test_not_ready_no_registry_item():
    active, pkg, app, ds = _chain_to_promotion(
        _active(),
        surface="day_guidance_card",
        requested_usage=USAGE_CONTEXT_SELECTION,
        consumer=CONSUMER_CONTEXT_SELECTOR,
        mode=APPLICATION_MODE_INCLUDE,
    )
    promo = try_promote_dataset_candidate_v1(ds, app, pkg, active)
    assert promo["training_example"]["approval_status"] == APPROVAL_STATUS_NOT_READY
    outcome = _register(active, pkg, app, promo["training_example"])
    assert outcome["result"] == REGISTRY_RESULT_REJECTED
    assert outcome["registry_item"] is None


def test_rejected_no_registry_item():
    active, pkg, app, ds = _chain_to_promotion(
        _active(),
        surface="content_ranker",
        requested_usage=USAGE_CONTENT_RANKING,
        consumer=CONSUMER_CONTENT_RANKER,
        mode=APPLICATION_MODE_BOOST,
        downstream_reaction_evidence=False,
    )
    promo = try_promote_dataset_candidate_v1(
        ds,
        app,
        pkg,
        active,
        reaction_evidence={"present": True},
        quality_evidence={"passed": True},
        review_approved=True,
    )
    assert promo["training_example"]["approval_status"] == APPROVAL_STATUS_REJECTED
    outcome = _register(active, pkg, app, promo["training_example"])
    assert outcome["result"] == REGISTRY_RESULT_REJECTED
    assert outcome["registry_item"] is None


def test_training_use_not_allowed_no_item():
    active, pkg, app, example = _approved(
        _active(),
        surface="day_guidance_card",
        requested_usage=USAGE_CONTEXT_SELECTION,
        consumer=CONSUMER_CONTEXT_SELECTOR,
        mode=APPLICATION_MODE_INCLUDE,
    )
    bad = copy.deepcopy(example)
    bad["training_use_allowed"] = False
    outcome = _register(active, pkg, app, bad)
    assert outcome["result"] == REGISTRY_RESULT_REJECTED
    assert outcome["registry_item"] is None


def test_missing_hashes_no_item():
    active, pkg, app, example = _approved(
        _active(),
        surface="day_guidance_card",
        requested_usage=USAGE_CONTEXT_SELECTION,
        consumer=CONSUMER_CONTEXT_SELECTOR,
        mode=APPLICATION_MODE_INCLUDE,
    )
    bad = copy.deepcopy(example)
    bad["input_snapshot_hash"] = ""
    outcome = _register(active, pkg, app, bad)
    assert outcome["result"] == REGISTRY_RESULT_REJECTED
    assert outcome["registry_item"] is None


def test_prompt_hint_prompt_refinement_domain():
    active, pkg, app, ds = _chain_to_promotion(
        _active(
            knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
            claim="responds_to_surface:today_hero",
        ),
        surface="day_guidance_card",
        requested_usage=USAGE_PROMPT_REFINEMENT,
        consumer=CONSUMER_PROMPT_BUILDER,
        mode=APPLICATION_MODE_ADJUST_TONE,
    )
    promo = try_promote_dataset_candidate_v1(
        ds,
        app,
        pkg,
        active,
        reaction_evidence={"present": True, "reaction_type": "completed_read"},
        quality_evidence={"passed": True, "score": 0.9},
        review_approved=True,
    )
    assert promo["result"] == PROMOTION_RESULT_APPROVED
    example = promo["training_example"]
    item = _register(active, pkg, app, example)["registry_item"]
    assert item["dataset_domain"] == DATASET_DOMAIN_PROMPT_REFINEMENT
    assert item["example_type"] == EXAMPLE_TYPE_PROMPT_REFINEMENT


def test_context_hint_context_selection_domain():
    active, pkg, app, example = _approved(
        _active(),
        surface="day_guidance_card",
        requested_usage=USAGE_CONTEXT_SELECTION,
        consumer=CONSUMER_CONTEXT_SELECTOR,
        mode=APPLICATION_MODE_INCLUDE,
    )
    item = _register(active, pkg, app, example)["registry_item"]
    assert item["dataset_domain"] == DATASET_DOMAIN_CONTEXT_SELECTION
    assert item["example_type"] == EXAMPLE_TYPE_CONTEXT_HINT


def test_cache_hint_cache_reuse_domain():
    active, pkg, app, ds = _chain_to_promotion(
        _active(
            knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
            claim="responds_to_surface:today_hero",
        ),
        surface="cache_layer",
        requested_usage=USAGE_CACHE_REUSE,
        consumer=CONSUMER_CACHE_REUSE,
        mode=APPLICATION_MODE_INCLUDE,
        reuse_success_evidence=True,
    )
    promo = try_promote_dataset_candidate_v1(
        ds,
        app,
        pkg,
        active,
        reaction_evidence={"present": True, "reaction_type": "cache_hit"},
    )
    example = promo["training_example"]
    item = _register(active, pkg, app, example)["registry_item"]
    assert item["dataset_domain"] == DATASET_DOMAIN_CACHE_REUSE
    assert item["example_type"] == EXAMPLE_TYPE_CACHE_HINT


def test_ranking_hint_ranking_domain():
    active, pkg, app, ds = _chain_to_promotion(
        _active(),
        surface="content_ranker",
        requested_usage=USAGE_CONTENT_RANKING,
        consumer=CONSUMER_CONTENT_RANKER,
        mode=APPLICATION_MODE_BOOST,
        downstream_reaction_evidence=True,
    )
    promo = try_promote_dataset_candidate_v1(
        ds,
        app,
        pkg,
        active,
        reaction_evidence={"present": True, "reaction_type": "clicked_result"},
        quality_evidence={"passed": True, "score": 0.85},
        review_approved=True,
    )
    example = promo["training_example"]
    item = _register(active, pkg, app, example)["registry_item"]
    assert item["dataset_domain"] == DATASET_DOMAIN_RANKING
    assert item["example_type"] == EXAMPLE_TYPE_RANKING_HINT


def test_surface_priority_day_model_domain():
    active, pkg, app, ds = _chain_to_promotion(
        _active(
            knowledge_type=KNOWLEDGE_TYPE_RESPONSE_STYLE,
            claim="responds_to_surface:today_hero",
        ),
        surface="today_hero",
        requested_usage=USAGE_SURFACE_PRIORITY,
        consumer=CONSUMER_SURFACE_PRIORITIZER,
        mode=APPLICATION_MODE_DELAY,
        user_reaction_evidence=True,
    )
    promo = try_promote_dataset_candidate_v1(
        ds,
        app,
        pkg,
        active,
        reaction_evidence={"present": True, "reaction_type": "viewed_surface"},
        quality_evidence={"passed": True, "score": 0.88},
        review_approved=True,
    )
    example = promo["training_example"]
    item = _register(active, pkg, app, example)["registry_item"]
    assert item["dataset_domain"] == DATASET_DOMAIN_DAY_MODEL
    assert item["example_type"] == EXAMPLE_TYPE_SURFACE_PRIORITY_HINT


def test_export_allowed_false():
    active, pkg, app, example = _approved(
        _active(),
        surface="day_guidance_card",
        requested_usage=USAGE_CONTEXT_SELECTION,
        consumer=CONSUMER_CONTEXT_SELECTOR,
        mode=APPLICATION_MODE_INCLUDE,
    )
    item = _register(active, pkg, app, example)["registry_item"]
    assert item["export_allowed"] is False


def test_training_started_false():
    active, pkg, app, example = _approved(
        _active(),
        surface="day_guidance_card",
        requested_usage=USAGE_CONTEXT_SELECTION,
        consumer=CONSUMER_CONTEXT_SELECTOR,
        mode=APPLICATION_MODE_INCLUDE,
    )
    item = _register(active, pkg, app, example)["registry_item"]
    assert item["training_started"] is False


def test_dataset_split_unassigned():
    active, pkg, app, example = _approved(
        _active(),
        surface="day_guidance_card",
        requested_usage=USAGE_CONTEXT_SELECTION,
        consumer=CONSUMER_CONTEXT_SELECTOR,
        mode=APPLICATION_MODE_INCLUDE,
    )
    item = _register(active, pkg, app, example)["registry_item"]
    assert item["dataset_split"] == DATASET_SPLIT_UNASSIGNED


def test_output_shape_stable():
    active, pkg, app, example = _approved(
        _active(),
        surface="day_guidance_card",
        requested_usage=USAGE_CONTEXT_SELECTION,
        consumer=CONSUMER_CONTEXT_SELECTOR,
        mode=APPLICATION_MODE_INCLUDE,
    )
    item = _register(active, pkg, app, example)["registry_item"]
    assert item["contract_version"] == DAY_TRAINING_DATASET_REGISTRY_ITEM_V1_CONTRACT
    assert set(item.keys()) == set(DAY_TRAINING_DATASET_REGISTRY_ITEM_V1_KEYS)
    assert validate_day_training_dataset_registry_item_v1(
        item,
        training_example=example,
        hint_package=pkg,
    ) == []
