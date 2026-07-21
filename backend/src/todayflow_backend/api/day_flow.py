"""API для связки дня: Прогноз → Аффирмации → Практики → Подсказки."""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from todayflow_backend.api.auth import require_user, get_optional_user
from todayflow_backend.db.models import User
from todayflow_backend.db.session import get_session
from todayflow_backend.i18n import request_locale
from todayflow_backend.core.affirmation_generator import generate_affirmations
from todayflow_backend.services.numerology import NumerologyService, get_numerology_service
from todayflow_backend.core.numerology_explainer import explain_numerology_number
from todayflow_backend.services.core_profile import get_core_profile_service
from todayflow_backend.services.interpretation_orchestrator import get_interpretation_orchestrator

router = APIRouter(prefix="/day-flow", tags=["day-flow"])


class DayFlowResponse(BaseModel):
    """Ответ со связкой дня."""
    date: str
    affirmations: list
    practice: Optional[dict] = None
    numerology: Optional[dict] = None
    tarot_card: Optional[dict] = None
    core_profile: Optional[dict] = None
    consistency: Optional[dict] = None


@router.get("/", response_model=DayFlowResponse)
async def get_day_flow(
    request: Request,
    target_date: Optional[str] = None,
    needs: Optional[str] = None,  # Потребности: "money", "love", "calm", "work", "health"
    fast: bool = True,
    user: Optional[User] = Depends(get_optional_user),
    db=Depends(get_session),
) -> DayFlowResponse:
    """
    Получает связку дня: Прогноз → Аффирмации → Практики → Подсказки.
    Если пользователь авторизован — персонализирует через натальную карту.
    """
    if not target_date:
        target_date = date.today().isoformat()
    
    target_date_obj = date.fromisoformat(target_date) if isinstance(target_date, str) else target_date
    locale = request_locale(request)
    
    # Аффирмации: персонализированные через ИИ, если пользователь авторизован
    affirmations = []
    core_profile = None
    consistency = None

    if user:
        try:
            core_profile_service = get_core_profile_service()
            core_profile = core_profile_service.build_cached_or_baseline(db, user)
        except Exception:
            core_profile = None

    if user and not fast:
        try:
            generated = generate_affirmations(
                user=user,
                db=db,
                needs=needs or "general",
                target_date=target_date,
                count=3
            )
            if generated:
                affirmations = [{"id": f"generated_{i}", "text": aff} for i, aff in enumerate(generated)]
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to generate personalized affirmations: {e}", exc_info=True)
    
    # По умолчанию и в fast-режиме используем редакционные аффирмации.
    if not affirmations:
        try:
            from todayflow_backend.core.content_loader import load_affirmations
            all_affirmations = load_affirmations(locale=locale)
            if needs:
                # Фильтруем по тегам, если указаны потребности
                filtered = [a for a in all_affirmations if needs.lower() in (a.get("tags", []) or [])]
                affirmations = filtered[:3] if filtered else all_affirmations[:3]
            else:
                affirmations = all_affirmations[:3]
        except Exception:
            affirmations = []
    
    # Практика: получаем текущую рекомендованную практику (только для авторизованных)
    practice = None
    if user:
        try:
            # Используем прямой вызов логики из practices.py
            from todayflow_backend.api.practices import GENERAL_PRACTICES, PERSONALIZED_PRACTICES
            import random
            
            # Выбираем случайную практику из общих или персонализированных
            all_practices = GENERAL_PRACTICES + PERSONALIZED_PRACTICES
            if all_practices:
                selected = random.choice(all_practices)
                practice = {
                    "id": selected.get("id"),
                    "title": selected.get("name") or selected.get("title"),
                    "description": selected.get("description"),
                    "duration_minutes": selected.get("duration_minutes"),
                    "is_personalized": selected in PERSONALIZED_PRACTICES,
                }
        except Exception:
            pass
    
    # Нумерология дня с объяснением через натальную карту
    numerology = None
    numerology_service = get_numerology_service()
    try:
        # Module-adjacent day-flow must not spoil day number before ritual reveal.
        daily_insight = numerology_service.daily_number(
            reference_date=target_date_obj, locale=locale, reveal=False
        )
        if daily_insight and daily_insight.number:
            numerology = {
                "dayNumber": daily_insight.number.value or daily_insight.number.reduced_value,
                "title": daily_insight.number.title,
                "summary": daily_insight.number.summary,
            }
            
            # Добавляем объяснение через натальную карту, если пользователь авторизован
            if user:
                try:
                    explanation = explain_numerology_number(
                        user=user,
                        db=db,
                        number=daily_insight.number.value or daily_insight.number.reduced_value,
                        number_type="day",
                        target_date=target_date
                    )
                    if explanation:
                        numerology.update({
                            "meaning": explanation.get("meaning"),
                            "whatToDo": explanation.get("what_to_do"),
                            "whatToAvoid": explanation.get("what_to_avoid"),
                            "possibleEvents": explanation.get("possible_events"),
                            "howDayLooks": explanation.get("how_day_looks"),
                        })
                except Exception:
                    pass
    except Exception:
        pass
    
    # Карта таро дня (опционально)
    tarot_card = None
    if user:
        try:
            from todayflow_backend.services.tarot import TarotService
            tarot_service = TarotService()
            # Do not assign/spoil card-of-day via day-flow; only return if already revealed.
            daily_draw = tarot_service.get_daily_draw(
                user, locale=locale, assign_if_missing=False
            )
            if (
                daily_draw
                and daily_draw.selection_status == "selected"
                and daily_draw.card
            ):
                tarot_card = {
                    "name": daily_draw.card.name,
                    "orientation": daily_draw.orientation,
                }
        except Exception:
            pass

    if user:
        try:
            orchestrator = get_interpretation_orchestrator()
            consistency = orchestrator.build_daily_guidance(
                core_profile=core_profile,
                numerology=numerology,
                needs=needs,
            )
        except Exception:
            consistency = None
    
    return DayFlowResponse(
        date=target_date,
        affirmations=affirmations,
        practice=practice,
        numerology=numerology,
        tarot_card=tarot_card,
        core_profile=core_profile,
        consistency=consistency,
    )
