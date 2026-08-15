"""Timed major Moon aspects for a civil-day window (VOC / lunar timeline).

Canon: DAY_SOURCES_CANON §5.2.3–5.2.4 — majors only (0/60/90/120/180).
Uses AstroService.compute_chart samples + binary search (same idea as returns).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Protocol
from zoneinfo import ZoneInfo

MAJOR_ASPECTS: tuple[tuple[str, float], ...] = (
    ("conjunction", 0.0),
    ("sextile", 60.0),
    ("square", 90.0),
    ("trine", 120.0),
    ("opposition", 180.0),
)

# Bodies Moon aspects against for VOC / daily timeline (lowercase normalize).
_TARGET_BODIES = (
    "sun",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
)

_ASPECT_RU = {
    "conjunction": "соединение",
    "sextile": "секстиль",
    "square": "квадрат",
    "trine": "тригон",
    "opposition": "оппозиция",
}

_PLANET_RU = {
    "sun": "Солнце",
    "mercury": "Меркурий",
    "venus": "Венера",
    "mars": "Марс",
    "jupiter": "Юпитер",
    "saturn": "Сатурн",
    "uranus": "Уран",
    "neptune": "Нептун",
    "pluto": "Плутон",
    "moon": "Луна",
}


class _ChartClient(Protocol):
    async def compute_chart(
        self, birth_payload: dict, coordinates: dict | None = None
    ) -> Any: ...


def _norm_body(name: str) -> str:
    return str(name or "").strip().lower().replace(" ", "_")


def _signed_rel(moon: float, planet: float) -> float:
    """Moon−planet in (−180, 180]."""
    return ((moon - planet + 180.0) % 360.0) - 180.0


def _residuals_for_aspect(moon: float, planet: float, angle: float) -> list[float]:
    """Signed residuals that cross 0 when the major aspect exacts.

    Conjunction/opposition: one target. Other majors: +angle and −angle.
    """
    rel = _signed_rel(moon, planet)
    if angle <= 0.0:
        return [rel]
    if abs(angle - 180.0) < 1e-9:
        return [((moon - planet) % 360.0) - 180.0]
    return [
        ((rel - angle + 180.0) % 360.0) - 180.0,
        ((rel + angle + 180.0) % 360.0) - 180.0,
    ]


def _longitudes_from_positions(positions: list[Any]) -> dict[str, float]:
    out: dict[str, float] = {}
    for pos in positions or []:
        if not isinstance(pos, dict):
            continue
        body = _norm_body(str(pos.get("body") or pos.get("planet") or ""))
        lon = pos.get("longitude")
        if body and isinstance(lon, (int, float)):
            out[body] = float(lon) % 360.0
    return out


async def _longitudes_at(
    astro_service: _ChartClient,
    when: datetime,
    *,
    coordinates: dict[str, float] | None = None,
) -> dict[str, float]:
    birth_payload: dict[str, Any] = {
        "date": when.date().isoformat(),
        "time": when.strftime("%H:%M:%S"),
        "location": "Equator",
    }
    # Prefer IANA from aware datetime — never treat local civil as UT.
    tzinfo = when.tzinfo
    tz_name = getattr(tzinfo, "key", None) if tzinfo is not None else None
    if isinstance(tz_name, str) and tz_name.strip():
        birth_payload["timezone_name"] = tz_name.strip()
    elif tzinfo is not None:
        offset = when.utcoffset()
        if offset is not None:
            birth_payload["timezone_offset_minutes"] = int(offset.total_seconds() // 60)
    else:
        birth_payload["timezone_name"] = "UTC"
    chart = await astro_service.compute_chart(
        birth_payload=birth_payload,
        coordinates=coordinates or {"latitude": 0.0, "longitude": 0.0},
    )
    positions = getattr(chart, "positions", None) or []
    return _longitudes_from_positions(list(positions))


async def _bisect_aspect_time(
    astro_service: _ChartClient,
    *,
    left: datetime,
    right: datetime,
    planet: str,
    aspect_angle: float,
    residual_index: int,
    coordinates: dict[str, float] | None,
    max_iter: int = 18,
) -> datetime | None:
    """Bisect until chosen Moon–planet residual ≈ 0 for the given major angle."""
    lo, hi = left, right
    lon_lo = await _longitudes_at(astro_service, lo, coordinates=coordinates)
    lon_hi = await _longitudes_at(astro_service, hi, coordinates=coordinates)
    if "moon" not in lon_lo or planet not in lon_lo or "moon" not in lon_hi or planet not in lon_hi:
        return None
    r_list_lo = _residuals_for_aspect(lon_lo["moon"], lon_lo[planet], aspect_angle)
    r_list_hi = _residuals_for_aspect(lon_hi["moon"], lon_hi[planet], aspect_angle)
    if residual_index >= len(r_list_lo) or residual_index >= len(r_list_hi):
        return None
    r_lo = r_list_lo[residual_index]
    r_hi = r_list_hi[residual_index]
    if abs(r_lo) < 1e-6:
        return lo
    if abs(r_hi) < 1e-6:
        return hi
    if r_lo * r_hi > 0:
        return None

    for _ in range(max_iter):
        mid = lo + (hi - lo) / 2
        lon_mid = await _longitudes_at(astro_service, mid, coordinates=coordinates)
        if "moon" not in lon_mid or planet not in lon_mid:
            return None
        r_mid = _residuals_for_aspect(lon_mid["moon"], lon_mid[planet], aspect_angle)[residual_index]
        if abs(r_mid) * 60.0 <= 2.0:  # ≤ ~2 arcminutes
            return mid.replace(microsecond=0)
        if r_lo * r_mid <= 0:
            hi, r_hi = mid, r_mid
        else:
            lo, r_lo = mid, r_mid
    return (lo + (hi - lo) / 2).replace(microsecond=0)


def _zone(timezone_name: str | None) -> ZoneInfo:
    raw = (timezone_name or "UTC").strip() or "UTC"
    try:
        return ZoneInfo(raw)
    except Exception:
        return ZoneInfo("UTC")


async def find_timed_major_moon_aspects(
    astro_service: _ChartClient,
    *,
    target_date: date,
    lookback_days: int = 2,
    lookahead_days: int = 3,
    step_hours: int = 2,
    coordinates: dict[str, float] | None = None,
    timezone_name: str | None = None,
) -> list[dict[str, Any]]:
    """Return major Moon aspects with exact_time in [target−lookback, target+lookahead]."""
    tz = _zone(timezone_name)
    start = datetime.combine(target_date - timedelta(days=lookback_days), datetime.min.time(), tzinfo=tz)
    end = datetime.combine(
        target_date + timedelta(days=lookahead_days), datetime.min.time(), tzinfo=tz
    ) + timedelta(days=1)
    step = timedelta(hours=max(1, step_hours))

    samples: list[tuple[datetime, dict[str, float]]] = []
    cursor = start
    while cursor <= end:
        try:
            lons = await _longitudes_at(astro_service, cursor, coordinates=coordinates)
        except Exception:
            cursor += step
            continue
        if "moon" in lons:
            samples.append((cursor, lons))
        cursor += step

    found: list[dict[str, Any]] = []
    seen: set[str] = set()

    for i in range(len(samples) - 1):
        t0, lon0 = samples[i]
        t1, lon1 = samples[i + 1]
        for planet in _TARGET_BODIES:
            if planet not in lon0 or planet not in lon1:
                continue
            for aspect_id, angle in MAJOR_ASPECTS:
                r0s = _residuals_for_aspect(lon0["moon"], lon0[planet], angle)
                r1s = _residuals_for_aspect(lon1["moon"], lon1[planet], angle)
                for idx, (r0, r1) in enumerate(zip(r0s, r1s)):
                    if r0 * r1 > 0 and abs(r0) > 1.0 and abs(r1) > 1.0:
                        continue
                    if abs(r0) > 50 and abs(r1) > 50:
                        continue
                    exact = await _bisect_aspect_time(
                        astro_service,
                        left=t0,
                        right=t1,
                        planet=planet,
                        aspect_angle=angle,
                        residual_index=idx,
                        coordinates=coordinates,
                    )
                    if exact is None:
                        continue
                    if exact < start or exact > end:
                        continue
                    aid = f"moon-{aspect_id}-{planet}-{exact.strftime('%Y%m%d%H%M')}"
                    if aid in seen:
                        continue
                    seen.add(aid)
                    found.append(
                        {
                            "id": aid,
                            "kind": "timed_lunar_aspect",
                            "aspect": aspect_id,
                            "planet": planet,
                            "planet_ru": _PLANET_RU.get(planet, planet),
                            "exact_time": exact.isoformat(timespec="seconds"),
                            "title": (
                                f"Луна — {_ASPECT_RU.get(aspect_id, aspect_id)} — "
                                f"{_PLANET_RU.get(planet, planet)}"
                            ),
                        }
                    )

    found.sort(key=lambda row: str(row.get("exact_time") or ""))
    return found


async def find_moon_sign_ingress_time(
    astro_service: _ChartClient,
    *,
    around_date: date,
    coordinates: dict[str, float] | None = None,
    timezone_name: str | None = None,
) -> datetime | None:
    """Bisect Moon crossing into a new sign near around_date (noon ± 36h)."""
    tz = _zone(timezone_name)
    center = datetime.combine(around_date, datetime.min.time().replace(hour=12), tzinfo=tz)
    left = center - timedelta(hours=36)
    right = center + timedelta(hours=36)
    step = timedelta(hours=2)
    samples: list[tuple[datetime, float, int]] = []
    cursor = left
    while cursor <= right:
        try:
            lons = await _longitudes_at(astro_service, cursor, coordinates=coordinates)
        except Exception:
            cursor += step
            continue
        if "moon" in lons:
            lon = lons["moon"]
            samples.append((cursor, lon, int(lon // 30) % 12))
        cursor += step

    for i in range(len(samples) - 1):
        t0, _, s0 = samples[i]
        t1, _, s1 = samples[i + 1]
        if s0 == s1:
            continue
        lo, hi = t0, t1
        for _ in range(18):
            mid = lo + (hi - lo) / 2
            lons = await _longitudes_at(astro_service, mid, coordinates=coordinates)
            if "moon" not in lons:
                break
            sign = int(lons["moon"] // 30) % 12
            if sign == s0:
                lo = mid
            else:
                hi = mid
            if (hi - lo).total_seconds() <= 60:
                return hi.replace(microsecond=0)
        return hi.replace(microsecond=0)
    return None


_ASPECT_ANGLE = {name: angle for name, angle in MAJOR_ASPECTS}


def match_timed_lunar_exact(
    headline: dict[str, Any] | None,
    timed_lunar_aspects: list[dict[str, Any]] | None,
    *,
    target_date: date,
) -> str | None:
    """Reuse Moon timeline if the headline pair is Moon × planet today."""
    hs = headline if isinstance(headline, dict) else {}
    a = _norm_body(str(hs.get("planet_a") or ""))
    b = _norm_body(str(hs.get("planet_b") or ""))
    aspect = _norm_body(str(hs.get("aspect") or ""))
    other = b if a == "moon" else a if b == "moon" else ""
    if not other or not aspect:
        return None
    day = target_date.isoformat()
    for row in timed_lunar_aspects or []:
        if not isinstance(row, dict):
            continue
        if _norm_body(str(row.get("planet") or "")) != other:
            continue
        if _norm_body(str(row.get("aspect") or "")) != aspect:
            continue
        when = str(row.get("exact_time") or "").strip()
        if when[:10] == day:
            return when
    return None


async def _bisect_pair_aspect_time(
    astro_service: _ChartClient,
    *,
    left: datetime,
    right: datetime,
    body_a: str,
    body_b: str,
    aspect_angle: float,
    residual_index: int,
    coordinates: dict[str, float] | None,
    max_iter: int = 18,
) -> datetime | None:
    lo, hi = left, right
    lon_lo = await _longitudes_at(astro_service, lo, coordinates=coordinates)
    lon_hi = await _longitudes_at(astro_service, hi, coordinates=coordinates)
    if body_a not in lon_lo or body_b not in lon_lo or body_a not in lon_hi or body_b not in lon_hi:
        return None
    r_list_lo = _residuals_for_aspect(lon_lo[body_a], lon_lo[body_b], aspect_angle)
    r_list_hi = _residuals_for_aspect(lon_hi[body_a], lon_hi[body_b], aspect_angle)
    if residual_index >= len(r_list_lo) or residual_index >= len(r_list_hi):
        return None
    r_lo = r_list_lo[residual_index]
    r_hi = r_list_hi[residual_index]
    if abs(r_lo) < 1e-6:
        return lo
    if abs(r_hi) < 1e-6:
        return hi
    if r_lo * r_hi > 0:
        return None

    for _ in range(max_iter):
        mid = lo + (hi - lo) / 2
        lon_mid = await _longitudes_at(astro_service, mid, coordinates=coordinates)
        if body_a not in lon_mid or body_b not in lon_mid:
            return None
        r_mid = _residuals_for_aspect(lon_mid[body_a], lon_mid[body_b], aspect_angle)[residual_index]
        if abs(r_mid) * 60.0 <= 2.0:
            return mid.replace(microsecond=0)
        if r_lo * r_mid <= 0:
            hi, r_hi = mid, r_mid
        else:
            lo, r_lo = mid, r_mid
    return (lo + (hi - lo) / 2).replace(microsecond=0)


async def find_exact_pair_aspect_time(
    astro_service: _ChartClient,
    *,
    planet_a: str,
    planet_b: str,
    aspect: str,
    target_date: date,
    timezone_name: str | None = None,
    coordinates: dict[str, float] | None = None,
    step_hours: int = 2,
) -> datetime | None:
    """Civil-day zero-cross for a shared-sky pair. None if it does not exact today.

    Noon orb is not a clock. WAVE2: orb ≠ time.
    """
    a = _norm_body(planet_a)
    b = _norm_body(planet_b)
    angle = _ASPECT_ANGLE.get(_norm_body(aspect))
    if not a or not b or a == b or angle is None:
        return None
    tz = _zone(timezone_name)
    start = datetime.combine(target_date, datetime.min.time(), tzinfo=tz)
    end = start + timedelta(days=1)
    step = timedelta(hours=max(1, step_hours))
    samples: list[tuple[datetime, dict[str, float]]] = []
    cursor = start
    while cursor <= end:
        try:
            lons = await _longitudes_at(astro_service, cursor, coordinates=coordinates)
        except Exception:
            cursor += step
            continue
        if a in lons and b in lons:
            samples.append((cursor, lons))
        cursor += step

    for i in range(len(samples) - 1):
        t0, lon0 = samples[i]
        t1, lon1 = samples[i + 1]
        r0s = _residuals_for_aspect(lon0[a], lon0[b], angle)
        r1s = _residuals_for_aspect(lon1[a], lon1[b], angle)
        for idx, (r0, r1) in enumerate(zip(r0s, r1s)):
            if r0 * r1 > 0 and abs(r0) > 1.0 and abs(r1) > 1.0:
                continue
            if abs(r0) > 50 and abs(r1) > 50:
                continue
            exact = await _bisect_pair_aspect_time(
                astro_service,
                left=t0,
                right=t1,
                body_a=a,
                body_b=b,
                aspect_angle=angle,
                residual_index=idx,
                coordinates=coordinates,
            )
            if exact is None:
                continue
            if exact < start or exact >= end:
                continue
            return exact
    return None


async def resolve_sky_aspect_exact_time(
    astro_service: _ChartClient,
    *,
    headline: dict[str, Any] | None,
    timed_lunar_aspects: list[dict[str, Any]] | None,
    target_date: date,
    timezone_name: str | None = None,
    coordinates: dict[str, float] | None = None,
) -> str | None:
    """Exact ISO clock for headline if it perfects on target_date; else None."""
    matched = match_timed_lunar_exact(
        headline, timed_lunar_aspects, target_date=target_date
    )
    if matched:
        return matched
    hs = headline if isinstance(headline, dict) else {}
    exact = await find_exact_pair_aspect_time(
        astro_service,
        planet_a=str(hs.get("planet_a") or ""),
        planet_b=str(hs.get("planet_b") or ""),
        aspect=str(hs.get("aspect") or ""),
        target_date=target_date,
        timezone_name=timezone_name,
        coordinates=coordinates,
    )
    if exact is None:
        return None
    return exact.isoformat(timespec="seconds")

