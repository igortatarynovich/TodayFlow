"""Number base v1 — static meanings for day / life-path / personal-year digits.

Canon: docs/numerology/NUMBER_BASE_V1.md · docs/audits/DAY_SYMBOL_REVEAL_CANON_V1.md
Data: DATA/reference/numerology/number_base_v1/numbers.json

Product master set in use: 11, 22, 33 (44 documented, in_use=false → reduces as 8).
Karmic debts 13/14/16/19 are lookup rows when they surface before final reduction.
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

# Live day reduction masters + core digits (hook / explainer required).
REQUIRED_VALUES = (1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33)
# Documented lookups (not required for day reduce path).
OPTIONAL_VALUES = (13, 14, 16, 19, 44)


def _str_list(raw: Any) -> list[str]:
    if not isinstance(raw, list):
        return []
    return [str(x).strip() for x in raw if str(x).strip()]


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
        kind = str(row.get("kind") or "core").strip()
        in_use = row.get("in_use")
        if in_use is None:
            in_use = kind != "master" or value in (11, 22, 33)
        out[value] = {
            "value": value,
            "kind": kind,
            "title": str(row.get("title") or "").strip(),
            "archetype": str(row.get("archetype") or row.get("title") or "").strip(),
            "base_meaning": meaning,
            "keywords": _str_list(row.get("keywords")),
            "strengths": _str_list(row.get("strengths")),
            "weaknesses": _str_list(row.get("weaknesses")),
            "talents": _str_list(row.get("talents")),
            "risks": _str_list(row.get("risks")),
            "risk": str(row.get("risk") or "").strip(),
            "theme": str(row.get("theme") or "").strip(),
            "lesson": str(row.get("lesson") or "").strip(),
            "base_digit": row.get("base_digit"),
            "in_use": bool(in_use),
        }
    return out


def get_number_base(value: int) -> dict[str, Any] | None:
    return numbers_by_value().get(int(value))


def format_base_prompt_block(value: int) -> str | None:
    """Human-readable base block for numerology_explainer user prompt."""
    row = get_number_base(value)
    if not row:
        return None
    lines = [
        "Базовое значение числа (канон number_base_v1 — не изобретай другое):",
        f"- value: {row['value']}",
        f"- kind: {row['kind']}",
        f"- archetype: {row['archetype']}",
        f"- base_meaning: {row['base_meaning']}",
    ]
    if row.get("keywords"):
        lines.append(f"- keywords: {', '.join(row['keywords'])}")
    if row.get("strengths"):
        lines.append(f"- strengths: {', '.join(row['strengths'])}")
    if row.get("weaknesses"):
        lines.append(f"- weaknesses: {', '.join(row['weaknesses'])}")
    if row.get("talents"):
        lines.append(f"- talents: {', '.join(row['talents'])}")
    risks = row.get("risks") or ([] if not row.get("risk") else [row["risk"]])
    if risks:
        lines.append(f"- risks: {', '.join(risks)}")
    if row.get("theme"):
        lines.append(f"- karmic theme: {row['theme']}")
    if row.get("lesson"):
        lines.append(f"- karmic lesson: {row['lesson']}")
    return "\n".join(lines)


def base_anchor_tokens(value: int) -> list[str]:
    """Tokens that a personalized meaning must touch (archetype + keywords)."""
    row = get_number_base(value)
    if not row:
        return []
    tokens: list[str] = []
    for piece in (row.get("archetype"), *(row.get("keywords") or [])):
        text = str(piece or "").strip().lower()
        if not text:
            continue
        tokens.append(text)
        for part in text.replace("/", " ").replace("—", " ").split():
            part = part.strip(".,;:")
            if len(part) >= 4:
                tokens.append(part)
    # de-dupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def meaning_aligned_with_base(meaning: str, value: int) -> bool:
    """True if meaning shares at least one base anchor token (len>=4)."""
    text = (meaning or "").strip().lower()
    if not text:
        return False
    anchors = [t for t in base_anchor_tokens(value) if len(t) >= 4]
    if not anchors:
        return False
    return any(a in text for a in anchors)


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
        if not row.get("archetype"):
            errors.append(f"empty_archetype_{value}")
        if not row.get("keywords"):
            errors.append(f"empty_keywords_{value}")
    for value in OPTIONAL_VALUES:
        row = by_val.get(value)
        if row and not row.get("base_meaning"):
            errors.append(f"empty_optional_meaning_{value}")
    if 44 in by_val and by_val[44].get("in_use"):
        errors.append("master_44_marked_in_use_but_product_masters_are_11_22_33")
    # Bogus FE key must never enter the bank
    if 20 in by_val:
        errors.append("bogus_value_20_must_not_be_in_number_base")
    return errors
