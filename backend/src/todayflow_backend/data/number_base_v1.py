"""Number base v1 — static meanings for personal/universal day numbers.

Canon: docs/audits/DAY_SYMBOL_REVEAL_CANON_V1.md
Data: DATA/reference/numerology/number_base_v1/numbers.json
"""

from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CONTRACT_VERSION = "number_base_v1"

DEFAULT_DATA_ROOT = Path(__file__).resolve().parents[4] / "DATA"
BASE_PATH = (
    Path(os.getenv("TODAYFLOW_DATA_DIR", DEFAULT_DATA_ROOT))
    / "reference"
    / "numerology"
    / "number_base_v1"
    / "numbers.json"
)

REQUIRED_VALUES = (1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33)


@lru_cache(maxsize=1)
def _load_payload() -> dict[str, Any]:
    if not BASE_PATH.is_file():
        logger.warning("number_base_v1 missing at %s", BASE_PATH)
        return {}
    with BASE_PATH.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        return {}
    if data.get("contract_version") != CONTRACT_VERSION:
        logger.warning(
            "number_base_v1 unexpected contract_version=%s",
            data.get("contract_version"),
        )
    return data


@lru_cache(maxsize=1)
def numbers_by_value() -> dict[int, dict[str, Any]]:
    payload = _load_payload()
    rows = payload.get("numbers") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        return {}
    out: dict[int, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        try:
            value = int(row["value"])
        except (KeyError, TypeError, ValueError):
            continue
        meaning = str(row.get("base_meaning") or "").strip()
        if not meaning:
            continue
        out[value] = {
            "value": value,
            "title": str(row.get("title") or "").strip(),
            "base_meaning": meaning,
            "keywords": [str(x).strip() for x in (row.get("keywords") or []) if str(x).strip()],
        }
    return out


def get_number_base(value: int) -> dict[str, Any] | None:
    return numbers_by_value().get(int(value))


def validate_number_base_v1() -> list[str]:
    """Return validation errors (empty = ok)."""
    errors: list[str] = []
    payload = _load_payload()
    if not payload:
        return ["number_base_v1_missing"]
    if payload.get("contract_version") != CONTRACT_VERSION:
        errors.append("bad_contract_version")
    by_val = numbers_by_value()
    for value in REQUIRED_VALUES:
        row = by_val.get(value)
        if not row:
            errors.append(f"missing_value_{value}")
            continue
        if not row.get("base_meaning"):
            errors.append(f"empty_meaning_{value}")
    return errors
