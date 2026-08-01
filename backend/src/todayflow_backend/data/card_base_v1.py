"""Tarot card base v1 — static upright/reversed meanings for all surfaces.

Canon: docs/tarot/TAROT_CARD_BASE_V1.md
Data: DATA/reference/tarot/card_base_v1/cards.json
"""

from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

logger = logging.getLogger(__name__)

CONTRACT_VERSION = "card_base_v1"
Orientation = Literal["upright", "reversed"]

DEFAULT_DATA_ROOT = Path(__file__).resolve().parents[4] / "DATA"
BASE_PATH = (
    Path(os.getenv("TODAYFLOW_DATA_DIR", DEFAULT_DATA_ROOT))
    / "reference"
    / "tarot"
    / "card_base_v1"
    / "cards.json"
)


def normalize_orientation(orientation: str | None) -> Orientation:
    raw = (orientation or "upright").strip().lower()
    return "reversed" if raw == "reversed" else "upright"


@lru_cache(maxsize=1)
def _load_payload() -> dict[str, Any]:
    if not BASE_PATH.is_file():
        logger.warning("card_base_v1 missing at %s", BASE_PATH)
        return {}
    with BASE_PATH.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        return {}
    if data.get("contract_version") != CONTRACT_VERSION:
        logger.warning(
            "card_base_v1 unexpected contract_version=%s",
            data.get("contract_version"),
        )
    return data


@lru_cache(maxsize=1)
def cards_by_id() -> dict[int, dict[str, Any]]:
    payload = _load_payload()
    cards = payload.get("cards") if isinstance(payload, dict) else None
    if not isinstance(cards, list):
        return {}
    out: dict[int, dict[str, Any]] = {}
    for row in cards:
        if not isinstance(row, dict):
            continue
        try:
            cid = int(row["id"])
        except (KeyError, TypeError, ValueError):
            continue
        upright = row.get("upright") if isinstance(row.get("upright"), dict) else {}
        reversed_ = row.get("reversed") if isinstance(row.get("reversed"), dict) else {}
        if not str(upright.get("base_meaning") or "").strip():
            continue
        if not str(reversed_.get("base_meaning") or "").strip():
            continue
        out[cid] = row
    return out


def get_card(card_id: int) -> dict[str, Any] | None:
    return cards_by_id().get(int(card_id))


def get_base_meaning(
    card_id: int,
    orientation: str | None = "upright",
) -> dict[str, Any] | None:
    """Lookup (card_id, orientation) → meaning payload for hook_reveal.base."""
    card = get_card(card_id)
    if not card:
        return None
    orient = normalize_orientation(orientation)
    side = card.get(orient) if isinstance(card.get(orient), dict) else {}
    meaning = str(side.get("base_meaning") or "").strip()
    if not meaning:
        return None
    return {
        "id": int(card_id),
        "name_ru": str(card.get("name_ru") or "").strip(),
        "type": str(card.get("type") or "").strip(),
        "orientation": orient,
        "meaning": meaning,
        "keywords": [str(x).strip() for x in (side.get("keywords") or []) if str(x).strip()],
    }


def validate_card_base_v1() -> list[str]:
    errors: list[str] = []
    payload = _load_payload()
    if not payload:
        return ["card_base_v1_missing"]
    if payload.get("contract_version") != CONTRACT_VERSION:
        errors.append("bad_contract_version")
    by_id = cards_by_id()
    if len(by_id) != 78:
        errors.append(f"expected_78_got_{len(by_id)}")
    for cid in range(78):
        card = by_id.get(cid)
        if not card:
            errors.append(f"missing_card_{cid}")
            continue
        for orient in ("upright", "reversed"):
            side = card.get(orient) if isinstance(card.get(orient), dict) else {}
            if not str(side.get("base_meaning") or "").strip():
                errors.append(f"empty_{orient}_{cid}")
    return errors
