"""Adapter: human_design — transit gates + soft bodygraph (L3 Personal)."""

from __future__ import annotations

from todayflow_backend.services.day_sources.human_design import build_human_design_payload
from todayflow_backend.services.day_sources.types import DaySourceInputs, SourceResult

_CALC = "human-design-adapter-v0"


def run_human_design(inputs: DaySourceInputs) -> SourceResult:
    has_time = inputs.birth_time is not None
    has_place = inputs.birth_lat is not None and inputs.birth_lon is not None
    payload = build_human_design_payload(
        inputs.target_date,
        birth_date=inputs.birth_date,
        has_birth_time=has_time,
        has_birth_place=has_place,
    )
    return SourceResult(
        family_id="human_design",
        capability_ids=list(payload.get("capability_ids") or []),
        layer="personal",
        status="ok",
        payload=payload,
        evidence_refs=["target_date"]
        + (["birth_date"] if inputs.birth_date else [])
        + (["birth_time"] if has_time else [])
        + (["birth_place"] if has_place else []),
        calculation_version=_CALC,
    )
