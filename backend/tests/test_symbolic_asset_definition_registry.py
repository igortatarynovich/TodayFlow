"""D1.1 — Symbolic Asset Definition registry tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.symbolic_asset_definition_registry_loader import (
    clear_symbolic_asset_definition_registry_cache,
    get_symbolic_asset_definition,
    list_symbolic_asset_definitions_by_category,
    load_symbolic_asset_definition_registry_v1,
)
from todayflow_backend.data.symbolic_asset_definition_registry_validator import (
    CANONICAL_ASSET_CATEGORIES,
    SYMBOLIC_ASSET_DEFINITION_REGISTRY_V1_CONTRACT,
    SYMBOLIC_ASSET_DEFINITION_V1_KEYS,
    validate_symbolic_asset_definition_registry_v1,
)


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    clear_symbolic_asset_definition_registry_cache()
    yield
    clear_symbolic_asset_definition_registry_cache()


@pytest.fixture
def registry() -> dict:
    return load_symbolic_asset_definition_registry_v1()


def test_registry_loads(registry: dict) -> None:
    assert registry["contract_version"] == SYMBOLIC_ASSET_DEFINITION_REGISTRY_V1_CONTRACT
    assert registry["domain"] == "symbolic"
    assert len(registry["symbolic_asset_definitions"]) >= 30


def test_asset_code_unique(registry: dict) -> None:
    codes = list(registry["symbolic_asset_definitions"].keys())
    assert len(codes) == len(set(codes))
    for code, entry in registry["symbolic_asset_definitions"].items():
        assert entry["asset_code"] == code


def test_category_valid(registry: dict) -> None:
    for entry in registry["symbolic_asset_definitions"].values():
        assert entry["category_code"] in CANONICAL_ASSET_CATEGORIES
        assert entry["asset_category"] == entry["category_code"]


def test_theme_codes_valid(registry: dict) -> None:
    errors = validate_symbolic_asset_definition_registry_v1(registry)
    assert not any("invalid theme_code" in err for err in errors)


def test_no_association_fields(registry: dict) -> None:
    forbidden = (
        "associations",
        "path_association",
        "cycle_association",
        "rhythm_association",
        "daymodel_association",
        "knowledge_association",
    )
    for entry in registry["symbolic_asset_definitions"].values():
        for field in forbidden:
            assert field not in entry


def test_no_recommendation_fields(registry: dict) -> None:
    for entry in registry["symbolic_asset_definitions"].values():
        assert "recommendation" not in entry
        assert "interpretation" not in entry
        assert "meaning" not in entry
        assert "insight" not in entry


def test_no_commerce_pricing_or_sku(registry: dict) -> None:
    forbidden = ("sku", "price", "pricing", "inventory", "product_id", "checkout")
    for entry in registry["symbolic_asset_definitions"].values():
        for field in forbidden:
            assert field not in entry
        assert isinstance(entry["commerce_eligible"], bool)


def test_visibility_tier_valid(registry: dict) -> None:
    for entry in registry["symbolic_asset_definitions"].values():
        assert entry["visibility_tier"] in {"reference", "soft", "standard", "full"}


def test_output_shape_stable(registry: dict) -> None:
    amethyst = get_symbolic_asset_definition("amethyst", registry)
    assert set(amethyst.keys()) == SYMBOLIC_ASSET_DEFINITION_V1_KEYS
    assert validate_symbolic_asset_definition_registry_v1(registry) == []


def test_validator_rejects_interpretive_asset_code(registry: dict) -> None:
    bad = copy.deepcopy(registry)
    bad["symbolic_asset_definitions"]["stone_for_anxiety"] = copy.deepcopy(
        bad["symbolic_asset_definitions"]["amethyst"]
    )
    bad["symbolic_asset_definitions"]["stone_for_anxiety"]["asset_code"] = "stone_for_anxiety"
    errors = validate_symbolic_asset_definition_registry_v1(bad)
    assert any("stone_for_anxiety" in err and "association" in err for err in errors)


def test_list_by_category_stones(registry: dict) -> None:
    stones = list_symbolic_asset_definitions_by_category("stone", registry)
    codes = {item["asset_code"] for item in stones}
    assert "amethyst" in codes
    assert "fool" not in codes
