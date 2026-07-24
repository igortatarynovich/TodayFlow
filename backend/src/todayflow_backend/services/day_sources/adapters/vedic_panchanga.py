"""Adapter: vedic_panchanga Source Family (Lahiri day factors)."""

from __future__ import annotations

from todayflow_backend.services.day_sources.panchanga import build_panchanga_payload
from todayflow_backend.services.day_sources.types import DaySourceInputs, SourceResult

_CALC = "vedic-panchanga-adapter-v0"


def run_vedic_panchanga(inputs: DaySourceInputs) -> SourceResult:
    payload = build_panchanga_payload(
        inputs.target_date,
        lat=inputs.lat,
        lon=inputs.lon,
        timezone_name=inputs.timezone,
    )
    return SourceResult(
        family_id="vedic_panchanga",
        capability_ids=list(payload.get("capability_ids") or []),
        layer="foundation",
        status="ok",
        payload=payload,
        evidence_refs=["target_date"]
        + (["geo", "timezone"] if inputs.lat is not None and inputs.lon is not None else []),
        calculation_version=_CALC,
    )
