"""D1.1 — Load Symbolic Asset Definition registry (objects only, not meanings)."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from todayflow_backend.data.reference_machine_loader import DATA_ROOT
from todayflow_backend.data.symbolic_asset_definition_registry_validator import (
    CANONICAL_ASSET_CATEGORIES,
    SYMBOLIC_ASSET_DEFINITION_REGISTRY_V1_CONTRACT,
    SYMBOLIC_ASSET_DEFINITION_V1_KEYS,
    validate_symbolic_asset_definition_registry_v1,
)

SYMBOLIC_ASSET_DEFINITION_REGISTRY_PATH = (
    DATA_ROOT / "reference" / "symbolic" / "symbolic_asset_definition_registry_v1.json"
)


class SymbolicAssetDefinitionRegistryError(Exception):
    """Raised when symbolic asset definition registry is missing or invalid."""


def clear_symbolic_asset_definition_registry_cache() -> None:
    load_symbolic_asset_definition_registry_v1.cache_clear()


@lru_cache(maxsize=1)
def load_symbolic_asset_definition_registry_v1() -> dict[str, Any]:
    path = Path(
        os.getenv(
            "TODAYFLOW_SYMBOLIC_ASSET_DEFINITION_REGISTRY_PATH",
            SYMBOLIC_ASSET_DEFINITION_REGISTRY_PATH,
        )
    )
    if not path.is_file():
        raise SymbolicAssetDefinitionRegistryError(
            f"symbolic asset definition registry not found: {path}"
        )
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    errors = validate_symbolic_asset_definition_registry_v1(payload)
    if errors:
        raise SymbolicAssetDefinitionRegistryError("; ".join(errors[:8]))
    return payload


def get_symbolic_asset_definition(
    asset_code: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = registry if registry is not None else load_symbolic_asset_definition_registry_v1()
    definitions = payload.get("symbolic_asset_definitions") or {}
    entry = definitions.get(asset_code)
    if not isinstance(entry, dict):
        raise SymbolicAssetDefinitionRegistryError(
            f"symbolic asset definition not found: {asset_code!r}"
        )
    return dict(entry)


def list_symbolic_asset_definitions_by_category(
    category_code: str,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    payload = registry if registry is not None else load_symbolic_asset_definition_registry_v1()
    definitions = payload.get("symbolic_asset_definitions") or {}
    return [
        dict(entry)
        for entry in definitions.values()
        if isinstance(entry, dict) and entry.get("category_code") == category_code
    ]


def list_symbolic_asset_definitions_ordered(
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    payload = registry if registry is not None else load_symbolic_asset_definition_registry_v1()
    definitions = payload.get("symbolic_asset_definitions") or {}
    return [dict(definitions[code]) for code in sorted(definitions.keys())]
