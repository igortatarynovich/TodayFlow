"""Day Lifecycle C5.1–C5.3 — system close + clock helpers + pre-warm guards."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from unittest.mock import patch
from zoneinfo import ZoneInfo

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from todayflow_backend.db.models import Base, DayConnection, DayRitual, DaySymbolState, PushDevice, User
from todayflow_backend.db import models as db_models
from todayflow_backend.services.day_lifecycle_clock_c5 import (
    DAY_STATUS_ASSEMBLING,
    DAY_STATUS_CLOSED,
    DAY_STATUS_NOT_READY,
    DAY_STATUS_READY,
    DEFAULT_ASSEMBLE_END,
    build_day_assembling_contract,
    compute_day_lifecycle_c5,
    in_assemble_window,
    in_d_minus_1_window,
    should_system_close_date,
)
from todayflow_backend.services.day_lifecycle_jobs_c5 import (
    SYSTEM_CLOSE_MARKER,
    _candidate_user_ids,
    prewarm_assemble_user_day,
    run_day_lifecycle_due,
    system_close_user_day,
)
from todayflow_backend.services.day_symbol_state_v1 import (
    ensure_symbols_prebaked,
    is_card_revealed,
    is_number_revealed,
    owner_key_for_user,
    public_view,
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
    morning = datetime(2026, 7, 27, 4, 0, tzinfo=tz)
    assert in_assemble_window(morning) is True
    assert DEFAULT_ASSEMBLE_END == "05:00"
    assert should_system_close_date(now_local=morning, candidate=morning.date()) is False
    assert should_system_close_date(
        now_local=morning,
        candidate=morning.date() - timedelta(days=1),
    ) is True

    late = datetime(2026, 7, 27, 23, 5, tzinfo=tz)
    assert should_system_close_date(now_local=late, candidate=late.date()) is True
    assert in_d_minus_1_window(late) is True
    assert in_d_minus_1_window(morning) is False


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


def test_assembling_contract_shell() -> None:
    lc = compute_day_lifecycle_c5(
        now=datetime(2026, 7, 27, 9, 0, tzinfo=ZoneInfo("Europe/Warsaw")),
        timezone_name="Europe/Warsaw",
    )
    shell = build_day_assembling_contract(lifecycle=lc, locale="ru")
    assert shell["day_story"] is None
    assert shell["progress"]["story_status"] == "assembling"
    assert shell["progress"]["day_lifecycle"]["status"] == DAY_STATUS_ASSEMBLING
    assert "почти готов" in shell["primary_action"].lower() or "мгновение" in shell["primary_action"].lower()


def test_symbols_prebaked_hidden_until_reveal() -> None:
    db = _session()
    user = User(id=21, email="sym@test.local", password_hash="x")
    db.add(user)
    db.commit()
    day = date(2026, 7, 27)
    owner = owner_key_for_user(21)
    row = ensure_symbols_prebaked(
        db,
        owner_key=owner,
        local_date=day,
        timezone_name="Europe/Moscow",
        user_id=21,
        locale="ru",
    )
    assert row.number_reduced is not None
    assert row.card_id is not None
    assert is_number_revealed(row) is False
    assert is_card_revealed(row) is False
    view = public_view(row, local_date=day, timezone_name="Europe/Moscow")
    assert view["number"]["revealed"] is False
    assert "value" not in view["number"]
    assert view["card"]["revealed"] is False
    assert "id" not in view["card"]
    stored = db.query(DaySymbolState).filter(DaySymbolState.owner_key == owner).one()
    assert stored.number_reduced == row.number_reduced


def test_run_day_lifecycle_due_calls_prewarm_in_window() -> None:
    db = _session()
    user = User(id=33, email="prewarm@test.local", password_hash="x")
    db.add(user)
    db.add(PushDevice(user_id=33, platform="web", token="tok-prewarm-33"))
    db.commit()
    now = datetime(2026, 7, 27, 4, 15, tzinfo=ZoneInfo("Europe/Moscow"))

    with patch(
        "todayflow_backend.services.day_lifecycle_jobs_c5.day_story_is_product_ready",
        return_value=False,
    ):
        with patch(
            "todayflow_backend.services.day_prewarm_job_c5.enqueue_day_prewarm",
        ) as enqueue:
            with patch(
                "todayflow_backend.services.day_lifecycle_jobs_c5._schedule_row",
                return_value={
                    "timezone": "Europe/Moscow",
                    "morning_time": "05:00",
                },
            ):
                counts = run_day_lifecycle_due(db, now_utc=now.astimezone(ZoneInfo("UTC")), max_prewarm=2)
    assert counts["prewarm_candidates"] >= 1
    assert counts["prewarm_enqueued"] >= 1
    assert enqueue.called


def test_prewarm_skips_when_ready_but_still_prebakes_symbols() -> None:
    db = _session()
    user = User(id=44, email="ready@test.local", password_hash="x")
    db.add(user)
    db.commit()
    day = date(2026, 7, 27)

    with patch(
        "todayflow_backend.services.day_lifecycle_jobs_c5.day_story_is_product_ready",
        return_value=True,
    ):
        outcome = prewarm_assemble_user_day(
            db,
            user=user,
            local_date=day,
            timezone_name="UTC",
            locale="ru",
        )
    assert outcome == "skipped_ready"
    owner = owner_key_for_user(44)
    row = db.query(DaySymbolState).filter(DaySymbolState.owner_key == owner, DaySymbolState.local_date == day).one()
    assert row.number_reduced is not None
    assert row.card_id is not None


def test_candidate_user_ids_includes_astro_profile() -> None:
    db = _session()
    db.add(User(id=71, email="astro@test.local", password_hash="x"))
    db.add(User(id=72, email="idle@test.local", password_hash="x"))
    db.add(
        db_models.AstroProfile(
            user_id=71,
            label="self",
            birth_date=date(1990, 1, 15),
            relation="self",
            is_primary=True,
        )
    )
    db.commit()
    ids = _candidate_user_ids(db)
    assert 71 in ids
    assert 72 not in ids


def test_candidate_user_ids_excludes_example_com() -> None:
    db = _session()
    db.add(User(id=91, email="p0compat@example.com", password_hash="x"))
    db.add(
        db_models.AstroProfile(
            user_id=91,
            label="self",
            birth_date=date(1990, 1, 15),
            relation="self",
            is_primary=True,
        )
    )
    db.commit()
    ids = _candidate_user_ids(db)
    assert 91 not in ids


def test_enqueue_day_prewarm_schedules_runner() -> None:
    db = _session()
    db.add(User(id=81, email="catchup@test.local", password_hash="x"))
    db.commit()
    from todayflow_backend.services.day_prewarm_job_c5 import enqueue_day_prewarm

    with patch(
        "todayflow_backend.services.day_prewarm_job_c5.schedule_job_runner"
    ) as schedule:
        job = enqueue_day_prewarm(
            db,
            user_id=81,
            local_date=date(2026, 8, 3),
            locale="ru",
            timezone_name="Europe/Moscow",
        )
    assert job.user_id == 81
    assert job.module == "day_lifecycle"
    assert job.surface == "prewarm"
    assert schedule.called
