"""Adapter: seasonal_calendar (sun rise/set + day length) for Day Foundation L1."""

from __future__ import annotations

from todayflow_backend.services.day_sources.sun_rise_set import sun_rise_set_local
from todayflow_backend.services.day_sources.types import DaySourceInputs, SourceResult

_CALC = "seasonal-calendar-adapter-v0"


def run_seasonal_calendar(inputs: DaySourceInputs) -> SourceResult:
    if inputs.lat is None or inputs.lon is None:
        return SourceResult(
            family_id="seasonal_calendar",
            capability_ids=[],
            layer="foundation",
            status="unavailable",
            unavailable_reason="missing_geo",
            calculation_version=_CALC,
        )
    try:
        sun = sun_rise_set_local(
            inputs.target_date,
            lat=float(inputs.lat),
            lon=float(inputs.lon),
            timezone_name=inputs.timezone,
        )
    except ValueError as exc:
        return SourceResult(
            family_id="seasonal_calendar",
            capability_ids=[],
            layer="foundation",
            status="unavailable",
            unavailable_reason=str(exc) or "sun_times_unavailable",
            calculation_version=_CALC,
        )

    # Rough meteorological season by month (N hemisphere); flip later if needed.
    month = inputs.target_date.month
    if month in (12, 1, 2):
        season = "winter"
        season_ru = "зима"
    elif month in (3, 4, 5):
        season = "spring"
        season_ru = "весна"
    elif month in (6, 7, 8):
        season = "summer"
        season_ru = "лето"
    else:
        season = "autumn"
        season_ru = "осень"

    return SourceResult(
        family_id="seasonal_calendar",
        capability_ids=["sun_rise_set", "season"],
        layer="foundation",
        status="ok",
        payload={
            "sun": sun,
            "season": season,
            "season_ru": season_ru,
            "summary_ru": (
                f"Восход {sun['sunrise_local'][11:16]}, закат {sun['sunset_local'][11:16]} "
                f"(день ≈ {sun['day_length_minutes']} мин). Сезон — {season_ru}."
            ),
        },
        evidence_refs=["target_date", "geo", "timezone"],
        calculation_version=_CALC,
    )
