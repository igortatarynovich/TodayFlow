"""Adapter: electional_horary — situational elective/horary checklist (L3)."""

from __future__ import annotations

from datetime import time

from todayflow_backend.services.day_sources.electional_horary import (
    build_electional_horary_payload,
)
from todayflow_backend.services.day_sources.types import DaySourceInputs, SourceResult

_CALC = "electional-horary-adapter-v1"


def run_electional_horary(inputs: DaySourceInputs) -> SourceResult:
    if not inputs.electional_requested:
        return SourceResult(
            family_id="electional_horary",
            capability_ids=[],
            layer="personal",
            status="skipped",
            unavailable_reason="missing_explicit_request",
            calculation_version=_CALC,
            payload={"requested": False},
        )

    lat = inputs.lat if inputs.lat is not None else inputs.birth_lat
    lon = inputs.lon if inputs.lon is not None else inputs.birth_lon
    if lat is None or lon is None:
        return SourceResult(
            family_id="electional_horary",
            capability_ids=[],
            layer="personal",
            status="unavailable",
            unavailable_reason="missing_geo",
            calculation_version=_CALC,
            payload={"requested": True},
        )

    elected_time = inputs.electional_time or time(12, 0)
    payload = build_electional_horary_payload(
        inputs.target_date,
        electional_time=elected_time,
        lat=float(lat),
        lon=float(lon),
        timezone_name=inputs.timezone,
        question=inputs.electional_question,
        celestial_events=inputs.celestial_events,
    )
    if inputs.electional_time is None:
        payload["notes_ru"] = (
            str(payload.get("notes_ru") or "")
            + " Время не задано — использован полдень как мягкий прокси."
        ).strip()

    return SourceResult(
        family_id="electional_horary",
        capability_ids=list(payload.get("capability_ids") or []),
        layer="personal",
        status="ok",
        payload=payload,
        evidence_refs=["target_date", "geo", "electional_request"]
        + (["electional_time"] if inputs.electional_time is not None else [])
        + (["electional_question"] if inputs.electional_question else [])
        + (["timezone"] if inputs.timezone else []),
        calculation_version=_CALC,
    )
