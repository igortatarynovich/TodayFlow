"""B1.13 — Evolution → Commerce visibility policy tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache, load_evolution_cd_v1
from todayflow_backend.data.evolution_product_effects_loader import clear_evolution_product_effects_cache
from todayflow_backend.services.evolution_commerce_visibility_policy_v1 import (
    BLOCK_COMMERCE_NOT_READY,
    BLOCK_INVALID_EVOLUTION_SLICE,
    EVOLUTION_COMMERCE_VISIBILITY_POLICY_V1_CONTRACT,
    EVOLUTION_COMMERCE_VISIBILITY_POLICY_V1_KEYS,
    SURFACE_BUNDLES,
    SURFACE_SHOP_ENTRY,
    SURFACE_SYMBOLIC_ASSETS,
    SURFACE_THEMED_COLLECTIONS,
    VISIBILITY_FULL,
    VISIBILITY_NONE,
    VISIBILITY_SOFT,
    VISIBILITY_STANDARD,
    build_evolution_commerce_visibility_policy_v1,
    validate_evolution_commerce_visibility_policy_v1,
)
from todayflow_backend.services.evolution_effect_consumer_map_v1 import (
    CONSUMER_COMMERCE_VISIBILITY,
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
        "explorer": {
            "confirmed_patterns": 3,
            "completed_cycles": 2,
            "reflection_events": 15,
            "active_days": 45,
            "signal_counts": {"practice_completed": 10},
            "confidence": 0.65,
        },
        "architect": {
            "confirmed_patterns": 5,
            "completed_cycles": 3,
            "reflection_events": 21,
            "active_days": 120,
            "signal_counts": {"confirmed_pattern": 2},
            "confidence": 0.75,
        },
        "mentor": {
            "confirmed_patterns": 6,
            "completed_cycles": 4,
            "reflection_events": 30,
            "active_days": 180,
            "signal_counts": {"confirmed_pattern": 3},
            "confidence": 0.85,
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


def _commerce_slice(cd: dict, stage: str, **policy_kwargs) -> dict:
    policy = _policy_for_stage(
        cd,
        stage,
        source_systems_ready={"commerce_visibility": True},
        **policy_kwargs,
    )
    return extract_evolution_effect_consumer_slice_v1(policy, CONSUMER_COMMERCE_VISIBILITY)


def _observer_soft_slice(cd: dict) -> dict:
    """Observer B1.5 registry is none; stage profile expects soft when slice allows."""
    slice_payload = _commerce_slice(cd, "observer")
    patched = copy.deepcopy(slice_payload)
    patched["effect_limits"]["commerce_visibility"] = "soft"
    patched["allowed_effects"] = {
        "commerce_effects": {
            "commerce_visibility": "soft",
            "symbolic_asset_tier": "soft",
            "themed_suggestions": False,
        }
    }
    return patched


def _ready(**overrides):
    base = {"commerce_visibility": True}
    base.update(overrides)
    return base


def test_seeker_visibility_none(cd: dict) -> None:
    policy = build_evolution_commerce_visibility_policy_v1(
        _commerce_slice(cd, "seeker"),
        commerce_readiness=_ready(),
    )

    assert policy["evolution_stage"] == "seeker"
    assert policy["commerce_visibility_level"] == VISIBILITY_NONE
    assert policy["allowed_surfaces"] == []


def test_observer_soft_visibility(cd: dict) -> None:
    policy = build_evolution_commerce_visibility_policy_v1(
        _observer_soft_slice(cd),
        commerce_readiness=_ready(),
    )

    assert policy["evolution_stage"] == "observer"
    assert policy["commerce_visibility_level"] == VISIBILITY_SOFT
    assert SURFACE_SHOP_ENTRY in policy["allowed_surfaces"]


def test_architect_standard_or_full_visibility(cd: dict) -> None:
    slice_payload = copy.deepcopy(_commerce_slice(cd, "architect"))
    slice_payload["effect_limits"]["commerce_visibility"] = "full"
    slice_payload["allowed_effects"] = {
        "commerce_effects": {
            "commerce_visibility": "full",
            "symbolic_asset_tier": "themed",
            "themed_suggestions": True,
        }
    }

    policy = build_evolution_commerce_visibility_policy_v1(
        slice_payload,
        commerce_readiness=_ready(),
    )

    assert policy["evolution_stage"] == "architect"
    assert policy["commerce_visibility_level"] in {VISIBILITY_STANDARD, VISIBILITY_FULL}
    assert SURFACE_SHOP_ENTRY in policy["allowed_surfaces"]
    assert SURFACE_SYMBOLIC_ASSETS in policy["allowed_surfaces"]


def test_commerce_not_ready_blocked(cd: dict) -> None:
    slice_payload = copy.deepcopy(_commerce_slice(cd, "architect"))
    slice_payload["effect_limits"]["commerce_visibility"] = "full"
    slice_payload["allowed_effects"] = {
        "commerce_effects": {
            "commerce_visibility": "full",
            "symbolic_asset_tier": "full",
            "themed_suggestions": True,
        }
    }

    policy = build_evolution_commerce_visibility_policy_v1(
        slice_payload,
        commerce_readiness={"commerce_visibility": False},
    )

    assert policy["commerce_visibility_level"] == VISIBILITY_NONE
    assert policy["allowed_surfaces"] == []
    reasons = {entry["reason"] for entry in policy["blocked_surfaces"]}
    assert BLOCK_COMMERCE_NOT_READY in reasons


def test_targeting_always_false(cd: dict) -> None:
    policy = build_evolution_commerce_visibility_policy_v1(
        _commerce_slice(cd, "architect"),
        commerce_readiness=_ready(),
    )

    assert policy["targeting_allowed"] is False
    assert "targeting" not in policy


def test_purchase_recommendation_always_false(cd: dict) -> None:
    policy = build_evolution_commerce_visibility_policy_v1(
        _commerce_slice(cd, "practitioner"),
        commerce_readiness=_ready(),
    )

    assert policy["purchase_recommendation_allowed"] is False
    assert "recommendation" not in policy


def test_personalized_offer_always_false(cd: dict) -> None:
    policy = build_evolution_commerce_visibility_policy_v1(
        _commerce_slice(cd, "explorer"),
        commerce_readiness=_ready(),
    )

    assert policy["personalized_offer_allowed"] is False


def test_no_sku_or_product_fields(cd: dict) -> None:
    policy = build_evolution_commerce_visibility_policy_v1(
        _commerce_slice(cd, "architect"),
        commerce_readiness=_ready(),
    )

    forbidden = {
        "sku",
        "product_id",
        "product",
        "products",
        "recommended_product",
        "recommended_sku",
        "purchase_prompt",
        "checkout",
    }
    assert forbidden.isdisjoint(set(policy.keys()))
    assert validate_evolution_commerce_visibility_policy_v1(policy) == []


def test_invalid_slice_idle_policy(cd: dict) -> None:
    valid_slice = _commerce_slice(cd, "seeker")
    invalid = copy.deepcopy(valid_slice)
    invalid["consumer_id"] = "not_commerce"

    policy = build_evolution_commerce_visibility_policy_v1(
        invalid,
        commerce_readiness=_ready(),
    )

    assert policy["source_evolution_slice_id"] is None
    assert policy["commerce_visibility_level"] == VISIBILITY_NONE
    reasons = {entry["reason"] for entry in policy["blocked_surfaces"]}
    assert BLOCK_INVALID_EVOLUTION_SLICE in reasons


def test_output_shape_stable(cd: dict) -> None:
    policy = build_evolution_commerce_visibility_policy_v1(
        _commerce_slice(cd, "practitioner"),
        commerce_readiness=_ready(),
    )

    assert policy["contract_version"] == EVOLUTION_COMMERCE_VISIBILITY_POLICY_V1_CONTRACT
    assert set(policy.keys()) == EVOLUTION_COMMERCE_VISIBILITY_POLICY_V1_KEYS
    blocked_surfaces = {entry["surface"] for entry in policy["blocked_surfaces"]}
    assert blocked_surfaces == {
        SURFACE_SHOP_ENTRY,
        SURFACE_SYMBOLIC_ASSETS,
        SURFACE_THEMED_COLLECTIONS,
        SURFACE_BUNDLES,
    } - set(policy["allowed_surfaces"])
