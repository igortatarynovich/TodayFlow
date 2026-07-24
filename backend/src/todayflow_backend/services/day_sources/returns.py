"""Solar + lunar returns soft layer for personal_astrology (canon §5.3).

School freeze v0:
- Solar return: civil noon date near birthday anniversary when tropical Sun
  is closest to natal noon Sun longitude (closed-form; not Swiss exact).
- Lunar return: nearest civil noon date when tropical Moon ≈ natal Moon.
- Soft ASC on return chart only with birth time+place (birth place).
- Period context: days since last / until next return.
"""

from __future__ import annotations

from datetime import date, time, timedelta
from typing import Any

from todayflow_backend.services.day_sources.panchanga import (
    tropical_moon_longitude,
    tropical_sun_longitude,
)
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

_SYNODIC_HINT_DAYS = 27.32166  # sidereal month ≈ return of Moon to same longitude


def _ang_dist(a: float, b: float) -> float:
    d = (float(a) - float(b) + 180.0) % 360.0 - 180.0
    return abs(d)


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


def _safe_anniversary(year: int, birth: date) -> date:
    try:
        return date(year, birth.month, birth.day)
    except ValueError:
        # Feb 29 → Feb 28 in non-leap years
        return date(year, birth.month, min(birth.day, 28))


def _best_noon_in_window(
    target_lon: float,
    center: date,
    *,
    lon_fn,
    half_window_days: int,
) -> tuple[date, float, float]:
    """Return (best_date, longitude_at_noon, angular_error)."""
    best_d = center
    best_lon = float(lon_fn(center))
    best_err = _ang_dist(best_lon, target_lon)
    for delta in range(-half_window_days, half_window_days + 1):
        if delta == 0:
            continue
        d = center + timedelta(days=delta)
        lon = float(lon_fn(d))
        err = _ang_dist(lon, target_lon)
        if err < best_err:
            best_err = err
            best_d = d
            best_lon = lon
    return best_d, best_lon, best_err


def find_solar_return_date(birth_date: date, target_year: int) -> tuple[date, float, float]:
    natal = tropical_sun_longitude(birth_date)
    approx = _safe_anniversary(target_year, birth_date)
    return _best_noon_in_window(natal, approx, lon_fn=tropical_sun_longitude, half_window_days=3)


def find_lunar_return_near(birth_date: date, around: date) -> tuple[date, float, float]:
    natal = tropical_moon_longitude(birth_date)
    # Seed from integer sidereal months since birth.
    cycles = max(0, round((around - birth_date).days / _SYNODIC_HINT_DAYS))
    seed = birth_date + timedelta(days=round(cycles * _SYNODIC_HINT_DAYS))
    # Nudge seed into ±14d of around.
    while seed < around - timedelta(days=14):
        seed += timedelta(days=round(_SYNODIC_HINT_DAYS))
    while seed > around + timedelta(days=14):
        seed -= timedelta(days=round(_SYNODIC_HINT_DAYS))
    return _best_noon_in_window(natal, seed, lon_fn=tropical_moon_longitude, half_window_days=2)


def _soft_asc(
    on: date,
    *,
    birth_time: time | None,
    birth_lat: float | None,
    birth_lon: float | None,
    timezone_name: str | None,
) -> dict[str, Any] | None:
    if birth_time is None or birth_lat is None or birth_lon is None:
        return None
    asc = compute_sidereal_lagna(
        on,
        birth_time,
        birth_lat=float(birth_lat),
        birth_lon=float(birth_lon),
        timezone_name=timezone_name,
    )
    return _body(float(asc["tropical_lon"]), name="ASC")


