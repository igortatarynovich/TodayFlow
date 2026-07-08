"""guide_contract_v2 — явный контракт HTTP payload для surface=guide (DE-13 v5).

Добавляет ``contract_version`` и ``guide_pipeline`` (lineage funnel/monolith) без ломки
плоских полей §9 DAY_ENGINE_AND_COHERENCE (headline, core_message, action_options, …).
"""

from __future__ import annotations

from typing import Any, Literal

from todayflow_backend.services.guide_narrative_funnel_v0 import (
    CORE_CONTRACT,
    FUNNEL_CHILD_CHAIN_CONTRACT,
    FUNNEL_CONTRACT,
    INTERP_CONTRACT,
    SATELLITES_CONTRACT,
)

GUIDE_CONTRACT_V2 = "guide_contract_v2"
GUIDE_PIPELINE_V0 = "guide_pipeline_v0"

GenerationMode = Literal["funnel", "monolith"]


def build_guide_pipeline_v0(
    *,
    generation_mode: GenerationMode,
    input_payload: dict[str, Any] | None,
    context_for_next_surfaces: str | None = None,
) -> dict[str, Any]:
    """Метаданные цепочки генерации для клиентов и learning logs."""
    ip = input_payload if isinstance(input_payload, dict) else {}
    out: dict[str, Any] = {
        "contract_version": GUIDE_PIPELINE_V0,
        "generation_mode": generation_mode,
    }
    if generation_mode == "funnel":
        out["funnel_contract"] = str(ip.get("guide_funnel_contract") or FUNNEL_CONTRACT)
        core_source = str(ip.get("guide_funnel_core_source") or "guide_decision_v0")
        out["steps"] = {
            "interpretation": {
                "contract_version": INTERP_CONTRACT,
                "generation_log_id": ip.get("guide_funnel_parent_log_id"),
                "cache_hit": bool(ip.get("guide_funnel_step1_cache_hit")),
            },
            "core_text": {
                "contract_version": CORE_CONTRACT
                if core_source == "funnel_core_text_v0"
                else "guide_decision_v0",
                "generation_log_id": ip.get("guide_funnel_step3_log_id"),
                "cache_hit": bool(ip.get("guide_funnel_step3_cache_hit")),
                "source": core_source,
            },
            "satellites": {
                "contract_version": SATELLITES_CONTRACT,
                "generation_log_id": ip.get("guide_funnel_step2_log_id"),
                "cache_hit": bool(ip.get("guide_funnel_step2_cache_hit")),
            },
        }
    cfs = str(context_for_next_surfaces or "").strip()
    if cfs:
        out["child_chain"] = {
            "contract_version": FUNNEL_CHILD_CHAIN_CONTRACT,
            "context_for_next_surfaces": cfs[:1200],
        }
    return out


def attach_guide_contract_v2(
    payload: dict[str, Any],
    *,
    input_payload: dict[str, Any] | None,
) -> None:
    """In-place: top-level ``contract_version`` + ``guide_pipeline`` на guide payload."""
    if not isinstance(payload, dict):
        return
    ip = input_payload if isinstance(input_payload, dict) else {}
    mode: GenerationMode = "funnel" if ip.get("guide_funnel_used") else "monolith"
    payload["contract_version"] = GUIDE_CONTRACT_V2
    payload["guide_pipeline"] = build_guide_pipeline_v0(
        generation_mode=mode,
        input_payload=ip,
        context_for_next_surfaces=str(payload.get("context_for_next_surfaces") or ""),
    )


def guide_funnel_core_is_llm_locked(input_payload: dict[str, Any] | None) -> bool:
    """True когда ядро guide из funnel step3 — не перезаписывать guide_decision_v0."""
    if not isinstance(input_payload, dict):
        return False
    return str(input_payload.get("guide_funnel_core_source") or "") == "funnel_core_text_v0"
