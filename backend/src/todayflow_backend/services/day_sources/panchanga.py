"""Vedic Panchanga v0 — Lahiri sidereal day factors (canon §5.6).

Deterministic closed-form Sun/Moon + Lahiri ayanamsha. No Swiss dependency in backend.
Gochara/dasha stay Personal later.
"""

from __future__ import annotations

import math
from datetime import date, datetime
from typing import Any

from todayflow_backend.services.day_sources.sun_rise_set import sun_rise_set_local

AYANAMSHA_ID = "lahiri_v0"

_TITHI_NAMES_RU = [
    "Пратипат",
    "Двития",
    "Трития",
    "Чатуртхи",
    "Панчами",
    "Шашти",
    "Саптами",
    "Аштами",
    "Навами",
    "Дашами",
    "Экадаши",
    "Двадаши",
    "Трайодаши",
    "Чатурдаши",
    "Пурнима",  # 15 waxing; 30 = Amavasya handled separately
]

_NAKSHATRA_RU = [
    "Ашвини",
    "Бхарани",
    "Криттика",
    "Рохини",
    "Мригашира",
    "Ардра",
    "Пунарвасу",
    "Пушья",
    "Ашлеша",
    "Магха",
    "Пурва-Пхалгуни",
    "Уттара-Пхалгуни",
    "Хаста",
    "Читра",
    "Свати",
    "Вишакха",
    "Анурадха",
    "Джьештха",
    "Мула",
    "Пурва-Ашадха",
    "Уттара-Ашадха",
    "Шравана",
    "Дхаништха",
    "Шатабхиша",
    "Пурва-Бхадрапада",
    "Уттара-Бхадрапада",
    "Ревати",
]

_YOGA_RU = [
    "Вишкумбха",
    "Прити",
    "Аюшман",
    "Саубхагья",
    "Шобхана",
    "Атиганда",
    "Сукарма",
    "Дхрити",
    "Шула",
    "Ганда",
    "Вриддхи",
    "Дхрува",
    "Вьягхата",
    "Харшана",
    "Ваджра",
    "Сиддхи",
    "Вьятипата",
    "Вариян",
    "Паригха",
    "Шива",
    "Сиддха",
    "Садхья",
    "Шубха",
    "Шукла",
    "Брахма",
    "Индра",
    "Вайдхрити",
]

# 11 karanas cycling; 1st of Shukla Pratipada is Kimstughna, then Bava…, last of Amavasya Naga.
_KARANA_RU = [
    "Бава",
    "Балава",
    "Каулава",
    "Тайтила",
    "Гара",
    "Ваниджа",
    "Вишти",
    "Шакуни",
    "Чатuspада",
    "Нага",
    "Кимстугхна",
]

_VARA = [
    ("monday", "Moon", "Луна", "Сомавара"),
    ("tuesday", "Mars", "Марс", "Мангалавара"),
    ("wednesday", "Mercury", "Меркурий", "Будхавара"),
    ("thursday", "Jupiter", "Юпитер", "Гурувара"),
    ("friday", "Venus", "Венера", "Шукравара"),
    ("saturday", "Saturn", "Сатурн", "Шанивара"),
    ("sunday", "Sun", "Солнце", "Равивара"),
]

# Rahu Kala day segments (1..8 of daylight), Yamaganda, Gulika — classical weekday tables.
_RAHU_SEGMENT = {0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3, 6: 8}  # Mon..Sun → 1-based eighth
_YAMAGANDA_SEGMENT = {0: 4, 1: 3, 2: 2, 3: 1, 4: 7, 5: 6, 6: 5}
_GULIKA_SEGMENT = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 7}


def _julian_centuries(d: date) -> float:
    # J2000.0 = 2451545.0; approx JD at 12h UT.
    a = (14 - d.month) // 12
    y = d.year + 4800 - a
    m = d.month + 12 * a - 3
    jd = d.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    jd += 0.5  # noon
    return (jd - 2451545.0) / 36525.0