def build_solar_return(
    birth_date: date,
    target_date: date,
    *,
    birth_time: time | None = None,
    birth_lat: float | None = None,
    birth_lon: float | None = None,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    natal_sun_lon = tropical_sun_longitude(birth_date)
    natal_sun = _body(natal_sun_lon, name="Sun")

    # Current period = last solar return on/before target_date.
    this_year = target_date.year
    d_this, lon_this, err_this = find_solar_return_date(birth_date, this_year)
    if d_this <= target_date:
        last_d, last_lon, last_err = d_this, lon_this, err_this
        next_d, next_lon, next_err = find_solar_return_date(birth_date, this_year + 1)
        period_year = this_year
    else:
        last_d, last_lon, last_err = find_solar_return_date(birth_date, this_year - 1)
        next_d, next_lon, next_err = d_this, lon_this, err_this
        period_year = this_year - 1

    sun_at_return = _body(last_lon, name="Sun")
    moon_at_return = _body(tropical_moon_longitude(last_d), name="Moon")
    asc = _soft_asc(
        last_d,
        birth_time=birth_time,
        birth_lat=birth_lat,
        birth_lon=birth_lon,
        timezone_name=timezone_name,
    )
    depth = "sun_moon_noon" if asc is None else "sun_moon_asc_soft"

    days_since = (target_date - last_d).days
    days_until = (next_d - target_date).days

    summary = (
        f"Solar return {period_year}: карта от {last_d.isoformat()} "
        f"(Солнце ≈ {sun_at_return['sign_ru']} {sun_at_return['degree_in_sign']:.1f}°, "
        f"ошибка noon {last_err:.2f}°). "
        f"День {days_since + 1} периода; до следующего SR ~{days_until} дн."
    )
    if asc:
        summary += f" Soft ASC SR — {asc['sign_ru']}."

    beat = {
        "id": "returns-solar",
        "kind": "solar_return",
        "title": f"Solar return · {period_year}",
        "story_ru": summary,
        "evidence_ref": "personal_astrology.solar_return",
    }

    return {
        "capability_id": "solar_return",
        "school_canon": "solar_return_noon_closed_form_v0",
        "depth": depth,
        "period_year": period_year,
        "return_date": last_d.isoformat(),
        "next_return_date": next_d.isoformat(),
        "days_since_return": days_since,
        "days_until_next": days_until,
        "noon_error_deg": round(last_err, 4),
        "next_noon_error_deg": round(next_err, 4),
        "natal": {"sun": natal_sun},
        "return_chart_soft": {
            "sun": sun_at_return,
            "moon": moon_at_return,
            "ascendant": asc,
        },
        "limitation_ru": (
            "Дата SR — noon closed-form (не точный момент Swiss). "
            "Полная карта возврата — later."
        ),
        "beats": [beat],
        "summary_ru": summary[:420],
    }


def build_lunar_return(
    birth_date: date,
    target_date: date,
    *,
    birth_time: time | None = None,
    birth_lat: float | None = None,
    birth_lon: float | None = None,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    natal_moon_lon = tropical_moon_longitude(birth_date)
    natal_moon = _body(natal_moon_lon, name="Moon")

    near_d, near_lon, near_err = find_lunar_return_near(birth_date, target_date)
    if near_d <= target_date:
        last_d, last_lon, last_err = near_d, near_lon, near_err
        next_d, next_lon, next_err = find_lunar_return_near(
            birth_date, near_d + timedelta(days=14)
        )
    else:
        next_d, next_lon, next_err = near_d, near_lon, near_err
        last_d, last_lon, last_err = find_lunar_return_near(
            birth_date, near_d - timedelta(days=14)
        )

    moon_at = _body(last_lon, name="Moon")
    sun_at = _body(tropical_sun_longitude(last_d), name="Sun")
    asc = _soft_asc(
        last_d,
        birth_time=birth_time,
        birth_lat=birth_lat,
        birth_lon=birth_lon,
        timezone_name=timezone_name,
    )
    depth = "moon_noon" if asc is None else "moon_asc_soft"

    days_since = (target_date - last_d).days
    days_until = (next_d - target_date).days

    summary = (
        f"Lunar return: от {last_d.isoformat()} "
        f"(Луна ≈ {moon_at['sign_ru']} {moon_at['degree_in_sign']:.1f}°, "
        f"ошибка noon {last_err:.2f}°). "
        f"День {days_since + 1} лунного периода; до следующего LR ~{days_until} дн."
    )
    if asc:
        summary += f" Soft ASC LR — {asc['sign_ru']}."

    beat = {
        "id": "returns-lunar",
        "kind": "lunar_return",
        "title": f"Lunar return · {last_d.isoformat()}",
        "story_ru": summary,
        "evidence_ref": "personal_astrology.lunar_return",
    }

    return {
        "capability_id": "lunar_return",
        "school_canon": "lunar_return_noon_closed_form_v0",
        "depth": depth,
        "return_date": last_d.isoformat(),
        "next_return_date": next_d.isoformat(),
        "days_since_return": days_since,
        "days_until_next": days_until,
        "noon_error_deg": round(last_err, 4),
        "next_noon_error_deg": round(next_err, 4),
        "natal": {"moon": natal_moon},
        "return_chart_soft": {
            "sun": sun_at,
            "moon": moon_at,
            "ascendant": asc,
        },
        "limitation_ru": (
            "Дата LR — noon closed-form (не точный момент Swiss). "
            "Полная карта возврата — later."
        ),
        "beats": [beat],
        "summary_ru": summary[:420],
    }


def build_returns_pack(
    birth_date: date,
    target_date: date,
    *,
    birth_time: time | None = None,
    birth_lat: float | None = None,
    birth_lon: float | None = None,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    solar = build_solar_return(
        birth_date,
        target_date,
        birth_time=birth_time,
        birth_lat=birth_lat,
        birth_lon=birth_lon,
        timezone_name=timezone_name,
    )
    lunar = build_lunar_return(
        birth_date,
        target_date,
        birth_time=birth_time,
        birth_lat=birth_lat,
        birth_lon=birth_lon,
        timezone_name=timezone_name,
    )
    return {
        "solar_return": solar,
        "lunar_return": lunar,
        "capability_ids": ["solar_return", "lunar_return"],
        "beats": list(solar.get("beats") or [])[:1] + list(lunar.get("beats") or [])[:1],
        "summary_ru": f"{solar['summary_ru']} {lunar['summary_ru']}"[:480],
    }
