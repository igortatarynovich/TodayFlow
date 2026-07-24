"""Adapter: vedic_personal — gochara + Lagna gochara + Vimshottari dasha (L3)."""

from __future__ import annotations

from todayflow_backend.services.day_sources.types import DaySourceInputs, SourceResult
from todayflow_backend.services.day_sources.vedic_personal import build_vedic_personal_payload

_CALC = "vedic-personal-adapter-v1"


def run_vedic_personal(inputs: DaySourceInputs) -> SourceResult:
    if inputs.birth_date is None:
        return SourceResult(
            family_id="vedic_personal",
            capability_ids=[],
            layer="personal",
            status="unavailable",
            unavailable_reason="missing_birth_date",
            calculation_version=_CALC,
        )

    has_time = inputs.birth_time is not None
    has_place = inputs.birth_lat is not None and inputs.birth_lon is not None
    payload = build_vedic_personal_payload(
        inputs.target_date,
        inputs.birth_date,
        birth_time=inputs.birth_time,
        birth_lat=inputs.birth_lat,
        birth_lon=inputs.birth_lon,
        timezone_name=inputs.timezone,
    )
    return SourceResult(
        family_id="vedic_personal",
        capability_ids=list(payload.get("capability_ids") or []),
        layer="personal",
        status="ok",
        payload=payload,
        evidence_refs=["birth_date", "target_date"]
        + (["birth_time"] if has_time else [])
        + (["birth_place"] if has_place else [])
        + (["timezone"] if inputs.timezone else []),
        calculation_version=_CALC,
    )
