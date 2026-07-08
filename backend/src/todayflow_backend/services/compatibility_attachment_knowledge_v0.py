"""Attachment style lens → hypothesis atoms (reference CD, user confirm required).

Canon: compatibility_attachment_reference_v0 + USER_KNOWLEDGE_MODEL hypothesis
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.db import models as db_models
from todayflow_backend.services.compatibility_attachment_reference_v0 import (
    COMPATIBILITY_ATTACHMENT_REFERENCE_V0_CONTRACT,
)
from todayflow_backend.services.meaning_derived_knowledge_v0 import (
    INFERRED_KNOWLEDGE_V0_CONTRACT,
    INFERRED_STATUS_ACTIVE,
    upsert_inferred_knowledge_v0,
    validate_inferred_knowledge_v0,
)

logger = logging.getLogger(__name__)

COMPATIBILITY_ATTACHMENT_KNOWLEDGE_V0_CONTRACT = "compatibility_attachment_knowledge_v0"

PROMOTABLE_ATTACHMENT_EVENT_TYPES = frozenset({"compatibility_attachment_confirm"})


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sanitize_code(value: str) -> str:
    return value.strip().lower().replace(" ", "_")[:64]


def _knowledge_id_for_code(code: str) -> str:
    return f"inf-attachment-lens-{_sanitize_code(code)}"


def _build_lens_payload(
    *,
    code: str,
    label: str,
    summary: str,
    evidence_blocks: list[str],
    evidence_count: int = 1,
    interpretation_ref_id: str | None = None,
    evidence_signal_ids: list[str] | None = None,
) -> dict[str, Any]:
    slug = _sanitize_code(code)
    captured = _utc_now_iso()
    chain_entry: dict[str, Any] = {
        "attachment_style_code": code,
        "evidence_blocks": evidence_blocks[:10],
        "source": COMPATIBILITY_ATTACHMENT_REFERENCE_V0_CONTRACT,
    }
    if interpretation_ref_id:
        chain_entry["interpretation_ref_id"] = interpretation_ref_id
        chain_entry["spawn_template"] = "attachment_lens:v0"
    return {
        "contract_version": INFERRED_KNOWLEDGE_V0_CONTRACT,
        "knowledge_id": _knowledge_id_for_code(code),
        "knowledge_type": "hypothesis",
        "data_class": "inferred",
        "claim": f"behavior_hypothesis:attachment_lens_{slug}",
        "value": slug,
        "summary": summary[:240],
        "confidence": round(min(0.72, 0.48 + evidence_count * 0.04), 3),
        "evidence_count": evidence_count,
        "evidence_window_days": 28,
        "evidence_signal_ids": list(evidence_signal_ids or [])[:20],
        "evidence_chain": [chain_entry],
        "confirmation_required": True,
        "confirmation_stage": "hypothesis",
        "status": INFERRED_STATUS_ACTIVE,
        "created_at": captured,
        "last_confirmed_at": captured,
        "captured_at": captured,
        "source": COMPATIBILITY_ATTACHMENT_KNOWLEDGE_V0_CONTRACT,
        "domain": "compatibility",
        "reference_status": "active",
        "decision_relevance": 0.46,
        "display_label": label[:120],
    }


def _block_feedback_from_compat_echo_events(events: list[Any]) -> dict[str, str]:
    from todayflow_backend.services.compatibility_attachment_reference_v0 import DEEP_BLOCK_KEYS

    out: dict[str, str] = {}
    for ev in events:
        pl = ev.payload if isinstance(getattr(ev, "payload", None), dict) else {}
        block = str(pl.get("block_key") or "").strip().lower()
        if not block:
            target = str(pl.get("target") or "")
            if target.startswith("deep:"):
                block = target.split(":", 1)[-1].strip().lower()
        echo = str(pl.get("echo") or "").strip().lower()
        if block in DEEP_BLOCK_KEYS and echo in {"yes", "partial", "no"}:
            out[block] = echo
    return out


def spawn_attachment_lens_from_ilr_v0(
    db: Session,
    *,
    user_id: int,
    matching_events: list[Any],
    interpretation_ref_id: str,
    evidence_count: int,
    commit: bool = False,
) -> list[str]:
    """ILR spawn_hypothesis_ids → attachment lens hypotheses from echo events."""
    from todayflow_backend.services.compatibility_attachment_reference_v0 import score_attachment_styles

    block_feedback = _block_feedback_from_compat_echo_events(matching_events)
    if not block_feedback:
        return []

    hints = score_attachment_styles(block_feedback)
    if not hints:
        return []

    event_ids = [str(ev.event_id) for ev in matching_events if getattr(ev, "event_id", None)]
    created: list[str] = []
    for hint in hints[:3]:
        code = str(hint.get("code") or "").strip()
        if not code:
            continue
        kid = _knowledge_id_for_code(code)
        row = (
            db.query(db_models.UserActiveKnowledge)
            .filter(
                db_models.UserActiveKnowledge.user_id == user_id,
                db_models.UserActiveKnowledge.knowledge_id == kid,
            )
            .first()
        )
        if row is not None:
            payload = row.payload if isinstance(row.payload, dict) else {}
            if payload.get("user_verdict") in {"confirm", "reject", "partial"}:
                continue
            merged_ids = list(dict.fromkeys([*(payload.get("evidence_signal_ids") or []), *event_ids]))[:20]
            updated = dict(payload)
            updated["evidence_signal_ids"] = merged_ids
            updated["evidence_count"] = max(int(payload.get("evidence_count") or 0), evidence_count)
            chain = list(updated.get("evidence_chain") or [])
            chain.append(
                {
                    "interpretation_ref_id": interpretation_ref_id,
                    "spawn_template": "attachment_lens:v0",
                    "attachment_style_code": code,
                    "evidence_blocks": hint.get("evidence_blocks") or [],
                }
            )
            updated["evidence_chain"] = chain[:10]
            row.payload = updated
            created.append(kid)
            continue

        blocks = [str(x) for x in (hint.get("evidence_blocks") or []) if x]
        payload = _build_lens_payload(
            code=code,
            label=str(hint.get("label") or code),
            summary=str(hint.get("summary") or ""),
            evidence_blocks=blocks,
            evidence_count=evidence_count,
            interpretation_ref_id=interpretation_ref_id,
            evidence_signal_ids=event_ids,
        )
        try:
            upsert_inferred_knowledge_v0(db, user_id=user_id, payload=payload, commit=False)
            created.append(kid)
        except ValueError as exc:
            logger.warning(
                "skip ILR attachment lens user=%s ref=%s code=%s: %s",
                user_id,
                interpretation_ref_id,
                code,
                exc,
            )
    if commit:
        db.commit()
    return created


def ensure_attachment_lens_hypotheses_v0(
    db: Session,
    *,
    user_id: int,
    attachment_reference: dict[str, Any] | None,
    commit: bool = False,
) -> list[str]:
    """Upsert hypothesis rows for top attachment hints (idempotent)."""
    if not attachment_reference:
        return []
    hints = attachment_reference.get("attachment_style_hints")
    if not isinstance(hints, list) or not hints:
        return []

    created: list[str] = []
    for hint in hints[:3]:
        if not isinstance(hint, dict):
            continue
        code = str(hint.get("code") or "").strip()
        if not code:
            continue
        kid = _knowledge_id_for_code(code)
        row = (
            db.query(db_models.UserActiveKnowledge)
            .filter(
                db_models.UserActiveKnowledge.user_id == user_id,
                db_models.UserActiveKnowledge.knowledge_id == kid,
            )
            .first()
        )
        if row is not None:
            payload = row.payload if isinstance(row.payload, dict) else {}
            if payload.get("user_verdict") in {"confirm", "reject", "partial"}:
                continue
            created.append(kid)
            continue

        blocks = [str(x) for x in (hint.get("evidence_blocks") or []) if x]
        payload = _build_lens_payload(
            code=code,
            label=str(hint.get("label") or code),
            summary=str(hint.get("summary") or ""),
            evidence_blocks=blocks,
        )
        try:
            upsert_inferred_knowledge_v0(db, user_id=user_id, payload=payload, commit=False)
            created.append(kid)
        except ValueError as exc:
            logger.warning("skip attachment lens user=%s code=%s: %s", user_id, code, exc)
    if commit:
        db.commit()
    return created


def promote_compatibility_attachment_confirm_v0(
    db: Session,
    event: db_models.MeaningEvent,
    *,
    commit: bool = False,
) -> db_models.UserActiveKnowledge | None:
    """Learning event after user confirms/rejects attachment lens chip."""
    event_type = str(event.event_type or "")
    if event_type not in PROMOTABLE_ATTACHMENT_EVENT_TYPES:
        return None

    pl = event.payload if isinstance(event.payload, dict) else {}
    code = str(pl.get("attachment_style_code") or pl.get("code") or "").strip()
    verdict_raw = str(pl.get("verdict") or pl.get("echo") or "").strip().lower()
    correction_map = {
        "yes": "confirm",
        "confirm": "confirm",
        "partial": "partial",
        "no": "reject",
        "reject": "reject",
    }
    correction = correction_map.get(verdict_raw)
    if not code or correction is None:
        return None
    kid = _knowledge_id_for_code(code)
    row = (
        db.query(db_models.UserActiveKnowledge)
        .filter(
            db_models.UserActiveKnowledge.user_id == int(event.user_id),
            db_models.UserActiveKnowledge.knowledge_id == kid,
        )
        .first()
    )
    if row is None:
        label = str(pl.get("label") or code)
        summary = str(pl.get("summary") or label)
        blocks = [str(x) for x in (pl.get("evidence_blocks") or []) if x]
        payload = _build_lens_payload(
            code=code,
            label=label,
            summary=summary,
            evidence_blocks=blocks,
        )
        errors = validate_inferred_knowledge_v0(payload)
        if errors:
            raise ValueError("; ".join(errors))
        row = db_models.UserActiveKnowledge(
            user_id=int(event.user_id),
            knowledge_id=kid,
            status=INFERRED_STATUS_ACTIVE,
            payload=payload,
        )
        db.add(row)
        db.flush()

    payload = row.payload if isinstance(row.payload, dict) else {}
    updated = dict(payload)
    updated["user_verdict"] = correction
    updated["verdict_at"] = _utc_now_iso()
    updated["evidence_signal_ids"] = list(
        dict.fromkeys([*(updated.get("evidence_signal_ids") or []), str(event.event_id)])
    )[:20]
    if correction == "confirm":
        updated["confirmation_stage"] = "confirmed"
        updated["confidence"] = round(min(0.88, float(payload.get("confidence") or 0.5) + 0.12), 3)
    row.payload = updated
    if commit:
        db.commit()
    else:
        db.flush()
    return row
