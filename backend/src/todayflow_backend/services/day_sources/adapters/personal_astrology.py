"""Adapter: personal_astrology — transits, profections, progressions, returns, rulers (L3)."""

from __future__ import annotations

from typing import Any

from todayflow_backend.services.day_sources.house_rulers import build_house_rulers_chains
from todayflow_backend.services.day_sources.profections import build_profections
from todayflow_backend.services.day_sources.progressions import build_progressions_pack
from todayflow_backend.services.day_sources.returns import build_returns_pack
from todayflow_backend.services.day_sources.types import DaySourceInputs, SourceResult

_CALC = "personal-astrology-adapter-v4"

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

    has_time = inputs.birth_time is not None
    has_place = inputs.birth_lat is not None and inputs.birth_lon is not None
    caps: list[str] = []
    beats: list[dict[str, Any]] = []
    evidence: list[str] = []
    depth = "none"
    profections = None
    progressions = None
    returns = None
    house_rulers = None

    if raw:
        caps.append("natal_transits")
        evidence.append("celestial_events.personal_transits")
        depth = "sign_level"
        house_capable = has_time and has_place
        house_rows = [r for r in raw if _transit_has_house(r)]
        if house_capable:
            caps.append("transits_by_house")
            depth = "houses" if house_rows else "sign_level_time_known"
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

    if inputs.birth_date is not None:
        evidence.append("birth_date")
        profections = build_profections(
            inputs.birth_date,
            inputs.target_date,
            birth_time=inputs.birth_time,
            birth_lat=inputs.birth_lat,
            birth_lon=inputs.birth_lon,
            timezone_name=inputs.timezone,
        )
        caps.append("profections")
        beats.extend(list(profections.get("beats") or [])[:1])

        progressions = build_progressions_pack(
            inputs.birth_date,
            inputs.target_date,
            birth_time=inputs.birth_time,
            birth_lat=inputs.birth_lat,
            birth_lon=inputs.birth_lon,
            timezone_name=inputs.timezone,
        )
        caps.extend(list(progressions.get("capability_ids") or []))
        # Soft background: at most one progression beat into the day pack.
        beats.extend(list(progressions.get("beats") or [])[:1])

        returns = build_returns_pack(
            inputs.birth_date,
            inputs.target_date,
            birth_time=inputs.birth_time,
            birth_lat=inputs.birth_lat,
            birth_lon=inputs.birth_lon,
            timezone_name=inputs.timezone,
        )
        caps.extend(list(returns.get("capability_ids") or []))
        # Period context: prefer solar return beat over lunar for day summary.
        beats.extend(list(returns.get("beats") or [])[:1])

        if has_time and has_place and inputs.birth_time is not None:
            evidence.extend(["birth_time", "birth_place"])
            focus_house = None
            if isinstance(profections, dict):
                annual = profections.get("annual") or {}
                if isinstance(annual, dict) and annual.get("house"):
                    focus_house = int(annual["house"])
            house_rulers = build_house_rulers_chains(
                inputs.birth_date,
                birth_time=inputs.birth_time,
                birth_lat=float(inputs.birth_lat),
                birth_lon=float(inputs.birth_lon),
                timezone_name=inputs.timezone,
                focus_house=focus_house,
            )
            caps.append("house_rulers_chains")
            beats.extend(list(house_rulers.get("beats") or [])[:1])

        if depth == "none":
            depth = f"profections_{profections.get('depth')}"

    if not caps:
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

    summary_parts: list[str] = []
    if beats and beats[0].get("kind") == "natal_transit":
        summary_parts.append(str(beats[0].get("story_ru") or beats[0].get("title") or ""))
        transit_extra = sum(1 for b in beats if b.get("kind") == "natal_transit") - 1
        if transit_extra > 0:
            summary_parts.append(f"Ещё активных личных транзитов: {transit_extra}.")
    if profections and profections.get("summary_ru"):
        summary_parts.append(str(profections["summary_ru"]))
    if progressions and progressions.get("secondary_progressions"):
        summary_parts.append(
            str(progressions["secondary_progressions"].get("summary_ru") or "")
        )
    if returns and returns.get("solar_return"):
        summary_parts.append(str(returns["solar_return"].get("summary_ru") or ""))
    if house_rulers and house_rulers.get("summary_ru"):
        summary_parts.append(str(house_rulers["summary_ru"]))
    summary = " ".join(p for p in summary_parts if p)

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
            "profections": profections,
            "secondary_progressions": (
                progressions.get("secondary_progressions") if progressions else None
            ),
            "solar_arc": progressions.get("solar_arc") if progressions else None,
            "solar_return": returns.get("solar_return") if returns else None,
            "lunar_return": returns.get("lunar_return") if returns else None,
            "house_rulers_chains": house_rulers,
            "beats": beats,
            "summary_ru": summary[:480],
            "school_canon": "personal_astrology_v4_house_rulers",
        },
        evidence_refs=evidence or ["birth_date"],
        calculation_version=_CALC,
    )
