"""Adapter: western_astrology Source Family (foundation slice from celestial_events)."""

from __future__ import annotations

from typing import Any

from todayflow_backend.services.day_sources.types import DaySourceInputs, SourceResult

_CALC = "western-astrology-adapter-v0"
_MOON_TOKENS = ("moon", "луна", "лун")


def _is_moonish(text: str | None) -> bool:
    low = (text or "").lower()
    return any(tok in low for tok in _MOON_TOKENS)


def run_western_astrology(inputs: DaySourceInputs) -> SourceResult:
    ce = inputs.celestial_events if isinstance(inputs.celestial_events, dict) else None
    if not ce:
        return SourceResult(
            family_id="western_astrology",
            capability_ids=[],
            layer="foundation",
            status="unavailable",
            unavailable_reason="missing_celestial_events",
            calculation_version=_CALC,
        )

    ingresses = [
        row
        for row in (ce.get("ingresses") or [])
        if isinstance(row, dict) and not _is_moonish(str(row.get("planet") or row.get("planet_ru")))
    ]
    retrogrades = [row for row in (ce.get("retrogrades") or []) if isinstance(row, dict)]
    aspects = [
        row
        for row in (ce.get("sky_aspects") or [])
        if isinstance(row, dict)
        and not _is_moonish(str(row.get("title") or ""))
        and not _is_moonish(str(row.get("story_ru") or ""))
    ]
    sun_sign = ce.get("sun_sign") if isinstance(ce.get("sun_sign"), dict) else None

    caps: list[str] = []
    if ingresses:
        caps.append("ingresses")
    if retrogrades:
        caps.append("retrogrades_and_stations")
    if aspects:
        caps.append("aspects")
    if sun_sign:
        caps.append("seasonal_solar_points")
    if caps:
        caps.insert(0, "planetary_positions")

    payload: dict[str, Any] = {
        "ingresses": ingresses,
        "retrogrades": retrogrades,
        "sky_aspects": aspects,
        "sun_sign": sun_sign,
    }
    if not caps:
        return SourceResult(
            family_id="western_astrology",
            capability_ids=[],
            layer="foundation",
            status="unavailable",
            unavailable_reason="empty_western_astrology_payload",
            payload=payload,
            evidence_refs=["celestial_events"],
            calculation_version=_CALC,
        )

    return SourceResult(
        family_id="western_astrology",
        capability_ids=caps,
        layer="foundation",
        status="ok",
        payload=payload,
        evidence_refs=["celestial_events"],
        calculation_version=_CALC,
    )
