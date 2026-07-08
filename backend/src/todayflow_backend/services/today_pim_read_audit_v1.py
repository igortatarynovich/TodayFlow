"""PR1 — auditable PIM read path markers for Today DRE (generation orchestration log)."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

PIM_READ_AUDIT_CONTRACT = "today_pim_read_audit_v1"


def build_pim_read_audit_v1(
    *,
    day_ctx: dict[str, Any],
    ritual_context: dict[str, Any] | None,
    fusion_dump: dict[str, Any] | None,
    read_model_id: str | None = None,
) -> dict[str, Any]:
    """
    Emits pim_slice_requested / pim_slice_used / dre_fields_used for orchestration trace.
    Empty atom_ids[] is valid on day-1.
    """
    layers = day_ctx.get("layers") if isinstance(day_ctx.get("layers"), dict) else {}
    kcs = layers.get("knowledge_context_slice")
    atom_ids: list[str] = []
    if isinstance(kcs, dict):
        items = kcs.get("items")
        if not isinstance(items, list):
            items = kcs.get("atoms")
        if isinstance(items, list):
            for item in items:
                if not isinstance(item, dict):
                    continue
                kid = item.get("knowledge_id") or item.get("id")
                if kid:
                    atom_ids.append(str(kid))

    dre_fields_used: list[str] = []
    ritual = ritual_context if isinstance(ritual_context, dict) else {}
    for key in ritual:
        dre_fields_used.append(f"ritual_context.{key}")
    if isinstance(kcs, dict) and kcs:
        dre_fields_used.append("layers.knowledge_context_slice")
    if isinstance(fusion_dump, dict) and fusion_dump.get("scores"):
        dre_fields_used.append("fusion_dump.scores")
    if layers.get("day_engine_brief"):
        dre_fields_used.append("layers.day_engine_brief")
    if layers.get("guide_decision"):
        dre_fields_used.append("layers.guide_decision")
    if layers.get("day_model"):
        dre_fields_used.append("layers.day_model")
    if layers.get("behavior_patterns"):
        dre_fields_used.append("layers.behavior_patterns")

    rid = (read_model_id or "").strip() or f"pr1-{uuid4().hex[:12]}"

    return {
        "contract_version": PIM_READ_AUDIT_CONTRACT,
        "pim_slice_requested": {
            "read_model_id": rid,
            "slice_policy_version": "pr1_v1",
        },
        "pim_slice_used": {
            "read_model_id": rid,
            "atom_count": len(atom_ids),
            "atom_ids": atom_ids,
            "knowledge_fact_count": len(atom_ids),
        },
        "dre_fields_used": sorted(set(dre_fields_used)),
    }
