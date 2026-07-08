"""API для связки дня (Day Connection) - связь между утром и вечером."""

from datetime import date
from typing import Literal, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from todayflow_backend.api.auth import require_user
from todayflow_backend.api.date_utils import parse_iso_date_or_400
from todayflow_backend.db.session import get_session
from todayflow_backend.db.models import DayConnection, User
from todayflow_backend.services.push_delivery import notify_morning_intention_saved

router = APIRouter(prefix="/day-connection", tags=["day-connection"])


class DayConnectionCreate(BaseModel):
    """Создание/обновление связки дня."""
    morning_intention: Optional[str] = None
    morning_focus: Optional[str] = None
    evening_reflection: Optional[str] = None
    evening_observations: Optional[dict] = None
    connection_thread: Optional[str] = None
    ritual_feedback: Optional[Literal["yes", "partial", "no"]] = None
    quick_decision_answer: Optional[Literal["yes", "no", "unclear"]] = None
    question_of_day_answer: Optional[str] = None
    morning_completed: Optional[bool] = None
    day_completed: Optional[bool] = None
    evening_completed: Optional[bool] = None


class DayConnectionResponse(BaseModel):
    """Ответ с связкой дня."""
    id: int
    date: str
    morning_intention: Optional[str]
    morning_focus: Optional[str]
    evening_reflection: Optional[str]
    evening_observations: Optional[dict]
    connection_thread: Optional[str]
    ritual_feedback: Optional[str]
    quick_decision_answer: Optional[str]
    question_of_day_answer: Optional[str]
    morning_completed: bool
    day_completed: bool
    evening_completed: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.get("/{target_date}", response_model=Optional[DayConnectionResponse])
def get_day_connection(
    target_date: str,
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
) -> Optional[DayConnectionResponse]:
    """Получить связку дня по дате."""
    date_obj = parse_iso_date_or_400(target_date)
    
    connection = db.query(DayConnection).filter(
        DayConnection.user_id == user.id,
        DayConnection.date == date_obj
    ).first()
    
    if not connection:
        return None
    
    return DayConnectionResponse(
        id=connection.id,
        date=connection.date.isoformat(),
        morning_intention=connection.morning_intention,
        morning_focus=connection.morning_focus,
        evening_reflection=connection.evening_reflection,
        evening_observations=connection.evening_observations,
        connection_thread=connection.connection_thread,
        ritual_feedback=connection.ritual_feedback,
        quick_decision_answer=connection.quick_decision_answer,
        question_of_day_answer=connection.question_of_day_answer,
        morning_completed=connection.morning_completed,
        day_completed=connection.day_completed,
        evening_completed=connection.evening_completed,
        created_at=connection.created_at.isoformat(),
        updated_at=connection.updated_at.isoformat(),
    )


@router.post("/{target_date}", response_model=DayConnectionResponse)
def create_or_update_day_connection(
    target_date: str,
    connection_data: DayConnectionCreate,
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
) -> DayConnectionResponse:
    """Создать или обновить связку дня."""
    date_obj = parse_iso_date_or_400(target_date)
    
    # Проверяем, есть ли уже связка
    existing = db.query(DayConnection).filter(
        DayConnection.user_id == user.id,
        DayConnection.date == date_obj
    ).first()
    
    if existing:
        # Обновляем существующую
        prev_morning_intention = existing.morning_intention
        if connection_data.morning_intention is not None:
            existing.morning_intention = connection_data.morning_intention
        if connection_data.morning_focus is not None:
            existing.morning_focus = connection_data.morning_focus
        if connection_data.evening_reflection is not None:
            existing.evening_reflection = connection_data.evening_reflection
        if connection_data.evening_observations is not None:
            existing.evening_observations = connection_data.evening_observations
        if connection_data.connection_thread is not None:
            existing.connection_thread = connection_data.connection_thread
        if connection_data.ritual_feedback is not None:
            existing.ritual_feedback = connection_data.ritual_feedback
        if connection_data.quick_decision_answer is not None:
            existing.quick_decision_answer = connection_data.quick_decision_answer
        if connection_data.question_of_day_answer is not None:
            existing.question_of_day_answer = connection_data.question_of_day_answer
        if connection_data.morning_completed is not None:
            existing.morning_completed = connection_data.morning_completed
        if connection_data.day_completed is not None:
            existing.day_completed = connection_data.day_completed
        if connection_data.evening_completed is not None:
            existing.evening_completed = connection_data.evening_completed
        
        from datetime import datetime
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)

        if connection_data.morning_intention is not None:
            new_g = (connection_data.morning_intention or "").strip()
            old_g = (prev_morning_intention or "").strip()
            if new_g and new_g != old_g:
                notify_morning_intention_saved(db, user, intention_preview=new_g)
                from todayflow_backend.api.today import invalidate_morning_cache_for_user

                invalidate_morning_cache_for_user(user.id)

        return DayConnectionResponse(
            id=existing.id,
            date=existing.date.isoformat(),
            morning_intention=existing.morning_intention,
            morning_focus=existing.morning_focus,
            evening_reflection=existing.evening_reflection,
            evening_observations=existing.evening_observations,
            connection_thread=existing.connection_thread,
            ritual_feedback=existing.ritual_feedback,
            quick_decision_answer=existing.quick_decision_answer,
            question_of_day_answer=existing.question_of_day_answer,
            morning_completed=existing.morning_completed,
            day_completed=existing.day_completed,
            evening_completed=existing.evening_completed,
            created_at=existing.created_at.isoformat(),
            updated_at=existing.updated_at.isoformat(),
        )
    
    # Создаём новую связку
    new_connection = DayConnection(
        user_id=user.id,
        date=date_obj,
        morning_intention=connection_data.morning_intention,
        morning_focus=connection_data.morning_focus,
        evening_reflection=connection_data.evening_reflection,
        evening_observations=connection_data.evening_observations,
        connection_thread=connection_data.connection_thread,
        ritual_feedback=connection_data.ritual_feedback,
        quick_decision_answer=connection_data.quick_decision_answer,
        question_of_day_answer=connection_data.question_of_day_answer,
        morning_completed=connection_data.morning_completed or False,
        day_completed=connection_data.day_completed or False,
        evening_completed=connection_data.evening_completed or False,
    )
    
    db.add(new_connection)
    db.commit()
    db.refresh(new_connection)

    if connection_data.morning_intention is not None:
        new_g = (connection_data.morning_intention or "").strip()
        if new_g:
            notify_morning_intention_saved(db, user, intention_preview=new_g)
            from todayflow_backend.api.today import invalidate_morning_cache_for_user

            invalidate_morning_cache_for_user(user.id)

    return DayConnectionResponse(
        id=new_connection.id,
        date=new_connection.date.isoformat(),
        morning_intention=new_connection.morning_intention,
        morning_focus=new_connection.morning_focus,
        evening_reflection=new_connection.evening_reflection,
        evening_observations=new_connection.evening_observations,
        connection_thread=new_connection.connection_thread,
        ritual_feedback=new_connection.ritual_feedback,
        quick_decision_answer=new_connection.quick_decision_answer,
        question_of_day_answer=new_connection.question_of_day_answer,
        morning_completed=new_connection.morning_completed,
        day_completed=new_connection.day_completed,
        evening_completed=new_connection.evening_completed,
        created_at=new_connection.created_at.isoformat(),
        updated_at=new_connection.updated_at.isoformat(),
    )
