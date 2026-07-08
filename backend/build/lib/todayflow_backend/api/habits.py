"""Habits API endpoints."""

from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from todayflow_backend.api.auth import require_user
from todayflow_backend.db.models import Habit, HabitEntry, User
from todayflow_backend.db.session import get_session

router = APIRouter(prefix="/habits", tags=["habits"])


class HabitCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: Optional[str] = None
    target_frequency: str = Field(default="daily")
    target_per_period: int = Field(default=1, ge=1, le=14)


class HabitUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    category: Optional[str] = None
    target_frequency: Optional[str] = None
    target_per_period: Optional[int] = Field(default=None, ge=1, le=14)
    is_active: Optional[bool] = None


class HabitResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    target_frequency: str
    target_per_period: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class HabitEntryCreate(BaseModel):
    date: str  # YYYY-MM-DD
    completed: bool = True
    intensity: Optional[int] = Field(default=None, ge=1, le=5)
    note: Optional[str] = None


class HabitEntryResponse(BaseModel):
    id: int
    habit_id: int
    date: str
    completed: bool
    intensity: Optional[int]
    note: Optional[str]
    created_at: datetime
    updated_at: datetime


class HabitOverviewItem(BaseModel):
    habit_id: int
    name: str
    category: Optional[str]
    current_streak_days: int
    completion_rate: float
    completed_days: int
    tracked_days: int


def _parse_iso_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Date must be in YYYY-MM-DD format") from exc


@router.post("", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
def create_habit(
    payload: HabitCreate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    existing = db.query(Habit).filter(Habit.user_id == current_user.id, Habit.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Habit with this name already exists")

    habit = Habit(
        user_id=current_user.id,
        name=payload.name.strip(),
        category=payload.category.strip() if payload.category else None,
        target_frequency=payload.target_frequency,
        target_per_period=payload.target_per_period,
        is_active=True,
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


@router.get("", response_model=List[HabitResponse])
def get_habits(
    include_inactive: bool = False,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    query = db.query(Habit).filter(Habit.user_id == current_user.id)
    if not include_inactive:
        query = query.filter(Habit.is_active == True)  # noqa: E712
    return query.order_by(Habit.created_at.desc()).all()


@router.put("/{habit_id}", response_model=HabitResponse)
def update_habit(
    habit_id: int,
    payload: HabitUpdate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    if (
        payload.name is None
        and payload.category is None
        and payload.target_frequency is None
        and payload.target_per_period is None
        and payload.is_active is None
    ):
        raise HTTPException(status_code=400, detail="No fields to update")

    if payload.name is not None:
        name = payload.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="Habit name is required")
        other = (
            db.query(Habit)
            .filter(Habit.user_id == current_user.id, Habit.name == name, Habit.id != habit_id)
            .first()
        )
        if other:
            raise HTTPException(status_code=400, detail="Habit with this name already exists")
        habit.name = name

    if payload.category is not None:
        habit.category = payload.category.strip() if payload.category.strip() else None

    if payload.target_frequency is not None:
        tf = (payload.target_frequency or "").strip().lower()
        if tf not in ("daily", "weekly"):
            raise HTTPException(status_code=400, detail="target_frequency must be daily or weekly")
        habit.target_frequency = tf

    if payload.target_per_period is not None:
        habit.target_per_period = payload.target_per_period

    if payload.is_active is not None:
        habit.is_active = payload.is_active

    habit.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(habit)
    return habit


@router.post("/{habit_id}/entries", response_model=HabitEntryResponse, status_code=status.HTTP_201_CREATED)
def upsert_habit_entry(
    habit_id: int,
    payload: HabitEntryCreate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    entry_date = _parse_iso_date(payload.date)

    entry = db.query(HabitEntry).filter(
        HabitEntry.user_id == current_user.id,
        HabitEntry.habit_id == habit_id,
        HabitEntry.date == entry_date,
    ).first()
    if entry:
        entry.completed = payload.completed
        entry.intensity = payload.intensity
        entry.note = payload.note
        entry.updated_at = datetime.utcnow()
    else:
        entry = HabitEntry(
            user_id=current_user.id,
            habit_id=habit_id,
            date=entry_date,
            completed=payload.completed,
            intensity=payload.intensity,
            note=payload.note,
        )
        db.add(entry)

    db.commit()
    db.refresh(entry)
    return HabitEntryResponse(
        id=entry.id,
        habit_id=entry.habit_id,
        date=entry.date.isoformat(),
        completed=entry.completed,
        intensity=entry.intensity,
        note=entry.note,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


@router.get("/{habit_id}/entries", response_model=List[HabitEntryResponse])
def get_habit_entries(
    habit_id: int,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    query = db.query(HabitEntry).filter(HabitEntry.user_id == current_user.id, HabitEntry.habit_id == habit_id)
    if from_date:
        query = query.filter(HabitEntry.date >= _parse_iso_date(from_date))
    if to_date:
        query = query.filter(HabitEntry.date <= _parse_iso_date(to_date))

    entries = query.order_by(HabitEntry.date.desc()).all()
    return [
        HabitEntryResponse(
            id=entry.id,
            habit_id=entry.habit_id,
            date=entry.date.isoformat(),
            completed=entry.completed,
            intensity=entry.intensity,
            note=entry.note,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
        )
        for entry in entries
    ]


@router.get("/overview/summary", response_model=List[HabitOverviewItem])
def habits_overview(
    period_days: int = 30,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    period_days = max(7, min(period_days, 90))
    end_date = date.today()
    start_date = end_date - timedelta(days=period_days - 1)

    habits = db.query(Habit).filter(Habit.user_id == current_user.id, Habit.is_active == True).all()  # noqa: E712
    result: List[HabitOverviewItem] = []

    for habit in habits:
        entries = db.query(HabitEntry).filter(
            HabitEntry.user_id == current_user.id,
            HabitEntry.habit_id == habit.id,
            HabitEntry.date >= start_date,
            HabitEntry.date <= end_date,
        ).all()
        completed_days = sum(1 for entry in entries if entry.completed)
        tracked_days = len(entries)
        completion_rate = round((completed_days / period_days) * 100, 2) if period_days > 0 else 0.0

        # Current streak from today backwards.
        streak = 0
        cursor = end_date
        entries_by_date = {entry.date: entry for entry in entries}
        while cursor >= start_date:
            day_entry = entries_by_date.get(cursor)
            if day_entry and day_entry.completed:
                streak += 1
                cursor -= timedelta(days=1)
            else:
                break

        result.append(
            HabitOverviewItem(
                habit_id=habit.id,
                name=habit.name,
                category=habit.category,
                current_streak_days=streak,
                completion_rate=completion_rate,
                completed_days=completed_days,
                tracked_days=tracked_days,
            )
        )

    result.sort(key=lambda item: (item.current_streak_days, item.completion_rate), reverse=True)
    return result
