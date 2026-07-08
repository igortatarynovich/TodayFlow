"""D1.5 — Symbolic Commerce Link registry tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.symbolic_asset_definition_registry_loader import (
    clear_symbolic_asset_definition_registry_cache,
    load_symbolic_asset_definition_registry_v1,
)
from todayflow_backend.data.symbolic_commerce_link_registry_loader import (
    clear_symbolic_commerce_link_registry_cache,
    get_symbolic_commerce_link,
    get_symbolic_commerce_link_by_sku,
    list_symbolic_commerce_links_for_asset,
    load_symbolic_commerce_link_registry_v1,
)
from todayflow_backend.data.symbolic_commerce_link_registry_validator import (
    ALLOWED_LINK_MODES,
    SYMBOLIC_COMMERCE_LINK_REGISTRY_V1_CONTRACT,
    SYMBOLIC_COMMERCE_LINK_V1_KEYS,
    SymbolicCommerceLinkValidationContext,
    validate_symbolic_commerce_link_registry_v1,
)


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    clear_symbolic_asset_definition_registry_cache()
    clear_symbolic_commerce_link_registry_cache()
    yield
    clear_symbolic_asset_definition_registry_cache()
    clear_symbolic_commerce_link_registry_cache()


@pytest.fixture
def registry() -> dict:
    return load_symbolic_commerce_link_registry_v1()


def _context() -> SymbolicCommerceLinkValidationContext:
    assets = load_symbolic_asset_definition_registry_v1()["symbolic_asset_definitions"]
    return SymbolicCommerceLinkValidationContext(asset_codes=frozenset(assets.keys()))


def test_registry_loads(registry: dict) -> None:
    assert registry["contract_version"] == SYMBOLIC_COMMERCE_LINK_REGISTRY_V1_CONTRACT
    assert registry["domain"] == "symbolic_commerce"
    assert len(registry["symbolic_commerce_links"]) >= 10


def test_sku_ref_unique(registry: dict) -> None:
    skus = [entry["sku_ref"] for entry in registry["symbolic_commerce_links"].values()]
    assert len(skus) == len(set(skus))


def test_asset_code_exists_in_d1_1(registry: dict) -> None:
    assets = load_symbolic_asset_definition_registry_v1()["symbolic_asset_definitions"]
    for entry in registry["symbolic_commerce_links"].values():
        assert entry["asset_code"] in assets


def test_link_mode_references_only(registry: dict) -> None:
    for entry in registry["symbolic_commerce_links"].values():
        assert entry["link_mode"] in ALLOWED_LINK_MODES


def test_no_symbolic_definition_fields(registry: dict) -> None:
    forbidden = (
        "meaning",
        "theme_codes",
        "association_refs",
        "visibility_tier",
        "recommendation",
        "offer_context",
        "price",
        "pricing",
    )
    for entry in registry["symbolic_commerce_links"].values():
        for field in forbidden:
            assert field not in entry


def test_output_shape_stable(registry: dict) -> None:
    sample = get_symbolic_commerce_link("link_amethyst_stone_v1", registry)
    assert set(sample.keys()) == SYMBOLIC_COMMERCE_LINK_V1_KEYS
    assert validate_symbolic_commerce_link_registry_v1(registry, context=_context()) == []


def test_validator_rejects_forbidden_meaning_field(registry: dict) -> None:
    bad = copy.deepcopy(registry)
    bad["symbolic_commerce_links"]["link_amethyst_stone_v1"]["meaning"] = "calming stone"
    errors = validate_symbolic_commerce_link_registry_v1(bad, context=_context())
    assert any("forbidden" in err for err in errors)


def test_get_by_sku(registry: dict) -> None:
    entry = get_symbolic_commerce_link_by_sku("sku.amethyst.stone.v1", registry)
    assert entry["asset_code"] == "amethyst"


def test_list_for_asset(registry: dict) -> None:
    links = list_symbolic_commerce_links_for_asset("amethyst", registry)
    assert len(links) >= 2
