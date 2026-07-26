"""Day Lifecycle C5 clock — not_ready before local ready_at."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from todayflow_backend.services.day_lifecycle_clock_c5 import (
    DAY_STATUS_NOT_READY,
    DAY_STATUS_READY,
    build_day_not_ready_contract,
    compute_day_lifecycle_c5,
)


def test_before_ready_at_is_not_ready() -> None:
    tz = "Europe/Warsaw"
    now = datetime(2026, 7, 27, 1, 15, tzinfo=ZoneInfo(tz))
    lc = compute_day_lifecycle_c5(now=now, timezone_name=tz, ready_time="08:30")
    assert lc["status"] == DAY_STATUS_NOT_READY
    assert lc["local_date"] == "2026-07-27"
    assert lc["ready_at"].startswith("2026-07-27T08:30:00")


def test_at_ready_at_is_ready() -> None:
    tz = "Europe/Warsaw"
    now = datetime(2026, 7, 27, 8, 30, tzinfo=ZoneInfo(tz))
    lc = compute_day_lifecycle_c5(now=now, timezone_name=tz, ready_time="08:30")
    assert lc["status"] == DAY_STATUS_READY


def test_explicit_other_date_skips_morning_gate() -> None:
    tz = "Europe/Warsaw"
    now = datetime(2026, 7, 27, 1, 15, tzinfo=ZoneInfo(tz))
    from datetime import date

    lc = compute_day_lifecycle_c5(
        now=now,
        timezone_name=tz,
        ready_time="08:30",
        target_date=date(2026, 7, 26),
    )
    assert lc["status"] == DAY_STATUS_READY
    assert lc["target_date"] == "2026-07-26"


def test_not_ready_contract_has_no_day_story() -> None:
    lc = compute_day_lifecycle_c5(
        now=datetime(2026, 7, 27, 2, 0, tzinfo=ZoneInfo("Europe/Moscow")),
        timezone_name="Europe/Moscow",
    )
    shell = build_day_not_ready_contract(lifecycle=lc, locale="ru")
    assert shell["generation_id"] == "day-not-ready-c5"
    assert shell["day_story"] is None
    assert shell["progress"]["day_lifecycle"]["status"] == DAY_STATUS_NOT_READY
    assert "08:30" in shell["primary_action"]


def test_assemble_window_flag() -> None:
    tz = "Europe/Moscow"
    now = datetime(2026, 7, 27, 6, 0, tzinfo=ZoneInfo(tz))
    lc = compute_day_lifecycle_c5(now=now, timezone_name=tz)
    assert lc["assemble_window"]["active"] is True
    assert lc["status"] == DAY_STATUS_NOT_READY  # before 08:30
