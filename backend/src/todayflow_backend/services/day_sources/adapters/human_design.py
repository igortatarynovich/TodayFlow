"""Adapter: human_design — transit gates + soft bodygraph (L3 Personal)."""

from __future__ import annotations

from todayflow_backend.services.day_sources.human_design import build_human_design_payload
from todayflow_backend.services.day_sources.types import DaySourceInputs, SourceResult


def run_human_design(inputs: DaySourceInputs) -> SourceResult:
    has_time = inputs.birth_time is not None
    has_place = inputs.birth_lat is not None and inputs.birth_lon is not None
    payload = build_human_design_payload(
        inputs.target_date,
        birth_date=inputs.birth_date,
        has_birth_time=has_time,
        has_birth_place=has_place,
        ephemeris=inputs.ephemeris if isinstance(inputs.ephemeris, dict) else None,
    )
    evidence = ["target_date"]
    if inputs.birth_date:
        evidence.append("birth_date")
    if has_time:
        evidence.append("birth_time")
    if has_place:
        evidence.append("birth_place")
    if isinstance(inputs.ephemeris, dict) and (
        inputs.ephemeris.get("transit_noon") or inputs.ephemeris.get("natal")
    ):
        evidence.append("ephemeris_bridge")
    return SourceResult(
        family_id="human_design",
        capability_ids=list(payload.get("capability_ids") or []),
        layer="personal",
        status="ok",
        payload=payload,
        evidence_refs=evidence,
        calculation_version="human-design-adapter-v1-ephemeris",
    )
