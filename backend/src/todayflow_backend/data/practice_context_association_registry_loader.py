"""C1.7 — Load Practice Context Association registry (context links, not selection)."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from todayflow_backend.data.evolution_cd_loader import load_evolution_cd_v1
from todayflow_backend.data.practice_context_association_registry_validator import (
    PRACTICE_CONTEXT_ASSOCIATION_REGISTRY_V1_CONTRACT,
    default_validation_context,
    validate_practice_context_association_registry_v1,
)
from todayflow_backend.data.practice_definition_registry_loader import (
    load_practice_definition_registry_v1,
)
from todayflow_backend.data.reference_machine_loader import DATA_ROOT

PRACTICE_CONTEXT_ASSOCIATION_REGISTRY_PATH = (
    DATA_ROOT
    / "reference"
    / "practice"
    / "practice_context_association_registry_v1.json"
)


class PracticeContextAssociationRegistryError(Exception):
    """Raised when practice context association registry is missing or invalid."""


def clear_practice_context_association_registry_cache() -> None:
    load_practice_context_association_registry_v1.cache_clear()


def _path_theme_codes_from_evolution_cd() -> frozenset[str]:
    cd = load_evolution_cd_v1()
    themes = cd.get("evolution_path_themes") or {}
    return frozenset(themes.keys())


def _practice_codes_from_definition_registry() -> frozenset[str]:
    payload = load_practice_definition_registry_v1()
    definitions = payload.get("practice_definitions") or {}
    return frozenset(definitions.keys())


@lru_cache(maxsize=1)
def load_practice_context_association_registry_v1() -> dict[str, Any]:
    path = Path(
        os.getenv(
            "TODAYFLOW_PRACTICE_CONTEXT_ASSOCIATION_REGISTRY_PATH",
            PRACTICE_CONTEXT_ASSOCIATION_REGISTRY_PATH,
        )
    )
    if not path.is_file():
        raise PracticeContextAssociationRegistryError(
            f"practice context association registry not found: {path}"
        )
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    context = default_validation_context(
        practice_codes=_practice_codes_from_definition_registry(),
        path_theme_codes=_path_theme_codes_from_evolution_cd(),
    )
    errors = validate_practice_context_association_registry_v1(payload, context=context)
    if errors:
        raise PracticeContextAssociationRegistryError("; ".join(errors[:8]))
    return payload


def get_practice_context_association(
    association_id: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = (
        registry if registry is not None else load_practice_context_association_registry_v1()
    )
    associations = payload.get("practice_context_associations") or {}
    entry = associations.get(association_id)
    if not isinstance(entry, dict):
        raise PracticeContextAssociationRegistryError(
            f"practice context association not found: {association_id!r}"
        )
    return dict(entry)


def list_practice_context_associations_for_practice(
    practice_definition_code: str,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    payload = (
        registry if registry is not None else load_practice_context_association_registry_v1()
    )
    associations = payload.get("practice_context_associations") or {}
    return [
        dict(entry)
        for entry in associations.values()
        if isinstance(entry, dict)
        and entry.get("practice_definition_code") == practice_definition_code
    ]


def list_practice_context_associations_by_source_type(
    source_type: str,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    payload = (
        registry if registry is not None else load_practice_context_association_registry_v1()
    )
    associations = payload.get("practice_context_associations") or {}
    return [
        dict(entry)
        for entry in associations.values()
        if isinstance(entry, dict) and entry.get("source_type") == source_type
    ]


def list_practice_context_associations_for_context(
    source_type: str,
    source_ref: str,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    payload = (
        registry if registry is not None else load_practice_context_association_registry_v1()
    )
    associations = payload.get("practice_context_associations") or {}
    return [
        dict(entry)
        for entry in associations.values()
        if isinstance(entry, dict)
        and entry.get("source_type") == source_type
        and entry.get("source_ref") == source_ref
    ]


def list_practice_context_associations_ordered(
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    payload = (
        registry if registry is not None else load_practice_context_association_registry_v1()
    )
    associations = payload.get("practice_context_associations") or {}
    return [dict(associations[assoc_id]) for assoc_id in sorted(associations.keys())]
