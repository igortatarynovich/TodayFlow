"""C1.4 — Ascetic Definition registry tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.ascetic_definition_registry_loader import (
    ASCETIC_DEFINITION_REGISTRY_V1_CONTRACT,
    clear_ascetic_definition_registry_cache,
    get_ascetic_definition,
    list_ascetic_definitions_ordered,
    list_ascetics_for_path,
    list_ascetics_requiring_safety_note,
    load_ascetic_definition_registry_v1,
)
from todayflow_backend.data.ascetic_definition_registry_validator import (
    ASCETIC_CATEGORIES_REQUIRING_SAFETY_NOTE,
    ASCETIC_POTENTIAL_SIGNAL_TYPES,
    CANONICAL_ASCETIC_DEFINITION_CODES,
    ASCETIC_DEFINITION_V1_KEYS,
    validate_ascetic_definition_registry_v1,
)
from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache, load_evolution_cd_v1


@pytest.fixture(autouse=True)
def _clear_caches() -> None:
    clear_evolution_cd_cache()
    clear_ascetic_definition_registry_cache()
    yield
    clear_evolution_cd_cache()
    clear_ascetic_definition_registry_cache()


@pytest.fixture
def registry() -> dict:
    return load_ascetic_definition_registry_v1()


def test_contract_and_ten_ascetics(registry: dict) -> None:
    assert registry["contract_version"] == ASCETIC_DEFINITION_REGISTRY_V1_CONTRACT
    assert registry["domain"] == "practice"
    ascetics = list_ascetic_definitions_ordered(registry)
    assert len(ascetics) == 10
    assert [a["code"] for a in ascetics] == list(CANONICAL_ASCETIC_DEFINITION_CODES)


def test_ascetic_schema_keys(registry: dict) -> None:
    for ascetic in list_ascetic_definitions_ordered(registry):
        assert set(ascetic.keys()) == ASCETIC_DEFINITION_V1_KEYS


def test_produces_signals_empty_at_cd_level(registry: dict) -> None:
    for ascetic in list_ascetic_definitions_ordered(registry):
        assert ascetic["produces_signals"] == []


def test_potential_signal_types_only_practice_completed(registry: dict) -> None:
    for ascetic in list_ascetic_definitions_ordered(registry):
        assert ascetic["potential_signal_types"] == ["practice_completed"]
        for sig in ascetic["potential_signal_types"]:
            assert sig in ASCETIC_POTENTIAL_SIGNAL_TYPES


def test_no_habit_goal_practice_fields(registry: dict) -> None:
    forbidden = {
        "linked_practice_definition_code",
        "linked_habit_definition_code",
        "frequency_type",
        "goal_type",
        "target_metric",
        "horizon",
        "minimum_completion_rule",
    }
    for ascetic in list_ascetic_definitions_ordered(registry):
        assert forbidden.isdisjoint(ascetic.keys())


def test_risky_categories_require_safety_note(registry: dict) -> None:
    safety = list_ascetics_requiring_safety_note(registry)
    assert len(safety) == 5
    for ascetic in list_ascetic_definitions_ordered(registry):
        if ascetic["ascetic_category"] in ASCETIC_CATEGORIES_REQUIRING_SAFETY_NOTE:
            assert ascetic["requires_safety_note"] is True
            assert ascetic["contraindications"]


def test_no_sugar_safety(registry: dict) -> None:
    ascetic = get_ascetic_definition("no_sugar", registry)
    assert ascetic["ascetic_category"] == "food"
    assert ascetic["requires_safety_note"] is True
    assert "eating_disorder_history" in ascetic["contraindications"]


def test_compatible_paths_reference_b1_1(registry: dict) -> None:
    cd = load_evolution_cd_v1()
    path_codes = set((cd.get("evolution_path_themes") or {}).keys())
    for ascetic in list_ascetic_definitions_ordered(registry):
        assert set(ascetic["compatible_paths"]).issubset(path_codes)


def test_list_ascetics_for_path_discipline(registry: dict) -> None:
    ascetics = list_ascetics_for_path("discipline", registry)
    codes = {a["code"] for a in ascetics}
    assert "morning_no_phone" in codes
    assert "no_multitasking" in codes


def test_validator_rejects_nonempty_produces_signals(registry: dict) -> None:
    cd = load_evolution_cd_v1()
    path_codes = frozenset((cd.get("evolution_path_themes") or {}).keys())
    bad = copy.deepcopy(registry)
    bad["ascetic_definitions"]["morning_no_phone"]["produces_signals"] = ["practice_completed"]
    errors = validate_ascetic_definition_registry_v1(bad, path_theme_codes=path_codes)
    assert any("produces_signals must be empty" in e for e in errors)


def test_validator_rejects_habit_streak_potential_signal(registry: dict) -> None:
    cd = load_evolution_cd_v1()
    path_codes = frozenset((cd.get("evolution_path_themes") or {}).keys())
    bad = copy.deepcopy(registry)
    bad["ascetic_definitions"]["morning_no_phone"]["potential_signal_types"] = ["habit_streak_confirmed"]
    errors = validate_ascetic_definition_registry_v1(bad, path_theme_codes=path_codes)
    assert any("habit_streak_confirmed" in e for e in errors)


def test_validator_rejects_food_without_safety_note(registry: dict) -> None:
    cd = load_evolution_cd_v1()
    path_codes = frozenset((cd.get("evolution_path_themes") or {}).keys())
    bad = copy.deepcopy(registry)
    bad["ascetic_definitions"]["no_sugar"]["requires_safety_note"] = False
    errors = validate_ascetic_definition_registry_v1(bad, path_theme_codes=path_codes)
    assert any("requires_safety_note must be true" in e for e in errors)


def test_validator_rejects_habit_field(registry: dict) -> None:
    cd = load_evolution_cd_v1()
    path_codes = frozenset((cd.get("evolution_path_themes") or {}).keys())
    bad = copy.deepcopy(registry)
    bad["ascetic_definitions"]["morning_no_phone"]["frequency_type"] = "daily"
    errors = validate_ascetic_definition_registry_v1(bad, path_theme_codes=path_codes)
    assert any("forbidden habit/goal/practice fields" in e for e in errors)


def test_validator_rejects_invalid_duration(registry: dict) -> None:
    cd = load_evolution_cd_v1()
    path_codes = frozenset((cd.get("evolution_path_themes") or {}).keys())
    bad = copy.deepcopy(registry)
    bad["ascetic_definitions"]["morning_no_phone"]["suggested_duration_days"] = 14
    errors = validate_ascetic_definition_registry_v1(bad, path_theme_codes=path_codes)
    assert any("suggested_duration_days" in e for e in errors)
