"""Interpretation Engine v0 — signal/event → multi-meaning instances → hypotheses.

Deterministic ILR path (no LLM). Canon: INTERPRETATION_LAYER_AND_REFERENCE.md §6–§7.
"""

from __future__ import annotations

import logging
import re
from datetime import UTC, date, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.db.models import MeaningEvent
from todayflow_backend.services.interpretation_reference_v0 import (
    InterpretationRuleV0,
    event_matches_rule,
    get_interpretation_rules_v0,
)
from todayflow_backend.services.compatibility_attachment_knowledge_v0 import (
    spawn_attachment_lens_from_ilr_v0,
)
from todayflow_backend.services.meaning_derived_knowledge_v0 import (
    INFERRED_KNOWLEDGE_V0_CONTRACT,
    upsert_inferred_knowledge_v0,
)

logger = logging.getLogger(__name__)

INTERPRETATION_INSTANCE_V0_CONTRACT = "interpretation_instance_v0"
INSTANCE_STATUS_OPEN = "open"

ALLOWED_INTERPRETATION_CLAIM_PREFIXES = frozenset({"interpretation_hypothesis"})

SPAWN_ATTACHMENT_LENS_V0 = "attachment_lens:v0"


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sanitize(value: str) -> str:
    cleaned = value.strip().lower().replace(" ", "_")
    return re.sub(r"[^a-z0-9_.-]", "", cleaned)[:64]


