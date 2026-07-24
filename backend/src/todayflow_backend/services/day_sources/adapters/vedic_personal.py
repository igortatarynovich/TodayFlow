"""Adapter: vedic_personal — gochara + Vimshottari dasha (L3)."""

from __future__ import annotations

from todayflow_backend.services.day_sources.types import DaySourceInputs, SourceResult
from todayflow_backend.services.day_sources.vedic_personal import build_vedic_personal_payload

_CALC = "vedic-personal-adapter-v0"


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
        has_birth_time=has_time,
        has_birth_place=has_place,
    )
    return SourceResult(
        family_id="vedic_personal",
        capability_ids=list(payload.get("capability_ids") or []),
        layer="personal",
        status="ok",
        payload=payload,
        evidence_refs=["birth_date", "target_date"]
        + (["birth_time"] if has_time else [])
        + (["birth_place"] if has_place else []),
        calculation_version=_CALC,
    )
