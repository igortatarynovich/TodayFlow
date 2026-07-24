"""Time lords soft layer — Firdaria + Zodiacal Releasing (canon §5.3).

School freeze v0:
- Classical 76-year Firdaria (day vs night sequence).
- Sect: day if natal noon Sun is in whole-sign houses 7–12 from tropical ASC
  when time+place known; otherwise diurnal default with honest limitation.
- Sub-period: divide major by the 9-lord cycle starting at the major lord.
- ZR: release from Lot of Fortune (Hellenistic day/night formula) using
  Egyptian lesser years; L1 major + soft L2. Without ASC → Moon-sign proxy.
"""

from __future__ import annotations

from datetime import date, time, timedelta
from typing import Any

from todayflow_backend.services.day_sources.panchanga import (
    tropical_moon_longitude,
    tropical_sun_longitude,
)
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

# Domicile lord + Egyptian lesser years for ZR sign periods.
_ZR_SIGN: list[tuple[str, str, int]] = [
    ("Mars", "Марс", 15),  # Aries
    ("Venus", "Венера", 8),  # Taurus
    ("Mercury", "Меркурий", 20),  # Gemini
    ("Moon", "Луна", 25),  # Cancer
    ("Sun", "Солнце", 19),  # Leo
    ("Mercury", "Меркурий", 20),  # Virgo
    ("Venus", "Венера", 8),  # Libra
    ("Mars", "Марс", 15),  # Scorpio
    ("Jupiter", "Юпитер", 12),  # Sagittarius
    ("Saturn", "Сатурн", 30),  # Capricorn
    ("Saturn", "Сатурн", 30),  # Aquarius
    ("Jupiter", "Юпитер", 12),  # Pisces
]

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


def _add_years(d: date, years: float) -> date:
    return d + timedelta(days=years * _DAYS_PER_YEAR)


def _age_years(birth: date, on: date) -> float:
    return max(0.0, (on - birth).days / _DAYS_PER_YEAR)


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
            "ascendant_tropical_lon": float(asc["tropical_lon"]),
        }
    return {
        "sect": "day",
        "method": "diurnal_default",
        "sun_whole_sign_house": None,
        "asc_sign_index": None,
        "ascendant_tropical_lon": None,
    }


def resolve_lot_of_fortune(
    birth_date: date,
    *,
    sect: str,
    asc_lon: float | None,
) -> dict[str, Any]:
    sun = tropical_sun_longitude(birth_date)
    moon = tropical_moon_longitude(birth_date)
    if asc_lon is None:
        # Soft proxy: release from natal Moon sign when ASC unknown.
        sign_i = _sign_index(moon)
        return {
            "lot": "fortune",
            "longitude": round(moon, 4),
            "sign_index": sign_i,
            "sign_ru": _SIGN_RU[sign_i],
            "method": "moon_sign_proxy",
            "sect": sect,
        }
    if sect == "day":
        lon = (float(asc_lon) + moon - sun) % 360.0
        method = "fortune_day_asc_moon_sun"
    else:
        lon = (float(asc_lon) + sun - moon) % 360.0
        method = "fortune_night_asc_sun_moon"
    sign_i = _sign_index(lon)
    return {
        "lot": "fortune",
        "longitude": round(lon, 4),
        "sign_index": sign_i,
        "sign_ru": _SIGN_RU[sign_i],
        "method": method,
        "sect": sect,
    }


def resolve_lot_of_spirit(
    birth_date: date,
    *,
    sect: str,
    asc_lon: float | None,
) -> dict[str, Any]:
    """Lot of Spirit — inverse of Fortune (Hellenistic)."""
    sun = tropical_sun_longitude(birth_date)
    moon = tropical_moon_longitude(birth_date)
    if asc_lon is None:
        # Soft proxy: release from natal Sun sign when ASC unknown.
        sign_i = _sign_index(sun)
        return {
            "lot": "spirit",
            "longitude": round(sun, 4),
            "sign_index": sign_i,
            "sign_ru": _SIGN_RU[sign_i],
            "method": "sun_sign_proxy",
            "sect": sect,
        }
    if sect == "day":
        lon = (float(asc_lon) + sun - moon) % 360.0
        method = "spirit_day_asc_sun_moon"
    else:
        lon = (float(asc_lon) + moon - sun) % 360.0
        method = "spirit_night_asc_moon_sun"
    sign_i = _sign_index(lon)
    return {
        "lot": "spirit",
        "longitude": round(lon, 4),
        "sign_index": sign_i,
        "sign_ru": _SIGN_RU[sign_i],
        "method": method,
        "sect": sect,
    }


