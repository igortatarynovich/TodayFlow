"""Deterministic Profile Step-5 bridge_line (journey «хочу возвращаться»).

SoT: docs/PROFILE_PRODUCT_JOURNEY_FORMS_V1.md § Шаг 5
     docs/PRODUCT_BLOCK_SIX_QUESTIONS.md — bridge = path transition, not empty CTA
Source: selected insight node (+ whether living context exists). Not day forecast.
Read-path only. No LLM. No Snapshot fields.
"""

from __future__ import annotations

from typing import Any

PROJECTION_VERSION = "profile_bridge_line_v0.1"

# Kind-based bridges — value of next action, not «tomorrow will…».
_BRIDGE_TENSION_RU = (
    "Наблюдения за несколько дней откроют, что у вас реально повторяется "
    "— не как теория, а как ваш ритм."
)
_BRIDGE_REPEAT_RU = (
    "Отметь в Today следующий момент, где может повториться эта ловушка "
    "— так станет видно, удалось ли её изменить."
)
_CTA_TODAY = "today"


def project_bridge_line_v0(
    *,
    insight_nodes: dict[str, Any] | None,
    effort_vector: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Logical exit from static portrait into daily practice."""
    _ = effort_vector  # available for future: tighten copy when vector present; not required for v0
    pack = insight_nodes if isinstance(insight_nodes, dict) else {}
    nodes = pack.get("nodes") if isinstance(pack.get("nodes"), list) else []

    empty = {
        "projection_version": PROJECTION_VERSION,
        "bridge_line": None,
        "cta": None,
        "leads_to": None,
        "source_node_id": None,
        "source_fields": [],
        "rules": {
            "no_llm": True,
            "not_empty_cta": True,
            "forbid_day_forecast": True,
            "path_transition_not_marketing": True,
        },
    }

    if not nodes or not isinstance(nodes[0], dict):
        # No Step-3 node → no Profile→practice bridge from this journey slice.
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
            "not_empty_cta": True,
            "forbid_day_forecast": True,
            "path_transition_not_marketing": True,
            "six_questions": {
                "why": "exit static portrait into lived practice",
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
