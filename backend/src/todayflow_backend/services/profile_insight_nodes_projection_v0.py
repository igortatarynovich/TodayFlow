"""Deterministic Profile Step-3 insight node projection (journey «Не замечал»).

SoT: docs/PROFILE_PRODUCT_JOURNEY_FORMS_V1.md § Шаг 3
Reuses Snapshot materials as-is — does NOT invent a second patterns schema:
  recurring_patterns[] · growth_zones[] · strengths[] · helps[] · living.signals
Grounded-on facts come from portrait_why_v0 (labels only — no causal trace claim).
Read-path only (like natal_summary / portrait_why_v0).
"""

from __future__ import annotations

import re
from typing import Any

PROJECTION_VERSION = "profile_insight_nodes_v0.1"
_MAX_NODES_FIRST_RELEASE = 1
_MAX_LIVING_QUOTES = 2
_MAX_INSIGHT = 220
_MAX_HELP = 180
_MAX_QUOTE = 160


def _clip(text: str, limit: int) -> str:
    t = re.sub(r"\s+", " ", str(text or "").strip())
    if len(t) <= limit:
        return t
    return t[: limit - 1].rstrip() + "…"


def _first_nonempty(items: Any) -> str | None:
    if not isinstance(items, list):
        return None
    for item in items:
        s = _clip(str(item or ""), _MAX_INSIGHT)
        if len(s) >= 8:
            return s
    return None


def _living_quotes(living: dict[str, Any] | None) -> list[str]:
    if not isinstance(living, dict):
        return []
    out: list[str] = []
    signals = living.get("signals")
    if isinstance(signals, list):
        for row in signals:
            if not isinstance(row, dict):
                continue
            note = _clip(str(row.get("note") or ""), _MAX_QUOTE)
            if len(note) < 6:
                continue
            # Present as short evidence quote; do not invent.
            q = note if note.startswith("«") else f"«{note.rstrip('.')}»"
            if q not in out:
                out.append(q)
            if len(out) >= _MAX_LIVING_QUOTES:
                break
    return out


def _grounded_on_from_why(portrait_why: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Fact labels only — Forms: «На что опирается вывод», not causal «Почему»."""
    if not isinstance(portrait_why, dict):
        return []
    rows: list[dict[str, Any]] = []
    for block_key in ("selected_by", "portrait_influenced_by"):
        for item in portrait_why.get(block_key) or []:
            if not isinstance(item, dict):
                continue
            label = str(item.get("label") or "").strip()
            if not label:
                continue
            # Prefer short fact tokens for node density (sun / LP / element / rhythm).
            fid = str(item.get("id") or "")
            if fid == "archetype_from_life_path":
                lp = item.get("life_path")
                label = f"число пути {lp}" if lp is not None else label
            elif fid == "sun":
                # Keep «Солнце в …»
                pass
            elif fid == "element":
                pass
            elif fid == "rhythm":
                # Shorten display: use value if present
                val = str(item.get("value") or "").strip()
                label = f"ритм — {val[0].lower() + val[1:]}" if val else label
            elif fid in ("moon", "asc", "mc"):
                # Step-3 grounded_on: keep birth-static anchors only for first release.
                continue
            rows.append(
                {
                    "id": fid or f"fact_{len(rows)}",
                    "label": label,
                    "fact_keys": list(item.get("fact_keys") or []),
                    "role": "grounded_on",
                }
            )
    # Cap density: LP + sun + element + rhythm
    order = {"archetype_from_life_path": 0, "sun": 1, "element": 2, "rhythm": 3}
    rows.sort(key=lambda r: order.get(str(r.get("id")), 99))
    return rows[:4]


def project_insight_nodes_v0(
    *,
    contract: dict[str, Any] | None,
    portrait_why: dict[str, Any] | None = None,
    living: dict[str, Any] | None = None,
    max_nodes: int = _MAX_NODES_FIRST_RELEASE,
) -> dict[str, Any]:
    """Compose 0..N story nodes from existing contract + living materials."""
    c = contract if isinstance(contract, dict) else {}
    grounded = _grounded_on_from_why(portrait_why)
    living_quotes = _living_quotes(living)

    patterns = _first_nonempty(c.get("recurring_patterns"))
    growth = _first_nonempty(c.get("growth_zones"))
    strength = _first_nonempty(c.get("strengths"))
    help_from_contract = _first_nonempty(c.get("helps"))

    nodes: list[dict[str, Any]] = []

    # Prefer confirmed repeat when gate produced patterns (living-backed Snapshot strings).
    if patterns and len(nodes) < max_nodes:
        source_fields = ["profile_contract_v1.recurring_patterns"]
        node: dict[str, Any] = {
            "id": "node_repeat_0",
            "kind": "repeat",
            "title": "Самая большая ловушка",
            "insight": patterns,
            "grounded_on": grounded,
            "help": help_from_contract,
            "source_fields": source_fields,
        }
        if help_from_contract:
            source_fields.append("profile_contract_v1.helps")
        if living_quotes:
            node["living_evidence"] = living_quotes
            source_fields.append("living.signals.note")
        node["source_fields"] = source_fields
        nodes.append(node)

    # Birth-only / no patterns: one tension node from growth_zones (Forms Case A).
    elif growth and len(nodes) < max_nodes:
        # Without living helps, strength may serve as practical support — not as living evidence.
        help_for_node = help_from_contract or (_clip(strength, _MAX_HELP) if strength else None)
        source_fields = ["profile_contract_v1.growth_zones"]
        node = {
            "id": "node_tension_0",
            "kind": "tension",
            "title": "Главное напряжение",
            "insight": growth,
            "grounded_on": grounded,
            "help": help_for_node,
            "source_fields": source_fields,
        }
        if help_for_node:
            source_fields.append(
                "profile_contract_v1.helps" if help_from_contract else "profile_contract_v1.strengths"
            )
        # living_evidence only when real signal notes exist (never invent from birth).
        if living_quotes:
            node["living_evidence"] = living_quotes
            source_fields.append("living.signals.note")
        node["source_fields"] = source_fields
        nodes.append(node)

    return {
        "projection_version": PROJECTION_VERSION,
        "nodes": nodes,
        "rules": {
            "max_nodes_first_release": _MAX_NODES_FIRST_RELEASE,
            "no_per_node_causal_trace": True,
            "living_evidence_requires_signal_notes": True,
            # v0: nearby living context only — NOT proven evidence for this specific pattern.
            # UI must not label quotes as «это уже проявлялось так» without a linked match.
            "living_evidence_is_adjacent_context_not_proof": True,
            "snapshot_materials_unchanged": True,
            "not_a_second_patterns_schema": True,
        },
    }


def attach_insight_nodes_v0(payload: dict[str, Any]) -> dict[str, Any]:
    """Ephemeral read-path attach — never persist into Snapshot."""
    if not isinstance(payload, dict):
        return payload
    payload["insight_nodes_v0"] = project_insight_nodes_v0(
        contract=payload.get("profile_contract_v1")
        if isinstance(payload.get("profile_contract_v1"), dict)
        else None,
        portrait_why=payload.get("portrait_why_v0")
        if isinstance(payload.get("portrait_why_v0"), dict)
        else None,
        living=payload.get("living") if isinstance(payload.get("living"), dict) else None,
    )
    return payload
