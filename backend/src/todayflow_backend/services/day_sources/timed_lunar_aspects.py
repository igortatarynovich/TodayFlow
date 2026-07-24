"""Timed major Moon aspects for a civil-day window (VOC / lunar timeline).

Canon: DAY_SOURCES_CANON §5.2.3–5.2.4 — majors only (0/60/90/120/180).
Uses AstroService.compute_chart samples + binary search (same idea as returns).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Protocol

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
    chart = await astro_service.compute_chart(
        birth_payload={
            "date": when.date().isoformat(),
            "time": when.strftime("%H:%M:%S"),
            "location": "Equator",
        },
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


async def find_timed_major_moon_aspects(
    astro_service: _ChartClient,
    *,
    target_date: date,
    lookback_days: int = 2,
    lookahead_days: int = 3,
    step_hours: int = 2,
    coordinates: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """Return major Moon aspects with exact_time in [target−lookback, target+lookahead]."""
    start = datetime.combine(target_date - timedelta(days=lookback_days), datetime.min.time())
    end = datetime.combine(
        target_date + timedelta(days=lookahead_days), datetime.min.time()
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
) -> datetime | None:
    """Bisect Moon crossing into a new sign near around_date (noon ± 36h)."""
    center = datetime.combine(around_date, datetime.min.time().replace(hour=12))
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
