"""sky_today_v1 — compact shared-sky nest for Today strip + tap sheet.

Canon: DAY_ENGINE_AND_COHERENCE §2 · TODAY_SCREEN_SCENARIO_V3 Block 1a.
Public nest is influence, not an ephemeris dump: Moon climate + one headline pair.
Personal overlay is L3 (day_personal / why_personal) — composed on Today, not this nest.
Honest omit when empty. No invented copy.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from todayflow_backend.services.sky_geometry_v1 import CORE_BODIES, positions_to_sky_bodies

SKY_TODAY_V1 = "sky_today_v1"

_ASPECT_RU = {
    "conjunction": "соединение",
    "sextile": "секстиль",
    "square": "квадрат",
    "trine": "тригон",
    "opposition": "оппозиция",
}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _norm_body(raw: Any) -> str:
    return _clean(raw).lower()


def _slim_position(row: dict[str, Any]) -> dict[str, Any] | None:
    body = _norm_body(row.get("body") or row.get("planet"))
    sign = _clean(row.get("sign"))
    sign_ru = _clean(row.get("sign_ru")) or sign
    if not body or not sign:
        return None
    degree = row.get("degree")
    return {
        "body": body,
        "body_ru": _clean(row.get("body_ru")) or body,
        "sign": sign,
        "sign_ru": sign_ru,
        "degree": float(degree) if isinstance(degree, (int, float)) else None,
        "retrograde": bool(row.get("retrograde") or row.get("is_retrograde")),
    }


_SIGN_PREP = {
    "Овен": "Овне",
    "Телец": "Тельце",
    "Близнецы": "Близнецах",
    "Рак": "Раке",
    "Лев": "Льве",
    "Дева": "Деве",
    "Весы": "Весах",
    "Скорпион": "Скорпионе",
    "Стрелец": "Стрельце",
    "Козерог": "Козероге",
    "Водолей": "Водолее",
    "Рыбы": "Рыбах",
}


def _in_sign_label(body_ru: str, sign_ru: str) -> str:
    prep = _SIGN_PREP.get(sign_ru, sign_ru)
    prefix = "во" if prep.startswith("Льв") else "в"
    return f"{body_ru} {prefix} {prep}"


def _moon_from_foundation(day_foundation: dict[str, Any] | None) -> dict[str, Any] | None:
    lunar = _as_dict(_as_dict(day_foundation).get("lunar"))
    moon = _as_dict(lunar.get("moon_sign"))
    sign = _clean(moon.get("sign"))
    sign_ru = _clean(moon.get("sign_ru")) or sign
    if not sign:
        return None
    return {
        "body": "moon",
        "body_ru": "Луна",
        "sign": sign,
        "sign_ru": sign_ru,
        "degree": float(moon["degree"]) if isinstance(moon.get("degree"), (int, float)) else None,
        "retrograde": False,
        "exact_time_local": None,
    }


def _on_day(raw: Any, target_date: date | None) -> str | None:
    value = _clean(raw)
    if not value:
        return None
    if target_date is not None and value[:10] != target_date.isoformat():
        return None
    return value


def _moon_ingress_time(ce: dict[str, Any], target_date: date | None) -> str | None:
    for row in ce.get("ingresses") or []:
        if not isinstance(row, dict):
            continue
        planet = _norm_body(row.get("planet") or row.get("planet_ru"))
        if "moon" not in planet and "лун" not in planet:
            continue
        when = _on_day(row.get("exact_time") or row.get("exact_time_local"), target_date)
        if when:
            return when
    return None


def _window_from_voc(ce: dict[str, Any], target_date: date | None) -> dict[str, str] | None:
    voc = _as_dict(ce.get("void_of_course"))
    if _clean(voc.get("status")).lower() != "ok":
        return None
    starts = _clean(voc.get("starts_at"))
    ends = _clean(voc.get("ends_at"))
    if not starts or not ends:
        return None
    if target_date is not None:
        day = target_date.isoformat()
        if not (starts[:10] <= day <= ends[:10]):
            return None
    return {"kind": "void_of_course", "starts_at": starts, "ends_at": ends}


def _headline_with_signs(
    headline: dict[str, Any] | None,
    by_body: dict[str, dict[str, Any]],
    *,
    target_date: date | None = None,
) -> dict[str, Any] | None:
    hs = _as_dict(headline)
    a = _norm_body(hs.get("planet_a"))
    b = _norm_body(hs.get("planet_b"))
    aspect = _norm_body(hs.get("aspect"))
    if not a or not b or not aspect:
        return None
    left = by_body.get(a) or {}
    right = by_body.get(b) or {}
    a_ru = _clean(left.get("body_ru")) or _clean(hs.get("planet_a"))
    b_ru = _clean(right.get("body_ru")) or _clean(hs.get("planet_b"))
    sign_a_ru = _clean(left.get("sign_ru"))
    sign_b_ru = _clean(right.get("sign_ru"))
    aspect_ru = _ASPECT_RU.get(aspect, aspect)
    if sign_a_ru and sign_b_ru:
        title_ru = f"{_in_sign_label(a_ru, sign_a_ru)} — {aspect_ru} — {_in_sign_label(b_ru, sign_b_ru)}"
    else:
        title_ru = _clean(hs.get("title_ru")) or f"{a_ru} — {aspect_ru} — {b_ru}"
    return {
        "id": _clean(hs.get("id")) or f"sky-{a}-{aspect}-{b}",
        "planet_a": a,
        "planet_b": b,
        "planet_a_ru": a_ru,
        "planet_b_ru": b_ru,
        "sign_a": _clean(left.get("sign")) or None,
        "sign_b": _clean(right.get("sign")) or None,
        "sign_a_ru": sign_a_ru or None,
        "sign_b_ru": sign_b_ru or None,
        "aspect": aspect,
        "aspect_ru": aspect_ru,
        "title_ru": title_ru,
        "story_ru": _clean(hs.get("story_ru")) or None,
        "orb_delta": hs.get("orb_delta"),
        "exact_time_local": _on_day(
            hs.get("exact_time_local") or hs.get("exact_time"), target_date
        ),
    }


def build_sky_today_v1(
    *,
    celestial_events: dict[str, Any] | None = None,
    day_foundation: dict[str, Any] | None = None,
    target_date: date | None = None,
) -> dict[str, Any] | None:
    """Compact nest for Today strip + sheet. None when nothing to show."""
    ce = _as_dict(celestial_events)
    raw_positions = list(ce.get("sky_positions") or [])
    bodies = positions_to_sky_bodies(raw_positions) if raw_positions else []
    positions: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in bodies or raw_positions:
        if not isinstance(row, dict):
            continue
        slim = _slim_position(row)
        if not slim or slim["body"] in seen:
            continue
        seen.add(slim["body"])
        positions.append(slim)
    order = {b: i for i, b in enumerate(CORE_BODIES)}
    positions.sort(key=lambda r: order.get(str(r.get("body")), 99))
    by_body = {str(r.get("body")): r for r in positions}

    moon = by_body.get("moon") or _moon_from_foundation(day_foundation)
    if isinstance(moon, dict):
        ingress = _moon_ingress_time(ce, target_date)
        if ingress:
            moon = {**moon, "exact_time_local": ingress}
        else:
            moon = {**moon, "exact_time_local": None}
    headline = _headline_with_signs(
        ce.get("headline_sky") if isinstance(ce.get("headline_sky"), dict) else None,
        by_body,
        target_date=target_date,
    )
    window = _window_from_voc(ce, target_date)

    if not moon and not headline:
        return None

    nest: dict[str, Any] = {
        "contract_version": SKY_TODAY_V1,
        "moon": moon,
        "headline": headline,
    }
    if window:
        nest["window"] = window
    return nest


def celestial_events_from_morning(morning: Any | None) -> dict[str, Any] | None:
    if morning is None:
        return None
    if isinstance(morning, dict):
        ce = morning.get("celestial_events")
        return ce if isinstance(ce, dict) else None
    ce = getattr(morning, "celestial_events", None)
    return ce if isinstance(ce, dict) else None
