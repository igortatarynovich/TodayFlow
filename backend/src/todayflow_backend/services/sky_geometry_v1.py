"""Shared-sky geometry for Today: bodies in signs + major aspects + one headline driver.

Canon: DAY_SOURCES_CANON §5.1 planetary_positions / aspects (majors).
Foundation orbs: DATA/foundation_v1/aspects.json via foundation_constants_v1.

This is the day's celestial plot (L1), not a natal encyclopedia.
Natal overlay (L3) stays natal_activations / top_driver_v1.
"""

from __future__ import annotations

from math import fabs
from typing import Any

from todayflow_backend.data.foundation_constants_v1 import (
    aspect_is_challenging,
    aspect_is_harmonious,
    aspects_by_id,
)

SKY_GEOMETRY_V1 = "sky_geometry_v1"

# Product majors only — same five as Wave2 natal_activations. Minors stay in the
# foundation table but do not compete for the day's headline.
_MAJOR_IDS = ("conjunction", "sextile", "square", "trine", "opposition")

CORE_BODIES = (
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

# How much the body moves the *civil day* (faster = more "today").
_DAILY_WEIGHT: dict[str, float] = {
    "moon": 1.00,
    "mercury": 0.92,
    "venus": 0.82,
    "sun": 0.80,
    "mars": 0.72,
    "jupiter": 0.48,
    "saturn": 0.38,
    "uranus": 0.22,
    "neptune": 0.22,
    "pluto": 0.22,
}

_ASPECT_WEIGHT: dict[str, float] = {
    "conjunction": 1.00,
    "opposition": 0.90,
    "square": 0.86,
    "trine": 0.62,
    "sextile": 0.52,
}

# Wire domains (today_domain_wire_v1) — shared climate, not personal verdicts.
_PLANET_DOMAINS: dict[str, tuple[str, ...]] = {
    "sun": ("work", "energy"),
    "moon": ("energy", "relationships"),
    "mercury": ("work",),
    "venus": ("relationships", "money"),
    "mars": ("energy", "work"),
    "jupiter": ("work", "money"),
    "saturn": ("work", "money"),
    "uranus": ("work", "energy"),
    "neptune": ("energy", "relationships"),
    "pluto": ("energy", "work"),
}

_ZODIAC = (
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
)

_SIGN_RU = {
    "Aries": "Овен",
    "Taurus": "Телец",
    "Gemini": "Близнецы",
    "Cancer": "Рак",
    "Leo": "Лев",
    "Virgo": "Дева",
    "Libra": "Весы",
    "Scorpio": "Скорпион",
    "Sagittarius": "Стрелец",
    "Capricorn": "Козерог",
    "Aquarius": "Водолей",
    "Pisces": "Рыбы",
}

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

_ASPECT_RU = {
    "conjunction": "соединение",
    "sextile": "секстиль",
    "square": "квадрат",
    "trine": "тригон",
    "opposition": "оппозиция",
}

_BODY_ALIASES = {
    "north_node": None,
    "south_node": None,
    "chiron": None,
    "lilith": None,
    "rising": None,
    "ascendant": None,
}


def _norm_body(name: str | None) -> str | None:
    raw = str(name or "").strip().lower().replace(" ", "_")
    if not raw:
        return None
    if raw in _BODY_ALIASES:
        return None if _BODY_ALIASES[raw] is None else _BODY_ALIASES[raw]
    if raw in CORE_BODIES:
        return raw
    return None


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def angular_separation(left: float, right: float) -> float:
    raw = fabs(float(left) - float(right)) % 360.0
    if raw > 180.0:
        raw = 360.0 - raw
    return raw


def sign_from_longitude(longitude: float) -> tuple[str, float]:
    lon = float(longitude) % 360.0
    idx = int(lon // 30) % 12
    return _ZODIAC[idx], lon % 30.0


def _major_aspect_table() -> list[tuple[str, float, float]]:
    table: list[tuple[str, float, float]] = []
    rows = aspects_by_id()
    for aid in _MAJOR_IDS:
        rec = rows.get(aid) or {}
        angle = rec.get("angle")
        orb = rec.get("orb")
        if angle is None or orb is None:
            continue
        table.append((aid, float(angle), float(orb)))
    return table


def resolve_major_aspect(separation: float) -> tuple[str, float, float] | None:
    """Return (aspect_id, orb_delta, max_orb) or None."""
    sep = float(separation)
    best: tuple[str, float, float] | None = None
    for aid, angle, orb in _major_aspect_table():
        delta = fabs(sep - angle)
        if delta <= orb and (best is None or delta < best[1]):
            best = (aid, delta, orb)
    return best


def pair_daily_weight(left: str, right: str) -> float:
    wa = _DAILY_WEIGHT.get(left, 0.3)
    wb = _DAILY_WEIGHT.get(right, 0.3)
    hi = max(wa, wb)
    lo = min(wa, wb)
    if hi <= 0:
        return 0.0
    return hi * (0.55 + 0.45 * (lo / hi))


def exactness(orb_delta: float, max_orb: float) -> float:
    cap = max(float(max_orb), 0.01)
    # Tight orbs punch above a loose hit of a "heavier" kind.
    return _clip01(1.0 - (max(0.0, float(orb_delta)) / cap) ** 0.7)


def daily_score(*, left: str, right: str, aspect: str, orb_delta: float, max_orb: float) -> float:
    return _clip01(
        pair_daily_weight(left, right)
        * _ASPECT_WEIGHT.get(aspect, 0.4)
        * exactness(orb_delta, max_orb)
    )


def domain_weights(left: str, right: str) -> dict[str, float]:
    scores = {"work": 0.0, "money": 0.0, "relationships": 0.0, "energy": 0.0}
    for body in (left, right):
        w = _DAILY_WEIGHT.get(body, 0.3)
        for domain in _PLANET_DOMAINS.get(body, ()):
            scores[domain] += w
    total = sum(scores.values()) or 1.0
    return {k: round(v / total, 3) for k, v in scores.items() if v > 0}


def thesis_hint(left: str, right: str, aspect: str) -> str:
    """family/variant for day_thesis_v1 — shared sky plot, not natal conflict."""
    pair = frozenset({left, right})
    challenging = aspect_is_challenging(aspect)
    harmonious = aspect_is_harmonious(aspect)
    conjunction = aspect == "conjunction"

    if pair == {"mercury", "jupiter"}:
        return "communication/truth_without_filter" if challenging else "communication/restart_messages"
    if pair == {"mercury", "saturn"}:
        return "pressure/patience_test" if challenging else "communication/clarity_returns_after_delay"
    if pair == {"sun", "mercury"} or pair == {"moon", "mercury"}:
        return "communication/truth_without_filter" if challenging else "communication/clarity_returns_after_delay"
    if "moon" in pair and "mars" in pair:
        return "pressure/patience_test" if challenging else "momentum/gather_pace"
    if "venus" in pair and "mars" in pair:
        return "connection/repair_after_friction" if challenging else "connection/honest_contact"
    if "venus" in pair and "moon" in pair:
        return "connection/honest_contact"
    if "saturn" in pair:
        return "pressure/boundary_day"
    if "uranus" in pair:
        return "change/sudden_turns"
    if "pluto" in pair and challenging:
        return "pressure/intensity_without_drama"
    if "jupiter" in pair and (harmonious or conjunction):
        return "momentum/new_window"
    if challenging:
        return "pressure/intensity_without_drama"
    if harmonious:
        return "momentum/steady_productive_rhythm"
    return "momentum/gather_pace"


def positions_to_sky_bodies(positions: list[Any] | None) -> list[dict[str, Any]]:
    """Normalize Swiss/AstroService rows → core bodies with sign + longitude."""
    by_body: dict[str, dict[str, Any]] = {}
    for pos in positions or []:
        if not isinstance(pos, dict):
            continue
        body = _norm_body(str(pos.get("body") or pos.get("planet") or ""))
        lon = pos.get("longitude")
        if not body or not isinstance(lon, (int, float)):
            continue
        lon_f = float(lon) % 360.0
        sign = str(pos.get("sign") or "").strip()
        degree = pos.get("degree")
        if not sign:
            sign, deg_in = sign_from_longitude(lon_f)
            if degree is None:
                degree = round(deg_in, 2)
        elif degree is None:
            _, deg_in = sign_from_longitude(lon_f)
            degree = round(deg_in, 2)
        by_body[body] = {
            "body": body,
            "body_ru": _PLANET_RU.get(body, body),
            "sign": sign,
            "sign_ru": _SIGN_RU.get(sign, sign),
            "degree": float(degree) if isinstance(degree, (int, float)) else None,
            "longitude": lon_f,
            "retrograde": bool(pos.get("retrograde") or pos.get("is_retrograde")),
        }
    return [by_body[b] for b in CORE_BODIES if b in by_body]


def transit_signs_from_bodies(bodies: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for row in bodies:
        body = str(row.get("body") or "")
        sign = str(row.get("sign") or "")
        if not body or not sign:
            continue
        payload = {
            "sign": sign,
            "sign_ru": row.get("sign_ru") or _SIGN_RU.get(sign, sign),
            "degree": row.get("degree"),
            "source": "transit_chart",
        }
        if body == "moon":
            out["moon_sign"] = payload
        elif body == "sun":
            out["sun_sign"] = payload
    return out


def _story_ru(left: str, right: str, aspect: str) -> str:
    rec = aspects_by_id().get(aspect) or {}
    meaning = str(rec.get("base_meaning_ru") or "").strip()
    a = _PLANET_RU.get(left, left)
    b = _PLANET_RU.get(right, right)
    asp = _ASPECT_RU.get(aspect, aspect)
    if meaning:
        return f"{a} — {asp} — {b}: {meaning}"
    return f"{a} — {asp} — {b}"


def sky_aspects_from_bodies(bodies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    indexed = {str(r.get("body")): r for r in bodies if r.get("body") and r.get("longitude") is not None}
    names = [b for b in CORE_BODIES if b in indexed]
    out: list[dict[str, Any]] = []
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            sep = angular_separation(float(indexed[left]["longitude"]), float(indexed[right]["longitude"]))
            hit = resolve_major_aspect(sep)
            if not hit:
                continue
            aspect, orb_delta, max_orb = hit
            score = daily_score(
                left=left,
                right=right,
                aspect=aspect,
                orb_delta=orb_delta,
                max_orb=max_orb,
            )
            if orb_delta <= 1.0:
                strength_label = "exact"
            elif orb_delta <= 3.0:
                strength_label = "tight"
            else:
                strength_label = "loose"
            tension = "high" if aspect_is_challenging(aspect) else ("low" if aspect_is_harmonious(aspect) else None)
            a_title = left.title()
            b_title = right.title()
            hint = thesis_hint(left, right, aspect)
            out.append(
                {
                    "id": f"sky-{left}-{aspect}-{right}",
                    "kind": "sky_aspect",
                    "aspect": aspect,
                    "planet_a": a_title,
                    "planet_b": b_title,
                    "title": f"{a_title} × {b_title}",
                    "title_ru": (
                        f"{_PLANET_RU.get(left, a_title)} — "
                        f"{_ASPECT_RU.get(aspect, aspect)} — "
                        f"{_PLANET_RU.get(right, b_title)}"
                    ),
                    "story_ru": _story_ru(left, right, aspect)[:240],
                    "orb_delta": round(orb_delta, 3),
                    "degrees_apart": round(sep, 2),
                    "strength": strength_label,
                    "tension_level": tension,
                    "daily_score": round(score, 4),
                    "domain_weights": domain_weights(left, right),
                    "thesis_hint": hint,
                    "priority_hint": "secondary",
                }
            )
    out.sort(key=lambda r: (-float(r.get("daily_score") or 0), float(r.get("orb_delta") or 99)))
    if out:
        out[0]["priority_hint"] = "primary"
        out[0]["kind"] = "sky_aspect"
    return out


def pick_headline_sky(aspects: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not aspects:
        return None
    top = aspects[0]
    return {
        "id": top.get("id"),
        "kind": "sky_aspect",
        "planet_a": top.get("planet_a"),
        "planet_b": top.get("planet_b"),
        "aspect": top.get("aspect"),
        "title": top.get("title"),
        "title_ru": top.get("title_ru"),
        "story_ru": top.get("story_ru"),
        "orb_delta": top.get("orb_delta"),
        "daily_score": top.get("daily_score"),
        "domain_weights": top.get("domain_weights") or {},
        "thesis_hint": top.get("thesis_hint"),
        "exact_time": top.get("exact_time"),
        "contract_version": SKY_GEOMETRY_V1,
    }
