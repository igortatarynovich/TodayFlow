"""Resolve IANA timezone for birth place — never invent civil-as-UT natal geometry.

Prefer explicit profile timezone_name / offset. Else match curated city (name or nearest
coords). Fail closed: return None when unresolved so callers refuse precise natal.
"""

from __future__ import annotations

import math
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# IANA by English city name (keys match Geocoder CITY_DATA "name").
_CITY_IANA: dict[str, str] = {
    "New York": "America/New_York",
    "Los Angeles": "America/Los_Angeles",
    "Chicago": "America/Chicago",
    "Miami": "America/New_York",
    "Toronto": "America/Toronto",
    "Vancouver": "America/Vancouver",
    "Mexico City": "America/Mexico_City",
    "São Paulo": "America/Sao_Paulo",
    "Buenos Aires": "America/Argentina/Buenos_Aires",
    "London": "Europe/London",
    "Paris": "Europe/Paris",
    "Berlin": "Europe/Berlin",
    "Moscow": "Europe/Moscow",
    "Saint Petersburg": "Europe/Moscow",
    "Minsk": "Europe/Minsk",
    "Kyiv": "Europe/Kyiv",
    "Riga": "Europe/Riga",
    "Vilnius": "Europe/Vilnius",
    "Tallinn": "Europe/Tallinn",
    "Tbilisi": "Asia/Tbilisi",
    "Yerevan": "Asia/Yerevan",
    "Astana": "Asia/Almaty",
    "Almaty": "Asia/Almaty",
    "Madrid": "Europe/Madrid",
    "Barcelona": "Europe/Madrid",
    "Rome": "Europe/Rome",
    "Amsterdam": "Europe/Amsterdam",
    "Stockholm": "Europe/Stockholm",
    "Oslo": "Europe/Oslo",
    "Copenhagen": "Europe/Copenhagen",
    "Helsinki": "Europe/Helsinki",
    "Warsaw": "Europe/Warsaw",
    "Prague": "Europe/Prague",
    "Vienna": "Europe/Vienna",
    "Zurich": "Europe/Zurich",
    "Lisbon": "Europe/Lisbon",
    "Istanbul": "Europe/Istanbul",
    "Athens": "Europe/Athens",
    "Dubai": "Asia/Dubai",
    "Tel Aviv": "Asia/Jerusalem",
    "Johannesburg": "Africa/Johannesburg",
    "Nairobi": "Africa/Nairobi",
    "Lagos": "Africa/Lagos",
    "Cairo": "Africa/Cairo",
    "Mumbai": "Asia/Kolkata",
    "Delhi": "Asia/Kolkata",
    "Bengaluru": "Asia/Kolkata",
    "Bangkok": "Asia/Bangkok",
    "Singapore": "Asia/Singapore",
    "Hong Kong": "Asia/Hong_Kong",
    "Shanghai": "Asia/Shanghai",
    "Beijing": "Asia/Shanghai",
    "Seoul": "Asia/Seoul",
    "Tokyo": "Asia/Tokyo",
    "Kyoto": "Asia/Tokyo",
    "Sydney": "Australia/Sydney",
    "Melbourne": "Australia/Melbourne",
    "Brisbane": "Australia/Brisbane",
    "Auckland": "Pacific/Auckland",
    "Wellington": "Pacific/Auckland",
    "Novosibirsk": "Asia/Novosibirsk",
    "Yekaterinburg": "Asia/Yekaterinburg",
    "Kazan": "Europe/Moscow",
    "Nizhny Novgorod": "Europe/Moscow",
    "Chelyabinsk": "Asia/Yekaterinburg",
    "Samara": "Europe/Samara",
    "Omsk": "Asia/Omsk",
    "Rostov-on-Don": "Europe/Moscow",
    "Ufa": "Asia/Yekaterinburg",
    "Krasnoyarsk": "Asia/Krasnoyarsk",
    "Voronezh": "Europe/Moscow",
    "Perm": "Asia/Yekaterinburg",
    "Volgograd": "Europe/Volgograd",
    "Krasnodar": "Europe/Moscow",
    "Saratov": "Europe/Saratov",
    "Tyumen": "Asia/Yekaterinburg",
    "Tolyatti": "Europe/Samara",
    "Izhevsk": "Europe/Samara",
    "Barnaul": "Asia/Barnaul",
    "Irkutsk": "Asia/Irkutsk",
    "Khabarovsk": "Asia/Vladivostok",
    "Vladivostok": "Asia/Vladivostok",
    "Yaroslavl": "Europe/Moscow",
    "Tomsk": "Asia/Tomsk",
    "Kemerovo": "Asia/Novokuznetsk",
    "Orenburg": "Asia/Yekaterinburg",
    "Novokuznetsk": "Asia/Novokuznetsk",
    "Ryazan": "Europe/Moscow",
    "Astrakhan": "Europe/Astrakhan",
    "Penza": "Europe/Moscow",
    "Lipetsk": "Europe/Moscow",
    "Kirov": "Europe/Kirov",
    "Cheboksary": "Europe/Moscow",
    "Kaliningrad": "Europe/Kaliningrad",
    "Tula": "Europe/Moscow",
    "Kursk": "Europe/Moscow",
    "Stavropol": "Europe/Moscow",
    "Ulyanovsk": "Europe/Ulyanovsk",
    "Ivanovo": "Europe/Moscow",
    "Bryansk": "Europe/Moscow",
    "Sochi": "Europe/Moscow",
    "Sevastopol": "Europe/Simferopol",
    "Simferopol": "Europe/Simferopol",
    "Kharkiv": "Europe/Kyiv",
    "Odessa": "Europe/Kyiv",
    "Dnipro": "Europe/Kyiv",
    "Lviv": "Europe/Kyiv",
    "Gomel": "Europe/Minsk",
    "Brest": "Europe/Minsk",
}

