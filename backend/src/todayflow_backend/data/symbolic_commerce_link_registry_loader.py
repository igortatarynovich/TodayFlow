"""D1.5 — Load Symbolic Commerce Link registry (SKU → asset_code refs only)."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from todayflow_backend.data.reference_machine_loader import DATA_ROOT
from todayflow_backend.data.symbolic_asset_definition_registry_loader import (
    load_symbolic_asset_definition_registry_v1,
)
from todayflow_backend.data.symbolic_commerce_link_registry_validator import (
    SymbolicCommerceLinkValidationContext,
    validate_symbolic_commerce_link_registry_v1,
)

SYMBOLIC_COMMERCE_LINK_REGISTRY_PATH = (
    DATA_ROOT / "reference" / "symbolic" / "symbolic_commerce_link_registry_v1.json"
)


class SymbolicCommerceLinkRegistryError(Exception):
    """Raised when symbolic commerce link registry is missing or invalid."""


def clear_symbolic_commerce_link_registry_cache() -> None:
    load_symbolic_commerce_link_registry_v1.cache_clear()


def _build_validation_context() -> SymbolicCommerceLinkValidationContext:
    payload = load_symbolic_asset_definition_registry_v1()
    definitions = payload.get("symbolic_asset_definitions") or {}
    return SymbolicCommerceLinkValidationContext(asset_codes=frozenset(definitions.keys()))


@lru_cache(maxsize=1)
def load_symbolic_commerce_link_registry_v1() -> dict[str, Any]:
    path = Path(
        os.getenv(
            "TODAYFLOW_SYMBOLIC_COMMERCE_LINK_REGISTRY_PATH",
            SYMBOLIC_COMMERCE_LINK_REGISTRY_PATH,
        )
    )
    if not path.is_file():
        raise SymbolicCommerceLinkRegistryError(
            f"symbolic commerce link registry not found: {path}"
        )
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    errors = validate_symbolic_commerce_link_registry_v1(
        payload,
        context=_build_validation_context(),
    )
    if errors:
        raise SymbolicCommerceLinkRegistryError("; ".join(errors[:8]))
    return payload


def get_symbolic_commerce_link(
    link_id: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = registry if registry is not None else load_symbolic_commerce_link_registry_v1()
    links = payload.get("symbolic_commerce_links") or {}
    entry = links.get(link_id)
    if not isinstance(entry, dict):
        raise SymbolicCommerceLinkRegistryError(f"symbolic commerce link not found: {link_id!r}")
    return dict(entry)


def get_symbolic_commerce_link_by_sku(
    sku_ref: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = registry if registry is not None else load_symbolic_commerce_link_registry_v1()
    links = payload.get("symbolic_commerce_links") or {}
    for entry in links.values():
        if isinstance(entry, dict) and entry.get("sku_ref") == sku_ref:
            return dict(entry)
    raise SymbolicCommerceLinkRegistryError(f"symbolic commerce link not found for sku: {sku_ref!r}")


def list_symbolic_commerce_links_for_asset(
    asset_code: str,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    payload = registry if registry is not None else load_symbolic_commerce_link_registry_v1()
    links = payload.get("symbolic_commerce_links") or {}
    return [
        dict(entry)
        for entry in links.values()
        if isinstance(entry, dict) and entry.get("asset_code") == asset_code
    ]


def list_symbolic_commerce_links_ordered(
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    payload = registry if registry is not None else load_symbolic_commerce_link_registry_v1()
    links = payload.get("symbolic_commerce_links") or {}
    return [dict(links[link_id]) for link_id in sorted(links.keys())]
