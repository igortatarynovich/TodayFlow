"""Celestial reference endpoints (moon, planets)."""

from fastapi import APIRouter, Depends, Query, Request

from todayflow_backend.api.auth import require_user
from todayflow_backend.core import models
from todayflow_backend.i18n import request_locale
from todayflow_backend.services.check_ins import CheckInService, get_checkin_service
from todayflow_backend.services.lunar import LunarService, get_lunar_service
from todayflow_backend.services.planetary import PlanetaryService, get_planetary_service
from todayflow_backend.services.weekly import WeeklyInsightService, get_weekly_service
from todayflow_backend.services.transit_feed import TransitFeedService, get_transit_feed_service

router = APIRouter(prefix="/celestial", tags=["celestial"])


@router.get("/moon-phase", response_model=models.MoonPhaseResponse)
async def get_moon_phase(request: Request, lunar_service: LunarService = Depends(get_lunar_service)) -> models.MoonPhaseResponse:
    """Return current lunar phase metadata + near-term milestones."""
    locale = request_locale(request)
    return lunar_service.current_phase(locale=locale)


@router.get("/planet-events", response_model=models.PlanetaryTimeline)
async def get_planet_events(
    request: Request,
    planetary_service: PlanetaryService = Depends(get_planetary_service),
    limit: int = Query(6, ge=1, le=20),
    window_limit: int = Query(2, ge=0, le=6),
) -> models.PlanetaryTimeline:
    """Return upcoming planetary events and influence windows for the Solar System strip."""
    return planetary_service.upcoming_events(limit=limit, window_limit=window_limit, locale=request_locale(request))


@router.get("/check-in", response_model=models.CheckInResponse)
async def get_check_in_prompt(
    request: Request,
    checkin_service: CheckInService = Depends(get_checkin_service), user=Depends(require_user)
) -> models.CheckInResponse:
    """Return a deterministic check-in prompt tied to the user's axes."""
    return checkin_service.daily_prompt(user.id, locale=request_locale(request))


@router.get("/weekly-insight", response_model=models.WeeklyInsightResponse)
async def get_weekly_insight(
    request: Request,
    weekly_service: WeeklyInsightService = Depends(get_weekly_service), user=Depends(require_user)
) -> models.WeeklyInsightResponse:
    """Return weekly lunar insight tied to moon phase + internal model."""
    try:
        return weekly_service.get_insight(user, locale=request_locale(request))
    except ValueError as e:
        # Если нет lite report, возвращаем базовый insight без персонализации
        from todayflow_backend.services.lunar import LunarService
        lunar_service = LunarService()
        lunar = lunar_service.current_phase(locale=request_locale(request))
        # Возвращаем базовый insight без привязки к internal model
        return models.WeeklyInsightResponse(
            insight=models.WeeklyInsight(
                phase_id=lunar.current.id,
                phase_name=lunar.current.name,
                axis_id=None,
                axis_label=None,
                title=f"Лунная фаза: {lunar.current.name}",
                summary=f"Текущая лунная фаза: {lunar.current.name}. Создайте профиль для персонализированных инсайтов.",
                cta="Создайте профиль для получения персонализированных инсайтов"
            ),
            next_phase=None
        )


@router.get("/transit-feed", response_model=models.TransitFeedResponse)
async def get_transit_feed(
    request: Request,
    transit_service: TransitFeedService = Depends(get_transit_feed_service),
    user=Depends(require_user),
) -> models.TransitFeedResponse:
    """Return aggregated lunar + planetary feed highlights for the dashboard."""
    return transit_service.get_feed(locale=request_locale(request))
