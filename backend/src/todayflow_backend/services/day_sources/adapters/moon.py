"""Adapter: moon Source Family (foundation slice from celestial_events)."""

from __future__ import annotations

from typing import Any

from todayflow_backend.services.day_sources.types import DaySourceInputs, SourceResult

_CALC = "moon-adapter-v0"
_MOON_TOKENS = ("moon", "луна", "лун")


def _is_moonish(text: str | None) -> bool:
    low = (text or "").lower()
    return any(tok in low for tok in _MOON_TOKENS)


def run_moon(inputs: DaySourceInputs) -> SourceResult:
    ce = inputs.celestial_events if isinstance(inputs.celestial_events, dict) else None
    if not ce:
        return SourceResult(
            family_id="moon",
            capability_ids=[],
            layer="foundation",
            status="unavailable",
            unavailable_reason="missing_celestial_events",
            calculation_version=_CALC,
        )

    phase = ce.get("lunar_phase") if isinstance(ce.get("lunar_phase"), dict) else None
    moon_sign = ce.get("moon_sign") if isinstance(ce.get("moon_sign"), dict) else None
    voc = ce.get("void_of_course") if isinstance(ce.get("void_of_course"), dict) else None
    moon_ingresses = [
        row
        for row in (ce.get("ingresses") or [])
        if isinstance(row, dict)
        and (
            _is_moonish(str(row.get("planet") or ""))
            or _is_moonish(str(row.get("planet_ru") or ""))
        )
    ]
    lunar_aspects = [
        row
        for row in (ce.get("sky_aspects") or [])
        if isinstance(row, dict)
        and (
            _is_moonish(str(row.get("title") or ""))
            or _is_moonish(str(row.get("story_ru") or ""))
        )
    ]
    timed = [row for row in (ce.get("timed_lunar_aspects") or []) if isinstance(row, dict)]

    caps: list[str] = []
    if phase:
        caps.append("phase")
    if moon_sign or moon_ingresses:
        caps.append("sign")
    if lunar_aspects or timed:
        caps.append("lunar_aspects")
    if moon_ingresses:
        caps.append("ingresses")
    if voc and voc.get("status") == "ok":
        caps.append("void_of_course")

    payload: dict[str, Any] = {
        "lunar_phase": phase,
        "moon_sign": moon_sign,
        "ingresses": moon_ingresses,
        "lunar_aspects": lunar_aspects,
        "timed_lunar_aspects": timed,
        "void_of_course": voc,
    }

    if not caps:
        return SourceResult(
            family_id="moon",
            capability_ids=[],
            layer="foundation",
            status="unavailable",
            unavailable_reason="empty_moon_payload",
            payload=payload,
            evidence_refs=["celestial_events"],
            calculation_version=_CALC,
        )

    return SourceResult(
        family_id="moon",
        capability_ids=caps,
        layer="foundation",
        status="ok",
        payload=payload,
        evidence_refs=["celestial_events"],
        calculation_version=_CALC,
    )
