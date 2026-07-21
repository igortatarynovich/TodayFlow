"""Numerology endpoints."""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field

from todayflow_backend.core import models
from todayflow_backend.api.auth import require_user, get_optional_user
from todayflow_backend.i18n import request_locale, translate
from todayflow_backend.services.numerology import (
    NumerologyError,
    NumerologyService,
    get_numerology_service,
)
from todayflow_backend.db.session import get_session
from todayflow_backend.services.core_profile import CoreProfileService, get_core_profile_service
from todayflow_backend.services.interpretation_orchestrator import (
    InterpretationOrchestrator,
    get_interpretation_orchestrator,
)

router = APIRouter(prefix="/numerology", tags=["numerology"])


class NumerologyPayload(BaseModel):
    full_name: str
    birth_date: str


class LifePathPayload(BaseModel):
    birth_date: str


class BirthdayNumberPayload(BaseModel):
    birth_day: int = Field(..., ge=1, le=31)


class PersonalYearPayload(BaseModel):
    birth_day: int = Field(..., ge=1, le=31)
    birth_month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=1900, le=2100)


@router.get("/master-numbers")
def master_numbers(service: NumerologyService = Depends(get_numerology_service)) -> list[int]:
    """Единый источник master numbers [11, 22, 33]. UI подтягивает отсюда."""
    return sorted(service.master_numbers)


@router.post("/life-path", response_model=models.NumerologyCalcResult)
def life_path(
    payload: LifePathPayload,
    request: Request,
    service: NumerologyService = Depends(get_numerology_service),
) -> models.NumerologyCalcResult:
    locale = request_locale(request)
    try:
        return service.life_path_calc(payload.birth_date)
    except NumerologyError as exc:
        detail = translate(f"numerology.errors.{exc.code}", locale=locale, default=str(exc))
        raise HTTPException(status_code=400, detail=detail) from exc


@router.post("/birthday-number", response_model=models.NumerologyCalcResult)
def birthday_number(
    payload: BirthdayNumberPayload,
    request: Request,
    service: NumerologyService = Depends(get_numerology_service),
) -> models.NumerologyCalcResult:
    try:
        return service.birthday_number_calc(payload.birth_day)
    except NumerologyError as exc:
        locale = request_locale(request)
        detail = translate(f"numerology.errors.{exc.code}", locale=locale, default=str(exc))
        raise HTTPException(status_code=400, detail=detail) from exc


@router.post("/personal-year", response_model=models.NumerologyCalcResult)
def personal_year(
    payload: PersonalYearPayload,
    request: Request,
    service: NumerologyService = Depends(get_numerology_service),
) -> models.NumerologyCalcResult:
    try:
        return service.personal_year_calc(payload.birth_day, payload.birth_month, payload.year)
    except NumerologyError as exc:
        locale = request_locale(request)
        detail = translate(f"numerology.errors.{exc.code}", locale=locale, default=str(exc))
        raise HTTPException(status_code=400, detail=detail) from exc


@router.post("/name", response_model=models.NumerologyProfile)
def compute_name_profile(
    payload: NumerologyPayload,
    request: Request,
    user=Depends(get_optional_user),
    service: NumerologyService = Depends(get_numerology_service),
) -> models.NumerologyProfile:
    locale = request_locale(request)
    try:
        profile = service.compute_profile(payload.full_name, payload.birth_date, locale=locale)
        if user:
            service.save_profile(user.id, profile, locale=locale)
            from todayflow_backend.api.today import invalidate_morning_cache_for_user

            invalidate_morning_cache_for_user(user.id)
        return profile
    except NumerologyError as exc:
        detail = translate(f"numerology.errors.{exc.code}", locale=locale, default=str(exc))
        raise HTTPException(status_code=400, detail=detail) from exc


@router.get("/history", response_model=list[models.NumerologyProfile])
def numerology_history(
    user=Depends(require_user),
    service: NumerologyService = Depends(get_numerology_service),
) -> list[models.NumerologyProfile]:
    return service.list_profiles(user.id)


@router.get("/daily", response_model=models.NumerologyDailyInsight)
def numerology_daily(
    request: Request,
    service: NumerologyService = Depends(get_numerology_service),
    user=Depends(get_optional_user),
    db=Depends(get_session),
) -> models.NumerologyDailyInsight:
    """Module GET — gated via unified SoT when authenticated; else always not_selected."""
    from todayflow_backend.services import day_symbol_state_v1 as day_symbols

    _ = service
    day = day_symbols.resolve_local_date(local_date=None, timezone_name="UTC")
    if user is None:
        return models.NumerologyDailyInsight(
            date=day.isoformat(), selection_status="not_selected", number=None
        )
    row = day_symbols.get_state_row(
        db, owner_key=day_symbols.owner_key_for_user(user.id), local_date=day
    )
    view = day_symbols.public_view(row, local_date=day, timezone_name="UTC")
    num = view.get("number") or {}
    if not num.get("revealed"):
        return models.NumerologyDailyInsight(
            date=day.isoformat(), selection_status="not_selected", number=None
        )
    return models.NumerologyDailyInsight(
        date=day.isoformat(),
        selection_status="selected",
        number=models.NumerologyNumber(
            title=str(num.get("title") or ""),
            value=int(num.get("value") or num.get("reduced_value") or 0),
            reduced_value=int(num.get("reduced_value") or 0),
            is_master=bool(num.get("is_master")),
            summary=str(num.get("summary") or ""),
        ),
    )


