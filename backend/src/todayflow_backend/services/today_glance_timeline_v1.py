"""Wave 2 Phase C — glance_timeline from natal_activations rank 1–3 + exact-time search.

Uses the same activation pool as VerdictStrip / day_scenario (today_natal_activations_v1).
Exact search: shared sky samples across the local day, then residual zero-cross + bisect.
If no exact within the civil day → activation stays in the pool but is omitted from glance.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Any

from todayflow_backend.services.day_lifecycle_clock_c5 import resolve_zone
from todayflow_backend.services.day_sources.timed_lunar_aspects import (
    _longitudes_at,
    _residuals_for_aspect,
)

logger = logging.getLogger(__name__)

ASPECT_ANGLE: dict[str, float] = {
    "conjunction": 0.0,
    "sextile": 60.0,
    "square": 90.0,
    "trine": 120.0,
    "quincunx": 150.0,
    "opposition": 180.0,
    # Harmonics — same strength pool as activations; needed so exact-time
    # can resolve when top ranks are quintile/biquintile (else Glance stays empty).
    "quintile": 72.0,
    "biquintile": 144.0,
}

# Coarse shared samples; bisect refines toward ≤5 min (contract C.1).
SAMPLE_STEP_MINUTES = 30
BISECT_MAX_ITER = 16
MAX_GLANCE_ROWS = 3
# Search strength order beyond 1–3 when top ranks lack exact (minors/slow/no chart hit).
# Still one pool / one ranker — no second ranking.
GLANCE_SEARCH_MAX_RANK = 12

_PLANET_RU = {
    "sun": "Солнце",
    "moon": "Луна",
    "mercury": "Меркурий",
    "venus": "Венера",
    "mars": "Марс",
    "jupiter": "Юпитер",
    "saturn": "Сатурн",
    "uranus": "Уран",
    "neptune": "Нептун",
    "pluto": "Плутон",
}

# Soft / hard for glance valence (favorable | caution) — not VerdictStrip dictionary.
_SOFT = frozenset({"trine", "sextile"})
_HARD = frozenset({"square", "opposition", "quincunx"})


def _norm(name: str | None) -> str:
    return (name or "").strip().lower().replace(" ", "_")


def _natal_body_aliases(name: str) -> list[str]:
    n = _norm(name)
    aliases = {
        "asc": ["asc", "ascendant"],
        "ascendant": ["asc", "ascendant"],
        "mc": ["mc", "midheaven"],
        "midheaven": ["mc", "midheaven"],
        "dsc": ["dsc", "descendant"],
        "descendant": ["dsc", "descendant"],
        "north_node": ["north_node", "northnode", "true_node"],
        "south_node": ["south_node", "southnode"],
    }
    return aliases.get(n, [n])


def natal_longitude_from_chart(natal_chart: Any, natal_point: str) -> float | None:
    positions = getattr(natal_chart, "positions", None) or []
    wanted = set(_natal_body_aliases(natal_point))
    for pos in positions:
        if not isinstance(pos, dict):
            continue
        body = _norm(str(pos.get("body") or pos.get("planet") or ""))
        if body not in wanted:
            continue
        lon = pos.get("longitude")
        if isinstance(lon, (int, float)):
            return float(lon) % 360.0
    return None


def aspect_angle(aspect: str) -> float | None:
    return ASPECT_ANGLE.get(_norm(aspect))


def primary_residual(transit_lon: float, natal_lon: float, angle: float) -> float:
    """Single residual for scanning (min |r| among aspect residuals)."""
    residuals = _residuals_for_aspect(transit_lon, natal_lon, angle)
    return min(residuals, key=lambda r: abs(r))


def glance_valence(aspect: str, transiting_planet: str) -> str:
    asp = _norm(aspect)
    if asp in _SOFT:
        return "favorable"
    if asp in _HARD:
        return "caution"
    # Conjunction: benefics soft-ish, malefics caution
    planet = _norm(transiting_planet)
    if planet in {"venus", "jupiter"}:
        return "favorable"
    if planet in {"mars", "saturn", "pluto"}:
        return "caution"
    return "caution"


def label_short_for(transiting_planet: str, aspect: str) -> str:
    """≤ ~4 words RU — no planet/aspect jargon (contract §4); distinct by body+aspect."""
    from todayflow_backend.services.today_activation_copy_v1 import aspect_class_label_short

    return aspect_class_label_short(aspect, transiting_planet)


def local_day_bounds(local_date: date, timezone_name: str) -> tuple[datetime, datetime]:
    tz = resolve_zone(timezone_name)
    start = datetime.combine(local_date, datetime.min.time(), tzinfo=tz)
    end = start + timedelta(days=1)
    return start, end


async def sample_sky_longitudes(
    astro_service: Any,
    *,
    start: datetime,
    end: datetime,
    step_minutes: int,
    coordinates: dict[str, float] | None,
) -> list[tuple[datetime, dict[str, float]]]:
    """Shared sky samples for the civil day (one chart per step)."""
    step = timedelta(minutes=max(5, int(step_minutes)))
    samples: list[tuple[datetime, dict[str, float]]] = []
    cursor = start
    while cursor < end:
        try:
            lons = await _longitudes_at(astro_service, cursor, coordinates=coordinates)
            if lons:
                samples.append((cursor, lons))
        except Exception:
            logger.debug("glance_sample_failed at %s", cursor.isoformat(), exc_info=True)
        cursor += step
    # Ensure last edge if needed
    if not samples or samples[-1][0] < end - timedelta(minutes=1):
        try:
            edge = end - timedelta(seconds=1)
            lons = await _longitudes_at(astro_service, edge, coordinates=coordinates)
            if lons:
                samples.append((edge, lons))
        except Exception:
            pass
    return samples


async def _bisect_transit_to_natal(
    astro_service: Any,
    *,
    left: datetime,
    right: datetime,
    transit_body: str,
    natal_lon: float,
    angle: float,
    residual_index: int,
    coordinates: dict[str, float] | None,
) -> datetime | None:
    body = _norm(transit_body)
    lo, hi = left, right
    lon_lo = await _longitudes_at(astro_service, lo, coordinates=coordinates)
    lon_hi = await _longitudes_at(astro_service, hi, coordinates=coordinates)
    if body not in lon_lo or body not in lon_hi:
        return None
    r_list_lo = _residuals_for_aspect(lon_lo[body], natal_lon, angle)
    r_list_hi = _residuals_for_aspect(lon_hi[body], natal_lon, angle)
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
    for _ in range(BISECT_MAX_ITER):
        mid = lo + (hi - lo) / 2
        lon_mid = await _longitudes_at(astro_service, mid, coordinates=coordinates)
        if body not in lon_mid:
            return None
        r_mid = _residuals_for_aspect(lon_mid[body], natal_lon, angle)[residual_index]
        if abs(r_mid) * 60.0 <= 2.0:
            return mid.replace(microsecond=0)
        if r_lo * r_mid <= 0:
            hi, r_hi = mid, r_mid
        else:
            lo, r_lo = mid, r_mid
    return (lo + (hi - lo) / 2).replace(microsecond=0)


async def find_exact_time_for_activation(
    astro_service: Any,
    *,
    activation: dict[str, Any],
    natal_lon: float,
    samples: list[tuple[datetime, dict[str, float]]],
    coordinates: dict[str, float] | None,
) -> datetime | None:
    angle = aspect_angle(str(activation.get("aspect") or ""))
    if angle is None:
        return None
    body = _norm(str(activation.get("transiting_planet") or ""))
    if not body or len(samples) < 2:
        return None

    for i in range(len(samples) - 1):
        t0, lon0 = samples[i]
        t1, lon1 = samples[i + 1]
        if body not in lon0 or body not in lon1:
            continue
        r0s = _residuals_for_aspect(lon0[body], natal_lon, angle)
        r1s = _residuals_for_aspect(lon1[body], natal_lon, angle)
        for idx, (r0, r1) in enumerate(zip(r0s, r1s)):
            if r0 * r1 > 0 and abs(r0) > 1e-9 and abs(r1) > 1e-9:
                continue
            if abs(r0) < 1e-6:
                return t0.replace(microsecond=0)
            if abs(r1) < 1e-6:
                return t1.replace(microsecond=0)
            if r0 * r1 > 0:
                continue
            exact = await _bisect_transit_to_natal(
                astro_service,
                left=t0,
                right=t1,
                transit_body=body,
                natal_lon=natal_lon,
                angle=angle,
                residual_index=idx,
                coordinates=coordinates,
            )
            if exact is not None:
                return exact
    return None


def build_glance_timeline_rows(
    activations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Pure: activations with exact_time_local set → ≤3 glance rows sorted by time."""
    timed: list[dict[str, Any]] = []
    for act in activations:
        if not isinstance(act, dict):
            continue
        rank = act.get("rank")
        try:
            rank_i = int(rank) if rank is not None else 99
        except (TypeError, ValueError):
            rank_i = 99
        if rank_i < 1 or rank_i > GLANCE_SEARCH_MAX_RANK:
            continue
        exact = act.get("exact_time_local")
        if not exact:
            continue
        if isinstance(exact, datetime):
            time_local = exact.isoformat(timespec="minutes")
        else:
            time_local = str(exact)
        timed.append(
            {
                "time_local": time_local,
                "label_short": label_short_for(
                    str(act.get("transiting_planet") or ""),
                    str(act.get("aspect") or ""),
                ),
                "valence": glance_valence(
                    str(act.get("aspect") or ""),
                    str(act.get("transiting_planet") or ""),
                ),
                "driver_id": str(act.get("id") or ""),
                "rank": rank_i,
            }
        )
    timed.sort(key=lambda r: (str(r.get("time_local") or ""), int(r.get("rank") or 99)))
    return [
        {
            "time_local": r["time_local"],
            "label_short": r["label_short"],
            "valence": r["valence"],
            "driver_id": r["driver_id"],
        }
        for r in timed[:MAX_GLANCE_ROWS]
    ]


