"""Calc → IL wire — ChartResponse-shaped snapshots to IL-4 packs.

Library layer only. Not Swiss. Not Today prompts. Not public JSON. Not `active`.
SoT: docs/astrology/CALC_IL_WIRE_V1.md
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from todayflow_backend.knowledge.il2_composition_v1 import load_objects
from todayflow_backend.knowledge.il3_interpretation_v1 import SkyFact, interpret
from todayflow_backend.knowledge.il4_expression_v1 import ExpressionPack, express

PLANET_BODIES = (
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
)

SKIP_BODIES = frozenset(
    {
        "rising",
        "north_node",
        "south_node",
        "chiron",
        "lilith",
        "dsc",
        "ic",
    }
)

SIGNS = (
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
)

# Foundation v1 majors only. Angle orb = conjunction orb (geometry, not a cookbook).
MAJOR_ASPECTS = (
    ("conjunction", 0.0, 8.0),
    ("sextile", 60.0, 4.0),
    ("square", 90.0, 6.0),
    ("trine", 120.0, 6.0),
    ("opposition", 180.0, 8.0),
)
ANGLE_ORB = 8.0


def _get(obj: Any, *keys: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, Mapping):
        for key in keys:
            if key in obj and obj[key] is not None:
                return obj[key]
        return default
    for key in keys:
        if hasattr(obj, key):
            value = getattr(obj, key)
            if value is not None:
                return value
    return default


def _positions(chart: Any) -> list[Any]:
    raw = _get(chart, "positions", "positions", default=[]) or []
    return list(raw)


def _houses(chart: Any) -> Mapping[Any, Any]:
    raw = _get(chart, "houses", default={}) or {}
    return raw if isinstance(raw, Mapping) else {}


def _float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _norm_lon(value: float) -> float:
    return value % 360.0


def _sep(a: float, b: float) -> float:
    delta = abs(_norm_lon(a) - _norm_lon(b)) % 360.0
    return min(delta, 360.0 - delta)


def _planet_id(body: str) -> str:
    return f"astro.object.{body}"


def _sign_id(sign: Any) -> str | None:
    if not sign:
        return None
    token = str(sign).strip().lower().replace("astro.sign.", "")
    if token not in SIGNS:
        return None
    return f"astro.sign.{token}"


def _house_id(number: Any) -> str | None:
    try:
        n = int(number)
    except (TypeError, ValueError):
        return None
    if n < 1 or n > 12:
        return None
    return f"astro.house.{n:02d}"


def _aspect_id(name: str) -> str:
    return f"astro.aspect.{name}"


def _house_lon(houses: Mapping[Any, Any], number: int) -> float | None:
    keys = (
        f"house_{number}",
        f"house_{number:02d}",
        str(number),
        number,
    )
    for key in keys:
        if key not in houses:
            continue
        entry = houses[key]
        lon = _float(_get(entry, "longitude") if not isinstance(entry, (int, float)) else entry)
        if lon is not None:
            return _norm_lon(lon)
    return None


def _cusps(houses: Mapping[Any, Any]) -> list[float] | None:
    values = [_house_lon(houses, i) for i in range(1, 13)]
    if any(v is None for v in values):
        return None
    return [v for v in values if v is not None]


def _house_for_longitude(longitude: float, cusps: Sequence[float]) -> int:
    point = _norm_lon(longitude)
    for house in range(12):
        start = _norm_lon(cusps[house])
        end = _norm_lon(cusps[(house + 1) % 12])
        if start <= end:
            if start <= point < end:
                return house + 1
        elif point >= start or point < end:
            return house + 1
    return 12


def _aspect_name(sep: float) -> str | None:
    hits: list[tuple[float, str]] = []
    for name, angle, orb in MAJOR_ASPECTS:
        residual = abs(sep - angle)
        if residual <= orb:
            hits.append((residual, name))
    if not hits:
        return None
    hits.sort()
    return hits[0][1]


def _body_name(position: Any) -> str:
    return str(_get(position, "body", "body", default="") or "").strip().lower()


def _indexed_planets(chart: Any) -> list[tuple[str, Any]]:
    out: list[tuple[str, Any]] = []
    seen: set[str] = set()
    for position in _positions(chart):
        body = _body_name(position)
        if body not in PLANET_BODIES or body in seen:
            continue
        seen.add(body)
        out.append((body, position))
    order = {name: index for index, name in enumerate(PLANET_BODIES)}
    out.sort(key=lambda item: order[item[0]])
    return out


def _rising_lon(chart: Any) -> float | None:
    for position in _positions(chart):
        if _body_name(position) == "rising":
            return _float(_get(position, "longitude"))
    return None


def _mc_lon(chart: Any) -> float | None:
    return _house_lon(_houses(chart), 10)


def _natal_facts(chart: Any) -> list[SkyFact]:
    facts: list[SkyFact] = []
    rising = _rising_lon(chart)
    mc = _mc_lon(chart)
    planets = _indexed_planets(chart)
    for body, position in planets:
        planet_id = _planet_id(body)
        sign_id = _sign_id(_get(position, "sign"))
        if sign_id:
            facts.append(SkyFact("planet_in_sign", (planet_id, sign_id)))
        house_id = _house_id(_get(position, "house"))
        if house_id:
            facts.append(SkyFact("planet_in_house", (planet_id, house_id)))
        longitude = _float(_get(position, "longitude"))
        if longitude is None:
            continue
        if rising is not None and _sep(longitude, rising) <= ANGLE_ORB:
            facts.append(SkyFact("planet_at_angle", (planet_id, "astro.object.asc")))
        if mc is not None and _sep(longitude, mc) <= ANGLE_ORB:
            facts.append(SkyFact("planet_at_angle", (planet_id, "astro.object.mc")))
    for i, (body_a, pos_a) in enumerate(planets):
        lon_a = _float(_get(pos_a, "longitude"))
        if lon_a is None:
            continue
        for body_b, pos_b in planets[i + 1 :]:
            lon_b = _float(_get(pos_b, "longitude"))
            if lon_b is None:
                continue
            name = _aspect_name(_sep(lon_a, lon_b))
            if name:
                facts.append(
                    SkyFact(
                        "aspect_pair",
                        (_planet_id(body_a), _planet_id(body_b), _aspect_id(name)),
                    )
                )
    return facts


def _transit_facts(natal: Any, transit: Any) -> list[SkyFact]:
    facts: list[SkyFact] = []
    natal_planets = _indexed_planets(natal)
    natal_lons = {
        body: _float(_get(position, "longitude")) for body, position in natal_planets
    }
    cusps = _cusps(_houses(natal))
    for body, position in _indexed_planets(transit):
        planet_id = _planet_id(body)
        longitude = _float(_get(position, "longitude"))
        if longitude is None:
            continue
        for natal_body, natal_lon in natal_lons.items():
            if natal_lon is None:
                continue
            name = _aspect_name(_sep(longitude, natal_lon))
            if name:
                facts.append(
                    SkyFact(
                        "transit_to_natal",
                        (planet_id, _planet_id(natal_body), _aspect_id(name)),
                    )
                )
        if cusps is not None:
            house_id = _house_id(_house_for_longitude(longitude, cusps))
            if house_id:
                facts.append(SkyFact("transit_through_house", (planet_id, house_id)))
    return facts


def skyfacts_from_calc(natal: Any, transit: Any | None = None) -> tuple[SkyFact, ...]:
    """Emit IL-3 SkyFacts. Occupancy is not conjunction; house 1/10 is not ASC/MC."""
    facts: list[SkyFact] = []
    if transit is not None:
        facts.extend(_transit_facts(natal, transit))
    facts.extend(_natal_facts(natal))
    return tuple(facts)


def wire_calc_to_il(
    natal: Any,
    *,
    transit: Any | None = None,
    surface: str = "today",
    catalog: Mapping[str, dict] | None = None,
) -> ExpressionPack:
    """IL-2 compose → IL-3 interpret → IL-4 express. Draft catalog is consumed as-is."""
    loaded = catalog or load_objects()
    themes = interpret(loaded, skyfacts_from_calc(natal, transit))
    return express(themes, surface)
