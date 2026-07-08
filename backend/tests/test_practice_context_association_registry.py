"""C1.7 — Practice Context Association registry tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.evolution_cd_loader import load_evolution_cd_v1
from todayflow_backend.data.practice_context_association_registry_loader import (
    clear_practice_context_association_registry_cache,
    get_practice_context_association,
    list_practice_context_associations_by_source_type,
    list_practice_context_associations_for_context,
    list_practice_context_associations_for_practice,
    load_practice_context_association_registry_v1,
)
from todayflow_backend.data.practice_context_association_registry_validator import (
    ALLOWED_ASSOCIATION_MODES,
    ALLOWED_DIRECTIONS,
    ALLOWED_SOURCE_TYPES,
    PRACTICE_CONTEXT_ASSOCIATION_REGISTRY_V1_CONTRACT,
    PRACTICE_CONTEXT_ASSOCIATION_V1_KEYS,
    default_validation_context,
    validate_practice_context_association_registry_v1,
)
from todayflow_backend.data.practice_definition_registry_loader import (
    load_practice_definition_registry_v1,
)


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    clear_practice_context_association_registry_cache()
    yield
    clear_practice_context_association_registry_cache()


@pytest.fixture
def registry() -> dict:
    return load_practice_context_association_registry_v1()


def _validation_context() -> object:
    defs = load_practice_definition_registry_v1()["practice_definitions"]
    cd = load_evolution_cd_v1()
    return default_validation_context(
        practice_codes=frozenset(defs.keys()),
        path_theme_codes=frozenset((cd.get("evolution_path_themes") or {}).keys()),
    )


def test_registry_loads(registry: dict) -> None:
    assert registry["contract_version"] == PRACTICE_CONTEXT_ASSOCIATION_REGISTRY_V1_CONTRACT
    assert registry["domain"] == "practice"
    assert 80 <= len(registry["practice_context_associations"]) <= 120


def test_practice_code_exists_in_c1_1(registry: dict) -> None:
    defs = load_practice_definition_registry_v1()["practice_definitions"]
    for entry in registry["practice_context_associations"].values():
        assert entry["practice_definition_code"] in defs


def test_source_type_valid(registry: dict) -> None:
    for entry in registry["practice_context_associations"].values():
        assert entry["source_type"] in ALLOWED_SOURCE_TYPES


def test_source_ref_valid_for_type(registry: dict) -> None:
    errors = validate_practice_context_association_registry_v1(
        registry,
        context=_validation_context(),
    )
    assert errors == []


def test_strength_and_confidence_in_range(registry: dict) -> None:
    for entry in registry["practice_context_associations"].values():
        assert 0 <= entry["strength"] <= 1
        assert 0 <= entry["confidence"] <= 1


def test_no_recommendation_or_forbidden_fields(registry: dict) -> None:
    forbidden = (
        "recommendation",
        "final_selection",
        "sku",
        "prompt",
        "llm_output",
        "needed_for",
        "fixes",
        "heals",
    )
    for entry in registry["practice_context_associations"].values():
        for field in forbidden:
            assert field not in entry


def test_no_user_id_or_personalization(registry: dict) -> None:
    for entry in registry["practice_context_associations"].values():
        assert "user_id" not in entry
        assert "personalized" not in entry
        assert "profile_id" not in entry


def test_association_mode_direction_status_valid(registry: dict) -> None:
    for entry in registry["practice_context_associations"].values():
        assert entry["association_mode"] in ALLOWED_ASSOCIATION_MODES
        assert entry["direction"] in ALLOWED_DIRECTIONS
        assert entry["status"] in {"draft", "active"}


def test_negative_edges_have_contraindication_level(registry: dict) -> None:
    negatives = [
        e for e in registry["practice_context_associations"].values() if e["direction"] == "negative"
    ]
    assert len(negatives) >= 3
    for entry in negatives:
        assert entry["contraindication_level"] in {"advisory", "moderate", "strict"}


def test_positive_edges_have_none_contraindication(registry: dict) -> None:
    for entry in registry["practice_context_associations"].values():
        if entry["direction"] == "positive":
            assert entry["contraindication_level"] == "none"


def test_output_shape_stable(registry: dict) -> None:
    sample = get_practice_context_association("pca_strategy_recover_reflection", registry)
    assert set(sample.keys()) == PRACTICE_CONTEXT_ASSOCIATION_V1_KEYS


def test_validator_rejects_forbidden_recommendation_field(registry: dict) -> None:
    bad = copy.deepcopy(registry)
    bad["practice_context_associations"]["pca_strategy_recover_reflection"]["recommendation"] = True
    errors = validate_practice_context_association_registry_v1(
        bad,
        context=_validation_context(),
    )
    assert any("forbidden fields" in err for err in errors)


def test_validator_rejects_invalid_practice_code(registry: dict) -> None:
    bad = copy.deepcopy(registry)
    bad["practice_context_associations"]["pca_bad_practice_link"] = copy.deepcopy(
        bad["practice_context_associations"]["pca_strategy_recover_reflection"]
    )
    entry = bad["practice_context_associations"]["pca_bad_practice_link"]
    entry["association_id"] = "pca_bad_practice_link"
    entry["practice_definition_code"] = "unknown_practice"
    errors = validate_practice_context_association_registry_v1(
        bad,
        context=_validation_context(),
    )
    assert any("unknown_practice" in err for err in errors)


def test_validator_rejects_negative_without_contraindication(registry: dict) -> None:
    bad = copy.deepcopy(registry)
    entry = bad["practice_context_associations"]["pca_rhythm_overload_block_body_activation"]
    entry["contraindication_level"] = "none"
    errors = validate_practice_context_association_registry_v1(
        bad,
        context=_validation_context(),
    )
    assert any("negative direction requires" in err for err in errors)


def test_list_helpers(registry: dict) -> None:
    recover_links = list_practice_context_associations_for_context(
        "daymodel_strategy",
        "recover",
        registry,
    )
    assert len(recover_links) >= 2
    reflection_links = list_practice_context_associations_for_practice("reflection", registry)
    assert len(reflection_links) >= 5
    strategy_links = list_practice_context_associations_by_source_type("daymodel_strategy", registry)
    assert len(strategy_links) == 20


def test_recover_vs_plan_causality_seed(registry: dict) -> None:
    recover = {
        e["practice_definition_code"]
        for e in list_practice_context_associations_for_context(
            "daymodel_strategy", "recover", registry
        )
    }
    plan = {
        e["practice_definition_code"]
        for e in list_practice_context_associations_for_context(
            "daymodel_strategy", "plan", registry
        )
    }
    assert "reflection" in recover
    assert "planning" in plan
    assert "planning" not in recover
