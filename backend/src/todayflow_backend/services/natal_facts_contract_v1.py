"""natal_facts Generation Contract — deterministic chart facts (MVP).

Natal facts are calculated from the Swiss Ephemeris-backed astro service, not
inferred by an LLM. When the service is unavailable or birth data is
insufficient, the contract falls back to an honest, bounded subset (e.g. sun-only
for date-only mode).
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import date, time
from typing import Any

from todayflow_backend.services.astro import ChartResponse, compute_chart_sync

logger = logging.getLogger(__name__)

NATAL_FACTS_CONTRACT = "natal_facts_v1"
PROMPT_ID = "profile.natal_facts.v1"
VALID_SIGNS = frozenset(
    {
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
    }
)


def resolve_natal_facts_mode(
    *,
    birth_time: time | str | None,
    time_unknown: bool,
    latitude: float | None,
    longitude: float | None,
    birth_date: date | str | None = None,
) -> str:
    """Delegate to Capability Resolver (Availability Matrix)."""
    from todayflow_backend.services.capability_resolver_v0 import resolve_natal_mode

    if birth_date is None:
        # Legacy callers only need angles eligibility (date already validated upstream).
        if time_unknown or not birth_time or latitude is None or longitude is None:
            return "date_only"
        return "full"
    mode = resolve_natal_mode(
        birth_date=birth_date,
        birth_time=birth_time,
        time_unknown=time_unknown,
        latitude=latitude,
        longitude=longitude,
    )
    if mode == "full":
        return "full"
    return "date_only"


def sun_sign_from_date(birth: date) -> str:
    """Tropical sun sign approx — parity with frontend sunSignFromIsoDate (lowercase)."""
    month, day = birth.month, birth.day
    if (month == 3 and day >= 21) or (month == 4 and day < 20):
        return "aries"
    if (month == 4 and day >= 20) or (month == 5 and day < 21):
        return "taurus"
    if (month == 5 and day >= 21) or (month == 6 and day < 21):
        return "gemini"
    if (month == 6 and day >= 21) or (month == 7 and day < 23):
        return "cancer"
    if (month == 7 and day >= 23) or (month == 8 and day < 23):
        return "leo"
    if (month == 8 and day >= 23) or (month == 9 and day < 23):
        return "virgo"
    if (month == 9 and day >= 23) or (month == 10 and day < 23):
        return "libra"
    if (month == 10 and day >= 23) or (month == 11 and day < 22):
        return "scorpio"
    if (month == 11 and day >= 22) or (month == 12 and day < 22):
        return "sagittarius"
    if (month == 12 and day >= 22) or (month == 1 and day < 20):
        return "capricorn"
    if (month == 1 and day >= 20) or (month == 2 and day < 19):
        return "aquarius"
    return "pisces"


def _normalize_sign(raw: Any) -> str | None:
    if raw is None:
        return None
    s = str(raw).strip().lower()
    aliases = {
        "овен": "aries",
        "телец": "taurus",
        "близнецы": "gemini",
        "рак": "cancer",
        "лев": "leo",
        "дева": "virgo",
        "весы": "libra",
        "скорпион": "scorpio",
        "стрелец": "sagittarius",
        "козерог": "capricorn",
        "водолей": "aquarius",
        "рыбы": "pisces",
    }
    s = aliases.get(s, s)
    return s if s in VALID_SIGNS else None


def _parse_json_object(raw: str) -> dict[str, Any] | None:
    text = (raw or "").strip()
    if not text:
        return None
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None


def _angle_or_none(raw: Any, *, allow: bool) -> dict[str, Any] | None:
    if not allow or not isinstance(raw, dict):
        return None
    sign = _normalize_sign(raw.get("sign"))
    if not sign:
        return None
    try:
        degree = float(raw.get("degree", 0))
        abs_lon = float(raw.get("absolute_longitude", degree))
    except (TypeError, ValueError):
        return None
    return {"sign": sign, "degree": degree, "absolute_longitude": abs_lon}


def validate_natal_facts(
    payload: dict[str, Any],
    *,
    expected_mode: str,
    structure_unavailable_reason: str | None = None,
) -> dict[str, Any]:
    """Normalize and enforce Execution Rules (no ASC/houses without full mode)."""
    mode = expected_mode if expected_mode in ("date_only", "full") else "date_only"
    allow_angles = mode == "full"

    planets_out: list[dict[str, Any]] = []
    for item in payload.get("planets") or []:
        if not isinstance(item, dict):
            continue
        pid = str(item.get("id") or "").strip().lower()
        sign = _normalize_sign(item.get("sign"))
        if not pid or not sign:
            continue
        entry: dict[str, Any] = {"id": pid, "sign": sign}
        for key in ("degree", "absolute_longitude"):
            try:
                if item.get(key) is not None:
                    entry[key] = float(item[key])
            except (TypeError, ValueError):
                pass
        if allow_angles and item.get("house") is not None:
            try:
                house = int(item["house"])
                if 1 <= house <= 12:
                    entry["house"] = house
            except (TypeError, ValueError):
                pass
        if item.get("retrograde") is not None:
            entry["retrograde"] = bool(item["retrograde"])
        planets_out.append(entry)

    angles_in = payload.get("angles") if isinstance(payload.get("angles"), dict) else {}
    angles = {
        "ascendant": _angle_or_none(angles_in.get("ascendant"), allow=allow_angles),
        "mc": _angle_or_none(angles_in.get("mc"), allow=allow_angles),
        "ic": _angle_or_none(angles_in.get("ic"), allow=allow_angles),
        "descendant": _angle_or_none(angles_in.get("descendant"), allow=allow_angles),
    }

    houses_out: list[dict[str, Any]] = []
    if allow_angles:
        for item in payload.get("houses") or []:
            if not isinstance(item, dict):
                continue
            sign = _normalize_sign(item.get("sign"))
            try:
                house = int(item.get("house"))
            except (TypeError, ValueError):
                continue
            if not sign or not (1 <= house <= 12):
                continue
            row: dict[str, Any] = {"house": house, "sign": sign}
            for key in ("degree", "absolute_longitude"):
                try:
                    if item.get(key) is not None:
                        row[key] = float(item[key])
                except (TypeError, ValueError):
                    pass
            houses_out.append(row)

    unavailable: list[dict[str, str]] = []
    for item in payload.get("unavailable_facts") or []:
        if isinstance(item, dict) and item.get("key"):
            unavailable.append(
                {"key": str(item["key"]), "reason": str(item.get("reason") or "unavailable")}
            )

    if not allow_angles:
        reason = structure_unavailable_reason or "birth_time_or_place_missing"
        for key in ("ascendant", "mc", "ic", "descendant", "houses"):
            if not any(u["key"] == key for u in unavailable):
                unavailable.append({"key": key, "reason": reason})
            else:
                # Prefer precise resolver reason over generic LLM wording.
                for u in unavailable:
                    if u["key"] == key and reason != "birth_time_or_place_missing":
                        u["reason"] = reason

    calc_id = str(payload.get("calculation_id") or "").strip()
    if not calc_id:
        calc_id = hashlib.sha256(json.dumps(planets_out, sort_keys=True).encode()).hexdigest()[:16]

    confidence = payload.get("confidence")
    try:
        confidence_f = max(0.0, min(1.0, float(confidence))) if confidence is not None else (0.55 if mode == "full" else 0.4)
    except (TypeError, ValueError):
        confidence_f = 0.4

    return {
        "contract_version": NATAL_FACTS_CONTRACT,
        "provider": str(payload.get("provider") or "deepseek"),
        "provider_version": str(payload.get("provider_version") or "v4-pro"),
        "calculation_id": calc_id,
        "house_system": (str(payload.get("house_system")) if allow_angles and payload.get("house_system") else None),
        "zodiac": "tropical",
        "mode": mode,
        "confidence": confidence_f,
        "planets": planets_out,
        "angles": angles,
        "houses": houses_out,
        "aspects": payload.get("aspects") if isinstance(payload.get("aspects"), list) else [],
        "unavailable_facts": unavailable,
    }


def _structure_reason_from_capability(capability: dict[str, Any] | None) -> str | None:
    if not capability:
        return None
    for u in capability.get("unavailable_facts") or []:
        if isinstance(u, dict) and u.get("key") == "ascendant":
            return str(u.get("reason") or "") or None
    return None


def date_only_fallback(
    birth: date,
    *,
    structure_unavailable_reason: str | None = None,
) -> dict[str, Any]:
    sun = sun_sign_from_date(birth)
    reason = structure_unavailable_reason or "birth_time_or_place_missing"
    return validate_natal_facts(
        {
            "provider": "deterministic_fallback",
            "provider_version": "sun_from_date_v1",
            "mode": "date_only",
            "confidence": 0.35,
            "planets": [{"id": "sun", "sign": sun, "degree": 15.0}],
            "angles": {},
            "houses": [],
            "aspects": [],
            "unavailable_facts": [
                {"key": "moon", "reason": "requires_llm_or_time"},
                {"key": "ascendant", "reason": reason},
                {"key": "houses", "reason": reason},
            ],
        },
        expected_mode="date_only",
        structure_unavailable_reason=reason,
    )


def _infer_sign_from_longitude(longitude: Any) -> str | None:
    try:
        lon = float(longitude) % 360.0
    except (TypeError, ValueError):
        return None
    zodiac = (
        "aries", "taurus", "gemini", "cancer", "leo", "virgo",
        "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
    )
    return zodiac[int(lon // 30) % 12]


def _body_id(name: str | None) -> str | None:
    if not name:
        return None
    raw = str(name).strip().lower().replace(" ", "_")
    aliases: dict[str, str] = {
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
        "north_node": "north_node",
        "south_node": "south_node",
        "chiron": "chiron",
        "lilith": "lilith",
    }
    return aliases.get(raw)


_ANGLE_ALIASES: dict[str, tuple[str, ...]] = {
    "ascendant": ("1", "asc", "ascendant", "rising"),
    "mc": ("10", "mc", "midheaven"),
    "ic": ("4", "ic"),
    "descendant": ("7", "dsc", "descendant"),
}


def _angle_from_chart(houses: dict[str, Any], aliases: tuple[str, ...]) -> dict[str, Any] | None:
    raw: Any = None
    for key in aliases:
        if key in houses:
            raw = houses[key]
            break
        if isinstance(key, str) and key.lower() in {k.lower() for k in houses}:
            for k in houses:
                if k.lower() == key.lower():
                    raw = houses[k]
                    break
        if raw is not None:
            break
    if not isinstance(raw, dict):
        return None
    sign = _normalize_sign(raw.get("sign"))
    if not sign:
        sign = _infer_sign_from_longitude(raw.get("longitude"))
    if not sign:
        return None
    entry: dict[str, Any] = {"sign": sign}
    try:
        if raw.get("degree") is not None:
            entry["degree"] = float(raw["degree"])
        if raw.get("longitude") is not None:
            entry["absolute_longitude"] = float(raw["longitude"])
    except (TypeError, ValueError):
        pass
    return entry


def _planet_entry_from_position(pos: dict[str, Any], *, allow_houses: bool) -> dict[str, Any] | None:
    pid = _body_id(pos.get("body") or pos.get("name") or pos.get("planet"))
    if not pid:
        return None
    sign = _normalize_sign(pos.get("sign"))
    if not sign:
        sign = _infer_sign_from_longitude(pos.get("longitude"))
    if not sign:
        return None
    entry: dict[str, Any] = {"id": pid, "sign": sign}
    try:
        if pos.get("degree") is not None:
            entry["degree"] = float(pos["degree"])
        if pos.get("longitude") is not None:
            entry["absolute_longitude"] = float(pos["longitude"])
    except (TypeError, ValueError):
        pass
    if "degree" not in entry and "absolute_longitude" in entry:
        entry["degree"] = entry["absolute_longitude"] % 30.0
    if allow_houses and pos.get("house") is not None:
        try:
            house = int(pos["house"])
            if 1 <= house <= 12:
                entry["house"] = house
        except (TypeError, ValueError):
            pass
    if pos.get("retrograde") is not None:
        entry["retrograde"] = bool(pos["retrograde"])
    return entry


def _house_entries_from_chart(houses: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for key, raw in houses.items():
        if not isinstance(raw, dict):
            continue
        try:
            house_num = int(key)
        except (TypeError, ValueError):
            continue
        if not 1 <= house_num <= 12:
            continue
        sign = _normalize_sign(raw.get("sign"))
        if not sign:
            sign = _infer_sign_from_longitude(raw.get("longitude"))
        if not sign:
            continue
        entry: dict[str, Any] = {"house": house_num, "sign": sign}
        try:
            if raw.get("degree") is not None:
                entry["degree"] = float(raw["degree"])
            if raw.get("longitude") is not None:
                entry["absolute_longitude"] = float(raw["longitude"])
        except (TypeError, ValueError):
            pass
        if "degree" not in entry and "absolute_longitude" in entry:
            entry["degree"] = entry["absolute_longitude"] % 30.0
        out.append(entry)
    return out


def _build_birth_payload_for_chart(available_input: dict[str, Any]) -> dict[str, Any]:
    """Map capability-resolver available_input to astro-service /chart birth payload."""
    birth: dict[str, Any] = {"date": str(available_input.get("birth_date") or "")}
    time_str = available_input.get("birth_time")
    if time_str:
        birth["time"] = str(time_str)
    location = available_input.get("location_name")
    if location:
        birth["location"] = str(location)
    tz = available_input.get("timezone_name")
    if tz:
        birth["timezone_name"] = str(tz)
    tz_offset = available_input.get("timezone_offset_minutes")
    if tz_offset is not None:
        try:
            birth["timezone_offset_minutes"] = int(tz_offset)
        except (TypeError, ValueError):
            pass
    return birth


def build_natal_facts_from_chart(
    chart: ChartResponse | dict[str, Any],
    *,
    mode: str,
    provider: str = "astro_service",
    provider_version: str = "1.0",
    unavailable_reason: str | None = None,
) -> dict[str, Any]:
    """Convert a Swiss Ephemeris-backed chart into the natal_facts contract.

    ``mode`` is the capability-resolver mode (``date_only`` or ``full``). The
    chart may contain more geometry than the mode allows; the validator enforces
    the contract boundaries and adds unavailable_facts when needed.
    """
    if isinstance(chart, ChartResponse):
        positions = chart.positions
        houses = chart.houses
        metadata = chart.metadata
    else:
        positions = chart.get("positions") if isinstance(chart.get("positions"), list) else []
        houses = chart.get("houses") if isinstance(chart.get("houses"), dict) else {}
        metadata = chart.get("metadata") if isinstance(chart.get("metadata"), dict) else {}

    allow_angles = mode == "full"
    planets: list[dict[str, Any]] = []
    for pos in positions:
        if not isinstance(pos, dict):
            continue
        entry = _planet_entry_from_position(pos, allow_houses=allow_angles)
        if entry:
            planets.append(entry)

    angles: dict[str, Any] = {
        "ascendant": None,
        "mc": None,
        "ic": None,
        "descendant": None,
    }
    houses_out: list[dict[str, Any]] = []
    if allow_angles:
        houses_out = _house_entries_from_chart(houses)
        for angle_key, aliases in _ANGLE_ALIASES.items():
            angles[angle_key] = _angle_from_chart(houses, aliases)

    # Ensure sun is always present; chart service should provide it, but guard.
    if not any(p.get("id") == "sun" for p in planets):
        sun_lon = None
        for pos in positions:
            if isinstance(pos, dict) and _body_id(pos.get("body") or pos.get("name")) == "sun":
                try:
                    sun_lon = float(pos.get("longitude") or pos.get("absolute_longitude"))
                except (TypeError, ValueError):
                    pass
                break
        sun_sign = _infer_sign_from_longitude(sun_lon) if sun_lon is not None else None
        if sun_sign:
            planets.insert(0, {"id": "sun", "sign": sun_sign, "degree": 15.0})

    aspects = metadata.get("aspects") if isinstance(metadata.get("aspects"), list) else []

    unavailable: list[dict[str, str]] = []
    if not allow_angles:
        reason = unavailable_reason or "birth_time_or_place_missing"
        for key in ("ascendant", "mc", "ic", "descendant", "houses"):
            unavailable.append({"key": key, "reason": reason})

    return validate_natal_facts(
        {
            "provider": provider,
            "provider_version": provider_version,
            "mode": mode,
            "confidence": 0.92 if mode == "full" else 0.55,
            "planets": planets,
            "angles": angles,
            "houses": houses_out,
            "aspects": aspects,
            "unavailable_facts": unavailable,
        },
        expected_mode=mode,
        structure_unavailable_reason=unavailable_reason,
    )


def build_available_input(
    *,
    birth_date: date,
    birth_time: time | str | None = None,
    time_unknown: bool = True,
    location_name: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    timezone_name: str | None = None,
    display_name: str | None = None,
    access: str = "free",
) -> dict[str, Any]:
    """Build available_input via Capability Resolver (mode + honesty fields)."""
    from todayflow_backend.services.capability_resolver_v0 import resolve_capability

    cap = resolve_capability(
        birth_date=birth_date,
        birth_time=birth_time,
        time_unknown=time_unknown,
        location_name=location_name,
        latitude=latitude,
        longitude=longitude,
        timezone_name=timezone_name,
        display_name=display_name,
        access=access,  # type: ignore[arg-type]
    )
    available = dict(cap["available_input"])
    # Preserve resolver pack for callers (API / generate) without leaking into LLM payload keys.
    available["_capability"] = {
        "resolver_version": cap["resolver_version"],
        "access": cap["access"],
        "mode": cap["mode"],
        "has_name": cap["has_name"],
        "has_time": cap["has_time"],
        "has_place": cap["has_place"],
        "unavailable_facts": cap["unavailable_facts"],
        "profile_slots": cap["profile_slots"],
        "layers": cap["layers"],
        "user_messages": cap["user_messages"],
    }
    return available


def generate_natal_facts(
    *,
    available_input: dict[str, Any],
    locale: str = "ru",
    capability: dict[str, Any] | None = None,
    chart_data: ChartResponse | dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return validated natal_facts from a deterministic chart source.

    Priority:
    1. ``chart_data`` if provided (e.g. cached CachedNatalChart).
    2. Synchronous call to the Swiss Ephemeris-backed astro service.
    3. Honest date-only fallback (sun sign) if the service is unavailable or
       birth data is insufficient for full angles/houses.

    ``locale`` is kept for API compatibility; no LLM call is made.
    """
    from todayflow_backend.services.capability_resolver_v0 import merge_unavailable_into_facts

    mode = str(available_input.get("mode") or "date_only")
    birth_raw = available_input.get("birth_date")
    try:
        birth = date.fromisoformat(str(birth_raw))
    except (TypeError, ValueError) as exc:
        raise ValueError("birth_date required as YYYY-MM-DD") from exc

    cap = capability or (
        available_input.get("_capability")
        if isinstance(available_input.get("_capability"), dict)
        else None
    )
    structure_reason = _structure_reason_from_capability(cap)

    def _from_chart(chart: ChartResponse | dict[str, Any]) -> dict[str, Any]:
        facts = build_natal_facts_from_chart(
            chart,
            mode=mode,
            provider="astro_service",
            provider_version="1.0",
            unavailable_reason=structure_reason,
        )
        if not any(p.get("id") == "sun" for p in facts["planets"]):
            facts["planets"].insert(0, {"id": "sun", "sign": sun_sign_from_date(birth), "degree": 15.0})
        return facts

    if chart_data is not None:
        facts = _from_chart(chart_data)
        if cap:
            facts = merge_unavailable_into_facts(facts, cap)
        return facts

    try:
        birth_payload = _build_birth_payload_for_chart(available_input)
        coordinates = None
        lat = available_input.get("latitude")
        lon = available_input.get("longitude")
        if lat is not None and lon is not None:
            coordinates = {"latitude": float(lat), "longitude": float(lon)}
        chart = compute_chart_sync(birth_payload=birth_payload, coordinates=coordinates)
        facts = _from_chart(chart)
    except Exception as exc:
        logger.warning(
            "natal_facts: chart computation failed (%s) — falling back to date_only",
            exc,
            exc_info=True,
        )
        facts = date_only_fallback(birth, structure_unavailable_reason=structure_reason)

    if cap:
        facts = merge_unavailable_into_facts(facts, cap)
    return facts


