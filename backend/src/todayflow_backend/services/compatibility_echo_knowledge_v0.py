"""Compatibility echo / scenario signals → hypothesis atoms (UKM write path v0).

Echo «точно / частично / мимо» and scenario switches are learning signals — not facts.
Promotes to inferred_knowledge_v0 (hypothesis, confirmation_required).

Canon: USER_KNOWLEDGE_MODEL.md · KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md (channel I)
"""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.db import models as db_models
from todayflow_backend.services.meaning_derived_knowledge_v0 import (
    INFERRED_KNOWLEDGE_V0_CONTRACT,
    INFERRED_STATUS_ACTIVE,
    upsert_inferred_knowledge_v0,
    validate_inferred_knowledge_v0,
)

logger = logging.getLogger(__name__)

COMPATIBILITY_ECHO_KNOWLEDGE_V0_CONTRACT = "compatibility_echo_knowledge_v0"

PROMOTABLE_COMPAT_EVENT_TYPES = frozenset(
    {
        "compatibility_echo",
        "compatibility_scenario_switch",
    }
)

_DEEP_BLOCK_KEYS = frozenset({"emotions", "communication", "conflicts", "sexuality", "long_term"})
_ECHO_LABELS = {"yes": "точно", "partial": "частично", "no": "мимо"}


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _payload_dict(raw: Any) -> dict[str, Any]:
    return raw if isinstance(raw, dict) else {}


def _sanitize(value: str) -> str:
    cleaned = value.strip().lower().replace(" ", "_")
    return re.sub(r"[^a-z0-9_.-]", "", cleaned)[:64]


def _resolve_slot(payload: dict[str, Any]) -> tuple[str, str]:
    """Return (slot_id, slot_label) for claim + summary."""
    block_key = str(payload.get("block_key") or "").strip().lower()
    if block_key in _DEEP_BLOCK_KEYS:
        labels = {
            "emotions": "эмоции",
            "communication": "коммуникация",
            "conflicts": "конфликты",
            "sexuality": "интимность",
            "long_term": "долгая дистанция",
        }
        return block_key, labels.get(block_key, block_key)

    target = str(payload.get("target") or "").strip()
    if target.startswith("deep:"):
        key = target.split(":", 1)[1].lower()
        if key in _DEEP_BLOCK_KEYS:
            return _resolve_slot({**payload, "block_key": key})
    if target.startswith("scenario:"):
        sid = _sanitize(target.split(":", 1)[1])
        return f"scenario_{sid}", f"сценарий «{sid}»"
    if target in {"main_thought", "strongest_resource", "main_risk"}:
        labels = {
            "main_thought": "главная мысль",
            "strongest_resource": "сильный ресурс",
            "main_risk": "главный риск",
        }
        return target, labels[target]
    return "general", "разбор совместимости"


def _confidence_for_echo(echo: str, evidence_count: int) -> float:
    base = {"yes": 0.58, "partial": 0.48, "no": 0.52}.get(echo, 0.45)
    return round(min(0.86, base + max(0, evidence_count - 1) * 0.04), 3)


def _summary_for_echo(*, echo: str, slot_label: str, format_id: str | None) -> str:
    echo_word = _ECHO_LABELS.get(echo, echo)
    fmt = f" (сценарий «{format_id}»)" if format_id else ""
    if echo == "yes":
        return f"Отмечает «{echo_word}» для блока «{slot_label}» в совместимости{fmt}."
    if echo == "no":
        return f"Считает «{echo_word}» про блок «{slot_label}» в совместимости{fmt}."
    return f"Частично узнаёт себя в блоке «{slot_label}»{fmt}."


def _build_echo_payload(
    event: db_models.MeaningEvent,
    *,
    slot_id: str,
    slot_label: str,
    echo: str,
    format_id: str | None,
    evidence_count: int,
    evidence_event_ids: list[str],
) -> dict[str, Any]:
    slug = _sanitize(f"{slot_id}_{echo}")
    captured = _utc_now_iso()
    return {
        "contract_version": INFERRED_KNOWLEDGE_V0_CONTRACT,
        "knowledge_id": f"inf-compat-echo-{slug}",
        "knowledge_type": "hypothesis",
        "data_class": "inferred",
        "claim": f"behavior_hypothesis:compat_echo_{slug}",
        "value": slug,
        "summary": _summary_for_echo(echo=echo, slot_label=slot_label, format_id=format_id),
        "confidence": _confidence_for_echo(echo, evidence_count),
        "evidence_count": evidence_count,
        "evidence_window_days": 28,
        "evidence_signal_ids": evidence_event_ids[:20],
        "evidence_chain": [
            {
                "event_id": str(event.event_id),
                "event_type": str(event.event_type),
                "echo": echo,
                "slot_id": slot_id,
                "format_id": format_id,
            }
        ],
        "confirmation_required": True,
        "confirmation_stage": "hypothesis",
        "status": INFERRED_STATUS_ACTIVE,
        "created_at": captured,
        "last_confirmed_at": captured,
        "captured_at": captured,
        "source": COMPATIBILITY_ECHO_KNOWLEDGE_V0_CONTRACT,
        "domain": "compatibility",
        "decision_relevance": 0.54 if echo == "yes" else 0.48,
    }


