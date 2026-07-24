"""Time lords soft layer — Firdaria majors/subs (canon §5.3 `time_lords`).

School freeze v0:
- Classical 76-year Firdaria (day vs night sequence).
- Sect: day if natal noon Sun is in whole-sign houses 7–12 from tropical ASC
  when time+place known; otherwise diurnal default with honest limitation.
- Sub-period: divide major by the 9-lord cycle starting at the major lord.
- ZR / other time-lord systems — later.
"""

from __future__ import annotations

from datetime import date, time, timedelta
from typing import Any

from todayflow_backend.services.day_sources.panchanga import tropical_sun_longitude
from todayflow_backend.services.day_sources.vedic_personal import compute_sidereal_lagna

_PLANET_RU = {
    "Sun": "Солнце",
    "Moon": "Луна",
    "Mercury": "Меркурий",
    "Venus": "Венера",
    "Mars": "Марс",
    "Jupiter": "Юпитер",
    "Saturn": "Сатурн",
    "NorthNode": "Сев. узел",
    "SouthNode": "Юж. узел",
}

# (planet_id, years) — classical Firdaria majors (sum = 76).
_DAY_MAJORS: tuple[tuple[str, int], ...] = (
    ("Sun", 10),
    ("Venus", 8),
    ("Mercury", 13),
    ("Moon", 9),
    ("Saturn", 11),
    ("Jupiter", 12),
    ("Mars", 7),
    ("NorthNode", 3),
    ("SouthNode", 3),
)

_NIGHT_MAJORS: tuple[tuple[str, int], ...] = (
    ("Moon", 9),
    ("Saturn", 11),
    ("Jupiter", 12),
    ("Mars", 7),
    ("NorthNode", 3),
    ("SouthNode", 3),
    ("Sun", 10),
    ("Venus", 8),
    ("Mercury", 13),
)

_DAYS_PER_YEAR = 365.2425