def _zr_period_at_age(start_sign: int, age: float) -> dict[str, Any]:
    """Locate L1 major ZR period for `age` years from birth."""
    cursor = 0.0
    sign = start_sign
    # Safety: up to ~3 full zodiac cycles of lesser years (~sum 214 per cycle).
    for _ in range(40):
        lord, lord_ru, years = _ZR_SIGN[sign]
        end = cursor + years
        if age < end or abs(age - end) < 1e-9:
            return {
                "sign_index": sign,
                "sign_ru": _SIGN_RU[sign],
                "lord": lord,
                "lord_ru": lord_ru,
                "years": years,
                "start_age": round(cursor, 4),
                "end_age": round(end, 4),
            }
        cursor = end
        sign = (sign + 1) % 12
    lord, lord_ru, years = _ZR_SIGN[start_sign]
    return {
        "sign_index": start_sign,
        "sign_ru": _SIGN_RU[start_sign],
        "lord": lord,
        "lord_ru": lord_ru,
        "years": years,
        "start_age": 0.0,
        "end_age": float(years),
    }


def _zr_l2(major: dict[str, Any], age: float) -> dict[str, Any]:
    """Soft L2: re-release from major sign; periods proportional to lesser years."""
    major_years = float(major["years"])
    start_sign = int(major["sign_index"])
    total_units = sum(y for _l, _r, y in _ZR_SIGN)
    into = max(0.0, age - float(major["start_age"]))
    cursor = 0.0
    sign = start_sign
    for step in range(12):
        _lord, _ru, units = _ZR_SIGN[sign]
        share = major_years * (units / total_units)
        end = cursor + share
        if into < end or step == 11:
            lord, lord_ru, _u = _ZR_SIGN[sign]
            return {
                "sign_index": sign,
                "sign_ru": _SIGN_RU[sign],
                "lord": lord,
                "lord_ru": lord_ru,
                "years": round(share, 4),
                "start_age": round(float(major["start_age"]) + cursor, 4),
                "end_age": round(float(major["start_age"]) + end, 4),
            }
        cursor = end
        sign = (sign + 1) % 12
    lord, lord_ru, units = _ZR_SIGN[start_sign]
    share = major_years * (units / total_units)
    return {
        "sign_index": start_sign,
        "sign_ru": _SIGN_RU[start_sign],
        "lord": lord,
        "lord_ru": lord_ru,
        "years": round(share, 4),
        "start_age": float(major["start_age"]),
        "end_age": float(major["start_age"]) + share,
    }


