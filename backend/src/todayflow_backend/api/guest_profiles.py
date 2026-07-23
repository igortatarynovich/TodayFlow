"""Guest durable profiles API (pre-account SoT)."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from todayflow_backend.db.session import get_session
from todayflow_backend.services import guest_profiles_v1 as guest_profiles

router = APIRouter(prefix="/guest", tags=["guest-profiles"])


class GuestProfileUpsertPayload(BaseModel):
    local_key: str = Field(..., min_length=1, max_length=32)
    display_name: Optional[str] = None
    birth_date: str
    birth_time: Optional[str] = None
    birth_time_known: Optional[bool] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone_name: Optional[str] = None
    relation: Optional[str] = None
    is_owner_candidate: Optional[bool] = None
    natal_facts: Optional[dict[str, Any]] = None


class CompatPersonPayload(BaseModel):
    label: Optional[str] = None
    display_name: Optional[str] = None
    birth_date: str
    birth_time: Optional[str] = None
    time_unknown: bool = True
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone_name: Optional[str] = None
    natal_facts: Optional[dict[str, Any]] = None


class CompatPairPayload(BaseModel):
    person_a: CompatPersonPayload
    person_b: CompatPersonPayload


def _map_error(exc: ValueError) -> HTTPException:
    code = str(exc)
    status = {
        "guest_auth_required": 401,
        "unknown_guest_session": 404,
        "invalid_guest_secret": 401,
        "guest_session_sealed": 409,
        "birth_date_required": 400,
        "invalid_local_key": 400,
    }.get(code, 400)
    return HTTPException(status_code=status, detail=code)


@router.post("/profiles")
def upsert_profile(
    payload: GuestProfileUpsertPayload,
    db: Session = Depends(get_session),
    x_guest_session_id: Optional[str] = Header(default=None, alias="X-Guest-Session-Id"),
    x_guest_session_secret: Optional[str] = Header(default=None, alias="X-Guest-Session-Secret"),
) -> dict:
    try:
        return guest_profiles.upsert_guest_profile(
            db,
            guest_session_id=x_guest_session_id or "",
            session_secret=x_guest_session_secret or "",
            local_key=payload.local_key,
            display_name=payload.display_name,
            birth_date=payload.birth_date,
            birth_time=payload.birth_time,
            birth_time_known=payload.birth_time_known,
            location_name=payload.location_name,
            latitude=payload.latitude,
            longitude=payload.longitude,
            timezone_name=payload.timezone_name,
            relation=payload.relation,
            is_owner_candidate=payload.is_owner_candidate,
            natal_facts=payload.natal_facts,
        )
    except ValueError as exc:
        raise _map_error(exc) from exc


@router.get("/profiles")
def get_profiles(
    db: Session = Depends(get_session),
    x_guest_session_id: Optional[str] = Header(default=None, alias="X-Guest-Session-Id"),
    x_guest_session_secret: Optional[str] = Header(default=None, alias="X-Guest-Session-Secret"),
) -> dict:
    try:
        return guest_profiles.list_guest_profiles(
            db,
            guest_session_id=x_guest_session_id or "",
            session_secret=x_guest_session_secret or "",
        )
    except ValueError as exc:
        raise _map_error(exc) from exc


@router.post("/profiles/compat-pair")
def upsert_compat_pair(
    payload: CompatPairPayload,
    db: Session = Depends(get_session),
    x_guest_session_id: Optional[str] = Header(default=None, alias="X-Guest-Session-Id"),
    x_guest_session_secret: Optional[str] = Header(default=None, alias="X-Guest-Session-Secret"),
) -> dict:
    try:
        return guest_profiles.upsert_compat_pair(
            db,
            guest_session_id=x_guest_session_id or "",
            session_secret=x_guest_session_secret or "",
            person_a=payload.person_a.model_dump(),
            person_b=payload.person_b.model_dump(),
        )
    except ValueError as exc:
        raise _map_error(exc) from exc