class NumerologyDailyRevealPayload(BaseModel):
    local_date: str | None = None
    timezone: str = "UTC"
    reveal_source: str = "numerology_module"
    idempotency_key: str | None = None


@router.post("/daily/reveal", response_model=models.NumerologyDailyInsight)
def numerology_daily_reveal(
    request: Request,
    payload: NumerologyDailyRevealPayload | None = None,
    service: NumerologyService = Depends(get_numerology_service),
    user=Depends(get_optional_user),
    db=Depends(get_session),
    x_guest_session_id: Optional[str] = Header(default=None, alias="X-Guest-Session-Id"),
) -> models.NumerologyDailyInsight:
    """Explicit reveal — persists in unified day symbol SoT (auth or guest session)."""
    from todayflow_backend.services import day_symbol_state_v1 as day_symbols

    _ = request_locale(request)
    body = payload or NumerologyDailyRevealPayload()
    source = (body.reveal_source or "").strip().lower()
    if source not in {"today", "today_ritual", "morning_ritual", "day_ritual", "ritual"}:
        raise HTTPException(
            status_code=403,
            detail="day_number_only_in_today",
        )
    day = day_symbols.resolve_local_date(local_date=body.local_date, timezone_name=body.timezone)
    guest_id = (x_guest_session_id or "").strip()
    if user is not None:
        owner_key = day_symbols.owner_key_for_user(user.id)
        user_id = int(user.id)
        guest_session_id = None
        key = (body.idempotency_key or f"numerology_module:{user.id}:{day.isoformat()}").strip()
    elif guest_id:
        try:
            owner_key = day_symbols.owner_key_for_guest(guest_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        user_id = None
        guest_session_id = guest_id
        key = (body.idempotency_key or f"numerology_module:g:{guest_id}:{day.isoformat()}").strip()
    else:
        raise HTTPException(status_code=401, detail="auth_or_guest_session_required")
    view = day_symbols.reveal_number(
        db,
        owner_key=owner_key,
        local_date=day,
        timezone_name=body.timezone,
        reveal_source=body.reveal_source,
        idempotency_key=key,
        user_id=user_id,
        guest_session_id=guest_session_id,
        numerology_service=service,
    )
    num = view.get("number") or {}
    return models.NumerologyDailyInsight(
        date=day.isoformat(),
        selection_status="selected",
        number=models.NumerologyNumber(
            title=str(num.get("title") or ""),
            value=int(num.get("value") or num.get("reduced_value") or 0),
            reduced_value=int(num.get("reduced_value") or 0),
            is_master=bool(num.get("is_master")),
            summary=str(num.get("summary") or ""),
        ),
    )


@router.get("/daily/explain", response_model=dict)
def explain_daily_numerology(
    request: Request,
    date: Optional[str] = None,
    user=Depends(require_user),
    db=Depends(get_session),
    service: NumerologyService = Depends(get_numerology_service),
    core_profile_service: CoreProfileService = Depends(get_core_profile_service),
    orchestrator: InterpretationOrchestrator = Depends(get_interpretation_orchestrator),
) -> dict:
    """
    Объясняет число дня через призму натальной карты пользователя.
    Только после reveal в unified day symbol SoT.
    """
    from datetime import date as date_class

    from todayflow_backend.services import day_symbol_state_v1 as day_symbols

    target_date = date or date_class.today().isoformat()
    target_date_obj = date_class.fromisoformat(target_date) if isinstance(target_date, str) else target_date

    row = day_symbols.get_state_row(
        db,
        owner_key=day_symbols.owner_key_for_user(user.id),
        local_date=target_date_obj,
    )
    if not day_symbols.is_number_revealed(row):
        raise HTTPException(status_code=409, detail="number_not_revealed")

    daily_insight = service.daily_number(
        reference_date=target_date_obj, locale=request_locale(request), reveal=True
    )

    if not daily_insight or not daily_insight.number:
        raise HTTPException(status_code=404, detail="Число дня не найдено")

    from todayflow_backend.core.numerology_explainer import explain_numerology_number

    explanation = explain_numerology_number(
        user=user,
        db=db,
        number=row.number_reduced
        if row is not None and row.number_reduced is not None
        else (daily_insight.number.value or daily_insight.number.reduced_value),
        number_type="day",
        target_date=target_date,
    )
    core_profile = core_profile_service.build(db, user)
    consistency = orchestrator.build_daily_guidance(
        core_profile=core_profile,
        numerology={"dayNumber": daily_insight.number.value or daily_insight.number.reduced_value},
        needs=None,
    )
    
    return {
        "number": {
            "value": daily_insight.number.value,
            "reduced_value": daily_insight.number.reduced_value,
            "title": daily_insight.number.title,
            "summary": daily_insight.number.summary,
        },
        "explanation": explanation,
        "date": target_date,
        "core_profile": core_profile,
        "consistency": consistency,
    }
