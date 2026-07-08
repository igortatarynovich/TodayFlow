"""C1.6 — Cycle Definition registry tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.ascetic_definition_registry_loader import (
    clear_ascetic_definition_registry_cache,
    load_ascetic_definition_registry_v1,
)
from todayflow_backend.data.cycle_definition_registry_loader import (
    CYCLE_DEFINITION_REGISTRY_V1_CONTRACT,
    clear_cycle_definition_registry_cache,
    get_cycle_definition,
    list_cycle_definitions_ordered,
    list_cycles_by_duration,
    list_cycles_for_path,
    load_cycle_definition_registry_v1,
)
from todayflow_backend.data.cycle_definition_registry_validator import (
    CANONICAL_CYCLE_DEFINITION_CODES,
    CYCLE_DEFINITION_ALLOWED_SIGNALS,
    CYCLE_DEFINITION_V1_KEYS,
    validate_cycle_definition_registry_v1,
)
from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache, load_evolution_cd_v1
from todayflow_backend.data.goal_definition_registry_loader import (
    clear_goal_definition_registry_cache,
    load_goal_definition_registry_v1,
)
from todayflow_backend.data.habit_definition_registry_loader import (
    clear_habit_definition_registry_cache,
    load_habit_definition_registry_v1,
)
from todayflow_backend.data.practice_definition_registry_loader import (
    clear_practice_definition_registry_cache,
    load_practice_definition_registry_v1,
)
from todayflow_backend.data.ritual_definition_registry_loader import (
    clear_ritual_definition_registry_cache,
    load_ritual_definition_registry_v1,
)


@pytest.fixture(autouse=True)
def _clear_caches() -> None:
    clear_evolution_cd_cache()
    clear_practice_definition_registry_cache()
    clear_habit_definition_registry_cache()
    clear_goal_definition_registry_cache()
    clear_ascetic_definition_registry_cache()
    clear_ritual_definition_registry_cache()
    clear_cycle_definition_registry_cache()
    yield
    clear_evolution_cd_cache()
    clear_practice_definition_registry_cache()
    clear_habit_definition_registry_cache()
    clear_goal_definition_registry_cache()
    clear_ascetic_definition_registry_cache()
    clear_ritual_definition_registry_cache()
    clear_cycle_definition_registry_cache()


@pytest.fixture
def registry() -> dict:
    return load_cycle_definition_registry_v1()


def test_contract_and_eight_cycles(registry: dict) -> None:
    assert registry["contract_version"] == CYCLE_DEFINITION_REGISTRY_V1_CONTRACT
    cycles = list_cycle_definitions_ordered(registry)
    assert len(cycles) == 8
    assert [c["code"] for c in cycles] == list(CANONICAL_CYCLE_DEFINITION_CODES)


def test_cycle_schema_keys(registry: dict) -> None:
    for cycle in list_cycle_definitions_ordered(registry):
        assert set(cycle.keys()) == CYCLE_DEFINITION_V1_KEYS


def test_all_cycles_produce_cycle_completed_only(registry: dict) -> None:
    for cycle in list_cycle_definitions_ordered(registry):
        assert cycle["produces_signals"] == ["cycle_completed"]
        for sig in cycle["produces_signals"]:
            assert sig in CYCLE_DEFINITION_ALLOWED_SIGNALS


def test_duration_days_align_b1_1(registry: dict) -> None:
    allowed = {7, 21, 30, 90}
    for cycle in list_cycle_definitions_ordered(registry):
        assert cycle["duration_days"] in allowed


def test_component_count_matches(registry: dict) -> None:
    for cycle in list_cycle_definitions_ordered(registry):
        assert cycle["component_count"] == len(cycle["components"])


def test_ninety_day_architect_includes_all_entity_types(registry: dict) -> None:
    cycle = get_cycle_definition("ninety_day_architect_cycle", registry)
    types = {c["component_type"] for c in cycle["components"]}
    assert types == {"goal", "ritual", "habit"}


def test_digital_boundary_cycle(registry: dict) -> None:
    cycle = get_cycle_definition("twenty_one_day_digital_boundary_cycle", registry)
    ascetics = [c for c in cycle["components"] if c["component_type"] == "ascetic"]
    assert len(ascetics) == 2


def test_primary_path_in_compatible_paths(registry: dict) -> None:
    for cycle in list_cycle_definitions_ordered(registry):
        assert cycle["primary_path_theme"] in cycle["compatible_paths"]


def test_list_cycles_by_duration_21(registry: dict) -> None:
    cycles = list_cycles_by_duration(21, registry)
    assert len(cycles) == 4


def test_list_cycles_for_path_discipline(registry: dict) -> None:
    cycles = list_cycles_for_path("discipline", registry)
    codes = {c["code"] for c in cycles}
    assert "twenty_one_day_discipline_cycle" in codes


def test_validator_rejects_unknown_ritual_component(registry: dict) -> None:
    refs = _registry_refs()
    bad = copy.deepcopy(registry)
    bad["cycle_definitions"]["seven_day_energy_reset"]["components"][0]["component_code"] = "missing"
    errors = validate_cycle_definition_registry_v1(bad, **refs)
    assert any("missing" in e for e in errors)


def test_validator_rejects_non_cycle_signal(registry: dict) -> None:
    refs = _registry_refs()
    bad = copy.deepcopy(registry)
    bad["cycle_definitions"]["seven_day_energy_reset"]["produces_signals"] = ["habit_streak_confirmed"]
    errors = validate_cycle_definition_registry_v1(bad, **refs)
    assert any("habit_streak_confirmed" in e for e in errors)


def test_validator_rejects_invalid_duration(registry: dict) -> None:
    refs = _registry_refs()
    bad = copy.deepcopy(registry)
    bad["cycle_definitions"]["seven_day_energy_reset"]["duration_days"] = 14
    errors = validate_cycle_definition_registry_v1(bad, **refs)
    assert any("duration_days" in e for e in errors)


def test_validator_rejects_user_progress_field(registry: dict) -> None:
    refs = _registry_refs()
    bad = copy.deepcopy(registry)
    bad["cycle_definitions"]["seven_day_energy_reset"]["user_progress"] = {}
    errors = validate_cycle_definition_registry_v1(bad, **refs)
    assert any("forbidden runtime" in e for e in errors)


def _registry_refs() -> dict:
    cd = load_evolution_cd_v1()
    return {
        "path_theme_codes": frozenset((cd.get("evolution_path_themes") or {}).keys()),
        "practice_codes": frozenset(
            (load_practice_definition_registry_v1().get("practice_definitions") or {}).keys()
        ),
        "habit_codes": frozenset(
            (load_habit_definition_registry_v1().get("habit_definitions") or {}).keys()
        ),
        "goal_codes": frozenset(
            (load_goal_definition_registry_v1().get("goal_definitions") or {}).keys()
        ),
        "ascetic_codes": frozenset(
            (load_ascetic_definition_registry_v1().get("ascetic_definitions") or {}).keys()
        ),
        "ritual_codes": frozenset(
            (load_ritual_definition_registry_v1().get("ritual_definitions") or {}).keys()
        ),
    }
