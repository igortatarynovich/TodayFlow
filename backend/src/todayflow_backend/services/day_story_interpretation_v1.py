"""Deterministic interpretation layer for day_story_v1 (before prose).

Canon: EXPLAINABLE_COMPUTATION — source → calc → interpretation → practice → text.
PR-3 P0: evidence + derived_claims + domain presence before LLM/fallback prose.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date, time
from typing import Any

DAY_STORY_INTERPRETATION_V1 = "day_story_interpretation_v1"
DAY_STORY_CALCULATION_VERSION = "day-story-interpretation-v1.2"

_DOMAIN_IDS = ("relationships", "money_work", "family")

# head_topic / intent keywords → domain evidence
_TOPIC_TO_DOMAIN: dict[str, str] = {
    "love": "relationships",
    "dialogue": "relationships",
    "relationships": "relationships",
    "близость": "relationships",
    "отношен": "relationships",
    "общен": "relationships",
    "контакт": "relationships",
    "family": "family",
    "семья": "family",
    "дом": "family",
    "money": "money_work",
    "career": "money_work",
    "деньг": "money_work",
    "работ": "money_work",
    "дела": "money_work",
    "body": "money_work",  # energy/work tempo — not a social domain claim
}


def _clip(text: str, limit: int) -> str:
    t = re.sub(r"\s+", " ", str(text or "").strip())
    if len(t) <= limit:
        return t
    return t[: limit - 1].rstrip() + "…"


def _evidence(
    *,
    evidence_id: str,
    source: str,
    claim_ref: str,
    summary: str,
    domain: str | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": evidence_id,
        "source": source,
        "claim_ref": claim_ref,
        "summary": _clip(summary, 240),
    }
    if domain:
        row["domain"] = domain
    return row


def _resolve_domain_from_topic(topic: str) -> str | None:
    low = (topic or "").strip().lower()
    if not low:
        return None
    if low in _TOPIC_TO_DOMAIN:
        return _TOPIC_TO_DOMAIN[low]
    for key, domain in _TOPIC_TO_DOMAIN.items():
        if key in low:
            return domain
    return None


def _slim_day_sky(celestial_events: dict[str, Any] | None) -> dict[str, Any]:
    """Compact sky pack for LLM — only ready story strings, capped."""
    ce = celestial_events if isinstance(celestial_events, dict) else {}
    out: dict[str, Any] = {}
    lunar = ce.get("lunar_phase") if isinstance(ce.get("lunar_phase"), dict) else {}
    if lunar:
        out["moon"] = {
            "name": _clip(lunar.get("name"), 80),
            "guidance": _clip(lunar.get("guidance") or lunar.get("themes"), 200),
        }
    ingresses = []
    for row in (ce.get("ingresses") or [])[:3]:
        if not isinstance(row, dict):
            continue
        story = _clip(row.get("story_ru"), 200)
        if not story:
            continue
        ingresses.append(
            {
                "planet_ru": _clip(row.get("planet_ru"), 40),
                "sign_ru": _clip(row.get("sign_ru"), 40),
                "story_ru": story,
            }
        )
    if ingresses:
        out["ingresses"] = ingresses
    aspects = []
    for row in (ce.get("sky_aspects") or [])[:2]:
        if not isinstance(row, dict):
            continue
        story = _clip(row.get("story_ru"), 200)
        if not story:
            continue
        aspects.append({"title": _clip(row.get("title"), 80), "story_ru": story})
    if aspects:
        out["sky_aspects"] = aspects
    retros = []
    for row in (ce.get("retrogrades") or [])[:2]:
        if not isinstance(row, dict):
            continue
        story = _clip(row.get("story_ru"), 200)
        if not story:
            continue
        retros.append({"planet_ru": _clip(row.get("planet_ru"), 40), "story_ru": story})
    if retros:
        out["retrogrades"] = retros
    return out


def build_day_story_interpretation_v1(
    *,
    day_engine_brief: dict[str, Any] | None,
    ritual_context: dict[str, Any] | None = None,
    intent_slice: dict[str, Any] | None = None,
    rhythm_context: dict[str, Any] | None = None,
    color: str = "",
    stone: str = "",
    celestial_events: dict[str, Any] | None = None,
    color_symbol: dict[str, Any] | None = None,
    stone_symbol: dict[str, Any] | None = None,
    fingerprint: str | None = None,
    locale: str = "ru",
    target_date: date | None = None,
    birth_date: date | None = None,
    birth_time: time | None = None,
    birth_lat: float | None = None,
    birth_lon: float | None = None,
    lat: float | None = None,
    lon: float | None = None,
    timezone: str | None = None,
    electional_requested: bool = False,
    electional_time: time | None = None,
    electional_question: str | None = None,
) -> dict[str, Any]:
    """Build structured interpretation + evidence from known inputs (no LLM)."""
    brief = day_engine_brief if isinstance(day_engine_brief, dict) else {}
    ritual = ritual_context if isinstance(ritual_context, dict) else {}
    intent = intent_slice if isinstance(intent_slice, dict) else {}
    rhythm = rhythm_context if isinstance(rhythm_context, dict) else {}
    ce = celestial_events if isinstance(celestial_events, dict) else {}
    color_sym = color_symbol if isinstance(color_symbol, dict) else {}
    stone_sym = stone_symbol if isinstance(stone_symbol, dict) else {}

    from todayflow_backend.services.day_foundation_v1 import (
        build_day_foundation_v1,
        foundation_to_interpretation_claims,
    )
    from todayflow_backend.services.day_personal_v1 import (
        build_day_personal_v1,
        personal_to_interpretation_claims,
    )

    resolved_date = target_date or date.today()
    # Foundation always runs: date-only Sources (weekday, universal day) do not need sky.
    day_foundation = build_day_foundation_v1(
        ce,
        target_date=resolved_date,
        birth_date=birth_date,
        lat=lat,
        lon=lon,
        timezone=timezone,
        locale=locale or "ru",
    )
    # Ritual may carry an explicit electional request (situational L3).
    ritual_electional = bool(ritual.get("electional_requested") or electional_requested)
    ritual_q = electional_question or (
        str(ritual.get("electional_question") or "").strip() or None
    )
    ritual_t = electional_time
    if ritual_t is None and ritual.get("electional_time"):
        raw_t = str(ritual.get("electional_time") or "")
        try:
            parts = [int(x) for x in raw_t.split(":")[:3]]
            while len(parts) < 3:
                parts.append(0)
            ritual_t = time(parts[0] % 24, parts[1] % 60, parts[2] % 60)
        except ValueError:
            ritual_t = None
    day_personal = build_day_personal_v1(
        ce,
        target_date=resolved_date,
        birth_date=birth_date,
        birth_time=birth_time,
        birth_lat=birth_lat,
        birth_lon=birth_lon,
        lat=lat,
        lon=lon,
        timezone=timezone,
        locale=locale or "ru",
        electional_requested=ritual_electional,
        electional_time=ritual_t,
        electional_question=ritual_q,
    )

    evidence: list[dict[str, Any]] = []
    claims: list[dict[str, Any]] = []
    domain_evidence: dict[str, list[str]] = {d: [] for d in _DOMAIN_IDS}
    color_name = str(color_sym.get("name") or color or "").strip()
    stone_name = str(stone_sym.get("name") or stone or "").strip()
    source_inputs: dict[str, Any] = {
        "has_day_engine_brief": bool(brief),
        "brief_contract": brief.get("contract_version"),
        "has_ritual_card": bool(ritual.get("tarot_main_id") or ritual.get("tarot_name_ru")),
        "has_ritual_number": ritual.get("numerology_value") is not None,
        "has_mood": bool(ritual.get("mood") or brief.get("thread_mood")),
        "has_head_topic": bool(ritual.get("head_topic") or brief.get("thread_head_topic")),
        "has_intent": bool(intent.get("what_matters_line") or intent.get("morning_focus")),
        "has_rhythm": bool(rhythm),
        "has_color": bool(color_name),
        "has_stone": bool(stone_name),
        "has_lunar": bool(isinstance(ce.get("lunar_phase"), dict) and ce.get("lunar_phase")),
        "has_ingress": bool(ce.get("ingresses")),
        "has_sky_aspect": bool(ce.get("sky_aspects")),
        "has_retro": bool(ce.get("retrogrades")),
        "has_day_foundation": bool(
            isinstance(day_foundation, dict)
            and (
                (day_foundation.get("source_inputs") or {}).get("has_essence")
                or (day_foundation.get("source_inputs") or {}).get("has_numerology")
                or (day_foundation.get("source_inputs") or {}).get("has_weekday")
                or (day_foundation.get("source_inputs") or {}).get("has_astro")
                or (day_foundation.get("source_inputs") or {}).get("has_lunar")
                or (day_foundation.get("source_inputs") or {}).get("has_seasonal")
                or (day_foundation.get("source_inputs") or {}).get("has_planetary_hours")
                or (day_foundation.get("source_inputs") or {}).get("has_panchanga")
                or (day_foundation.get("source_inputs") or {}).get("has_chinese")
                or (day_foundation.get("source_inputs") or {}).get("has_mayan")
            )
        ),
        "locale": (locale or "ru")[:8],
        "target_date": resolved_date.isoformat(),
        "has_birth_date": birth_date is not None,
        "has_geo": lat is not None and lon is not None,
        "has_day_personal": bool(
            isinstance(day_personal, dict)
            and (
                (day_personal.get("source_inputs") or {}).get("has_personal_astrology")
                or (day_personal.get("source_inputs") or {}).get("has_human_design")
                or (day_personal.get("source_inputs") or {}).get("has_bazi")
                or (day_personal.get("source_inputs") or {}).get("has_vedic_personal")
            )
        ),
    }

    def add_claim(
        claim_id: str,
        text: str,
        *,
        evidence_ids: list[str],
        domain: str | None = None,
        kind: str = "observation",
    ) -> None:
        claims.append(
            {
                "id": claim_id,
                "kind": kind,
                "text": _clip(text, 280),
                "evidence_ids": evidence_ids,
                "domain": domain,
            }
        )

    # Brief anchors — prefer foundation essence as day axis when present.
    essence = (
        day_foundation.get("essence")
        if isinstance(day_foundation, dict) and isinstance(day_foundation.get("essence"), dict)
        else {}
    )
    foundation_axis = str(essence.get("theme") or "").strip()
    foundation_story = str(essence.get("story_ru") or "").strip()
    anchor = foundation_axis or str(brief.get("anchor_summary") or "").strip()
    if foundation_axis or foundation_story:
        eid = "ev.foundation.essence"
        evidence.append(
            _evidence(
                evidence_id=eid,
                source="day_foundation_v1.essence",
                claim_ref="day_axis",
                summary=foundation_story or foundation_axis,
            )
        )
        add_claim(
            "claim.day_axis",
            foundation_story or foundation_axis,
            evidence_ids=[eid],
            kind="axis",
        )
    elif anchor:
        eid = "ev.brief.anchor"
        evidence.append(
            _evidence(
                evidence_id=eid,
                source="day_narrative_brief_v0.anchor_summary",
                claim_ref="day_axis",
                summary=anchor,
            )
        )
        add_claim("claim.day_axis", anchor, evidence_ids=[eid], kind="axis")

    # Foundation layer claims (astro / lunar beats) — after axis.
    if isinstance(day_foundation, dict):
        for fc in foundation_to_interpretation_claims(day_foundation):
            if fc.get("id") == "claim.foundation.essence":
                continue  # already as claim.day_axis
            claims.append(fc)
            evidence.append(
                _evidence(
                    evidence_id=f"ev.{fc.get('id')}",
                    source=str((fc.get("evidence_ids") or ["day_foundation_v1"])[0]),
                    claim_ref=str(fc.get("layer") or "sky"),
                    summary=str(fc.get("text") or ""),
                )
            )

    # Personal L3 activation (natal transits) — never mixed into Foundation essence.
    if isinstance(day_personal, dict):
        for pc in personal_to_interpretation_claims(day_personal):
            claims.append(pc)
            evidence.append(
                _evidence(
                    evidence_id=f"ev.{pc.get('id')}",
                    source=str((pc.get("evidence_ids") or ["day_personal_v1"])[0]),
                    claim_ref="personal",
                    summary=str(pc.get("text") or ""),
                )
            )
    do_hint = str(brief.get("do_hint") or "").strip()
    if do_hint:
        eid = "ev.brief.do_hint"
        evidence.append(
            _evidence(
                evidence_id=eid,
                source="day_narrative_brief_v0.do_hint",
                claim_ref="primary_move",
                summary=do_hint,
            )
        )
        add_claim("claim.primary_move", do_hint, evidence_ids=[eid], kind="action")

    avoid_hint = str(brief.get("avoid_hint") or "").strip()
    if avoid_hint:
        eid = "ev.brief.avoid_hint"
        evidence.append(
            _evidence(
                evidence_id=eid,
                source="day_narrative_brief_v0.avoid_hint",
                claim_ref="abstain",
                summary=avoid_hint,
            )
        )
        add_claim("claim.abstain", avoid_hint, evidence_ids=[eid], kind="risk")

    tempo = str(brief.get("tempo_hint") or "").strip()
    if tempo:
        eid = "ev.brief.tempo"
        evidence.append(
            _evidence(
                evidence_id=eid,
                source="day_narrative_brief_v0.tempo_hint",
                claim_ref="tempo",
                summary=tempo,
            )
        )
        add_claim("claim.tempo", tempo, evidence_ids=[eid], kind="tempo")

    # Ritual / topic → domain evidence
    head_topic = str(
        ritual.get("head_topic") or brief.get("thread_head_topic") or ""
    ).strip()
    domain_from_topic = _resolve_domain_from_topic(head_topic)
    if head_topic and domain_from_topic:
        eid = "ev.ritual.head_topic"
        evidence.append(
            _evidence(
                evidence_id=eid,
                source="ritual.head_topic",
                claim_ref="head_topic",
                summary=head_topic,
                domain=domain_from_topic,
            )
        )
        domain_evidence[domain_from_topic].append(eid)
        add_claim(
            f"claim.domain.{domain_from_topic}.topic",
            f"Тема дня касается сферы «{domain_from_topic}»: {head_topic}",
            evidence_ids=[eid],
            domain=domain_from_topic,
            kind="domain_focus",
        )

    intent_line = str(intent.get("what_matters_line") or intent.get("morning_focus") or "").strip()
    domain_from_intent = _resolve_domain_from_topic(intent_line)
    if intent_line and domain_from_intent:
        eid = "ev.intent.matters"
        evidence.append(
            _evidence(
                evidence_id=eid,
                source="intent_layer_v0",
                claim_ref="what_matters",
                summary=intent_line,
                domain=domain_from_intent,
            )
        )
        domain_evidence[domain_from_intent].append(eid)
        add_claim(
            f"claim.domain.{domain_from_intent}.intent",
            intent_line,
            evidence_ids=[eid],
            domain=domain_from_intent,
            kind="domain_focus",
        )

    mood = str(ritual.get("mood") or brief.get("thread_mood") or "").strip()
    if mood:
        eid = "ev.ritual.mood"
        evidence.append(
            _evidence(
                evidence_id=eid,
                source="ritual.mood",
                claim_ref="mood",
                summary=mood,
            )
        )
        add_claim("claim.mood", f"Настроение чек-ина: {mood}", evidence_ids=[eid], kind="mood")

    if ritual.get("tarot_name_ru") or ritual.get("tarot_main_id"):
        eid = "ev.ritual.card"
        card = str(ritual.get("tarot_name_ru") or ritual.get("tarot_main_id") or "")
        evidence.append(
            _evidence(
                evidence_id=eid,
                source="ritual.tarot",
                claim_ref="day_card",
                summary=f"Карта дня: {card}",
            )
        )
        add_claim("claim.day_card", f"Карта дня учтена как дополнение: {card}", evidence_ids=[eid], kind="symbol")

    if ritual.get("numerology_value") is not None:
        eid = "ev.ritual.number"
        num = str(ritual.get("numerology_value"))
        evidence.append(
            _evidence(
                evidence_id=eid,
                source="ritual.numerology",
                claim_ref="day_number",
                summary=f"Число дня: {num}",
            )
        )
        add_claim("claim.day_number", f"Число дня: {num}", evidence_ids=[eid], kind="symbol")

    # --- Sky evidence: when foundation is present, beats already cover sky claims ---
    use_legacy_sky_claims = not source_inputs.get("has_day_foundation")
    if use_legacy_sky_claims:
        lunar = ce.get("lunar_phase") if isinstance(ce.get("lunar_phase"), dict) else {}
        lunar_body = str(lunar.get("guidance") or lunar.get("themes") or "").strip()
        lunar_name = str(lunar.get("name") or "").strip()
        if lunar_name or lunar_body:
            eid = "ev.sky.moon"
            summary = f"{lunar_name}: {lunar_body}".strip(": ").strip() if lunar_body else lunar_name
            evidence.append(
                _evidence(
                    evidence_id=eid,
                    source="celestial_events.lunar_phase",
                    claim_ref="moon",
                    summary=summary,
                )
            )
            add_claim("claim.sky.moon", summary, evidence_ids=[eid], kind="sky")

        for idx, row in enumerate((ce.get("ingresses") or [])[:3]):
            if not isinstance(row, dict):
                continue
            story = str(row.get("story_ru") or "").strip()
            if not story:
                continue
            planet = str(row.get("planet") or row.get("planet_ru") or idx)
            eid = f"ev.sky.ingress.{planet}"
            evidence.append(
                _evidence(
                    evidence_id=eid,
                    source="celestial_events.ingresses",
                    claim_ref="ingress",
                    summary=story,
                )
            )
            add_claim(f"claim.sky.ingress.{planet}", story, evidence_ids=[eid], kind="sky")

        for row in (ce.get("sky_aspects") or [])[:2]:
            if not isinstance(row, dict):
                continue
            story = str(row.get("story_ru") or "").strip()
            if not story:
                continue
            aid = str(row.get("id") or row.get("title") or "aspect")[:40]
            eid = f"ev.sky.aspect.{aid}"
            evidence.append(
                _evidence(
                    evidence_id=eid,
                    source="celestial_events.sky_aspects",
                    claim_ref="sky_aspect",
                    summary=story,
                )
            )
            add_claim(f"claim.sky.aspect.{aid}", story, evidence_ids=[eid], kind="sky")

        for row in (ce.get("retrogrades") or [])[:2]:
            if not isinstance(row, dict):
                continue
            story = str(row.get("story_ru") or "").strip()
            if not story:
                continue
            planet = str(row.get("planet") or row.get("planet_ru") or "retro")
            eid = f"ev.sky.retro.{planet}"
            evidence.append(
                _evidence(
                    evidence_id=eid,
                    source="celestial_events.retrogrades",
                    claim_ref="retrograde",
                    summary=story,
                )
            )
            add_claim(f"claim.sky.retro.{planet}", story, evidence_ids=[eid], kind="sky")

    # --- Color / stone ready copy ---
    if color_name:
        eid = "ev.talisman.color"
        evidence.append(
            _evidence(
                evidence_id=eid,
                source="celestial_events.daily_symbols.color",
                claim_ref="color",
                summary=color_name,
            )
        )
        benefit = str(color_sym.get("benefit_ru") or color_sym.get("story_ru") or "").strip()
        if benefit:
            eid_b = "ev.talisman.color.benefit"
            evidence.append(
                _evidence(
                    evidence_id=eid_b,
                    source="celestial_events.daily_symbols.color.benefit_ru",
                    claim_ref="color_why",
                    summary=benefit,
                )
            )
            add_claim(
                "claim.talisman.color_why",
                f"Цвет дня — {color_name}: {benefit}",
                evidence_ids=[eid, eid_b],
                kind="support",
            )
        avoid_c = str(color_sym.get("avoid_color_ru") or "").strip()
        avoid_w = str(color_sym.get("avoid_why_ru") or "").strip()
        if avoid_c and avoid_w:
            eid_a = "ev.talisman.color.avoid"
            evidence.append(
                _evidence(
                    evidence_id=eid_a,
                    source="celestial_events.daily_symbols.color.avoid",
                    claim_ref="color_avoid",
                    summary=f"{avoid_c}: {avoid_w}",
                )
            )
            add_claim(
                "claim.talisman.color_avoid",
                f"Сегодня лучше не {avoid_c}: {avoid_w}",
                evidence_ids=[eid_a],
                kind="support",
            )

    if stone_name:
        eid = "ev.talisman.stone"
        evidence.append(
            _evidence(
                evidence_id=eid,
                source="celestial_events.daily_symbols.stone",
                claim_ref="stone",
                summary=stone_name,
            )
        )
        stone_story = str(stone_sym.get("story_ru") or "").strip()
        if stone_story:
            eid_s = "ev.talisman.stone.story"
            evidence.append(
                _evidence(
                    evidence_id=eid_s,
                    source="celestial_events.daily_symbols.stone.story_ru",
                    claim_ref="stone_why",
                    summary=stone_story,
                )
            )
            add_claim(
                "claim.talisman.stone_why",
                f"Камень-опора — {stone_name}: {stone_story}",
                evidence_ids=[eid, eid_s],
                kind="support",
            )

    present_domains = [d for d in _DOMAIN_IDS if domain_evidence[d]]
    absent_domains = [d for d in _DOMAIN_IDS if d not in present_domains]

    limitations: list[str] = []
    if not present_domains:
        limitations.append(
            "Нет явного сигнала по сферам (отношения / работа / семья) — доменные блоки не заполняются выдуманным текстом."
        )
    else:
        for d in absent_domains:
            limitations.append(f"Сфера «{d}» без личного сигнала сегодня — блок отсутствует.")
    if not source_inputs["has_ritual_card"]:
        limitations.append("Карта дня не раскрыта или отсутствует — не упоминать карту.")
    if not source_inputs["has_ritual_number"]:
        limitations.append("Число дня не раскрыто или отсутствует — не упоминать число.")
    if not anchor and not do_hint:
        limitations.append("Краткий бриф дня пуст — story строится из минимума известных сигналов.")
    if not source_inputs["has_color"] or not any(c.get("id") == "claim.talisman.color_why" for c in claims):
        limitations.append("Нет готового why цвета — talisman.note / supports_story без выдуманной связи небо→цвет.")
    if not any(str(c.get("kind") or "") == "sky" for c in claims):
        limitations.append("Нет celestial story_ru — не сочинять астрологические объяснения.")

    confidence = 0.35
    if evidence:
        confidence = min(0.92, 0.35 + 0.08 * len(evidence))
    if present_domains:
        confidence = min(0.95, confidence + 0.05 * len(present_domains))
    if not fingerprint and not evidence:
        confidence = 0.2

    interpretation = {
        "contract_version": DAY_STORY_INTERPRETATION_V1,
        "calculation_version": DAY_STORY_CALCULATION_VERSION,
        "source_inputs": source_inputs,
        "evidence": evidence,
        "derived_claims": claims,
        "domain_evidence_ids": domain_evidence,
        "domains_present": present_domains,
        "domains_absent": absent_domains,
        "confidence": round(confidence, 3),
        "limitations": limitations,
        "fingerprint": fingerprint or "",
        "day_sky": _slim_day_sky(ce),
        "day_foundation": day_foundation,
        "day_personal": day_personal,
    }
    return interpretation


def interpretation_fingerprint(interpretation: dict[str, Any]) -> str:
    payload = {
        "cv": interpretation.get("calculation_version"),
        "claims": [c.get("id") for c in (interpretation.get("derived_claims") or [])],
        "evidence": [e.get("id") for e in (interpretation.get("evidence") or [])],
        "domains": interpretation.get("domains_present"),
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]