def _rank_int(act: dict[str, Any]) -> int:
    rank = act.get("rank")
    try:
        return int(rank) if rank is not None else 99
    except (TypeError, ValueError):
        return 99


async def compute_glance_timeline(
    *,
    activations: list[dict[str, Any]],
    natal_chart: Any,
    local_date: date,
    timezone_name: str,
    astro_service: Any,
    coordinates: dict[str, float] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Returns (glance_timeline, activations_with_exact_times).

    Exact-time search walks strength ranks 1…GLANCE_SEARCH_MAX_RANK (same pool,
    no second ranker). Stops early once MAX_GLANCE_ROWS have exact times.
    Untimeable aspects (no angle / no natal lon / no zero-cross today) stay null
    and are omitted from glance_timeline.
    """
    enriched = [dict(a) for a in activations if isinstance(a, dict)]
    for act in enriched:
        act["exact_time_local"] = None

    candidates = [
        a
        for a in enriched
        if 1 <= _rank_int(a) <= GLANCE_SEARCH_MAX_RANK
        and aspect_angle(str(a.get("aspect") or "")) is not None
    ]
    candidates.sort(key=_rank_int)
    if not candidates or not natal_chart:
        return [], enriched

    start, end = local_day_bounds(local_date, timezone_name)
    try:
        samples = await sample_sky_longitudes(
            astro_service,
            start=start,
            end=end,
            step_minutes=SAMPLE_STEP_MINUTES,
            coordinates=coordinates,
        )
    except Exception:
        logger.exception("glance_sky_sample_failed date=%s", local_date.isoformat())
        return [], enriched

    timed_count = 0
    for act in candidates:
        if timed_count >= MAX_GLANCE_ROWS:
            break
        natal_lon = natal_longitude_from_chart(natal_chart, str(act.get("natal_point") or ""))
        if natal_lon is None:
            continue
        try:
            exact = await find_exact_time_for_activation(
                astro_service,
                activation=act,
                natal_lon=natal_lon,
                samples=samples,
                coordinates=coordinates,
            )
        except Exception:
            logger.exception("glance_exact_failed id=%s", act.get("id"))
            exact = None
        if exact is None:
            continue
        # Store timezone-aware ISO for FE
        act["exact_time_local"] = exact.isoformat(timespec="minutes")
        timed_count += 1

    return build_glance_timeline_rows(enriched), enriched
