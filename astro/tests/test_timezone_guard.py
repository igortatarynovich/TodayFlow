"""Precise birth time must not silently treat civil clock as UT."""

from __future__ import annotations

import pytest

from todayflow_astro.core import models
from todayflow_astro.services.engine import AstroEngine
from todayflow_astro.services.errors import TimezoneRequiredError


def _req(*, tz=None, offset=None, time="12:12"):
    birth = models.BirthData(
        date="1990-02-13",
        time=time,
        location="Minsk",
        timezone_name=tz,
        timezone_offset_minutes=offset,
    )
    return models.ChartRequest(
        birth=birth,
        coordinates=models.Coordinates(latitude=53.9045, longitude=27.5615),
        timezone_name=tz,
        timezone_offset_minutes=offset,
    )


def test_precise_without_tz_raises():
    eng = AstroEngine()
    with pytest.raises(TimezoneRequiredError):
        eng._parse_birth_datetime_utc(_req())


def test_precise_with_iana_converts_to_ut():
    eng = AstroEngine()
    utc, precise, meta = eng._parse_birth_datetime_utc(_req(tz="Europe/Minsk"))
    assert precise is True
    assert utc.hour == 9
    assert utc.minute == 12
    assert meta.get("timezone_source") == "iana"


def test_precise_with_offset_converts_to_ut():
    eng = AstroEngine()
    utc, precise, meta = eng._parse_birth_datetime_utc(_req(offset=180))
    assert precise is True
    assert utc.hour == 9
    assert meta.get("timezone_source") == "offset"


def test_unknown_time_allows_midday_ut_without_tz():
    eng = AstroEngine()
    utc, precise, _meta = eng._parse_birth_datetime_utc(_req(time=None))
    assert precise is False
    assert utc.hour == 12
