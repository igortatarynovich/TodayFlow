"""Deterministic Profile Step-5 bridge_line (journey «хочу возвращаться»).

SoT: docs/profile/PROFILE_PRODUCT_JOURNEY_FORMS_V1.md § Шаг 5
     docs/PRODUCT_BLOCK_SIX_QUESTIONS.md

Answers ONLY: «Почему теперь имеет смысл открыть Today?»
Does NOT answer «что делать?» — that is effort_vector_v0.
Not motivation, not day forecast, not a second recommendation.

Read-path only. No LLM. No Snapshot fields.
"""

from __future__ import annotations

import re
from typing import Any

PROJECTION_VERSION = "profile_bridge_line_v0.2"

# Why Today continues the path — no imperative action (that belongs to effort_vector).
_BRIDGE_TENSION_RU = (
    "Особенность уже ясна на уровне портрета. "
    "Today показывает, как она проявляется в конкретном дне — не как теория."
)
_BRIDGE_REPEAT_RU = (
    "Повтор уже назван. "
    "Today — следующий экран пути: там видно, как эта ловушка проявляется сегодня "
    "и сдвигается ли она."
)
_CTA_TODAY = "today"

_ACTION_VERB_RE = re.compile(
    r"^(отметь|сделай|начни|добавь|открой|запиши|проверь|выбери)\b",
    re.I,
)


def _looks_like_effort_or_action(text: str) -> bool:
    """Guard: bridge must not read as a second effort_vector."""
    t = (text or "").strip()
    if not t:
        return False
    if _ACTION_VERB_RE.search(t):
        return True
    return False


def _near_duplicate(a: str | None, b: str | None) -> bool:
    na = re.sub(r"\s+", " ", (a or "").strip().lower())
    nb = re.sub(r"\s+", " ", (b or "").strip().lower())
    if not na or not nb:
        return False
    if na == nb:
        return True
    return len(na) >= 24 and (na in nb or nb in na)


def project_bridge_line_v0(
    *,
    insight_nodes: dict[str, Any] | None,
    effort_vector: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Why open Today now — path continuity after Profile insight."""
    pack = insight_nodes if isinstance(insight_nodes, dict) else {}
    nodes = pack.get("nodes") if isinstance(pack.get("nodes"), list) else []
    effort = effort_vector if isinstance(effort_vector, dict) else {}
    effort_text = str(effort.get("effort_vector") or "").strip() or None

    empty = {
        "projection_version": PROJECTION_VERSION,
        "bridge_line": None,
        "cta": None,
        "leads_to": None,
        "source_node_id": None,
        "source_fields": [],
        "rules": {
            "no_llm": True,
            "answers_why_open_today_only": True,
            "forbid_effort_vector_duplicate": True,
            "forbid_day_forecast": True,
            "forbid_imperative_action": True,
            "path_transition_not_marketing": True,
        },
    }

    if not nodes or not isinstance(nodes[0], dict):
        return empty

    node = nodes[0]
    node_id = str(node.get("id") or "").strip() or None
    kind = str(node.get("kind") or "").strip().lower()

    if kind == "repeat":
        line = _BRIDGE_REPEAT_RU
        source_fields = ["insight_nodes_v0.nodes[0].kind"]
        if node.get("living_evidence"):
            source_fields.append("insight_nodes_v0.nodes[0].living_evidence")
    elif kind == "tension":
        line = _BRIDGE_TENSION_RU
        source_fields = ["insight_nodes_v0.nodes[0].kind"]
    else:
        return empty

    # Safety: never ship a bridge that is action-advice or restates effort_vector.
    if _looks_like_effort_or_action(line) or _near_duplicate(line, effort_text):
        return {
            **empty,
            "source_node_id": node_id,
            "node_kind": kind,
            "source_fields": source_fields,
        }

    return {
        "projection_version": PROJECTION_VERSION,
        "bridge_line": line,
        "cta": _CTA_TODAY,
        "leads_to": "today",
        "source_node_id": node_id,
        "node_kind": kind,
        "source_fields": source_fields,
        "rules": {
            "no_llm": True,
            "answers_why_open_today_only": True,
            "forbid_effort_vector_duplicate": True,
            "forbid_day_forecast": True,
            "forbid_imperative_action": True,
            "path_transition_not_marketing": True,
            "six_questions": {
                "why": "why Today naturally continues this portrait now",
                "not": "what to do (that is effort_vector)",
                "leads_to": "today",
            },
        },
    }


def attach_bridge_line_v0(payload: dict[str, Any]) -> dict[str, Any]:
    """Ephemeral read-path attach — never persist into Snapshot."""
    if not isinstance(payload, dict):
        return payload
    payload["bridge_line_v0"] = project_bridge_line_v0(
        insight_nodes=payload.get("insight_nodes_v0")
        if isinstance(payload.get("insight_nodes_v0"), dict)
        else None,
        effort_vector=payload.get("effort_vector_v0")
        if isinstance(payload.get("effort_vector_v0"), dict)
        else None,
    )
    return payload
