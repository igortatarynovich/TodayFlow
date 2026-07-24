"""Tests for timed major Moon aspects + VOC wiring."""

from __future__ import annotations

import asyncio
from datetime import date, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from todayflow_backend.services.astro import ChartResponse
from todayflow_backend.services.celestial_events_builder import build_celestial_events
from todayflow_backend.services.day_sources.timed_lunar_aspects import (
    find_timed_major_moon_aspects,
)
from todayflow_backend.services.day_sources.void_of_course import build_void_of_course_v0


class _LinearMoonAstro:
    """Moon longitude advances ~13°/day from a fixed Sun at 0° — creates crossings."""

    def __init__(self, base: date) -> None:
        self.base = datetime.combine(base, datetime.min.time())

    async def compute_chart(self, birth_payload: dict, coordinates: dict | None = None):
        _ = coordinates
        when = datetime.fromisoformat(
            f"{birth_payload['date']}T{birth_payload.get('time') or '00:00:00'}"
        )
        hours = (when - self.base).total_seconds() / 3600.0
        moon_lon = (hours * (13.0 / 24.0)) % 360.0  # ~13°/day
        positions = [
            {"body": "sun", "longitude": 0.0, "sign": "Aries"},
            {"body": "moon", "longitude": moon_lon, "sign": "Aries"},
            {"body": "venus", "longitude": 60.0, "sign": "Gemini"},
            {"body": "mars", "longitude": 90.0, "sign": "Cancer"},
        ]
        return ChartResponse(mode="transit", positions=positions, houses={}, metadata={})


def test_find_timed_major_moon_aspects_finds_crossings():
    base = date(2026, 7, 20)
    aspects = asyncio.run(
        find_timed_major_moon_aspects(
            _LinearMoonAstro(base),
            target_date=date(2026, 7, 24),
            lookback_days=4,
            lookahead_days=1,
            step_hours=3,
        )
    )
    assert aspects
    assert all(a.get("exact_time") for a in aspects)
    assert any(a.get("aspect") == "conjunction" and a.get("planet") == "sun" for a in aspects)


def test_build_celestial_events_wires_timed_aspects_into_voc():
    mock_current = SimpleNamespace(
        id="full",
        name="Полнолуние",
        themes="t",
        guidance="g",
        keywords=[],
        cycle_day=15,
    )
    mock_lunar = SimpleNamespace(current=mock_current, next_phase=None)
    mock_retro = SimpleNamespace(
        retrograde_planets=[],
        ingresses=[
            SimpleNamespace(
                planet="Moon",
                sign="Leo",
                ingress_date="2026-07-25",
            )
        ],
    )
    mock_chart = MagicMock()
    mock_chart.positions = [
        {"body": "moon", "longitude": 100.0, "sign": "Cancer"},
        {"body": "sun", "longitude": 10.0, "sign": "Cancer"},
    ]
    mock_astro = MagicMock()
    mock_astro.compute_chart = AsyncMock(return_value=mock_chart)

    timed = [
        {
            "id": "moon-trine-venus-1",
            "aspect": "trine",
            "planet": "venus",
            "exact_time": "2026-07-24T08:00:00",
            "title": "Луна — тригон — Венера",
        }
    ]

    with patch("todayflow_backend.services.celestial_events_builder.LunarService") as lunar_cls, patch(
        "todayflow_backend.services.celestial_events_builder.RetrogradeService"
    ) as retro_cls, patch(
        "todayflow_backend.services.celestial_events_builder.AspectEngine"
    ) as aspect_cls, patch(
        "todayflow_backend.services.celestial_events_builder.find_timed_major_moon_aspects",
        new=AsyncMock(return_value=timed),
    ), patch(
        "todayflow_backend.services.celestial_events_builder.find_moon_sign_ingress_time",
        new=AsyncMock(return_value=datetime(2026, 7, 25, 14, 30, 0)),
    ):
        lunar_cls.return_value.current_phase.return_value = mock_lunar
        retro_cls.return_value.get_retrograde_status = AsyncMock(return_value=mock_retro)
        aspect_cls.return_value.callouts.return_value = MagicMock(callouts=[])

        payload = asyncio.run(
            build_celestial_events(date(2026, 7, 24), "ru", astro_service=mock_astro)
        )

    assert payload["timed_lunar_aspects"] == timed
    assert payload["void_of_course"]["status"] == "ok"
    assert payload["void_of_course"]["in_void_of_course"] is True
    moon_ing = next(i for i in payload["ingresses"] if "oon" in str(i.get("planet")))
    assert moon_ing["exact_time"].startswith("2026-07-25T14:30")


def test_void_of_course_uses_exact_ingress_time():
    voc = build_void_of_course_v0(
        target_date=date(2026, 7, 24),
        ingresses=[{"planet": "Moon", "exact_time": "2026-07-25T14:30:00"}],
        timed_lunar_aspects=[{"id": "a", "exact_time": "2026-07-24T08:00:00"}],
    )
    assert voc["status"] == "ok"
    assert voc["ends_at"].startswith("2026-07-25T14:30")
    assert voc["in_void_of_course"] is True
