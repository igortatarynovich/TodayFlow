"""Adapter: chinese_metaphysics Source Family (day pillar / Jianchu / jieqi)."""

from __future__ import annotations

from todayflow_backend.services.day_sources.chinese_metaphysics import build_chinese_day_payload
from todayflow_backend.services.day_sources.types import DaySourceInputs, SourceResult

_CALC = "chinese-metaphysics-adapter-v0"


def run_chinese_metaphysics(inputs: DaySourceInputs) -> SourceResult:
    # Canon: civil date + TZ. Day boundary stays civil target_date for v0.
    payload = build_chinese_day_payload(inputs.target_date)
    return SourceResult(
        family_id="chinese_metaphysics",
        capability_ids=list(payload.get("capability_ids") or []),
        layer="foundation",
        status="ok",
        payload=payload,
        evidence_refs=["target_date"] + (["timezone"] if inputs.timezone else []),
        calculation_version=_CALC,
    )
