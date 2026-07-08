"""Load DayModel content registry (P1.2 keys + P1.3 seed texts)."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from todayflow_backend.data.day_content_registry_validator import (
    validate_day_content_registry_payload,
)
from todayflow_backend.data.reference_machine_loader import DATA_ROOT

DAY_CONTENT_REGISTRY_CONTRACT = "day_content_registry_v1"
DAY_CONTENT_REGISTRY_PATH = DATA_ROOT / "reference" / "day" / "content" / "registry.json"

ALLOWED_CONTENT_STATUSES = frozenset({"draft", "review", "active"})


class DayContentRegistryError(Exception):
    """Raised when the day content registry is missing or invalid."""


def clear_day_content_registry_cache() -> None:
    load_day_content_registry.cache_clear()


@lru_cache(maxsize=1)
def load_day_content_registry() -> dict[str, Any]:
    path = Path(os.getenv("TODAYFLOW_DAY_CONTENT_REGISTRY", DAY_CONTENT_REGISTRY_PATH))
    if not path.is_file():
        raise DayContentRegistryError(f"day content registry not found: {path}")
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    _validate_registry(payload)
    return payload


def _validate_registry(payload: dict[str, Any]) -> None:
    if payload.get("contract_version") != DAY_CONTENT_REGISTRY_CONTRACT:
        raise DayContentRegistryError(
            f"expected contract_version={DAY_CONTENT_REGISTRY_CONTRACT!r}, "
            f"got {payload.get('contract_version')!r}"
        )
    errors = validate_day_content_registry_payload(payload)
    if errors:
        raise DayContentRegistryError("; ".join(errors[:5]))


def registry_has_key(content_key: str, registry: dict[str, Any] | None = None) -> bool:
    reg = registry if registry is not None else load_day_content_registry()
    entry = reg["keys"].get(content_key)
    if entry is None:
        return False
    text_short = entry.get("text_short")
    return isinstance(text_short, str) and bool(text_short.strip())


def get_registry_entry(
    content_key: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    reg = registry if registry is not None else load_day_content_registry()
    entry = reg["keys"].get(content_key)
    if entry is None:
        raise DayContentRegistryError(f"content key not found: {content_key!r}")
    return dict(entry)
