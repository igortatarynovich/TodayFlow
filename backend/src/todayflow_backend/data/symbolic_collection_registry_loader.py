"""D1.3 — Load Symbolic Collection registry (curated groups, not shop bundles)."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from todayflow_backend.data.cycle_definition_registry_validator import (
    CANONICAL_CYCLE_DEFINITION_CODES,
)
from todayflow_backend.data.evolution_cd_loader import load_evolution_cd_v1
from todayflow_backend.data.evolution_cd_validator import CANONICAL_STAGE_ORDER
from todayflow_backend.data.practice_definition_registry_validator import (
    CANONICAL_PRACTICE_CATEGORIES,
)
from todayflow_backend.data.reference_machine_loader import DATA_ROOT
from todayflow_backend.data.symbolic_asset_association_registry_loader import (
    load_symbolic_asset_association_registry_v1,
)
from todayflow_backend.data.symbolic_asset_definition_registry_loader import (
    load_symbolic_asset_definition_registry_v1,
)
from todayflow_backend.data.symbolic_collection_registry_validator import (
    SymbolicCollectionValidationContext,
    validate_symbolic_collection_registry_v1,
)
from todayflow_backend.services.calendar_rhythm_pattern_candidate_v1 import (
    ALLOWED_CANDIDATE_TYPES,
)

SYMBOLIC_COLLECTION_REGISTRY_PATH = (
    DATA_ROOT / "reference" / "symbolic" / "symbolic_collection_registry_v1.json"
)


class SymbolicCollectionRegistryError(Exception):
    """Raised when symbolic collection registry is missing or invalid."""


def clear_symbolic_collection_registry_cache() -> None:
    load_symbolic_collection_registry_v1.cache_clear()


def _build_validation_context() -> SymbolicCollectionValidationContext:
    asset_payload = load_symbolic_asset_definition_registry_v1()
    association_payload = load_symbolic_asset_association_registry_v1()
    cd = load_evolution_cd_v1()
    return SymbolicCollectionValidationContext(
        asset_codes=frozenset(
            (asset_payload.get("symbolic_asset_definitions") or {}).keys()
        ),
        association_ids=frozenset(
            (association_payload.get("symbolic_asset_associations") or {}).keys()
        ),
        path_theme_codes=frozenset((cd.get("evolution_path_themes") or {}).keys()),
        evolution_stage_codes=frozenset(CANONICAL_STAGE_ORDER),
        practice_codes=frozenset(CANONICAL_PRACTICE_CATEGORIES),
        cycle_codes=frozenset(CANONICAL_CYCLE_DEFINITION_CODES),
        rhythm_pattern_types=frozenset(ALLOWED_CANDIDATE_TYPES),
    )


@lru_cache(maxsize=1)
def load_symbolic_collection_registry_v1() -> dict[str, Any]:
    path = Path(
        os.getenv(
            "TODAYFLOW_SYMBOLIC_COLLECTION_REGISTRY_PATH",
            SYMBOLIC_COLLECTION_REGISTRY_PATH,
        )
    )
    if not path.is_file():
        raise SymbolicCollectionRegistryError(
            f"symbolic collection registry not found: {path}"
        )
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    errors = validate_symbolic_collection_registry_v1(
        payload,
        context=_build_validation_context(),
    )
    if errors:
        raise SymbolicCollectionRegistryError("; ".join(errors[:8]))
    return payload


def get_symbolic_collection(
    collection_code: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = registry if registry is not None else load_symbolic_collection_registry_v1()
    collections = payload.get("symbolic_collections") or {}
    entry = collections.get(collection_code)
    if not isinstance(entry, dict):
        raise SymbolicCollectionRegistryError(
            f"symbolic collection not found: {collection_code!r}"
        )
    return dict(entry)


def list_symbolic_collections_by_type(
    collection_type: str,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    payload = registry if registry is not None else load_symbolic_collection_registry_v1()
    collections = payload.get("symbolic_collections") or {}
    return [
        dict(entry)
        for entry in collections.values()
        if isinstance(entry, dict) and entry.get("collection_type") == collection_type
    ]


def list_symbolic_collections_for_asset(
    asset_code: str,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    payload = registry if registry is not None else load_symbolic_collection_registry_v1()
    collections = payload.get("symbolic_collections") or {}
    return [
        dict(entry)
        for entry in collections.values()
        if isinstance(entry, dict) and asset_code in (entry.get("asset_codes") or [])
    ]


def list_symbolic_collections_ordered(
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    payload = registry if registry is not None else load_symbolic_collection_registry_v1()
    collections = payload.get("symbolic_collections") or {}
    return [dict(collections[code]) for code in sorted(collections.keys())]
