"""D1.3 — Symbolic Collection registry tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.symbolic_asset_association_registry_loader import (
    load_symbolic_asset_association_registry_v1,
)
from todayflow_backend.data.symbolic_asset_definition_registry_loader import (
    load_symbolic_asset_definition_registry_v1,
)
from todayflow_backend.data.symbolic_collection_registry_loader import (
    _build_validation_context,
    clear_symbolic_collection_registry_cache,
    get_symbolic_collection,
    list_symbolic_collections_by_type,
    list_symbolic_collections_for_asset,
    load_symbolic_collection_registry_v1,
)
from todayflow_backend.data.symbolic_collection_registry_validator import (
    ALLOWED_COLLECTION_TYPES,
    ALLOWED_COLLECTION_VISIBILITY_TIERS,
    SYMBOLIC_COLLECTION_REGISTRY_V1_CONTRACT,
    SYMBOLIC_COLLECTION_V1_KEYS,
    validate_symbolic_collection_registry_v1,
)


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    clear_symbolic_collection_registry_cache()
    yield
    clear_symbolic_collection_registry_cache()


@pytest.fixture
def registry() -> dict:
    return load_symbolic_collection_registry_v1()


def test_registry_loads(registry: dict) -> None:
    assert registry["contract_version"] == SYMBOLIC_COLLECTION_REGISTRY_V1_CONTRACT
    assert registry["domain"] == "symbolic"
    assert 10 <= len(registry["symbolic_collections"]) <= 16


def test_collection_code_unique(registry: dict) -> None:
    codes = list(registry["symbolic_collections"].keys())
    assert len(codes) == len(set(codes))
    for code, entry in registry["symbolic_collections"].items():
        assert entry["collection_code"] == code


def test_asset_codes_exist_in_d1_1(registry: dict) -> None:
    assets = load_symbolic_asset_definition_registry_v1()["symbolic_asset_definitions"]
    for entry in registry["symbolic_collections"].values():
        for asset_code in entry["asset_codes"]:
            assert asset_code in assets


def test_association_refs_exist_in_d1_2(registry: dict) -> None:
    associations = load_symbolic_asset_association_registry_v1()["symbolic_asset_associations"]
    for entry in registry["symbolic_collections"].values():
        for assoc_id in entry["association_refs"]:
            assert assoc_id in associations


def test_compatible_contexts_and_type_valid(registry: dict) -> None:
    errors = validate_symbolic_collection_registry_v1(
        registry,
        context=_build_validation_context(),
    )
    assert errors == []


def test_collection_type_valid(registry: dict) -> None:
    for entry in registry["symbolic_collections"].values():
        assert entry["collection_type"] in ALLOWED_COLLECTION_TYPES


def test_visibility_tier_valid(registry: dict) -> None:
    for entry in registry["symbolic_collections"].values():
        assert entry["visibility_tier"] in ALLOWED_COLLECTION_VISIBILITY_TIERS


def test_no_commerce_fields(registry: dict) -> None:
    forbidden = (
        "sku",
        "price",
        "pricing",
        "inventory",
        "product_bundle",
        "purchase_cta",
        "checkout",
        "purchase",
    )
    for entry in registry["symbolic_collections"].values():
        for field in forbidden:
            assert field not in entry


def test_no_recommendation_or_personalization(registry: dict) -> None:
    forbidden = (
        "recommendation",
        "user_id",
        "personalized",
        "personalized_reason",
        "needed_for",
        "fixes",
        "heals",
        "sales_copy",
        "ui_copy",
    )
    for entry in registry["symbolic_collections"].values():
        for field in forbidden:
            assert field not in entry


def test_output_shape_stable(registry: dict) -> None:
    sample = get_symbolic_collection("clarity_path_symbols", registry)
    assert set(sample.keys()) == SYMBOLIC_COLLECTION_V1_KEYS


def test_validator_rejects_commerce_field(registry: dict) -> None:
    bad = copy.deepcopy(registry)
    bad["symbolic_collections"]["clarity_path_symbols"]["sku"] = "BUNDLE-001"
    errors = validate_symbolic_collection_registry_v1(
        bad,
        context=_build_validation_context(),
    )
    assert any("forbidden fields" in err for err in errors)


def test_validator_rejects_unknown_asset(registry: dict) -> None:
    bad = copy.deepcopy(registry)
    entry = bad["symbolic_collections"]["clarity_path_symbols"]
    entry["asset_codes"] = list(entry["asset_codes"]) + ["stone_for_anxiety"]
    errors = validate_symbolic_collection_registry_v1(
        bad,
        context=_build_validation_context(),
    )
    assert any("stone_for_anxiety" in err for err in errors)


def test_list_helpers(registry: dict) -> None:
    path_collections = list_symbolic_collections_by_type("path", registry)
    assert len(path_collections) == 4
    amethyst_collections = list_symbolic_collections_for_asset("amethyst", registry)
    assert any(item["collection_code"] == "clarity_path_symbols" for item in amethyst_collections)
