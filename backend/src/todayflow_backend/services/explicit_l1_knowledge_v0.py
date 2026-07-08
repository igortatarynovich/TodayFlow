"""Explicit L1 knowledge promotion — meaning_events → UserActiveKnowledge (UKM write path v0).

User-stated signals (mood, focus, promise, outcome) bypass pattern gate thresholds.
Canon: USER_KNOWLEDGE_MODEL.md (fact · explicit) · PERSONAL_INTELLIGENCE_LAYER.md §3.1
"""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.db import models as db_models

logger = logging.getLogger(__name__)

EXPLICIT_L1_KNOWLEDGE_V0_CONTRACT = "explicit_l1_knowledge_v0"
EXPLICIT_L1_STATUS_ACTIVE = "active"

PROMOTABLE_EVENT_TYPES = frozenset(
    {
        "mood_selected",
        "head_topic_selected",
        "action_option_selected",
        "day_focus_outcome",
        "sphere_feedback",
        "profile_atom_correction",
    }
)

ALLOWED_EXPLICIT_CLAIM_PREFIXES = frozenset(
    {
        "explicit_mood",
        "explicit_focus",
        "explicit_promise",
        "explicit_outcome",
        "interpretation_confirm",
        "profile_correction",
    }
)

MACHINE_CLAIM_PATTERN = re.compile(r"^[a-z_]+:[a-z0-9_.-]+$")

KNOWLEDGE_ID_BY_KIND = {
    "mood": "el1-mood-current",
    "focus": "el1-focus-current",
    "promise": "el1-promise-current",
    "outcome": "el1-outcome-latest",
}


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _payload_dict(raw: Any) -> dict[str, Any]:
    return raw if isinstance(raw, dict) else {}


def _sanitize_value(value: str) -> str:
    cleaned = value.strip().lower().replace(" ", "_")
    cleaned = re.sub(r"[^a-z0-9_.-]", "", cleaned)
    return cleaned[:64]


