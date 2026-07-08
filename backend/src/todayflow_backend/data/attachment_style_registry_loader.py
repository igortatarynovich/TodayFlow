"""Import pilot — Load attachment style reference from DATA/reference/psychology/."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from todayflow_backend.data.attachment_style_registry_validator import (
    ATTACHMENT_STYLE_REGISTRY_V1_CONTRACT,
    validate_attachment_style_registry_v1,
)
from todayflow_backend.data.reference_machine_loader import DATA_ROOT

ATTACHMENT_STYLE_REGISTRY_PATH = (
    DATA_ROOT / "reference" / "psychology" / "attachment_style_registry_v1.json"
)


class AttachmentStyleRegistryError(Exception):
    """Raised when attachment style registry is missing or invalid."""


def clear_attachment_style_registry_cache() -> None:
    load_attachment_style_registry_v1.cache_clear()


@lru_cache(maxsize=1)
def load_attachment_style_registry_v1() -> dict[str, Any]:
    path = Path(os.getenv("TODAYFLOW_ATTACHMENT_STYLE_REGISTRY_PATH", ATTACHMENT_STYLE_REGISTRY_PATH))
    if not path.is_file():
        raise AttachmentStyleRegistryError(f"attachment style registry not found: {path}")
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    errors = validate_attachment_style_registry_v1(payload)
    if errors:
        raise AttachmentStyleRegistryError("; ".join(errors[:8]))
    return payload


def list_attachment_styles(
    registry: dict[str, Any] | None = None,
    *,
    allowed_statuses: frozenset[str] | None = None,
) -> list[dict[str, Any]]:
    payload = registry if registry is not None else load_attachment_style_registry_v1()
    statuses = allowed_statuses or frozenset({"active"})
    styles = payload.get("attachment_styles") or {}
    return [
        dict(styles[code])
        for code in sorted(styles.keys())
        if isinstance(styles.get(code), dict) and styles[code].get("status") in statuses
    ]


def get_attachment_style(code: str, registry: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = registry if registry is not None else load_attachment_style_registry_v1()
    styles = payload.get("attachment_styles") or {}
    style = styles.get(code)
    if not isinstance(style, dict):
        raise AttachmentStyleRegistryError(f"attachment style not found: {code!r}")
    return dict(style)


def deep_block_bias_for_style(code: str, block_key: str) -> float | None:
    """Return normalized bias weight for a compatibility deep block (reference only)."""
    style = get_attachment_style(code)
    bias = style.get("deep_block_bias") or {}
    if block_key not in bias:
        return None
    total = sum(float(v) for v in bias.values() if isinstance(v, (int, float)))
    if total <= 0:
        return None
    return round(float(bias[block_key]) / total, 4)
