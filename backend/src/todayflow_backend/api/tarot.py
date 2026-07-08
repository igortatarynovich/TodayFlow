"""Tarot Flow endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel

from todayflow_backend.api.auth import require_user
from todayflow_backend.core import models
from todayflow_backend.i18n import request_locale
from todayflow_backend.services.tarot import TarotService, get_tarot_service
from todayflow_backend.db.session import get_session
from todayflow_backend.services.core_profile import CoreProfileService, get_core_profile_service
from todayflow_backend.services.interpretation_orchestrator import (
    InterpretationOrchestrator,
    get_interpretation_orchestrator,
)
from todayflow_backend.services.learning import get_learning_service
from todayflow_backend.services.tarot_answer_v1 import compose_tarot_answer_v1, TAROT_ANSWER_V1_CONTRACT

router = APIRouter(prefix="/tarot", tags=["tarot"])


class TarotSpreadContextResponse(BaseModel):
    spread: models.TarotSpreadResult
    core_profile: dict
    consistency: dict
    reading: models.TarotSpreadReading
    tarot_answer_v1: dict | None = None
    generation_log_id: int | None = None


def _spread_needs(spread_id: str | None, concern_domain: str | None) -> str:
    domain = (concern_domain or "").strip().lower()
    domain_map = {
        "relationships": "love",
        "work": "work",
        "money": "money",
        "family": "family",
        "decision": "general",
        "conflict": "general",
        "inner_state": "general",
        "growth": "general",
    }
    if domain in domain_map:
        return domain_map[domain]
    sid = (spread_id or "").strip().lower()
    spread_map = {
        "one_card": "general",
        "three_cards": "general",
        "guidance_relationship_five": "love",
        "guidance_sexual_five": "love",
        "relationship_mirror": "love",
        "guidance_work_money": "money",
        "career_compass": "work",
        "guidance_choice_two": "general",
        "guidance_yes_no": "general",
        "guidance_inner_conflict": "general",
        "love": "love",
        "career": "work",
        "money": "money",
        "family": "family",
    }
    return spread_map.get(sid, "general")


@router.get("/daily/public", response_model=models.TarotDailyDraw)
async def get_public_daily_tarot_draw(
    request: Request,
    tarot_service: TarotService = Depends(get_tarot_service),
) -> models.TarotDailyDraw:
    """Return general daily card/mantra/ritual combo (not personalized, for public access)."""
    from datetime import date
    from todayflow_backend.db.models import User
    
    # Create a temporary user with fixed ID for deterministic public draws
    public_user = User(id=0, email="public@todayflow.app")
    return tarot_service.get_daily_draw(public_user, locale=request_locale(request))


@router.get("/cards/{card_id}", response_model=models.TarotCard)
async def get_tarot_card_by_id(
    request: Request,
    card_id: int,
    tarot_service: TarotService = Depends(get_tarot_service),
) -> models.TarotCard:
    """Major arcana card reference (public, same source as spreads and daily draw)."""
    card = tarot_service.get_card_by_id(card_id, locale=request_locale(request))
    if card is None:
        raise HTTPException(status_code=404, detail="unknown_tarot_card")
    return card


@router.get("/daily", response_model=models.TarotDailyDraw)
async def get_daily_tarot_draw(
    request: Request,
    tarot_service: TarotService = Depends(get_tarot_service),
    user=Depends(require_user),
) -> models.TarotDailyDraw:
    """Return the deterministic card/mantra/ritual combo for today."""
    return tarot_service.get_daily_draw(user, locale=request_locale(request))


@router.get("/daily/explain", response_model=dict)
async def explain_daily_tarot_card(
    request: Request,
    date: Optional[str] = None,
    user=Depends(require_user),
    db=Depends(get_session),
) -> dict:
    """
    Объясняет карту таро дня через призму натальной карты пользователя.
    Возвращает: что делать, чего избегать, какие события могут произойти и почему.
    """
    from datetime import date as date_class
    from todayflow_backend.core.tarot_explainer import explain_tarot_card
    from todayflow_backend.services.tarot import get_tarot_service
    
    target_date = date or date_class.today().isoformat()
    
    # Получаем карту дня
    tarot_service = get_tarot_service()
    daily_draw = tarot_service.get_daily_draw(user, locale=request_locale(request))
    
    if not daily_draw or not daily_draw.card:
        raise HTTPException(status_code=404, detail="Карта дня не найдена")
    
    # Объясняем через ИИ
    explanation = explain_tarot_card(
        user=user,
        db=db,
        card_name=daily_draw.card.name,
        orientation=daily_draw.card.orientation or "upright",
        target_date=target_date
    )
    
    return {
        "card": {
            "name": daily_draw.card.name,
            "orientation": daily_draw.card.orientation,
        },
        "explanation": explanation,
        "date": target_date
    }


@router.get("/history", response_model=models.TarotHistoryResponse)
async def get_tarot_history(
    request: Request,
    tarot_service: TarotService = Depends(get_tarot_service),
    user=Depends(require_user),
) -> models.TarotHistoryResponse:
    """Return the latest draws plus current streak metadata."""
    return tarot_service.get_history(user, locale=request_locale(request))


@router.post("/spread", response_model=models.TarotSpreadResult)
async def generate_tarot_spread(
    request: Request,
    payload: models.TarotSpreadRequest = models.TarotSpreadRequest(),
    tarot_service: TarotService = Depends(get_tarot_service),
    user=Depends(require_user),
) -> models.TarotSpreadResult:
    """Generate a multi-card spread using configured templates."""
    return tarot_service.generate_spread(
        payload.spread_id,
        user,
        locale=request_locale(request),
        selected_cards=payload.selected_cards,
    )


@router.post("/spread/context", response_model=TarotSpreadContextResponse)
async def generate_tarot_spread_with_context(
    request: Request,
    payload: models.TarotSpreadRequest = models.TarotSpreadRequest(),
    tarot_service: TarotService = Depends(get_tarot_service),
    user=Depends(require_user),
    db=Depends(get_session),
    core_profile_service: CoreProfileService = Depends(get_core_profile_service),
    orchestrator: InterpretationOrchestrator = Depends(get_interpretation_orchestrator),
) -> TarotSpreadContextResponse:
    spread = tarot_service.generate_spread(
        payload.spread_id,
        user,
        locale=request_locale(request),
        selected_cards=payload.selected_cards,
    )
    core_profile = core_profile_service.build(db, user)

    needs = _spread_needs(payload.spread_id, payload.concern_domain)
    consistency = orchestrator.build_daily_guidance(
        core_profile=core_profile,
        numerology=None,
        needs=needs,
    )
    reading, tarot_answer = compose_tarot_answer_v1(
        spread,
        question=payload.question,
        concern_domain=payload.concern_domain,
        consistency=consistency.model_dump() if hasattr(consistency, "model_dump") else consistency,
        core_profile=core_profile.model_dump() if hasattr(core_profile, "model_dump") else core_profile,
    )
    generation_log_id: int | None = None
    try:
        gen = get_learning_service().log_generation(
            db,
            module="tarot_answer_v1",
            surface="tarot_answer",
            user_id=user.id,
            input_payload={
                "spread_id": spread.spread_id,
                "question": payload.question,
                "concern_domain": payload.concern_domain,
                "card_ids": [c.card.id for c in spread.cards],
                "contract": TAROT_ANSWER_V1_CONTRACT,
            },
            normalized_response=tarot_answer,
            status="success",
            used_fallback=True,
            locale=request_locale(request),
        )
        generation_log_id = gen.id
        tarot_answer = {**tarot_answer, "generation_id": str(gen.id)}
    except Exception:
        generation_log_id = None

    return TarotSpreadContextResponse(
        spread=spread,
        core_profile=core_profile,
        consistency=consistency,
        reading=reading,
        tarot_answer_v1=tarot_answer,
        generation_log_id=generation_log_id,
    )


@router.post("/spread/context/public", response_model=TarotSpreadContextResponse)
async def generate_tarot_spread_with_context_public(
    request: Request,
    payload: models.TarotSpreadRequest = models.TarotSpreadRequest(),
    tarot_service: TarotService = Depends(get_tarot_service),
) -> TarotSpreadContextResponse:
    """Guest spread result — no account, no personalized profile."""
    from todayflow_backend.db.models import User

    public_user = User(id=0, email="public@todayflow.app")
    spread = tarot_service.generate_spread(
        payload.spread_id,
        public_user,
        locale=request_locale(request),
        selected_cards=payload.selected_cards,
    )
    reading, tarot_answer = compose_tarot_answer_v1(
        spread,
        question=payload.question,
        concern_domain=payload.concern_domain,
        consistency=None,
        core_profile=None,
    )
    return TarotSpreadContextResponse(
        spread=spread,
        core_profile={},
        consistency={},
        reading=reading,
        tarot_answer_v1=tarot_answer,
        generation_log_id=None,
    )


@router.get("/spread/history", response_model=models.TarotSpreadHistoryResponse)
async def get_tarot_spread_history(
    request: Request,
    tarot_service: TarotService = Depends(get_tarot_service),
    user=Depends(require_user),
) -> models.TarotSpreadHistoryResponse:
    """Return recent spread draws for the dashboard/PDF surfaces."""
    return tarot_service.get_spread_history(user, locale=request_locale(request))


@router.get("/reminder", response_model=models.TarotReminderSettings)
async def get_tarot_reminder(
    tarot_service: TarotService = Depends(get_tarot_service),
    user=Depends(require_user),
) -> models.TarotReminderSettings:
    """Return reminder preferences for Tarot Flow notifications."""
    return tarot_service.get_reminder_setting(user)


@router.put("/reminder", response_model=models.TarotReminderSettings)
async def update_tarot_reminder(
    payload: models.TarotReminderUpdate,
    tarot_service: TarotService = Depends(get_tarot_service),
    user=Depends(require_user),
) -> models.TarotReminderSettings:
    """Save reminder preferences for Tarot Flow notifications."""
    return tarot_service.update_reminder_setting(user, payload)


@router.get("/reminder/ical")
async def download_tarot_reminder_ical(
    request: Request,
    tarot_service: TarotService = Depends(get_tarot_service),
    user=Depends(require_user),
) -> Response:
    """Download an ICS feed for the user's reminder schedule."""
    try:
        ics = tarot_service.generate_reminder_ics(user, locale=request_locale(request))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return Response(
        content=ics,
        media_type="text/calendar",
        headers={"Content-Disposition": 'attachment; filename="todayflow_tarot_reminder.ics"'},
    )