def validate_explicit_l1_claim(claim: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(claim, str) or not claim.strip():
        return ["claim required"]
    if " " in claim:
        errors.append("prose claim not allowed")
    if not MACHINE_CLAIM_PATTERN.match(claim):
        errors.append("claim must be machine-readable key:value")
    prefix = claim.split(":", 1)[0] if ":" in claim else ""
    if prefix not in ALLOWED_EXPLICIT_CLAIM_PREFIXES:
        errors.append("claim prefix not allowed for explicit L1")
    return errors


def _extract_explicit_l1_from_event(event: db_models.MeaningEvent) -> dict[str, Any] | None:
    pl = _payload_dict(event.payload)
    event_type = str(event.event_type or "")

    if event_type == "mood_selected":
        value = _sanitize_value(str(pl.get("mood_id") or pl.get("mood") or ""))
        if not value:
            return None
        return {
            "kind": "mood",
            "knowledge_id": KNOWLEDGE_ID_BY_KIND["mood"],
            "claim": f"explicit_mood:{value}",
            "value": value,
            "summary": f"Состояние: {value}",
        }

    if event_type == "head_topic_selected":
        value = _sanitize_value(str(pl.get("topic_id") or pl.get("head_topic") or ""))
        if not value:
            return None
        return {
            "kind": "focus",
            "knowledge_id": KNOWLEDGE_ID_BY_KIND["focus"],
            "claim": f"explicit_focus:{value}",
            "value": value,
            "summary": f"Фокус: {value}",
        }

    if event_type == "action_option_selected":
        text = str(pl.get("action_text") or pl.get("promise_text") or pl.get("text") or "").strip()
        option_id = pl.get("action_option_id") or pl.get("suggestion_id")
        if text:
            slug = _sanitize_value(text[:48]) or "custom"
        elif option_id is not None:
            slug = _sanitize_value(str(option_id))
            text = slug
        else:
            idx = pl.get("action_option_index")
            if idx is None:
                return None
            slug = f"option_{idx}"
            text = slug
        return {
            "kind": "promise",
            "knowledge_id": KNOWLEDGE_ID_BY_KIND["promise"],
            "claim": f"explicit_promise:{slug}",
            "value": text[:240],
            "summary": f"Обещание дня: {text[:120]}",
        }

    if event_type == "day_focus_outcome":
        value = _sanitize_value(str(pl.get("outcome") or pl.get("day_focus_outcome") or ""))
        if not value:
            return None
        return {
            "kind": "outcome",
            "knowledge_id": KNOWLEDGE_ID_BY_KIND["outcome"],
            "claim": f"explicit_outcome:{value}",
            "value": value,
            "summary": f"Итог обещания: {value}",
        }

    if event_type == "sphere_feedback" and pl.get("interpretation_confirm") is True:
        target = _sanitize_value(str(pl.get("target") or "unknown"))
        echo = _sanitize_value(str(pl.get("echo") or pl.get("resonance") or ""))
        if not echo:
            return None
        return {
            "kind": "interpretation_confirm",
            "knowledge_id": f"el1-confirm-{target}",
            "claim": f"interpretation_confirm:{target}_{echo}",
            "value": echo,
            "summary": f"Подтверждение «{target}»: {echo}",
        }

    if event_type == "profile_atom_correction":
        knowledge_id = str(pl.get("knowledge_id") or "").strip()[:64]
        correction = _sanitize_value(str(pl.get("correction") or pl.get("verdict") or ""))
        if not knowledge_id or not correction:
            return None
        safe_id = _sanitize_value(knowledge_id.replace("el1-", "")) or "atom"
        return {
            "kind": "profile_correction",
            "knowledge_id": f"el1-verdict-{safe_id}",
            "claim": f"profile_correction:{correction}_{safe_id}",
            "value": correction,
            "summary": str(pl.get("claim_summary") or pl.get("summary") or knowledge_id)[:200],
            "source_knowledge_id": knowledge_id,
            "user_verdict": correction,
        }

    return None


def build_explicit_l1_knowledge_payload(
    event: db_models.MeaningEvent,
    extracted: dict[str, Any],
) -> dict[str, Any]:
    captured = event.event_time.isoformat() if event.event_time else _utc_now_iso()
    payload: dict[str, Any] = {
        "contract_version": EXPLICIT_L1_KNOWLEDGE_V0_CONTRACT,
        "knowledge_id": extracted["knowledge_id"],
        "knowledge_type": "fact",
        "data_class": "explicit",
        "claim": extracted["claim"],
        "value": extracted["value"],
        "summary": extracted["summary"],
        "confidence": 1.0,
        "evidence_count": 1,
        "evidence_window_days": 1,
        "evidence_signal_ids": [str(event.event_id)],
        "source_event_type": str(event.event_type),
        "source_event_id": str(event.event_id),
        "local_date": event.local_date.isoformat() if event.local_date else None,
        "status": EXPLICIT_L1_STATUS_ACTIVE,
        "created_at": captured,
        "last_confirmed_at": captured,
        "captured_at": captured,
    }
    if extracted.get("source_knowledge_id"):
        payload["source_knowledge_id"] = extracted["source_knowledge_id"]
    if extracted.get("user_verdict"):
        payload["user_verdict"] = extracted["user_verdict"]
    return payload


def validate_explicit_l1_knowledge_v0(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("contract_version") != EXPLICIT_L1_KNOWLEDGE_V0_CONTRACT:
        errors.append("invalid contract_version")
    for key in (
        "knowledge_id",
        "knowledge_type",
        "data_class",
        "claim",
        "value",
        "summary",
        "confidence",
        "evidence_count",
        "status",
        "last_confirmed_at",
    ):
        if key not in payload:
            errors.append(f"missing field: {key}")
    claim = payload.get("claim")
    if isinstance(claim, str):
        errors.extend(validate_explicit_l1_claim(claim))
    if payload.get("knowledge_type") != "fact":
        errors.append("knowledge_type must be fact")
    if payload.get("data_class") != "explicit":
        errors.append("data_class must be explicit")
    if payload.get("status") != EXPLICIT_L1_STATUS_ACTIVE:
        errors.append("status must be active")
    return errors


def upsert_explicit_l1_knowledge_v0(
    db: Session,
    *,
    user_id: int,
    payload: dict[str, Any],
    commit: bool = True,
) -> db_models.UserActiveKnowledge:
    errors = validate_explicit_l1_knowledge_v0(payload)
    if errors:
        raise ValueError("; ".join(errors))

    knowledge_id = str(payload["knowledge_id"])
    row = (
        db.query(db_models.UserActiveKnowledge)
        .filter(
            db_models.UserActiveKnowledge.user_id == user_id,
            db_models.UserActiveKnowledge.knowledge_id == knowledge_id,
        )
        .first()
    )
    if row is None:
        row = db_models.UserActiveKnowledge(
            user_id=user_id,
            knowledge_id=knowledge_id,
            status=EXPLICIT_L1_STATUS_ACTIVE,
            payload=payload,
        )
        db.add(row)
    else:
        row.status = EXPLICIT_L1_STATUS_ACTIVE
        row.payload = payload

    if commit:
        db.commit()
        db.refresh(row)
    else:
        db.flush()
    return row


def promote_meaning_event_explicit_l1_v0(
    db: Session,
    event: db_models.MeaningEvent,
    *,
    commit: bool = False,
) -> db_models.UserActiveKnowledge | None:
    """Promote one explicit L1 meaning event into UserActiveKnowledge."""
    if str(event.event_type or "") not in PROMOTABLE_EVENT_TYPES:
        return None

    extracted = _extract_explicit_l1_from_event(event)
    if extracted is None:
        return None

    payload = build_explicit_l1_knowledge_payload(event, extracted)
    return upsert_explicit_l1_knowledge_v0(
        db,
        user_id=int(event.user_id),
        payload=payload,
        commit=commit,
    )


def load_user_explicit_l1_knowledge_v0(
    db: Session,
    user_id: int,
    *,
    limit: int = 20,
) -> list[dict[str, Any]]:
    rows = (
        db.query(db_models.UserActiveKnowledge)
        .filter(
            db_models.UserActiveKnowledge.user_id == user_id,
            db_models.UserActiveKnowledge.status == EXPLICIT_L1_STATUS_ACTIVE,
        )
        .order_by(db_models.UserActiveKnowledge.updated_at.desc())
        .limit(max(1, min(limit, 100)))
        .all()
    )
    result: list[dict[str, Any]] = []
    for row in rows:
        payload = row.payload
        if not isinstance(payload, dict):
            continue
        if payload.get("contract_version") != EXPLICIT_L1_KNOWLEDGE_V0_CONTRACT:
            continue
        errors = validate_explicit_l1_knowledge_v0(payload)
        if errors:
            logger.warning("skip explicit L1 row %s: %s", row.knowledge_id, "; ".join(errors))
            continue
        result.append(payload)
    return result
