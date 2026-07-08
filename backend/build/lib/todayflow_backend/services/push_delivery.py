"""Push notification delivery: schedules, daily goal nudges, FCM stub."""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any

import httpx
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from todayflow_backend.core.config import settings
from todayflow_backend.db import models as db_models

logger = logging.getLogger(__name__)

WINDOW_MINUTES = 14

DEFAULT_SCHEDULE: dict[str, Any] = {
    "timezone": "Europe/Moscow",
    "morning_enabled": True,
    "morning_time": "08:30",
    "day_enabled": True,
    "day_time": "13:00",
    "evening_enabled": True,
    "evening_time": "20:00",
    "goal_midday_enabled": True,
    "goal_midday_time": "12:30",
    "goal_afternoon_enabled": True,
    "goal_afternoon_time": "16:00",
    "quiet_start": "22:00",
    "quiet_end": "08:00",
    "max_auto_per_day": 5,
    "notify_rhythm_today": True,
    "notify_goal_nudges": True,
    "notify_goal_ack": True,
    "notify_streak_care": True,
    "notify_weekly_focus": True,
    "notify_tarot_card": True,
    "notify_habit_reminders": True,
    "notify_comeback": True,
}

# Крон-напоминания, суммарный дневной лимит которых задаёт max_auto_per_day
AUTO_CAP_KINDS = frozenset(
    {"morning_rhythm", "day_rhythm", "evening_rhythm", "goal_midday", "goal_afternoon"}
)


def _tz(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name or "UTC")
    except ZoneInfoNotFoundError:
        return ZoneInfo("UTC")


def _parse_hhmm(value: str) -> int:
    parts = (value or "12:00").strip().split(":")
    h = int(parts[0]) if parts[0].isdigit() else 12
    m = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    return h * 60 + m


def _circ_minutes_apart(a: int, b: int) -> int:
    d = abs(a - b)
    return min(d, 1440 - d)


def _within_window(now_minutes: int, target_minutes: int) -> bool:
    return _circ_minutes_apart(now_minutes, target_minutes) <= WINDOW_MINUTES


def _in_quiet_hours(now_minutes: int, quiet_start: str, quiet_end: str) -> bool:
    """Типичный кейс: 22:00–08:00 (start > end, охватывает полночь). Если start < end — интервал внутри суток."""
    a = _parse_hhmm(quiet_start)
    b = _parse_hhmm(quiet_end)
    if a == b:
        return False
    if a > b:
        return now_minutes >= a or now_minutes < b
    return a <= now_minutes < b


def _auto_dispatch_count(db: Session, user_id: int, local_day: date) -> int:
    q = (
        db.query(func.count(db_models.PushDispatchLog.id))
        .filter(
            db_models.PushDispatchLog.user_id == user_id,
            db_models.PushDispatchLog.dispatch_date == local_day,
            db_models.PushDispatchLog.kind.in_(AUTO_CAP_KINDS),
        )
    )
    return int(q.scalar() or 0)


def _schedule_row(sched: db_models.UserPushSchedule | None) -> dict[str, Any]:
    if not sched:
        return dict(DEFAULT_SCHEDULE)
    cap = getattr(sched, "max_auto_per_day", None)
    if cap is None:
        cap = DEFAULT_SCHEDULE["max_auto_per_day"]
    cap = max(1, min(15, int(cap)))
    return {
        "timezone": sched.timezone or DEFAULT_SCHEDULE["timezone"],
        "morning_enabled": bool(sched.morning_enabled),
        "morning_time": sched.morning_time or DEFAULT_SCHEDULE["morning_time"],
        "day_enabled": bool(sched.day_enabled),
        "day_time": sched.day_time or DEFAULT_SCHEDULE["day_time"],
        "evening_enabled": bool(sched.evening_enabled),
        "evening_time": sched.evening_time or DEFAULT_SCHEDULE["evening_time"],
        "goal_midday_enabled": bool(sched.goal_midday_enabled),
        "goal_midday_time": sched.goal_midday_time or DEFAULT_SCHEDULE["goal_midday_time"],
        "goal_afternoon_enabled": bool(sched.goal_afternoon_enabled),
        "goal_afternoon_time": sched.goal_afternoon_time or DEFAULT_SCHEDULE["goal_afternoon_time"],
        "quiet_start": getattr(sched, "quiet_start", None) or DEFAULT_SCHEDULE["quiet_start"],
        "quiet_end": getattr(sched, "quiet_end", None) or DEFAULT_SCHEDULE["quiet_end"],
        "max_auto_per_day": cap,
        "notify_rhythm_today": bool(getattr(sched, "notify_rhythm_today", True)),
        "notify_goal_nudges": bool(getattr(sched, "notify_goal_nudges", True)),
        "notify_goal_ack": bool(getattr(sched, "notify_goal_ack", True)),
        "notify_streak_care": bool(getattr(sched, "notify_streak_care", True)),
        "notify_weekly_focus": bool(getattr(sched, "notify_weekly_focus", True)),
        "notify_tarot_card": bool(getattr(sched, "notify_tarot_card", True)),
        "notify_habit_reminders": bool(getattr(sched, "notify_habit_reminders", True)),
        "notify_comeback": bool(getattr(sched, "notify_comeback", True)),
    }


