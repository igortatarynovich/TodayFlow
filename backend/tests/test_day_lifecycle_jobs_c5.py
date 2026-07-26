"""Day Lifecycle C5.1–C5.3 — system close + clock helpers."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from todayflow_backend.db.models import Base, DayConnection, DayRitual, User
from todayflow_backend.services.day_lifecycle_clock_c5 import (
    DAY_STATUS_CLOSED,
    DAY_STATUS_NOT_READY,
    DAY_STATUS_READY,
    compute_day_lifecycle_c5,
    in_assemble_window,
    should_system_close_date,
)
from todayflow_backend.services.day_lifecycle_jobs_c5 import (
    SYSTEM_CLOSE_MARKER,
    system_close_user_day,
)


def _session():
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=eng)
    return sessionmaker(bind=eng)()


def test_closed_status_wins() -> None:
    tz = "Europe/Warsaw"
    now = datetime(2026, 7, 26, 20, 0, tzinfo=ZoneInfo(tz))
    lc = compute_day_lifecycle_c5(now=now, timezone_name=tz, closed=True)
    assert lc["status"] == DAY_STATUS_CLOSED
    assert lc["close_time"] == "23:00"


def test_assemble_window_and_close_deadline() -> None:
    tz = ZoneInfo("Europe/Moscow")
    morning = datetime(2026, 7, 27, 6, 0, tzinfo=tz)
    assert in_assemble_window(morning) is True
    assert should_system_close_date(now_local=morning, candidate=morning.date()) is False
    assert should_system_close_date(
        now_local=morning,
        candidate=morning.date() - timedelta(days=1),
    ) is True

    late = datetime(2026, 7, 27, 23, 5, tzinfo=tz)
    assert should_system_close_date(now_local=late, candidate=late.date()) is True


def test_system_close_marks_evening() -> None:
    db = _session()
    user = User(id=9, email="close@test.local", password_hash="x")
    db.add(user)
    db.commit()
    day = date(2026, 7, 26)

    assert system_close_user_day(db, user_id=9, local_date=day) == "closed"
    row = db.query(DayConnection).filter(DayConnection.user_id == 9, DayConnection.date == day).one()
    assert row.evening_completed is True
    assert isinstance(row.evening_observations, dict)
    assert row.evening_observations.get(SYSTEM_CLOSE_MARKER) is True
    assert row.evening_observations.get("closed_by") == "system"

    ritual = db.query(DayRitual).filter(DayRitual.user_id == 9, DayRitual.date == day).one()
    assert ritual.completed is True

    assert system_close_user_day(db, user_id=9, local_date=day) == "already_closed"


def test_not_ready_before_ready_still() -> None:
    now = datetime(2026, 7, 27, 1, 0, tzinfo=ZoneInfo("Europe/Warsaw"))
    lc = compute_day_lifecycle_c5(now=now, timezone_name="Europe/Warsaw")
    assert lc["status"] == DAY_STATUS_NOT_READY
    assert DAY_STATUS_READY != lc["status"]
