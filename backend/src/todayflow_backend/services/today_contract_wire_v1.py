"""Wire legacy Today inputs → today_contract_v1 for GET /today/contract."""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.api.morning_ritual import MorningRitualResponse
from todayflow_backend.db.models import User
from todayflow_backend.services.day_story_wire_v1 import build_day_story_v1_wire


def build_today_contract_v1_wire(
    db: Session,
    *,
    user: User,
    target_date: date,
    locale: str,
    morning: MorningRitualResponse,
    fusion_dump: dict[str, Any],
    core_profile: dict[str, Any],
) -> dict[str, Any]:
    """Single day_story_v1 LLM (or fallback) → today_contract_v1."""
    contract, _, _ = build_day_story_v1_wire(
        db,
        user=user,
        target_date=target_date,
        locale=locale,
        morning=morning,
        fusion_dump=fusion_dump,
        core_profile=core_profile,
    )
    return contract
