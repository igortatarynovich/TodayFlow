"""C1.6 — Load Cycle Definition registry (temporal programs linking C1.1–C1.5)."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from todayflow_backend.data.ascetic_definition_registry_loader import load_ascetic_definition_registry_v1
from todayflow_backend.data.evolution_cd_loader import load_evolution_cd_v1
from todayflow_backend.data.goal_definition_registry_loader import load_goal_definition_registry_v1
from todayflow_backend.data.habit_definition_registry_loader import load_habit_definition_registry_v1
from todayflow_backend.data.practice_definition_registry_loader import load_practice_definition_registry_v1
from todayflow_backend.data.reference_machine_loader import DATA_ROOT
from todayflow_backend.data.ritual_definition_registry_loader import load_ritual_definition_registry_v1
from todayflow_backend.data.cycle_definition_registry_validator import (
    CANONICAL_CYCLE_DEFINITION_CODES,
    CYCLE_DEFINITION_REGISTRY_V1_CONTRACT,
    CYCLE_DEFINITION_V1_KEYS,
    validate_cycle_definition_registry_v1,
)

CYCLE_DEFINITION_REGISTRY_PATH = (
    DATA_ROOT / "reference" / "practice" / "cycle_definition_registry_v1.json"
)


class CycleDefinitionRegistryError(Exception):
    """Raised when cycle definition registry is missing or invalid."""


def clear_cycle_definition_registry_cache() -> None:
    load_cycle_definition_registry_v1.cache_clear()


def _path_theme_codes_from_evolution_cd() -> frozenset[str]:
    cd = load_evolution_cd_v1()
    return frozenset((cd.get("evolution_path_themes") or {}).keys())


def _practice_codes() -> frozenset[str]:
    return frozenset((load_practice_definition_registry_v1().get("practice_definitions") or {}).keys())


def _habit_codes() -> frozenset[str]:
    return frozenset((load_habit_definition_registry_v1().get("habit_definitions") or {}).keys())


def _goal_codes() -> frozenset[str]:
    return frozenset((load_goal_definition_registry_v1().get("goal_definitions") or {}).keys())


def _ascetic_codes() -> frozenset[str]:
    return frozenset((load_ascetic_definition_registry_v1().get("ascetic_definitions") or {}).keys())


def _ritual_codes() -> frozenset[str]:
    return frozenset((load_ritual_definition_registry_v1().get("ritual_definitions") or {}).keys())


@lru_cache(maxsize=1)
def load_cycle_definition_registry_v1() -> dict[str, Any]:
    path = Path(os.getenv("TODAYFLOW_CYCLE_DEFINITION_REGISTRY_PATH", CYCLE_DEFINITION_REGISTRY_PATH))
    if not path.is_file():
        raise CycleDefinitionRegistryError(f"cycle definition registry not found: {path}")
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    errors = validate_cycle_definition_registry_v1(
        payload,
        path_theme_codes=_path_theme_codes_from_evolution_cd(),
        practice_codes=_practice_codes(),
        habit_codes=_habit_codes(),
        goal_codes=_goal_codes(),
        ascetic_codes=_ascetic_codes(),
        ritual_codes=_ritual_codes(),
    )
    if errors:
        raise CycleDefinitionRegistryError("; ".join(errors[:8]))
    return payload


def get_cycle_definition(
    code: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = registry if registry is not None else load_cycle_definition_registry_v1()
    definitions = payload.get("cycle_definitions") or {}
    entry = definitions.get(code)
    if not isinstance(entry, dict):
        raise CycleDefinitionRegistryError(f"cycle definition not found: {code!r}")
    return dict(entry)


def list_cycle_definitions_ordered(
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    payload = registry if registry is not None else load_cycle_definition_registry_v1()
    definitions = payload.get("cycle_definitions") or {}
    return [dict(definitions[code]) for code in CANONICAL_CYCLE_DEFINITION_CODES if code in definitions]


def list_cycles_for_path(
    path_theme_code: str,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return [
        cycle
        for cycle in list_cycle_definitions_ordered(registry)
        if path_theme_code in cycle.get("compatible_paths", [])
    ]


def list_cycles_by_duration(
    duration_days: int,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return [
        cycle
        for cycle in list_cycle_definitions_ordered(registry)
        if cycle.get("duration_days") == duration_days
    ]
