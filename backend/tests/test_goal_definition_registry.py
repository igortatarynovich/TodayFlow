"""C1.3 — Goal Definition registry tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache, load_evolution_cd_v1
from todayflow_backend.data.goal_definition_registry_loader import (
    GOAL_DEFINITION_REGISTRY_V1_CONTRACT,
    clear_goal_definition_registry_cache,
    get_goal_definition,
    list_goal_definitions_ordered,
    list_goals_by_type,
    list_goals_for_path,
    load_goal_definition_registry_v1,
)
from todayflow_backend.data.goal_definition_registry_validator import (
    CANONICAL_GOAL_DEFINITION_CODES,
    GOAL_DEFINITION_ALLOWED_SIGNALS,
    GOAL_DEFINITION_V1_KEYS,
    validate_goal_definition_registry_v1,
)


@pytest.fixture(autouse=True)
def _clear_caches() -> None:
    clear_evolution_cd_cache()
    clear_goal_definition_registry_cache()
    yield
    clear_evolution_cd_cache()
    clear_goal_definition_registry_cache()


@pytest.fixture
def registry() -> dict:
    return load_goal_definition_registry_v1()


def test_contract_and_ten_goals(registry: dict) -> None:
    assert registry["contract_version"] == GOAL_DEFINITION_REGISTRY_V1_CONTRACT
    assert registry["domain"] == "practice"
    goals = list_goal_definitions_ordered(registry)
    assert len(goals) == 10
    assert [g["code"] for g in goals] == list(CANONICAL_GOAL_DEFINITION_CODES)


def test_goal_schema_keys(registry: dict) -> None:
    for goal in list_goal_definitions_ordered(registry):
        assert set(goal.keys()) == GOAL_DEFINITION_V1_KEYS


def test_weekly_goals_produce_weekly_signal(registry: dict) -> None:
    weekly = list_goals_by_type("weekly", registry)
    assert len(weekly) == 6
    for goal in weekly:
        assert goal["produces_signals"] == ["weekly_goal_completed"]


def test_milestone_goals_produce_milestone_signal(registry: dict) -> None:
    milestones = list_goals_by_type("milestone", registry)
    assert len(milestones) == 2
    for goal in milestones:
        assert goal["produces_signals"] == ["goal_milestone_reached"]


def test_long_horizon_goals_produce_milestone_signal(registry: dict) -> None:
    long_horizon = list_goals_by_type("long_horizon", registry)
    assert len(long_horizon) == 2
    for goal in long_horizon:
        assert goal["produces_signals"] == ["goal_milestone_reached"]


def test_no_practice_or_habit_link_fields(registry: dict) -> None:
    forbidden = {
        "linked_practice_definition_code",
        "linked_habit_definition_code",
        "frequency_type",
        "minimum_completion_rule",
    }
    for goal in list_goal_definitions_ordered(registry):
        assert forbidden.isdisjoint(goal.keys())


def test_compatible_paths_reference_b1_1(registry: dict) -> None:
    cd = load_evolution_cd_v1()
    path_codes = set((cd.get("evolution_path_themes") or {}).keys())
    for goal in list_goal_definitions_ordered(registry):
        assert set(goal["compatible_paths"]).issubset(path_codes)


def test_list_goals_for_path_clarity(registry: dict) -> None:
    goals = list_goals_for_path("clarity", registry)
    codes = {g["code"] for g in goals}
    assert "weekly_clarity_theme" in codes
    assert "focus_sprint_week" in codes


def test_validator_rejects_practice_signal_at_goal_level(registry: dict) -> None:
    cd = load_evolution_cd_v1()
    path_codes = frozenset((cd.get("evolution_path_themes") or {}).keys())
    bad = copy.deepcopy(registry)
    bad["goal_definitions"]["weekly_clarity_theme"]["produces_signals"] = ["practice_completed"]
    errors = validate_goal_definition_registry_v1(bad, path_theme_codes=path_codes)
    assert any("practice_completed" in e for e in errors)


def test_validator_rejects_weekly_without_weekly_signal(registry: dict) -> None:
    cd = load_evolution_cd_v1()
    path_codes = frozenset((cd.get("evolution_path_themes") or {}).keys())
    bad = copy.deepcopy(registry)
    bad["goal_definitions"]["weekly_clarity_theme"]["produces_signals"] = ["goal_milestone_reached"]
    errors = validate_goal_definition_registry_v1(bad, path_theme_codes=path_codes)
    assert any("weekly_goal_completed" in e for e in errors)


def test_validator_rejects_empty_target_metric(registry: dict) -> None:
    cd = load_evolution_cd_v1()
    path_codes = frozenset((cd.get("evolution_path_themes") or {}).keys())
    bad = copy.deepcopy(registry)
    bad["goal_definitions"]["weekly_clarity_theme"]["target_metric"] = {}
    errors = validate_goal_definition_registry_v1(bad, path_theme_codes=path_codes)
    assert any("target_metric" in e for e in errors)


def test_validator_rejects_extra_content_fields(registry: dict) -> None:
    cd = load_evolution_cd_v1()
    path_codes = frozenset((cd.get("evolution_path_themes") or {}).keys())
    bad = copy.deepcopy(registry)
    bad["goal_definitions"]["weekly_clarity_theme"]["instruction_text"] = "Write three goals"
    errors = validate_goal_definition_registry_v1(bad, path_theme_codes=path_codes)
    assert any("unexpected fields" in e for e in errors)


def test_allowed_signals_subset(registry: dict) -> None:
    for goal in list_goal_definitions_ordered(registry):
        for sig in goal["produces_signals"]:
            assert sig in GOAL_DEFINITION_ALLOWED_SIGNALS


def test_habit_consistency_milestone(registry: dict) -> None:
    goal = get_goal_definition("habit_consistency_milestone", registry)
    assert goal["goal_type"] == "milestone"
    assert goal["target_metric"]["metric_type"] == "habit_streak_days"
    assert goal["target_metric"]["target_value"] == 21
