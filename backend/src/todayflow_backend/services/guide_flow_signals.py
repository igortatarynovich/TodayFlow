"""DE-7: server-side «done» signals from meaning_events for fusion / DayContext."""

from __future__ import annotations

from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from todayflow_backend.db.models import MeaningEvent

# Canonical types counted for `fusion.activity_context.guide_meaning_completions_today`
# (same day, `local_date`; do not trust client totals).
GUIDE_MEANING_COMPLETION_EVENT_TYPES: tuple[str, ...] = (
    "habit_completed",
    "practice_completed",
    "focus_completed",
    "affirmation_done",
    "ascetic_step_done",
)


def guide_meaning_completions_today_counts(
    db: Session, *, user_id: int, day: date
) -> dict[str, int]:
    rows = (
        db.query(MeaningEvent.event_type, func.count(MeaningEvent.id))
        .filter(
            MeaningEvent.user_id == user_id,
            MeaningEvent.local_date == day,
            MeaningEvent.event_type.in_(GUIDE_MEANING_COMPLETION_EVENT_TYPES),
        )
        .group_by(MeaningEvent.event_type)
        .all()
    )
    out = {t: 0 for t in GUIDE_MEANING_COMPLETION_EVENT_TYPES}
    for et, c in rows:
        if et in out:
            out[et] = int(c or 0)
    return out
