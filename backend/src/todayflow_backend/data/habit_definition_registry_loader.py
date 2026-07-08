"""C1.2 — Load Habit Definition registry (recurrence patterns linked to C1.1)."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from todayflow_backend.data.evolution_cd_loader import load_evolution_cd_v1
from todayflow_backend.data.habit_definition_registry_validator import (
    CANONICAL_HABIT_DEFINITION_CODES,
    HABIT_DEFINITION_REGISTRY_V1_CONTRACT,
    HABIT_DEFINITION_V1_KEYS,
    validate_habit_definition_registry_v1,
)
from todayflow_backend.data.practice_definition_registry_loader import (
    load_practice_definition_registry_v1,
)
from todayflow_backend.data.reference_machine_loader import DATA_ROOT

HABIT_DEFINITION_REGISTRY_PATH = (
    DATA_ROOT / "reference" / "practice" / "habit_definition_registry_v1.json"
)


class HabitDefinitionRegistryError(Exception):
    """Raised when habit definition registry is missing or invalid."""


def clear_habit_definition_registry_cache() -> None:
    load_habit_definition_registry_v1.cache_clear()


def _path_theme_codes_from_evolution_cd() -> frozenset[str]:
    cd = load_evolution_cd_v1()
    themes = cd.get("evolution_path_themes") or {}
    return frozenset(themes.keys())


def _practice_definition_codes_from_c1_1() -> frozenset[str]:
    registry = load_practice_definition_registry_v1()
    definitions = registry.get("practice_definitions") or {}
    return frozenset(definitions.keys())


@lru_cache(maxsize=1)
def load_habit_definition_registry_v1() -> dict[str, Any]:
    path = Path(
        os.getenv("TODAYFLOW_HABIT_DEFINITION_REGISTRY_PATH", HABIT_DEFINITION_REGISTRY_PATH)
    )
    if not path.is_file():
        raise HabitDefinitionRegistryError(f"habit definition registry not found: {path}")
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    errors = validate_habit_definition_registry_v1(
        payload,
        path_theme_codes=_path_theme_codes_from_evolution_cd(),
        practice_definition_codes=_practice_definition_codes_from_c1_1(),
    )
    if errors:
        raise HabitDefinitionRegistryError("; ".join(errors[:8]))
    return payload


def get_habit_definition(
    code: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = registry if registry is not None else load_habit_definition_registry_v1()
    definitions = payload.get("habit_definitions") or {}
    entry = definitions.get(code)
    if not isinstance(entry, dict):
        raise HabitDefinitionRegistryError(f"habit definition not found: {code!r}")
    return dict(entry)


def list_habit_definitions_ordered(
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    payload = registry if registry is not None else load_habit_definition_registry_v1()
    definitions = payload.get("habit_definitions") or {}
    return [dict(definitions[code]) for code in CANONICAL_HABIT_DEFINITION_CODES if code in definitions]


def list_habits_for_practice_definition(
    practice_definition_code: str,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return [
        habit
        for habit in list_habit_definitions_ordered(registry)
        if habit.get("linked_practice_definition_code") == practice_definition_code
    ]


def list_habits_for_path(
    path_theme_code: str,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return [
        habit
        for habit in list_habit_definitions_ordered(registry)
        if path_theme_code in habit.get("compatible_paths", [])
    ]


def get_linked_practice_definition(
    habit_code: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from todayflow_backend.data.practice_definition_registry_loader import get_practice_definition

    habit = get_habit_definition(habit_code, registry)
    linked_code = habit["linked_practice_definition_code"]
    return get_practice_definition(linked_code)
