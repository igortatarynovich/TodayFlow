"""Project legacy ``profile_contract_v1`` from Character Engine adapters.

Used when CHARACTER_ENGINE_PUBLISH_READY is on — CE is SoT; contract is a DTO projection.
"""

from __future__ import annotations

import re
from typing import Any

from todayflow_backend.services.profile_contract_v1 import (
    PROFILE_STATUS_FORMING,
    PROFILE_STATUS_READY,
    enrich_profile_contract_living,
)

_MAX = 720


def _clip(text: Any, n: int = _MAX) -> str:
    s = re.sub(r"\s+", " ", str(text or "").strip())
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def _adapter_val(fields: dict[str, Any], key: str) -> Any:
    row = fields.get(key)
    if not isinstance(row, dict):
        return None
    return row.get("value")


def project_profile_contract_from_character_engine_v0(
    payload: dict[str, Any],
    *,
    living: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build profile_contract_v1 from ``character_engine_v1`` (+ Stage nests fallback)."""
    ce = payload.get("character_engine_v1") if isinstance(payload.get("character_engine_v1"), dict) else {}
    legacy = ce.get("legacy_projections") if isinstance(ce.get("legacy_projections"), dict) else {}
    fields = legacy.get("fields") if isinstance(legacy.get("fields"), dict) else {}

    # Fallback: Stage 5 nest if envelope legacy missing.
    if not fields:
        diag = payload.get("diagnostics") if isinstance(payload.get("diagnostics"), dict) else {}
        s5 = (diag.get("character_engine_stage5") or {}).get("stage5") or {}
        lm = s5.get("legacy_map") if isinstance(s5, dict) else {}
        if isinstance(lm, dict):
            fields = lm.get("fields") if isinstance(lm.get("fields"), dict) else {}

    identity = _clip(_adapter_val(fields, "identity_core") or _adapter_val(fields, "recognition_line") or "")
    if not identity:
        cascade = ce.get("cascade") if isinstance(ce.get("cascade"), dict) else {}
        ic = cascade.get("identity_core") if isinstance(cascade.get("identity_core"), dict) else {}
        identity = _clip(ic.get("surface_text") or "")

    recognition = _clip(_adapter_val(fields, "recognition_line") or identity, 220)
    strengths = _adapter_val(fields, "strengths")
    if not isinstance(strengths, list):
        strengths = [strengths] if strengths else []
    strengths = [_clip(x, 360) for x in strengths if str(x or "").strip()][:4]
    growth = _adapter_val(fields, "growth_zones")
    if not isinstance(growth, list):
        growth = [growth] if growth else []
    growth = [_clip(x, 360) for x in growth if str(x or "").strip()][:3]
    helps = _adapter_val(fields, "helps")
    if not isinstance(helps, list):
        helps = [helps] if helps else []
    helps = [_clip(x, 360) for x in helps if str(x or "").strip()][:3]
    patterns = _adapter_val(fields, "recurring_patterns")
    if not isinstance(patterns, list):
        patterns = [patterns] if patterns else []
    patterns = [_clip(x, 360) for x in patterns if str(x or "").strip()][:3]

    ce_ready = str(ce.get("status") or "") == "ready"
    status = PROFILE_STATUS_READY if (ce_ready and identity) else PROFILE_STATUS_FORMING

    contract: dict[str, Any] = {
        "status": status,
        "identity_core": identity,
        "recognition_line": recognition or identity,
        "strengths": strengths,
        "growth_zones": growth,
        "helps": helps,
        "recurring_patterns": patterns,
        "decision_style": _clip(_adapter_val(fields, "decision_style") or "", 420) or None,
        "relationship_style": _clip(_adapter_val(fields, "relationship_style") or "", 420) or None,
        "money_style": _clip(_adapter_val(fields, "money_patterns") or "", 420) or None,
        "living_changes": None,
        "generation_meta": {
            "path": "character_engine_v1",
            "sot": "character_engine_v1",
            "ce_status": ce.get("status"),
            "adapter_version": legacy.get("adapter_version") or "character_engine_adapter_v1",
            "steps": [
                {
                    "prompt_id": "profile.character_engine.cascade",
                    "contract_id": "character_engine_v1",
                }
            ],
        },
    }
    for k in ("decision_style", "relationship_style", "money_style"):
        if not contract.get(k):
            contract[k] = None

    return enrich_profile_contract_living(contract, living=living)