def upsert_daily_goal_snapshot(db: Session, *, user_id: int, target_date: date, goal_text: str) -> None:
    text = (goal_text or "").strip()
    if not text:
        return
    row = (
        db.query(db_models.DailyGoalSnapshot)
        .filter(
            db_models.DailyGoalSnapshot.user_id == user_id,
            db_models.DailyGoalSnapshot.target_date == target_date,
        )
        .first()
    )
    if row:
        row.goal_text = text
    else:
        db.add(
            db_models.DailyGoalSnapshot(
                user_id=user_id,
                target_date=target_date,
                goal_text=text,
            )
        )
    db.commit()


def _send_fcm_legacy(token: str, title: str, body: str, data: dict[str, str]) -> bool:
    key = settings.fcm_server_key
    if not key:
        return False
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.post(
                "https://fcm.googleapis.com/fcm/send",
                headers={
                    "Authorization": f"key={key}",
                    "Content-Type": "application/json",
                },
                json={
                    "to": token,
                    "notification": {"title": title, "body": body},
                    "data": data,
                    "priority": "high",
                },
            )
            if r.status_code >= 400:
                logger.warning("FCM error %s: %s", r.status_code, r.text[:500])
                return False
            return True
    except Exception as e:
        logger.warning("FCM request failed: %s", e, exc_info=True)
        return False


def deliver_to_user_devices(
    db: Session,
    *,
    user_id: int,
    title: str,
    body: str,
    data: dict[str, str],
) -> int:
    """Send to all devices; returns count of successful sends (including log-only when no FCM key)."""
    devices = db.query(db_models.PushDevice).filter(db_models.PushDevice.user_id == user_id).all()
    if not devices:
        logger.info("push_skip_no_device user=%s title=%s", user_id, title)
        return 0
    sent = 0
    for d in devices:
        ok = _send_fcm_legacy(d.token, title, body, data)
        if ok or not settings.fcm_server_key:
            # Without FCM key we still count as "delivered" for cron metrics / logs
            sent += 1
            logger.info(
                "push_deliver user=%s platform=%s title=%s fcm=%s",
                user_id,
                d.platform,
                title,
                bool(settings.fcm_server_key and ok),
            )
    return sent


def _already_sent(db: Session, user_id: int, local_day: date, kind: str) -> bool:
    return (
        db.query(db_models.PushDispatchLog)
        .filter(
            db_models.PushDispatchLog.user_id == user_id,
            db_models.PushDispatchLog.dispatch_date == local_day,
            db_models.PushDispatchLog.kind == kind,
        )
        .first()
        is not None
    )


def _mark_sent(db: Session, user_id: int, local_day: date, kind: str) -> None:
    try:
        db.add(
            db_models.PushDispatchLog(
                user_id=user_id,
                dispatch_date=local_day,
                kind=kind,
            )
        )
        db.commit()
    except IntegrityError:
        db.rollback()


def _copy_rhythm(*, en: bool, phase: str) -> tuple[str, str]:
    if phase == "morning":
        return (
            ("TodayFlow — morning", "Open Today: set your line for the day.")
            if en
            else ("TodayFlow — утро", "Зайди в Today и зафиксируй линию дня.")
        )
    if phase == "day":
        return (
            ("TodayFlow — day", "Short check-in: one honest mark in Today.")
            if en
            else ("TodayFlow — день", "Короткий чекин в Today — одна честная отметка.")
        )
    return (
        ("TodayFlow — evening", "Close the day in Today when you are ready.")
        if en
        else ("TodayFlow — вечер", "Закрой день в Today, когда будешь готов.")
    )


