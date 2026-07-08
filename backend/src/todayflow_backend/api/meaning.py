"""Meaning Rings events and snapshots API."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from todayflow_backend.api.auth import require_user
from todayflow_backend.api.learning_contracts import (
    CompatibilityAttachmentConfirmPayload,
    InterpretationInstanceConfirmPayload,
    ProfileAtomCorrectionPayload,
)
from todayflow_backend.db.models import MeaningEvent, User, utc_naive_now
from todayflow_backend.db.session import get_session
from todayflow_backend.services.meaning_progress import (
    build_meaning_progress_snapshot,
)
from todayflow_backend.services.explicit_l1_knowledge_v0 import (
    promote_meaning_event_explicit_l1_v0,
)
from todayflow_backend.services.compatibility_attachment_knowledge_v0 import (
    promote_compatibility_attachment_confirm_v0,
)
from todayflow_backend.services.compatibility_echo_knowledge_v0 import (
    promote_compatibility_echo_knowledge_v0,
)
from todayflow_backend.services.interpretation_engine_v0 import (
    mark_inferred_knowledge_verdict_v0,
    mark_interpretation_instance_verdict_v0,
    sync_interpretation_engine_v0,
)
from todayflow_backend.services.meaning_derived_knowledge_v0 import (
    sync_meaning_derived_knowledge_v0,
)

router = APIRouter(prefix="/meaning", tags=["meaning"])

RingName = Literal["Mind", "Body", "Love", "Wealth", "Purpose", "Energy"]

# Legacy + product-specific + Today canon (TODAY_PERSONALIZATION_CORE.md §Шаг 2).
VALID_EVENT_TYPES = frozenset(
    {
        "habit_completed",
        "ascetic_step_done",
        "practice_completed",
        "diary_entry",
        "reflection_answer",
        "guidance_ask",
        "guidance_clarify",
        "tarot_spread_done",
        "tarot_session_started",
        "tarot_question_domain_selected",
        "tarot_question_refined",
        "tarot_spread_selected",
        "tarot_question_submitted",
        "tarot_reading_resonance",
        "tarot_reading_follow_up",
        "tarot_deepen_started",
        "compatibility_view",
        "compatibility_encyclopedia_view",
        "compatibility_topic_select",
        "compatibility_echo",
        "compatibility_scenario_switch",
        "compatibility_deep_open",
        "compatibility_attachment_confirm",
        "cycle_log",
        "affirmation_done",
        "self_awareness_question",
        "consistency_bonus",
        # Today ritual / surfaces (snake_case, stable web ↔ iOS)
        "day_opened",
        "day_sky_fact_viewed",
        "tarot_selected",
        "tarot_revealed",
        "number_selected",
        "first_synthesis_viewed",
        "mood_selected",
        "head_topic_selected",
        "sphere_opened",
        "sphere_feedback",
        "action_option_selected",
        "focus_started",
        "focus_completed",
        "support_selected",
        "goal_created",
        "habit_created",
        "evening_reflection_submitted",
        "today_narrative_depth_changed",
        "today_guide_why_opened",
        "today_day_history_first_visible",
        # iOS TodayExperienceLayout / demos (accepted so clients don’t 400)
        "today_ring_open",
        "today_micro_reflection",
        "today_habit_toggle",
        "core_loop_viability_surface_visible",
        "onboarding_intent_selected",
        "onboarding_reality_selected",
        "onboarding_recognition_shown",
        "day_focus_outcome",
        "tarot_spread_viewed",
        "profile_atom_correction",
        "interpretation_instance_confirm",
    }
)

VALID_EVENT_SOURCES = {"today", "flow", "insight", "compatibility", "profile", "onboarding", "tarot"}


def _naive_utc(dt: datetime) -> datetime:
    """Store timestamps in naive UTC columns (see MeaningEvent.event_time)."""
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


class MeaningEventInput(BaseModel):
    event_id: str | None = Field(default=None, max_length=64)
    event_type: str = Field(
        ...,
        max_length=64,
        description=(
            "Canonical event name. Compatibility learning: compatibility_echo, "
            "compatibility_attachment_confirm, interpretation_instance_confirm, profile_atom_correction."
        ),
    )
    event_source: str = Field(
        ...,
        max_length=32,
        description="today | flow | compatibility | profile | tarot | onboarding | insight",
    )
    event_time: datetime | None = None
    local_date: date | None = None
    quality_score: float = Field(default=1.0, ge=0.0, le=1.0)
    payload: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Event-specific JSON. Typed payloads (OpenAPI components): "
            "CompatibilityAttachmentConfirmPayload, InterpretationInstanceConfirmPayload, "
            "ProfileAtomCorrectionPayload."
        ),
        json_schema_extra={
            "examples": [
                {
                    "surface": "analyze_dynamics",
                    "attachment_style_code": "anxious",
                    "label": "Тревожный",
                    "summary": "Может быть важно заранее прояснять ожидания.",
                    "echo": "yes",
                    "verdict": "confirm",
                    "knowledge_id": "inf-attachment-lens-anxious",
                },
                {
                    "surface": "profile_quick_map",
                    "instance_id": "ilr-inst-abc123",
                    "interpretation_ref_id": "beh.compat_echo_yes.v1",
                    "correction": "confirm",
                    "verdict": "confirm",
                    "summary": "В совместимости часто отмечаешь «точно».",
                },
            ]
        },
    )
    idempotency_key: str = Field(..., max_length=128)


class MeaningEventsRequest(BaseModel):
    events: list[MeaningEventInput] = Field(default_factory=list, min_length=1, max_length=50)


class MeaningEventsResponse(BaseModel):
    accepted: int
    deduplicated: int
    total: int


class MeaningLearningPayloadSchemaRefs(BaseModel):
    """Reference shapes for compatibility / ILR learning events (OpenAPI components)."""

    compatibility_attachment_confirm: CompatibilityAttachmentConfirmPayload | None = Field(
        None,
        description="Use when event_type=compatibility_attachment_confirm",
    )
    interpretation_instance_confirm: InterpretationInstanceConfirmPayload | None = Field(
        None,
        description="Use when event_type=interpretation_instance_confirm",
    )
    profile_atom_correction: ProfileAtomCorrectionPayload | None = Field(
        None,
        description="Use when event_type=profile_atom_correction",
    )


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


def _persist_meaning_events(
    db: Session,
    user_id: int,
    events: list[MeaningEventInput],
) -> tuple[int, int]:
    """Insert events with in-batch + DB dedup. Returns (accepted, deduplicated)."""
    accepted = 0
    deduplicated = 0
    seen_in_batch: set[str] = set()
    newly_persisted: list[MeaningEvent] = []

    def _append_event(item: MeaningEventInput) -> None:
        nonlocal accepted
        event_time = _naive_utc(item.event_time) if item.event_time else utc_naive_now()
        event = MeaningEvent(
            event_id=item.event_id or str(uuid4()),
            user_id=user_id,
            event_type=item.event_type,
            event_source=item.event_source,
            event_time=event_time,
            local_date=item.local_date or event_time.date(),
            quality_score=item.quality_score,
            payload=item.payload or {},
            idempotency_key=item.idempotency_key.strip(),
        )
        db.add(event)
        newly_persisted.append(event)
        accepted += 1

    for item in events:
        if item.event_type not in VALID_EVENT_TYPES:
            raise HTTPException(status_code=400, detail=f"Unsupported event_type: {item.event_type}")
        if item.event_source not in VALID_EVENT_SOURCES:
            raise HTTPException(status_code=400, detail=f"Unsupported event_source: {item.event_source}")

        idempotency_key = item.idempotency_key.strip()
        if idempotency_key in seen_in_batch:
            deduplicated += 1
            continue

        existing = (
            db.query(MeaningEvent.id)
            .filter(
                MeaningEvent.user_id == user_id,
                MeaningEvent.idempotency_key == idempotency_key,
            )
            .first()
        )
        if existing is not None:
            deduplicated += 1
            seen_in_batch.add(idempotency_key)
            continue

        seen_in_batch.add(idempotency_key)
        _append_event(item)

    if not newly_persisted:
        return accepted, deduplicated

    try:
        db.commit()
        for event in newly_persisted:
            db.refresh(event)
            try:
                promote_meaning_event_explicit_l1_v0(db, event, commit=False)
            except ValueError:
                pass
            try:
                promote_compatibility_echo_knowledge_v0(db, event, commit=False)
            except ValueError:
                pass
            try:
                promote_compatibility_attachment_confirm_v0(db, event, commit=False)
            except ValueError:
                pass
            if str(event.event_type) == "profile_atom_correction":
                pl = event.payload if isinstance(event.payload, dict) else {}
                kid = str(pl.get("knowledge_id") or "").strip()
                verdict = str(pl.get("correction") or pl.get("verdict") or "").strip()
                if kid and verdict:
                    mark_inferred_knowledge_verdict_v0(
                        db,
                        user_id=user_id,
                        knowledge_id=kid,
                        verdict=verdict,
                        commit=False,
                    )
            if str(event.event_type) == "interpretation_instance_confirm":
                pl = event.payload if isinstance(event.payload, dict) else {}
                iid = str(pl.get("instance_id") or "").strip()
                verdict = str(pl.get("correction") or pl.get("verdict") or "").strip()
                if iid and verdict:
                    mark_interpretation_instance_verdict_v0(
                        db,
                        user_id=user_id,
                        instance_id=iid,
                        verdict=verdict,
                        commit=False,
                    )
        try:
            sync_meaning_derived_knowledge_v0(db, user_id=user_id, commit=False)
            sync_interpretation_engine_v0(db, user_id=user_id, commit=False)
        except Exception:
            pass
        db.commit()
    except IntegrityError:
        db.rollback()
        accepted = 0
        deduplicated = 0
        seen_in_batch = set()
        retry_persisted: list[MeaningEvent] = []
        for item in events:
            idempotency_key = item.idempotency_key.strip()
            if idempotency_key in seen_in_batch:
                deduplicated += 1
                continue
            seen_in_batch.add(idempotency_key)

            existing = (
                db.query(MeaningEvent.id)
                .filter(
                    MeaningEvent.user_id == user_id,
                    MeaningEvent.idempotency_key == idempotency_key,
                )
                .first()
            )
            if existing is not None:
                deduplicated += 1
                continue

            event_time = _naive_utc(item.event_time) if item.event_time else utc_naive_now()
            event = MeaningEvent(
                event_id=item.event_id or str(uuid4()),
                user_id=user_id,
                event_type=item.event_type,
                event_source=item.event_source,
                event_time=event_time,
                local_date=item.local_date or event_time.date(),
                quality_score=item.quality_score,
                payload=item.payload or {},
                idempotency_key=idempotency_key,
            )
            db.add(event)
            try:
                db.commit()
                db.refresh(event)
                accepted += 1
                retry_persisted.append(event)
                try:
                    promote_meaning_event_explicit_l1_v0(db, event, commit=False)
                    promote_compatibility_echo_knowledge_v0(db, event, commit=False)
                    promote_compatibility_attachment_confirm_v0(db, event, commit=False)
                    db.commit()
                except ValueError:
                    db.rollback()
            except IntegrityError:
                db.rollback()
                deduplicated += 1

    return accepted, deduplicated


@router.get("/events/learning-payloads", response_model=MeaningLearningPayloadSchemaRefs)
def get_meaning_learning_payload_schemas() -> MeaningLearningPayloadSchemaRefs:
    """Schema reference for PIM learning event payloads (attachment lens, ILR confirm)."""
    return MeaningLearningPayloadSchemaRefs(
        compatibility_attachment_confirm=CompatibilityAttachmentConfirmPayload(
            surface="analyze_dynamics",
            attachment_style_code="anxious",
            label="Тревожный",
            summary="Может быть важно заранее прояснять ожидания.",
            echo="yes",
            verdict="confirm",
            knowledge_id="inf-attachment-lens-anxious",
        ),
        interpretation_instance_confirm=InterpretationInstanceConfirmPayload(
            surface="profile_quick_map",
            instance_id="ilr-inst-example",
            interpretation_ref_id="beh.compat_echo_yes.v1",
            correction="confirm",
            verdict="confirm",
            summary="В совместимости часто отмечаешь «точно».",
        ),
        profile_atom_correction=ProfileAtomCorrectionPayload(
            knowledge_id="inf-attachment-lens-anxious",
            correction="confirm",
            claim_summary="Может быть важно заранее прояснять ожидания.",
            surface="analyze_dynamics",
            attachment_style_code="anxious",
        ),
    )


@router.post("/events", response_model=MeaningEventsResponse)
def post_meaning_events(
    body: MeaningEventsRequest,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
) -> MeaningEventsResponse:
    """Ingest meaning events (learning signals). See GET /meaning/events/learning-payloads for typed payloads."""
    accepted, deduplicated = _persist_meaning_events(db, current_user.id, body.events)
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
        generated_at=utc_naive_now().isoformat(),
        rings=rings,
    )
