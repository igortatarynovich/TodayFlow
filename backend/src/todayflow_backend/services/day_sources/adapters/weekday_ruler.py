"""Adapter: weekday_ruler Source Family."""

from __future__ import annotations

from todayflow_backend.services.day_sources.types import DaySourceInputs, SourceResult

_CALC = "weekday-ruler-adapter-v0"

# Monday=0 … Sunday=6 (Python date.weekday)
_RULERS: list[tuple[str, str, str]] = [
    ("monday", "Moon", "Луна"),
    ("tuesday", "Mars", "Марс"),
    ("wednesday", "Mercury", "Меркурий"),
    ("thursday", "Jupiter", "Юпитер"),
    ("friday", "Venus", "Венера"),
    ("saturday", "Saturn", "Сатурн"),
    ("sunday", "Sun", "Солнце"),
]


def run_weekday_ruler(inputs: DaySourceInputs) -> SourceResult:
    wd = inputs.target_date.weekday()
    slug, planet, planet_ru = _RULERS[wd]
    return SourceResult(
        family_id="weekday_ruler",
        capability_ids=["weekday_ruler"],
        layer="foundation",
        status="ok",
        payload={
            "weekday": slug,
            "weekday_index": wd,
            "ruler_planet": planet,
            "ruler_planet_ru": planet_ru,
            "target_date": inputs.target_date.isoformat(),
        },
        evidence_refs=["target_date"],
        calculation_version=_CALC,
    )
