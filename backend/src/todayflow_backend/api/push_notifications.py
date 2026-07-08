"""Register push devices and Today rhythm / goal reminder schedules."""

from __future__ import annotations

import hmac
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from todayflow_backend.api.auth import require_user
from todayflow_backend.core.config import settings
from todayflow_backend.db import models as db_models
from todayflow_backend.db.models import User
from todayflow_backend.db.session import get_session
from todayflow_backend.services.push_delivery import _schedule_row, run_due_notifications

router = APIRouter(prefix="/notifications", tags=["notifications"])
internal_router = APIRouter(prefix="/internal", tags=["internal"])


class PushDeviceRegister(BaseModel):
    platform: str = Field(..., description="ios | android | web")
    token: str = Field(..., min_length=8)
    device_label: Optional[str] = None


class PushDeviceResponse(BaseModel):
    id: int
    platform: str
    device_label: Optional[str] = None

    class Config:
        from_attributes = True


class PushSchedulePayload(BaseModel):
    timezone: Optional[str] = None
    morning_enabled: Optional[bool] = None
    morning_time: Optional[str] = None  # HH:MM local
    day_enabled: Optional[bool] = None
    day_time: Optional[str] = None
    evening_enabled: Optional[bool] = None
    evening_time: Optional[str] = None
    goal_midday_enabled: Optional[bool] = None
    goal_midday_time: Optional[str] = None
    goal_afternoon_enabled: Optional[bool] = None
    goal_afternoon_time: Optional[str] = None
    quiet_start: Optional[str] = None
    quiet_end: Optional[str] = None
    max_auto_per_day: Optional[int] = Field(None, ge=1, le=15)
    notify_rhythm_today: Optional[bool] = None
    notify_goal_nudges: Optional[bool] = None
    notify_goal_ack: Optional[bool] = None
    notify_streak_care: Optional[bool] = None
    notify_weekly_focus: Optional[bool] = None
    notify_tarot_card: Optional[bool] = None
    notify_habit_reminders: Optional[bool] = None
    notify_comeback: Optional[bool] = None


class PushScheduleResponse(BaseModel):
    timezone: str
    morning_enabled: bool
    morning_time: str
    day_enabled: bool
    day_time: str
    evening_enabled: bool
    evening_time: str
    goal_midday_enabled: bool
    goal_midday_time: str
    goal_afternoon_enabled: bool
    goal_afternoon_time: str
    quiet_start: str
    quiet_end: str
    max_auto_per_day: int
    notify_rhythm_today: bool
    notify_goal_nudges: bool
    notify_goal_ack: bool
    notify_streak_care: bool
    notify_weekly_focus: bool
    notify_tarot_card: bool
    notify_habit_reminders: bool
    notify_comeback: bool


def _schedule_to_response(row: db_models.UserPushSchedule) -> PushScheduleResponse:
    sch = _schedule_row(row)
    return PushScheduleResponse(
        timezone=sch["timezone"],
        morning_enabled=sch["morning_enabled"],
        morning_time=sch["morning_time"],
        day_enabled=sch["day_enabled"],
        day_time=sch["day_time"],
        evening_enabled=sch["evening_enabled"],
        evening_time=sch["evening_time"],
        goal_midday_enabled=sch["goal_midday_enabled"],
        goal_midday_time=sch["goal_midday_time"],
        goal_afternoon_enabled=sch["goal_afternoon_enabled"],
        goal_afternoon_time=sch["goal_afternoon_time"],
        quiet_start=sch["quiet_start"],
        quiet_end=sch["quiet_end"],
        max_auto_per_day=sch["max_auto_per_day"],
        notify_rhythm_today=sch["notify_rhythm_today"],
        notify_goal_nudges=sch["notify_goal_nudges"],
        notify_goal_ack=sch["notify_goal_ack"],
        notify_streak_care=sch["notify_streak_care"],
        notify_weekly_focus=sch["notify_weekly_focus"],
        notify_tarot_card=sch["notify_tarot_card"],
        notify_habit_reminders=sch["notify_habit_reminders"],
        notify_comeback=sch["notify_comeback"],
    )


def _default_schedule_row(db: Session, user_id: int) -> db_models.UserPushSchedule:
    row = db_models.UserPushSchedule(user_id=user_id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.post("/devices", response_model=PushDeviceResponse)
def register_push_device(
    payload: PushDeviceRegister,
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    platform = payload.platform.lower().strip()
    if platform not in {"ios", "android", "web"}:
        raise HTTPException(status_code=400, detail="platform must be ios, android, or web")
    existing = (
        db.query(db_models.PushDevice)
        .filter(
            db_models.PushDevice.user_id == user.id,
            db_models.PushDevice.token == payload.token,
        )
        .first()
    )
    if existing:
        existing.platform = platform
        existing.device_label = payload.device_label
        db.commit()
        db.refresh(existing)
        return PushDeviceResponse(id=existing.id, platform=existing.platform, device_label=existing.device_label)
    row = db_models.PushDevice(
        user_id=user.id,
        platform=platform,
        token=payload.token,
        device_label=payload.device_label,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return PushDeviceResponse(id=row.id, platform=row.platform, device_label=row.device_label)


@router.delete("/devices/{device_id}", status_code=204)
def delete_push_device(
    device_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    row = (
        db.query(db_models.PushDevice)
        .filter(db_models.PushDevice.id == device_id, db_models.PushDevice.user_id == user.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Device not found")
    db.delete(row)
    db.commit()
    return None


@router.get("/schedule", response_model=PushScheduleResponse)
def get_push_schedule(
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    row = db.query(db_models.UserPushSchedule).filter(db_models.UserPushSchedule.user_id == user.id).first()
    if not row:
        row = _default_schedule_row(db, user.id)
    return _schedule_to_response(row)


@router.put("/schedule", response_model=PushScheduleResponse)
def update_push_schedule(
    payload: PushSchedulePayload,
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    row = db.query(db_models.UserPushSchedule).filter(db_models.UserPushSchedule.user_id == user.id).first()
    if not row:
        row = db_models.UserPushSchedule(user_id=user.id)
        db.add(row)
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return _schedule_to_response(row)


@internal_router.post("/push/run-due")
def internal_run_due_pushes(
    x_push_dispatch_secret: Optional[str] = Header(None, alias="X-Push-Dispatch-Secret"),
    db: Session = Depends(get_session),
):
    """
    Cron/worker hook: dispatch rhythm + goal nudges. Protect with PUSH_DISPATCH_SECRET.
    """
    secret = settings.push_dispatch_secret
    if not secret or not x_push_dispatch_secret or not hmac.compare_digest(x_push_dispatch_secret, secret):
        raise HTTPException(status_code=404, detail="Not found")
    counts = run_due_notifications(db)
    return {"ok": True, "counts": counts}
