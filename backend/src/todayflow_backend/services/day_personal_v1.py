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
    lat: float | None = None,
    lon: float | None = None,
    locale: str = "ru",
    electional_requested: bool = False,
    electional_time: time | None = None,
    electional_question: str | None = None,
    ephemeris: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Collect personal Source Families into a wire pack for Today / interpretation."""
    from todayflow_backend.services.day_sources.ephemeris_bridge import ephemeris_from_celestial

    ce = celestial_events if isinstance(celestial_events, dict) else {}
    eph = ephemeris if isinstance(ephemeris, dict) else ephemeris_from_celestial(ce)
    inputs = DaySourceInputs(
        target_date=target_date or date.today(),
        timezone=timezone,
        lat=lat,
        lon=lon,
        birth_date=birth_date,
        birth_time=birth_time,
        birth_lat=birth_lat,
        birth_lon=birth_lon,
        celestial_events=ce or None,
        ephemeris=eph,
        locale=locale,
        electional_requested=electional_requested,
        electional_time=electional_time,
        electional_question=electional_question,
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
    vedic_personal = _ok_payload("vedic_personal")
    kabbalah = _ok_payload("kabbalah_letter")
    electional = _ok_payload("electional_horary")

    summary_parts = [
        str((personal_astro or {}).get("summary_ru") or "").strip(),
        str((human_design or {}).get("summary_ru") or "").strip(),
        str((bazi or {}).get("summary_ru") or "").strip(),
        str((vedic_personal or {}).get("summary_ru") or "").strip(),
    ]
    if electional:
        summary_parts.append(str(electional.get("summary_ru") or "").strip())
    summary = _clip(" ".join(p for p in summary_parts if p), 480)

    electional_row = sources.get("electional_horary") if isinstance(sources, dict) else None

    return {
        "contract_version": "day_personal_v1",
        "calculation_version": "day-personal-v1.6",
        "personal_astrology": personal_astro,
        "human_design": human_design,
        "bazi": bazi,
        "vedic_personal": vedic_personal,
        "kabbalah_letter": kabbalah,
        "electional_horary": electional,
        "summary_ru": summary,
        "source_inputs": {
            "has_personal_astrology": bool(personal_astro),
            "has_human_design": bool(human_design),
            "has_bazi": bool(bazi),
            "has_vedic_personal": bool(vedic_personal),
            "has_kabbalah_letter": bool(kabbalah),
            "has_electional_horary": bool(electional),
            "electional_status": (
                electional_row.get("status")
                if isinstance(electional_row, dict)
                else None
            ),
            "ok_family_ids": list(bundle.get("ok_family_ids") or []),
            "unavailable": {
                fid: row.get("unavailable_reason")
                for fid, row in sources.items()
                if isinstance(row, dict) and row.get("status") in {"unavailable", "skipped"}
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

    def _beat_claim(
        *,
        beat: dict[str, Any],
        claim_prefix: str,
        layer: str,
    ) -> dict[str, Any] | None:
        text = _clip(str(beat.get("story_ru") or beat.get("title") or ""), 280)
        if not text:
            return None
        return {
            "id": f"{claim_prefix}.{beat.get('id')}",
            "kind": "personal",
            "text": text,
            "evidence_ids": [str(beat.get("evidence_ref") or beat.get("id"))],
            "domain": None,
            "layer": layer,
        }

    def _from_family(
        *,
        key: str,
        claim_prefix: str,
        layer: str,
        source_fallback: str,
        limit: int = 4,
        prefer_kinds: tuple[str, ...] = (),
        natal_transit_cap: int | None = None,
    ) -> None:
        block = personal.get(key)
        if not isinstance(block, dict):
            return
        beats = [b for b in (block.get("beats") or []) if isinstance(b, dict)]
        ordered: list[dict[str, Any]] = []
        seen: set[int] = set()

        def _take(b: dict[str, Any]) -> None:
            i = id(b)
            if i in seen:
                return
            seen.add(i)
            ordered.append(b)

        for kind in prefer_kinds:
            for b in beats:
                if str(b.get("kind") or "") == kind:
                    _take(b)
        transit_n = 0
        for b in beats:
            kind = str(b.get("kind") or "")
            if kind == "natal_transit":
                if natal_transit_cap is not None and transit_n >= natal_transit_cap:
                    continue
                transit_n += 1
            _take(b)

        local: list[dict[str, Any]] = []
        for b in ordered[:limit]:
            claim = _beat_claim(beat=b, claim_prefix=claim_prefix, layer=layer)
            if claim:
                local.append(claim)
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

    # Soft personal caps first so house_rulers / time_lords reach Today claims
    # even when natal transits fill the beat list.
    _from_family(
        key="personal_astrology",
        claim_prefix="claim.personal.astro",
        layer="personal_astrology",
        source_fallback="source.personal_astrology",
        limit=5,
        prefer_kinds=(
            "house_rulers_chains",
            "time_lords",
            "profection_annual",
            "solar_return",
            "secondary_progression",
            "planet_returns",
        ),
        natal_transit_cap=1,
    )
    # HD soft: type/authority first, then channel + gate activation.
    _from_family(
        key="human_design",
        claim_prefix="claim.personal.hd",
        layer="human_design",
        source_fallback="source.human_design",
        limit=2,
        prefer_kinds=(
            "type_authority",
            "profile_lines_cross",
            "channel",
            "transit_hits_natal_gate",
            "transit_gate",
        ),
    )
    _from_family(
        key="bazi",
        claim_prefix="claim.personal.bazi",
        layer="bazi",
        source_fallback="source.bazi",
        limit=2,
    )
    _from_family(
        key="vedic_personal",
        claim_prefix="claim.personal.vedic",
        layer="vedic_personal",
        source_fallback="source.vedic_personal",
        limit=2,
    )
    # Only present when user explicitly requested electional/horary.
    _from_family(
        key="electional_horary",
        claim_prefix="claim.personal.electional",
        layer="electional_horary",
        source_fallback="source.electional_horary",
        limit=2,
    )
    return claims