def tropical_sun_longitude(d: date) -> float:
    """Approx geometric mean longitude of the Sun (degrees), Meeus-style."""
    t = _julian_centuries(d)
    l0 = (280.46646 + 36000.76983 * t + 0.0003032 * t * t) % 360.0
    m = (357.52911 + 35999.05029 * t - 0.0001537 * t * t) % 360.0
    m_rad = math.radians(m)
    c = (
        (1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(m_rad)
        + (0.019993 - 0.000101 * t) * math.sin(2 * m_rad)
        + 0.000289 * math.sin(3 * m_rad)
    )
    return (l0 + c) % 360.0


def tropical_moon_longitude(d: date) -> float:
    """Low-precision Moon ecliptic longitude (degrees) for daily Panchanga."""
    t = _julian_centuries(d)
    l_prime = (
        218.3164477
        + 481267.88123421 * t
        - 0.0015786 * t * t
        + t * t * t / 538841.0
        - t**4 / 65194000.0
    ) % 360.0
    d_el = (
        297.8501921
        + 445267.1114034 * t
        - 0.0018819 * t * t
        + t * t * t / 545868.0
        - t**4 / 113065000.0
    ) % 360.0
    m = (357.5291092 + 35999.0502909 * t - 0.0001536 * t * t + t * t * t / 24490000.0) % 360.0
    m_prime = (
        134.9633964
        + 477198.8675055 * t
        + 0.0087414 * t * t
        + t * t * t / 69699.0
        - t**4 / 14712000.0
    ) % 360.0
    f = (
        93.2720950
        + 483202.0175233 * t
        - 0.0036539 * t * t
        - t * t * t / 3526000.0
        + t**4 / 863310000.0
    ) % 360.0

    def r(x: float) -> float:
        return math.radians(x)

    lon = (
        l_prime
        + 6.289 * math.sin(r(m_prime))
        + 1.274 * math.sin(r(2 * d_el - m_prime))
        + 0.658 * math.sin(r(2 * d_el))
        + 0.214 * math.sin(r(2 * m_prime))
        - 0.186 * math.sin(r(m))
        - 0.114 * math.sin(r(2 * f))
    )
    return lon % 360.0


def lahiri_ayanamsha(d: date) -> float:
    """Lahiri (Chitrapaksha) approx: ~23.85° at J2000 + precession."""
    t = _julian_centuries(d)
    # Canonical-ish linear Lahiri used in many panchanga engines.
    return (23.85407474 + 1.397666906 * t) % 360.0


def to_sidereal(tropical_lon: float, ayanamsha: float) -> float:
    return (tropical_lon - ayanamsha) % 360.0


def compute_panchanga_core(d: date) -> dict[str, Any]:
    aya = lahiri_ayanamsha(d)
    sun_t = tropical_sun_longitude(d)
    moon_t = tropical_moon_longitude(d)
    sun_s = to_sidereal(sun_t, aya)
    moon_s = to_sidereal(moon_t, aya)

    elongation = (moon_s - sun_s) % 360.0
    tithi_index = int(elongation // 12.0)  # 0..29
    paksha = "shukla" if tithi_index < 15 else "krishna"
    paksha_ru = "растущая" if paksha == "shukla" else "убывающая"
    tithi_num = tithi_index + 1
    if tithi_num == 15:
        tithi_name = "Пурнима"
    elif tithi_num == 30:
        tithi_name = "Амавасья"
    elif tithi_num < 15:
        tithi_name = _TITHI_NAMES_RU[tithi_num - 1]
    else:
        # Krishna 16..29 → Pratipat..Chaturdashi names
        tithi_name = _TITHI_NAMES_RU[tithi_num - 16]

    nak_index = int(moon_s // (360.0 / 27.0)) % 27
    pada = int((moon_s % (360.0 / 27.0)) // (360.0 / 108.0)) + 1

    yoga_index = int(((sun_s + moon_s) % 360.0) // (360.0 / 27.0)) % 27

    # Karana: 60 half-tithis in lunar month; fixed sequence with specials at ends.
    karana_half = int(elongation // 6.0)  # 0..59
    if karana_half == 0:
        karana_name = "Кимстугхна"
        karana_index = 10
    elif karana_half >= 57:
        # 57 Shakuni, 58 Chatuspada, 59 Naga
        specials = ["Шакуни", "Чатuspада", "Нага"]
        karana_name = specials[karana_half - 57]
        karana_index = 7 + (karana_half - 57)
    else:
        # Repeating Bava..Vishti (7) for halves 1..56
        karana_index = (karana_half - 1) % 7
        karana_name = _KARANA_RU[karana_index]

    wd = d.weekday()
    vara_slug, vara_planet, vara_planet_ru, vara_name_ru = _VARA[wd]

    return {
        "ayanamsha": {"id": AYANAMSHA_ID, "degrees": round(aya, 4)},
        "sun_sidereal_lon": round(sun_s, 4),
        "moon_sidereal_lon": round(moon_s, 4),
        "tithi": {
            "number": tithi_num,
            "index": tithi_index,
            "name_ru": tithi_name,
            "paksha": paksha,
            "paksha_ru": paksha_ru,
            "elongation_deg": round(elongation, 4),
        },
        "nakshatra": {
            "index": nak_index,
            "number": nak_index + 1,
            "name_ru": _NAKSHATRA_RU[nak_index],
            "pada": pada,
        },
        "yoga": {
            "index": yoga_index,
            "number": yoga_index + 1,
            "name_ru": _YOGA_RU[yoga_index],
        },
        "karana": {
            "index": karana_index,
            "name_ru": karana_name,
            "half_index": karana_half,
        },
        "vara": {
            "weekday": vara_slug,
            "name_ru": vara_name_ru,
            "ruler_planet": vara_planet,
            "ruler_planet_ru": vara_planet_ru,
        },
        "target_date": d.isoformat(),
        "method": "lahiri_approx_v0",
    }


def _day_eighth_window(sunrise: datetime, sunset: datetime, segment_1_based: int) -> dict[str, str]:
    span = (sunset - sunrise) / 8
    start = sunrise + span * (segment_1_based - 1)
    end = sunrise + span * segment_1_based
    return {
        "start_local": start.isoformat(timespec="seconds"),
        "end_local": end.isoformat(timespec="seconds"),
        "segment": segment_1_based,
    }


def compute_muhurta_intervals(
    d: date,
    *,
    lat: float,
    lon: float,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    sun = sun_rise_set_local(d, lat=lat, lon=lon, timezone_name=timezone_name)
    sunrise = datetime.fromisoformat(sun["sunrise_local"])
    sunset = datetime.fromisoformat(sun["sunset_local"])
    wd = d.weekday()
    return {
        "rahu_kala": {
            "name_ru": "Раху-кала",
            **_day_eighth_window(sunrise, sunset, _RAHU_SEGMENT[wd]),
        },
        "yamaganda": {
            "name_ru": "Ямаганда",
            **_day_eighth_window(sunrise, sunset, _YAMAGANDA_SEGMENT[wd]),
        },
        "gulika_kala": {
            "name_ru": "Гулика-кала",
            **_day_eighth_window(sunrise, sunset, _GULIKA_SEGMENT[wd]),
        },
        "sunrise_local": sun["sunrise_local"],
        "sunset_local": sun["sunset_local"],
    }


def build_panchanga_payload(
    d: date,
    *,
    lat: float | None = None,
    lon: float | None = None,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    core = compute_panchanga_core(d)
    caps = ["tithi", "nakshatra", "yoga", "karana", "vara", "ayanamsha"]
    muhurta = None
    if lat is not None and lon is not None:
        try:
            muhurta = compute_muhurta_intervals(
                d, lat=float(lat), lon=float(lon), timezone_name=timezone_name
            )
            caps.append("muhurta_intervals")
        except ValueError:
            muhurta = None

    t = core["tithi"]
    n = core["nakshatra"]
    summary = (
        f"Панчанга (Lahiri): титхи {t['name_ru']} ({t['paksha_ru']}), "
        f"накшатра {n['name_ru']} (пада {n['pada']}), "
        f"йога {core['yoga']['name_ru']}, карана {core['karana']['name_ru']}, "
        f"{core['vara']['name_ru']}."
    )
    return {
        **core,
        "muhurta": muhurta,
        "capability_ids": caps,
        "summary_ru": summary,
    }
