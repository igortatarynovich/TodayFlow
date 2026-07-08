"""Tracking API endpoints — контур влияния TodayFlow.

Включает:
- Прогресс-трекер: записи по аскезам и аффирмациям (два отдельных сервиса).
  Трекер аскез (/asceticisms/tracker) и трекер аффирмаций (/affirmations/tracker)
  используют общий API /tracking/progress, но не смешивают выбор в одной форме.
- Трекер привычек — отдельный сервис (/habits), не этот API.
- Дневник наблюдений
- Ритуал закрытия дня
- Автоматические инсайты
- Недельная интеграция
"""

from collections import defaultdict
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_

from todayflow_backend.api.auth import require_user
from todayflow_backend.services.push_delivery import notify_goal_saved
from todayflow_backend.db.session import get_session
from todayflow_backend.db.models import (
    User,
    ProgressTrackerEntry,
    ObservationDiaryEntry,
    DayConnection,
    DayRitual,
    AutoInsight,
    WeeklyIntegration,
    WeeklyGoal,
    WeeklyGoalStep,
    StateCheckIn,
    HabitEntry,
    Habit,
    PracticeUsage,
    MenstrualCycle,
    AsceticContract,
)
from todayflow_backend.core.content_loader import get_lexicon_phrase
from todayflow_backend.core.tracking_generators import InsightGeneratorDB, WeeklyAnalyzerDB
from todayflow_backend.core.reflection_generator_db import ReflectionGeneratorDB

router = APIRouter(prefix="/tracking", tags=["tracking"])


# ============================================================================
# Прогресс-трекер
# ============================================================================

class ProgressTrackerEntryCreate(BaseModel):
    """Создание записи в прогресс-трекере."""
    date: str  # YYYY-MM-DD
    asceticism_id: Optional[str] = None
    affirmation_id: Optional[str] = None
    completed: bool
    state: Optional[str] = None  # 1-2 слова: "calm", "tension", etc.
    state_scale: Optional[int] = None  # 1-5
    note: Optional[str] = None


class ProgressTrackerEntryResponse(BaseModel):
    """Ответ с записью трекера."""
    id: int
    date: str
    asceticism_id: Optional[str]
    affirmation_id: Optional[str]
    completed: bool
    state: Optional[str]
    state_scale: Optional[int]
    note: Optional[str]
    created_at: datetime
    updated_at: datetime


class AsceticContractCreate(BaseModel):
    """Создание контракта аскезы."""
    title: str
    asceticism_id: Optional[str] = None
    intention: Optional[str] = None
    start_date: str  # YYYY-MM-DD
    end_date: Optional[str] = None  # YYYY-MM-DD


class AsceticContractCheckin(BaseModel):
    """Чекины по контракту аскезы."""
    date: str  # YYYY-MM-DD
    completed: bool = True
    state_scale: Optional[int] = None  # 1-5
    note: Optional[str] = None


class AsceticContractResponse(BaseModel):
    id: int
    asceticism_id: Optional[str]
    title: str
    intention: Optional[str]
    start_date: str
    end_date: Optional[str]
    status: str
    streak_days: int
    longest_streak_days: int
    last_completed_date: Optional[str]
    created_at: datetime
    updated_at: datetime


class FusionIndexResponse(BaseModel):
    """Дневной интегральный индекс состояния."""
    date: str
    scores: dict  # energy, emotional_balance, focus (0-100)
    cycle_context: dict
    activity_context: dict
    rhythm_context: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str]
    encouragement: str


def _parse_iso_date(value: str) -> date:
    return datetime.strptime(value, '%Y-%m-%d').date()


