"""D1.4 — Symbolic visibility policy tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache, load_evolution_cd_v1
from todayflow_backend.data.evolution_product_effects_loader import clear_evolution_product_effects_cache
from todayflow_backend.data.symbolic_asset_association_registry_loader import (
    clear_symbolic_asset_association_registry_cache,
)
from todayflow_backend.data.symbolic_asset_definition_registry_loader import (
    clear_symbolic_asset_definition_registry_cache,
    load_symbolic_asset_definition_registry_v1,
)
from todayflow_backend.data.symbolic_collection_registry_loader import (
    clear_symbolic_collection_registry_cache,
    load_symbolic_collection_registry_v1,
)
from todayflow_backend.services.calendar_intelligence_consumer_policy_v1 import (
    BLOCK_CYCLE_VISIBILITY_NOT_ALLOWED,
    BLOCK_RHYTHM_VISIBILITY_NOT_ALLOWED,
    build_calendar_intelligence_consumer_policy_v1,
)
from todayflow_backend.services.evolution_commerce_visibility_policy_v1 import (
    EVOLUTION_COMMERCE_VISIBILITY_POLICY_V1_CONTRACT,
    SYMBOLIC_TIER_ASSET_CATEGORIES,
    VISIBILITY_ALLOWED_SURFACES,
    VISIBILITY_FULL,
    VISIBILITY_NONE,
    VISIBILITY_SOFT,
    VISIBILITY_STANDARD,
    build_evolution_commerce_visibility_policy_v1,
    validate_evolution_commerce_visibility_policy_v1,
)
from todayflow_backend.services.evolution_effect_consumer_map_v1 import (
    CONSUMER_CALENDAR,
    CONSUMER_COMMERCE_VISIBILITY,
    extract_evolution_effect_consumer_slice_v1,
)
from todayflow_backend.services.evolution_effect_runtime_policy_v1 import (
    build_evolution_effect_runtime_policy_v1,
)
from todayflow_backend.services.evolution_user_state_v1 import build_evolution_user_state_v1
from todayflow_backend.services.evolution_calendar_runtime_policy_v1 import (
    build_evolution_calendar_runtime_policy_v1,
)
from todayflow_backend.services.symbolic_visibility_policy_v1 import (
    BLOCK_ASSETS_ONLY_POLICY,
    BLOCK_INVALID_COMMERCE_POLICY,
    BLOCK_VISIBILITY_NONE,
    SYMBOLIC_VISIBILITY_POLICY_V1_CONTRACT,
    SYMBOLIC_VISIBILITY_POLICY_V1_KEYS,
    build_symbolic_visibility_policy_v1,
    validate_symbolic_visibility_policy_v1,
)


@pytest.fixture(autouse=True)
def _clear_caches() -> None:
    clear_evolution_cd_cache()
    clear_evolution_product_effects_cache()
    clear_symbolic_asset_definition_registry_cache()
    clear_symbolic_asset_association_registry_cache()
    clear_symbolic_collection_registry_cache()
    yield
    clear_evolution_cd_cache()
    clear_evolution_product_effects_cache()
    clear_symbolic_asset_definition_registry_cache()
    clear_symbolic_asset_association_registry_cache()
    clear_symbolic_collection_registry_cache()


@pytest.fixture
def cd() -> dict:
    return load_evolution_cd_v1()


@pytest.fixture
def asset_registry() -> dict:
    return load_symbolic_asset_definition_registry_v1()


@pytest.fixture
def collection_registry() -> dict:
    return load_symbolic_collection_registry_v1()


def _runtime_policy(cd: dict, stage: str, **policy_kwargs):
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
        evolution_score_snapshot=420,
        last_evaluated_at="2026-06-01T09:00:00Z",
        cd=cd,
    )
    return build_evolution_effect_runtime_policy_v1(
        evolution_user_state=state,
        evolution_score_snapshot_id="evolution_score_snapshot_v1:user-1:2026-06-01T09:00:00Z",
        **policy_kwargs,
    )


def _commerce_policy(cd: dict, stage: str, **runtime_kwargs):
    runtime = _runtime_policy(
        cd,
        stage,
        source_systems_ready={"commerce_visibility": True},
        **runtime_kwargs,
    )
    slice_payload = extract_evolution_effect_consumer_slice_v1(
        runtime,
        CONSUMER_COMMERCE_VISIBILITY,
    )
    return build_evolution_commerce_visibility_policy_v1(
        slice_payload,
        commerce_readiness={"commerce_visibility": True},
    )


def _calendar_policy(cd: dict, stage: str, **runtime_kwargs):
    runtime = _runtime_policy(
        cd,
        stage,
        source_systems_ready={"calendar_intelligence": True, "share_features": True},
        **runtime_kwargs,
    )
    calendar_slice = extract_evolution_effect_consumer_slice_v1(runtime, CONSUMER_CALENDAR)
    runtime_policy = build_evolution_calendar_runtime_policy_v1(
        calendar_slice,
        calendar_readiness={"calendar_intelligence": True},
    )
    return build_calendar_intelligence_consumer_policy_v1(runtime_policy)


def _observer_soft_commerce(cd: dict) -> dict:
    runtime = _runtime_policy(
        cd,
        "observer",
        source_systems_ready={"commerce_visibility": True},
    )
    slice_payload = extract_evolution_effect_consumer_slice_v1(
        runtime,
        CONSUMER_COMMERCE_VISIBILITY,
    )
    patched = copy.deepcopy(slice_payload)
    patched["effect_limits"]["commerce_visibility"] = "soft"
    patched["allowed_effects"] = {
        "commerce_effects": {
            "commerce_visibility": "soft",
            "symbolic_asset_tier": "soft",
            "themed_suggestions": False,
        }
    }
    return build_evolution_commerce_visibility_policy_v1(
        patched,
        commerce_readiness={"commerce_visibility": True},
    )


def _synthetic_commerce_policy(visibility_level: str) -> dict:
    """Build a valid B1.13 policy for D1.4 tests when registry slice caps below stage."""
    allowed_surfaces = list(VISIBILITY_ALLOWED_SURFACES.get(visibility_level, []))
    blocked_surfaces = [
        {"surface": surface, "reason": "stage_visibility_none"}
        for surface in ("shop_entry", "symbolic_assets", "themed_collections", "bundles")
        if surface not in allowed_surfaces
    ]
    if visibility_level == VISIBILITY_FULL:
        tier = "full"
    elif visibility_level == VISIBILITY_STANDARD:
        tier = "themed"
    else:
        tier = "soft"
    categories = (
        []
        if visibility_level == VISIBILITY_NONE
        else list(SYMBOLIC_TIER_ASSET_CATEGORIES.get(tier, []))
    )
    policy = {
        "contract_version": EVOLUTION_COMMERCE_VISIBILITY_POLICY_V1_CONTRACT,
        "policy_id": f"ecvp-test-{visibility_level}",
        "source_evolution_slice_id": "slice-test",
        "evolution_stage": "practitioner",
        "commerce_visibility_level": visibility_level,
        "allowed_surfaces": allowed_surfaces,
        "blocked_surfaces": blocked_surfaces,
        "allowed_asset_categories": categories,
        "targeting_allowed": False,
        "purchase_recommendation_allowed": False,
        "personalized_offer_allowed": False,
        "commerce_mutation_allowed": False,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "created_at": "2026-06-01T12:00:00Z",
    }
    assert validate_evolution_commerce_visibility_policy_v1(policy) == []
    return policy


def _practitioner_standard_commerce(cd: dict) -> dict:
    return _synthetic_commerce_policy(VISIBILITY_STANDARD)


def _architect_full_commerce(cd: dict) -> dict:
    return _synthetic_commerce_policy(VISIBILITY_FULL)


def test_visibility_none_blocks_everything(
    cd: dict,
    asset_registry: dict,
    collection_registry: dict,
) -> None:
    policy = build_symbolic_visibility_policy_v1(
        _commerce_policy(cd, "seeker"),
        calendar_consumer_policy=_calendar_policy(cd, "seeker"),
        asset_registry=asset_registry,
        collection_registry=collection_registry,
    )

    assert policy["visibility_level"] == VISIBILITY_NONE
    assert policy["visible_assets"] == []
    assert policy["visible_collections"] == []
    assert len(policy["blocked_assets"]) == len(asset_registry["symbolic_asset_definitions"])
    assert len(policy["blocked_collections"]) == len(collection_registry["symbolic_collections"])
    assert BLOCK_VISIBILITY_NONE in policy["blocked_reasons"]


def test_soft_visibility_assets_only(
    cd: dict,
    asset_registry: dict,
    collection_registry: dict,
) -> None:
    policy = build_symbolic_visibility_policy_v1(
        _observer_soft_commerce(cd),
        calendar_consumer_policy=_calendar_policy(cd, "observer"),
        asset_registry=asset_registry,
        collection_registry=collection_registry,
    )

    assert policy["visibility_level"] == VISIBILITY_SOFT
    assert policy["visible_assets"]
    assert policy["visible_collections"] == []
    assert len(policy["blocked_collections"]) == len(collection_registry["symbolic_collections"])
    assert BLOCK_ASSETS_ONLY_POLICY in policy["blocked_reasons"]
    assert policy["associations_metadata_allowed"] is False


def test_standard_visibility_assets_and_collections(
    cd: dict,
    collection_registry: dict,
) -> None:
    policy = build_symbolic_visibility_policy_v1(
        _practitioner_standard_commerce(cd),
        calendar_consumer_policy=_calendar_policy(cd, "practitioner"),
    )

    assert policy["visibility_level"] == VISIBILITY_STANDARD
    assert policy["visible_assets"]
    assert policy["visible_collections"]
    assert "clarity_path_symbols" in policy["visible_collections"]
    assert policy["associations_metadata_allowed"] is False


def test_full_visibility_allows_associations_metadata(cd: dict) -> None:
    policy = build_symbolic_visibility_policy_v1(
        _architect_full_commerce(cd),
        calendar_consumer_policy=_calendar_policy(cd, "architect"),
    )

    assert policy["visibility_level"] == VISIBILITY_FULL
    assert policy["associations_metadata_allowed"] is True
    assert policy["visible_assets"]
    assert policy["visible_collections"]


def test_rhythm_hidden_redacts_rhythm_collections(
    cd: dict,
    collection_registry: dict,
) -> None:
    policy = build_symbolic_visibility_policy_v1(
        _architect_full_commerce(cd),
        calendar_consumer_policy=_calendar_policy(cd, "practitioner"),
    )

    assert "recovery_rhythm_symbols" in policy["redacted_collections"]
    assert "reflection_rhythm_symbols" in policy["redacted_collections"]
    assert BLOCK_RHYTHM_VISIBILITY_NOT_ALLOWED in policy["blocked_reasons"]
    assert "rhythm" not in policy["allowed_collection_types"] or policy["redacted_collections"]


def test_cycle_hidden_redacts_cycle_collections(
    cd: dict,
    collection_registry: dict,
) -> None:
    commerce = _architect_full_commerce(cd)
    calendar = _calendar_policy(cd, "seeker")
    calendar = copy.deepcopy(calendar)
    calendar["cycle_overlay_visibility_allowed"] = False

    policy = build_symbolic_visibility_policy_v1(
        commerce,
        calendar_consumer_policy=calendar,
    )

    cycle_codes = [
        code
        for code, entry in collection_registry["symbolic_collections"].items()
        if entry["collection_type"] == "cycle"
    ]
    assert cycle_codes
    for code in cycle_codes:
        assert code in policy["redacted_collections"]
    assert BLOCK_CYCLE_VISIBILITY_NOT_ALLOWED in policy["blocked_reasons"]


def test_invalid_commerce_policy_idle_visibility(
    asset_registry: dict,
    collection_registry: dict,
) -> None:
    policy = build_symbolic_visibility_policy_v1(None)

    assert policy["visibility_level"] == VISIBILITY_NONE
    assert policy["visible_assets"] == []
    assert BLOCK_INVALID_COMMERCE_POLICY in policy["blocked_reasons"]
    assert len(policy["blocked_assets"]) == len(asset_registry["symbolic_asset_definitions"])


def test_recommendation_allowed_false(cd: dict) -> None:
    policy = build_symbolic_visibility_policy_v1(
        _practitioner_standard_commerce(cd),
        calendar_consumer_policy=_calendar_policy(cd, "practitioner"),
    )
    assert policy["recommendation_allowed"] is False


def test_commerce_activation_allowed_false(cd: dict) -> None:
    policy = build_symbolic_visibility_policy_v1(
        _practitioner_standard_commerce(cd),
        calendar_consumer_policy=_calendar_policy(cd, "practitioner"),
    )
    assert policy["commerce_activation_allowed"] is False
    assert policy["personalization_allowed"] is False


def test_output_shape_stable(cd: dict) -> None:
    policy = build_symbolic_visibility_policy_v1(
        _practitioner_standard_commerce(cd),
        calendar_consumer_policy=_calendar_policy(cd, "practitioner"),
    )

    assert policy["contract_version"] == SYMBOLIC_VISIBILITY_POLICY_V1_CONTRACT
    assert set(policy.keys()) == SYMBOLIC_VISIBILITY_POLICY_V1_KEYS
    assert validate_symbolic_visibility_policy_v1(policy) == []
