"""Soft tropical mean longitudes for classical planets (day_sources).

Low-precision Meeus-style mean longitudes for noon civil dates.
Good enough for soft returns / HD gate seeds — not Swiss Ephemeris.
"""

from __future__ import annotations

from datetime import date
from typing import Callable

from todayflow_backend.services.day_sources.panchanga import (
    tropical_moon_longitude,
    tropical_sun_longitude,
)


def _julian_centuries(d: date) -> float:
    """Julian centuries from J2000.0 at civil noon (same as panchanga)."""
    a = (14 - d.month) // 12
    y = d.year + 4800 - a
    m = d.month + 12 * a - 3
    jd = d.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    jd += 0.5  # noon
    return (jd - 2451545.0) / 36525.0


def _norm(lon: float) -> float:
    return float(lon) % 360.0


def tropical_mercury_longitude(d: date) -> float:
    t = _julian_centuries(d)
    return _norm(252.250906 + 149472.6746358 * t)


def tropical_venus_longitude(d: date) -> float:
    t = _julian_centuries(d)
    return _norm(181.979801 + 58517.8156760 * t)


def tropical_mars_longitude(d: date) -> float:
    t = _julian_centuries(d)
    return _norm(355.433000 + 19140.2993039 * t)


def tropical_jupiter_longitude(d: date) -> float:
    t = _julian_centuries(d)
    return _norm(34.351519 + 3034.9056606 * t)


def tropical_saturn_longitude(d: date) -> float:
    t = _julian_centuries(d)
    return _norm(50.077444 + 1222.1138488 * t)


def tropical_uranus_longitude(d: date) -> float:
    t = _julian_centuries(d)
    return _norm(314.055005 + 428.4669983 * t - 0.00000486 * t * t)


def tropical_neptune_longitude(d: date) -> float:
    t = _julian_centuries(d)
    return _norm(304.348665 + 218.4862002 * t + 0.00000036 * t * t)


def tropical_pluto_longitude(d: date) -> float:
    # Soft mean longitude only — high eccentricity ignored.
    t = _julian_centuries(d)
    return _norm(238.9568 + 145.2078 * t)


_BODY_FN: dict[str, Callable[[date], float]] = {
    "Sun": tropical_sun_longitude,
    "Moon": tropical_moon_longitude,
    "Mercury": tropical_mercury_longitude,
    "Venus": tropical_venus_longitude,
    "Mars": tropical_mars_longitude,
    "Jupiter": tropical_jupiter_longitude,
    "Saturn": tropical_saturn_longitude,
    "Uranus": tropical_uranus_longitude,
    "Neptune": tropical_neptune_longitude,
    "Pluto": tropical_pluto_longitude,
}

# Sidereal-ish tropical return periods (days) for seeding the search window.
_PERIOD_DAYS: dict[str, float] = {
    "Sun": 365.2425,
    "Moon": 27.32166,
    "Mercury": 87.969,
    "Venus": 224.701,
    "Mars": 686.980,
    "Jupiter": 4332.589,
    "Saturn": 10759.22,
    "Uranus": 30687.15,
    "Neptune": 60190.03,
    "Pluto": 90560.0,
}


def classical_longitude(body: str, d: date) -> float:
    fn = _BODY_FN.get(body)
    if fn is None:
        raise KeyError(body)
    return float(fn(d))


def classical_bodies() -> tuple[str, ...]:
    return tuple(_BODY_FN.keys())


def outer_bodies() -> tuple[str, ...]:
    return ("Uranus", "Neptune", "Pluto")


def period_days(body: str) -> float:
    return float(_PERIOD_DAYS[body])


def ang_dist(a: float, b: float) -> float:
    d = (float(a) - float(b) + 180.0) % 360.0 - 180.0
    return abs(d)
