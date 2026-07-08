"""P1.3 — Resolve P1.2 content mapping to registry content entries (no assembly/LLM)."""

from __future__ import annotations

from typing import Any

from todayflow_backend.data.day_content_registry_loader import load_day_content_registry
from todayflow_backend.services.day_model_v1_content_mapper import (
    DAY_MODEL_CONTENT_MAPPING_V1_CONTRACT,
)

DAY_MODEL_CONTENT_RESOLUTION_V1_CONTRACT = "day_model_content_resolution_v1"

DAY_MODEL_CONTENT_RESOLUTION_V1_KEYS = frozenset(
    {
        "contract_version",
        "entries_by_slot",
        "entries_by_key",
        "missing_keys",
        "degraded",
    }
)


class DayModelContentResolutionError(ValueError):
    """Raised when mapping input is invalid for content resolution."""


def get_content_entry(
    content_key: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    reg = registry if registry is not None else load_day_content_registry()
    entry = reg["keys"].get(content_key)
    if entry is None:
        raise DayModelContentResolutionError(f"content key not in registry: {content_key!r}")
    return dict(entry)


def resolve_content_entries_from_mapping(
    mapping: dict[str, Any],
    *,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Resolve P1.2 mapping output to concrete content entries from registry.

    Does not assemble final Today text — entries only.
    """
    if mapping.get("contract_version") != DAY_MODEL_CONTENT_MAPPING_V1_CONTRACT:
        raise DayModelContentResolutionError(
            f"expected contract_version={DAY_MODEL_CONTENT_MAPPING_V1_CONTRACT!r}, "
            f"got {mapping.get('contract_version')!r}"
        )

    reg = registry if registry is not None else load_day_content_registry()
    entries_by_slot: dict[str, list[dict[str, Any]]] = {}
    entries_by_key: dict[str, dict[str, Any]] = {}
    missing: list[str] = list(mapping.get("missing_keys", []))

    slot_map: dict[str, list[str]] = {}
    slot_map.update(mapping.get("required_slots", {}))
    for slot, keys in mapping.get("optional_slots", {}).items():
        slot_map.setdefault(slot, [])
        slot_map[slot] = slot_map[slot] + keys

    seen_keys: set[str] = set()
    for slot, keys in slot_map.items():
        slot_entries: list[dict[str, Any]] = []
        for content_key in keys:
            if content_key in seen_keys:
                continue
            seen_keys.add(content_key)
            if content_key not in reg["keys"]:
                if content_key not in missing:
                    missing.append(content_key)
                continue
            entry = get_content_entry(content_key, reg)
            slot_entries.append(entry)
            entries_by_key[content_key] = entry
        if slot_entries:
            entries_by_slot[slot] = slot_entries

    return {
        "contract_version": DAY_MODEL_CONTENT_RESOLUTION_V1_CONTRACT,
        "entries_by_slot": entries_by_slot,
        "entries_by_key": entries_by_key,
        "missing_keys": sorted(set(missing)),
        "degraded": bool(mapping.get("degraded", False)) or bool(missing),
    }
