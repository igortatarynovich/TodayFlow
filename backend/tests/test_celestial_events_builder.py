"""Tests for celestial_events_builder."""

from __future__ import annotations

import asyncio
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

from todayflow_backend.services.celestial_events_builder import (
    _format_personal_transit,
    _symbol_preset_index,
    build_celestial_events,
)


def test_format_personal_transit_ru():
    row = _format_personal_transit(
        {
            "transiting_planet": "Mars",
            "natal_planet": "Saturn",
            "aspect": "square",
            "strength": "strong",
        }
    )
    assert row is not None
    assert "Марс" in row["title"]
    assert "Сатурн" in row["title"]
    assert row["story_ru"]


def test_symbol_preset_index_stable():
    d = date(2026, 6, 23)
    a = _symbol_preset_index(d, 7)
    b = _symbol_preset_index(d, 7)
    assert a == b
    assert 0 <= a < 12


def test_build_celestial_events_includes_symbols_and_transits():
    from types import SimpleNamespace

    mock_current = SimpleNamespace(
        id="full",
        name="Полнолуние",
        themes="эмоциональная ясность",
        guidance="завершение цикла",
        keywords=[],
        cycle_day=15,
    )
    mock_lunar = SimpleNamespace(current=mock_current, next_phase=None)

    mock_retro = SimpleNamespace(retrograde_planets=["Mercury"], ingresses=[])

    mock_chart = MagicMock()
    mock_chart.positions = [{"body": "Sun", "longitude": 10.0}, {"body": "Moon", "longitude": 100.0}]
    mock_astro = MagicMock()
    mock_astro.compute_chart = AsyncMock(return_value=mock_chart)

    with patch("todayflow_backend.services.celestial_events_builder.LunarService") as lunar_cls, patch(
        "todayflow_backend.services.celestial_events_builder.RetrogradeService"
    ) as retro_cls, patch(
        "todayflow_backend.services.celestial_events_builder.AspectEngine"
    ) as aspect_cls:
        lunar_cls.return_value.current_phase.return_value = mock_lunar
        retro_cls.return_value.get_retrograde_status = AsyncMock(return_value=mock_retro)
        aspect_cls.return_value.callouts.return_value = MagicMock(callouts=[])

        payload = asyncio.run(
            build_celestial_events(
                date(2026, 6, 23),
                "ru",
                personal_day=7,
                personal_transits=[
                    {"transiting_planet": "Venus", "natal_planet": "Moon", "aspect": "trine", "strength": "medium"}
                ],
                astro_service=mock_astro,
            )
        )

    assert payload["lunar_phase"]["name"] == "Полнолуние"
    assert payload["retrogrades"][0]["planet_ru"] == "Меркурий"
    assert payload["personal_transits"]
    assert payload["daily_symbols"]["totem"]["emoji"]
    assert payload["daily_symbols"]["color"]["name"]
