"""C1.3 — Load Goal Definition registry (desired outcomes, not actions)."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from todayflow_backend.data.evolution_cd_loader import load_evolution_cd_v1
from todayflow_backend.data.goal_definition_registry_validator import (
    CANONICAL_GOAL_DEFINITION_CODES,
    GOAL_DEFINITION_REGISTRY_V1_CONTRACT,
    GOAL_DEFINITION_V1_KEYS,
    validate_goal_definition_registry_v1,
)
from todayflow_backend.data.reference_machine_loader import DATA_ROOT

GOAL_DEFINITION_REGISTRY_PATH = (
    DATA_ROOT / "reference" / "practice" / "goal_definition_registry_v1.json"
)


class GoalDefinitionRegistryError(Exception):
    """Raised when goal definition registry is missing or invalid."""


def clear_goal_definition_registry_cache() -> None:
    load_goal_definition_registry_v1.cache_clear()


def _path_theme_codes_from_evolution_cd() -> frozenset[str]:
    cd = load_evolution_cd_v1()
    themes = cd.get("evolution_path_themes") or {}
    return frozenset(themes.keys())


@lru_cache(maxsize=1)
def load_goal_definition_registry_v1() -> dict[str, Any]:
    path = Path(os.getenv("TODAYFLOW_GOAL_DEFINITION_REGISTRY_PATH", GOAL_DEFINITION_REGISTRY_PATH))
    if not path.is_file():
        raise GoalDefinitionRegistryError(f"goal definition registry not found: {path}")
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    errors = validate_goal_definition_registry_v1(
        payload,
        path_theme_codes=_path_theme_codes_from_evolution_cd(),
    )
    if errors:
        raise GoalDefinitionRegistryError("; ".join(errors[:8]))
    return payload


def get_goal_definition(
    code: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = registry if registry is not None else load_goal_definition_registry_v1()
    definitions = payload.get("goal_definitions") or {}
    entry = definitions.get(code)
    if not isinstance(entry, dict):
        raise GoalDefinitionRegistryError(f"goal definition not found: {code!r}")
    return dict(entry)


def list_goal_definitions_ordered(
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    payload = registry if registry is not None else load_goal_definition_registry_v1()
    definitions = payload.get("goal_definitions") or {}
    return [dict(definitions[code]) for code in CANONICAL_GOAL_DEFINITION_CODES if code in definitions]


def list_goals_for_path(
    path_theme_code: str,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return [
        goal
        for goal in list_goal_definitions_ordered(registry)
        if path_theme_code in goal.get("compatible_paths", [])
    ]


def list_goals_by_type(
    goal_type: str,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return [
        goal
        for goal in list_goal_definitions_ordered(registry)
        if goal.get("goal_type") == goal_type
    ]
