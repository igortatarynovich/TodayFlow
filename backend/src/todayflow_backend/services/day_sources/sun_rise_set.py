"""Approximate local sunrise / sunset (NOAA-style) for Day Sources.

v0: deterministic closed-form solar times — no Swiss Ephemeris dependency in backend.
Good enough for planetary hours; later can swap to swe.rise_trans via astro service.
"""

from __future__ import annotations

import math
from datetime import date, datetime, time, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def resolve_tz(timezone_name: str | None, lon: float | None = None) -> timezone | ZoneInfo:
    if timezone_name:
        try:
            return ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError:
            pass
    # Fallback: rough longitude-based fixed offset (15° ≈ 1h).
    if lon is not None:
        hours = max(-12, min(14, round(float(lon) / 15.0)))
        return timezone(timedelta(hours=hours))
    return timezone.utc


def _julian_day(d: date) -> float:
    # Julian day at 0h UTC for civil date (Gregorian).
    a = (14 - d.month) // 12
    y = d.year + 4800 - a
    m = d.month + 12 * a - 3
    return d.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def sun_rise_set_local(
    target_date: date,
    *,
    lat: float,
    lon: float,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    """Return sunrise/sunset as ISO local times + day length.

    Raises ValueError for polar day/night (no rise or set).
    """
    tz = resolve_tz(timezone_name, lon)
    # NOAA Solar Calculator (abridged).
    n = _julian_day(target_date) - 2451545.0 + 0.0008
    j_star = n - lon / 360.0
    m = (357.5291 + 0.98560028 * j_star) % 360.0
    m_rad = math.radians(m)
    c = 1.9148 * math.sin(m_rad) + 0.0200 * math.sin(2 * m_rad) + 0.0003 * math.sin(3 * m_rad)
    lambda_sun = (m + c + 180.0 + 102.9372) % 360.0
    lam_rad = math.radians(lambda_sun)
    j_transit = 2451545.0 + j_star + 0.0053 * math.sin(m_rad) - 0.0069 * math.sin(2 * lam_rad)
    delta = math.asin(math.sin(lam_rad) * math.sin(math.radians(23.4397)))
    lat_rad = math.radians(lat)
    cos_h = (math.sin(math.radians(-0.833)) - math.sin(lat_rad) * math.sin(delta)) / (
        math.cos(lat_rad) * math.cos(delta)
    )
    if cos_h < -1.0 or cos_h > 1.0:
        raise ValueError("no_sunrise_or_sunset_at_latitude")
    hour_angle = math.degrees(math.acos(cos_h))
    j_rise = j_transit - hour_angle / 360.0
    j_set = j_transit + hour_angle / 360.0

    def jd_to_utc(jd: float) -> datetime:
        # JD → Unix-ish: JD 2440587.5 = 1970-01-01 00:00 UTC
        seconds = (jd - 2440587.5) * 86400.0
        return datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds)

    rise_utc = jd_to_utc(j_rise)
    set_utc = jd_to_utc(j_set)
    rise_local = rise_utc.astimezone(tz)
    set_local = set_utc.astimezone(tz)
    # Keep clock times; pin to the requested civil date for planetary-hour construction.
    rise_local = datetime.combine(target_date, rise_local.time(), tzinfo=tz)
    set_local = datetime.combine(target_date, set_local.time(), tzinfo=tz)
    if set_local <= rise_local:
        set_local = set_local + timedelta(days=1)

    day_len = set_local - rise_local
    return {
        "sunrise_local": rise_local.isoformat(timespec="seconds"),
        "sunset_local": set_local.isoformat(timespec="seconds"),
        "day_length_minutes": int(round(day_len.total_seconds() / 60.0)),
        "latitude": lat,
        "longitude": lon,
        "timezone": getattr(tz, "key", str(tz)),
        "method": "noaa_approx_v0",
        "target_date": target_date.isoformat(),
    }


def parse_aware(iso: str) -> datetime:
    return datetime.fromisoformat(iso)
