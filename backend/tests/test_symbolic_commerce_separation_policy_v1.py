"""D1.5 — Symbolic commerce separation policy tests."""

from __future__ import annotations

import pytest

from todayflow_backend.data.symbolic_asset_definition_registry_loader import (
    clear_symbolic_asset_definition_registry_cache,
)
from todayflow_backend.data.symbolic_commerce_link_registry_loader import (
    clear_symbolic_commerce_link_registry_cache,
    load_symbolic_commerce_link_registry_v1,
)
from todayflow_backend.services.symbolic_commerce_separation_policy_v1 import (
    BLOCK_COMMERCE_DEFINES_SYMBOLIC,
    BLOCK_INVALID_LINK_REGISTRY,
    BLOCK_UNKNOWN_ASSET_REF,
    BLOCK_UNKNOWN_SKU_REF,
    SYMBOLIC_COMMERCE_SEPARATION_POLICY_V1_CONTRACT,
    SYMBOLIC_COMMERCE_SEPARATION_POLICY_V1_KEYS,
    build_symbolic_commerce_separation_policy_v1,
    validate_commerce_product_separation_v1,
    validate_symbolic_commerce_separation_policy_v1,
)


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    clear_symbolic_asset_definition_registry_cache()
    clear_symbolic_commerce_link_registry_cache()
    yield
    clear_symbolic_asset_definition_registry_cache()
    clear_symbolic_commerce_link_registry_cache()


def test_separation_policy_loads_from_registry() -> None:
    policy = build_symbolic_commerce_separation_policy_v1()

    assert policy["contract_version"] == SYMBOLIC_COMMERCE_SEPARATION_POLICY_V1_CONTRACT
    assert policy["separation_enforced"] is True
    assert policy["commerce_may_define_assets"] is False
    assert policy["commerce_may_reference_assets"] is True
    assert len(policy["validated_links"]) >= 10


def test_commerce_may_not_define_assets() -> None:
    policy = build_symbolic_commerce_separation_policy_v1()
    assert policy["commerce_may_define_assets"] is False
    assert policy["visibility_owned_by_symbolic_layer"] is True


def test_valid_commerce_product_ref_only() -> None:
    policy = build_symbolic_commerce_separation_policy_v1(
        commerce_product={
            "sku_ref": "sku.amethyst.stone.v1",
            "asset_code": "amethyst",
            "product_type": "physical_stone",
        }
    )
    assert policy["product_separation_valid"] is True
    assert policy["rejected_product_fields"] == []


def test_commerce_product_with_meaning_rejected() -> None:
    policy = build_symbolic_commerce_separation_policy_v1(
        commerce_product={
            "sku_ref": "sku.amethyst.stone.v1",
            "asset_code": "amethyst",
            "meaning": "stone for anxiety",
        }
    )
    assert policy["product_separation_valid"] is False
    assert BLOCK_COMMERCE_DEFINES_SYMBOLIC in policy["blocked_reasons"]
    assert "meaning" in policy["rejected_product_fields"]


def test_commerce_product_with_association_rejected() -> None:
    errors = validate_commerce_product_separation_v1(
        {
            "sku_ref": "sku.amethyst.stone.v1",
            "association_refs": ["assoc_amethyst_path_clarity"],
        }
    )
    assert any("defines symbolic layer" in err for err in errors)


def test_unknown_asset_ref_rejected() -> None:
    policy = build_symbolic_commerce_separation_policy_v1(
        commerce_product={
            "sku_ref": "sku.amethyst.stone.v1",
            "asset_code": "stone_for_anxiety",
        }
    )
    assert policy["product_separation_valid"] is False
    assert BLOCK_UNKNOWN_ASSET_REF in policy["blocked_reasons"]


def test_unknown_sku_ref_rejected() -> None:
    policy = build_symbolic_commerce_separation_policy_v1(
        commerce_product={
            "sku_ref": "sku.unknown.product.v1",
            "asset_code": "amethyst",
        }
    )
    assert policy["product_separation_valid"] is False
    assert BLOCK_UNKNOWN_SKU_REF in policy["blocked_reasons"]


def test_recommendation_from_commerce_not_allowed() -> None:
    policy = build_symbolic_commerce_separation_policy_v1()
    assert policy["recommendation_from_commerce_allowed"] is False


def test_invalid_link_registry_idle_policy() -> None:
    policy = build_symbolic_commerce_separation_policy_v1(
        {"contract_version": "bad", "symbolic_commerce_links": {}}
    )
    assert policy["validated_links"] == []
    assert BLOCK_INVALID_LINK_REGISTRY in policy["blocked_reasons"]


def test_output_shape_stable() -> None:
    policy = build_symbolic_commerce_separation_policy_v1(
        link_registry=load_symbolic_commerce_link_registry_v1()
    )
    assert set(policy.keys()) == SYMBOLIC_COMMERCE_SEPARATION_POLICY_V1_KEYS
    assert validate_symbolic_commerce_separation_policy_v1(policy) == []
