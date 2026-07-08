"""API endpoints для календаря-органайзера."""

from datetime import datetime, date, time as dt_time, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from todayflow_backend.api.auth import require_user
from todayflow_backend.db.session import get_session
from todayflow_backend.db.models import (
    User,
    CalendarEvent,
    CalendarNote,
    MenstrualCycle,
    ProgressTrackerEntry,
    ObservationDiaryEntry,
    DayConnection,
    DayRitual,
    PracticeUsage,
    SavedForecast
)

router = APIRouter(prefix="/calendar", tags=["calendar"])


# ============================================================================
# Единый календарь-органайзер (объединённый endpoint)
# ============================================================================

class UnifiedCalendarDayResponse(BaseModel):
    """Данные одного дня для единого календаря."""
    date: str
    # Органайзер
    events: List[dict] = []
    notes: List[dict] = []
    # Цикл (если включён)
    cycle: Optional[dict] = None
    # Полезная нагрузка
    activities: dict = {}  # practice, affirmation, asceticism, diary, ritual
    mood: Optional[int] = None  # 1-5
    forecast: Optional[dict] = None  # Прогноз на дату
    weekly_integration: Optional[dict] = None  # Недельная интеграция
    streaks: dict = {}  # Текущие стрики по активностям


class UnifiedCalendarResponse(BaseModel):
    """Ответ с данными единого календаря за период."""
    days: List[UnifiedCalendarDayResponse]
    streaks: dict  # Общие стрики
    stats: dict  # Статистика по активностям
    filters: dict  # Доступные фильтры


