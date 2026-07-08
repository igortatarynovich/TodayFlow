"""D1.2 — Symbolic Asset Association registry tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.evolution_cd_loader import load_evolution_cd_v1
from todayflow_backend.data.symbolic_asset_association_registry_loader import (
    clear_symbolic_asset_association_registry_cache,
    get_symbolic_asset_association,
    list_symbolic_asset_associations_by_type,
    list_symbolic_asset_associations_for_asset,
    load_symbolic_asset_association_registry_v1,
)
from todayflow_backend.data.symbolic_asset_association_registry_validator import (
    ALLOWED_ASSOCIATION_MODES,
    ALLOWED_ASSOCIATION_TYPES,
    SYMBOLIC_ASSET_ASSOCIATION_REGISTRY_V1_CONTRACT,
    SYMBOLIC_ASSET_ASSOCIATION_V1_KEYS,
    default_validation_context,
    validate_symbolic_asset_association_registry_v1,
)
from todayflow_backend.data.symbolic_asset_definition_registry_loader import (
    load_symbolic_asset_definition_registry_v1,
)


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    clear_symbolic_asset_association_registry_cache()
    yield
    clear_symbolic_asset_association_registry_cache()


@pytest.fixture
def registry() -> dict:
    return load_symbolic_asset_association_registry_v1()


def _validation_context() -> object:
    assets = load_symbolic_asset_definition_registry_v1()["symbolic_asset_definitions"]
    cd = load_evolution_cd_v1()
    return default_validation_context(
        asset_codes=frozenset(assets.keys()),
        path_theme_codes=frozenset((cd.get("evolution_path_themes") or {}).keys()),
    )


def test_registry_loads(registry: dict) -> None:
    assert registry["contract_version"] == SYMBOLIC_ASSET_ASSOCIATION_REGISTRY_V1_CONTRACT
    assert registry["domain"] == "symbolic"
    assert 60 <= len(registry["symbolic_asset_associations"]) <= 100


def test_asset_code_exists_in_d1_1(registry: dict) -> None:
    assets = load_symbolic_asset_definition_registry_v1()["symbolic_asset_definitions"]
    for entry in registry["symbolic_asset_associations"].values():
        assert entry["asset_code"] in assets


def test_association_type_valid(registry: dict) -> None:
    for entry in registry["symbolic_asset_associations"].values():
        assert entry["association_type"] in ALLOWED_ASSOCIATION_TYPES


def test_target_ref_valid_for_type(registry: dict) -> None:
    errors = validate_symbolic_asset_association_registry_v1(
        registry,
        context=_validation_context(),
    )
    assert errors == []


def test_strength_and_confidence_in_range(registry: dict) -> None:
    for entry in registry["symbolic_asset_associations"].values():
        assert 0 <= entry["strength"] <= 1
        assert 0 <= entry["confidence"] <= 1


def test_no_recommendation_or_commerce_fields(registry: dict) -> None:
    forbidden = (
        "recommendation",
        "sku",
        "price",
        "pricing",
        "inventory",
        "purchase",
        "product_id",
        "checkout",
        "needed_for",
        "fixes",
        "heals",
    )
    for entry in registry["symbolic_asset_associations"].values():
        for field in forbidden:
            assert field not in entry


def test_no_user_id_or_personalization(registry: dict) -> None:
    for entry in registry["symbolic_asset_associations"].values():
        assert "user_id" not in entry
        assert "personalized" not in entry
        assert "profile_id" not in entry


def test_association_mode_and_status_valid(registry: dict) -> None:
    for entry in registry["symbolic_asset_associations"].values():
        assert entry["association_mode"] in ALLOWED_ASSOCIATION_MODES
        assert entry["status"] in {"draft", "active"}


def test_output_shape_stable(registry: dict) -> None:
    sample = get_symbolic_asset_association("assoc_amethyst_path_clarity", registry)
    assert set(sample.keys()) == SYMBOLIC_ASSET_ASSOCIATION_V1_KEYS


def test_validator_rejects_forbidden_recommendation_field(registry: dict) -> None:
    bad = copy.deepcopy(registry)
    bad["symbolic_asset_associations"]["assoc_amethyst_path_clarity"]["recommendation"] = True
    errors = validate_symbolic_asset_association_registry_v1(
        bad,
        context=_validation_context(),
    )
    assert any("forbidden fields" in err for err in errors)


def test_validator_rejects_invalid_asset_code(registry: dict) -> None:
    bad = copy.deepcopy(registry)
    bad["symbolic_asset_associations"]["assoc_bad_asset_path_clarity"] = copy.deepcopy(
        bad["symbolic_asset_associations"]["assoc_amethyst_path_clarity"]
    )
    entry = bad["symbolic_asset_associations"]["assoc_bad_asset_path_clarity"]
    entry["association_id"] = "assoc_bad_asset_path_clarity"
    entry["asset_code"] = "stone_for_anxiety"
    errors = validate_symbolic_asset_association_registry_v1(
        bad,
        context=_validation_context(),
    )
    assert any("stone_for_anxiety" in err for err in errors)


def test_list_helpers(registry: dict) -> None:
    amethyst_links = list_symbolic_asset_associations_for_asset("amethyst", registry)
    assert len(amethyst_links) >= 2
    path_links = list_symbolic_asset_associations_by_type("path", registry)
    assert len(path_links) == 20
