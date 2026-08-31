"""Shared Global Day artifact — one LLM Global stage per date × locale × semantic_version.

Key MUST NOT include user_id, profile_hash, or expression/prompt.
Force rebuild regenerates the same key (engineering ledger), it does not mint a new identity.

Canon: docs/COMPUTE_LIFECYCLE_AND_ARTIFACT_ECONOMICS_V1.md · TODAY_CONTENT_PIPELINE_V1 I0.
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.db import models as db_models

logger = logging.getLogger(__name__)

GLOBAL_DAY_SEMANTIC_VERSION = "global-day-semantic.v1"
MODULE = "today"
SURFACE = "shared_global_day"

_locks_guard = threading.Lock()
_key_locks: dict[str, threading.Lock] = {}


def normalize_locale(locale: str | None) -> str:
    raw = (locale or "ru").strip().lower()[:32]
    return raw or "ru"


def normalize_local_date(local_date: date | str) -> str:
    if isinstance(local_date, date):
        return local_date.isoformat()
    return str(local_date or "").strip()[:10]


def global_day_key(
    *,
    local_date: date | str,
    locale: str | None,
    semantic_version: str = GLOBAL_DAY_SEMANTIC_VERSION,
) -> str:
    """Identity of the shared Global Day. No user, profile, or expression version."""
    payload = {
        "local_date": normalize_local_date(local_date),
        "locale": normalize_locale(locale),
        "semantic_version": str(semantic_version or GLOBAL_DAY_SEMANTIC_VERSION).strip(),
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:32]


def _lock_for(key: str) -> threading.Lock:
    with _locks_guard:
        lock = _key_locks.get(key)
        if lock is None:
            lock = threading.Lock()
            _key_locks[key] = lock
        return lock


def load_shared_global_day(
    db: Session,
    *,
    local_date: date | str,
    locale: str | None,
    semantic_version: str = GLOBAL_DAY_SEMANTIC_VERSION,
) -> dict[str, Any] | None:
    key = global_day_key(
        local_date=local_date, locale=locale, semantic_version=semantic_version
    )
    loc = normalize_locale(locale)
    rows = (
        db.query(db_models.GenerationLog)
        .filter(
            db_models.GenerationLog.module == MODULE,
            db_models.GenerationLog.surface == SURFACE,
            db_models.GenerationLog.status == "success",
            db_models.GenerationLog.user_id.is_(None),
            db_models.GenerationLog.locale == loc,
        )
        .order_by(db_models.GenerationLog.id.desc())
        .limit(120)
        .all()
    )
    for row in rows:
        inp = row.input_payload if isinstance(row.input_payload, dict) else {}
        if str(inp.get("global_day_key") or "") != key:
            continue
        body = row.normalized_response if isinstance(row.normalized_response, dict) else None
        if not body:
            continue
        if not body.get("conflict") and not body.get("interpretive_chorus"):
            continue
        return dict(body)
    return None


def save_shared_global_day(
    db: Session,
    *,
    local_date: date | str,
    locale: str | None,
    artifact: dict[str, Any],
    force_rebuild: bool = False,
    semantic_version: str = GLOBAL_DAY_SEMANTIC_VERSION,
) -> str:
    """Persist under the same identity. force_rebuild is a regeneration, not a new key."""
    key = global_day_key(
        local_date=local_date, locale=locale, semantic_version=semantic_version
    )
    loc = normalize_locale(locale)
    day = normalize_local_date(local_date)
    from todayflow_backend.services.learning import get_learning_service

    learning = get_learning_service()
    learning.log_generation(
        db,
        module=MODULE,
        surface=SURFACE,
        user_id=None,
        locale=loc,
        input_payload={
            "global_day_key": key,
            "local_date": day,
            "locale": loc,
            "semantic_version": semantic_version,
            "force_rebuild": bool(force_rebuild),
            "ledger": "engineering" if force_rebuild else "product",
        },
        normalized_response=dict(artifact),
        status="success",
    )
    return key