def locate_zodiacal_releasing(
    birth_date: date,
    target_date: date,
    *,
    lot: dict[str, Any],
) -> dict[str, Any]:
    age = _age_years(birth_date, target_date)
    start_sign = int(lot["sign_index"])
    major = _zr_period_at_age(start_sign, age)
    l2 = _zr_l2(major, age)
    # Soft peak: L1 sign is opposite the lot's start (classic "loosing of the bond" cue).
    opposite = (start_sign + 6) % 12
    peakish = int(major["sign_index"]) == opposite
    return {
        "age_years": round(age, 4),
        "lot": lot,
        "level1": {
            **major,
            "start_date": _add_years(birth_date, float(major["start_age"])).isoformat(),
            "end_date": _add_years(birth_date, float(major["end_age"])).isoformat(),
        },
        "level2": {
            **l2,
            "start_date": _add_years(birth_date, float(l2["start_age"])).isoformat(),
            "end_date": _add_years(birth_date, float(l2["end_age"])).isoformat(),
        },
        "peak_soft": {
            "active": peakish,
            "note_ru": (
                "L1 на противоположном знаке от лота (soft peak / loosing cue)."
                if peakish
                else None
            ),
        },
    }


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

    cycles_done = int(age // cycle_years)
    abs_major_start = cycles_done * cycle_years + major_start_age
    abs_major_end = abs_major_start + major_years

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
            "start_date": _add_years(birth_date, abs_major_start).isoformat(),
            "end_date": _add_years(birth_date, abs_major_end).isoformat(),
        },
        "sub": {
            "planet": sub_planet,
            "planet_ru": _PLANET_RU[sub_planet],
            "years": round(sub_years, 4),
            "start_age": round(sub_start_age, 4),
            "end_age": round(sub_start_age + sub_years, 4),
            "start_date": _add_years(birth_date, sub_start_age).isoformat(),
            "end_date": _add_years(birth_date, sub_start_age + sub_years).isoformat(),
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

    asc_lon = sect_info.get("ascendant_tropical_lon")
    fortune = resolve_lot_of_fortune(
        birth_date,
        sect=str(sect_info["sect"]),
        asc_lon=asc_lon,
    )
    spirit = resolve_lot_of_spirit(
        birth_date,
        sect=str(sect_info["sect"]),
        asc_lon=asc_lon,
    )
    zr_fortune = locate_zodiacal_releasing(birth_date, target_date, lot=fortune)
    zr_spirit = locate_zodiacal_releasing(birth_date, target_date, lot=spirit)

    if sect_info["method"] == "sun_vs_asc_whole_sign" and fortune["method"] != "moon_sign_proxy":
        depth = "firdaria_zr_fortune_spirit_sect"
    elif sect_info["method"] == "sun_vs_asc_whole_sign":
        depth = "firdaria_sect_known"
    else:
        depth = "firdaria_zr_fortune_spirit_proxy"

    major = fir["major"]
    sub = fir["sub"]
    l1 = zr_fortune["level1"]
    l2 = zr_fortune["level2"]
    s1 = zr_spirit["level1"]
    s2 = zr_spirit["level2"]

    summary = (
        f"Firdaria: мажор {_PLANET_RU[major['planet']]} "
        f"({major['start_date']} → {major['end_date']}), "
        f"субпериод {_PLANET_RU[sub['planet']]} "
        f"(до {sub['end_date']}). "
        f"ZR Fortune→{fortune['sign_ru']}: L1 {l1['sign_ru']}/{l1['lord_ru']}, "
        f"L2 {l2['sign_ru']}. "
        f"ZR Spirit→{spirit['sign_ru']}: L1 {s1['sign_ru']}/{s1['lord_ru']}, "
        f"L2 {s2['sign_ru']}."
    )
    if fortune["method"] == "moon_sign_proxy":
        summary += " Лоты soft: Луна/Солнце (нет ASC)."
    elif sect_info["method"] == "diurnal_default":
        summary += " Секта: дневная по умолчанию."
    if zr_fortune.get("peak_soft", {}).get("active"):
        summary += " Fortune L1 — soft peak (opposite)."
    if zr_spirit.get("peak_soft", {}).get("active"):
        summary += " Spirit L1 — soft peak (opposite)."

    beat = {
        "id": f"time-lords-firdaria-zr-{major['planet'].lower()}",
        "kind": "time_lords",
        "title": (
            f"Time lords · Firdaria {major['planet_ru']} · "
            f"ZR F {l1['sign_ru']}/S {s1['sign_ru']}"
        ),
        "story_ru": summary,
        "evidence_ref": "personal_astrology.time_lords",
    }

    return {
        "capability_id": "time_lords",
        "school_canon": "firdaria_zr_fortune_spirit_v0",
        "depth": depth,
        "sect": sect_info,
        "firdaria": fir,
        "zodiacal_releasing": zr_fortune,
        "zodiacal_releasing_spirit": zr_spirit,
        "systems_available": [
            "firdaria",
            "zodiacal_releasing",
            "zodiacal_releasing_spirit",
        ],
        "systems_deferred": ["profection_lords_as_time_lord", "swiss_timed_lots"],
        "limitation_ru": (
            "Firdaria + ZR from Fortune and Spirit (Egyptian lesser years, L1/L2 soft). "
            "Without ASC: Fortune←Moon, Spirit←Sun. Swiss-timed lots — later."
        ),
        "beats": [beat],
        "summary_ru": summary[:480],
    }