# Max distance (km) for nearest-city TZ inference from coordinates.
_NEAREST_KM = 120.0


def _valid_iana(name: str | None) -> str | None:
    raw = (name or "").strip()
    if not raw:
        return None
    try:
        return ZoneInfo(raw).key
    except ZoneInfoNotFoundError:
        # Legacy alias
        if raw == "Europe/Kiev":
            try:
                return ZoneInfo("Europe/Kyiv").key
            except ZoneInfoNotFoundError:
                return None
        return None


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


def timezone_for_city_name(city_name: str | None) -> str | None:
    if not city_name:
        return None
    return _valid_iana(_CITY_IANA.get(city_name))


def timezone_nearest_city(lat: float, lon: float) -> str | None:
    from todayflow_backend.services.geocode import CITY_DATA

    best_tz: str | None = None
    best_d = _NEAREST_KM
    for row in CITY_DATA:
        name = str(row.get("name") or "")
        tz = _CITY_IANA.get(name)
        if not tz:
            continue
        try:
            d = _haversine_km(lat, lon, float(row["latitude"]), float(row["longitude"]))
        except (TypeError, ValueError, KeyError):
            continue
        if d <= best_d:
            best_d = d
            best_tz = tz
    return _valid_iana(best_tz)


def resolve_birth_timezone(
    *,
    timezone_name: str | None = None,
    timezone_offset_minutes: int | None = None,
    location_name: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
) -> dict[str, Any]:
    """Return {timezone_name, source, need_tz}.

    need_tz=True means precise natal must not be computed until TZ is known.
    Offset alone is enough for Swiss (need_tz=False, timezone_name may stay null).
    """
    explicit = _valid_iana(timezone_name)
    if explicit:
        return {"timezone_name": explicit, "source": "explicit", "need_tz": False}

    if timezone_offset_minutes is not None:
        try:
            int(timezone_offset_minutes)
            return {
                "timezone_name": None,
                "source": "offset_minutes",
                "need_tz": False,
                "timezone_offset_minutes": int(timezone_offset_minutes),
            }
        except (TypeError, ValueError):
            pass

    # Name → curated city
    try:
        from todayflow_backend.services.geocode import Geocoder

        hit = Geocoder().lookup(location_name)
    except Exception:
        hit = None
    if hit:
        by_name = timezone_for_city_name(str(hit.get("name") or ""))
        if by_name:
            return {"timezone_name": by_name, "source": "geocode_city", "need_tz": False}

    if latitude is not None and longitude is not None:
        nearest = timezone_nearest_city(float(latitude), float(longitude))
        if nearest:
            return {"timezone_name": nearest, "source": "nearest_city", "need_tz": False}

    return {"timezone_name": None, "source": None, "need_tz": True}


def profile_needs_timezone(
    *,
    time_unknown: bool,
    birth_time: Any,
    timezone_name: str | None,
    timezone_offset_minutes: int | None,
) -> bool:
    """True when birth time is known but neither IANA nor offset is usable."""
    if time_unknown or not birth_time:
        return False
    if _valid_iana(timezone_name):
        return False
    if timezone_offset_minutes is not None:
        try:
            int(timezone_offset_minutes)
            return False
        except (TypeError, ValueError):
            pass
    return True
