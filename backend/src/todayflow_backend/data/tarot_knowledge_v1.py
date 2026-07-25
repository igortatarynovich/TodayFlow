"""Tarot Knowledge Base v1 — semantic facts for Context Pack.

Canon: docs/tarot/TAROT_KNOWLEDGE_BASE_V1.md
Data: DATA/reference/tarot/knowledge_v1/cards.json
"""

from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CONTRACT_VERSION = "tarot_knowledge_v1"

DEFAULT_DATA_ROOT = Path(__file__).resolve().parents[4] / "DATA"
KB_PATH = (
    Path(os.getenv("TODAYFLOW_DATA_DIR", DEFAULT_DATA_ROOT))
    / "reference"
    / "tarot"
    / "knowledge_v1"
    / "cards.json"
)

_DOMAIN_TO_FACET: dict[str, str] = {
    "work": "work",
    "work_change": "work",
    "relationships": "relationships",
    "relationship": "relationships",
    "family": "relationships",
    "money": "money",
    "growth": "growth",
    "purpose": "growth",
    "decision": "growth",
    "conflict": "relationships",
    "inner_state": "growth",
    "self": "growth",
    "creative": "growth",
    "general": "growth",
    "choice": "growth",
    "undefined": "growth",
}


@lru_cache(maxsize=1)
def _load_payload() -> dict[str, Any]:
    if not KB_PATH.is_file():
        logger.warning("tarot_knowledge_v1 missing at %s", KB_PATH)
        return {}
    with KB_PATH.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        return {}
    if data.get("contract_version") != CONTRACT_VERSION:
        logger.warning(
            "tarot_knowledge_v1 unexpected contract_version=%s",
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
            cid = int(row["card_id"])
        except (KeyError, TypeError, ValueError):
            continue
        out[cid] = row
    return out


def get_card(card_id: int) -> dict[str, Any] | None:
    return cards_by_id().get(int(card_id))


def domain_facet(card: dict[str, Any], question_domain: str | None) -> dict[str, str] | None:
    domains = card.get("domains") if isinstance(card.get("domains"), dict) else {}
    facet_key = _DOMAIN_TO_FACET.get((question_domain or "general").strip().lower(), "growth")
    text = str(domains.get(facet_key) or "").strip()
    if not text:
        return None
    return {"domain": facet_key, "fact": text}


def meaning_range_from_kb(
    card: dict[str, Any],
    *,
    question_domain: str | None = None,
    catalog_up: str = "",
    catalog_rev: str = "",
    keywords: list[str] | None = None,
    element: str | None = None,
    element_ru: str | None = None,
) -> dict[str, Any]:
    """Project KB record into pack meaning_range facts."""
    rev = card.get("reversed") if isinstance(card.get("reversed"), dict) else {}
    light = [str(x).strip() for x in (card.get("light") or []) if str(x).strip()]
    shadow = [str(x).strip() for x in (card.get("shadow") or []) if str(x).strip()]
    up_themes = [str(x).strip() for x in (card.get("upright_themes") or light) if str(x).strip()]
    rev_themes = [
        str(x).strip()
        for x in (card.get("reversed_themes") or rev.get("themes") or shadow)
        if str(x).strip()
    ]
    facet = domain_facet(card, question_domain)
    out: dict[str, Any] = {
        "knowledge_source": CONTRACT_VERSION,
        "central_symbol": str(card.get("central_archetype") or "").strip(),
        "light_side": light,
        "shadow_side": shadow,
        "inner_conflict": str(card.get("inner_conflict") or "").strip() or None,
        "outer_expression": str(card.get("outer_expression") or "").strip() or None,
        "domains": {
            k: str(v).strip()
            for k, v in (card.get("domains") or {}).items()
            if str(v).strip()
        },
        "domain_lens": facet,
        "upright_themes": up_themes,
        "reversed_themes": rev_themes,
        "reversed_central": str(rev.get("central") or "").strip() or None,
        "reversed_trap": str(rev.get("trap") or "").strip() or None,
        "amplifies_questions": [
            str(x).strip() for x in (card.get("amplifies_questions") or []) if str(x).strip()
        ],
        "intensifies_with": [int(x) for x in (card.get("intensifies_with") or [])],
        "softens_with": [int(x) for x in (card.get("softens_with") or [])],
        "upright_meaning": catalog_up,
        "reversed_meaning": catalog_rev,
        "keywords": keywords or up_themes[:4],
        "element": element,
        "element_ru": element_ru,
    }
    # Q1 minor archetype profile — semantic facts for the LLM author (not prose).
    for key in (
        "core_scene",
        "central_conflict",
        "driving_need",
        "shadow_pattern",
        "growth_direction",
        "work_lens",
        "relationship_lens",
        "money_lens",
        "inner_lens",
        "reversed_shift",
        "adjacent_distinction",
    ):
        val = str(card.get(key) or "").strip()
        if val:
            out[key] = val
    return out
