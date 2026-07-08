"""Meaning Rings events and snapshots API."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from todayflow_backend.api.auth import require_user
from todayflow_backend.db.models import MeaningEvent, User
from todayflow_backend.db.session import get_session
from todayflow_backend.services.meaning_progress import (
    build_meaning_progress_snapshot,
)

router = APIRouter(prefix="/meaning", tags=["meaning"])

RingName = Literal["Mind", "Body", "Love", "Wealth", "Purpose", "Energy"]

VALID_EVENT_TYPES = {
    "habit_completed",
    "ascetic_step_done",
    "practice_completed",
    "diary_entry",
    "reflection_answer",
    "guidance_ask",
    "tarot_spread_done",
    "compatibility_view",
    "cycle_log",
    "affirmation_done",
    "self_awareness_question",
    "consistency_bonus",
}

VALID_EVENT_SOURCES = {"today", "flow", "insight", "compatibility", "profile"}


class MeaningEventInput(BaseModel):
    event_id: str | None = Field(default=None, max_length=64)
    event_type: str = Field(..., max_length=64)
    event_source: str = Field(..., max_length=32)
    event_time: datetime | None = None
    local_date: date | None = None
    quality_score: float = Field(default=1.0, ge=0.0, le=1.0)
    payload: dict[str, Any] | None = None
    idempotency_key: str = Field(..., max_length=128)


class MeaningEventsRequest(BaseModel):
    events: list[MeaningEventInput] = Field(default_factory=list, min_length=1, max_length=50)


class MeaningEventsResponse(BaseModel):
    accepted: int
    deduplicated: int
    total: int


class MeaningRingItem(BaseModel):
    ring: RingName
    score: int
    trend_7d: int
    confidence: Literal["low", "medium", "high"]
    top_contributors: list[str]


class MeaningRingsResponse(BaseModel):
    window_days: int
    generated_at: str
    rings: list[MeaningRingItem]


@router.post("/events", response_model=MeaningEventsResponse)
def post_meaning_events(
    body: MeaningEventsRequest,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
) -> MeaningEventsResponse:
    accepted = 0
    deduplicated = 0

    for item in body.events:
        if item.event_type not in VALID_EVENT_TYPES:
            raise HTTPException(status_code=400, detail=f"Unsupported event_type: {item.event_type}")
        if item.event_source not in VALID_EVENT_SOURCES:
            raise HTTPException(status_code=400, detail=f"Unsupported event_source: {item.event_source}")

        existing = (
            db.query(MeaningEvent.id)
            .filter(
                MeaningEvent.user_id == current_user.id,
                MeaningEvent.idempotency_key == item.idempotency_key,
            )
            .first()
        )
        if existing is not None:
            deduplicated += 1
            continue

        event_time = item.event_time or datetime.utcnow()
        event = MeaningEvent(
            event_id=item.event_id or str(uuid4()),
            user_id=current_user.id,
            event_type=item.event_type,
            event_source=item.event_source,
            event_time=event_time,
            local_date=item.local_date or event_time.date(),
            quality_score=item.quality_score,
            payload=item.payload or {},
            idempotency_key=item.idempotency_key,
        )
        db.add(event)
        accepted += 1

    db.commit()
    return MeaningEventsResponse(accepted=accepted, deduplicated=deduplicated, total=len(body.events))


@router.get("/rings", response_model=MeaningRingsResponse)
def get_meaning_rings(
    window_days: int = Query(28, ge=7, le=60),
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
) -> MeaningRingsResponse:
    snapshot = build_meaning_progress_snapshot(
        db=db,
        user_id=current_user.id,
        target_date=date.today(),
        window_days=window_days,
    )
    rings = [
        MeaningRingItem(
            ring=item.ring,
            score=item.score,
            trend_7d=item.trend_7d,
            confidence=item.confidence,
            top_contributors=item.top_contributors,
        )
        for item in snapshot.rings
    ]

    return MeaningRingsResponse(
        window_days=window_days,
        generated_at=datetime.utcnow().isoformat(),
        rings=rings,
    )
