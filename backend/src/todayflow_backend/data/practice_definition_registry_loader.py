"""C1.1 — Load Practice Definition registry (action types, not content)."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from todayflow_backend.data.evolution_cd_loader import load_evolution_cd_v1
from todayflow_backend.data.practice_definition_registry_validator import (
    CANONICAL_PRACTICE_CATEGORIES,
    PRACTICE_DEFINITION_REGISTRY_V1_CONTRACT,
    PRACTICE_DEFINITION_V1_KEYS,
    validate_practice_definition_registry_v1,
)
from todayflow_backend.data.reference_machine_loader import DATA_ROOT

PRACTICE_DEFINITION_REGISTRY_PATH = (
    DATA_ROOT / "reference" / "practice" / "practice_definition_registry_v1.json"
)


class PracticeDefinitionRegistryError(Exception):
    """Raised when practice definition registry is missing or invalid."""


def clear_practice_definition_registry_cache() -> None:
    load_practice_definition_registry_v1.cache_clear()


def _path_theme_codes_from_evolution_cd() -> frozenset[str]:
    cd = load_evolution_cd_v1()
    themes = cd.get("evolution_path_themes") or {}
    return frozenset(themes.keys())


@lru_cache(maxsize=1)
def load_practice_definition_registry_v1() -> dict[str, Any]:
    path = Path(
        os.getenv("TODAYFLOW_PRACTICE_DEFINITION_REGISTRY_PATH", PRACTICE_DEFINITION_REGISTRY_PATH)
    )
    if not path.is_file():
        raise PracticeDefinitionRegistryError(f"practice definition registry not found: {path}")
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    path_theme_codes = _path_theme_codes_from_evolution_cd()
    errors = validate_practice_definition_registry_v1(
        payload,
        path_theme_codes=path_theme_codes,
    )
    if errors:
        raise PracticeDefinitionRegistryError("; ".join(errors[:8]))
    return payload


def get_practice_definition(
    code: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = registry if registry is not None else load_practice_definition_registry_v1()
    definitions = payload.get("practice_definitions") or {}
    entry = definitions.get(code)
    if not isinstance(entry, dict):
        raise PracticeDefinitionRegistryError(f"practice definition not found: {code!r}")
    return dict(entry)


def list_practice_definitions_ordered(
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    payload = registry if registry is not None else load_practice_definition_registry_v1()
    definitions = payload.get("practice_definitions") or {}
    return [dict(definitions[code]) for code in CANONICAL_PRACTICE_CATEGORIES if code in definitions]


def list_practice_definitions_for_path(
    path_theme_code: str,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return [
        definition
        for definition in list_practice_definitions_ordered(registry)
        if path_theme_code in definition.get("compatible_paths", [])
    ]


def list_produced_signal_types(
    practice_code: str,
    registry: dict[str, Any] | None = None,
) -> list[str]:
    definition = get_practice_definition(practice_code, registry)
    signals = definition.get("produces_signals") or []
    return list(signals)
