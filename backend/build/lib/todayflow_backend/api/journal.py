"""Journal API endpoints."""

import csv
import io
from datetime import datetime, date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from pydantic import BaseModel
import re
from collections import Counter

from todayflow_backend.db.session import get_session
from todayflow_backend.db.models import JournalEntry, User
from todayflow_backend.api.auth import require_user, get_optional_user

router = APIRouter(prefix="/journal", tags=["journal"])


class JournalEntryCreate(BaseModel):
    type: str  # 'observation', 'gratitude', 'insight'
    content: str
    practice_id: Optional[str] = None  # Контекст: после практики
    tarot_card_id: Optional[str] = None  # Контекст: после таро
    pattern_axis_id: Optional[str] = None  # Контекст: активный паттерн
    day: Optional[str] = None  # Контекст: дата дня (ISO format)


class JournalEntryResponse(BaseModel):
    id: int
    type: str
    content: str
    practice_id: Optional[str] = None
    tarot_card_id: Optional[str] = None
    pattern_axis_id: Optional[str] = None
    day: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/entries", response_model=List[JournalEntryResponse])
def get_journal_entries(
    entry_type: Optional[str] = None,
    limit: Optional[int] = None,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """Get journal entries for the current user."""
    query = db.query(JournalEntry).filter(JournalEntry.user_id == current_user.id)
    
    if entry_type:
        if entry_type not in ["observation", "gratitude", "insight"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid entry type. Must be 'observation', 'gratitude', or 'insight'"
            )
        query = query.filter(JournalEntry.type == entry_type)
    
    query = query.order_by(JournalEntry.created_at.desc())
    
    if limit:
        query = query.limit(limit)
    
    entries = query.all()
    return entries


@router.post("/entries", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
def create_journal_entry(
    entry: JournalEntryCreate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """Create a new journal entry."""
    if entry.type not in ["observation", "gratitude", "insight"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid entry type. Must be 'observation', 'gratitude', or 'insight'"
        )
    
    if not entry.content or not entry.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content cannot be empty"
        )
    
    # Ограничение длины (500 символов)
    content = entry.content.strip()
    if len(content) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content must be 500 characters or less"
        )
    
    # Парсим day если передан
    entry_day = None
    if entry.day:
        try:
            entry_day = datetime.strptime(entry.day, "%Y-%m-%d").date()
        except ValueError:
            pass
    
    db_entry = JournalEntry(
        user_id=current_user.id,
        type=entry.type,
        content=content,
        practice_id=entry.practice_id,
        tarot_card_id=entry.tarot_card_id,
        pattern_axis_id=entry.pattern_axis_id,
        day=entry_day,
    )
    
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    return db_entry


@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_journal_entry(
    entry_id: int,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """Delete a journal entry."""
    entry = db.query(JournalEntry).filter(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == current_user.id
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found"
        )
    
    db.delete(entry)
    db.commit()
    
    return None


class JournalAnalyticsResponse(BaseModel):
    total_entries: int
    observation_count: int
    gratitude_count: int
    insight_count: int
    entries_by_type: dict
    activity_by_month: List[dict]  # [{month: str, observation: int, gratitude: int, insight: int}]
    activity_by_week: List[dict]  # [{week: str, observation: int, gratitude: int, insight: int}]
    recent_activity_days: int  # Количество дней с записями за последние 30 дней
    most_common_words: List[dict]  # [{word: str, count: int}]
    most_common_patterns: List[dict]  # [{pattern_axis_id: str, count: int}]
    most_common_contexts: List[dict]  # [{context_type: str, count: int}]
    avg_entries_per_week: float


@router.get("/analytics", response_model=JournalAnalyticsResponse)
def get_journal_analytics(
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """
    Получить аналитику по журналам пользователя.
    """
    # Все записи пользователя
    all_entries = db.query(JournalEntry).filter(
        JournalEntry.user_id == current_user.id
    ).order_by(JournalEntry.created_at.asc()).all()
    
    total_entries = len(all_entries)
    observation_count = sum(1 for e in all_entries if e.type == "observation")
    gratitude_count = sum(1 for e in all_entries if e.type == "gratitude")
    insight_count = sum(1 for e in all_entries if e.type == "insight")
    
    entries_by_type = {
        "observation": observation_count,
        "gratitude": gratitude_count,
        "insight": insight_count,
    }
    
    # Активность по месяцам (последние 12 месяцев)
    activity_by_month = []
    now = datetime.utcnow()
    for i in range(11, -1, -1):
        month_date = now - timedelta(days=30 * i)
        month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i == 0:
            month_end = now
        else:
            next_month = (month_start.month % 12) + 1
            year = month_start.year + (1 if next_month == 1 else 0)
            month_end = month_start.replace(month=next_month, year=year)
        
        month_entries = [
            e for e in all_entries
            if month_start <= e.created_at < month_end
        ]
        
        activity_by_month.append({
            "month": month_start.strftime("%Y-%m"),
            "observation": sum(1 for e in month_entries if e.type == "observation"),
            "gratitude": sum(1 for e in month_entries if e.type == "gratitude"),
            "insight": sum(1 for e in month_entries if e.type == "insight"),
        })
    
    # Активность по неделям (последние 8 недель)
    activity_by_week = []
    for i in range(7, -1, -1):
        week_start = (now - timedelta(weeks=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = week_start - timedelta(days=week_start.weekday())  # Понедельник
        week_end = week_start + timedelta(days=7)
        
        week_entries = [
            e for e in all_entries
            if week_start <= e.created_at < week_end
        ]
        
        activity_by_week.append({
            "week": week_start.strftime("%Y-%m-%d"),
            "observation": sum(1 for e in week_entries if e.type == "observation"),
            "gratitude": sum(1 for e in week_entries if e.type == "gratitude"),
            "insight": sum(1 for e in week_entries if e.type == "insight"),
        })
    
    # Количество дней с активностью за последние 30 дней
    thirty_days_ago = now - timedelta(days=30)
    recent_entries = [e for e in all_entries if e.created_at >= thirty_days_ago]
    recent_dates = set(e.created_at.date() for e in recent_entries)
    recent_activity_days = len(recent_dates)
    
    # Самые частые слова (простой анализ)
    stop_words = {
        "и", "в", "на", "с", "по", "для", "от", "до", "из", "за", "к", "о", "об",
        "я", "ты", "он", "она", "мы", "вы", "они", "это", "что", "как", "где",
        "чтобы", "или", "но", "а", "то", "же", "так", "уже", "еще", "тоже",
        "мой", "твой", "наш", "ваш", "свой", "мне", "тебе", "ему", "ей", "нам",
        "вам", "им", "меня", "тебя", "его", "её", "нас", "вас", "их",
    }
    
    word_counts = Counter()
    for entry in all_entries:
        # Простое извлечение слов (кириллица и латиница)
        words = re.findall(r'\b[а-яёa-z]+\b', entry.content.lower())
        for word in words:
            if len(word) > 3 and word not in stop_words:  # Игнорируем короткие слова и стоп-слова
                word_counts[word] += 1
    
    most_common_words = [
        {"word": word, "count": count}
        for word, count in word_counts.most_common(20)
    ]
    
    # Анализ паттернов (pattern_axis_id)
    pattern_counts = Counter()
    for entry in all_entries:
        if entry.pattern_axis_id:
            pattern_counts[entry.pattern_axis_id] += 1
    
    most_common_patterns = [
        {"pattern_axis_id": pattern_id, "count": count}
        for pattern_id, count in pattern_counts.most_common(7)
    ]
    
    # Анализ контекстов (practice_id, tarot_card_id)
    context_counts = Counter()
    for entry in all_entries:
        if entry.practice_id:
            context_counts["practice"] += 1
        if entry.tarot_card_id:
            context_counts["tarot"] += 1
    
    most_common_contexts = [
        {"context_type": context_type, "count": count}
        for context_type, count in context_counts.most_common(5)
    ]
    
    # Среднее количество записей в неделю
    if all_entries:
        first_entry_date = all_entries[0].created_at
        weeks_span = max(1, (now - first_entry_date).days / 7)
        avg_entries_per_week = total_entries / weeks_span
    else:
        avg_entries_per_week = 0.0
    
    return JournalAnalyticsResponse(
        total_entries=total_entries,
        observation_count=observation_count,
        gratitude_count=gratitude_count,
        insight_count=insight_count,
        entries_by_type=entries_by_type,
        activity_by_month=activity_by_month,
        activity_by_week=activity_by_week,
        recent_activity_days=recent_activity_days,
        most_common_words=most_common_words,
        most_common_patterns=most_common_patterns,
        most_common_contexts=most_common_contexts,
        avg_entries_per_week=round(avg_entries_per_week, 2),
    )


class JournalRepetitionsResponse(BaseModel):
    """Повторы и акценты для ретеншна."""
    tension_mentions: Optional[int] = None  # Упоминания напряжения за 7 дней
    insight_after_practice: Optional[int] = None  # Инсайты после практик
    most_active_pattern: Optional[str] = None  # Самый активный паттерн (A1-A7)


@router.get("/repetitions", response_model=JournalRepetitionsResponse)
def get_journal_repetitions(
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """
    Получить повторы и акценты для мягкого зеркала.
    Не аналитика, а мягкое отражение паттернов.
    """
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    recent_entries = db.query(JournalEntry).filter(
        JournalEntry.user_id == current_user.id,
        JournalEntry.created_at >= seven_days_ago
    ).all()
    
    # Ищем упоминания напряжения (простой поиск по ключевым словам)
    tension_keywords = ["напряжение", "напряжен", "стресс", "тревог", "беспокойств"]
    tension_mentions = 0
    for entry in recent_entries:
        content_lower = entry.content.lower()
        if any(keyword in content_lower for keyword in tension_keywords):
            tension_mentions += 1
    
    # Инсайты после практик
    insight_after_practice = sum(
        1 for entry in recent_entries
        if entry.type == "insight" and entry.practice_id is not None
    )
    
    # Самый активный паттерн
    pattern_counts = {}
    for entry in recent_entries:
        if entry.pattern_axis_id:
            pattern_counts[entry.pattern_axis_id] = pattern_counts.get(entry.pattern_axis_id, 0) + 1
    
    most_active_pattern = None
    if pattern_counts:
        most_active_pattern = max(pattern_counts.items(), key=lambda x: x[1])[0]
    
    return JournalRepetitionsResponse(
        tension_mentions=tension_mentions if tension_mentions > 0 else None,
        insight_after_practice=insight_after_practice if insight_after_practice > 0 else None,
        most_active_pattern=most_active_pattern,
    )


@router.get("/export/csv")
def export_journal_csv(
    entry_type: Optional[str] = None,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """Export journal entries as CSV."""
    query = db.query(JournalEntry).filter(JournalEntry.user_id == current_user.id)
    
    if entry_type:
        if entry_type not in ["observation", "gratitude", "insight"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid entry type. Must be 'observation', 'gratitude', or 'insight'"
            )
        query = query.filter(JournalEntry.type == entry_type)
    
    entries = query.order_by(JournalEntry.created_at.desc()).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "ID", "Тип", "Содержание", "Практика", "Карта Таро", "Паттерн", "День", "Создано", "Обновлено"
    ])
    
    # Write entries
    for entry in entries:
        writer.writerow([
            entry.id,
            entry.type,
            entry.content,
            entry.practice_id or "",
            entry.tarot_card_id or "",
            entry.pattern_axis_id or "",
            entry.day.isoformat() if entry.day else "",
            entry.created_at.isoformat(),
            entry.updated_at.isoformat(),
        ])
    
    output.seek(0)
    
    # Generate filename
    filename = f"journal_entries_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/export/json")
def export_journal_json(
    entry_type: Optional[str] = None,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """Export journal entries as JSON."""
    import json
    
    query = db.query(JournalEntry).filter(JournalEntry.user_id == current_user.id)
    
    if entry_type:
        if entry_type not in ["observation", "gratitude", "insight"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid entry type. Must be 'observation', 'gratitude', or 'insight'"
            )
        query = query.filter(JournalEntry.type == entry_type)
    
    entries = query.order_by(JournalEntry.created_at.desc()).all()
    
    # Convert to dict
    entries_data = [
        {
            "id": entry.id,
            "type": entry.type,
            "content": entry.content,
            "practice_id": entry.practice_id,
            "tarot_card_id": entry.tarot_card_id,
            "pattern_axis_id": entry.pattern_axis_id,
            "day": entry.day.isoformat() if entry.day else None,
            "created_at": entry.created_at.isoformat(),
            "updated_at": entry.updated_at.isoformat(),
        }
        for entry in entries
    ]
    
    # Generate filename
    filename = f"journal_entries_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    
    return Response(
        content=json.dumps(entries_data, ensure_ascii=False, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

