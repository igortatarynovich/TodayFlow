"""Unified day symbol reveal API (card + number) — single server SoT."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from todayflow_backend.api.auth import get_optional_user, require_user
from todayflow_backend.db.session import get_session
from todayflow_backend.services import day_symbol_state_v1 as symbols

router = APIRouter(prefix="/today/symbols", tags=["today-symbols"])


class CardRevealPayload(BaseModel):
    card_id: int = Field(..., ge=0, le=78)
    orientation: str = "upright"
    local_date: Optional[str] = None
    timezone: str = "UTC"
    reveal_source: str = "ritual"
    idempotency_key: str = Field(..., min_length=8, max_length=128)


class NumberRevealPayload(BaseModel):
    local_date: Optional[str] = None
    timezone: str = "UTC"
    reveal_source: str = "ritual"
    idempotency_key: str = Field(..., min_length=8, max_length=128)


class GuestClaimPayload(BaseModel):
    guest_session_id: str = Field(..., min_length=8, max_length=64)
    local_date: Optional[str] = None


def _owner_from_request(
    user,
    guest_session_id: str | None,
    *,
    db: Session | None = None,
    mutate: bool = False,
) -> tuple[str, int | None, str | None]:
    if user is not None:
        return symbols.owner_key_for_user(user.id), int(user.id), None
    gid = (guest_session_id or "").strip()
    if not gid:
        raise HTTPException(status_code=401, detail="auth_or_guest_session_required")
    if mutate and db is not None:
        from todayflow_backend.services.guest_claim_v1 import guest_session_is_mutable

        if not guest_session_is_mutable(db, gid):
            raise HTTPException(status_code=409, detail="guest_session_sealed")
    try:
        return symbols.owner_key_for_guest(gid), None, gid
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/state")
def get_symbol_state(
    request: Request,
    local_date: Optional[str] = None,
    timezone: str = "UTC",
    db: Session = Depends(get_session),
    user=Depends(get_optional_user),
    x_guest_session_id: Optional[str] = Header(default=None, alias="X-Guest-Session-Id"),
) -> dict:
    """Read-only. Never creates or reveals."""
    _ = request
    owner_key, _, _ = _owner_from_request(user, x_guest_session_id)
    day = symbols.resolve_local_date(local_date=local_date, timezone_name=timezone)
    row = symbols.get_state_row(db, owner_key=owner_key, local_date=day)
    return symbols.public_view(row, local_date=day, timezone_name=timezone)


def _with_story_refresh_meta(
    db,
    *,
    view: dict,
    owner_key: str,
    local_date,
    timezone_name: str,
    user_id: int | None,
    guest_id: str | None,
) -> dict:
    from todayflow_backend.services import day_story_refresh_v1 as story_refresh

    if user_id is not None:
        try:
            from todayflow_backend.api.today import invalidate_morning_cache_for_user

            invalidate_morning_cache_for_user(user_id)
        except Exception:
            pass
    meta = story_refresh.mark_day_story_stale_after_input_change(
        db,
        owner_key=owner_key,
        local_date=local_date,
        timezone_name=timezone_name,
        locale="ru",
        user_id=user_id,
        guest_session_id=guest_id,
    )
    return story_refresh.attach_story_refresh_meta(view, meta)


@router.post("/card/reveal")
def reveal_card_symbol(
    payload: CardRevealPayload,
    db: Session = Depends(get_session),
    user=Depends(get_optional_user),
    x_guest_session_id: Optional[str] = Header(default=None, alias="X-Guest-Session-Id"),
) -> dict:
    owner_key, user_id, guest_id = _owner_from_request(
        user, x_guest_session_id, db=db, mutate=True
    )
    day = symbols.resolve_local_date(local_date=payload.local_date, timezone_name=payload.timezone)
    try:
        view = symbols.reveal_card(
            db,
            owner_key=owner_key,
            local_date=day,
            timezone_name=payload.timezone,
            card_id=payload.card_id,
            orientation=payload.orientation,
            reveal_source=payload.reveal_source,
            idempotency_key=payload.idempotency_key,
            user_id=user_id,
            guest_session_id=guest_id,
        )
    except ValueError as exc:
        code = str(exc)
        status = 400 if code != "unknown_tarot_card" else 404
        raise HTTPException(status_code=status, detail=code) from exc
    return _with_story_refresh_meta(
        db,
        view=view,
        owner_key=owner_key,
        local_date=day,
        timezone_name=payload.timezone,
        user_id=user_id,
        guest_id=guest_id,
    )


@router.post("/number/reveal")
def reveal_number_symbol(
    payload: NumberRevealPayload,
    db: Session = Depends(get_session),
    user=Depends(get_optional_user),
    x_guest_session_id: Optional[str] = Header(default=None, alias="X-Guest-Session-Id"),
) -> dict:
    owner_key, user_id, guest_id = _owner_from_request(
        user, x_guest_session_id, db=db, mutate=True
    )
    day = symbols.resolve_local_date(local_date=payload.local_date, timezone_name=payload.timezone)
    try:
        view = symbols.reveal_number(
            db,
            owner_key=owner_key,
            local_date=day,
            timezone_name=payload.timezone,
            reveal_source=payload.reveal_source,
            idempotency_key=payload.idempotency_key,
            user_id=user_id,
            guest_session_id=guest_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _with_story_refresh_meta(
        db,
        view=view,
        owner_key=owner_key,
        local_date=day,
        timezone_name=payload.timezone,
        user_id=user_id,
        guest_id=guest_id,
    )


@router.post("/claim")
def claim_guest_symbols(
    payload: GuestClaimPayload,
    db: Session = Depends(get_session),
    user=Depends(require_user),
) -> dict:
    """Transfer guest symbol reveals into the authenticated user (idempotent)."""
    from todayflow_backend.services import day_story_refresh_v1 as story_refresh

    day = None
    if payload.local_date:
        day = symbols.resolve_local_date(local_date=payload.local_date, timezone_name="UTC")
    try:
        result = symbols.claim_guest_symbols_to_user(
            db,
            guest_session_id=payload.guest_session_id,
            user_id=int(user.id),
            local_date=day,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    claim_day = day or symbols.resolve_local_date(local_date=None, timezone_name="UTC")
    meta = story_refresh.mark_day_story_stale_after_input_change(
        db,
        owner_key=symbols.owner_key_for_user(int(user.id)),
        local_date=claim_day,
        timezone_name="UTC",
        locale="ru",
        user_id=int(user.id),
    )
    result = dict(result)
    result.update(meta)
    return result
