"""Guest-safe natal_facts Generation Contract endpoint."""

from __future__ import annotations

from datetime import date, time
from typing import Any, Literal, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from todayflow_backend.core.rate_limit import limiter
from todayflow_backend.i18n import request_locale
from todayflow_backend.services.natal_facts_contract_v1 import (
    build_available_input,
    generate_natal_facts,
)

router = APIRouter(prefix="/profile", tags=["natal-facts"])

AccessHint = Literal["guest", "free", "trial", "paid"]


class NatalFactsRequest(BaseModel):
    birth_date: date
    birth_time: Optional[time] = None
    time_unknown: bool = True
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone_name: Optional[str] = None
    display_name: Optional[str] = None
    # Capability access for slot gates; full /profile remains auth-gated elsewhere.
    access: Optional[AccessHint] = Field(
        default=None,
        description="guest|free|trial|paid — defaults to free for natal preview",
    )


class NatalFactsResponse(BaseModel):
    available_input: dict[str, Any]
    natal_facts: dict[str, Any]
    capability: dict[str, Any]


@router.post("/natal-facts", response_model=NatalFactsResponse)
@limiter.limit("20/minute")
def post_natal_facts(request: Request, payload: NatalFactsRequest) -> NatalFactsResponse:
    """Compute NatalChartFacts via LLM contract (guest-safe, rate-limited)."""
    locale = request_locale(request)
    access: AccessHint = payload.access or "free"

    available = build_available_input(
        birth_date=payload.birth_date,
        birth_time=payload.birth_time,
        time_unknown=payload.time_unknown,
        location_name=payload.location_name,
        latitude=payload.latitude,
        longitude=payload.longitude,
        timezone_name=payload.timezone_name,
        display_name=payload.display_name,
        access=access,
    )
    capability = available.pop("_capability", {}) or {}
    try:
        facts = generate_natal_facts(
            available_input=available,
            locale=locale,
            capability=capability,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    cap_out = facts.get("capability") if isinstance(facts.get("capability"), dict) else capability
    return NatalFactsResponse(
        available_input=available,
        natal_facts=facts,
        capability=cap_out,
    )