def _build_scenario_switch_payload(
    event: db_models.MeaningEvent,
    *,
    to_format: str,
    evidence_count: int,
    evidence_event_ids: list[str],
) -> dict[str, Any]:
    slug = _sanitize(to_format)
    captured = _utc_now_iso()
    return {
        "contract_version": INFERRED_KNOWLEDGE_V0_CONTRACT,
        "knowledge_id": f"inf-compat-interest-{slug}",
        "knowledge_type": "hypothesis",
        "data_class": "inferred",
        "claim": f"behavior_hypothesis:compat_interest_{slug}",
        "value": slug,
        "summary": f"Переключается на сценарий совместимости «{to_format}» ({evidence_count} раз).",
        "confidence": round(min(0.82, 0.5 + evidence_count * 0.05), 3),
        "evidence_count": evidence_count,
        "evidence_window_days": 28,
        "evidence_signal_ids": evidence_event_ids[:20],
        "evidence_chain": [
            {
                "event_id": str(event.event_id),
                "event_type": "compatibility_scenario_switch",
                "to_format_id": to_format,
            }
        ],
        "confirmation_required": True,
        "confirmation_stage": "hypothesis",
        "status": INFERRED_STATUS_ACTIVE,
        "created_at": captured,
        "last_confirmed_at": captured,
        "captured_at": captured,
        "source": COMPATIBILITY_ECHO_KNOWLEDGE_V0_CONTRACT,
        "domain": "compatibility",
        "decision_relevance": 0.46,
    }


def _upsert_with_merge(
    db: Session,
    *,
    user_id: int,
    payload: dict[str, Any],
    event_id: str,
    event_type: str,
    echo: str | None = None,
    to_format: str | None = None,
) -> db_models.UserActiveKnowledge | None:
    errors = validate_inferred_knowledge_v0(payload)
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
            status=INFERRED_STATUS_ACTIVE,
            payload=payload,
        )
        db.add(row)
        db.flush()
        return row

    existing = row.payload if isinstance(row.payload, dict) else {}
    if existing.get("user_verdict") in {"confirm", "reject", "partial"}:
        return None

    prev_count = int(existing.get("evidence_count") or 0)
    new_count = prev_count + 1
    ids = [str(x) for x in (existing.get("evidence_signal_ids") or []) if x]
    if event_id and event_id not in ids:
        ids.append(event_id)

    merged = dict(payload)
    merged["evidence_count"] = new_count
    merged["evidence_signal_ids"] = ids[:20]
    merged["created_at"] = existing.get("created_at") or merged.get("created_at")
    merged["confidence"] = (
        _confidence_for_echo(str(echo or "partial"), new_count)
        if event_type == "compatibility_echo"
        else round(min(0.82, 0.5 + new_count * 0.05), 3)
    )

    if event_type == "compatibility_scenario_switch" and to_format:
        merged["summary"] = (
            f"Переключается на сценарий совместимости «{to_format}» ({new_count} раз)."
        )

    row.payload = merged
    row.status = INFERRED_STATUS_ACTIVE
    db.flush()
    return row


def promote_compatibility_echo_knowledge_v0(
    db: Session,
    event: db_models.MeaningEvent,
    *,
    commit: bool = False,
) -> db_models.UserActiveKnowledge | None:
    """Promote one compatibility echo / scenario switch into hypothesis atom."""
    event_type = str(event.event_type or "")
    if event_type not in PROMOTABLE_COMPAT_EVENT_TYPES:
        return None

    pl = _payload_dict(event.payload)
    event_id = str(event.event_id or "")

    if event_type == "compatibility_echo":
        echo = str(pl.get("echo") or "").strip().lower()
        if echo not in {"yes", "partial", "no"}:
            return None
        slot_id, slot_label = _resolve_slot(pl)
        format_id = str(pl.get("format_id") or pl.get("scenario_id") or "").strip() or None
        payload = _build_echo_payload(
            event,
            slot_id=slot_id,
            slot_label=slot_label,
            echo=echo,
            format_id=format_id,
            evidence_count=1,
            evidence_event_ids=[event_id] if event_id else [],
        )
        row = _upsert_with_merge(
            db,
            user_id=int(event.user_id),
            payload=payload,
            event_id=event_id,
            event_type=event_type,
            echo=echo,
        )
    else:
        to_format = str(pl.get("to_scenario_id") or pl.get("format_id") or "").strip()
        if not to_format:
            return None
        payload = _build_scenario_switch_payload(
            event,
            to_format=to_format,
            evidence_count=1,
            evidence_event_ids=[event_id] if event_id else [],
        )
        row = _upsert_with_merge(
            db,
            user_id=int(event.user_id),
            payload=payload,
            event_id=event_id,
            event_type=event_type,
            to_format=to_format,
        )

    if commit:
        db.commit()
    return row


def load_user_compatibility_hypotheses_v0(
    db: Session,
    user_id: int,
    *,
    limit: int = 10,
) -> list[dict[str, Any]]:
    rows = (
        db.query(db_models.UserActiveKnowledge)
        .filter(
            db_models.UserActiveKnowledge.user_id == user_id,
            db_models.UserActiveKnowledge.status == INFERRED_STATUS_ACTIVE,
        )
        .order_by(db_models.UserActiveKnowledge.updated_at.desc())
        .limit(max(limit * 3, 20))
        .all()
    )
    out: list[dict[str, Any]] = []
    for row in rows:
        payload = row.payload if isinstance(row.payload, dict) else {}
        if payload.get("source") != COMPATIBILITY_ECHO_KNOWLEDGE_V0_CONTRACT:
            continue
        if payload.get("contract_version") != INFERRED_KNOWLEDGE_V0_CONTRACT:
            continue
        out.append(payload)
        if len(out) >= limit:
            break
    return out
