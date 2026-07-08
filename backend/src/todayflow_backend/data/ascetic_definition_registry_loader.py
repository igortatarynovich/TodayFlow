"""C1.4 — Load Ascetic Definition registry (restrictions, not habits or goals)."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from todayflow_backend.data.ascetic_definition_registry_validator import (
    ASCETIC_DEFINITION_REGISTRY_V1_CONTRACT,
    CANONICAL_ASCETIC_DEFINITION_CODES,
    ASCETIC_DEFINITION_V1_KEYS,
    validate_ascetic_definition_registry_v1,
)
from todayflow_backend.data.evolution_cd_loader import load_evolution_cd_v1
from todayflow_backend.data.reference_machine_loader import DATA_ROOT

ASCETIC_DEFINITION_REGISTRY_PATH = (
    DATA_ROOT / "reference" / "practice" / "ascetic_definition_registry_v1.json"
)


class AsceticDefinitionRegistryError(Exception):
    """Raised when ascetic definition registry is missing or invalid."""


def clear_ascetic_definition_registry_cache() -> None:
    load_ascetic_definition_registry_v1.cache_clear()


def _path_theme_codes_from_evolution_cd() -> frozenset[str]:
    cd = load_evolution_cd_v1()
    themes = cd.get("evolution_path_themes") or {}
    return frozenset(themes.keys())


@lru_cache(maxsize=1)
def load_ascetic_definition_registry_v1() -> dict[str, Any]:
    path = Path(
        os.getenv("TODAYFLOW_ASCETIC_DEFINITION_REGISTRY_PATH", ASCETIC_DEFINITION_REGISTRY_PATH)
    )
    if not path.is_file():
        raise AsceticDefinitionRegistryError(f"ascetic definition registry not found: {path}")
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    errors = validate_ascetic_definition_registry_v1(
        payload,
        path_theme_codes=_path_theme_codes_from_evolution_cd(),
    )
    if errors:
        raise AsceticDefinitionRegistryError("; ".join(errors[:8]))
    return payload


def get_ascetic_definition(
    code: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = registry if registry is not None else load_ascetic_definition_registry_v1()
    definitions = payload.get("ascetic_definitions") or {}
    entry = definitions.get(code)
    if not isinstance(entry, dict):
        raise AsceticDefinitionRegistryError(f"ascetic definition not found: {code!r}")
    return dict(entry)


def list_ascetic_definitions_ordered(
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    payload = registry if registry is not None else load_ascetic_definition_registry_v1()
    definitions = payload.get("ascetic_definitions") or {}
    return [dict(definitions[code]) for code in CANONICAL_ASCETIC_DEFINITION_CODES if code in definitions]


def list_ascetics_for_path(
    path_theme_code: str,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return [
        ascetic
        for ascetic in list_ascetic_definitions_ordered(registry)
        if path_theme_code in ascetic.get("compatible_paths", [])
    ]


def list_ascetics_requiring_safety_note(
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return [
        ascetic
        for ascetic in list_ascetic_definitions_ordered(registry)
        if ascetic.get("requires_safety_note") is True
    ]
