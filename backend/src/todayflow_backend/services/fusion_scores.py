"""Детерминированные fusion scores (энергия / баланс / фокус) — общая логика для tracking и DE-9."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from todayflow_backend.db.models import (
    DayConnection,
    DayRitual,
    MenstrualCycle,
    ObservationDiaryEntry,
    PracticeUsage,
    ProgressTrackerEntry,
)


def _coerce_calendar_date(val: Any) -> date | None:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    if isinstance(val, str) and len(val) >= 10:
        try:
            return date.fromisoformat(val[:10])
        except ValueError:
            return None
    return None


def _clamp(value: int) -> int:
    return max(0, min(100, value))


def build_fusion_scores_for_inputs(
    *,
    practice_count: int,
    ritual_completed: bool,
    cycle_entry: Any | None,
    mood_avg: float | None,
    diary_done: bool,
    day_connection: Any | None,
    ascetic_completed: bool,
    affirmation_completed: bool,
) -> dict[str, int]:
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

    return {
        "energy": _clamp(energy),
        "emotional_balance": _clamp(emotional_balance),
        "focus": _clamp(focus),
    }


def _day_connection_has_flow_signal(dc: DayConnection | None) -> bool:
    """Ответы/сигналы DayConnection, которые участвуют в fusion (O7: опора для дельты)."""
    if dc is None:
        return False
    if getattr(dc, "ritual_feedback", None):
        return True
    if getattr(dc, "question_of_day_answer", None):
        return True
    if getattr(dc, "quick_decision_answer", None):
        return True
    return False


def compute_fusion_scores_for_date(db: Session, user_id: int, day: date) -> dict[str, int]:
    """Те же правила, что и в `GET /tracking/fusion/{date}` — только блок scores."""
    progress_entries = (
        db.query(ProgressTrackerEntry)
        .filter(ProgressTrackerEntry.user_id == user_id, ProgressTrackerEntry.date == day)
        .all()
    )
    diary_entry = (
        db.query(ObservationDiaryEntry)
        .filter(ObservationDiaryEntry.user_id == user_id, ObservationDiaryEntry.date == day)
        .first()
    )
    ritual_entry = (
        db.query(DayRitual).filter(DayRitual.user_id == user_id, DayRitual.date == day).first()
    )
    cycle_entry = (
        db.query(MenstrualCycle).filter(MenstrualCycle.user_id == user_id, MenstrualCycle.date == day).first()
    )
    practice_count = int(
        db.query(func.count(PracticeUsage.id))
        .filter(
            PracticeUsage.user_id == user_id,
            func.date(PracticeUsage.completed_at) == day,
        )
        .scalar()
        or 0
    )
    day_connection = (
        db.query(DayConnection).filter(DayConnection.user_id == user_id, DayConnection.date == day).first()
    )

    mood_values = [entry.state_scale for entry in progress_entries if entry.state_scale]
    mood_avg = round(sum(mood_values) / len(mood_values), 2) if mood_values else None
    ascetic_completed = any(entry.completed and entry.asceticism_id for entry in progress_entries)
    affirmation_completed = any(entry.completed and entry.affirmation_id for entry in progress_entries)
    ritual_completed = bool(ritual_entry and ritual_entry.completed)
    diary_done = diary_entry is not None

    return build_fusion_scores_for_inputs(
        practice_count=practice_count,
        ritual_completed=ritual_completed,
        cycle_entry=cycle_entry,
        mood_avg=mood_avg,
        diary_done=diary_done,
        day_connection=day_connection,
        ascetic_completed=ascetic_completed,
        affirmation_completed=affirmation_completed,
    )


def compute_fusion_scores_and_flow_signals_map_for_dates(
    db: Session, user_id: int, dates: list[date]
) -> tuple[dict[date, dict[str, int]], dict[date, bool]]:
    """DE-9 + O7: scores и флаг «в этот день были отметки Flow», влияющие на fusion (для доверия дельты)."""
    uniq = sorted(set(dates))
    if not uniq:
        return {}, {}
    lo, hi = uniq[0], uniq[-1]

    pes = (
        db.query(ProgressTrackerEntry)
        .filter(
            ProgressTrackerEntry.user_id == user_id,
            ProgressTrackerEntry.date >= lo,
            ProgressTrackerEntry.date <= hi,
        )
        .all()
    )
    pe_by_date: dict[date, list[ProgressTrackerEntry]] = defaultdict(list)
    for p in pes:
        pe_by_date[p.date].append(p)

    diary_dates_raw = (
        db.query(ObservationDiaryEntry.date)
        .filter(
            ObservationDiaryEntry.user_id == user_id,
            ObservationDiaryEntry.date >= lo,
            ObservationDiaryEntry.date <= hi,
        )
        .all()
    )
    diary_set = {row[0] for row in diary_dates_raw}

    rituals = (
        db.query(DayRitual)
        .filter(DayRitual.user_id == user_id, DayRitual.date >= lo, DayRitual.date <= hi)
        .all()
    )
    ritual_by_date = {r.date: r for r in rituals}

    cycles = (
        db.query(MenstrualCycle)
        .filter(MenstrualCycle.user_id == user_id, MenstrualCycle.date >= lo, MenstrualCycle.date <= hi)
        .all()
    )
    cycle_by_date = {c.date: c for c in cycles}

    connections = (
        db.query(DayConnection)
        .filter(DayConnection.user_id == user_id, DayConnection.date >= lo, DayConnection.date <= hi)
        .all()
    )
    dc_by_date = {c.date: c for c in connections}

    day_col = func.date(PracticeUsage.completed_at)
    practice_rows = (
        db.query(day_col.label("d"), func.count(PracticeUsage.id))
        .filter(
            PracticeUsage.user_id == user_id,
            day_col >= lo,
            day_col <= hi,
        )
        .group_by(day_col)
        .all()
    )
    practice_count_by_date: dict[date, int] = {}
    for d0, cnt in practice_rows:
        d_key = _coerce_calendar_date(d0)
        if d_key is None:
            continue
        practice_count_by_date[d_key] = int(cnt or 0)

    out: dict[date, dict[str, int]] = {}
    signals: dict[date, bool] = {}
    for d in uniq:
        progress_entries = pe_by_date.get(d, [])
        mood_values = [entry.state_scale for entry in progress_entries if entry.state_scale]
        mood_avg = round(sum(mood_values) / len(mood_values), 2) if mood_values else None
        ascetic_completed = any(entry.completed and entry.asceticism_id for entry in progress_entries)
        affirmation_completed = any(entry.completed and entry.affirmation_id for entry in progress_entries)
        ritual_entry = ritual_by_date.get(d)
        ritual_completed = bool(ritual_entry and ritual_entry.completed)
        diary_done = d in diary_set
        cycle_entry = cycle_by_date.get(d)
        day_connection = dc_by_date.get(d)
        practice_count = int(practice_count_by_date.get(d, 0))
        out[d] = build_fusion_scores_for_inputs(
            practice_count=practice_count,
            ritual_completed=ritual_completed,
            cycle_entry=cycle_entry,
            mood_avg=mood_avg,
            diary_done=diary_done,
            day_connection=day_connection,
            ascetic_completed=ascetic_completed,
            affirmation_completed=affirmation_completed,
        )
        has_flow = (
            practice_count > 0
            or mood_avg is not None
            or diary_done
            or ritual_completed
            or ascetic_completed
            or affirmation_completed
            or _day_connection_has_flow_signal(day_connection)
        )
        signals[d] = bool(has_flow)
    return out, signals


def compute_fusion_scores_map_for_dates(
    db: Session, user_id: int, dates: list[date]
) -> dict[date, dict[str, int]]:
    """Один проход по БД для нескольких календарных дат (DE-9 / история тренда)."""
    scores, _ = compute_fusion_scores_and_flow_signals_map_for_dates(db, user_id, dates)
    return scores
