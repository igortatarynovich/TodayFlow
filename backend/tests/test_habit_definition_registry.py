"""C1.2 — Habit Definition registry tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache, load_evolution_cd_v1
from todayflow_backend.data.habit_definition_registry_loader import (
    HABIT_DEFINITION_REGISTRY_V1_CONTRACT,
    clear_habit_definition_registry_cache,
    get_habit_definition,
    get_linked_practice_definition,
    list_habit_definitions_ordered,
    list_habits_for_practice_definition,
    list_habits_for_path,
    load_habit_definition_registry_v1,
)
from todayflow_backend.data.habit_definition_registry_validator import (
    CANONICAL_HABIT_DEFINITION_CODES,
    HABIT_DEFINITION_ALLOWED_SIGNALS,
    HABIT_DEFINITION_V1_KEYS,
    validate_habit_definition_registry_v1,
)
from todayflow_backend.data.practice_definition_registry_loader import (
    clear_practice_definition_registry_cache,
    load_practice_definition_registry_v1,
)


@pytest.fixture(autouse=True)
def _clear_caches() -> None:
    clear_evolution_cd_cache()
    clear_practice_definition_registry_cache()
    clear_habit_definition_registry_cache()
    yield
    clear_evolution_cd_cache()
    clear_practice_definition_registry_cache()
    clear_habit_definition_registry_cache()


@pytest.fixture
def registry() -> dict:
    return load_habit_definition_registry_v1()


def test_contract_and_ten_habits(registry: dict) -> None:
    assert registry["contract_version"] == HABIT_DEFINITION_REGISTRY_V1_CONTRACT
    assert registry["domain"] == "practice"
    habits = list_habit_definitions_ordered(registry)
    assert len(habits) == 10
    assert [h["code"] for h in habits] == list(CANONICAL_HABIT_DEFINITION_CODES)


def test_habit_schema_keys(registry: dict) -> None:
    for habit in list_habit_definitions_ordered(registry):
        assert set(habit.keys()) == HABIT_DEFINITION_V1_KEYS


def test_all_habits_link_to_c1_1_practice(registry: dict) -> None:
    practice_codes = set((load_practice_definition_registry_v1().get("practice_definitions") or {}).keys())
    for habit in list_habit_definitions_ordered(registry):
        assert habit["linked_practice_definition_code"] in practice_codes


def test_all_habits_produce_streak_signal(registry: dict) -> None:
    for habit in list_habit_definitions_ordered(registry):
        assert habit["produces_signals"] == ["practice_completed", "habit_streak_confirmed"]


def test_evening_reflection_links_reflection_practice(registry: dict) -> None:
    habit = get_habit_definition("evening_reflection", registry)
    assert habit["linked_practice_definition_code"] == "reflection"
    practice = get_linked_practice_definition("evening_reflection", registry)
    assert practice["code"] == "reflection"


def test_list_habits_for_practice_definition(registry: dict) -> None:
    breathing_habits = list_habits_for_practice_definition("breathing", registry)
    assert len(breathing_habits) == 1
    assert breathing_habits[0]["code"] == "daily_breathing"


def test_list_habits_for_path_discipline(registry: dict) -> None:
    habits = list_habits_for_path("discipline", registry)
    codes = {h["code"] for h in habits}
    assert "daily_breathing" in codes
    assert "attention_training" in codes


def test_compatible_paths_reference_b1_1(registry: dict) -> None:
    cd = load_evolution_cd_v1()
    path_codes = set((cd.get("evolution_path_themes") or {}).keys())
    for habit in list_habit_definitions_ordered(registry):
        assert set(habit["compatible_paths"]).issubset(path_codes)


def test_validator_rejects_unknown_practice_link(registry: dict) -> None:
    cd = load_evolution_cd_v1()
    path_codes = frozenset((cd.get("evolution_path_themes") or {}).keys())
    practice_codes = frozenset(
        (load_practice_definition_registry_v1().get("practice_definitions") or {}).keys()
    )
    bad = copy.deepcopy(registry)
    bad["habit_definitions"]["daily_breathing"]["linked_practice_definition_code"] = "nonexistent"
    errors = validate_habit_definition_registry_v1(
        bad,
        path_theme_codes=path_codes,
        practice_definition_codes=practice_codes,
    )
    assert any("nonexistent" in e for e in errors)


def test_validator_rejects_ritual_signal_at_habit_level(registry: dict) -> None:
    cd = load_evolution_cd_v1()
    path_codes = frozenset((cd.get("evolution_path_themes") or {}).keys())
    practice_codes = frozenset(
        (load_practice_definition_registry_v1().get("practice_definitions") or {}).keys()
    )
    bad = copy.deepcopy(registry)
    bad["habit_definitions"]["daily_breathing"]["produces_signals"] = [
        "practice_completed",
        "ritual_streak_confirmed",
    ]
    errors = validate_habit_definition_registry_v1(
        bad,
        path_theme_codes=path_codes,
        practice_definition_codes=practice_codes,
    )
    assert any("ritual_streak_confirmed" in e for e in errors)


def test_validator_rejects_empty_minimum_completion_rule(registry: dict) -> None:
    cd = load_evolution_cd_v1()
    path_codes = frozenset((cd.get("evolution_path_themes") or {}).keys())
    practice_codes = frozenset(
        (load_practice_definition_registry_v1().get("practice_definitions") or {}).keys()
    )
    bad = copy.deepcopy(registry)
    bad["habit_definitions"]["daily_breathing"]["minimum_completion_rule"] = {}
    errors = validate_habit_definition_registry_v1(
        bad,
        path_theme_codes=path_codes,
        practice_definition_codes=practice_codes,
    )
    assert any("minimum_completion_rule" in e for e in errors)


def test_validator_rejects_extra_content_fields(registry: dict) -> None:
    cd = load_evolution_cd_v1()
    path_codes = frozenset((cd.get("evolution_path_themes") or {}).keys())
    practice_codes = frozenset(
        (load_practice_definition_registry_v1().get("practice_definitions") or {}).keys()
    )
    bad = copy.deepcopy(registry)
    bad["habit_definitions"]["daily_breathing"]["instruction_text"] = "Do 4-7-8 breathing"
    errors = validate_habit_definition_registry_v1(
        bad,
        path_theme_codes=path_codes,
        practice_definition_codes=practice_codes,
    )
    assert any("unexpected fields" in e for e in errors)


def test_allowed_signals_subset(registry: dict) -> None:
    for habit in list_habit_definitions_ordered(registry):
        for sig in habit["produces_signals"]:
            assert sig in HABIT_DEFINITION_ALLOWED_SIGNALS
