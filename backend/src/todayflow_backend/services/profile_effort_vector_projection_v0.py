"""Deterministic Profile Step-4 effort_vector (journey «что делать дальше»).

SoT: docs/profile/PROFILE_PRODUCT_JOURNEY_FORMS_V1.md § Шаг 4
Source: ONLY insight_nodes_v0.nodes[0] — never life_mission / Today / astrology / new rec lists.
Read-path only. No LLM. No Snapshot fields.
"""

from __future__ import annotations

import re
from typing import Any

PROJECTION_VERSION = "profile_effort_vector_v0.1"
_MAX_VECTOR = 140
_MIN_VECTOR = 8


def _clip(text: str, limit: int) -> str:
    t = re.sub(r"\s+", " ", str(text or "").strip())
    if len(t) <= limit:
        return t
    return t[: limit - 1].rstrip() + "…"


def _norm(text: str) -> str:
    t = re.sub(r"\s+", " ", (text or "").strip().lower())
    t = re.sub(r"[«»\"'.,!?;:—\-]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _is_near_duplicate(a: str, b: str) -> bool:
    """Reject help that merely restates insight (no new effort direction)."""
    na, nb = _norm(a), _norm(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    if len(na) >= 16 and (na in nb or nb in na):
        return True
    # Token Jaccard — high overlap ≈ same claim
    ta, tb = set(na.split()), set(nb.split())
    if not ta or not tb:
        return False
    overlap = len(ta & tb) / max(1, len(ta | tb))
    return overlap >= 0.72


def project_effort_vector_v0(
    *,
    insight_nodes: dict[str, Any] | None,
) -> dict[str, Any]:
    """Derive effort_vector from the selected Step-3 node only."""
    pack = insight_nodes if isinstance(insight_nodes, dict) else {}
    nodes = pack.get("nodes") if isinstance(pack.get("nodes"), list) else []
    empty = {
        "projection_version": PROJECTION_VERSION,
        "effort_vector": None,
        "source_node_id": None,
        "source_fields": [],
        "rules": {
            "no_llm": True,
            "source_only_selected_insight_node": True,
            "forbid_life_mission": True,
            "forbid_today_astrology_rec_lists": True,
            "null_when_no_safe_help": True,
        },
    }
    if not nodes or not isinstance(nodes[0], dict):
        return empty

    node = nodes[0]
    node_id = str(node.get("id") or "").strip() or None
    kind = str(node.get("kind") or "").strip().lower()
    insight = _clip(str(node.get("insight") or ""), 240)
    help_line = _clip(str(node.get("help") or ""), _MAX_VECTOR)

    # Safe deterministic path: node.help that adds direction beyond restating insight.
    # No formula that invents action from insight alone — null instead of generic advice.
    if len(help_line) < _MIN_VECTOR or _is_near_duplicate(help_line, insight):
        return {
            **empty,
            "source_node_id": node_id,
            "node_kind": kind or None,
            "source_fields": ["insight_nodes_v0.nodes[0]"],
        }

    # Role of the vector follows node kind (context for consumers / UI later).
    role = {
        "repeat": "exit_recurring_trap",
        "tension": "steer_main_tension",
    }.get(kind, "from_selected_node")

    return {
        "projection_version": PROJECTION_VERSION,
        "effort_vector": help_line,
        "source_node_id": node_id,
        "node_kind": kind or None,
        "role": role,
        "source_fields": [
            "insight_nodes_v0.nodes[0].help",
            "insight_nodes_v0.nodes[0].id",
            "insight_nodes_v0.nodes[0].kind",
        ],
        "rules": {
            "no_llm": True,
            "source_only_selected_insight_node": True,
            "forbid_life_mission": True,
            "forbid_today_astrology_rec_lists": True,
            "null_when_no_safe_help": True,
            "insight_is_context_not_vector": True,
        },
    }


def attach_effort_vector_v0(payload: dict[str, Any]) -> dict[str, Any]:
    """Ephemeral read-path attach — never persist into Snapshot."""
    if not isinstance(payload, dict):
        return payload
    payload["effort_vector_v0"] = project_effort_vector_v0(
        insight_nodes=payload.get("insight_nodes_v0")
        if isinstance(payload.get("insight_nodes_v0"), dict)
        else None,
    )
    return payload
