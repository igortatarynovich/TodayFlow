"""Adapter: seasonal_calendar (season + optional sun + soft holidays) for Day Foundation L1."""

from __future__ import annotations

from todayflow_backend.services.day_sources.holidays import holidays_for_date
from todayflow_backend.services.day_sources.sun_rise_set import sun_rise_set_local
from todayflow_backend.services.day_sources.types import DaySourceInputs, SourceResult

_CALC = "seasonal-calendar-adapter-v1"


def _season_for_month(month: int) -> tuple[str, str]:
    # Rough meteorological season by month (N hemisphere); flip later if needed.
    if month in (12, 1, 2):
        return "winter", "зима"
    if month in (3, 4, 5):
        return "spring", "весна"
    if month in (6, 7, 8):
        return "summer", "лето"
    return "autumn", "осень"


def run_seasonal_calendar(inputs: DaySourceInputs) -> SourceResult:
    season, season_ru = _season_for_month(inputs.target_date.month)
    holidays = holidays_for_date(inputs.target_date, locale=inputs.locale)
    caps = ["season", "holidays"]
    evidence = ["target_date", "locale"]
    sun = None
    sun_note = ""

    if inputs.lat is not None and inputs.lon is not None:
        try:
            sun = sun_rise_set_local(
                inputs.target_date,
                lat=float(inputs.lat),
                lon=float(inputs.lon),
                timezone_name=inputs.timezone,
            )
            caps.append("sun_rise_set")
            evidence.extend(["geo", "timezone"])
            sun_note = (
                f"Восход {sun['sunrise_local'][11:16]}, закат {sun['sunset_local'][11:16]} "
                f"(день ≈ {sun['day_length_minutes']} мин). "
            )
        except ValueError:
            sun = None

    holiday_bit = ""
    if holidays.get("is_holiday") and holidays.get("today"):
        holiday_bit = f" Сегодня — {holidays['today'][0]['name_ru']}."

    summary = f"{sun_note}Сезон — {season_ru}.{holiday_bit}".strip()

    return SourceResult(
        family_id="seasonal_calendar",
        capability_ids=caps,
        layer="foundation",
        status="ok",
        payload={
            "sun": sun,
            "season": season,
            "season_ru": season_ru,
            "holidays": holidays,
            "summary_ru": summary,
            "notes_ru": (
                None
                if sun
                else "Без geo: сезон + holidays soft; восход/закат недоступны."
            ),
        },
        evidence_refs=evidence,
        calculation_version=_CALC,
    )
