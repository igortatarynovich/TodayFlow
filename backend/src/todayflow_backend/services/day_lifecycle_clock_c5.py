"""Day Lifecycle C5 — clock for assemble-once / ready / not-ready.

Canon: docs/audits/DAY_LIFECYCLE_V1.md

Status vocabulary (progress.day_lifecycle.status):
  - day_not_ready — local midnight → ready_at (default morning_time 08:30)
  - ready — at/after ready_at (story may still be assembling elsewhere)
  - closed — user or system evening close (C5.3)
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# Defaults aligned with push DEFAULT_SCHEDULE + DAY_LIFECYCLE_V1.
DEFAULT_TIMEZONE = "Europe/Moscow"
DEFAULT_READY_TIME = "08:30"
DEFAULT_ASSEMBLE_START = "05:00"
DEFAULT_ASSEMBLE_END = "07:00"
DEFAULT_CLOSE_TIME = "23:00"

DAY_STATUS_NOT_READY = "day_not_ready"
DAY_STATUS_ASSEMBLING = "assembling"
DAY_STATUS_READY = "ready"
DAY_STATUS_CLOSED = "closed"


def parse_hhmm(value: str | None, *, fallback: str) -> time:
    raw = (value or "").strip() or fallback
    try:
        hh, mm = raw.split(":")
        return time(hour=int(hh), minute=int(mm))
    except (TypeError, ValueError):
        fh, fm = fallback.split(":")
        return time(hour=int(fh), minute=int(fm))


def resolve_zone(timezone_name: str | None) -> ZoneInfo:
    name = (timezone_name or "").strip() or DEFAULT_TIMEZONE
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        return ZoneInfo(DEFAULT_TIMEZONE)


def local_now(*, now: datetime | None = None, timezone_name: str | None = None) -> datetime:
    tz = resolve_zone(timezone_name)
    base = now or datetime.now(timezone.utc)
    if base.tzinfo is None:
        base = base.replace(tzinfo=timezone.utc)
    return base.astimezone(tz)


def compute_day_lifecycle_c5(
    *,
    now: datetime | None = None,
    timezone_name: str | None = None,
    ready_time: str | None = None,
    assemble_start: str | None = None,
    assemble_end: str | None = None,
    close_time: str | None = None,
    closed: bool = False,
    target_date: date | None = None,
) -> dict[str, Any]:
    """Pure clock. Gate not_ready only when target_date is the current local date."""
    tz_name = (timezone_name or "").strip() or DEFAULT_TIMEZONE
    tz = resolve_zone(tz_name)
    now_local = local_now(now=now, timezone_name=tz_name)
    local_date = now_local.date()
    ready_t = parse_hhmm(ready_time, fallback=DEFAULT_READY_TIME)
    asm_start = parse_hhmm(assemble_start, fallback=DEFAULT_ASSEMBLE_START)
    asm_end = parse_hhmm(assemble_end, fallback=DEFAULT_ASSEMBLE_END)
    close_t = parse_hhmm(close_time, fallback=DEFAULT_CLOSE_TIME)

    ready_at = datetime.combine(local_date, ready_t, tzinfo=tz)
    assemble_start_at = datetime.combine(local_date, asm_start, tzinfo=tz)
    assemble_end_at = datetime.combine(local_date, asm_end, tzinfo=tz)
    close_at = datetime.combine(local_date, close_t, tzinfo=tz)
    in_assemble = assemble_start_at <= now_local < assemble_end_at
    past_close = now_local >= close_at

    effective_date = target_date or local_date
    if closed:
        status = DAY_STATUS_CLOSED
    elif effective_date != local_date:
        # Historical / explicit other day — no morning gate.
        status = DAY_STATUS_READY
    elif now_local < ready_at:
        status = DAY_STATUS_NOT_READY
    else:
        status = DAY_STATUS_READY

    return {
        "contract_version": "day_lifecycle_c5",
        "status": status,
        "local_date": local_date.isoformat(),
        "target_date": effective_date.isoformat(),
        "timezone": str(tz),
        "ready_time": ready_t.strftime("%H:%M"),
        "ready_at": ready_at.isoformat(),
        "close_time": close_t.strftime("%H:%M"),
        "close_at": close_at.isoformat(),
        "past_close_deadline": past_close,
        "assemble_window": {
            "start": asm_start.strftime("%H:%M"),
            "end": asm_end.strftime("%H:%M"),
            "active": in_assemble,
        },
        "now_local": now_local.isoformat(),
    }


def in_assemble_window(
    now_local: datetime,
    *,
    assemble_start: str | None = None,
    assemble_end: str | None = None,
) -> bool:
    start = parse_hhmm(assemble_start, fallback=DEFAULT_ASSEMBLE_START)
    end = parse_hhmm(assemble_end, fallback=DEFAULT_ASSEMBLE_END)
    minutes = now_local.hour * 60 + now_local.minute
    return (start.hour * 60 + start.minute) <= minutes < (end.hour * 60 + end.minute)


def should_system_close_date(
    *,
    now_local: datetime,
    candidate: date,
    close_time: str | None = None,
    assemble_start: str | None = None,
) -> bool:
    """True when candidate day should be force-closed if user did not close."""
    from datetime import timedelta

    today = now_local.date()
    close_t = parse_hhmm(close_time, fallback=DEFAULT_CLOSE_TIME)
    asm_start = parse_hhmm(assemble_start, fallback=DEFAULT_ASSEMBLE_START)
    if candidate == today:
        close_at = datetime.combine(today, close_t, tzinfo=now_local.tzinfo)
        return now_local >= close_at
    if candidate == today - timedelta(days=1):
        # Catch-up: once today's assemble window opens, yesterday must be closed.
        assemble_at = datetime.combine(today, asm_start, tzinfo=now_local.tzinfo)
        return now_local >= assemble_at
    return False


def resolve_user_timezone(db, *, user_id: int, explicit: str | None = None) -> str:
    """Prefer explicit request TZ, else push schedule, else default."""
    from todayflow_backend.db import models as db_models

    if (explicit or "").strip():
        return resolve_zone(explicit).key
    row = (
        db.query(db_models.UserPushSchedule)
        .filter(db_models.UserPushSchedule.user_id == int(user_id))
        .first()
    )
    if row is not None and (row.timezone or "").strip():
        return resolve_zone(row.timezone).key
    return DEFAULT_TIMEZONE


def resolve_user_ready_time(db, *, user_id: int) -> str:
    from todayflow_backend.db import models as db_models

    row = (
        db.query(db_models.UserPushSchedule)
        .filter(db_models.UserPushSchedule.user_id == int(user_id))
        .first()
    )
    if row is not None and (row.morning_time or "").strip():
        return parse_hhmm(row.morning_time, fallback=DEFAULT_READY_TIME).strftime("%H:%M")
    return DEFAULT_READY_TIME


def build_day_not_ready_contract(*, lifecycle: dict[str, Any], locale: str = "ru") -> dict[str, Any]:
    """Minimal today_contract_v1 shell — no day_story plot before ready_at."""
    from todayflow_backend.services.today_contract_fallbacks_v1 import DOMAIN_FALLBACKS_V1

    meta = DOMAIN_FALLBACKS_V1["_meta"]
    _ = meta
    domains = {
        key: dict(val)
        for key, val in DOMAIN_FALLBACKS_V1.items()
        if key != "_meta"
    }
    if (locale or "").lower().startswith("en"):
        primary = f"Your day will be ready at {lifecycle.get('ready_time') or DEFAULT_READY_TIME}."
        period = "The day is still assembling — check back at ready time."
        growth = "Quiet hours: nothing to decide yet."
    else:
        primary = f"День будет готов в {lifecycle.get('ready_time') or DEFAULT_READY_TIME}."
        period = "День ещё собирается — до утра сценарий закрыт."
        growth = "Сейчас тихие часы: ничего решать не нужно."

    return {
        "contract_version": "today_contract_v1",
        "global_context": {"period": period},
        "personal_growth": {"development_point": growth},
        "domains": domains,
        "primary_action": primary,
        "progress": {
            "day_lifecycle": lifecycle,
            "story_status": "not_ready",
            "story_refresh_required": False,
        },
        "generation_id": "day-not-ready-c5",
        "day_story": None,
    }


def build_day_assembling_contract(*, lifecycle: dict[str, Any], locale: str = "ru") -> dict[str, Any]:
    """Past ready_at but package not served yet — beautiful wait, no user-triggered assemble."""
    nest = dict(lifecycle or {})
    nest["status"] = DAY_STATUS_ASSEMBLING
    shell = build_day_not_ready_contract(lifecycle=nest, locale=locale)
    if (locale or "").lower().startswith("en"):
        shell["primary_action"] = "Your day is almost ready — one moment."
        shell["global_context"] = {"period": "We are laying out today’s package."}
    else:
        shell["primary_action"] = "День почти готов — ещё мгновение."
        shell["global_context"] = {"period": "Мы раскладываем сегодняшний пакет."}
    progress = dict(shell.get("progress") or {})
    progress["story_status"] = "assembling"
    shell["progress"] = progress
    shell["generation_id"] = "day-assembling-c5"
    return shell
