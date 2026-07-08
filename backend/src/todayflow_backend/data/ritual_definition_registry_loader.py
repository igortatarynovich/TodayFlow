"""C1.5 — Load Ritual Definition registry (containers linking C1.1/C1.2/C1.4)."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from todayflow_backend.data.ascetic_definition_registry_loader import load_ascetic_definition_registry_v1
from todayflow_backend.data.evolution_cd_loader import load_evolution_cd_v1
from todayflow_backend.data.habit_definition_registry_loader import load_habit_definition_registry_v1
from todayflow_backend.data.practice_definition_registry_loader import load_practice_definition_registry_v1
from todayflow_backend.data.reference_machine_loader import DATA_ROOT
from todayflow_backend.data.ritual_definition_registry_validator import (
    CANONICAL_RITUAL_DEFINITION_CODES,
    RITUAL_DEFINITION_REGISTRY_V1_CONTRACT,
    RITUAL_DEFINITION_V1_KEYS,
    validate_ritual_definition_registry_v1,
)

RITUAL_DEFINITION_REGISTRY_PATH = (
    DATA_ROOT / "reference" / "practice" / "ritual_definition_registry_v1.json"
)


class RitualDefinitionRegistryError(Exception):
    """Raised when ritual definition registry is missing or invalid."""


def clear_ritual_definition_registry_cache() -> None:
    load_ritual_definition_registry_v1.cache_clear()


def _path_theme_codes_from_evolution_cd() -> frozenset[str]:
    cd = load_evolution_cd_v1()
    themes = cd.get("evolution_path_themes") or {}
    return frozenset(themes.keys())


def _practice_codes_from_c1_1() -> frozenset[str]:
    registry = load_practice_definition_registry_v1()
    return frozenset((registry.get("practice_definitions") or {}).keys())


def _habit_codes_from_c1_2() -> frozenset[str]:
    registry = load_habit_definition_registry_v1()
    return frozenset((registry.get("habit_definitions") or {}).keys())


def _ascetic_codes_from_c1_4() -> frozenset[str]:
    registry = load_ascetic_definition_registry_v1()
    return frozenset((registry.get("ascetic_definitions") or {}).keys())


@lru_cache(maxsize=1)
def load_ritual_definition_registry_v1() -> dict[str, Any]:
    path = Path(
        os.getenv("TODAYFLOW_RITUAL_DEFINITION_REGISTRY_PATH", RITUAL_DEFINITION_REGISTRY_PATH)
    )
    if not path.is_file():
        raise RitualDefinitionRegistryError(f"ritual definition registry not found: {path}")
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    errors = validate_ritual_definition_registry_v1(
        payload,
        path_theme_codes=_path_theme_codes_from_evolution_cd(),
        practice_codes=_practice_codes_from_c1_1(),
        habit_codes=_habit_codes_from_c1_2(),
        ascetic_codes=_ascetic_codes_from_c1_4(),
    )
    if errors:
        raise RitualDefinitionRegistryError("; ".join(errors[:8]))
    return payload


def get_ritual_definition(
    code: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = registry if registry is not None else load_ritual_definition_registry_v1()
    definitions = payload.get("ritual_definitions") or {}
    entry = definitions.get(code)
    if not isinstance(entry, dict):
        raise RitualDefinitionRegistryError(f"ritual definition not found: {code!r}")
    return dict(entry)


def list_ritual_definitions_ordered(
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    payload = registry if registry is not None else load_ritual_definition_registry_v1()
    definitions = payload.get("ritual_definitions") or {}
    return [dict(definitions[code]) for code in CANONICAL_RITUAL_DEFINITION_CODES if code in definitions]


def list_rituals_for_path(
    path_theme_code: str,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return [
        ritual
        for ritual in list_ritual_definitions_ordered(registry)
        if path_theme_code in ritual.get("compatible_paths", [])
    ]


def list_rituals_by_category(
    ritual_category: str,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return [
        ritual
        for ritual in list_ritual_definitions_ordered(registry)
        if ritual.get("ritual_category") == ritual_category
    ]
