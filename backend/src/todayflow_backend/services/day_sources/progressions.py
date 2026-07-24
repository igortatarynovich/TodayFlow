"""Secondary progressions + solar arc soft layer (canon §5.3).

School freeze:
- Secondary: 1 day after birth = 1 year of life (Naibod/day-for-year).
- Bodies v0: Sun + Moon via closed-form tropical longitudes (noon civil dates).
- Solar arc: natal Moon (and soft ASC if known) advanced by progressed-Sun arc.
- Progressed angles require birth time+place; without them angles stay unavailable.
"""

from __future__ import annotations

from datetime import date, timedelta, time
from typing import Any

from todayflow_backend.services.day_sources.panchanga import (
    tropical_moon_longitude,
    tropical_sun_longitude,
)
from todayflow_backend.services.day_sources.vedic_personal import compute_sidereal_lagna

_DAYS_PER_YEAR = 365.2425

_SIGN_RU = [
    "Овен",
    "Телец",
    "Близнецы",
    "Рак",
    "Лев",
    "Дева",
    "Весы",
    "Скорпион",
    "Стрелец",
    "Козерог",
    "Водолей",
    "Рыбы",
]


def _sign_index(lon: float) -> int:
    return int(float(lon) % 360.0 // 30.0) % 12


def _body(lon: float, *, name: str) -> dict[str, Any]:
    si = _sign_index(lon)
    return {
        "name": name,
        "longitude": round(float(lon) % 360.0, 4),
        "sign_index": si,
        "sign_ru": _SIGN_RU[si],
        "degree_in_sign": round(float(lon) % 30.0, 4),
    }


def age_years_exact(birth: date, on: date) -> float:
    return max(0.0, (on - birth).days / _DAYS_PER_YEAR)


def progressed_calendar_date(birth: date, on: date) -> date:
    """Civil date whose noon sky approximates the secondary progressed chart."""
    days = age_years_exact(birth, on)
    return birth + timedelta(days=days)


def build_secondary_progressions(
    birth_date: date,
    target_date: date,
    *,
    birth_time: time | None = None,
    birth_lat: float | None = None,
    birth_lon: float | None = None,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    age = age_years_exact(birth_date, target_date)
    prog_date = progressed_calendar_date(birth_date, target_date)

    natal_sun = _body(tropical_sun_longitude(birth_date), name="Sun")
    natal_moon = _body(tropical_moon_longitude(birth_date), name="Moon")
    prog_sun = _body(tropical_sun_longitude(prog_date), name="Sun")
    prog_moon = _body(tropical_moon_longitude(prog_date), name="Moon")

    sun_changed_sign = natal_sun["sign_index"] != prog_sun["sign_index"]
    moon_changed_sign = natal_moon["sign_index"] != prog_moon["sign_index"]

    progressed_asc = None
    depth = "sun_moon_noon"
    if birth_time is not None and birth_lat is not None and birth_lon is not None:
        # Progressed ASC ≈ ASC for birth clock on progressed calendar day (soft).
        asc = compute_sidereal_lagna(
            prog_date,
            birth_time,
            birth_lat=float(birth_lat),
            birth_lon=float(birth_lon),
            timezone_name=timezone_name,
        )
        progressed_asc = _body(float(asc["tropical_lon"]), name="ASC")
        depth = "sun_moon_asc_soft"

    summary = (
        f"Секундарные прогрессии (день=год): прогресс. Солнце "
        f"{prog_sun['sign_ru']} {prog_sun['degree_in_sign']:.1f}°, "
        f"Луна {prog_moon['sign_ru']} {prog_moon['degree_in_sign']:.1f}° "
        f"(возраст {age:.2f} лет → дата {prog_date.isoformat()})."
    )
    if sun_changed_sign:
        summary += f" Солнце сменило знак с {natal_sun['sign_ru']}."
    if moon_changed_sign:
        summary += f" Луна сменила знак с {natal_moon['sign_ru']}."

    beat = {
        "id": "progressions-secondary-sun-moon",
        "kind": "secondary_progression",
        "title": f"Прогресс. Солнце · {prog_sun['sign_ru']}",
        "story_ru": summary,
        "evidence_ref": "personal_astrology.secondary_progressions",
    }

    return {
        "capability_id": "secondary_progressions",
        "school_canon": "day_for_year_sun_moon_v0",
        "depth": depth,
        "age_years": round(age, 4),
        "progressed_date": prog_date.isoformat(),
        "natal": {"sun": natal_sun, "moon": natal_moon},
        "progressed": {
            "sun": prog_sun,
            "moon": prog_moon,
            "ascendant": progressed_asc,
        },
        "sun_changed_sign": sun_changed_sign,
        "moon_changed_sign": moon_changed_sign,
        "beats": [beat],
        "summary_ru": summary[:400],
    }


def build_solar_arc(
    birth_date: date,
    target_date: date,
    *,
    birth_time: time | None = None,
    birth_lat: float | None = None,
    birth_lon: float | None = None,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    age = age_years_exact(birth_date, target_date)
    prog_date = progressed_calendar_date(birth_date, target_date)

    natal_sun_lon = tropical_sun_longitude(birth_date)
    prog_sun_lon = tropical_sun_longitude(prog_date)
    arc = (prog_sun_lon - natal_sun_lon) % 360.0

    natal_moon_lon = tropical_moon_longitude(birth_date)
    sa_moon = _body((natal_moon_lon + arc) % 360.0, name="Moon")
    sa_sun = _body(prog_sun_lon, name="Sun")  # SA Sun == progressed Sun

    sa_asc = None
    depth = "sun_moon"
    if birth_time is not None and birth_lat is not None and birth_lon is not None:
        natal_asc = compute_sidereal_lagna(
            birth_date,
            birth_time,
            birth_lat=float(birth_lat),
            birth_lon=float(birth_lon),
            timezone_name=timezone_name,
        )
        sa_asc = _body((float(natal_asc["tropical_lon"]) + arc) % 360.0, name="ASC")
        depth = "sun_moon_asc"

    summary = (
        f"Solar arc: дуга {arc:.2f}° (прогресс. Солнце). "
        f"SA Луна в {sa_moon['sign_ru']} {sa_moon['degree_in_sign']:.1f}°."
    )
    if sa_asc:
        summary += f" SA ASC — {sa_asc['sign_ru']}."

    beat = {
        "id": "progressions-solar-arc",
        "kind": "solar_arc",
        "title": f"Solar arc · {arc:.1f}°",
        "story_ru": summary,
        "evidence_ref": "personal_astrology.solar_arc",
    }

    return {
        "capability_id": "solar_arc",
        "school_canon": "solar_arc_equals_progressed_sun_arc_v0",
        "depth": depth,
        "age_years": round(age, 4),
        "arc_degrees": round(arc, 4),
        "progressed_date": prog_date.isoformat(),
        "bodies": {"sun": sa_sun, "moon": sa_moon, "ascendant": sa_asc},
        "beats": [beat],
        "summary_ru": summary[:400],
    }


def build_progressions_pack(
    birth_date: date,
    target_date: date,
    *,
    birth_time: time | None = None,
    birth_lat: float | None = None,
    birth_lon: float | None = None,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    secondary = build_secondary_progressions(
        birth_date,
        target_date,
        birth_time=birth_time,
        birth_lat=birth_lat,
        birth_lon=birth_lon,
        timezone_name=timezone_name,
    )
    solar_arc = build_solar_arc(
        birth_date,
        target_date,
        birth_time=birth_time,
        birth_lat=birth_lat,
        birth_lon=birth_lon,
        timezone_name=timezone_name,
    )
    return {
        "secondary_progressions": secondary,
        "solar_arc": solar_arc,
        "capability_ids": ["secondary_progressions", "solar_arc"],
        "beats": list(secondary.get("beats") or [])[:1] + list(solar_arc.get("beats") or [])[:1],
        "summary_ru": f"{secondary['summary_ru']} {solar_arc['summary_ru']}"[:420],
    }