def notify_goal_saved(db: Session, user: db_models.User, *, goal_preview: str) -> None:
    """Immediate acknowledgment when user saves a tracked goal (weekly/calendar line). Не входит в max_auto_per_day."""
    st = user.settings
    if not st or not st.push_opt_in:
        return
    if not db.query(db_models.PushDevice).filter(db_models.PushDevice.user_id == user.id).first():
        return
    sched_row = db.query(db_models.UserPushSchedule).filter(db_models.UserPushSchedule.user_id == user.id).first()
    sch = _schedule_row(sched_row)
    if not sch["notify_goal_ack"]:
        return
    tz = _tz(sch["timezone"])
    nu = datetime.now(timezone.utc)
    now_local = nu.astimezone(tz)
    now_min = now_local.hour * 60 + now_local.minute
    if _in_quiet_hours(now_min, sch["quiet_start"], sch["quiet_end"]):
        logger.info("push_goal_saved_quiet_skip user=%s", user.id)
        return
    en = (st.locale or "").lower().startswith("en")
    short = goal_preview.strip()
    if len(short) > 120:
        short = short[:117] + "..."
    title, body = (
        ("Focus saved", f"We will nudge you to stay on this weekly line: {short}")
        if en
        else ("Фокус в трекинге сохранён", f"Будем мягко напоминать про недельную линию: {short}")
    )
    deliver_to_user_devices(
        db,
        user_id=user.id,
        title=title,
        body=body,
        data={"route": "/tracking/calendar", "kind": "goal_saved"},
    )


def notify_morning_intention_saved(db: Session, user: db_models.User, *, intention_preview: str) -> None:
    """Acknowledgment when user saves morning intention (not the same as tracked goals). Не входит в max_auto_per_day."""
    st = user.settings
    if not st or not st.push_opt_in:
        return
    if not db.query(db_models.PushDevice).filter(db_models.PushDevice.user_id == user.id).first():
        return
    sched_row = db.query(db_models.UserPushSchedule).filter(db_models.UserPushSchedule.user_id == user.id).first()
    sch = _schedule_row(sched_row)
    if not sch["notify_goal_ack"]:
        return
    tz = _tz(sch["timezone"])
    nu = datetime.now(timezone.utc)
    now_local = nu.astimezone(tz)
    now_min = now_local.hour * 60 + now_local.minute
    if _in_quiet_hours(now_min, sch["quiet_start"], sch["quiet_end"]):
        logger.info("push_intention_saved_quiet_skip user=%s", user.id)
        return
    en = (st.locale or "").lower().startswith("en")
    short = intention_preview.strip()
    if len(short) > 120:
        short = short[:117] + "..."
    title, body = (
        ("Intention saved", f"Today’s line: {short}")
        if en
        else ("Намерение на день сохранено", f"Твоя линия сегодня: {short}")
    )
    deliver_to_user_devices(
        db,
        user_id=user.id,
        title=title,
        body=body,
        data={"route": "/today", "kind": "intention_saved"},
    )


