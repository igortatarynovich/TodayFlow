"""C1.1 — Practice Definition registry tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache, load_evolution_cd_v1
from todayflow_backend.data.practice_definition_registry_loader import (
    PRACTICE_DEFINITION_REGISTRY_V1_CONTRACT,
    clear_practice_definition_registry_cache,
    get_practice_definition,
    list_practice_definitions_for_path,
    list_practice_definitions_ordered,
    list_produced_signal_types,
    load_practice_definition_registry_v1,
)
from todayflow_backend.data.practice_definition_registry_validator import (
    CANONICAL_PRACTICE_CATEGORIES,
    PRACTICE_DEFINITION_ALLOWED_SIGNALS,
    PRACTICE_DEFINITION_V1_KEYS,
    validate_practice_definition_registry_v1,
)


@pytest.fixture(autouse=True)
def _clear_caches() -> None:
    clear_evolution_cd_cache()
    clear_practice_definition_registry_cache()
    yield
    clear_evolution_cd_cache()
    clear_practice_definition_registry_cache()


@pytest.fixture
def registry() -> dict:
    return load_practice_definition_registry_v1()


def test_contract_and_ten_definitions(registry: dict) -> None:
    assert registry["contract_version"] == PRACTICE_DEFINITION_REGISTRY_V1_CONTRACT
    assert registry["domain"] == "practice"
    definitions = list_practice_definitions_ordered(registry)
    assert len(definitions) == 10
    assert [d["code"] for d in definitions] == list(CANONICAL_PRACTICE_CATEGORIES)


def test_definition_schema_keys(registry: dict) -> None:
    for definition in list_practice_definitions_ordered(registry):
        assert set(definition.keys()) == PRACTICE_DEFINITION_V1_KEYS
        assert definition["code"] == definition["category"]


def test_all_definitions_produce_practice_completed(registry: dict) -> None:
    for definition in list_practice_definitions_ordered(registry):
        assert "practice_completed" in definition["produces_signals"]


def test_reflection_produces_evening_reflection(registry: dict) -> None:
    reflection = get_practice_definition("reflection", registry)
    assert reflection["produces_signals"] == [
        "practice_completed",
        "evening_reflection_confirmed",
    ]


def test_breathing_does_not_produce_reflection_signal(registry: dict) -> None:
    breathing = get_practice_definition("breathing", registry)
    assert breathing["produces_signals"] == ["practice_completed"]


def test_compatible_paths_reference_b1_1_themes(registry: dict) -> None:
    cd = load_evolution_cd_v1()
    path_codes = set((cd.get("evolution_path_themes") or {}).keys())
    for definition in list_practice_definitions_ordered(registry):
        assert set(definition["compatible_paths"]).issubset(path_codes)


def test_list_for_path_discipline(registry: dict) -> None:
    discipline_defs = list_practice_definitions_for_path("discipline", registry)
    codes = {d["code"] for d in discipline_defs}
    assert "breathing" in codes
    assert "planning" in codes
    assert "gratitude" not in codes


def test_list_produced_signal_types(registry: dict) -> None:
    assert list_produced_signal_types("reflection", registry) == [
        "practice_completed",
        "evening_reflection_confirmed",
    ]


def test_validator_rejects_habit_signal_at_definition_level(registry: dict) -> None:
    cd = load_evolution_cd_v1()
    path_codes = frozenset((cd.get("evolution_path_themes") or {}).keys())
    bad = copy.deepcopy(registry)
    bad["practice_definitions"]["breathing"]["produces_signals"] = [
        "practice_completed",
        "habit_streak_confirmed",
    ]
    errors = validate_practice_definition_registry_v1(bad, path_theme_codes=path_codes)
    assert any("habit_streak_confirmed" in e for e in errors)


def test_validator_rejects_unknown_path(registry: dict) -> None:
    cd = load_evolution_cd_v1()
    path_codes = frozenset((cd.get("evolution_path_themes") or {}).keys())
    bad = copy.deepcopy(registry)
    bad["practice_definitions"]["breathing"]["compatible_paths"].append("nonexistent_path")
    errors = validate_practice_definition_registry_v1(bad, path_theme_codes=path_codes)
    assert any("nonexistent_path" in e for e in errors)


def test_validator_requires_practice_completed(registry: dict) -> None:
    cd = load_evolution_cd_v1()
    path_codes = frozenset((cd.get("evolution_path_themes") or {}).keys())
    bad = copy.deepcopy(registry)
    bad["practice_definitions"]["breathing"]["produces_signals"] = ["evening_reflection_confirmed"]
    errors = validate_practice_definition_registry_v1(bad, path_theme_codes=path_codes)
    assert any("practice_completed" in e for e in errors)


def test_allowed_signals_subset(registry: dict) -> None:
    for definition in list_practice_definitions_ordered(registry):
        for sig in definition["produces_signals"]:
            assert sig in PRACTICE_DEFINITION_ALLOWED_SIGNALS
