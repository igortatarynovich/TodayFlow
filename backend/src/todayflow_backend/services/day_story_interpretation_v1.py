"""Deterministic interpretation layer for day_story_v1 (before prose).

Canon: EXPLAINABLE_COMPUTATION — source → calc → interpretation → practice → text.
PR-3 P0: evidence + derived_claims + domain presence before LLM/fallback prose.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

DAY_STORY_INTERPRETATION_V1 = "day_story_interpretation_v1"
DAY_STORY_CALCULATION_VERSION = "day-story-interpretation-v1.0"

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


def build_day_story_interpretation_v1(
    *,
    day_engine_brief: dict[str, Any] | None,
    ritual_context: dict[str, Any] | None = None,
    intent_slice: dict[str, Any] | None = None,
    rhythm_context: dict[str, Any] | None = None,
    color: str = "",
    stone: str = "",
    fingerprint: str | None = None,
    locale: str = "ru",
) -> dict[str, Any]:
    """Build structured interpretation + evidence from known inputs (no LLM)."""
    brief = day_engine_brief if isinstance(day_engine_brief, dict) else {}
    ritual = ritual_context if isinstance(ritual_context, dict) else {}
    intent = intent_slice if isinstance(intent_slice, dict) else {}
    rhythm = rhythm_context if isinstance(rhythm_context, dict) else {}

    evidence: list[dict[str, Any]] = []
    claims: list[dict[str, Any]] = []
    domain_evidence: dict[str, list[str]] = {d: [] for d in _DOMAIN_IDS}
    source_inputs: dict[str, Any] = {
        "has_day_engine_brief": bool(brief),
        "brief_contract": brief.get("contract_version"),
        "has_ritual_card": bool(ritual.get("tarot_main_id") or ritual.get("tarot_name_ru")),
        "has_ritual_number": ritual.get("numerology_value") is not None,
        "has_mood": bool(ritual.get("mood") or brief.get("thread_mood")),
        "has_head_topic": bool(ritual.get("head_topic") or brief.get("thread_head_topic")),
        "has_intent": bool(intent.get("what_matters_line") or intent.get("morning_focus")),
        "has_rhythm": bool(rhythm),
        "has_color": bool(str(color or "").strip()),
        "has_stone": bool(str(stone or "").strip()),
        "locale": (locale or "ru")[:8],
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

    # Brief anchors
    anchor = str(brief.get("anchor_summary") or "").strip()
    if anchor:
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

    if color.strip():
        eid = "ev.talisman.color"
        evidence.append(
            _evidence(
                evidence_id=eid,
                source="morning.lucky_color",
                claim_ref="color",
                summary=color.strip(),
            )
        )
    if stone.strip():
        eid = "ev.talisman.stone"
        evidence.append(
            _evidence(
                evidence_id=eid,
                source="morning.lucky_stone",
                claim_ref="stone",
                summary=stone.strip(),
            )
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
