"""Moon void-of-course (VOC) — majors-only canon (DAY_SOURCES_CANON §3 / §5.2.4).

v0: full window requires timed major Moon aspects before the next sign ingress.
Without an aspect timeline the capability is explicitly unavailable (not guessed).
"""

from __future__ import annotations

from datetime import date
from typing import Any

VOC_RULE_ID = "majors_only_v1"
_MOON_TOKENS = ("moon", "луна", "лун")


def _is_moonish(text: str | None) -> bool:
    low = (text or "").lower()
    return any(tok in low for tok in _MOON_TOKENS)


def _moon_ingress_moment(ingresses: list[Any]) -> str | None:
    for row in ingresses or []:
        if not isinstance(row, dict):
            continue
        if not (
            _is_moonish(str(row.get("planet") or ""))
            or _is_moonish(str(row.get("planet_ru") or ""))
        ):
            continue
        raw = row.get("exact_time") or row.get("ingress_date") or row.get("local_time")
        if raw:
            return str(raw)
    return None


def build_void_of_course_v0(
    *,
    target_date: date,
    ingresses: list[Any] | None = None,
    timed_lunar_aspects: list[Any] | None = None,
) -> dict[str, Any]:
    """Return VOC payload. status=ok only when start+end are known from timed aspects."""
    next_ingress = _moon_ingress_moment(ingresses or [])
    timed = [a for a in (timed_lunar_aspects or []) if isinstance(a, dict) and a.get("exact_time")]
    if not timed or not next_ingress:
        return {
            "rule_id": VOC_RULE_ID,
            "status": "unavailable",
            "unavailable_reason": "missing_aspect_timeline",
            "next_moon_ingress_date": (str(next_ingress)[:10] if next_ingress else None),
            "target_date": target_date.isoformat(),
        }

    ingress_key = str(next_ingress)[:19]
    before: list[dict[str, Any]] = []
    for row in timed:
        et = str(row.get("exact_time") or "")[:19]
        if et and et <= ingress_key:
            before.append(row)
    if not before:
        return {
            "rule_id": VOC_RULE_ID,
            "status": "unavailable",
            "unavailable_reason": "no_major_aspect_before_ingress",
            "next_moon_ingress_date": str(next_ingress)[:10],
            "target_date": target_date.isoformat(),
        }

    before.sort(key=lambda r: str(r.get("exact_time") or ""))
    last = before[-1]
    starts_at = str(last.get("exact_time"))
    ends_at = str(next_ingress)
    day = target_date.isoformat()
    # Civil-day product: day is in VOC if the window overlaps that calendar date.
    in_voc = starts_at[:10] <= day <= ends_at[:10]
    return {
        "rule_id": VOC_RULE_ID,
        "status": "ok",
        "starts_at": starts_at,
        "ends_at": ends_at,
        "in_void_of_course": in_voc,
        "last_aspect_id": last.get("id"),
        "next_moon_ingress_date": ends_at[:10],
        "target_date": target_date.isoformat(),
    }
