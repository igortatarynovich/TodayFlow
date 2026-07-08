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

router = APIRouter(prefix="/tarot", tags=["tarot"])


class TarotSpreadContextResponse(BaseModel):
    spread: models.TarotSpreadResult
    core_profile: dict
    consistency: dict
    reading: models.TarotSpreadReading


def _orientation_label_ru(orientation: str | None) -> str:
    o = (orientation or "").strip().lower()
    if o in ("reversed", "reverse", "r"):
        return "перевёрнутая"
    return "прямая"


def _multispread_manifestation(spread_id: str | None) -> str:
    """Слой расклада без повторения daily guidance из orchestrator (Today)."""
    sid = (spread_id or "").strip().lower()
    if sid == "three_cards":
        return (
            "Соедините три позиции в одну историю: прошлое задаёт контекст, настоящее — выбор, перспектива — ориентир, "
            "а не жёсткое предсказание."
        )
    if sid == "love":
        return (
            "В теме близости и отношений проявление расклада — через честный контакт, ясные границы и наблюдение за своей реакцией, "
            "а не через общий «настрой дня»."
        )
    if sid in ("career", "money"):
        return (
            "В работе и ресурсе сигнал расклада проверяется делами и договорённостями: один измеримый шаг, который можно назвать вслух."
        )
    if sid == "family":
        return (
            "В семейной теме держите фокус на ролях и границах без обобщения «как всегда»: расклад про этот запрос, не про весь день целиком."
        )
    return (
        "Переведите линию расклада в одно конкретное наблюдение или действие в ближайшие часы — в той сфере, о которой был вопрос."
    )


def _multispread_caution(spread_id: str | None) -> str:
    sid = (spread_id or "").strip().lower()
    if sid == "love":
        return (
            "Не используйте карты вместо диалога с человеком и не читайте результат как обвинение или окончательный вердикт о партнёре."
        )
    if sid in ("career", "money"):
        return (
            "Не подменяйте раскладом финансовую или юридическую оценку; карты задают ракурс размышления, не замену экспертизы."
        )
    return (
        "Избегайте фаталистического чтения и дублирования одних и тех же формулировок на экране «Сегодня» и в этом раскладе: это разные слои."
    )


def _compose_spread_reading(
    spread: models.TarotSpreadResult,
    consistency: dict | None,
    core_profile: dict | None,
) -> models.TarotSpreadReading:
    """Текст чтения расклада: без копирования словарного значения карты и без daily do/avoid (Today)."""
    _ = consistency  # намеренно не используем — совпадало с «Сегодня» и давало ощущение повтора
    cards = spread.cards or []
    lead_card = cards[0] if cards else None
    profile_anchor = (
        ((core_profile or {}).get("interpretation") or {}).get("identity")
        or ((core_profile or {}).get("baseline") or {}).get("archetype_seed")
        or "ваш текущий жизненный акцент"
    )

    if spread.spread_id == "one_card" and lead_card:
        card_name = lead_card.card.name
        orient = _orientation_label_ru(lead_card.orientation)
        meaning = (
            f"Этот однокарточный ответ относится к вашему вопросу и не должен дублировать общий фон дня из раздела «Сегодня». "
            f"Карта «{card_name}» ({orient}) задаёт ракурс интерпретации. "
            f"Справочное значение аркана приведено в блоке карты; здесь — только профессиональная рамка расклада, без повтора текста дня."
        )
        manifestation = (
            "Перенесите сигнал в одно наблюдаемое действие или уточняющий вопрос в ближайшие часы — в той области, о которой вы спрашивали."
        )
        caution = (
            "Не подменяйте картой медицинскую, юридическую или финансовую оценку ситуации; не читайте результат как приговор."
        )
        next_step = (
            "Зафиксируйте вывод одной короткой фразой. Подробности по аркану — в справочнике карты; общий контекст дня — в «Сегодня», "
            "избегая дословного повторения между экранами."
        )
        return models.TarotSpreadReading(
            meaning=meaning,
            manifestation=manifestation,
            caution=caution,
            next_step=next_step,
        )

    position_lines = []
    for card in cards[:5]:
        position_title = (card.position.title or "позиция").strip()
        card_title = card.card.name
        position_lines.append(f"{position_title} — «{card_title}»")
    position_summary = "; ".join(position_lines)
    spread_title = (spread.title or "расклад").strip()
    meaning = (
        f"«{spread_title}» читается как единая линия ответа на ваш вопрос, отдельно от карты дня и дневного гороскопа в «Сегодня». "
        f"{position_summary}. "
        f"Связка позиций уточняет тему «{profile_anchor}» в контексте запроса, а не заменяет справочные значения карт в блоках выше."
        if position_summary
        else (
            f"«{spread_title}» лучше трактовать как одну траекторию через тему «{profile_anchor}», "
            f"без смешения с общим фоном дня в других разделах приложения."
        )
    )
    manifestation = _multispread_manifestation(spread.spread_id)
    caution = _multispread_caution(spread.spread_id)
    next_step = (
        "Сформулируйте один следующий шаг по этому раскладу. Углубляйтесь через другие сценарии приложения, когда будете готовы — "
        "без необходимости сверять дословно с текстом «Сегодня»."
    )
    return models.TarotSpreadReading(
        meaning=meaning,
        manifestation=manifestation,
        caution=caution,
        next_step=next_step,
    )


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

    spread_needs_map = {
        "one_card": "general",
        "three_cards": "work",
        "love": "love",
        "career": "work",
        "money": "money",
        "family": "family",
    }
    needs = spread_needs_map.get(payload.spread_id or "", "general")
    consistency = orchestrator.build_daily_guidance(
        core_profile=core_profile,
        numerology=None,
        needs=needs,
    )
    return TarotSpreadContextResponse(
        spread=spread,
        core_profile=core_profile,
        consistency=consistency,
        reading=_compose_spread_reading(spread, consistency, core_profile),
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
