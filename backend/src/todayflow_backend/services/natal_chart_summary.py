"""Сжатое резюме натальной карты для LLM и ядра профиля (без сырых координат)."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.services.aspects import AspectEngine
from todayflow_backend.services.natal_chart_cache import get_natal_chart_cache_service
from todayflow_backend.services.natal_chart_interpreter import get_natal_chart_interpreter


def _trunc(text: str, max_len: int) -> str:
    s = (text or "").strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 1].rstrip() + "…"


_PLANET_ALIASES: dict[str, str] = {
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
}

_PRIORITY_LUMINARIES = ("Sun", "Moon")
_PRIORITY_PERSONAL = ("Mercury", "Venus", "Mars")
_OUTER = ("Jupiter", "Saturn", "Uranus", "Neptune", "Pluto")


def _canon_planet(raw: str | None) -> str | None:
    if not raw or not isinstance(raw, str):
        return None
    key = raw.strip().lower()
    return _PLANET_ALIASES.get(key)


def _index_positions(chart_positions: list[dict] | None) -> dict[str, dict[str, Any]]:
    by_name: dict[str, dict[str, Any]] = {}
    if not chart_positions:
        return by_name
    for pos in chart_positions:
        if not isinstance(pos, dict):
            continue
        body = _canon_planet(pos.get("body") or pos.get("name"))
        if body:
            by_name[body] = pos
    return by_name


def build_natal_chart_summary_for_core(
    db: Session,
    *,
    astro_profile_id: int | None,
    locale: str = "ru",
) -> dict[str, Any]:
    """Текстовое резюме карты из кеша: углы, личные планеты, внешние, ключевые аспекты.

    Не вычисляет карту заново и не отдаёт долготы/орбы — только готовые формулировки для модели.
    """
    if not astro_profile_id:
        return {"available": False, "reason": "no_astro_profile"}

    cache = get_natal_chart_cache_service(db).get_cached_natal_chart(astro_profile_id)
    if cache is None:
        return {"available": False, "reason": "chart_not_cached"}

    interpreter = get_natal_chart_interpreter()
    full = interpreter.interpret_full_chart(cache)
    by_pos = _index_positions(cache.positions)

    angles_block: dict[str, Any] = {}
    angles = full.get("angles") if isinstance(full.get("angles"), dict) else {}
    asc = angles.get("ascendant") if isinstance(angles.get("ascendant"), dict) else {}
    mc = angles.get("mc") if isinstance(angles.get("mc"), dict) else {}
    if asc.get("sign") or asc.get("meaning"):
        angles_block["ascendant_sign"] = asc.get("sign")
        angles_block["ascendant"] = _trunc(str(asc.get("meaning") or ""), 200)
    if mc.get("sign") or mc.get("meaning"):
        angles_block["midheaven_sign"] = mc.get("sign")
        angles_block["midheaven"] = _trunc(str(mc.get("meaning") or ""), 200)

    meta = cache.metadata if isinstance(cache.metadata, dict) else {}
    house_system = meta.get("house_system") or meta.get("houseSystem")

    def planet_entry(body: str) -> dict[str, Any] | None:
        pos = by_pos.get(body)
        if not pos:
            return None
        sign = pos.get("sign")
        house = pos.get("house")
        gist = None
        if sign:
            gist = interpreter.interpret_planet_in_sign(body, str(sign))
        if not gist and house is not None:
            try:
                gist = interpreter.interpret_planet_in_house(body, int(house))
            except (TypeError, ValueError):
                gist = None
        return {
            "name": body,
            "sign": sign,
            "house": house,
            "gist": _trunc(str(gist or ""), 260),
        }

    luminaries: list[dict[str, Any]] = []
    for body in _PRIORITY_LUMINARIES:
        row = planet_entry(body)
        if row:
            luminaries.append(row)

    personal: list[dict[str, Any]] = []
    for body in _PRIORITY_PERSONAL:
        row = planet_entry(body)
        if row:
            personal.append(row)

    outer_gists: list[dict[str, Any]] = []
    for body in _OUTER:
        row = planet_entry(body)
        if row and row.get("gist"):
            outer_gists.append(
                {
                    "name": body,
                    "sign": row.get("sign"),
                    "gist": _trunc(str(row["gist"]), 150),
                }
            )

    notable_aspects: list[dict[str, Any]] = []
    positions_for_aspects: list[dict[str, Any]] = []
    for pos in cache.positions or []:
        if not isinstance(pos, dict):
            continue
        raw_body = pos.get("body") or pos.get("name")
        lon = pos.get("longitude")
        if raw_body is None or lon is None:
            continue
        try:
            positions_for_aspects.append({"body": str(raw_body).lower(), "longitude": float(lon)})
        except (TypeError, ValueError):
            continue

    if positions_for_aspects:
        engine = AspectEngine()
        aspect_response = engine.callouts(positions_for_aspects, locale=locale)
        for c in (aspect_response.callouts or [])[:7]:
            line = (c.integration or c.description or c.label or "").strip()
            notable_aspects.append(
                {
                    "bodies": c.bodies,
                    "aspect": c.aspect_id,
                    "strength": c.strength,
                    "gist": _trunc(line, 220),
                }
            )

    return {
        "available": True,
        "astro_profile_id": astro_profile_id,
        "house_system": str(house_system)[:80] if house_system else None,
        "angles": angles_block,
        "luminaries": luminaries,
        "personal_planets": personal,
        "outer_planets": outer_gists[:5],
        "notable_aspects": notable_aspects,
    }