def natal_facts_to_cache_rows(facts: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    """Map NatalChartFacts → CachedNatalChart-compatible rows.

    ChartResponse.positions must be a **list** (Swiss shape). Contract facts live in
    chart_metadata.natal_facts — never overwrite Swiss positions with a dict map.
    """
    positions: list[dict[str, Any]] = []
    for p in facts.get("planets") or []:
        if not isinstance(p, dict) or not p.get("id"):
            continue
        positions.append(
            {
                "name": str(p["id"]).capitalize(),
                "sign": p.get("sign"),
                "degree": p.get("degree"),
                "longitude": p.get("absolute_longitude"),
                "house": p.get("house"),
                "retrograde": p.get("retrograde"),
                "source": "natal_facts",
            }
        )
    houses: dict[str, Any] = {}
    angles = facts.get("angles") if isinstance(facts.get("angles"), dict) else {}
    for key, alias in (("ascendant", "Asc"), ("mc", "MC"), ("ic", "IC"), ("descendant", "DSC")):
        ang = angles.get(key)
        if isinstance(ang, dict):
            houses[alias] = ang
    for h in facts.get("houses") or []:
        if isinstance(h, dict) and h.get("house") is not None:
            houses[str(h["house"])] = h
    capability = facts.get("capability") if isinstance(facts.get("capability"), dict) else None
    meta = {
        "source": "natal_facts_contract",
        "natal_facts": facts,
        "mode": facts.get("mode"),
        "provider": facts.get("provider"),
        "calculation_id": facts.get("calculation_id"),
        "provenance": {
            "contract_version": facts.get("contract_version"),
            "provider": facts.get("provider"),
            "provider_version": facts.get("provider_version"),
            "prompt_id": facts.get("prompt_id"),
            "prompt_version": facts.get("prompt_version"),
            "calculation_id": facts.get("calculation_id"),
            "resolver_version": (capability or {}).get("resolver_version"),
            "access": (capability or {}).get("access"),
        },
        "capability": capability,
    }
    return positions, houses, meta


def persist_natal_facts_on_profile(db: Any, astro_profile_id: int, facts: dict[str, Any]) -> None:
    from todayflow_backend.db import models as db_models

    positions, houses, meta = natal_facts_to_cache_rows(facts)
    row = (
        db.query(db_models.CachedNatalChart)
        .filter(db_models.CachedNatalChart.astro_profile_id == astro_profile_id)
        .first()
    )
    if row is None:
        row = db_models.CachedNatalChart(
            astro_profile_id=astro_profile_id,
            # List shape required by ChartResponse; full contract JSON in metadata.
            positions=positions or [],
            houses=houses or {},
            chart_metadata=meta,
        )
        db.add(row)
    else:
        existing_meta = dict(row.chart_metadata or {})
        existing_meta.update(meta)
        row.chart_metadata = existing_meta
        # Do not replace a richer Swiss list with a thin facts list unless empty.
        if not row.positions:
            row.positions = positions or []
        if facts.get("mode") == "full" and houses and not row.houses:
            row.houses = houses
        db.add(row)
