"""Endpoints for generation feedback and prompt registry introspection."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from todayflow_backend.api.auth import require_admin, require_user
from todayflow_backend.db import models as db_models
from todayflow_backend.db.session import get_session
from todayflow_backend.services.learning import LearningService, get_learning_service

router = APIRouter(prefix="/learning", tags=["learning"])


class GenerationFeedbackPayload(BaseModel):
    generation_log_id: int
    signal: str = Field(..., min_length=2, max_length=64)
    score: int | None = Field(default=None, ge=0, le=100)
    note: str | None = Field(default=None, max_length=4000)
    metadata: dict | None = Field(
        default=None,
        description="Произвольный JSON. Для Profile Selector: outcome (см. FeedbackOutcome в profile_engine), "
        "profile_selector — срез с клиента, совпадающий с полем profile_selector в generation input_payload.",
    )


@router.post("/feedback")
def submit_generation_feedback(
    payload: GenerationFeedbackPayload,
    user: db_models.User = Depends(require_user),
    db: Session = Depends(get_session),
    learning_service: LearningService = Depends(get_learning_service),
) -> dict:
    generation = db.query(db_models.GenerationLog).filter_by(id=payload.generation_log_id).first()
    if generation is None:
        raise HTTPException(status_code=404, detail="Generation log not found")
    if generation.user_id is not None and generation.user_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Access forbidden")

    feedback = learning_service.add_feedback(
        db,
        generation_log_id=generation.id,
        user_id=user.id,
        signal=payload.signal,
        score=payload.score,
        note=payload.note,
        metadata=payload.metadata,
    )
    return {
        "feedback_id": feedback.id,
        "generation_log_id": generation.id,
        "signal": feedback.signal,
        "score": feedback.score,
    }


@router.get("/prompts")
def list_prompt_versions(
    module: str | None = None,
    admin: db_models.User = Depends(require_admin),
    db: Session = Depends(get_session),
) -> dict:
    query = db.query(db_models.PromptVersion).order_by(
        db_models.PromptVersion.module.asc(),
        db_models.PromptVersion.version.desc(),
        db_models.PromptVersion.prompt_kind.asc(),
    )
    if module:
        query = query.filter_by(module=module)

    items = query.all()
    return {
        "items": [
            {
                "id": item.id,
                "module": item.module,
                "version": item.version,
                "prompt_kind": item.prompt_kind,
                "label": item.label,
                "is_active": item.is_active,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
                "metadata": item.meta_payload,
            }
            for item in items
        ]
    }