@router.get("/unified", response_model=UnifiedCalendarResponse)
def get_unified_calendar(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    include_cycle: bool = False,
    include_tracker: bool = True,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """
    Получить данные единого календаря-органайзера за период.
    Объединяет события, записи, цикл, трекер активностей, прогнозы, настроение.
    """
    # Определяем период
    today = date.today()
    if not from_date:
        from_date_obj = today.replace(day=1)
    else:
        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
    
    if not to_date:
        if today.month == 12:
            to_date_obj = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            to_date_obj = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    else:
        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
    
    # Загружаем все данные
    events = db.query(CalendarEvent).filter(
        CalendarEvent.user_id == current_user.id,
        CalendarEvent.date >= from_date_obj,
        CalendarEvent.date <= to_date_obj
    ).all()
    
    notes = db.query(CalendarNote).filter(
        CalendarNote.user_id == current_user.id,
        CalendarNote.date >= from_date_obj,
        CalendarNote.date <= to_date_obj
    ).all()
    
    cycles = []
    if include_cycle:
        cycles = db.query(MenstrualCycle).filter(
            MenstrualCycle.user_id == current_user.id,
            MenstrualCycle.date >= from_date_obj,
            MenstrualCycle.date <= to_date_obj
        ).all()
    
    activities_data = {}
    if include_tracker:
        progress_entries = db.query(ProgressTrackerEntry).filter(
            ProgressTrackerEntry.user_id == current_user.id,
            ProgressTrackerEntry.date >= from_date_obj,
            ProgressTrackerEntry.date <= to_date_obj
        ).all()
        
        diary_entries = db.query(ObservationDiaryEntry).filter(
            ObservationDiaryEntry.user_id == current_user.id,
            ObservationDiaryEntry.date >= from_date_obj,
            ObservationDiaryEntry.date <= to_date_obj
        ).all()
        
        ritual_entries = db.query(DayRitual).filter(
            DayRitual.user_id == current_user.id,
            DayRitual.date >= from_date_obj,
            DayRitual.date <= to_date_obj
        ).all()
        
        practice_usages = db.query(PracticeUsage).filter(
            PracticeUsage.user_id == current_user.id,
            func.date(PracticeUsage.completed_at) >= from_date_obj,
            func.date(PracticeUsage.completed_at) <= to_date_obj
        ).all()
        day_connections = db.query(DayConnection).filter(
            DayConnection.user_id == current_user.id,
            DayConnection.date >= from_date_obj,
            DayConnection.date <= to_date_obj,
        ).all()
        
        # Группируем по дням
        for entry in progress_entries:
            day_key = entry.date.isoformat()
            if day_key not in activities_data:
                activities_data[day_key] = {}
            if entry.asceticism_id:
                activities_data[day_key]["asceticism"] = {
                    "completed": entry.completed,
                    "state_scale": entry.state_scale,
                    "note": entry.note
                }
            if entry.affirmation_id:
                activities_data[day_key]["affirmation"] = {
                    "completed": entry.completed,
                    "state_scale": entry.state_scale,
                    "note": entry.note
                }
        
        for entry in diary_entries:
            day_key = entry.date.isoformat()
            if day_key not in activities_data:
                activities_data[day_key] = {}
            activities_data[day_key]["diary"] = {
                "completed": True,
                "note": entry.noticed
            }
            # Настроение из дневника (если есть state_scale)
            if hasattr(entry, 'state_scale') and entry.state_scale:
                activities_data[day_key]["mood"] = entry.state_scale
        
        for entry in ritual_entries:
            day_key = entry.date.isoformat()
            if day_key not in activities_data:
                activities_data[day_key] = {}
            activities_data[day_key]["ritual"] = {
                "completed": entry.completed
            }
        
        for usage in practice_usages:
            day_key = usage.completed_at.date().isoformat()
            if day_key not in activities_data:
                activities_data[day_key] = {}
            if "practice" not in activities_data[day_key]:
                activities_data[day_key]["practice"] = {"completed": True, "count": 0}
            activities_data[day_key]["practice"]["count"] = activities_data[day_key]["practice"].get("count", 0) + 1

        for entry in day_connections:
            day_key = entry.date.isoformat()
            signals_count = int(bool(entry.ritual_feedback)) + int(bool(entry.quick_decision_answer)) + int(bool(entry.question_of_day_answer))
            if signals_count == 0:
                continue
            if day_key not in activities_data:
                activities_data[day_key] = {}
            activities_data[day_key]["daily_signals"] = {
                "completed": True,
                "signals_count": signals_count,
                "ritual_feedback": entry.ritual_feedback,
                "quick_decision_answer": entry.quick_decision_answer,
                "question_of_day_answer": entry.question_of_day_answer,
            }
    
    # Прогнозы
    forecasts = db.query(SavedForecast).filter(
        SavedForecast.user_id == current_user.id,
        SavedForecast.date >= from_date_obj,
        SavedForecast.date <= to_date_obj
    ).all()
    
    # Группируем по дням
    days_dict: dict = {}
    current_date = from_date_obj
    while current_date <= to_date_obj:
        day_key = current_date.isoformat()
        days_dict[day_key] = UnifiedCalendarDayResponse(
            date=day_key,
            events=[],
            notes=[],
            cycle=None,
            activities=activities_data.get(day_key, {}),
            mood=activities_data.get(day_key, {}).get("mood"),
            forecast=None,
            weekly_integration=None,
            streaks={}
        )
        current_date += timedelta(days=1)
    
    # Заполняем события
    for event in events:
        day_key = event.date.isoformat()
        if day_key in days_dict:
            days_dict[day_key].events.append({
                "id": event.id,
                "title": event.title,
                "time": event.time.strftime('%H:%M') if event.time else None,
                "is_all_day": event.is_all_day,
                "color": event.color,
                "category": event.category
            })
    
    # Заполняем записи
    for note in notes:
        day_key = note.date.isoformat()
        if day_key in days_dict:
            days_dict[day_key].notes.append({
                "id": note.id,
                "text": note.note_text,
                "event_id": note.event_id
            })
    
    # Заполняем цикл
    for cycle_entry in cycles:
        day_key = cycle_entry.date.isoformat()
        if day_key in days_dict:
            days_dict[day_key].cycle = {
                "cycle_day": cycle_entry.cycle_day,
                "period_intensity": cycle_entry.period_intensity,
                "ovulation": cycle_entry.ovulation,
                "fertile_window": cycle_entry.fertile_window,
                "symptoms": cycle_entry.symptoms
            }
    
    # Заполняем прогнозы
    for forecast in forecasts:
        day_key = forecast.date.isoformat()
        if day_key in days_dict:
            days_dict[day_key].forecast = {
                "id": forecast.id,
                "theme": forecast.blocks.get("theme", "") if isinstance(forecast.blocks, dict) else "",
                "has_forecast": True
            }
    
    # Вычисляем стрики
    streaks = {}
    stats = {}
    
    if include_tracker:
        # Вычисляем стрики для каждой активности
        activity_types = ["practice", "affirmation", "asceticism", "diary", "ritual", "daily_signals"]
        for activity_type in activity_types:
            current_streak = 0
            total = 0
            completed = 0
            
            # Идём от сегодня назад
            check_date = today
            while check_date >= from_date_obj:
                day_key = check_date.isoformat()
                day_data = activities_data.get(day_key, {})
                activity = day_data.get(activity_type)
                
                if activity:
                    total += 1
                    if activity.get("completed"):
                        completed += 1
                        if check_date == today or (check_date < today and current_streak > 0):
                            current_streak += 1
                        elif check_date == today:
                            current_streak = 1
                    else:
                        if check_date < today:
                            break
                else:
                    if check_date < today:
                        break
                
                check_date -= timedelta(days=1)
            
            streaks[activity_type] = current_streak
            stats[activity_type] = {
                "total": total,
                "completed": completed,
                "percentage": round((completed / total * 100) if total > 0 else 0, 1)
            }
    
    return UnifiedCalendarResponse(
        days=list(days_dict.values()),
        streaks=streaks,
        stats=stats,
        filters={
            "include_cycle": include_cycle,
            "include_tracker": include_tracker
        }
    )


# ============================================================================
# Календарные события
# ============================================================================

class CalendarEventCreate(BaseModel):
    """Создание календарного события."""
    title: str
    date: str  # YYYY-MM-DD
    time: Optional[str] = None  # HH:MM или null для "весь день"
    is_all_day: bool = False
    color: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    repeat_type: Optional[str] = None  # "none", "daily", "weekly", "monthly"
    reminder_minutes: Optional[int] = None


class CalendarEventUpdate(BaseModel):
    """Обновление календарного события."""
    title: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    is_all_day: Optional[bool] = None
    color: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    repeat_type: Optional[str] = None
    reminder_minutes: Optional[int] = None


class CalendarEventResponse(BaseModel):
    """Ответ с календарным событием."""
    id: int
    title: str
    date: str
    time: Optional[str] = None
    is_all_day: bool
    color: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    repeat_type: Optional[str] = None
    reminder_minutes: Optional[int] = None
    created_at: datetime
    updated_at: datetime


@router.post("/events", response_model=CalendarEventResponse, status_code=status.HTTP_201_CREATED)
def create_calendar_event(
    event: CalendarEventCreate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Создать календарное событие."""
    event_date = datetime.strptime(event.date, '%Y-%m-%d').date()
    event_time = None
    if event.time and not event.is_all_day:
        try:
            event_time = datetime.strptime(event.time, '%H:%M').time()
        except ValueError:
            pass
    
    db_event = CalendarEvent(
        user_id=current_user.id,
        title=event.title,
        date=event_date,
        time=event_time,
        is_all_day=event.is_all_day,
        color=event.color,
        category=event.category,
        description=event.description,
        repeat_type=event.repeat_type or "none",
        reminder_minutes=event.reminder_minutes
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    return CalendarEventResponse(
        id=db_event.id,
        title=db_event.title,
        date=db_event.date.isoformat(),
        time=db_event.time.strftime('%H:%M') if db_event.time else None,
        is_all_day=db_event.is_all_day,
        color=db_event.color,
        category=db_event.category,
        description=db_event.description,
        repeat_type=db_event.repeat_type,
        reminder_minutes=db_event.reminder_minutes,
        created_at=db_event.created_at,
        updated_at=db_event.updated_at
    )


@router.get("/events", response_model=List[CalendarEventResponse])
def get_calendar_events(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Получить календарные события за период."""
    query = db.query(CalendarEvent).filter(CalendarEvent.user_id == current_user.id)
    
    if from_date:
        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
        query = query.filter(CalendarEvent.date >= from_date_obj)
    
    if to_date:
        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
        query = query.filter(CalendarEvent.date <= to_date_obj)
    
    events = query.order_by(CalendarEvent.date, CalendarEvent.time).all()
    
    return [
        CalendarEventResponse(
            id=e.id,
            title=e.title,
            date=e.date.isoformat(),
            time=e.time.strftime('%H:%M') if e.time else None,
            is_all_day=e.is_all_day,
            color=e.color,
            category=e.category,
            description=e.description,
            repeat_type=e.repeat_type,
            reminder_minutes=e.reminder_minutes,
            created_at=e.created_at,
            updated_at=e.updated_at
        )
        for e in events
    ]


@router.put("/events/{event_id}", response_model=CalendarEventResponse)
def update_calendar_event(
    event_id: int,
    event_update: CalendarEventUpdate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Обновить календарное событие."""
    db_event = db.query(CalendarEvent).filter(
        CalendarEvent.id == event_id,
        CalendarEvent.user_id == current_user.id
    ).first()
    
    if not db_event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    
    if event_update.title is not None:
        db_event.title = event_update.title
    if event_update.date is not None:
        db_event.date = datetime.strptime(event_update.date, '%Y-%m-%d').date()
    if event_update.time is not None:
        if event_update.time:
            db_event.time = datetime.strptime(event_update.time, '%H:%M').time()
        else:
            db_event.time = None
    if event_update.is_all_day is not None:
        db_event.is_all_day = event_update.is_all_day
    if event_update.color is not None:
        db_event.color = event_update.color
    if event_update.category is not None:
        db_event.category = event_update.category
    if event_update.description is not None:
        db_event.description = event_update.description
    if event_update.repeat_type is not None:
        db_event.repeat_type = event_update.repeat_type
    if event_update.reminder_minutes is not None:
        db_event.reminder_minutes = event_update.reminder_minutes
    
    db_event.updated_at = datetime.now()
    db.commit()
    db.refresh(db_event)
    
    return CalendarEventResponse(
        id=db_event.id,
        title=db_event.title,
        date=db_event.date.isoformat(),
        time=db_event.time.strftime('%H:%M') if db_event.time else None,
        is_all_day=db_event.is_all_day,
        color=db_event.color,
        category=db_event.category,
        description=db_event.description,
        repeat_type=db_event.repeat_type,
        reminder_minutes=db_event.reminder_minutes,
        created_at=db_event.created_at,
        updated_at=db_event.updated_at
    )


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calendar_event(
    event_id: int,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Удалить календарное событие."""
    db_event = db.query(CalendarEvent).filter(
        CalendarEvent.id == event_id,
        CalendarEvent.user_id == current_user.id
    ).first()
    
    if not db_event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    
    db.delete(db_event)
    db.commit()
    return None


# ============================================================================
# Записи к дню
# ============================================================================

class CalendarNoteCreate(BaseModel):
    """Создание записи к дню."""
    date: str  # YYYY-MM-DD
    event_id: Optional[int] = None
    note_text: str


class CalendarNoteResponse(BaseModel):
    """Ответ с записью к дню."""
    id: int
    date: str
    event_id: Optional[int] = None
    note_text: str
    created_at: datetime
    updated_at: datetime


@router.post("/notes", response_model=CalendarNoteResponse, status_code=status.HTTP_201_CREATED)
def create_calendar_note(
    note: CalendarNoteCreate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Создать запись к дню."""
    note_date = datetime.strptime(note.date, '%Y-%m-%d').date()
    
    # Проверяем, нет ли уже записи на эту дату
    existing = db.query(CalendarNote).filter(
        CalendarNote.user_id == current_user.id,
        CalendarNote.date == note_date
    ).first()
    
    if existing:
        existing.note_text = note.note_text
        existing.event_id = note.event_id
        existing.updated_at = datetime.now()
        db.commit()
        db.refresh(existing)
        return CalendarNoteResponse(
            id=existing.id,
            date=existing.date.isoformat(),
            event_id=existing.event_id,
            note_text=existing.note_text,
            created_at=existing.created_at,
            updated_at=existing.updated_at
        )
    
    db_note = CalendarNote(
        user_id=current_user.id,
        date=note_date,
        event_id=note.event_id,
        note_text=note.note_text
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    return CalendarNoteResponse(
        id=db_note.id,
        date=db_note.date.isoformat(),
        event_id=db_note.event_id,
        note_text=db_note.note_text,
        created_at=db_note.created_at,
        updated_at=db_note.updated_at
    )


@router.get("/notes", response_model=List[CalendarNoteResponse])
def get_calendar_notes(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Получить записи к дням за период."""
    query = db.query(CalendarNote).filter(CalendarNote.user_id == current_user.id)
    
    if from_date:
        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
        query = query.filter(CalendarNote.date >= from_date_obj)
    
    if to_date:
        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
        query = query.filter(CalendarNote.date <= to_date_obj)
    
    notes = query.order_by(CalendarNote.date.desc()).all()
    
    return [
        CalendarNoteResponse(
            id=n.id,
            date=n.date.isoformat(),
            event_id=n.event_id,
            note_text=n.note_text,
            created_at=n.created_at,
            updated_at=n.updated_at
        )
        for n in notes
    ]


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calendar_note(
    note_id: int,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Удалить запись к дню."""
    db_note = db.query(CalendarNote).filter(
        CalendarNote.id == note_id,
        CalendarNote.user_id == current_user.id
    ).first()
    
    if not db_note:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    
    db.delete(db_note)
    db.commit()
    return None


# ============================================================================
# Трекинг менструального цикла (опционально)
# ============================================================================

class MenstrualCycleCreate(BaseModel):
    """Создание записи трекинга цикла."""
    date: str  # YYYY-MM-DD
    cycle_day: Optional[int] = None
    period_intensity: Optional[str] = None  # "light", "medium", "heavy"
    ovulation: bool = False
    fertile_window: bool = False
    symptoms: Optional[dict] = None


class MenstrualCycleResponse(BaseModel):
    """Ответ с записью трекинга цикла."""
    id: int
    date: str
    cycle_day: Optional[int] = None
    period_intensity: Optional[str] = None
    ovulation: bool
    fertile_window: bool
    symptoms: Optional[dict] = None
    created_at: datetime
    updated_at: datetime


class MenstrualCycleInsightsResponse(BaseModel):
    """Сводка по циклу за период."""
    from_date: str
    to_date: str
    tracked_days: int
    average_cycle_day: Optional[float] = None
    period_intensity_distribution: dict
    ovulation_days: int
    fertile_window_days: int
    top_symptoms: List[dict]
    recommendations: List[str]


@router.post("/cycle", response_model=MenstrualCycleResponse, status_code=status.HTTP_201_CREATED)
def create_menstrual_cycle_entry(
    entry: MenstrualCycleCreate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Создать запись трекинга менструального цикла."""
    entry_date = datetime.strptime(entry.date, '%Y-%m-%d').date()
    
    # Проверяем, нет ли уже записи на эту дату
    existing = db.query(MenstrualCycle).filter(
        MenstrualCycle.user_id == current_user.id,
        MenstrualCycle.date == entry_date
    ).first()
    
    if existing:
        if entry.cycle_day is not None:
            existing.cycle_day = entry.cycle_day
        if entry.period_intensity is not None:
            existing.period_intensity = entry.period_intensity
        existing.ovulation = entry.ovulation
        existing.fertile_window = entry.fertile_window
        if entry.symptoms is not None:
            existing.symptoms = entry.symptoms
        existing.updated_at = datetime.now()
        db.commit()
        db.refresh(existing)
        return MenstrualCycleResponse(
            id=existing.id,
            date=existing.date.isoformat(),
            cycle_day=existing.cycle_day,
            period_intensity=existing.period_intensity,
            ovulation=existing.ovulation,
            fertile_window=existing.fertile_window,
            symptoms=existing.symptoms,
            created_at=existing.created_at,
            updated_at=existing.updated_at
        )
    
    db_entry = MenstrualCycle(
        user_id=current_user.id,
        date=entry_date,
        cycle_day=entry.cycle_day,
        period_intensity=entry.period_intensity,
        ovulation=entry.ovulation,
        fertile_window=entry.fertile_window,
        symptoms=entry.symptoms
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    return MenstrualCycleResponse(
        id=db_entry.id,
        date=db_entry.date.isoformat(),
        cycle_day=db_entry.cycle_day,
        period_intensity=db_entry.period_intensity,
        ovulation=db_entry.ovulation,
        fertile_window=db_entry.fertile_window,
        symptoms=db_entry.symptoms,
        created_at=db_entry.created_at,
        updated_at=db_entry.updated_at
    )


@router.get("/cycle", response_model=List[MenstrualCycleResponse])
def get_menstrual_cycle_entries(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Получить записи трекинга цикла за период."""
    query = db.query(MenstrualCycle).filter(MenstrualCycle.user_id == current_user.id)
    
    if from_date:
        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
        query = query.filter(MenstrualCycle.date >= from_date_obj)
    
    if to_date:
        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
        query = query.filter(MenstrualCycle.date <= to_date_obj)
    
    entries = query.order_by(MenstrualCycle.date.desc()).all()
    
    return [
        MenstrualCycleResponse(
            id=e.id,
            date=e.date.isoformat(),
            cycle_day=e.cycle_day,
            period_intensity=e.period_intensity,
            ovulation=e.ovulation,
            fertile_window=e.fertile_window,
            symptoms=e.symptoms,
            created_at=e.created_at,
            updated_at=e.updated_at
        )
        for e in entries
    ]


@router.get("/cycle/insights", response_model=MenstrualCycleInsightsResponse)
def get_menstrual_cycle_insights(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Получить сводку и рекомендации по циклу за период."""
    today = date.today()
    if not to_date:
        to_date_obj = today
    else:
        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()

    if not from_date:
        from_date_obj = to_date_obj - timedelta(days=29)
    else:
        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()

    entries = db.query(MenstrualCycle).filter(
        MenstrualCycle.user_id == current_user.id,
        MenstrualCycle.date >= from_date_obj,
        MenstrualCycle.date <= to_date_obj
    ).order_by(MenstrualCycle.date.asc()).all()

    intensity_distribution = {
        "none": 0,
        "light": 0,
        "medium": 0,
        "heavy": 0,
    }
    ovulation_days = 0
    fertile_window_days = 0
    cycle_day_values: List[int] = []
    symptom_counter: dict = {}

    for entry in entries:
        level = entry.period_intensity or "none"
        if level not in intensity_distribution:
            level = "none"
        intensity_distribution[level] += 1
        if entry.ovulation:
            ovulation_days += 1
        if entry.fertile_window:
            fertile_window_days += 1
        if entry.cycle_day:
            cycle_day_values.append(entry.cycle_day)
        if isinstance(entry.symptoms, dict):
            for key, value in entry.symptoms.items():
                if isinstance(value, bool) and value:
                    symptom_counter[key] = symptom_counter.get(key, 0) + 1
                elif isinstance(value, (int, float)) and value >= 3:
                    symptom_counter[key] = symptom_counter.get(key, 0) + 1
                elif isinstance(value, str) and value.strip():
                    symptom_counter[key] = symptom_counter.get(key, 0) + 1
                elif isinstance(value, list):
                    for item in value:
                        label = str(item).strip()
                        if label:
                            symptom_counter[label] = symptom_counter.get(label, 0) + 1

    average_cycle_day = None
    if cycle_day_values:
        average_cycle_day = round(sum(cycle_day_values) / len(cycle_day_values), 2)

    top_symptoms = sorted(
        [{"label": key, "count": count} for key, count in symptom_counter.items()],
        key=lambda row: row["count"],
        reverse=True,
    )[:5]

    recommendations: List[str] = []
    if intensity_distribution["heavy"] >= 2:
        recommendations.append("В дни с высокой интенсивностью снижай нагрузку и планируй восстановление.")
    if fertile_window_days > 0:
        recommendations.append("В фертильные дни ставь коммуникационные и творческие задачи в приоритет.")
    if ovulation_days > 0:
        recommendations.append("Окно овуляции часто дает рост энергии: используй его для сложных дел.")
    if not entries:
        recommendations.append("Начни с 7 дней фиксации цикла, чтобы получить персональные паттерны.")
    if not recommendations:
        recommendations.append("Ритм цикла выглядит стабильным. Продолжай ежедневную фиксацию состояния.")

    return MenstrualCycleInsightsResponse(
        from_date=from_date_obj.isoformat(),
        to_date=to_date_obj.isoformat(),
        tracked_days=len(entries),
        average_cycle_day=average_cycle_day,
        period_intensity_distribution=intensity_distribution,
        ovulation_days=ovulation_days,
        fertile_window_days=fertile_window_days,
        top_symptoms=top_symptoms,
        recommendations=recommendations,
    )


@router.delete("/cycle/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menstrual_cycle_entry(
    entry_id: int,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Удалить запись трекинга цикла."""
    db_entry = db.query(MenstrualCycle).filter(
        MenstrualCycle.id == entry_id,
        MenstrualCycle.user_id == current_user.id
    ).first()
    
    if not db_entry:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    
    db.delete(db_entry)
    db.commit()
    return None