def _sign_index(lon: float) -> int:
    return int(float(lon) % 360.0 // 30.0) % 12


def _whole_sign_house(asc_sign: int, body_sign: int) -> int:
    return ((body_sign - asc_sign) % 12) + 1


def resolve_sect(
    birth_date: date,
    *,
    birth_time: time | None,
    birth_lat: float | None,
    birth_lon: float | None,
    timezone_name: str | None,
) -> dict[str, Any]:
    if birth_time is not None and birth_lat is not None and birth_lon is not None:
        asc = compute_sidereal_lagna(
            birth_date,
            birth_time,
            birth_lat=float(birth_lat),
            birth_lon=float(birth_lon),
            timezone_name=timezone_name,
        )
        asc_sign = _sign_index(float(asc["tropical_lon"]))
        sun_sign = _sign_index(tropical_sun_longitude(birth_date))
        house = _whole_sign_house(asc_sign, sun_sign)
        is_day = house >= 7
        return {
            "sect": "day" if is_day else "night",
            "method": "sun_vs_asc_whole_sign",
            "sun_whole_sign_house": house,
            "asc_sign_index": asc_sign,
        }
    return {
        "sect": "day",
        "method": "diurnal_default",
        "sun_whole_sign_house": None,
        "asc_sign_index": None,
    }


def _age_years(birth: date, on: date) -> float:
    return max(0.0, (on - birth).days / _DAYS_PER_YEAR)


def _add_years(d: date, years: float) -> date:
    return d + timedelta(days=years * _DAYS_PER_YEAR)


def _major_sequence(sect: str) -> tuple[tuple[str, int], ...]:
    return _DAY_MAJORS if sect == "day" else _NIGHT_MAJORS


def locate_firdaria(
    birth_date: date,
    target_date: date,
    *,
    sect: str,
) -> dict[str, Any]:
    age = _age_years(birth_date, target_date)
    majors = _major_sequence(sect)
    cycle_years = sum(y for _, y in majors)
    age_in_cycle = age % cycle_years

    cursor = 0.0
    major_idx = 0
    major_planet = majors[0][0]
    major_years = majors[0][1]
    major_start_age = 0.0
    for i, (planet, years) in enumerate(majors):
        end = cursor + years
        if age_in_cycle < end or i == len(majors) - 1:
            major_idx = i
            major_planet = planet
            major_years = years
            major_start_age = cursor
            break
        cursor = end

    # Absolute ages accounting for completed full cycles.
    cycles_done = int(age // cycle_years)
    abs_major_start = cycles_done * cycle_years + major_start_age
    abs_major_end = abs_major_start + major_years

    # Sub-periods: 9 lords starting at major lord, proportional shares.
    order = [p for p, _ in majors]
    start_i = order.index(major_planet)
    sub_order = order[start_i:] + order[:start_i]
    total_units = sum(dict(majors)[p] for p in sub_order)
    into_major = age_in_cycle - major_start_age
    sub_cursor = 0.0
    sub_planet = sub_order[0]
    sub_years = major_years * (dict(majors)[sub_order[0]] / total_units)
    sub_start_age = abs_major_start
    for p in sub_order:
        share = major_years * (dict(majors)[p] / total_units)
        end = sub_cursor + share
        if into_major < end or p == sub_order[-1]:
            sub_planet = p
            sub_years = share
            sub_start_age = abs_major_start + sub_cursor
            break
        sub_cursor = end

    major_start_date = _add_years(birth_date, abs_major_start)
    major_end_date = _add_years(birth_date, abs_major_end)
    sub_start_date = _add_years(birth_date, sub_start_age)
    sub_end_date = _add_years(birth_date, sub_start_age + sub_years)

    return {
        "age_years": round(age, 4),
        "cycle_years": cycle_years,
        "major": {
            "planet": major_planet,
            "planet_ru": _PLANET_RU[major_planet],
            "years": major_years,
            "index": major_idx,
            "start_age": round(abs_major_start, 4),
            "end_age": round(abs_major_end, 4),
            "start_date": major_start_date.isoformat(),
            "end_date": major_end_date.isoformat(),
        },
        "sub": {
            "planet": sub_planet,
            "planet_ru": _PLANET_RU[sub_planet],
            "years": round(sub_years, 4),
            "start_age": round(sub_start_age, 4),
            "end_age": round(sub_start_age + sub_years, 4),
            "start_date": sub_start_date.isoformat(),
            "end_date": sub_end_date.isoformat(),
        },
    }


def build_time_lords(
    birth_date: date,
    target_date: date,
    *,
    birth_time: time | None = None,
    birth_lat: float | None = None,
    birth_lon: float | None = None,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    sect_info = resolve_sect(
        birth_date,
        birth_time=birth_time,
        birth_lat=birth_lat,
        birth_lon=birth_lon,
        timezone_name=timezone_name,
    )
    fir = locate_firdaria(birth_date, target_date, sect=str(sect_info["sect"]))
    depth = (
        "firdaria_sect_known"
        if sect_info["method"] == "sun_vs_asc_whole_sign"
        else "firdaria_diurnal_default"
    )

    major = fir["major"]
    sub = fir["sub"]
    summary = (
        f"Firdaria: мажор {_PLANET_RU[major['planet']]} "
        f"({major['start_date']} → {major['end_date']}), "
        f"субпериод {_PLANET_RU[sub['planet']]} "
        f"(до {sub['end_date']})."
    )
    if sect_info["method"] == "diurnal_default":
        summary += " Секта: дневная по умолчанию (нет времени/места)."

    beat = {
        "id": f"time-lords-firdaria-{major['planet'].lower()}",
        "kind": "time_lords",
        "title": f"Firdaria · {major['planet_ru']} / {sub['planet_ru']}",
        "story_ru": summary,
        "evidence_ref": "personal_astrology.time_lords",
    }

    return {
        "capability_id": "time_lords",
        "school_canon": "firdaria_classical_v0",
        "depth": depth,
        "sect": sect_info,
        "firdaria": fir,
        "systems_available": ["firdaria"],
        "systems_deferred": ["zodiacal_releasing", "profection_lords_as_time_lord"],
        "limitation_ru": (
            "Только классическая Firdaria. Zodiacal Releasing и др. — later. "
            "Секта без времени/места = дневная default."
        ),
        "beats": [beat],
        "summary_ru": summary[:420],
    }
