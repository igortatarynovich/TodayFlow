"""Guest session progress sync + protected full claim API."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from todayflow_backend.api.auth import require_user
from todayflow_backend.db.session import get_session
from todayflow_backend.services import day_symbol_state_v1 as symbols
from todayflow_backend.services import guest_claim_v1 as guest_claim

router = APIRouter(prefix="/today/guest", tags=["today-guest"])


class GuestSessionEnsurePayload(BaseModel):
    guest_session_id: Optional[str] = None
    locale: Optional[str] = "ru"
    timezone: Optional[str] = "UTC"


class GuestProgressPayload(BaseModel):
    local_date: Optional[str] = None
    timezone: str = "UTC"
    locale: str = "ru"
    mood: Optional[dict[str, Any]] = None
    goals: Optional[dict[str, Any]] = None
    onboarding: Optional[dict[str, Any]] = None
    first_result: Optional[dict[str, Any]] = None
    ritual: Optional[dict[str, Any]] = None
    today_state: Optional[dict[str, Any]] = None
    day_story: Optional[dict[str, Any]] = None
    story_fingerprint: Optional[str] = None
    story_status: Optional[str] = None
    profile_draft: Optional[dict[str, Any]] = None


class GuestClaimTokenPayload(BaseModel):
    pass


class GuestClaimPayload(BaseModel):
    claim_token: str = Field(..., min_length=16, max_length=256)
    local_date: Optional[str] = None
    redirect_target: str = "/today?first=1"


def _map_guest_error(exc: ValueError) -> HTTPException:
    code = str(exc)
    status = {
        "guest_auth_required": 401,
        "unknown_guest_session": 404,
        "invalid_guest_secret": 401,
        "guest_session_sealed": 409,
        "claim_token_required": 400,
        "invalid_claim_token": 401,
        "claim_token_expired": 401,
        "guest_session_already_claimed": 409,
        "invalid_guest_session_id": 400,
    }.get(code, 400)
    return HTTPException(status_code=status, detail=code)


@router.post("/session")
def ensure_session(
    payload: GuestSessionEnsurePayload | None = None,
    db: Session = Depends(get_session),
) -> dict:
    body = payload or GuestSessionEnsurePayload()
    try:
        return guest_claim.ensure_guest_session(
            db,
            guest_session_id=body.guest_session_id,
            locale=body.locale,
            timezone_name=body.timezone,
        )
    except ValueError as exc:
        raise _map_guest_error(exc) from exc


@router.put("/progress")
def put_progress(
    payload: GuestProgressPayload,
    db: Session = Depends(get_session),
    x_guest_session_id: Optional[str] = Header(default=None, alias="X-Guest-Session-Id"),
    x_guest_session_secret: Optional[str] = Header(default=None, alias="X-Guest-Session-Secret"),
) -> dict:
    try:
        day = symbols.resolve_local_date(
            local_date=payload.local_date, timezone_name=payload.timezone
        )
        return guest_claim.upsert_guest_progress(
            db,
            guest_session_id=x_guest_session_id or "",
            session_secret=x_guest_session_secret or "",
            local_date=day,
            timezone_name=payload.timezone,
            locale=payload.locale,
            mood=payload.mood,
            goals=payload.goals,
            onboarding=payload.onboarding,
            first_result=payload.first_result,
            ritual=payload.ritual,
            today_state=payload.today_state,
            day_story=payload.day_story,
            story_fingerprint=payload.story_fingerprint,
            story_status=payload.story_status,
            profile_draft=payload.profile_draft,
        )
    except ValueError as exc:
        raise _map_guest_error(exc) from exc


@router.post("/claim-token")
def create_claim_token(
    payload: GuestClaimTokenPayload | None = None,
    db: Session = Depends(get_session),
    x_guest_session_id: Optional[str] = Header(default=None, alias="X-Guest-Session-Id"),
    x_guest_session_secret: Optional[str] = Header(default=None, alias="X-Guest-Session-Secret"),
) -> dict:
    _ = payload
    try:
        return guest_claim.issue_claim_token(
            db,
            guest_session_id=x_guest_session_id or "",
            session_secret=x_guest_session_secret or "",
        )
    except ValueError as exc:
        raise _map_guest_error(exc) from exc


@router.post("/claim")
def claim_guest(
    payload: GuestClaimPayload,
    db: Session = Depends(get_session),
    user=Depends(require_user),
) -> dict:
    """Atomic full claim — body contains only claim_token (+ optional local_date/redirect)."""
    day = None
    if payload.local_date:
        day = symbols.resolve_local_date(local_date=payload.local_date, timezone_name="UTC")
    try:
        return guest_claim.claim_guest_session_to_user(
            db,
            claim_token=payload.claim_token,
            user_id=int(user.id),
            local_date=day,
            redirect_target=payload.redirect_target or "/today?first=1",
        )
    except ValueError as exc:
        raise _map_guest_error(exc) from exc
