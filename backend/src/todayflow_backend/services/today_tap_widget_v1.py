"""Wave 2 Phase A — tap_event_v1 persistence + accuracy summary."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Any

from todayflow_backend.db import models as db_models

TAP_RESPONSES = frozenset({"avoided_trap", "fell_into_trap", "not_applicable", "skipped"})
ACCURACY_DOMAINS = ("work", "money", "relationships", "energy")

_SPHERE_TO_DOMAIN: dict[str, str] = {
    "work": "work",
    "work_decisions": "work",
    "career": "work",
    "money": "money",
    "finances": "money",
    "money_work": "money",
    "relationships": "relationships",
    "love": "relationships",
    "family": "relationships",
    "energy": "energy",
    "health": "energy",
    "body": "energy",
}


def day_facts_id_for(user_id: int, local_date: date) -> str:
    return f"{user_id}:{local_date.isoformat()}"


def map_sphere_to_domain(sphere: str | None) -> str:
    key = (sphere or "").strip().lower()
    if key in ACCURACY_DOMAINS:
        return key
    return _SPHERE_TO_DOMAIN.get(key, "work")


def upsert_tap_event(
    db,
    *,
    user_id: int,
    local_date: date,
    scene_id: str,
    prompted_text: str,
    response: str,
    domain: str = "work",
    free_text: str | None = None,
    day_facts_id: str | None = None,
) -> dict[str, Any]:
    if response not in TAP_RESPONSES:
        raise ValueError(f"invalid_response:{response}")
    scene_key = (scene_id or "").strip()
    prompt = (prompted_text or "").strip()
    if not scene_key or not prompt:
        raise ValueError("scene_id_and_prompted_text_required")

    domain_key = domain if domain in ACCURACY_DOMAINS else map_sphere_to_domain(domain)
    facts_id = (day_facts_id or "").strip() or day_facts_id_for(user_id, local_date)
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    row = (
        db.query(db_models.TodayTapEvent)
        .filter(
            db_models.TodayTapEvent.user_id == user_id,
            db_models.TodayTapEvent.local_date == local_date,
            db_models.TodayTapEvent.scene_id == scene_key,
        )
        .first()
    )
    if row is None:
        row = db_models.TodayTapEvent(
            event_id=uuid.uuid4().hex,
            user_id=user_id,
            day_facts_id=facts_id,
            local_date=local_date,
            scene_id=scene_key,
            domain=domain_key,
            prompted_text=prompt[:2000],
            response=response,
            free_text=(free_text.strip()[:2000] if isinstance(free_text, str) and free_text.strip() else None),
            responded_at=now,
        )
        db.add(row)
    else:
        row.day_facts_id = facts_id
        row.domain = domain_key
        row.prompted_text = prompt[:2000]
        row.response = response
        row.free_text = free_text.strip()[:2000] if isinstance(free_text, str) and free_text.strip() else None
        row.responded_at = now

    db.commit()
    db.refresh(row)
    return tap_event_public(row)


def tap_event_public(row: db_models.TodayTapEvent) -> dict[str, Any]:
    return {
        "schema_version": "tap_event_v1",
        "event_id": row.event_id,
        "user_id": str(row.user_id),
        "day_facts_id": row.day_facts_id,
        "local_date": row.local_date.isoformat(),
        "scene_id": row.scene_id,
        "domain": row.domain,
        "prompted_text": row.prompted_text,
        "response": row.response,
        "free_text": row.free_text,
        "responded_at": row.responded_at.isoformat() + "Z" if row.responded_at else None,
    }


def empty_domain_bucket() -> dict[str, int]:
    return {"correct": 0, "total": 0}


def build_accuracy_summary(db, *, user_id: int, window_days: int = 14) -> dict[str, Any]:
    window = max(1, min(int(window_days), 90))
    end = date.today()
    start = end - timedelta(days=window - 1)
    rows = (
        db.query(db_models.TodayTapEvent)
        .filter(
            db_models.TodayTapEvent.user_id == user_id,
            db_models.TodayTapEvent.local_date >= start,
            db_models.TodayTapEvent.local_date <= end,
        )
        .all()
    )

    overall = empty_domain_bucket()
    by_domain = {d: empty_domain_bucket() for d in ACCURACY_DOMAINS}

    for row in rows:
        # not_applicable / skipped excluded from denominator (contract §5)
        if row.response in ("not_applicable", "skipped"):
            continue
        if row.response not in ("avoided_trap", "fell_into_trap"):
            continue
        domain = row.domain if row.domain in by_domain else "work"
        by_domain[domain]["total"] += 1
        overall["total"] += 1
        if row.response == "avoided_trap":
            by_domain[domain]["correct"] += 1
            overall["correct"] += 1

    return {
        "schema_version": "accuracy_summary_v1",
        "window": f"{window}d",
        "from_date": start.isoformat(),
        "to_date": end.isoformat(),
        "overall": overall,
        "by_domain": by_domain,
    }
