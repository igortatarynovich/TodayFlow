"""Adapter: bazi — personal pillars + clashes (L3, chinese_metaphysics §5.7)."""

from __future__ import annotations

from todayflow_backend.services.day_sources.bazi import build_bazi_personal_payload
from todayflow_backend.services.day_sources.types import DaySourceInputs, SourceResult

_CALC = "bazi-adapter-v0"


def run_bazi(inputs: DaySourceInputs) -> SourceResult:
    if inputs.birth_date is None:
        return SourceResult(
            family_id="bazi",
            capability_ids=[],
            layer="personal",
            status="unavailable",
            unavailable_reason="missing_birth_date",
            calculation_version=_CALC,
        )

    payload = build_bazi_personal_payload(
        inputs.target_date,
        inputs.birth_date,
        birth_time=inputs.birth_time,
    )
    return SourceResult(
        family_id="bazi",
        capability_ids=list(payload.get("capability_ids") or []),
        layer="personal",
        status="ok",
        payload=payload,
        evidence_refs=["birth_date", "target_date"]
        + (["birth_time"] if inputs.birth_time is not None else []),
        calculation_version=_CALC,
    )
