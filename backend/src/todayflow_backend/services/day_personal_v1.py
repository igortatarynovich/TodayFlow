"""Day Personal v1 — L3 activation from personal Source Families (not Foundation)."""

from __future__ import annotations

import re
from datetime import date, time
from typing import Any

from todayflow_backend.services.day_sources import DaySourceInputs
from todayflow_backend.services.day_sources.registry import collect_personal_sources


def _clip(text: str, limit: int) -> str:
    t = re.sub(r"\s+", " ", str(text or "").strip())
    if len(t) <= limit:
        return t
    return t[: limit - 1].rstrip() + "…"


def build_day_personal_v1(
    celestial_events: dict[str, Any] | None,
    *,
    target_date: date | None = None,
    birth_date: date | None = None,
    birth_time: time | None = None,
    birth_lat: float | None = None,
    birth_lon: float | None = None,
    timezone: str | None = None,
    locale: str = "ru",
) -> dict[str, Any]:
    """Collect personal Source Families into a wire pack for Today / interpretation."""
    ce = celestial_events if isinstance(celestial_events, dict) else {}
    inputs = DaySourceInputs(
        target_date=target_date or date.today(),
        timezone=timezone,
        birth_date=birth_date,
        birth_time=birth_time,
        birth_lat=birth_lat,
        birth_lon=birth_lon,
        celestial_events=ce or None,
        locale=locale,
    )
    bundle = collect_personal_sources(inputs)
    sources = bundle.get("sources") if isinstance(bundle.get("sources"), dict) else {}
    personal_astro = sources.get("personal_astrology") if isinstance(sources, dict) else None
    payload = (
        personal_astro.get("payload")
        if isinstance(personal_astro, dict) and personal_astro.get("status") == "ok"
        else None
    )

    return {
        "contract_version": "day_personal_v1",
        "calculation_version": "day-personal-v1.0",
        "personal_astrology": payload,
        "summary_ru": _clip(str((payload or {}).get("summary_ru") or ""), 320),
        "source_inputs": {
            "has_personal_astrology": bool(payload),
            "ok_family_ids": list(bundle.get("ok_family_ids") or []),
            "unavailable": {
                fid: row.get("unavailable_reason")
                for fid, row in sources.items()
                if isinstance(row, dict) and row.get("status") == "unavailable"
            },
        },
        "source_bundle": {
            "contract_version": bundle.get("contract_version"),
            "ok_family_ids": bundle.get("ok_family_ids"),
        },
    }


def personal_to_interpretation_claims(personal: dict[str, Any] | None) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    if not isinstance(personal, dict):
        return claims
    astro = personal.get("personal_astrology")
    if not isinstance(astro, dict):
        return claims
    for b in (astro.get("beats") or [])[:4]:
        if not isinstance(b, dict):
            continue
        text = _clip(str(b.get("story_ru") or b.get("title") or ""), 280)
        if not text:
            continue
        claims.append(
            {
                "id": f"claim.personal.astro.{b.get('id')}",
                "kind": "personal",
                "text": text,
                "evidence_ids": [str(b.get("evidence_ref") or b.get("id"))],
                "domain": None,
                "layer": "personal_astrology",
            }
        )
    summary = _clip(str(astro.get("summary_ru") or ""), 280)
    if summary and not claims:
        claims.append(
            {
                "id": "claim.personal.astro.summary",
                "kind": "personal",
                "text": summary,
                "evidence_ids": ["source.personal_astrology"],
                "domain": None,
                "layer": "personal_astrology",
            }
        )
    return claims