@router.get("/favorites", response_model=models.TarotFavoritesResponse)
async def get_tarot_favorites(
    tarot_service: TarotService = Depends(get_tarot_service),
    user=Depends(require_user),
) -> models.TarotFavoritesResponse:
    """Get list of favorite card IDs for the user."""
    favorites = tarot_service.get_favorites(user)
    return models.TarotFavoritesResponse(favorites=favorites)


@router.post("/favorites/toggle", response_model=models.TarotFavoritesResponse)
async def toggle_tarot_favorite(
    payload: models.TarotFavoriteUpdate,
    tarot_service: TarotService = Depends(get_tarot_service),
    user=Depends(require_user),
) -> models.TarotFavoritesResponse:
    """Toggle favorite status for a card."""
    tarot_service.toggle_favorite(user, payload.card_id)
    favorites = tarot_service.get_favorites(user)
    return models.TarotFavoritesResponse(favorites=favorites)


@router.post("/deck/draw", response_model=List[models.TarotCard])
async def draw_cards_from_deck(
    request: Request,
    payload: models.TarotDeckDrawRequest = models.TarotDeckDrawRequest(),
    tarot_service: TarotService = Depends(get_tarot_service),
    user=Depends(require_user),
) -> List[models.TarotCard]:
    """Draw cards from deck for interactive selection (returns 10 cards by default)."""
    return tarot_service.draw_cards_from_deck(user, count=payload.count or 10, locale=request_locale(request))


@router.post("/deck/draw/public", response_model=List[models.TarotCard])
async def draw_cards_from_deck_public(
    request: Request,
    payload: models.TarotDeckDrawRequest = models.TarotDeckDrawRequest(),
    tarot_service: TarotService = Depends(get_tarot_service),
) -> List[models.TarotCard]:
    """Draw cards from deck for public/guest users (returns 10 cards by default)."""
    from todayflow_backend.db.models import User
    public_user = User(id=0, email="public@todayflow.app")
    return tarot_service.draw_cards_from_deck(public_user, count=payload.count or 10, locale=request_locale(request))
