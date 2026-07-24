"""Adapter: mayan_calendars — Tzolkin/Haab + Dreamspell (soft Foundation)."""

from __future__ import annotations

from todayflow_backend.services.day_sources.mayan_calendars import build_mayan_calendars_payload
from todayflow_backend.services.day_sources.types import DaySourceInputs, SourceResult

_CALC = "mayan-calendars-adapter-v0"


def run_mayan_calendars(inputs: DaySourceInputs) -> SourceResult:
    payload = build_mayan_calendars_payload(inputs.target_date)
    return SourceResult(
        family_id="mayan_calendars",
        capability_ids=list(payload.get("capability_ids") or []),
        layer="foundation",
        status="ok",
        payload=payload,
        evidence_refs=["target_date"],
        calculation_version=_CALC,
    )
