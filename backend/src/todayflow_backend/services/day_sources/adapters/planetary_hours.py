"""Adapter: planetary_hours — 24 unequal Chaldean hours from local sunrise/sunset."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from todayflow_backend.services.day_sources.sun_rise_set import parse_aware, sun_rise_set_local
from todayflow_backend.services.day_sources.types import DaySourceInputs, SourceResult

_CALC = "planetary-hours-adapter-v0"

# Chaldean order (descending speed historically used for hours).
_CHALDEAN: list[tuple[str, str]] = [
    ("Saturn", "Сатурн"),
    ("Jupiter", "Юпитер"),
    ("Mars", "Марс"),
    ("Sun", "Солнце"),
    ("Venus", "Венера"),
    ("Mercury", "Меркурий"),
    ("Moon", "Луна"),
]

# Monday=0 … Sunday=6 — day ruler at sunrise (same table as weekday_ruler).
_DAY_RULER: list[tuple[str, str]] = [
    ("Moon", "Луна"),
    ("Mars", "Марс"),
    ("Mercury", "Меркурий"),
    ("Jupiter", "Юпитер"),
    ("Venus", "Венера"),
    ("Saturn", "Сатурн"),
    ("Sun", "Солнце"),
]


def _build_hours(
    *,
    sunrise: datetime,
    sunset: datetime,
    next_sunrise: datetime,
    day_ruler: str,
) -> list[dict[str, Any]]:
    chaldean_ids = [p for p, _ in _CHALDEAN]
    ru_map = dict(_CHALDEAN)
    start_idx = chaldean_ids.index(day_ruler)
    day_span = (sunset - sunrise) / 12
    night_span = (next_sunrise - sunset) / 12
    hours: list[dict[str, Any]] = []
    cursor = sunrise
    for i in range(24):
        span = day_span if i < 12 else night_span
        end = cursor + span
        planet = chaldean_ids[(start_idx + i) % 7]
        hours.append(
            {
                "index": i + 1,
                "period": "day" if i < 12 else "night",
                "ruler_planet": planet,
                "ruler_planet_ru": ru_map[planet],
                "start_local": cursor.isoformat(timespec="seconds"),
                "end_local": end.isoformat(timespec="seconds"),
            }
        )
        cursor = end
    return hours


def build_planetary_hours_table(
    *,
    target_date: date,
    lat: float,
    lon: float,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    today = sun_rise_set_local(
        target_date, lat=lat, lon=lon, timezone_name=timezone_name
    )
    tomorrow = sun_rise_set_local(
        target_date + timedelta(days=1),
        lat=lat,
        lon=lon,
        timezone_name=timezone_name,
    )
    sunrise = parse_aware(today["sunrise_local"])
    sunset = parse_aware(today["sunset_local"])
    next_sunrise = parse_aware(tomorrow["sunrise_local"])
    # Ensure next sunrise is after sunset (date anchoring edge cases).
    if next_sunrise <= sunset:
        next_sunrise = next_sunrise + timedelta(days=1)

    day_ruler, day_ruler_ru = _DAY_RULER[target_date.weekday()]
    hours = _build_hours(
        sunrise=sunrise,
        sunset=sunset,
        next_sunrise=next_sunrise,
        day_ruler=day_ruler,
    )
    return {
        "day_ruler_planet": day_ruler,
        "day_ruler_planet_ru": day_ruler_ru,
        "sunrise_local": today["sunrise_local"],
        "sunset_local": today["sunset_local"],
        "next_sunrise_local": next_sunrise.isoformat(timespec="seconds"),
        "hours": hours,
        "method": "chaldean_unequal_v0",
        "sun_method": today.get("method"),
        "target_date": target_date.isoformat(),
    }


def run_planetary_hours(inputs: DaySourceInputs) -> SourceResult:
    if inputs.lat is None or inputs.lon is None:
        return SourceResult(
            family_id="planetary_hours",
            capability_ids=[],
            layer="foundation",
            status="unavailable",
            unavailable_reason="missing_geo",
            calculation_version=_CALC,
        )
    try:
        table = build_planetary_hours_table(
            target_date=inputs.target_date,
            lat=float(inputs.lat),
            lon=float(inputs.lon),
            timezone_name=inputs.timezone,
        )
    except ValueError as exc:
        return SourceResult(
            family_id="planetary_hours",
            capability_ids=[],
            layer="foundation",
            status="unavailable",
            unavailable_reason=str(exc) or "planetary_hours_unavailable",
            calculation_version=_CALC,
        )

    first = table["hours"][0] if table.get("hours") else {}
    summary = (
        f"Планетарные часы от восхода: первый час — {table['day_ruler_planet_ru']}"
        f" ({str(first.get('start_local') or '')[11:16]}–{str(first.get('end_local') or '')[11:16]})."
    )
    return SourceResult(
        family_id="planetary_hours",
        capability_ids=["planetary_hours"],
        layer="foundation",
        status="ok",
        payload={**table, "summary_ru": summary},
        evidence_refs=["target_date", "geo", "timezone"],
        calculation_version=_CALC,
    )
