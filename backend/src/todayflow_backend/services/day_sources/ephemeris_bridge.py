"""Swiss / AstroService ephemeris bridge for day_sources (canon deepenings).

Day Source adapters stay sync. Async AstroService snapshots are fetched upstream
(celestial_events / morning ritual) and injected as `ephemeris` on inputs.

Fallback: soft mean longitudes in classical_longitudes.py.
"""

from __future__ import annotations

from datetime import date, time
from typing import Any, Protocol

from todayflow_backend.services.day_sources.classical_longitudes import (
    classical_bodies,
    classical_longitude,
)

_BODY_ALIASES: dict[str, str] = {
    "sun": "Sun",
    "moon": "Moon",
    "mercury": "Mercury",
    "venus": "Venus",
    "mars": "Mars",
    "jupiter": "Jupiter",
    "saturn": "Saturn",
    "uranus": "Uranus",
    "neptune": "Neptune",
    "pluto": "Pluto",
    "earth": "Earth",
    "true node": "NorthNode",
    "true_node": "NorthNode",
    "mean node": "NorthNode",
    "northnode": "NorthNode",
    "north node": "NorthNode",
    "southnode": "SouthNode",
    "south node": "SouthNode",
}

_CANON_BODIES = set(classical_bodies()) | {"Earth", "NorthNode", "SouthNode"}


def _canon_body(name: str) -> str | None:
    raw = str(name or "").strip()
    if not raw:
        return None
    if raw in _CANON_BODIES:
        return raw
    key = raw.lower().replace("_", " ")
    if key in _BODY_ALIASES:
        return _BODY_ALIASES[key]
    compact = key.replace(" ", "")
    return _BODY_ALIASES.get(compact)


def normalize_positions(positions: list[Any] | None) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for pos in positions or []:
        if not isinstance(pos, dict):
            continue
        body = _canon_body(str(pos.get("body") or pos.get("planet") or ""))
        lon = pos.get("longitude")
        if not body or not isinstance(lon, (int, float)):
            continue
        out[body] = {
            "body": body,
            "longitude": float(lon) % 360.0,
            "sign": pos.get("sign"),
            "degree": pos.get("degree") or pos.get("degree_in_sign"),
            "retrograde": bool(pos.get("retrograde") or pos.get("is_retrograde")),
        }
    # Soft Earth opposite Sun when Swiss chart has Sun but not Earth.
    if "Sun" in out and "Earth" not in out:
        sun_lon = float(out["Sun"]["longitude"])
        out["Earth"] = {
            "body": "Earth",
            "longitude": (sun_lon + 180.0) % 360.0,
            "sign": None,
            "degree": None,
            "retrograde": False,
            "derived_from": "sun_opposition",
        }
    return out


def snapshot_from_positions(
    positions: list[Any] | None,
    *,
    as_of: date,
    role: str,
    source: str = "astro_service_swiss",
    houses: dict[str, Any] | None = None,
) -> dict[str, Any]:
    bodies = normalize_positions(positions)
    return {
        "role": role,
        "source": source,
        "as_of": as_of.isoformat(),
        "body_count": len(bodies),
        "bodies": bodies,
        "houses": houses if isinstance(houses, dict) else None,
    }


def empty_ephemeris_pack() -> dict[str, Any]:
    return {
        "contract_version": "ephemeris_bridge_v0",
        "transit_noon": None,
        "natal": None,
    }


class _ChartClient(Protocol):
    async def compute_chart(
        self, birth_payload: dict, coordinates: dict | None = None
    ) -> Any: ...


def longitude_from_snapshot(snapshot: dict[str, Any] | None, body: str) -> float | None:
    if not isinstance(snapshot, dict):
        return None
    bodies = snapshot.get("bodies")
    if not isinstance(bodies, dict):
        return None
    canon = _canon_body(body) or body
    row = bodies.get(canon)
    if isinstance(row, dict) and isinstance(row.get("longitude"), (int, float)):
        return float(row["longitude"]) % 360.0
    return None


def resolve_body_longitude(
    body: str,
    d: date,
    *,
    ephemeris: dict[str, Any] | None = None,
    role: str = "transit",
) -> dict[str, Any]:
    """Prefer Swiss snapshot for role; else soft mean longitude."""
    snap = None
    if isinstance(ephemeris, dict):
        if role == "natal":
            snap = ephemeris.get("natal")
        else:
            snap = ephemeris.get("transit_noon")
    lon = longitude_from_snapshot(snap if isinstance(snap, dict) else None, body)
    if lon is not None:
        return {
            "longitude": lon,
            "source": str((snap or {}).get("source") or "astro_service_swiss"),
            "role": role,
            "body": _canon_body(body) or body,
        }
    # Earth soft opposite Sun (mean).
    if body == "Earth" or _canon_body(body) == "Earth":
        sun = classical_longitude("Sun", d)
        return {
            "longitude": (sun + 180.0) % 360.0,
            "source": "mean_longitude_soft",
            "role": role,
            "body": "Earth",
            "derived_from": "sun_opposition",
        }
    return {
        "longitude": classical_longitude(body, d),
        "source": "mean_longitude_soft",
        "role": role,
        "body": _canon_body(body) or body,
    }


async def fetch_noon_snapshot(
    astro_service: _ChartClient,
    target_date: date,
    *,
    lat: float = 0.0,
    lon: float = 0.0,
) -> dict[str, Any] | None:
    try:
        chart = await astro_service.compute_chart(
            birth_payload={
                "date": target_date.isoformat(),
                "time": "12:00:00",
                "location": "Equator" if lat == 0.0 and lon == 0.0 else f"{lat},{lon}",
            },
            coordinates={"latitude": float(lat), "longitude": float(lon)},
        )
    except Exception:
        return None
    positions = getattr(chart, "positions", None) or []
    houses = getattr(chart, "houses", None)
    return snapshot_from_positions(
        list(positions),
        as_of=target_date,
        role="transit_noon",
        houses=houses if isinstance(houses, dict) else None,
    )


async def fetch_natal_snapshot(
    astro_service: _ChartClient,
    birth_date: date,
    *,
    birth_time: time | None = None,
    birth_lat: float | None = None,
    birth_lon: float | None = None,
    timezone_name: str | None = None,
) -> dict[str, Any] | None:
    clock = birth_time or time(12, 0)
    lat = float(birth_lat) if birth_lat is not None else 0.0
    lon = float(birth_lon) if birth_lon is not None else 0.0
    birth_payload: dict[str, Any] = {
        "date": birth_date.isoformat(),
        "time": clock.strftime("%H:%M:%S"),
        "location": f"{lat},{lon}",
    }
    if timezone_name:
        birth_payload["timezone_name"] = timezone_name
    try:
        chart = await astro_service.compute_chart(
            birth_payload=birth_payload,
            coordinates={"latitude": lat, "longitude": lon},
        )
    except Exception:
        return None
    positions = getattr(chart, "positions", None) or []
    houses = getattr(chart, "houses", None)
    return snapshot_from_positions(
        list(positions),
        as_of=birth_date,
        role="natal",
        houses=houses if isinstance(houses, dict) else None,
    )


def ephemeris_from_celestial(celestial_events: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(celestial_events, dict):
        return None
    pack = celestial_events.get("ephemeris")
    return pack if isinstance(pack, dict) else None
