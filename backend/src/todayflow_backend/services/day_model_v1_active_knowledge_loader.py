"""A1.8 — Load user Active Knowledge from DB for Branch A hot path."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.db import models as db_models
from todayflow_backend.services.day_model_v1_active_knowledge import (
    ACTIVE_KNOWLEDGE_STATUS,
    DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
    validate_day_active_knowledge_v1,
)

logger = logging.getLogger(__name__)

ACTIVE_KNOWLEDGE_ROW_STATUS_ACTIVE = "active"


def load_user_active_knowledge_list_v1(
    db: Session,
    user_id: int,
    *,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """
    Return validated `day_active_knowledge_v1` payloads for user.

    Empty list when no rows. Invalid rows are skipped with warning.
    """
    rows = (
        db.query(db_models.UserActiveKnowledge)
        .filter(
            db_models.UserActiveKnowledge.user_id == user_id,
            db_models.UserActiveKnowledge.status == ACTIVE_KNOWLEDGE_ROW_STATUS_ACTIVE,
        )
        .order_by(db_models.UserActiveKnowledge.updated_at.desc())
        .limit(max(1, min(limit, 500)))
        .all()
    )

    result: list[dict[str, Any]] = []
    for row in rows:
        payload = row.payload
        if not isinstance(payload, dict):
            logger.warning(
                "skip active knowledge row %s: payload not dict", row.knowledge_id
            )
            continue
        if payload.get("contract_version") != DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT:
            logger.warning(
                "skip active knowledge row %s: invalid contract_version",
                row.knowledge_id,
            )
            continue
        if payload.get("status") != ACTIVE_KNOWLEDGE_STATUS:
            continue
        errors = validate_day_active_knowledge_v1(payload)
        if errors:
            logger.warning(
                "skip active knowledge row %s: %s",
                row.knowledge_id,
                "; ".join(errors),
            )
            continue
        if payload.get("knowledge_id") != row.knowledge_id:
            payload = dict(payload)
            payload["knowledge_id"] = row.knowledge_id
        result.append(payload)

    return result


def upsert_user_active_knowledge_v1(
    db: Session,
    *,
    user_id: int,
    active_knowledge: dict[str, Any],
) -> db_models.UserActiveKnowledge:
    """Persist or update one active knowledge record (admin / promotion path)."""
    errors = validate_day_active_knowledge_v1(active_knowledge)
    if errors:
        raise ValueError("; ".join(errors))

    knowledge_id = str(active_knowledge["knowledge_id"])
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
            status=ACTIVE_KNOWLEDGE_ROW_STATUS_ACTIVE,
            payload=active_knowledge,
        )
        db.add(row)
    else:
        row.status = ACTIVE_KNOWLEDGE_ROW_STATUS_ACTIVE
        row.payload = active_knowledge

    db.commit()
    db.refresh(row)
    return row