def run_due_notifications(db: Session, *, now_utc: datetime | None = None) -> dict[str, int]:
    """
    Called from cron (POST /internal/push/run-due). Uses each user's local time and schedule.
    Kinds: morning_rhythm, day_rhythm, evening_rhythm, goal_midday, goal_afternoon
    """
    now_utc = now_utc or datetime.utcnow()
    counts: dict[str, int] = {
        k: 0
        for k in (
            "morning_rhythm",
            "day_rhythm",
            "evening_rhythm",
            "goal_midday",
            "goal_afternoon",
            "skipped",
            "blocked_quiet",
            "blocked_cap",
        )
    }

    user_ids = [r[0] for r in db.query(db_models.PushDevice.user_id).distinct().all()]
    for uid in user_ids:
        user = db.query(db_models.User).filter(db_models.User.id == uid).first()
        if not user:
            continue
        st = user.settings
        if not st or not st.push_opt_in:
            counts["skipped"] += 1
            continue

        sched_row = db.query(db_models.UserPushSchedule).filter(db_models.UserPushSchedule.user_id == uid).first()
        sch = _schedule_row(sched_row)
        tz = _tz(sch["timezone"])
        nu = now_utc
        if nu.tzinfo is None:
            nu = nu.replace(tzinfo=timezone.utc)
        now_local = nu.astimezone(tz)
        local_day = now_local.date()
        now_min = now_local.hour * 60 + now_local.minute
        en = (st.locale or "").lower().startswith("en")

        def try_kind(
            kind: str,
            enabled: bool,
            time_str: str,
            title: str,
            body: str,
            *,
            need_rhythm: bool = False,
            need_goal: bool = False,
            route: str = "/today",
        ) -> None:
            if need_rhythm and not sch["notify_rhythm_today"]:
                return
            if need_goal and not sch["notify_goal_nudges"]:
                return
            if not enabled or _already_sent(db, uid, local_day, kind):
                return
            if not _within_window(now_min, _parse_hhmm(time_str)):
                return
            if _in_quiet_hours(now_min, sch["quiet_start"], sch["quiet_end"]):
                counts["blocked_quiet"] += 1
                return
            if _auto_dispatch_count(db, uid, local_day) >= int(sch["max_auto_per_day"]):
                counts["blocked_cap"] += 1
                return
            n = deliver_to_user_devices(
                db,
                user_id=uid,
                title=title,
                body=body,
                data={"route": route, "kind": kind},
            )
            if n > 0:
                _mark_sent(db, uid, local_day, kind)
                counts[kind] += 1

        mt, mb = _copy_rhythm(en=en, phase="morning")
        dt, db_ = _copy_rhythm(en=en, phase="day")
        et, eb = _copy_rhythm(en=en, phase="evening")

        try_kind("morning_rhythm", sch["morning_enabled"], sch["morning_time"], mt, mb, need_rhythm=True)
        try_kind("day_rhythm", sch["day_enabled"], sch["day_time"], dt, db_, need_rhythm=True)
        try_kind("evening_rhythm", sch["evening_enabled"], sch["evening_time"], et, eb, need_rhythm=True)

        week_start = local_day - timedelta(days=local_day.weekday())
        weekly = (
            db.query(db_models.WeeklyGoal)
            .filter(
                db_models.WeeklyGoal.user_id == uid,
                db_models.WeeklyGoal.week_start == week_start,
                db_models.WeeklyGoal.completed.is_(False),
                or_(db_models.WeeklyGoal.scope == "week", db_models.WeeklyGoal.scope.is_(None)),
            )
            .order_by(
                db_models.WeeklyGoal.progress_days.desc(),
                db_models.WeeklyGoal.created_at.asc(),
            )
            .first()
        )
        if not weekly:
            month_start = local_day.replace(day=1)
            weekly = (
                db.query(db_models.WeeklyGoal)
                .filter(
                    db_models.WeeklyGoal.user_id == uid,
                    db_models.WeeklyGoal.week_start == month_start,
                    db_models.WeeklyGoal.scope == "month",
                    db_models.WeeklyGoal.completed.is_(False),
                )
                .order_by(
                    db_models.WeeklyGoal.progress_days.desc(),
                    db_models.WeeklyGoal.created_at.asc(),
                )
                .first()
            )
        if weekly and (weekly.title or "").strip():
            gshort = weekly.title.strip()
            if len(gshort) > 100:
                gshort = gshort[:97] + "..."
            gt_mid, gb_mid = (
                ("Weekly focus", f"One small step on this line: {gshort}")
                if en
                else ("Недельный фокус", f"Один шаг по этой линии: {gshort}")
            )
            gt_aft, gb_aft = (
                ("Still on track?", f"Circle back to your weekly focus: {gshort}")
                if en
                else ("Держишь курс?", f"Вернись к недельному фокусу: {gshort}")
            )
            try_kind(
                "goal_midday",
                sch["goal_midday_enabled"],
                sch["goal_midday_time"],
                gt_mid,
                gb_mid,
                need_goal=True,
                route=f"/tracking/calendar?date={local_day.isoformat()}",
            )
            try_kind(
                "goal_afternoon",
                sch["goal_afternoon_enabled"],
                sch["goal_afternoon_time"],
                gt_aft,
                gb_aft,
                need_goal=True,
                route=f"/tracking/calendar?date={local_day.isoformat()}",
            )

    return counts