@router.post("/progress", response_model=ProgressTrackerEntryResponse, status_code=status.HTTP_201_CREATED)
def create_progress_entry(
    entry: ProgressTrackerEntryCreate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Создать запись в прогресс-трекере."""
    entry_date = datetime.strptime(entry.date, '%Y-%m-%d').date()
    
    # Проверяем, нет ли уже записи на эту дату
    existing = db.query(ProgressTrackerEntry).filter(
        ProgressTrackerEntry.user_id == current_user.id,
        ProgressTrackerEntry.date == entry_date,
        ProgressTrackerEntry.asceticism_id == entry.asceticism_id,
        ProgressTrackerEntry.affirmation_id == entry.affirmation_id
    ).first()
    
    if existing:
        # Обновляем существующую запись
        existing.completed = entry.completed
        existing.state = entry.state
        existing.state_scale = entry.state_scale
        existing.note = entry.note
        existing.updated_at = datetime.now()
        db.commit()
        db.refresh(existing)
        return ProgressTrackerEntryResponse(
            id=existing.id,
            date=existing.date.isoformat(),
            asceticism_id=existing.asceticism_id,
            affirmation_id=existing.affirmation_id,
            completed=existing.completed,
            state=existing.state,
            state_scale=existing.state_scale,
            note=existing.note,
            created_at=existing.created_at,
            updated_at=existing.updated_at
        )
    
    # Создаём новую запись
    db_entry = ProgressTrackerEntry(
        user_id=current_user.id,
        date=entry_date,
        asceticism_id=entry.asceticism_id,
        affirmation_id=entry.affirmation_id,
        completed=entry.completed,
        state=entry.state,
        state_scale=entry.state_scale,
        note=entry.note
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    return ProgressTrackerEntryResponse(
        id=db_entry.id,
        date=db_entry.date.isoformat(),
        asceticism_id=db_entry.asceticism_id,
        affirmation_id=db_entry.affirmation_id,
        completed=db_entry.completed,
        state=db_entry.state,
        state_scale=db_entry.state_scale,
        note=db_entry.note,
        created_at=db_entry.created_at,
        updated_at=db_entry.updated_at
    )


@router.get("/progress", response_model=List[ProgressTrackerEntryResponse])
def get_progress_entries(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Получить записи прогресс-трекера за период."""
    query = db.query(ProgressTrackerEntry).filter(
        ProgressTrackerEntry.user_id == current_user.id
    )
    
    if from_date:
        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
        query = query.filter(ProgressTrackerEntry.date >= from_date_obj)
    
    if to_date:
        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
        query = query.filter(ProgressTrackerEntry.date <= to_date_obj)
    
    entries = query.order_by(ProgressTrackerEntry.date.desc()).all()
    
    return [
        ProgressTrackerEntryResponse(
            id=e.id,
            date=e.date.isoformat(),
            asceticism_id=e.asceticism_id,
            affirmation_id=e.affirmation_id,
            completed=e.completed,
            state=e.state,
            state_scale=e.state_scale,
            note=e.note,
            created_at=e.created_at,
            updated_at=e.updated_at
        )
        for e in entries
    ]


@router.post("/ascetic-contracts", response_model=AsceticContractResponse, status_code=status.HTTP_201_CREATED)
def create_ascetic_contract(
    payload: AsceticContractCreate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Зафиксировать контракт аскезы."""
    start_date = _parse_iso_date(payload.start_date)
    end_date = _parse_iso_date(payload.end_date) if payload.end_date else None
    contract = AsceticContract(
        user_id=current_user.id,
        asceticism_id=payload.asceticism_id,
        title=payload.title.strip(),
        intention=payload.intention,
        start_date=start_date,
        end_date=end_date,
        status="active",
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return AsceticContractResponse(
        id=contract.id,
        asceticism_id=contract.asceticism_id,
        title=contract.title,
        intention=contract.intention,
        start_date=contract.start_date.isoformat(),
        end_date=contract.end_date.isoformat() if contract.end_date else None,
        status=contract.status,
        streak_days=contract.streak_days,
        longest_streak_days=contract.longest_streak_days,
        last_completed_date=contract.last_completed_date.isoformat() if contract.last_completed_date else None,
        created_at=contract.created_at,
        updated_at=contract.updated_at,
    )


@router.get("/ascetic-contracts", response_model=List[AsceticContractResponse])
def get_ascetic_contracts(
    status_filter: Optional[str] = None,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Список контрактов аскезы пользователя."""
    query = db.query(AsceticContract).filter(AsceticContract.user_id == current_user.id)
    if status_filter:
        query = query.filter(AsceticContract.status == status_filter)
    contracts = query.order_by(AsceticContract.created_at.desc()).all()
    return [
        AsceticContractResponse(
            id=contract.id,
            asceticism_id=contract.asceticism_id,
            title=contract.title,
            intention=contract.intention,
            start_date=contract.start_date.isoformat(),
            end_date=contract.end_date.isoformat() if contract.end_date else None,
            status=contract.status,
            streak_days=contract.streak_days,
            longest_streak_days=contract.longest_streak_days,
            last_completed_date=contract.last_completed_date.isoformat() if contract.last_completed_date else None,
            created_at=contract.created_at,
            updated_at=contract.updated_at,
        )
        for contract in contracts
    ]


@router.post("/ascetic-contracts/{contract_id}/checkin", response_model=AsceticContractResponse)
def checkin_ascetic_contract(
    contract_id: int,
    payload: AsceticContractCheckin,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Отметить выполнение дня по контракту аскезы."""
    contract = db.query(AsceticContract).filter(
        AsceticContract.id == contract_id,
        AsceticContract.user_id == current_user.id,
    ).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Ascetic contract not found")

    target_date = _parse_iso_date(payload.date)
    ascetic_id = contract.asceticism_id or f"contract:{contract.id}"
    existing_progress = db.query(ProgressTrackerEntry).filter(
        ProgressTrackerEntry.user_id == current_user.id,
        ProgressTrackerEntry.date == target_date,
        ProgressTrackerEntry.asceticism_id == ascetic_id,
        ProgressTrackerEntry.affirmation_id == None,  # noqa: E711
    ).first()
    if existing_progress:
        existing_progress.completed = payload.completed
        existing_progress.state_scale = payload.state_scale
        existing_progress.note = payload.note
        existing_progress.updated_at = datetime.utcnow()
    else:
        db.add(
            ProgressTrackerEntry(
                user_id=current_user.id,
                date=target_date,
                asceticism_id=ascetic_id,
                completed=payload.completed,
                state_scale=payload.state_scale,
                note=payload.note,
            )
        )

    if payload.completed:
        if contract.last_completed_date and (target_date - contract.last_completed_date).days == 1:
            contract.streak_days += 1
        elif contract.last_completed_date == target_date:
            pass
        else:
            contract.streak_days = 1
        contract.last_completed_date = target_date
        contract.longest_streak_days = max(contract.longest_streak_days, contract.streak_days)
        if contract.end_date and target_date >= contract.end_date:
            contract.status = "completed"

    contract.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(contract)
    return AsceticContractResponse(
        id=contract.id,
        asceticism_id=contract.asceticism_id,
        title=contract.title,
        intention=contract.intention,
        start_date=contract.start_date.isoformat(),
        end_date=contract.end_date.isoformat() if contract.end_date else None,
        status=contract.status,
        streak_days=contract.streak_days,
        longest_streak_days=contract.longest_streak_days,
        last_completed_date=contract.last_completed_date.isoformat() if contract.last_completed_date else None,
        created_at=contract.created_at,
        updated_at=contract.updated_at,
    )


@router.get("/fusion/{target_date}", response_model=FusionIndexResponse)
def get_daily_fusion_index(
    target_date: str,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """Интегральный индекс дня: энергия, эмоциональная устойчивость, фокус."""
    day = _parse_iso_date(target_date)
    progress_entries = db.query(ProgressTrackerEntry).filter(
        ProgressTrackerEntry.user_id == current_user.id,
        ProgressTrackerEntry.date == day,
    ).all()
    diary_entry = db.query(ObservationDiaryEntry).filter(
        ObservationDiaryEntry.user_id == current_user.id,
        ObservationDiaryEntry.date == day,
    ).first()
    ritual_entry = db.query(DayRitual).filter(
        DayRitual.user_id == current_user.id,
        DayRitual.date == day,
    ).first()
    cycle_entry = db.query(MenstrualCycle).filter(
        MenstrualCycle.user_id == current_user.id,
        MenstrualCycle.date == day,
    ).first()
    practice_count = db.query(PracticeUsage).filter(
        PracticeUsage.user_id == current_user.id,
        func.date(PracticeUsage.completed_at) == day,
    ).count()
    day_connection = db.query(DayConnection).filter(
        DayConnection.user_id == current_user.id,
        DayConnection.date == day,
    ).first()

    mood_values = [entry.state_scale for entry in progress_entries if entry.state_scale]
    mood_avg = round(sum(mood_values) / len(mood_values), 2) if mood_values else None

    ascetic_completed = any(entry.completed and entry.asceticism_id for entry in progress_entries)
    affirmation_completed = any(entry.completed and entry.affirmation_id for entry in progress_entries)
    ritual_completed = bool(ritual_entry and ritual_entry.completed)
    diary_done = diary_entry is not None

    energy = 50
    energy += min(practice_count, 3) * 8
    if ritual_completed:
        energy += 6
    if cycle_entry and cycle_entry.period_intensity:
        if cycle_entry.period_intensity == "heavy":
            energy -= 18
        elif cycle_entry.period_intensity == "medium":
            energy -= 10
        elif cycle_entry.period_intensity == "light":
            energy -= 4
    if cycle_entry and cycle_entry.ovulation:
        energy += 8
    if cycle_entry and cycle_entry.fertile_window:
        energy += 4

    emotional_balance = 50
    if mood_avg is not None:
        emotional_balance += int((mood_avg - 3) * 12)
    if diary_done:
        emotional_balance += 6
    if cycle_entry and cycle_entry.period_intensity == "heavy":
        emotional_balance -= 6
    if day_connection:
        if day_connection.ritual_feedback == "yes":
            emotional_balance += 4
        elif day_connection.ritual_feedback == "partial":
            emotional_balance += 2
        elif day_connection.ritual_feedback == "no":
            emotional_balance -= 4
        if day_connection.question_of_day_answer:
            emotional_balance += 3

    focus = 50
    if ritual_completed:
        focus += 10
    if ascetic_completed:
        focus += 10
    if affirmation_completed:
        focus += 6
    if mood_avg is not None and mood_avg <= 2:
        focus -= 10
    if day_connection:
        if day_connection.ritual_feedback == "yes":
            focus += 4
        elif day_connection.ritual_feedback == "partial":
            focus += 2
        elif day_connection.ritual_feedback == "no":
            focus -= 2
        if day_connection.quick_decision_answer == "yes":
            focus += 4
        elif day_connection.quick_decision_answer == "unclear":
            focus -= 3
        if day_connection.question_of_day_answer:
            focus += 2

    def clamp(value: int) -> int:
        return max(0, min(100, value))

    scores = {
        "energy": clamp(energy),
        "emotional_balance": clamp(emotional_balance),
        "focus": clamp(focus),
    }

    recommendations: List[str] = []
    if scores["energy"] < 40:
        recommendations.append("Снизь нагрузку и выбери короткую восстановительную практику.")
    if not ritual_completed:
        recommendations.append("Закрой день ритуалом: это повысит фокус на завтра.")
    if not diary_done:
        recommendations.append("Добавь короткую запись в дневник, чтобы стабилизировать эмоциональный фон.")
    if not ascetic_completed:
        recommendations.append("Сделай минимальный шаг по аскезе сегодня, чтобы не потерять серию.")
    if not day_connection or not day_connection.question_of_day_answer:
        recommendations.append("Ответь на вопрос дня: это помогает точнее настраивать завтрашний фокус.")
    if scores["focus"] >= 70:
        recommendations.append("Окно высокого фокуса: поставь 1 приоритетную задачу на 45 минут.")
    if not recommendations:
        recommendations.append("Ритм стабильный. Сохрани текущий темп и отметь результат в трекере.")

    avg_score = round((scores["energy"] + scores["emotional_balance"] + scores["focus"]) / 3, 1)
    if avg_score < 40:
        encouragement = "Сегодня важнее бережный режим. Маленькие шаги уже считаются прогрессом."
    elif avg_score < 70:
        encouragement = "Ровный день. Держи базовую дисциплину и не перегружайся."
    else:
        encouragement = "Сильный день. Используй импульс на ключевую задачу и практику."

    rhythm_context = _build_rhythm_context(db, current_user.id, day)

    return FusionIndexResponse(
        date=day.isoformat(),
        scores=scores,
        cycle_context={
            "tracked": cycle_entry is not None,
            "cycle_day": cycle_entry.cycle_day if cycle_entry else None,
            "period_intensity": cycle_entry.period_intensity if cycle_entry else None,
            "ovulation": cycle_entry.ovulation if cycle_entry else False,
            "fertile_window": cycle_entry.fertile_window if cycle_entry else False,
        },
        activity_context={
            "practice_count": practice_count,
            "mood_avg": mood_avg,
            "ritual_completed": ritual_completed,
            "diary_done": diary_done,
            "ascetic_completed": ascetic_completed,
            "affirmation_completed": affirmation_completed,
            "signals_completed": int(bool(day_connection and day_connection.ritual_feedback))
            + int(bool(day_connection and day_connection.quick_decision_answer))
            + int(bool(day_connection and day_connection.question_of_day_answer)),
            "ritual_feedback": day_connection.ritual_feedback if day_connection else None,
            "quick_decision_answer": day_connection.quick_decision_answer if day_connection else None,
            "question_of_day_answer": day_connection.question_of_day_answer if day_connection else None,
        },
        rhythm_context=rhythm_context,
        recommendations=recommendations,
        encouragement=encouragement,
    )


# ============================================================================
# Дневник наблюдений
# ============================================================================

class ObservationDiaryEntryCreate(BaseModel):
    """Создание записи в дневнике наблюдений."""
    date: str  # YYYY-MM-DD
    noticed: str  # "Что я заметил" (1-2 предложения)
    hardest: str  # "Где было сложнее всего" (1-2 предложения)
    easier_than_expected: str  # "Что оказалось легче, чем ожидал" (1-2 предложения)


class ObservationDiaryEntryResponse(BaseModel):
    """Ответ с записью дневника."""
    id: int
    date: str
    noticed: str
    hardest: str
    easier_than_expected: str
    created_at: datetime
    updated_at: datetime


@router.post("/diary", response_model=ObservationDiaryEntryResponse, status_code=status.HTTP_201_CREATED)
def create_diary_entry(
    entry: ObservationDiaryEntryCreate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Создать запись в дневнике наблюдений."""
    entry_date = datetime.strptime(entry.date, '%Y-%m-%d').date()
    
    # Проверяем, нет ли уже записи на эту дату
    existing = db.query(ObservationDiaryEntry).filter(
        ObservationDiaryEntry.user_id == current_user.id,
        ObservationDiaryEntry.date == entry_date
    ).first()
    
    if existing:
        # Обновляем существующую запись
        existing.noticed = entry.noticed
        existing.hardest = entry.hardest
        existing.easier_than_expected = entry.easier_than_expected
        existing.updated_at = datetime.now()
        db.commit()
        db.refresh(existing)
        return ObservationDiaryEntryResponse(
            id=existing.id,
            date=existing.date.isoformat(),
            noticed=existing.noticed,
            hardest=existing.hardest,
            easier_than_expected=existing.easier_than_expected,
            created_at=existing.created_at,
            updated_at=existing.updated_at
        )
    
    # Создаём новую запись
    db_entry = ObservationDiaryEntry(
        user_id=current_user.id,
        date=entry_date,
        noticed=entry.noticed,
        hardest=entry.hardest,
        easier_than_expected=entry.easier_than_expected
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    return ObservationDiaryEntryResponse(
        id=db_entry.id,
        date=db_entry.date.isoformat(),
        noticed=db_entry.noticed,
        hardest=db_entry.hardest,
        easier_than_expected=db_entry.easier_than_expected,
        created_at=db_entry.created_at,
        updated_at=db_entry.updated_at
    )


@router.get("/diary", response_model=List[ObservationDiaryEntryResponse])
def get_diary_entries(
    date: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Получить записи дневника за период."""
    query = db.query(ObservationDiaryEntry).filter(
        ObservationDiaryEntry.user_id == current_user.id
    )
    
    # Если указана конкретная дата, используем её
    if date:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        query = query.filter(ObservationDiaryEntry.date == date_obj)
    else:
        # Иначе используем диапазон дат
        if from_date:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
            query = query.filter(ObservationDiaryEntry.date >= from_date_obj)
        
        if to_date:
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
            query = query.filter(ObservationDiaryEntry.date <= to_date_obj)
    
    entries = query.order_by(ObservationDiaryEntry.date.desc()).all()
    
    return [
        ObservationDiaryEntryResponse(
            id=e.id,
            date=e.date.isoformat(),
            noticed=e.noticed,
            hardest=e.hardest,
            easier_than_expected=e.easier_than_expected,
            created_at=e.created_at,
            updated_at=e.updated_at
        )
        for e in entries
    ]


# ============================================================================
# Ритуал закрытия дня
# ============================================================================

class DayRitualCreate(BaseModel):
    """Создание записи ритуала закрытия дня."""
    date: str  # YYYY-MM-DD
    completed: bool
    closing_phrase_id: Optional[str] = None  # ID фразы из Lexicon
    custom_closing_phrase: Optional[str] = None  # Своя завершающая фраза
    sufficiency_confirmed: bool
    # Расширение для кастомизации
    ritual_type: Optional[str] = "template"  # "custom" | "template" | "combined"
    custom_elements: Optional[List[dict]] = None  # [{type: "gratitude", content: "..."}, ...]
    day_connection_id: Optional[int] = None  # Связь с day connection
    observations: Optional[dict] = None  # {noticed: "...", hardest: "...", easier: "..."}


class DayRitualResponse(BaseModel):
    """Ответ с записью ритуала."""
    id: int
    date: str
    completed: bool
    closing_phrase_id: Optional[str]
    closing_phrase_text: Optional[str]  # Текст фразы из Lexicon
    custom_closing_phrase: Optional[str]  # Своя завершающая фраза
    sufficiency_confirmed: bool
    ritual_type: Optional[str]
    custom_elements: Optional[List[dict]]
    day_connection_id: Optional[int]
    observations: Optional[dict]
    created_at: datetime
    updated_at: datetime


@router.post("/ritual", response_model=DayRitualResponse, status_code=status.HTTP_201_CREATED)
def create_day_ritual(
    ritual: DayRitualCreate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Создать запись ритуала закрытия дня."""
    entry_date = datetime.strptime(ritual.date, '%Y-%m-%d').date()
    
    # Загружаем текст фразы из Lexicon
    closing_phrase_text = None
    if ritual.closing_phrase_id:
        phrase = get_lexicon_phrase(ritual.closing_phrase_id)
        if phrase:
            closing_phrase_text = phrase.get('text')
    
    # Проверяем, нет ли уже записи на эту дату
    existing = db.query(DayRitual).filter(
        DayRitual.user_id == current_user.id,
        DayRitual.date == entry_date
    ).first()
    
    if existing:
        # Обновляем существующую запись
        existing.completed = ritual.completed
        existing.closing_phrase_id = ritual.closing_phrase_id
        existing.closing_phrase_text = closing_phrase_text
        existing.sufficiency_confirmed = ritual.sufficiency_confirmed
        if ritual.ritual_type:
            existing.ritual_type = ritual.ritual_type
        if ritual.custom_elements is not None:
            existing.custom_elements = ritual.custom_elements
        if ritual.custom_closing_phrase is not None:
            existing.custom_closing_phrase = ritual.custom_closing_phrase
        if ritual.day_connection_id:
            existing.day_connection_id = ritual.day_connection_id
        if ritual.observations is not None:
            # Сохраняем наблюдения в DayRitual
            existing.observations = ritual.observations
            # Также сохраняем в day_connection если есть связь
            if ritual.day_connection_id:
                from todayflow_backend.db.models import DayConnection
                day_conn = db.query(DayConnection).filter(
                    DayConnection.id == ritual.day_connection_id,
                    DayConnection.user_id == current_user.id
                ).first()
                if day_conn:
                    day_conn.evening_observations = ritual.observations
                    day_conn.evening_completed = ritual.completed
        existing.updated_at = datetime.now()
        db.commit()
        db.refresh(existing)
        return DayRitualResponse(
            id=existing.id,
            date=existing.date.isoformat(),
            completed=existing.completed,
            closing_phrase_id=existing.closing_phrase_id,
            closing_phrase_text=existing.closing_phrase_text,
            custom_closing_phrase=existing.custom_closing_phrase if hasattr(existing, 'custom_closing_phrase') else None,
            sufficiency_confirmed=existing.sufficiency_confirmed,
            ritual_type=existing.ritual_type,
            custom_elements=existing.custom_elements,
            day_connection_id=existing.day_connection_id,
            observations=ritual.observations,
            created_at=existing.created_at,
            updated_at=existing.updated_at
        )
    
    # Создаём новую запись
    db_entry = DayRitual(
        user_id=current_user.id,
        date=entry_date,
        completed=ritual.completed,
        closing_phrase_id=ritual.closing_phrase_id,
        closing_phrase_text=closing_phrase_text,
        sufficiency_confirmed=ritual.sufficiency_confirmed,
        ritual_type=ritual.ritual_type or "template",
        custom_elements=ritual.custom_elements,
        custom_closing_phrase=ritual.custom_closing_phrase,
        day_connection_id=ritual.day_connection_id,
        observations=ritual.observations,
    )
    db.add(db_entry)
    
    # Если есть наблюдения и day_connection_id, обновляем day_connection
    # Сохраняем наблюдения в day_connection если есть связь
    if ritual.observations and ritual.day_connection_id:
        from todayflow_backend.db.models import DayConnection
        day_conn = db.query(DayConnection).filter(
            DayConnection.id == ritual.day_connection_id,
            DayConnection.user_id == current_user.id
        ).first()
        if day_conn:
            day_conn.evening_observations = ritual.observations
            day_conn.evening_completed = ritual.completed
    
    db.commit()
    db.refresh(db_entry)
    
    return DayRitualResponse(
        id=db_entry.id,
        date=db_entry.date.isoformat(),
        completed=db_entry.completed,
        closing_phrase_id=db_entry.closing_phrase_id,
        closing_phrase_text=db_entry.closing_phrase_text,
        custom_closing_phrase=ritual.custom_closing_phrase,
        sufficiency_confirmed=db_entry.sufficiency_confirmed,
        ritual_type=db_entry.ritual_type,
        custom_elements=db_entry.custom_elements,
        day_connection_id=db_entry.day_connection_id,
        observations=ritual.observations,
        created_at=db_entry.created_at,
        updated_at=db_entry.updated_at
    )


@router.get("/ritual/{date}", response_model=Optional[DayRitualResponse])
def get_day_ritual(
    date: str,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Получить ритуал закрытия дня по дате."""
    entry_date = datetime.strptime(date, '%Y-%m-%d').date()
    
    ritual = db.query(DayRitual).filter(
        DayRitual.user_id == current_user.id,
        DayRitual.date == entry_date
    ).first()
    
    if not ritual:
        return None
    
    # Получаем observations из DayRitual, если нет - из DayConnection
    observations = ritual.observations if hasattr(ritual, 'observations') else None
    if not observations and ritual.day_connection_id:
        from todayflow_backend.db.models import DayConnection
        day_conn = db.query(DayConnection).filter(
            DayConnection.id == ritual.day_connection_id
        ).first()
        if day_conn:
            observations = day_conn.evening_observations
    
    return DayRitualResponse(
        id=ritual.id,
        date=ritual.date.isoformat(),
        completed=ritual.completed,
        closing_phrase_id=ritual.closing_phrase_id,
        closing_phrase_text=ritual.closing_phrase_text,
        custom_closing_phrase=ritual.custom_closing_phrase if hasattr(ritual, 'custom_closing_phrase') else None,
        sufficiency_confirmed=ritual.sufficiency_confirmed,
        ritual_type=ritual.ritual_type,
        custom_elements=ritual.custom_elements,
        day_connection_id=ritual.day_connection_id,
        observations=observations,
        created_at=ritual.created_at,
        updated_at=ritual.updated_at
    )


# ============================================================================
# Автоматические инсайты
# ============================================================================

class AutoInsightResponse(BaseModel):
    """Ответ с автоматическим инсайтом."""
    id: str
    date: str
    type: str  # "streak", "pattern", "shift", "correlation", "weekend_pattern"
    insight_text: str
    data_points: dict
    confidence: Optional[str] = "medium"  # "low", "medium", "high"
    created_at: datetime


@router.get("/insights", response_model=List[AutoInsightResponse])
def get_auto_insights(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    date: Optional[str] = None,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Получить автоматические инсайты за период. Поддержка date= для фильтра по одному дню."""
    if date and not from_date and not to_date:
        from_date = date
        to_date = date
    query = db.query(AutoInsight).filter(
        AutoInsight.user_id == current_user.id
    )
    
    if from_date:
        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
        query = query.filter(AutoInsight.date >= from_date_obj)
    
    if to_date:
        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
        query = query.filter(AutoInsight.date <= to_date_obj)
    
    insights = query.order_by(AutoInsight.date.desc()).all()
    
    return [
        AutoInsightResponse(
            id=insight.id,
            date=insight.date.isoformat(),
            type=insight.type,
            insight_text=insight.insight_text,
            data_points=insight.data_points,
            confidence=insight.data_points.get('confidence', 'medium') if isinstance(insight.data_points, dict) else 'medium',
            created_at=insight.created_at
        )
        for insight in insights
    ]


class InsightGenerateRequest(BaseModel):
    """Запрос на генерацию инсайта."""
    date: str  # YYYY-MM-DD


@router.post("/insights/generate", response_model=AutoInsightResponse)
def generate_insight(
    request: InsightGenerateRequest,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Сгенерировать инсайт для пользователя на дату."""
    generator = InsightGeneratorDB(db)
    try:
        insight_data = generator.generate_insight(current_user.id, request.date)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при генерации инсайта: {str(e)}"
        )
    
    if not insight_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недостаточно данных для генерации инсайта. Заполните прогресс-трекер и дневник наблюдений."
        )
    
    # Сохраняем инсайт в БД
    confidence = insight_data.get('confidence', 'medium')
    insight = AutoInsight(
        id=insight_data['id'],
        user_id=current_user.id,
        date=datetime.strptime(request.date, '%Y-%m-%d').date(),
        type=insight_data['type'],
        insight_text=insight_data['insight_text'],
        data_points={**insight_data['data_points'], 'confidence': confidence}  # Сохраняем confidence в data_points
    )
    db.add(insight)
    db.commit()
    db.refresh(insight)
    
    # Извлекаем confidence из data_points (если есть) или используем medium по умолчанию
    confidence = insight.data_points.get('confidence', 'medium') if isinstance(insight.data_points, dict) else 'medium'
    
    return AutoInsightResponse(
        id=insight.id,
        date=insight.date.isoformat(),
        type=insight.type,
        insight_text=insight.insight_text,
        data_points=insight.data_points,
        confidence=confidence,
        created_at=insight.created_at
    )


# ============================================================================
# Недельная интеграция
# ============================================================================

class WeeklyIntegrationResponse(BaseModel):
    """Ответ с недельной интеграцией."""
    week_start: str
    week_end: str
    integration_text: str
    data_points: dict
    created_at: datetime


class WeeklyGoalCreate(BaseModel):
    week_start: str  # YYYY-MM-DD: для scope=week — любой день недели (нормализуем к пн); для month — любой день месяца (якорь = 1-е число)
    title: str
    scope: str = "week"  # week | month


class WeeklyGoalUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None


class WeeklyGoalResponse(BaseModel):
    id: int
    week_start: str
    title: str
    completed: bool
    progress_days: int
    last_progress_date: Optional[str]
    scope: str
    period_end: Optional[str]
    created_at: datetime
    updated_at: datetime


class WeeklyGoalStepRequest(BaseModel):
    date: Optional[str] = None  # YYYY-MM-DD, optional


def _monday_of_week(d: date) -> date:
    return d - timedelta(days=d.weekday())


def _truncate_rhythm_text(value: str | None, max_len: int) -> str:
    s = (value or "").strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 1].rstrip() + "…"


def _build_rhythm_context(db: Session, user_id: int, day: date) -> Dict[str, Any]:
    """Компактный слой «ритма» для narrative/fusion: цели, привычки, аскезы, дневник."""
    ws = _monday_of_week(day)
    ms = day.replace(day=1)

    goals_out: List[Dict[str, Any]] = []
    seen_goal_ids: set[int] = set()

    week_goals = (
        db.query(WeeklyGoal)
        .filter(
            WeeklyGoal.user_id == user_id,
            WeeklyGoal.completed.is_(False),
            WeeklyGoal.week_start == ws,
            or_(WeeklyGoal.scope == "week", WeeklyGoal.scope.is_(None)),
        )
        .order_by(WeeklyGoal.created_at.asc())
        .limit(8)
        .all()
    )
    for g in week_goals:
        if g.id not in seen_goal_ids:
            seen_goal_ids.add(g.id)
            goals_out.append(
                {
                    "title": _truncate_rhythm_text(g.title, 160),
                    "scope": "week",
                    "completed": bool(g.completed),
                }
            )

    month_goals = (
        db.query(WeeklyGoal)
        .filter(
            WeeklyGoal.user_id == user_id,
            WeeklyGoal.completed.is_(False),
            WeeklyGoal.week_start == ms,
            WeeklyGoal.scope == "month",
        )
        .order_by(WeeklyGoal.created_at.asc())
        .limit(8)
        .all()
    )
    for g in month_goals:
        if g.id not in seen_goal_ids:
            seen_goal_ids.add(g.id)
            goals_out.append(
                {
                    "title": _truncate_rhythm_text(g.title, 160),
                    "scope": "month",
                    "completed": bool(g.completed),
                }
            )

    habits = (
        db.query(Habit)
        .filter(Habit.user_id == user_id, Habit.is_active == True)  # noqa: E712
        .order_by(Habit.created_at.desc())
        .limit(15)
        .all()
    )
    habit_ids = [h.id for h in habits]
    entries_by_habit: Dict[int, bool] = {}
    if habit_ids:
        for he in (
            db.query(HabitEntry)
            .filter(
                HabitEntry.user_id == user_id,
                HabitEntry.date == day,
                HabitEntry.habit_id.in_(habit_ids),
            )
            .all()
        ):
            entries_by_habit[he.habit_id] = bool(he.completed)

    habits_out = [
        {
            "name": _truncate_rhythm_text(h.name, 120),
            "category": _truncate_rhythm_text(h.category, 80) if h.category else None,
            "frequency": (h.target_frequency or "daily").lower(),
            "completed_today": entries_by_habit.get(h.id, False),
        }
        for h in habits
    ]

    contracts = (
        db.query(AsceticContract)
        .filter(
            AsceticContract.user_id == user_id,
            AsceticContract.status == "active",
            AsceticContract.start_date <= day,
            or_(AsceticContract.end_date.is_(None), AsceticContract.end_date >= day),
        )
        .order_by(AsceticContract.created_at.desc())
        .limit(12)
        .all()
    )
    ascetics_out: List[Dict[str, Any]] = []
    for c in contracts:
        aid = c.asceticism_id
        done_today = False
        if aid:
            row = (
                db.query(ProgressTrackerEntry)
                .filter(
                    ProgressTrackerEntry.user_id == user_id,
                    ProgressTrackerEntry.date == day,
                    ProgressTrackerEntry.asceticism_id == aid,
                    ProgressTrackerEntry.completed.is_(True),
                )
                .first()
            )
            done_today = row is not None
        ascetics_out.append(
            {
                "title": _truncate_rhythm_text(c.title, 120),
                "streak_days": int(c.streak_days or 0),
                "completed_today": done_today,
            }
        )

    diary_start = day - timedelta(days=6)
    diary_count = (
        db.query(ObservationDiaryEntry)
        .filter(
            ObservationDiaryEntry.user_id == user_id,
            ObservationDiaryEntry.date >= diary_start,
            ObservationDiaryEntry.date <= day,
        )
        .count()
    )
    has_today = (
        db.query(ObservationDiaryEntry)
        .filter(ObservationDiaryEntry.user_id == user_id, ObservationDiaryEntry.date == day)
        .first()
        is not None
    )

    return {
        "goals": goals_out,
        "habits": habits_out,
        "ascetics": ascetics_out,
        "diary": {
            "has_entry_today": has_today,
            "entries_last_7_days": int(diary_count),
        },
    }


def _last_day_of_month(d: date) -> date:
    if d.month == 12:
        next_month = d.replace(year=d.year + 1, month=1, day=1)
    else:
        next_month = d.replace(month=d.month + 1, day=1)
    return next_month - timedelta(days=1)


def _goal_progress_target(scope: str) -> int:
    return 12 if (scope or "").lower() == "month" else 5


def _weekly_goal_to_response(goal: WeeklyGoal) -> WeeklyGoalResponse:
    return WeeklyGoalResponse(
        id=goal.id,
        week_start=goal.week_start.isoformat(),
        title=goal.title,
        completed=goal.completed,
        progress_days=goal.progress_days,
        last_progress_date=goal.last_progress_date.isoformat() if goal.last_progress_date else None,
        scope=(goal.scope or "week").lower(),
        period_end=goal.period_end.isoformat() if goal.period_end else None,
        created_at=goal.created_at,
        updated_at=goal.updated_at,
    )


def _record_goal_step(db: Session, *, goal: WeeklyGoal, user: User, step_date: date) -> WeeklyGoal:
    """Сохранить шаг по цели за день (идемпотентно). Возвращает обновлённую цель."""
    gscope = (goal.scope or "week").lower()
    if gscope == "month":
        if step_date.replace(day=1) != goal.week_start:
            raise HTTPException(status_code=400, detail="Step date must be inside goal month")
        if goal.period_end and step_date > goal.period_end:
            raise HTTPException(status_code=400, detail="Step date after goal period end")
    else:
        if _monday_of_week(step_date) != goal.week_start:
            raise HTTPException(status_code=400, detail="Step date must be inside goal week")

    existing_step = (
        db.query(WeeklyGoalStep)
        .filter(
            WeeklyGoalStep.weekly_goal_id == goal.id,
            WeeklyGoalStep.step_date == step_date,
        )
        .first()
    )
    if existing_step:
        return goal

    db.add(
        WeeklyGoalStep(
            weekly_goal_id=goal.id,
            user_id=user.id,
            step_date=step_date,
        )
    )
    goal.progress_days = (goal.progress_days or 0) + 1
    goal.last_progress_date = step_date
    target = _goal_progress_target(gscope)
    if goal.progress_days >= target:
        goal.completed = True
    goal.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(goal)
    return goal


def _pick_calendar_goal(db: Session, user_id: int, on_date: date) -> Optional[WeeklyGoal]:
    """Приоритет: недельная невыполненная цель на эту неделю, иначе месячная на этот месяц."""
    ws = _monday_of_week(on_date)
    g = (
        db.query(WeeklyGoal)
        .filter(
            WeeklyGoal.user_id == user_id,
            WeeklyGoal.completed.is_(False),
            WeeklyGoal.week_start == ws,
            or_(WeeklyGoal.scope == "week", WeeklyGoal.scope.is_(None)),
        )
        .order_by(WeeklyGoal.progress_days.desc(), WeeklyGoal.created_at.asc())
        .first()
    )
    if g:
        return g
    ms = on_date.replace(day=1)
    return (
        db.query(WeeklyGoal)
        .filter(
            WeeklyGoal.user_id == user_id,
            WeeklyGoal.completed.is_(False),
            WeeklyGoal.week_start == ms,
            WeeklyGoal.scope == "month",
        )
        .order_by(WeeklyGoal.progress_days.desc(), WeeklyGoal.created_at.asc())
        .first()
    )


@router.get("/weekly/{week_start}", response_model=Optional[WeeklyIntegrationResponse])
def get_weekly_integration(
    week_start: str,
    week_end: Optional[str] = None,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Получить недельную интеграцию."""
    if not week_end:
        # Вычисляем week_end как week_start + 6 дней
        week_start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
        week_end_date = week_start_date + timedelta(days=6)
        week_end = week_end_date.isoformat()
    
    integration = db.query(WeeklyIntegration).filter(
        WeeklyIntegration.user_id == current_user.id,
        WeeklyIntegration.week_start == datetime.strptime(week_start, '%Y-%m-%d').date(),
        WeeklyIntegration.week_end == datetime.strptime(week_end, '%Y-%m-%d').date()
    ).first()
    
    if not integration:
        return None
    
    return WeeklyIntegrationResponse(
        week_start=integration.week_start.isoformat(),
        week_end=integration.week_end.isoformat(),
        integration_text=integration.integration_text,
        data_points=integration.data_points,
        created_at=integration.created_at
    )


@router.get("/weekly-goals", response_model=List[WeeklyGoalResponse])
def get_weekly_goals(
    week_start: Optional[str] = None,
    scope: Optional[str] = None,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """Получить цели трекинга (неделя / месяц)."""
    query = db.query(WeeklyGoal).filter(WeeklyGoal.user_id == current_user.id)
    if week_start:
        query = query.filter(WeeklyGoal.week_start == datetime.strptime(week_start, "%Y-%m-%d").date())
    if scope:
        sc = scope.lower()
        if sc == "week":
            query = query.filter(or_(WeeklyGoal.scope == "week", WeeklyGoal.scope.is_(None)))
        elif sc == "month":
            query = query.filter(WeeklyGoal.scope == "month")
    goals = query.order_by(WeeklyGoal.created_at.asc()).all()
    return [_weekly_goal_to_response(g) for g in goals]


@router.post("/weekly-goals", response_model=WeeklyGoalResponse, status_code=status.HTTP_201_CREATED)
def create_weekly_goal(
    payload: WeeklyGoalCreate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """Создать цель трекинга (неделя или месяц)."""
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Goal title is required")

    scope = (payload.scope or "week").lower()
    if scope not in ("week", "month"):
        raise HTTPException(status_code=400, detail="scope must be week or month")

    anchor = datetime.strptime(payload.week_start, "%Y-%m-%d").date()
    if scope == "week":
        week_start_date = _monday_of_week(anchor)
        period_end_date = week_start_date + timedelta(days=6)
    else:
        week_start_date = anchor.replace(day=1)
        period_end_date = _last_day_of_month(week_start_date)

    scope_filter = (
        or_(WeeklyGoal.scope == "week", WeeklyGoal.scope.is_(None))
        if scope == "week"
        else WeeklyGoal.scope == "month"
    )
    existing_count = (
        db.query(WeeklyGoal)
        .filter(
            WeeklyGoal.user_id == current_user.id,
            WeeklyGoal.week_start == week_start_date,
            scope_filter,
        )
        .count()
    )
    if existing_count >= 3:
        raise HTTPException(status_code=400, detail="Goal limit reached for this period (max 3)")

    duplicate = db.query(WeeklyGoal).filter(
        WeeklyGoal.user_id == current_user.id,
        WeeklyGoal.week_start == week_start_date,
        scope_filter,
        WeeklyGoal.title == title,
    ).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="Goal already exists for this period")

    goal = WeeklyGoal(
        user_id=current_user.id,
        week_start=week_start_date,
        title=title,
        completed=False,
        progress_days=0,
        last_progress_date=None,
        scope=scope,
        period_end=period_end_date,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    notify_goal_saved(db, current_user, goal_preview=goal.title)
    return _weekly_goal_to_response(goal)


@router.put("/weekly-goals/{goal_id}", response_model=WeeklyGoalResponse)
def update_weekly_goal(
    goal_id: int,
    payload: WeeklyGoalUpdate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """Обновить цель недели (title/completed)."""
    goal = db.query(WeeklyGoal).filter(
        WeeklyGoal.id == goal_id,
        WeeklyGoal.user_id == current_user.id,
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Weekly goal not found")

    if payload.title is not None:
        title = payload.title.strip()
        if not title:
            raise HTTPException(status_code=400, detail="Goal title is required")
        goal.title = title
    if payload.completed is not None:
        goal.completed = payload.completed

    goal.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(goal)
    return _weekly_goal_to_response(goal)


@router.delete("/weekly-goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_weekly_goal(
    goal_id: int,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """Удалить цель недели."""
    goal = db.query(WeeklyGoal).filter(
        WeeklyGoal.id == goal_id,
        WeeklyGoal.user_id == current_user.id,
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Weekly goal not found")
    db.delete(goal)
    db.commit()
    return None


@router.post("/weekly-goals/{goal_id}/step", response_model=WeeklyGoalResponse)
def step_weekly_goal(
    goal_id: int,
    payload: WeeklyGoalStepRequest,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """Отметить шаг по цели за день (идемпотентно: один шаг на цель на дату)."""
    goal = db.query(WeeklyGoal).filter(
        WeeklyGoal.id == goal_id,
        WeeklyGoal.user_id == current_user.id,
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Weekly goal not found")

    step_date = datetime.strptime(payload.date, "%Y-%m-%d").date() if payload.date else datetime.utcnow().date()
    goal = _record_goal_step(db, goal=goal, user=current_user, step_date=step_date)
    return _weekly_goal_to_response(goal)


class WeeklyGenerateRequest(BaseModel):
    """Запрос на генерацию недельной интеграции."""
    week_start: str  # YYYY-MM-DD


@router.post("/weekly/generate", response_model=WeeklyIntegrationResponse)
def generate_weekly_integration(
    request: WeeklyGenerateRequest,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Сгенерировать недельную интеграцию."""
    week_start_date = datetime.strptime(request.week_start, '%Y-%m-%d').date()
    # Вычисляем week_end (неделя = 7 дней)
    week_end_date = datetime.fromordinal(week_start_date.toordinal() + 6).date()
    week_end_str = week_end_date.isoformat()
    
    analyzer = WeeklyAnalyzerDB(db)
    try:
        integration_data = analyzer.analyze_week(current_user.id, request.week_start, week_end_str)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при генерации недельной интеграции: {str(e)}"
        )
    
    if not integration_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недостаточно данных для генерации недельной интеграции. Заполните прогресс-трекер и дневник наблюдений за эту неделю."
        )
    
    # Проверяем, нет ли уже интеграции для этой недели
    existing = db.query(WeeklyIntegration).filter(
        WeeklyIntegration.user_id == current_user.id,
        WeeklyIntegration.week_start == week_start_date,
        WeeklyIntegration.week_end == week_end_date
    ).first()
    
    if existing:
        # Обновляем существующую
        existing.integration_text = integration_data['integration_text']
        existing.data_points = integration_data['data_points']
        db.commit()
        db.refresh(existing)
        return WeeklyIntegrationResponse(
            week_start=existing.week_start.isoformat(),
            week_end=existing.week_end.isoformat(),
            integration_text=existing.integration_text,
            data_points=existing.data_points,
            created_at=existing.created_at
        )
    
    # Создаём новую интеграцию
    integration = WeeklyIntegration(
        user_id=current_user.id,
        week_start=week_start_date,
        week_end=week_end_date,
        integration_text=integration_data['integration_text'],
        data_points=integration_data['data_points']
    )
    db.add(integration)
    db.commit()
    db.refresh(integration)
    
    return WeeklyIntegrationResponse(
        week_start=integration.week_start.isoformat(),
        week_end=integration.week_end.isoformat(),
        integration_text=integration.integration_text,
        data_points=integration.data_points,
        created_at=integration.created_at
    )


# ============================================================================
# Генерация отражений
# ============================================================================

class DailyReflectionResponse(BaseModel):
    """Ответ с дневным отражением."""
    date: str
    forecast_type: str
    layers: List[str]
    theme: dict
    recommended_practice: dict
    insight: Optional[dict]
    diary_note: Optional[dict]


@router.get("/reflection/daily/{date}", response_model=Optional[DailyReflectionResponse])
def get_daily_reflection(
    date: str,
    forecast_type: str,
    layers: List[str],
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Получить дневное отражение."""
    generator = ReflectionGeneratorDB(db)
    reflection = generator.generate_daily_reflection(
        user_id=current_user.id,
        target_date=date,
        forecast_type=forecast_type,
        layers=layers
    )
    
    if not reflection:
        return None
    
    return DailyReflectionResponse(
        date=reflection['date'],
        forecast_type=reflection['forecast_type'],
        layers=reflection['layers'],
        theme=reflection['theme'],
        recommended_practice=reflection['recommended_practice'],
        insight=reflection.get('insight'),
        diary_note=reflection.get('diary_note')
    )


@router.get("/reflection/weekly/{week_start}", response_model=Optional[dict])
def get_weekly_reflection(
    week_start: str,
    week_end: str,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Получить недельное отражение."""
    generator = ReflectionGeneratorDB(db)
    reflection = generator.generate_weekly_reflection(
        user_id=current_user.id,
        week_start=week_start,
        week_end=week_end
    )
    
    return reflection


# ============================================================================
# Единый календарный трекер
# ============================================================================

class CalendarActivityLog(BaseModel):
    """Быстрое логирование активности в календаре."""
    date: str  # YYYY-MM-DD
    activity_type: str  # "practice" | "affirmation" | "asceticism" | "diary" | "ritual" | "numerology_check"
    activity_id: Optional[str] = None  # ID активности (для practice, affirmation, asceticism)
    completed: bool = True
    state_scale: Optional[int] = None  # 1-5 для настроения
    note: Optional[str] = None  # Короткая заметка


class CalendarDayResponse(BaseModel):
    """Данные одного дня для календаря."""
    date: str
    activities: dict  # {activity_type: {completed: bool, state_scale: int?, note: str?}}
    mood: Optional[int] = None  # 1-5, если есть
    streak: dict = {}  # {activity_type: int} - текущий стрик по типу


class CalendarAsceticEntryLite(BaseModel):
    date: str
    completed: bool


class CalendarGoalTrack(BaseModel):
    id: int
    title: str
    scope: str
    completed: bool
    week_start: str
    step_dates: List[str] = Field(default_factory=list)


class CalendarHabitTrack(BaseModel):
    id: int
    name: str
    target_frequency: str = "daily"
    target_per_period: int = 1
    is_active: bool = True
    completed_dates: List[str] = Field(default_factory=list)


class CalendarAsceticTrack(BaseModel):
    asceticism_id: str
    title: Optional[str] = None
    contract_status: Optional[str] = None  # active | completed | paused
    entries: List[CalendarAsceticEntryLite] = Field(default_factory=list)


class CalendarResponse(BaseModel):
    """Ответ с данными календаря за период."""
    days: List[CalendarDayResponse]
    streaks: dict  # {activity_type: int} - текущие стрики по типам
    stats: dict  # {activity_type: {total: int, completed: int, percentage: float}}
    month_summary: Optional[dict] = None  # агрегаты за запрошенный интервал (карта месяца)
    goal_tracks: List[CalendarGoalTrack] = Field(default_factory=list)
    habit_tracks: List[CalendarHabitTrack] = Field(default_factory=list)
    ascetic_tracks: List[CalendarAsceticTrack] = Field(default_factory=list)


@router.post("/calendar/log", response_model=dict, status_code=status.HTTP_201_CREATED)
def quick_log_activity(
    log: CalendarActivityLog,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Быстрое логирование активности (1-2 тапа)."""
    entry_date = datetime.strptime(log.date, '%Y-%m-%d').date()
    
    if log.activity_type == "practice":
        # Логируем через PracticeUsage
        from todayflow_backend.db.models import PracticeUsage
        # Вычисляем начало недели (понедельник)
        days_since_monday = entry_date.weekday()  # 0 = Monday, 6 = Sunday
        week_start = entry_date - timedelta(days=days_since_monday)
        
        usage = PracticeUsage(
            user_id=current_user.id,
            practice_id=log.activity_id or "",
            completed_at=datetime.combine(entry_date, datetime.min.time()),
            week_start=week_start,
            is_personalized=False
        )
        db.add(usage)
        db.commit()
        return {"status": "logged", "type": "practice"}
    
    elif log.activity_type in ["asceticism", "affirmation"]:
        # Логируем через ProgressTrackerEntry
        existing = db.query(ProgressTrackerEntry).filter(
            ProgressTrackerEntry.user_id == current_user.id,
            ProgressTrackerEntry.date == entry_date,
            ProgressTrackerEntry.asceticism_id == (log.activity_id if log.activity_type == "asceticism" else None),
            ProgressTrackerEntry.affirmation_id == (log.activity_id if log.activity_type == "affirmation" else None)
        ).first()
        
        if existing:
            existing.completed = log.completed
            existing.state_scale = log.state_scale
            existing.note = log.note
            existing.updated_at = datetime.now()
        else:
            entry = ProgressTrackerEntry(
                user_id=current_user.id,
                date=entry_date,
                asceticism_id=log.activity_id if log.activity_type == "asceticism" else None,
                affirmation_id=log.activity_id if log.activity_type == "affirmation" else None,
                completed=log.completed,
                state_scale=log.state_scale,
                note=log.note
            )
            db.add(entry)
        db.commit()
        return {"status": "logged", "type": log.activity_type}
    
    elif log.activity_type == "ritual":
        # Логируем через DayRitual
        existing = db.query(DayRitual).filter(
            DayRitual.user_id == current_user.id,
            DayRitual.date == entry_date
        ).first()
        
        if existing:
            existing.completed = log.completed
            existing.updated_at = datetime.now()
        else:
            ritual = DayRitual(
                user_id=current_user.id,
                date=entry_date,
                completed=log.completed,
                sufficiency_confirmed=log.completed
            )
            db.add(ritual)
        db.commit()
        return {"status": "logged", "type": "ritual"}
    
    elif log.activity_type == "diary":
        # Для дневника нужны поля noticed, hardest, easier_than_expected
        # Быстрое логирование - просто отмечаем что дневник заполнен
        existing = db.query(ObservationDiaryEntry).filter(
            ObservationDiaryEntry.user_id == current_user.id,
            ObservationDiaryEntry.date == entry_date
        ).first()
        
        if existing:
            return {"status": "exists", "type": "diary"}
        else:
            # Создаём минимальную запись
            diary = ObservationDiaryEntry(
                user_id=current_user.id,
                date=entry_date,
                noticed=log.note or "Заметил",
                hardest="",
                easier_than_expected=""
            )
            db.add(diary)
            db.commit()
            return {"status": "logged", "type": "diary"}

    elif log.activity_type == "goal":
        if not log.completed:
            return {"status": "noop", "type": "goal", "message": "Снятие отметки цели из календаря пока не поддерживается"}
        picked = _pick_calendar_goal(db, current_user.id, entry_date)
        if not picked:
            raise HTTPException(
                status_code=400,
                detail="Нет активной цели на эту неделю или месяц — создай цель в календаре или в разделе недели",
            )
        _record_goal_step(db, goal=picked, user=current_user, step_date=entry_date)
        return {"status": "logged", "type": "goal", "goal_id": picked.id}

    return {"status": "unknown_type", "type": log.activity_type}


class StateCheckInBody(BaseModel):
    phase: str
    mood_scale: Optional[int] = None
    energy_scale: Optional[int] = None
    stress_scale: Optional[int] = None
    note: Optional[str] = None
    tags: Optional[List[str]] = None


class StateCheckInResponse(BaseModel):
    id: int
    checkin_date: str
    phase: str
    mood_scale: Optional[int]
    energy_scale: Optional[int]
    stress_scale: Optional[int]
    note: Optional[str]
    tags: Optional[Any]
    updated_at: datetime


class DayOutlookPhaseDetail(BaseModel):
    """Одна фаза дня для карты состояния (всегда три слота: утро, день, вечер)."""

    phase: str
    empty: bool = True
    mood_scale: Optional[int] = None
    energy_scale: Optional[int] = None
    stress_scale: Optional[int] = None
    has_note: bool = False


class DayOutlookResponse(BaseModel):
    date: str
    paragraphs: List[str]
    phases: dict
    signals: dict
    phase_details: List[DayOutlookPhaseDetail] = Field(default_factory=list)


@router.get("/state-check-in/{target_date}", response_model=List[StateCheckInResponse])
def list_state_check_ins(
    target_date: str,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    d0 = datetime.strptime(target_date, "%Y-%m-%d").date()
    rows = (
        db.query(StateCheckIn)
        .filter(StateCheckIn.user_id == current_user.id, StateCheckIn.checkin_date == d0)
        .order_by(StateCheckIn.phase.asc())
        .all()
    )
    return [
        StateCheckInResponse(
            id=r.id,
            checkin_date=r.checkin_date.isoformat(),
            phase=r.phase,
            mood_scale=r.mood_scale,
            energy_scale=r.energy_scale,
            stress_scale=r.stress_scale,
            note=r.note,
            tags=r.tags,
            updated_at=r.updated_at,
        )
        for r in rows
    ]


@router.post("/state-check-in/{target_date}", response_model=StateCheckInResponse)
def upsert_state_check_in(
    target_date: str,
    body: StateCheckInBody,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    phase = (body.phase or "").lower().strip()
    if phase not in ("morning", "day", "evening"):
        raise HTTPException(status_code=400, detail="phase must be morning, day or evening")
    if body.mood_scale is not None and not (1 <= body.mood_scale <= 5):
        raise HTTPException(status_code=400, detail="mood_scale must be 1-5")
    if body.energy_scale is not None and not (1 <= body.energy_scale <= 5):
        raise HTTPException(status_code=400, detail="energy_scale must be 1-5")
    if body.stress_scale is not None and not (1 <= body.stress_scale <= 5):
        raise HTTPException(status_code=400, detail="stress_scale must be 1-5")

    d0 = datetime.strptime(target_date, "%Y-%m-%d").date()
    tags_payload: Optional[Any] = body.tags if body.tags is not None else None

    row = (
        db.query(StateCheckIn)
        .filter(
            StateCheckIn.user_id == current_user.id,
            StateCheckIn.checkin_date == d0,
            StateCheckIn.phase == phase,
        )
        .first()
    )
    if row:
        row.mood_scale = body.mood_scale
        row.energy_scale = body.energy_scale
        row.stress_scale = body.stress_scale
        row.note = body.note
        row.tags = tags_payload
        row.updated_at = datetime.utcnow()
    else:
        row = StateCheckIn(
            user_id=current_user.id,
            checkin_date=d0,
            phase=phase,
            mood_scale=body.mood_scale,
            energy_scale=body.energy_scale,
            stress_scale=body.stress_scale,
            note=body.note,
            tags=tags_payload,
        )
        db.add(row)
    db.commit()
    db.refresh(row)
    return StateCheckInResponse(
        id=row.id,
        checkin_date=row.checkin_date.isoformat(),
        phase=row.phase,
        mood_scale=row.mood_scale,
        energy_scale=row.energy_scale,
        stress_scale=row.stress_scale,
        note=row.note,
        tags=row.tags,
        updated_at=row.updated_at,
    )


@router.get("/day-outlook/{target_date}", response_model=DayOutlookResponse)
def get_day_outlook(
    target_date: str,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """Краткий итог дня по чек-инам и связке дня (без LLM)."""
    d0 = datetime.strptime(target_date, "%Y-%m-%d").date()
    checkins = (
        db.query(StateCheckIn)
        .filter(StateCheckIn.user_id == current_user.id, StateCheckIn.checkin_date == d0)
        .all()
    )
    by_phase = {c.phase: c for c in checkins}
    phases = {
        "morning": "morning" in by_phase,
        "day": "day" in by_phase,
        "evening": "evening" in by_phase,
    }
    filled = sum(1 for v in phases.values() if v)

    dc = (
        db.query(DayConnection)
        .filter(DayConnection.user_id == current_user.id, DayConnection.date == d0)
        .first()
    )
    goal_steps_today = (
        db.query(WeeklyGoalStep)
        .filter(WeeklyGoalStep.user_id == current_user.id, WeeklyGoalStep.step_date == d0)
        .count()
    )
    habit_done = (
        db.query(HabitEntry)
        .filter(
            HabitEntry.user_id == current_user.id,
            HabitEntry.date == d0,
            HabitEntry.completed.is_(True),
        )
        .count()
    )

    paragraphs: List[str] = []
    if filled == 0:
        paragraphs.append("Сегодня ещё нет чек-инов состояния (утро / день / вечер). Три короткие отметки помогут потом увидеть динамику дня.")
    else:
        paragraphs.append(f"Зафиксировано чек-инов состояния: {filled} из 3 (утро, день, вечер).")
        for label, key in (("Утро", "morning"), ("День", "day"), ("Вечер", "evening")):
            c = by_phase.get(key)
            if not c:
                continue
            bits = []
            if c.mood_scale is not None:
                bits.append(f"настроение {c.mood_scale}/5")
            if c.energy_scale is not None:
                bits.append(f"энергия {c.energy_scale}/5")
            if c.stress_scale is not None:
                bits.append(f"стресс {c.stress_scale}/5")
            if c.note:
                bits.append(f"заметка: {c.note[:120]}{'…' if c.note and len(c.note) > 120 else ''}")
            paragraphs.append(f"{label}: " + (", ".join(bits) if bits else "отметка без шкал."))

    if dc and (dc.morning_intention or "").strip():
        paragraphs.append(f"Намерение дня: «{(dc.morning_intention or '').strip()[:200]}»")

    if goal_steps_today:
        paragraphs.append(f"По целям в трекинге сегодня отмечен шаг ({goal_steps_today} отметок).")
    if habit_done:
        paragraphs.append(f"Привычки: {habit_done} отметок «сделано» за день.")

    signals = {
        "day_connection": bool(dc),
        "morning_intention": bool(dc and (dc.morning_intention or "").strip()),
        "goal_steps": goal_steps_today,
        "habits_done": habit_done,
    }

    phase_details: List[DayOutlookPhaseDetail] = []
    for key in ("morning", "day", "evening"):
        c = by_phase.get(key)
        if c:
            phase_details.append(
                DayOutlookPhaseDetail(
                    phase=key,
                    empty=False,
                    mood_scale=c.mood_scale,
                    energy_scale=c.energy_scale,
                    stress_scale=c.stress_scale,
                    has_note=bool((c.note or "").strip()),
                )
            )
        else:
            phase_details.append(DayOutlookPhaseDetail(phase=key, empty=True))

    return DayOutlookResponse(
        date=d0.isoformat(),
        paragraphs=paragraphs,
        phases=phases,
        signals=signals,
        phase_details=phase_details,
    )


@router.get("/calendar", response_model=CalendarResponse)
def get_calendar_data(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session)
):
    """Получить данные календаря за период для единого трекера."""
    from datetime import timedelta
    
    # Определяем период (по умолчанию текущий месяц)
    today = date.today()
    if not from_date:
        from_date_obj = today.replace(day=1)
    else:
        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
    
    if not to_date:
        # Последний день текущего месяца
        if today.month == 12:
            to_date_obj = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            to_date_obj = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    else:
        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
    
    # Собираем все активности за период
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
    days_dict: dict = {}
    current_date = from_date_obj
    while current_date <= to_date_obj:
        days_dict[current_date.isoformat()] = {
            "date": current_date.isoformat(),
            "activities": {},
            "mood": None,
            "streak": {}
        }
        current_date += timedelta(days=1)
    
    # Заполняем данные
    for entry in progress_entries:
        day_key = entry.date.isoformat()
        if entry.asceticism_id:
            days_dict[day_key]["activities"]["asceticism"] = {
                "completed": entry.completed,
                "state_scale": entry.state_scale,
                "note": entry.note
            }
            if entry.state_scale:
                days_dict[day_key]["mood"] = entry.state_scale
        if entry.affirmation_id:
            days_dict[day_key]["activities"]["affirmation"] = {
                "completed": entry.completed,
                "state_scale": entry.state_scale,
                "note": entry.note
            }
            if entry.state_scale and not days_dict[day_key]["mood"]:
                days_dict[day_key]["mood"] = entry.state_scale
    
    for entry in diary_entries:
        day_key = entry.date.isoformat()
        days_dict[day_key]["activities"]["diary"] = {
            "completed": True,
            "note": entry.noticed
        }
    
    for entry in ritual_entries:
        day_key = entry.date.isoformat()
        days_dict[day_key]["activities"]["ritual"] = {
            "completed": entry.completed
        }
    
    for usage in practice_usages:
        day_key = usage.completed_at.date().isoformat()
        if day_key in days_dict:
            if "practice" not in days_dict[day_key]["activities"]:
                days_dict[day_key]["activities"]["practice"] = {"completed": True, "count": 0}
            days_dict[day_key]["activities"]["practice"]["count"] = days_dict[day_key]["activities"]["practice"].get("count", 0) + 1

    for entry in day_connections:
        day_key = entry.date.isoformat()
        signals_count = int(bool(entry.ritual_feedback)) + int(bool(entry.quick_decision_answer)) + int(bool(entry.question_of_day_answer))
        if signals_count == 0:
            continue
        days_dict[day_key]["activities"]["daily_signals"] = {
            "completed": True,
            "signals_count": signals_count,
            "ritual_feedback": entry.ritual_feedback,
            "quick_decision_answer": entry.quick_decision_answer,
            "question_of_day_answer": entry.question_of_day_answer,
        }

    goal_steps = (
        db.query(WeeklyGoalStep)
        .options(joinedload(WeeklyGoalStep.weekly_goal))
        .filter(
            WeeklyGoalStep.user_id == current_user.id,
            WeeklyGoalStep.step_date >= from_date_obj,
            WeeklyGoalStep.step_date <= to_date_obj,
        )
        .all()
    )
    for s in goal_steps:
        day_key = s.step_date.isoformat()
        if day_key not in days_dict:
            continue
        wg = s.weekly_goal
        title = (wg.title if wg else "") or ""
        cur = days_dict[day_key]["activities"].get("goal")
        if not cur:
            days_dict[day_key]["activities"]["goal"] = {
                "completed": True,
                "count": 1,
                "titles": [title] if title else [],
            }
        else:
            cur["count"] = int(cur.get("count") or 0) + 1
            cur["completed"] = True
            if title and title not in (cur.get("titles") or []):
                cur.setdefault("titles", []).append(title)

    habit_rows = (
        db.query(HabitEntry, Habit.name)
        .join(Habit, HabitEntry.habit_id == Habit.id)
        .filter(
            HabitEntry.user_id == current_user.id,
            HabitEntry.date >= from_date_obj,
            HabitEntry.date <= to_date_obj,
            HabitEntry.completed.is_(True),
        )
        .all()
    )
    for he, hname in habit_rows:
        day_key = he.date.isoformat()
        if day_key not in days_dict:
            continue
        cur = days_dict[day_key]["activities"].get("habits")
        if not cur:
            days_dict[day_key]["activities"]["habits"] = {
                "completed": True,
                "count": 1,
                "names": [hname],
            }
        else:
            cur["count"] = int(cur.get("count") or 0) + 1
            cur["completed"] = True
            if hname not in (cur.get("names") or []):
                cur.setdefault("names", []).append(hname)

    state_rows = (
        db.query(StateCheckIn)
        .filter(
            StateCheckIn.user_id == current_user.id,
            StateCheckIn.checkin_date >= from_date_obj,
            StateCheckIn.checkin_date <= to_date_obj,
        )
        .all()
    )
    by_day_state: dict[str, List[StateCheckIn]] = {}
    for r in state_rows:
        by_day_state.setdefault(r.checkin_date.isoformat(), []).append(r)
    for day_key, rows in by_day_state.items():
        if day_key not in days_dict:
            continue
        has_m = any(x.phase == "morning" for x in rows)
        has_d = any(x.phase == "day" for x in rows)
        has_e = any(x.phase == "evening" for x in rows)
        filled = int(has_m) + int(has_d) + int(has_e)
        days_dict[day_key]["activities"]["state_phases"] = {
            "completed": filled >= 1,
            "filled": filled,
            "of": 3,
            "morning": has_m,
            "day": has_d,
            "evening": has_e,
            "full_day": filled >= 3,
        }

    # Вычисляем стрики
    streaks = {}
    activity_types = [
        "practice",
        "affirmation",
        "asceticism",
        "diary",
        "ritual",
        "daily_signals",
        "goal",
        "habits",
        "state_phases",
    ]
    
    for activity_type in activity_types:
        streak = 0
        check_date = today
        while check_date >= from_date_obj:
            day_key = check_date.isoformat()
            if day_key in days_dict:
                activity = days_dict[day_key]["activities"].get(activity_type)
                if activity and activity.get("completed"):
                    streak += 1
                else:
                    break
            else:
                break
            check_date -= timedelta(days=1)
        streaks[activity_type] = streak
    
    # Вычисляем статистику
    stats = {}
    for activity_type in activity_types:
        total_days = len([d for d in days_dict.values()])
        completed_days = len([d for d in days_dict.values() if d["activities"].get(activity_type, {}).get("completed")])
        stats[activity_type] = {
            "total": total_days,
            "completed": completed_days,
            "percentage": round((completed_days / total_days * 100) if total_days > 0 else 0, 1)
        }

    total_days_ct = len(days_dict)
    full_state_days = sum(
        1
        for d in days_dict.values()
        if (d["activities"].get("state_phases") or {}).get("full_day")
    )
    goal_days = stats.get("goal", {}).get("completed", 0)
    habit_days = stats.get("habits", {}).get("completed", 0)
    month_summary = {
        "from": from_date_obj.isoformat(),
        "to": to_date_obj.isoformat(),
        "total_days": total_days_ct,
        "days_full_state_checkins": full_state_days,
        "days_with_goal_step": goal_days,
        "days_with_habits": habit_days,
    }

    # --- Треки по отдельным сущностям (цели / привычки / аскезы) ---
    step_dates_by_goal: dict[int, list[str]] = defaultdict(list)
    for s in goal_steps:
        step_dates_by_goal[s.weekly_goal_id].append(s.step_date.isoformat())

    active_goal_rows = (
        db.query(WeeklyGoal)
        .filter(WeeklyGoal.user_id == current_user.id, WeeklyGoal.completed.is_(False))
        .all()
    )
    goal_id_union = set(step_dates_by_goal.keys()) | {g.id for g in active_goal_rows}
    goal_tracks_out: list[CalendarGoalTrack] = []
    for gid in sorted(goal_id_union):
        wg = next((g for g in active_goal_rows if g.id == gid), None)
        if wg is None:
            wg = db.get(WeeklyGoal, gid)
        if not wg or wg.user_id != current_user.id:
            continue
        dates = sorted(set(step_dates_by_goal.get(gid, [])))
        goal_tracks_out.append(
            CalendarGoalTrack(
                id=wg.id,
                title=wg.title,
                scope=wg.scope or "week",
                completed=wg.completed,
                week_start=wg.week_start.isoformat(),
                step_dates=dates,
            )
        )
    goal_tracks_out.sort(key=lambda t: (t.completed, t.title.lower()))

    habits_active = (
        db.query(Habit)
        .filter(Habit.user_id == current_user.id, Habit.is_active.is_(True))
        .all()
    )
    habit_entries_in_range = (
        db.query(HabitEntry)
        .filter(
            HabitEntry.user_id == current_user.id,
            HabitEntry.date >= from_date_obj,
            HabitEntry.date <= to_date_obj,
            HabitEntry.completed.is_(True),
        )
        .all()
    )
    completed_dates_by_habit: dict[int, list[str]] = defaultdict(list)
    for he in habit_entries_in_range:
        completed_dates_by_habit[he.habit_id].append(he.date.isoformat())

    habit_seen = {h.id for h in habits_active}
    habit_tracks_out: list[CalendarHabitTrack] = []
    for h in habits_active:
        habit_tracks_out.append(
            CalendarHabitTrack(
                id=h.id,
                name=h.name,
                target_frequency=h.target_frequency or "daily",
                target_per_period=h.target_per_period or 1,
                is_active=h.is_active,
                completed_dates=sorted(set(completed_dates_by_habit.get(h.id, []))),
            )
        )
    for hid, cdates in completed_dates_by_habit.items():
        if hid in habit_seen:
            continue
        h = db.get(Habit, hid)
        if not h or h.user_id != current_user.id:
            continue
        habit_tracks_out.append(
            CalendarHabitTrack(
                id=h.id,
                name=h.name,
                target_frequency=h.target_frequency or "daily",
                target_per_period=h.target_per_period or 1,
                is_active=h.is_active,
                completed_dates=sorted(set(cdates)),
            )
        )
    habit_tracks_out.sort(key=lambda t: (not t.is_active, t.name.lower()))

    by_asc: dict[str, list[CalendarAsceticEntryLite]] = defaultdict(list)
    for entry in progress_entries:
        if not entry.asceticism_id:
            continue
        if entry.date < from_date_obj or entry.date > to_date_obj:
            continue
        by_asc[entry.asceticism_id].append(
            CalendarAsceticEntryLite(date=entry.date.isoformat(), completed=entry.completed)
        )

    asc_contracts = (
        db.query(AsceticContract)
        .filter(AsceticContract.user_id == current_user.id)
        .all()
    )
    active_contracts = [c for c in asc_contracts if (c.status or "") == "active" and c.asceticism_id]
    for c in active_contracts:
        if c.asceticism_id not in by_asc:
            by_asc[c.asceticism_id] = []

    ascetic_tracks_out: list[CalendarAsceticTrack] = []
    for aid, ents in by_asc.items():
        ents.sort(key=lambda x: x.date)
        title = next((c.title for c in asc_contracts if c.asceticism_id == aid), None)
        cstat = next((c.status for c in asc_contracts if c.asceticism_id == aid), None)
        ascetic_tracks_out.append(
            CalendarAsceticTrack(
                asceticism_id=aid,
                title=title,
                contract_status=cstat,
                entries=ents,
            )
        )
    ascetic_tracks_out.sort(key=lambda t: (t.title or t.asceticism_id or "").lower())

    return CalendarResponse(
        days=[CalendarDayResponse(**day_data) for day_data in days_dict.values()],
        streaks=streaks,
        stats=stats,
        month_summary=month_summary,
        goal_tracks=goal_tracks_out,
        habit_tracks=habit_tracks_out,
        ascetic_tracks=ascetic_tracks_out,
    )
