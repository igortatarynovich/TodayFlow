"""Swiss Ephemeris path must be used; Moshier fallback must not be silent."""

from __future__ import annotations

import os

import pytest
import swisseph as swe

from todayflow_astro.core import models
from todayflow_astro.services.engine import AstroEngine
from todayflow_astro.services.errors import EphemerisDegradedError


def test_engine_reports_swiss_swieph_when_ephe_present():
    eng = AstroEngine()
    chart = eng.compute_chart(
        models.ChartRequest(
            birth=models.BirthData(
                date="1990-02-13",
                time="12:12",
                location="Minsk",
                timezone_name="Europe/Minsk",
            ),
            coordinates=models.Coordinates(latitude=53.9045, longitude=27.5615),
            timezone_name="Europe/Minsk",
        )
    )
    assert chart.metadata.get("ephemeris_source") == "swiss_swieph"
    rising = next(p for p in chart.positions if p.body == "rising")
    assert rising.sign == "Gemini"
    assert abs(rising.degree - 14.77) < 0.05


def test_cleared_ephe_path_raises_ephemeris_degraded(monkeypatch):
    eng = AstroEngine()
    if not eng._ephe_path or not os.path.isdir(eng._ephe_path):
        pytest.skip("no Swiss ephe path in this environment")
    # Poison process-global path; compute_chart must re-set or fail closed.
    swe.set_ephe_path("")
    monkeypatch.setattr(eng, "_ephe_path", "/tmp/todayflow-missing-ephe-dir")
    with pytest.raises(EphemerisDegradedError):
        eng.compute_chart(
            models.ChartRequest(
                birth=models.BirthData(
                    date="1990-02-13",
                    time="12:12",
                    location="Minsk",
                    timezone_name="Europe/Minsk",
                ),
                coordinates=models.Coordinates(latitude=53.9045, longitude=27.5615),
                timezone_name="Europe/Minsk",
            )
        )
    # Restore for other tests in the same process.
    if os.path.isdir("/app/ephe"):
        swe.set_ephe_path("/app/ephe")
    elif os.getenv("SWISS_EPHEMERIS_PATH"):
        swe.set_ephe_path(os.environ["SWISS_EPHEMERIS_PATH"])
