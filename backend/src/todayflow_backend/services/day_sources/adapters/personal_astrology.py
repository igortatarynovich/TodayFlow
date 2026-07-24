"""Adapter: personal_astrology — natal transits (L3 Personal, not Foundation)."""

from __future__ import annotations

from typing import Any

from todayflow_backend.services.day_sources.types import DaySourceInputs, SourceResult

_CALC = "personal-astrology-adapter-v0"

_HOUSE_KEYS = ("house", "natal_house", "transit_house", "house_number")


def _transit_has_house(row: dict[str, Any]) -> bool:
    for k in _HOUSE_KEYS:
        if row.get(k) not in (None, "", []):
            return True
    return False


def run_personal_astrology(inputs: DaySourceInputs) -> SourceResult:
    ce = inputs.celestial_events if isinstance(inputs.celestial_events, dict) else {}
    raw = [r for r in (ce.get("personal_transits") or []) if isinstance(r, dict)]

    if inputs.birth_date is None and not raw:
        return SourceResult(
            family_id="personal_astrology",
            capability_ids=[],
            layer="personal",
            status="unavailable",
            unavailable_reason="missing_birth_date",
            calculation_version=_CALC,
        )

    if not raw:
        return SourceResult(
            family_id="personal_astrology",
            capability_ids=[],
            layer="personal",
            status="unavailable",
            unavailable_reason="missing_personal_transits",
            payload={
                "birth_date": inputs.birth_date.isoformat() if inputs.birth_date else None,
                "depth": "none",
            },
            evidence_refs=["birth_date"] if inputs.birth_date else [],
            calculation_version=_CALC,
        )

    has_time = inputs.birth_time is not None
    has_place = inputs.birth_lat is not None and inputs.birth_lon is not None
    house_capable = has_time and has_place
    house_rows = [r for r in raw if _transit_has_house(r)]

    caps = ["natal_transits"]
    depth = "sign_level"
    if house_capable:
        caps.append("transits_by_house")
        depth = "houses" if house_rows else "sign_level_time_known"

    beats: list[dict[str, Any]] = []
    for row in raw[:6]:
        title = str(row.get("title") or "")
        story = str(row.get("story_ru") or "")
        if not title and not story:
            continue
        beats.append(
            {
                "id": str(row.get("id") or f"pt-{len(beats)}"),
                "kind": "natal_transit",
                "title": title,
                "story_ru": story or title,
                "transiting_planet": row.get("transiting_planet"),
                "natal_planet": row.get("natal_planet"),
                "aspect": row.get("aspect"),
                "strength": row.get("strength"),
                "evidence_ref": "celestial_events.personal_transits",
            }
        )

    lead = beats[0] if beats else {}
    summary = ""
    if lead:
        summary = str(lead.get("story_ru") or lead.get("title") or "")
        if len(beats) > 1:
            summary = f"{summary} Ещё активных личных транзитов: {len(beats) - 1}."

    return SourceResult(
        family_id="personal_astrology",
        capability_ids=caps,
        layer="personal",
        status="ok",
        payload={
            "depth": depth,
            "capability_ids": caps,
            "birth_date": inputs.birth_date.isoformat() if inputs.birth_date else None,
            "has_birth_time": has_time,
            "has_birth_place": has_place,
            "transits": raw[:8],
            "beats": beats,
            "summary_ru": summary[:320],
            "school_canon": "placidus_when_time_place",
        },
        evidence_refs=["celestial_events.personal_transits", "birth_date"],
        calculation_version=_CALC,
    )
