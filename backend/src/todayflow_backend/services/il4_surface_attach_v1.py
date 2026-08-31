"""Attach IL-4 expression packs to product LLM inputs (Today / Profile / Compatibility).

Not meaning SoT. Not public JSON. Not Swiss inside the attach gateway.
SoT: docs/astrology/IL4_SURFACE_ATTACH_V1.md
"""

from __future__ import annotations

from typing import Any, Mapping

from todayflow_backend.knowledge.calc_il_wire_v1 import PLANET_BODIES, wire_calc_to_il
from todayflow_backend.knowledge.il4_expression_v1 import ExpressionPack, SURFACES
from todayflow_backend.services.il4_selection_v1 import select_themes

_BODY_ALIASES: dict[str, str] = {
    "sun": "sun",
    "moon": "moon",
    "mercury": "mercury",
    "venus": "venus",
    "mars": "mars",
    "jupiter": "jupiter",
    "saturn": "saturn",
    "uranus": "uranus",
    "neptune": "neptune",
    "pluto": "pluto",
    "ascendant": "rising",
    "asc": "rising",
    "rising": "rising",
}


def _normalize_body(raw: Any) -> str | None:
    token = str(raw or "").strip().lower().replace(" ", "_")
    if not token:
        return None
    mapped = _BODY_ALIASES.get(token)
    if mapped:
        return mapped
    if token in PLANET_BODIES or token == "rising":
        return token
    return None


def _normalize_position_row(row: Mapping[str, Any]) -> dict[str, Any]:
    body = _normalize_body(row.get("body") or row.get("planet") or row.get("name"))
    out: dict[str, Any] = dict(row)
    if body:
        out["body"] = body
    return out


def _normalize_houses(houses: Mapping[str, Any] | None) -> dict[str, Any]:
    if not isinstance(houses, Mapping):
        return {}
    out: dict[str, Any] = {}
    for key, entry in houses.items():
        if isinstance(entry, (int, float)):
            out[str(key)] = {"longitude": float(entry) % 360.0}
            continue
        if not isinstance(entry, Mapping):
            continue
        row = dict(entry)
        if row.get("longitude") is None and row.get("cusp") is not None:
            row["longitude"] = row["cusp"]
        out[str(key)] = row
    return out


def chart_input_from_ephemeris_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any] | None:
    if isinstance(snapshot.get("positions"), list):
        positions = [
            _normalize_position_row(row)
            for row in snapshot["positions"]
            if isinstance(row, Mapping)
        ]
        if not positions:
            return None
        return {
            "positions": positions,
            "houses": _normalize_houses(snapshot.get("houses") if isinstance(snapshot.get("houses"), Mapping) else {}),
        }
    bodies = snapshot.get("bodies")
    if not isinstance(bodies, Mapping) or not bodies:
        return None
    positions: list[dict[str, Any]] = []
    for _name, row in bodies.items():
        if not isinstance(row, Mapping):
            continue
        body = _normalize_body(row.get("body") or _name)
        if body not in PLANET_BODIES and body != "rising":
            continue
        longitude = row.get("longitude")
        if not isinstance(longitude, (int, float)):
            continue
        positions.append(
            {
                "body": body,
                "sign": row.get("sign"),
                "longitude": float(longitude) % 360.0,
                "degree": row.get("degree"),
                "house": row.get("house"),
            }
        )
    if not positions:
        return None
    houses = snapshot.get("houses") if isinstance(snapshot.get("houses"), Mapping) else {}
    return {"positions": positions, "houses": _normalize_houses(houses)}


def chart_input_from_any(raw: Any) -> dict[str, Any] | None:
    if raw is None:
        return None
    if hasattr(raw, "model_dump"):
        raw = raw.model_dump()
    if not isinstance(raw, Mapping):
        return None
    if isinstance(raw.get("bodies"), Mapping):
        return chart_input_from_ephemeris_snapshot(raw)
    positions = raw.get("positions")
    if isinstance(positions, list) and positions:
        normalized = [
            _normalize_position_row(row) for row in positions if isinstance(row, Mapping)
        ]
        if not normalized:
            return None
        houses = raw.get("houses") if isinstance(raw.get("houses"), Mapping) else {}
        return {"positions": normalized, "houses": _normalize_houses(houses)}
    return None


def expression_pack_to_dict(pack: ExpressionPack) -> dict[str, Any]:
    return {
        "surface": pack.surface,
        "tone": pack.tone,
        "meaning_source": pack.meaning_source,
        "lines": [
            {
                "rank": line.rank,
                "band": line.band,
                "role": line.role,
                "construction": line.construction,
                "jobs": {name: list(lemmas) for name, lemmas in line.jobs.items()},
                "subject_jobs": list(line.subject_jobs),
                "modifier_jobs": list(line.modifier_jobs),
                "text": line.text,
            }
            for line in pack.lines
        ],
        "dropped": [
            {
                "construction": frame.construction,
                "status": frame.status,
                "reason": frame.reason,
            }
            for frame in pack.dropped
        ],
    }


def attach_il4_expression_pack(
    *,
    surface: str,
    natal: Any,
    transit: Any | None = None,
) -> dict[str, Any] | None:
    """Resolve charts → IL-4 pack dict for LLM input. Returns None when geometry is missing."""
    if surface not in SURFACES:
        return None
    natal_chart = chart_input_from_any(natal)
    if natal_chart is None:
        return None
    transit_chart = chart_input_from_any(transit) if transit is not None else None
    pack = wire_calc_to_il(natal_chart, transit=transit_chart, surface=surface)
    if not pack.lines and not pack.dropped:
        return None
    pack_dict = expression_pack_to_dict(pack)
    selected = select_themes(pack_dict, surface=surface)
    return selected if selected is not None else pack_dict


def attach_from_celestial_ephemeris(
    celestial_events: Mapping[str, Any] | None,
    *,
    surface: str = "today",
) -> dict[str, Any] | None:
    from todayflow_backend.services.day_sources.ephemeris_bridge import ephemeris_from_celestial

    pack = ephemeris_from_celestial(celestial_events)
    if not isinstance(pack, Mapping):
        return None
    natal = pack.get("natal")
    if not isinstance(natal, Mapping):
        return None
    transit = pack.get("transit_noon") if isinstance(pack.get("transit_noon"), Mapping) else None
    return attach_il4_expression_pack(surface=surface, natal=natal, transit=transit)


def attach_from_profile_input(
    profile_input: Mapping[str, Any],
    *,
    surface: str = "profile",
) -> dict[str, Any] | None:
    natal = profile_input.get("natal")
    if isinstance(natal, Mapping):
        attached = attach_il4_expression_pack(surface=surface, natal=natal)
        if attached is not None:
            return attached
    positions = profile_input.get("positions")
    if isinstance(positions, list):
        houses = profile_input.get("houses") if isinstance(profile_input.get("houses"), Mapping) else {}
        return attach_il4_expression_pack(
            surface=surface,
            natal={"positions": positions, "houses": houses},
        )
    return None


def attach_from_chart_pair(
    chart1: Any,
    chart2: Any | None = None,
    *,
    surface: str = "compatibility",
) -> dict[str, Any] | None:
    """Partner chart is modeled as transit-to-natal geometry (wire transit_to_natal band)."""
    return attach_il4_expression_pack(surface=surface, natal=chart1, transit=chart2)