def _normalize_weights(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    total = sum(float(c.get("prior_weight") or 0) for c in candidates) or 1.0
    out: list[dict[str, Any]] = []
    for item in candidates:
        weight = round(float(item.get("prior_weight") or 0) / total, 4)
        out.append(
            {
                "code": item["code"],
                "label": item["label"],
                "weight": weight,
                "confidence": round(min(0.85, 0.45 + weight * 0.5), 3),
            }
        )
    remainder = 1.0 - sum(x["weight"] for x in out)
    if out and abs(remainder) > 0.0001:
        out[0]["weight"] = round(out[0]["weight"] + remainder, 4)
    return out


def _build_instance_payload(
    rule: InterpretationRuleV0,
    *,
    evidence_event_ids: list[str],
    evidence_count: int,
    window_days: int,
) -> dict[str, Any]:
    meanings = _normalize_weights(list(rule["candidate_meanings"]))
    dominant = max(meanings, key=lambda m: m["weight"])
    ref_slug = _sanitize(rule["interpretation_ref_id"].replace(".", "_"))
    captured = _utc_now_iso()
    return {
        "contract_version": INTERPRETATION_INSTANCE_V0_CONTRACT,
        "instance_id": f"ii-{ref_slug}",
        "interpretation_ref_id": rule["interpretation_ref_id"],
        "level": rule["level"],
        "taxonomy": rule["taxonomy"],
        "meanings": meanings,
        "dominant_meaning": dominant["code"],
        "dominant_label": dominant["label"],
        "summary": rule["summary_dominant"],
        "evidence_count": evidence_count,
        "evidence_window_days": window_days,
        "evidence_event_ids": evidence_event_ids[:50],
        "status": INSTANCE_STATUS_OPEN,
        "confirmation_required": rule["level"] in {"L3", "L4"},
        "created_at": captured,
        "captured_at": captured,
    }


def _build_hypothesis_from_instance(instance: dict[str, Any]) -> dict[str, Any]:
    ref_id = str(instance["interpretation_ref_id"])
    ref_slug = _sanitize(ref_id.replace(".", "_"))
    dominant = str(instance.get("dominant_meaning") or "unknown")
    count = int(instance.get("evidence_count") or 0)
    captured = _utc_now_iso()
    return {
        "contract_version": INFERRED_KNOWLEDGE_V0_CONTRACT,
        "knowledge_id": f"inf-ilr-{ref_slug}",
        "knowledge_type": "hypothesis",
        "data_class": "interpretation",
        "claim": f"interpretation_hypothesis:{ref_slug}_{dominant}",
        "value": dominant,
        "summary": str(instance.get("summary") or instance.get("dominant_label") or ref_id)[:240],
        "confidence": round(min(0.88, 0.55 + count * 0.04), 3),
        "evidence_count": count,
        "evidence_window_days": int(instance.get("evidence_window_days") or 28),
        "evidence_signal_ids": list(instance.get("evidence_event_ids") or [])[:20],
        "evidence_chain": [
            {
                "interpretation_ref_id": ref_id,
                "instance_id": instance.get("instance_id"),
                "dominant_meaning": dominant,
                "meanings": instance.get("meanings"),
            }
        ],
        "confirmation_required": True,
        "confirmation_stage": "hypothesis",
        "status": "active",
        "created_at": captured,
        "last_confirmed_at": captured,
        "captured_at": captured,
        "source": "interpretation_engine_v0",
    }


def validate_interpretation_instance_v0(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("contract_version") != INTERPRETATION_INSTANCE_V0_CONTRACT:
        errors.append("invalid contract_version")
    meanings = payload.get("meanings")
    if not isinstance(meanings, list) or not meanings:
        errors.append("meanings required")
    elif abs(sum(float(m.get("weight") or 0) for m in meanings if isinstance(m, dict)) - 1.0) > 0.02:
        errors.append("meanings weights must sum to ~1.0")
    if not payload.get("interpretation_ref_id"):
        errors.append("interpretation_ref_id required")
    return errors


def upsert_interpretation_instance_v0(
    db: Session,
    *,
    user_id: int,
    payload: dict[str, Any],
    commit: bool = False,
) -> None:
    errors = validate_interpretation_instance_v0(payload)
    if errors:
        raise ValueError("; ".join(errors))

    from todayflow_backend.db import models as db_models

    instance_id = str(payload["instance_id"])
    row = (
        db.query(db_models.UserActiveKnowledge)
        .filter(
            db_models.UserActiveKnowledge.user_id == user_id,
            db_models.UserActiveKnowledge.knowledge_id == instance_id,
        )
        .first()
    )
    if row is None:
        row = db_models.UserActiveKnowledge(
            user_id=user_id,
            knowledge_id=instance_id,
            status=INSTANCE_STATUS_OPEN,
            payload=payload,
        )
        db.add(row)
    else:
        existing = row.payload if isinstance(row.payload, dict) else {}
        if existing.get("status") in {"confirmed", "rejected", "superseded"}:
            return
        row.payload = payload
        row.status = INSTANCE_STATUS_OPEN

    if commit:
        db.commit()
    else:
        db.flush()


def load_user_interpretation_instances_v0(
    db: Session,
    user_id: int,
    *,
    limit: int = 10,
) -> list[dict[str, Any]]:
    from todayflow_backend.db import models as db_models

    rows = (
        db.query(db_models.UserActiveKnowledge)
        .filter(
            db_models.UserActiveKnowledge.user_id == user_id,
            db_models.UserActiveKnowledge.status == INSTANCE_STATUS_OPEN,
        )
        .order_by(db_models.UserActiveKnowledge.updated_at.desc())
        .limit(max(1, min(limit, 50)))
        .all()
    )
    result: list[dict[str, Any]] = []
    for row in rows:
        payload = row.payload
        if not isinstance(payload, dict):
            continue
        if payload.get("contract_version") != INTERPRETATION_INSTANCE_V0_CONTRACT:
            continue
        if payload.get("status") != INSTANCE_STATUS_OPEN:
            continue
        if payload.get("user_verdict") in {"confirm", "reject", "partial"}:
            continue
        errors = validate_interpretation_instance_v0(payload)
        if errors:
            continue
        result.append(payload)
    return result


def mark_inferred_knowledge_verdict_v0(
    db: Session,
    *,
    user_id: int,
    knowledge_id: str,
    verdict: str,
    commit: bool = False,
) -> bool:
    """Apply user verdict to source inferred/ILR hypothesis row."""
    from todayflow_backend.db import models as db_models

    row = (
        db.query(db_models.UserActiveKnowledge)
        .filter(
            db_models.UserActiveKnowledge.user_id == user_id,
            db_models.UserActiveKnowledge.knowledge_id == knowledge_id,
        )
        .first()
    )
    if row is None:
        return False
    payload = row.payload if isinstance(row.payload, dict) else {}
    if payload.get("contract_version") != INFERRED_KNOWLEDGE_V0_CONTRACT:
        return False
    if payload.get("user_verdict") in {"confirm", "reject", "partial"}:
        return False
    updated = dict(payload)
    updated["user_verdict"] = verdict
    updated["verdict_at"] = _utc_now_iso()
    row.payload = updated
    if commit:
        db.commit()
    else:
        db.flush()
    return True


def mark_interpretation_instance_verdict_v0(
    db: Session,
    *,
    user_id: int,
    instance_id: str,
    verdict: str,
    commit: bool = False,
) -> bool:
    """Apply user verdict to an open ILR interpretation instance."""
    from todayflow_backend.db import models as db_models

    row = (
        db.query(db_models.UserActiveKnowledge)
        .filter(
            db_models.UserActiveKnowledge.user_id == user_id,
            db_models.UserActiveKnowledge.knowledge_id == instance_id,
        )
        .first()
    )
    if row is None:
        return False
    payload = row.payload if isinstance(row.payload, dict) else {}
    if payload.get("contract_version") != INTERPRETATION_INSTANCE_V0_CONTRACT:
        return False
    if payload.get("user_verdict") in {"confirm", "reject", "partial"}:
        return False
    updated = dict(payload)
    updated["user_verdict"] = verdict
    updated["verdict_at"] = _utc_now_iso()
    if verdict == "confirm":
        updated["status"] = "confirmed"
        row.status = "confirmed"
    elif verdict == "reject":
        updated["status"] = "rejected"
        row.status = "rejected"
    row.payload = updated
    if commit:
        db.commit()
    else:
        db.flush()
    return True


def _spawn_hypotheses_for_rule_v0(
    db: Session,
    *,
    user_id: int,
    rule: InterpretationRuleV0,
    matching: list[MeaningEvent],
) -> int:
    spawn_ids = rule.get("spawn_hypothesis_ids") or ()
    if not spawn_ids or not matching:
        return 0

    spawned = 0
    for spawn_id in spawn_ids:
        if spawn_id != SPAWN_ATTACHMENT_LENS_V0:
            logger.warning("unknown spawn_hypothesis_id=%s ref=%s", spawn_id, rule["interpretation_ref_id"])
            continue
        try:
            created = spawn_attachment_lens_from_ilr_v0(
                db,
                user_id=user_id,
                matching_events=matching,
                interpretation_ref_id=str(rule["interpretation_ref_id"]),
                evidence_count=len(matching),
                commit=False,
            )
            spawned += len(created)
        except ValueError as exc:
            logger.warning(
                "spawn attachment lens failed user=%s ref=%s: %s",
                user_id,
                rule["interpretation_ref_id"],
                exc,
            )
    return spawned


def sync_interpretation_engine_v0(
    db: Session,
    *,
    user_id: int,
    reference_date: date | None = None,
    window_days: int = 28,
    commit: bool = True,
) -> dict[str, int]:
    """Match meaning events to ILR rules; upsert instances + hypotheses."""
    ref = reference_date or date.today()
    start = ref - timedelta(days=max(1, window_days) - 1)
    rows = (
        db.query(MeaningEvent)
        .filter(
            MeaningEvent.user_id == user_id,
            MeaningEvent.local_date >= start,
            MeaningEvent.local_date <= ref,
        )
        .order_by(MeaningEvent.event_time.asc(), MeaningEvent.id.asc())
        .all()
    )

    instances = 0
    hypotheses = 0
    spawned = 0

    for rule in get_interpretation_rules_v0():
        matching: list[MeaningEvent] = []
        for row in rows:
            pl = row.payload if isinstance(row.payload, dict) else {}
            if event_matches_rule(str(row.event_type or ""), pl, rule):
                matching.append(row)

        if len(matching) < int(rule["min_signal_count"]):
            continue

        event_ids = [str(ev.event_id) for ev in matching]
        instance_payload = _build_instance_payload(
            rule,
            evidence_event_ids=event_ids,
            evidence_count=len(matching),
            window_days=window_days,
        )
        try:
            upsert_interpretation_instance_v0(db, user_id=user_id, payload=instance_payload, commit=False)
            instances += 1
        except ValueError as exc:
            logger.warning("skip interpretation instance user=%s: %s", user_id, exc)
            continue

        spawned += _spawn_hypotheses_for_rule_v0(
            db,
            user_id=user_id,
            rule=rule,
            matching=matching,
        )

        if len(matching) >= 3:
            try:
                upsert_inferred_knowledge_v0(
                    db,
                    user_id=user_id,
                    payload=_build_hypothesis_from_instance(instance_payload),
                    commit=False,
                )
                hypotheses += 1
            except ValueError as exc:
                logger.warning("skip ILR hypothesis user=%s: %s", user_id, exc)

    if commit:
        db.commit()

    return {"instances": instances, "hypotheses": hypotheses, "spawned": spawned}
