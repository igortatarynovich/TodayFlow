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

    def _ok_payload(family_id: str) -> dict[str, Any] | None:
        row = sources.get(family_id) if isinstance(sources, dict) else None
        if isinstance(row, dict) and row.get("status") == "ok" and isinstance(row.get("payload"), dict):
            return row["payload"]
        return None

    personal_astro = _ok_payload("personal_astrology")
    human_design = _ok_payload("human_design")
    bazi = _ok_payload("bazi")

    summary_parts = [
        str((personal_astro or {}).get("summary_ru") or "").strip(),
        str((human_design or {}).get("summary_ru") or "").strip(),
        str((bazi or {}).get("summary_ru") or "").strip(),
    ]
    summary = _clip(" ".join(p for p in summary_parts if p), 420)

    return {
        "contract_version": "day_personal_v1",
        "calculation_version": "day-personal-v1.2",
        "personal_astrology": personal_astro,
        "human_design": human_design,
        "bazi": bazi,
        "summary_ru": summary,
        "source_inputs": {
            "has_personal_astrology": bool(personal_astro),
            "has_human_design": bool(human_design),
            "has_bazi": bool(bazi),
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

    def _from_family(
        *,
        key: str,
        claim_prefix: str,
        layer: str,
        source_fallback: str,
        limit: int = 4,
    ) -> None:
        block = personal.get(key)
        if not isinstance(block, dict):
            return
        local: list[dict[str, Any]] = []
        for b in (block.get("beats") or [])[:limit]:
            if not isinstance(b, dict):
                continue
            text = _clip(str(b.get("story_ru") or b.get("title") or ""), 280)
            if not text:
                continue
            local.append(
                {
                    "id": f"{claim_prefix}.{b.get('id')}",
                    "kind": "personal",
                    "text": text,
                    "evidence_ids": [str(b.get("evidence_ref") or b.get("id"))],
                    "domain": None,
                    "layer": layer,
                }
            )
        summary = _clip(str(block.get("summary_ru") or ""), 280)
        if summary and not local:
            local.append(
                {
                    "id": f"{claim_prefix}.summary",
                    "kind": "personal",
                    "text": summary,
                    "evidence_ids": [source_fallback],
                    "domain": None,
                    "layer": layer,
                }
            )
        claims.extend(local)

    _from_family(
        key="personal_astrology",
        claim_prefix="claim.personal.astro",
        layer="personal_astrology",
        source_fallback="source.personal_astrology",
    )
    # HD is soft for Today (in_today=false): at most one transit beat into claims.
    _from_family(
        key="human_design",
        claim_prefix="claim.personal.hd",
        layer="human_design",
        source_fallback="source.human_design",
        limit=1,
    )
    _from_family(
        key="bazi",
        claim_prefix="claim.personal.bazi",
        layer="bazi",
        source_fallback="source.bazi",
        limit=2,
    )
    return claims
