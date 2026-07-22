"""natal_facts Generation Contract — LLM structured chart facts (MVP).

Does not run Swiss Ephemeris in the product path. Legacy Swiss remains elsewhere.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import date, time
from typing import Any

from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_text,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_default_chat_model,
)
from todayflow_backend.prompts.registry_v1 import get_prompt

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
) -> str:
    if time_unknown or not birth_time:
        return "date_only"
    if latitude is None or longitude is None:
        return "date_only"
    return "full"


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


def validate_natal_facts(payload: dict[str, Any], *, expected_mode: str) -> dict[str, Any]:
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
        for key in ("ascendant", "mc", "ic", "descendant", "houses"):
            if not any(u["key"] == key for u in unavailable):
                unavailable.append({"key": key, "reason": "birth_time_or_place_missing"})

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


def date_only_fallback(birth: date) -> dict[str, Any]:
    sun = sun_sign_from_date(birth)
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
                {"key": "ascendant", "reason": "birth_time_or_place_missing"},
                {"key": "houses", "reason": "birth_time_or_place_missing"},
            ],
        },
        expected_mode="date_only",
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
) -> dict[str, Any]:
    mode = resolve_natal_facts_mode(
        birth_time=birth_time,
        time_unknown=time_unknown,
        latitude=latitude,
        longitude=longitude,
    )
    time_str: str | None = None
    if isinstance(birth_time, time):
        time_str = birth_time.strftime("%H:%M:%S")
    elif birth_time:
        time_str = str(birth_time)
    return {
        "display_name": (display_name or "").strip() or None,
        "birth_date": birth_date.isoformat(),
        "birth_time": None if time_unknown else time_str,
        "time_unknown": time_unknown,
        "location_name": (location_name or "").strip() or None,
        "latitude": latitude,
        "longitude": longitude,
        "timezone_name": timezone_name,
        "mode": mode,
    }


def generate_natal_facts(
    *,
    available_input: dict[str, Any],
    locale: str = "ru",
) -> dict[str, Any]:
    mode = str(available_input.get("mode") or "date_only")
    birth_raw = available_input.get("birth_date")
    try:
        birth = date.fromisoformat(str(birth_raw))
    except (TypeError, ValueError) as exc:
        raise ValueError("birth_date required as YYYY-MM-DD") from exc

    if not is_llm_chat_configured():
        logger.info("natal_facts: LLM not configured — deterministic sun fallback")
        return date_only_fallback(birth)

    system, version = get_prompt(PROMPT_ID, locale=locale)
    user_payload = {
        "contract_id": "natal_facts",
        "prompt_version": version,
        "available_input": available_input,
    }
    client = get_openai_compatible_client()
    model = resolve_default_chat_model()
    raw = chat_completion_text(
        client,
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
        ],
        temperature=0.2,
        max_tokens=2500,
        json_object=True,
    )
    parsed = _parse_json_object(raw or "")
    if not parsed:
        logger.warning("natal_facts: empty/invalid LLM JSON — fallback")
        return date_only_fallback(birth)

    facts = validate_natal_facts(parsed, expected_mode=mode)
    if not any(p.get("id") == "sun" for p in facts["planets"]):
        facts["planets"].insert(0, {"id": "sun", "sign": sun_sign_from_date(birth), "degree": 15.0})
    facts["prompt_id"] = PROMPT_ID
    facts["prompt_version"] = version
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
    meta = {
        "source": "natal_facts_contract",
        "natal_facts": facts,
        "mode": facts.get("mode"),
        "provider": facts.get("provider"),
        "calculation_id": facts.get("calculation_id"),
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
