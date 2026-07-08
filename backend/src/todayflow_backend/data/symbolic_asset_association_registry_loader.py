"""D1.2 — Load Symbolic Asset Association registry (links only, not recommendations)."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from todayflow_backend.data.evolution_cd_loader import load_evolution_cd_v1
from todayflow_backend.data.reference_machine_loader import DATA_ROOT
from todayflow_backend.data.symbolic_asset_association_registry_validator import (
    SYMBOLIC_ASSET_ASSOCIATION_REGISTRY_V1_CONTRACT,
    default_validation_context,
    validate_symbolic_asset_association_registry_v1,
)
from todayflow_backend.data.symbolic_asset_definition_registry_loader import (
    load_symbolic_asset_definition_registry_v1,
)

SYMBOLIC_ASSET_ASSOCIATION_REGISTRY_PATH = (
    DATA_ROOT
    / "reference"
    / "symbolic"
    / "symbolic_asset_association_registry_v1.json"
)


class SymbolicAssetAssociationRegistryError(Exception):
    """Raised when symbolic asset association registry is missing or invalid."""


def clear_symbolic_asset_association_registry_cache() -> None:
    load_symbolic_asset_association_registry_v1.cache_clear()


def _path_theme_codes_from_evolution_cd() -> frozenset[str]:
    cd = load_evolution_cd_v1()
    themes = cd.get("evolution_path_themes") or {}
    return frozenset(themes.keys())


def _asset_codes_from_definition_registry() -> frozenset[str]:
    payload = load_symbolic_asset_definition_registry_v1()
    definitions = payload.get("symbolic_asset_definitions") or {}
    return frozenset(definitions.keys())


@lru_cache(maxsize=1)
def load_symbolic_asset_association_registry_v1() -> dict[str, Any]:
    path = Path(
        os.getenv(
            "TODAYFLOW_SYMBOLIC_ASSET_ASSOCIATION_REGISTRY_PATH",
            SYMBOLIC_ASSET_ASSOCIATION_REGISTRY_PATH,
        )
    )
    if not path.is_file():
        raise SymbolicAssetAssociationRegistryError(
            f"symbolic asset association registry not found: {path}"
        )
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    context = default_validation_context(
        asset_codes=_asset_codes_from_definition_registry(),
        path_theme_codes=_path_theme_codes_from_evolution_cd(),
    )
    errors = validate_symbolic_asset_association_registry_v1(payload, context=context)
    if errors:
        raise SymbolicAssetAssociationRegistryError("; ".join(errors[:8]))
    return payload


def get_symbolic_asset_association(
    association_id: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = (
        registry if registry is not None else load_symbolic_asset_association_registry_v1()
    )
    associations = payload.get("symbolic_asset_associations") or {}
    entry = associations.get(association_id)
    if not isinstance(entry, dict):
        raise SymbolicAssetAssociationRegistryError(
            f"symbolic asset association not found: {association_id!r}"
        )
    return dict(entry)


def list_symbolic_asset_associations_for_asset(
    asset_code: str,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    payload = (
        registry if registry is not None else load_symbolic_asset_association_registry_v1()
    )
    associations = payload.get("symbolic_asset_associations") or {}
    return [
        dict(entry)
        for entry in associations.values()
        if isinstance(entry, dict) and entry.get("asset_code") == asset_code
    ]


def list_symbolic_asset_associations_by_type(
    association_type: str,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    payload = (
        registry if registry is not None else load_symbolic_asset_association_registry_v1()
    )
    associations = payload.get("symbolic_asset_associations") or {}
    return [
        dict(entry)
        for entry in associations.values()
        if isinstance(entry, dict) and entry.get("association_type") == association_type
    ]


def list_symbolic_asset_associations_ordered(
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    payload = (
        registry if registry is not None else load_symbolic_asset_association_registry_v1()
    )
    associations = payload.get("symbolic_asset_associations") or {}
    return [dict(associations[assoc_id]) for assoc_id in sorted(associations.keys())]
