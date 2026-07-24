"""Adapter: kabbalah_letter — Hebrew date / gematria / sefira soft (L3, not Foundation)."""

from __future__ import annotations

from todayflow_backend.services.day_sources.kabbalah_letter import build_kabbalah_letter_payload
from todayflow_backend.services.day_sources.types import DaySourceInputs, SourceResult

_CALC = "kabbalah-letter-adapter-v0"


def run_kabbalah_letter(inputs: DaySourceInputs) -> SourceResult:
    payload = build_kabbalah_letter_payload(inputs.target_date)
    return SourceResult(
        family_id="kabbalah_letter",
        capability_ids=list(payload.get("capability_ids") or []),
        layer="personal",
        status="ok",
        payload=payload,
        evidence_refs=["target_date"],
        calculation_version=_CALC,
    )
