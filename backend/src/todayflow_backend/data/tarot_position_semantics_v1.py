"""Tarot Position Semantics v1 — how to read a card in a position.

Canon: docs/tarot/TAROT_POSITION_SEMANTICS_V1.md
Data: DATA/reference/tarot/position_semantics_v1/roles.json
"""

from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CONTRACT_VERSION = "tarot_position_semantics_v1"

DEFAULT_DATA_ROOT = Path(__file__).resolve().parents[4] / "DATA"
ROLES_PATH = (
    Path(os.getenv("TODAYFLOW_DATA_DIR", DEFAULT_DATA_ROOT))
    / "reference"
    / "tarot"
    / "position_semantics_v1"
    / "roles.json"
)

# Keyword heuristics when position_id is not in the explicit map.
_HEURISTIC_RULES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("risk", "harm", "caution"), "risk"),
    (("fear", "warn"), "warning"),
    (("block", "friction", "stop", "obstacle"), "blocks"),
    (("give", "gain", "open", "benefit", "path_"), "gain"),
    (("resource", "leverage", "chance", "support"), "resource"),
    (("hidden", "blind", "secret", "suppress", "under"), "hidden_cause"),
    (("next", "step", "action", "move", "practical", "unstick"), "next_step"),
    (("advice", "counsel"), "advice"),
    (("outcome", "result", "if_stay"), "outcome"),
    (("past", "origin"), "past"),
    (("present", "pulse", "now"), "present"),
    (("future",), "future"),
    (("weight", "consider", "important", "core"), "weights"),
    (("nuance", "tension"), "nuance"),
    (("bridge", "integrat"), "bridge"),
    (("between", "dynamic"), "dynamic"),
    (("other",), "other"),
    (("self", "you", "want", "mind", "heart", "body"), "self"),
    (("focus", "essence", "situation"), "focus"),
)


@lru_cache(maxsize=1)
def _load_payload() -> dict[str, Any]:
    if not ROLES_PATH.is_file():
        logger.warning("tarot_position_semantics_v1 missing at %s", ROLES_PATH)
        return {}
    with ROLES_PATH.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        return {}
    if data.get("contract_version") != CONTRACT_VERSION:
        logger.warning(
            "tarot_position_semantics_v1 unexpected contract_version=%s",
            data.get("contract_version"),
        )
    return data


@lru_cache(maxsize=1)
def roles_by_id() -> dict[str, dict[str, Any]]:
    payload = _load_payload()
    roles = payload.get("roles") if isinstance(payload, dict) else None
    if not isinstance(roles, list):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for row in roles:
        if not isinstance(row, dict):
            continue
        rid = str(row.get("role_id") or "").strip()
        if rid:
            out[rid] = row
    return out


@lru_cache(maxsize=1)
def position_role_map() -> dict[str, str]:
    payload = _load_payload()
    raw = payload.get("position_role_map") if isinstance(payload, dict) else None
    if not isinstance(raw, dict):
        return {}
    return {str(k).strip().lower(): str(v).strip() for k, v in raw.items() if str(k).strip()}


def resolve_role_id(position_id: str | None) -> str:
    pid = (position_id or "").strip().lower()
    mapped = position_role_map().get(pid)
    if mapped and mapped in roles_by_id():
        return mapped
    for needles, role in _HEURISTIC_RULES:
        if any(n in pid for n in needles):
            if role in roles_by_id():
                return role
    return "neutral" if "neutral" in roles_by_id() else "neutral"


def get_role(role_id: str) -> dict[str, Any] | None:
    return roles_by_id().get((role_id or "").strip())


def pack_position_semantics(position_id: str | None) -> dict[str, Any]:
    """Facts for Context Pack — instructions, not final prose."""
    role_id = resolve_role_id(position_id)
    role = get_role(role_id) or get_role("neutral") or {}
    do_not = [str(x).strip() for x in (role.get("do_not") or []) if str(x).strip()]
    return {
        "role_id": str(role.get("role_id") or role_id),
        "purpose": str(role.get("purpose") or "").strip(),
        "answers_question": str(role.get("answers_question") or "").strip(),
        "extract_from_card": str(role.get("extract_from_card") or "").strip(),
        "do_not": do_not,
        "result_type": str(role.get("result_type") or "neutral_read").strip(),
        "short_instruction": str(role.get("short_instruction") or "").strip(),
    }
