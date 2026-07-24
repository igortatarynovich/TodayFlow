"""Annual (and soft monthly) profections for personal_astrology (canon §5.3).

School: whole-sign annual profection from ASC when time+place; otherwise solar-chart
proxy from tropical Sun sign at birth_date (not a substitute for true ASC).
"""

from __future__ import annotations

from datetime import date, time
from typing import Any

from todayflow_backend.services.day_sources.panchanga import tropical_sun_longitude
from todayflow_backend.services.day_sources.vedic_personal import compute_sidereal_lagna

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

# Traditional domicile rulers (tropical whole-sign).
_SIGN_RULERS: list[tuple[str, str]] = [
    ("Mars", "Марс"),
    ("Venus", "Венера"),
    ("Mercury", "Меркурий"),
    ("Moon", "Луна"),
    ("Sun", "Солнце"),
    ("Mercury", "Меркурий"),
    ("Venus", "Венера"),
    ("Mars", "Марс"),
    ("Jupiter", "Юпитер"),
    ("Saturn", "Сатурн"),
    ("Saturn", "Сатурн"),
    ("Jupiter", "Юпитер"),
]

_HOUSE_THEME_RU: dict[int, str] = {
    1: "тело, самопрезентация, как вас видят",
    2: "ресурсы, речь, ближайшая опора",
    3: "короткие шаги, связь, смелость малого действия",
    4: "дом, корни, внутреннее основание",
    5: "творчество, радость, риск сердца",
    6: "ритм дел, здоровье-как-практика, служебное",
    7: "другой человек, договор, зеркало",
    8: "глубина, общие ресурсы, перемены",
    9: "смысл, путь, обучение",
    10: "дело, видимость, ответственность",
    11: "круг, цели, поддержка извне",
    12: "пауза, уединение, невидимая работа",
}


def completed_age_years(birth: date, on: date) -> int:
    years = on.year - birth.year
    if (on.month, on.day) < (birth.month, birth.day):
        years -= 1
    return max(0, years)


def months_since_birthday(birth: date, on: date) -> int:
    """Months elapsed since last birthday anniversary (0..11)."""
    age = completed_age_years(birth, on)
    last_bd = date(birth.year + age, birth.month, birth.day)
    months = (on.year - last_bd.year) * 12 + (on.month - last_bd.month)
    if on.day < last_bd.day:
        months -= 1
    return max(0, min(11, months))


def _sign_index(lon: float) -> int:
    return int(float(lon) % 360.0 // 30.0) % 12


def resolve_first_house_sign(
    birth_date: date,
    *,
    birth_time: time | None,
    birth_lat: float | None,
    birth_lon: float | None,
    timezone_name: str | None,
) -> dict[str, Any]:
    if birth_time is not None and birth_lat is not None and birth_lon is not None:
        # Tropical ASC for western traditional profections (use tropical_lon).
        asc = compute_sidereal_lagna(
            birth_date,
            birth_time,
            birth_lat=float(birth_lat),
            birth_lon=float(birth_lon),
            timezone_name=timezone_name,
        )
        sign_i = _sign_index(float(asc["tropical_lon"]))
        return {
            "sign_index": sign_i,
            "sign_ru": _SIGN_RU[sign_i],
            "method": "tropical_asc_whole_sign",
            "ascendant_tropical_lon": asc["tropical_lon"],
        }

    sun_lon = tropical_sun_longitude(birth_date)
    sign_i = _sign_index(sun_lon)
    return {
        "sign_index": sign_i,
        "sign_ru": _SIGN_RU[sign_i],
        "method": "solar_sign_proxy",
        "sun_tropical_lon": round(sun_lon, 4),
    }


def build_profections(
    birth_date: date,
    target_date: date,
    *,
    birth_time: time | None = None,
    birth_lat: float | None = None,
    birth_lon: float | None = None,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    age = completed_age_years(birth_date, target_date)
    first = resolve_first_house_sign(
        birth_date,
        birth_time=birth_time,
        birth_lat=birth_lat,
        birth_lon=birth_lon,
        timezone_name=timezone_name,
    )
    annual_house = (age % 12) + 1
    annual_sign_i = (int(first["sign_index"]) + annual_house - 1) % 12
    lord_id, lord_ru = _SIGN_RULERS[annual_sign_i]

    months = months_since_birthday(birth_date, target_date)
    month_house = ((annual_house - 1 + months) % 12) + 1
    month_sign_i = (int(first["sign_index"]) + month_house - 1) % 12
    month_lord_id, month_lord_ru = _SIGN_RULERS[month_sign_i]

    depth = "asc_whole_sign" if first["method"] == "tropical_asc_whole_sign" else "solar_proxy"

    theme = _HOUSE_THEME_RU.get(annual_house, "")
    summary = (
        f"Профекция года (возраст {age}): {annual_house}-й дом, "
        f"знак {_SIGN_RU[annual_sign_i]}, управитель {lord_ru}"
        + (f" — {theme}." if theme else ".")
    )
    if depth == "solar_proxy":
        summary = (
            f"{summary} База — солнечный знак (нет времени/места для ASC)."
        )

    beat = {
        "id": f"profection-annual-h{annual_house}",
        "kind": "profection_annual",
        "title": f"Профекция: {annual_house}-й дом · {lord_ru}",
        "story_ru": summary,
        "evidence_ref": "personal_astrology.profections",
    }

    return {
        "capability_id": "profections",
        "school_canon": "whole_sign_annual_profection_v0",
        "depth": depth,
        "age_years": age,
        "first_house": first,
        "annual": {
            "house": annual_house,
            "sign_index": annual_sign_i,
            "sign_ru": _SIGN_RU[annual_sign_i],
            "lord": lord_id,
            "lord_ru": lord_ru,
            "theme_ru": theme,
        },
        "monthly": {
            "house": month_house,
            "sign_ru": _SIGN_RU[month_sign_i],
            "lord": month_lord_id,
            "lord_ru": month_lord_ru,
            "months_since_birthday": months,
        },
        "beats": [beat],
        "summary_ru": summary[:360],
    }
