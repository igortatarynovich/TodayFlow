"""Report-related endpoints."""

from typing import Optional, List, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from todayflow_backend.api.auth import get_optional_user, require_user
from todayflow_backend.core import models
from todayflow_backend.db import models as db_models
from todayflow_backend.db.session import get_session
from todayflow_backend.i18n import request_locale, translate
from todayflow_backend.services.lite_reports import LiteReportService, get_lite_report_service
from todayflow_backend.services.personal_transits import PersonalTransitService, get_personal_transit_service
from todayflow_backend.services import astro
from todayflow_backend.services.geocode import Geocoder
from todayflow_backend.core.llm_openai_compatible import is_llm_chat_configured
from datetime import date, timedelta

router = APIRouter(prefix="/reports", tags=["reports"])


def _first_non_empty_text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        for item in value:
            if isinstance(item, str) and item.strip():
                return item.strip()
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str) and text.strip():
                    return text.strip()
    return ""


def _build_ai_enhanced_daily_forecast(
    transit_forecast: models.DailyForecast,
    generated,
    forecast_date: date,
    natal_chart_data: Optional[dict[str, Any]],
) -> models.DailyForecast:
    theme_text = _first_non_empty_text(generated.blocks.get("theme", ""))
    notice_items = generated.blocks.get("notice", [])
    scene_items = generated.blocks.get("scene", [])
    micro_action = _first_non_empty_text(generated.blocks.get("micro_action", ""))

    combined_actions = list(transit_forecast.conscious_actions or [])
    if micro_action:
        combined_actions.insert(0, micro_action)
    if isinstance(scene_items, list):
        for item in scene_items[:2]:
            text = _first_non_empty_text(item)
            if text:
                combined_actions.append(text)

    seen_actions: set[str] = set()
    deduped_actions: list[str] = []
    for action in combined_actions:
        normalized = action.strip()
        if normalized and normalized not in seen_actions:
            seen_actions.add(normalized)
            deduped_actions.append(normalized)

    ai_insights: list[models.TransitInsight] = []
    base_insight = transit_forecast.psychological_insights[0] if transit_forecast.psychological_insights else None

    insight_candidates: list[str] = []
    if theme_text:
        insight_candidates.append(theme_text)
    if isinstance(notice_items, list):
        for item in notice_items[:2]:
            text = _first_non_empty_text(item)
            if text:
                insight_candidates.append(text)

    if base_insight:
        for text in insight_candidates:
            ai_insights.append(
                models.TransitInsight(
                    transiting_planet=base_insight.transiting_planet,
                    natal_planet=base_insight.natal_planet,
                    aspect=base_insight.aspect,
                    strength=base_insight.strength,
                    tension_level=base_insight.tension_level,
                    area=base_insight.area,
                    feeling=base_insight.feeling,
                    psychological_description=text,
                    recommendations=base_insight.recommendations,
                )
            )

    return models.DailyForecast(
        date=forecast_date.isoformat(),
        transits=transit_forecast.transits,
        tensions=transit_forecast.tensions,
        resources=transit_forecast.resources,
        psychological_insights=ai_insights if ai_insights else transit_forecast.psychological_insights,
        conscious_actions=deduped_actions if deduped_actions else transit_forecast.conscious_actions,
        intensity_score=transit_forecast.intensity_score,
        natal_chart=natal_chart_data,
    )


@router.post("/lite", response_model=models.LiteReport)
async def generate_lite_report(
    request: Request,
    payload: models.BirthData,
    service: LiteReportService = Depends(get_lite_report_service),
    user=Depends(get_optional_user),
    astro_profile_id: Optional[int] = Query(None, description="ID астро профиля для привязки lite report"),
) -> models.LiteReport:
    locale = request_locale(request)
    return await service.generate(payload, user=user, locale=locale, astro_profile_id=astro_profile_id)
@router.get("/lite", response_model=models.LiteReport)
async def get_lite_report(
    request: Request,
    service: LiteReportService = Depends(get_lite_report_service),
    user=Depends(require_user),
    astro_profile_id: Optional[int] = Query(None, description="ID астро профиля для получения lite report"),
) -> models.LiteReport:
    locale = request_locale(request)
    report = service._get_latest_report(user, astro_profile_id=astro_profile_id)
    if not report:
        raise HTTPException(status_code=404, detail=translate("reports.lite.notFound", locale=locale))
    if report.chart_positions:
        report.aspects = service.aspect_engine.callouts(report.chart_positions, locale=locale)
    return report


@router.get("/history", response_model=models.ReportHistoryResponse)
async def get_reports_history(
    request: Request,
    user=Depends(require_user),
    db: Session = Depends(get_session),
) -> models.ReportHistoryResponse:
    """Get user's report history."""
    from sqlalchemy.orm import joinedload
    
    reports = (
        db.query(db_models.GeneratedReport)
        .filter_by(user_id=user.id)
        .order_by(db_models.GeneratedReport.created_at.desc())
        .all()
    )
    
    # Get all AstroProfiles for the user to map profile_id (AstroProfile.id) to label
    astro_profiles = {p.id: p.label for p in db.query(db_models.AstroProfile).filter_by(user_id=user.id).all()}
    
    history_items = []
    for report in reports:
        profile_label = None
        if report.profile_id:
            # profile_id should point to AstroProfile.id
            profile_label = astro_profiles.get(report.profile_id)
        
        history_items.append(
            models.ReportHistoryItem(
                id=report.id,
                profile_id=report.profile_id,
                product_type=report.product_type,
                content_version=report.content_version,
                created_at=report.created_at,
                profile_label=profile_label,
            )
        )
    
    return models.ReportHistoryResponse(
        history=history_items,
        total=len(history_items),
    )


@router.get("/daily-forecast/public", response_model=models.DailyForecast)
async def get_daily_forecast_public(
    request: Request,
    forecast_date: Optional[date] = Query(None, description="Date for forecast (defaults to today)"),
    locale: str = Query("ru", description="Locale"),
) -> models.DailyForecast:
    """
    Get free daily forecast (базовый, без персонализации).
    
    Бесплатно:
    - Только астрология (общие транзиты дня)
    - Без персонализации
    - Один слой
    - Короткий
    
    Цель: привычка возвращаться утром.
    """
    if forecast_date is None:
        forecast_date = date.today()
    
    # Получаем общие транзиты дня (без натальной карты)
    from todayflow_backend.services.personal_transits import PersonalTransitService
    from todayflow_backend.services import astro
    
    transit_service = PersonalTransitService()
    astro_service = astro.AstroService()
    
    # Создаем базовую натальную карту для текущего дня (общие транзиты)
    # Используем текущую дату как "рождение" для получения общих транзитов
    birth_data = models.BirthData(
        date=forecast_date.isoformat(),
        time="12:00",
        location="UTC",
        coordinates=models.Coordinates(latitude=0.0, longitude=0.0)
    )
    
    # Получаем общий прогноз (без персонализации)
    transit_forecast = await transit_service.get_daily_forecast(
        natal_chart=None,  # Без натальной карты - общий прогноз
        forecast_date=forecast_date,
        birth_data=birth_data,
        locale=locale,
    )
    
    return models.DailyForecast(
        date=forecast_date.isoformat(),
        transits=transit_forecast.transits or [],
        tensions=transit_forecast.tensions or [],
        resources=transit_forecast.resources or [],
        psychological_insights=transit_forecast.psychological_insights[:1] if transit_forecast.psychological_insights else [],  # Только 1 инсайт
        conscious_actions=transit_forecast.conscious_actions[:1] if transit_forecast.conscious_actions else [],  # Только 1 действие
        intensity_score=transit_forecast.intensity_score or 0.0,
        natal_chart=None,  # Без натальной карты для бесплатных
    )


@router.get("/daily-forecast", response_model=models.DailyForecast)
async def get_daily_forecast(
    request: Request,
    forecast_date: Optional[date] = Query(None, description="Date for forecast (defaults to today)"),
    astro_profile_id: Optional[int] = Query(None, description="ID астро профиля для прогноза (defaults to primary)"),
    use_ai: bool = Query(True, description="Использовать ИИ для генерации (через натальную карту)"),
    user=Depends(require_user),
    db: Session = Depends(get_session),
    transit_service: PersonalTransitService = Depends(get_personal_transit_service),
    astro_service: astro.AstroService = Depends(lambda: astro.AstroService()),
    geocoder: Geocoder = Depends(lambda: Geocoder()),
) -> models.DailyForecast:
    """
    Get personalized daily forecast based on transits to natal chart.
    
    Платно (требует подписку):
    - Учёт натальной карты
    - Учёт Personal Day / Year
    - Усиление текста «про тебя»
    - ИИ генерация с персонализацией
    
    Если use_ai=True — генерирует через ИИ с учётом натальной карты.
    """
    locale = request_locale(request)
    
    # Проверяем подписку для персонализации
    from todayflow_backend.api.practices import get_subscription_level
    subscription_level = get_subscription_level(user, db)
    is_paid = subscription_level in ["lite", "pro"] or user.is_paid
    
    if not is_paid:
        # Бесплатный пользователь - возвращаем базовый прогноз
        # Но используем его натальную карту если есть (для транзитов)
        try:
            astro_profile = await _get_user_astro_profile(user, db, astro_profile_id, locale)
            birth_data = await _prepare_birth_data(astro_profile, geocoder, locale)
            natal_chart = await _compute_natal_chart(birth_data, astro_service, astro_profile, db)
            
            if natal_chart and natal_chart.positions:
                # Есть натальная карта - используем транзиты к ней, но без ИИ персонализации
                transit_forecast = await transit_service.get_daily_forecast(
                    natal_chart=natal_chart,
                    forecast_date=forecast_date or date.today(),
                    birth_data=birth_data,
                    locale=locale,
                )
                
                # Ограничиваем для бесплатных: только 1 инсайт, 1 действие
                return models.DailyForecast(
                    date=(forecast_date or date.today()).isoformat(),
                    transits=transit_forecast.transits or [],
                    tensions=transit_forecast.tensions or [],
                    resources=transit_forecast.resources or [],
                    psychological_insights=transit_forecast.psychological_insights[:1] if transit_forecast.psychological_insights else [],
                    conscious_actions=transit_forecast.conscious_actions[:1] if transit_forecast.conscious_actions else [],
                    intensity_score=transit_forecast.intensity_score or 0.0,
                    natal_chart=_format_natal_chart_for_response(natal_chart),
                )
        except Exception:
            pass  # Fallback на публичный прогноз
    
    # Если нет натальной карты или ошибка - возвращаем публичный прогноз
    if forecast_date is None:
        forecast_date = date.today()
    
    # Платные пользователи продолжают с полным прогнозом
    # Get user's astro profile
    astro_profile = await _get_user_astro_profile(user, db, astro_profile_id, locale)
    birth_data = await _prepare_birth_data(astro_profile, geocoder, locale)
    natal_chart = await _compute_natal_chart(birth_data, astro_service, astro_profile, db)
    
    if not natal_chart or not natal_chart.positions:
        # Нет натальной карты - возвращаем публичный прогноз
        return await get_daily_forecast_public(request, forecast_date, locale)
    
    # Проверяем кеш прогноза
    from todayflow_backend.services.forecast_cache import get_forecast_cache_service
    cache_service = get_forecast_cache_service(db)
    cached_forecast = cache_service.get_cached_forecast(
        user_id=user.id,
        astro_profile_id=astro_profile.id,
        forecast_type="daily",
        forecast_date=forecast_date,
        locale=locale,
        use_ai=use_ai and is_paid  # ИИ только для платных
    )
    
    if cached_forecast:
        # Возвращаем из кеша
        return models.DailyForecast(**cached_forecast)
    
    # Если запрошена генерация через ИИ (только для платных)
    if use_ai and is_paid:
        try:
            from todayflow_backend.core.text_generator import TextGenerator
            from todayflow_backend.services.day_meaning_builder import DayMeaningBuilder
            from todayflow_backend.services.numerology import get_numerology_service
            from todayflow_backend.services.tarot import TarotService
            from todayflow_backend.core.user_context import get_user_context
            
            if is_llm_chat_configured():
                # НОВЫЙ ПАЙПЛАЙН: система → смысл → интерпретация → лексикон → ИИ
                # 1. Строим DayMeaning из систем (только для платных)
                numerology_service = get_numerology_service()
                tarot_service = TarotService()
                
                builder = DayMeaningBuilder(
                    transit_service=transit_service,
                    numerology_service=numerology_service,
                    tarot_service=tarot_service,
                )
                
                day_meaning = await builder.build(
                    user=user,
                    target_date=forecast_date,
                    natal_chart=natal_chart,
                    birth_data=birth_data,
                    locale=locale,
                    db=db,
                )
                
                # 2. Получаем контекст пользователя
                user_context = get_user_context(user, forecast_date.isoformat(), db)
                
                # 3. Генерируем текст из DayMeaning
                generator = TextGenerator()
                generated = generator.generate_from_meaning(
                    day_meaning=day_meaning,
                    user_context=user_context,
                    locale=locale,
                    validate=True,
                )
                
                # 4. Формируем DailyForecast из DayMeaning и сгенерированного текста
                # Преобразуем generated.blocks в psychological_insights и conscious_actions
                psychological_insights = []
                conscious_actions = []
                
                # theme + notice → psychological_insights
                theme_text = generated.blocks.get("theme", "")
                if isinstance(theme_text, str) and theme_text.strip():
                    base_tension = day_meaning.astro_state.tensions[0] if day_meaning.astro_state.tensions else {}
                    psychological_insights.append(models.TransitInsight(
                        transiting_planet=base_tension.get("transiting_planet", "Unknown"),
                        natal_planet=base_tension.get("natal_planet", "Unknown"),
                        aspect=base_tension.get("aspect", "conjunction"),
                        strength=base_tension.get("strength", "medium"),
                        tension_level=day_meaning.interpretation_direction,
                        area=day_meaning.focus_area,
                        feeling="",
                        psychological_description=theme_text,
                        recommendations=[],
                    ))

                # notice → psychological_insights
                notice_items = generated.blocks.get("notice", [])
                if notice_items and day_meaning.astro_state.tensions:
                    # Используем структуру первого транзита для insights
                    base_tension = day_meaning.astro_state.tensions[0]
                    for notice_text in notice_items[:2]:
                        if isinstance(notice_text, str):
                            psychological_insights.append(models.TransitInsight(
                                transiting_planet=base_tension.get("transiting_planet", "Unknown"),
                                natal_planet=base_tension.get("natal_planet", "Unknown"),
                                aspect=base_tension.get("aspect", "conjunction"),
                                strength=base_tension.get("strength", "medium"),
                                tension_level=day_meaning.interpretation_direction,
                                area=day_meaning.focus_area,
                                feeling="",
                                psychological_description=notice_text,
                                recommendations=[]
                            ))
                
                # scene → conscious_actions
                scene_items = generated.blocks.get("scene", [])
                for scene_text in scene_items:
                    if isinstance(scene_text, str):
                        conscious_actions.append(scene_text)
                
                # micro_action → conscious_actions
                micro_action = generated.blocks.get("micro_action", "")
                if micro_action and isinstance(micro_action, str):
                    conscious_actions.append(micro_action)
                
                # Если нет действий из ИИ, используем из транзитов
                if not conscious_actions:
                    transit_forecast = await transit_service.get_daily_forecast(
                        natal_chart=natal_chart,
                        forecast_date=forecast_date,
                        birth_data=birth_data,
                        locale=locale,
                    )
                    conscious_actions = list(transit_forecast.conscious_actions)
                    if not psychological_insights:
                        psychological_insights = list(transit_forecast.psychological_insights)
                
                # Формируем данные натальной карты для ответа
                natal_chart_data = _format_natal_chart_for_response(natal_chart)
                
                forecast_result = models.DailyForecast(
                    date=forecast_date.isoformat(),
                    transits=day_meaning.astro_state.transits,
                    tensions=day_meaning.astro_state.tensions,
                    resources=day_meaning.astro_state.resources,
                    psychological_insights=psychological_insights if psychological_insights else [],
                    conscious_actions=conscious_actions,
                    intensity_score=day_meaning.intensity,
                    natal_chart=natal_chart_data
                )
                
                # Сохраняем в кеш
                cache_service.save_forecast(
                    user_id=user.id,
                    astro_profile_id=astro_profile.id,
                    forecast_type="daily",
                    forecast_date=forecast_date,
                    forecast_data=forecast_result.model_dump(),
                    locale=locale,
                    use_ai=True
                )
                
                return forecast_result
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"AI generation failed, falling back to transit service: {e}", exc_info=True)
            # Fallback на обычный сервис
    
    # Generate daily forecast через transit service (fallback или если use_ai=False)
    forecast = await transit_service.get_daily_forecast(
        natal_chart=natal_chart,
        forecast_date=forecast_date,
        birth_data=birth_data,
        locale=locale,
    )
    
    # Для бесплатных пользователей ограничиваем количество инсайтов и действий
    if not is_paid:
        forecast.psychological_insights = forecast.psychological_insights[:1] if forecast.psychological_insights else []
        forecast.conscious_actions = forecast.conscious_actions[:1] if forecast.conscious_actions else []
    
    # Добавляем натальную карту в ответ (только для платных)
    if is_paid:
        natal_chart_data = _format_natal_chart_for_response(natal_chart)
        forecast.natal_chart = natal_chart_data
    else:
        forecast.natal_chart = None  # Без натальной карты для бесплатных
    
    # Сохраняем в кеш
    from todayflow_backend.services.forecast_cache import get_forecast_cache_service
    cache_service = get_forecast_cache_service(db)
    cache_service.save_forecast(
        user_id=user.id,
        astro_profile_id=astro_profile.id,
        forecast_type="daily",
        forecast_date=forecast_date,
        forecast_data=forecast.model_dump(),
        locale=locale,
        use_ai=False
    )
    
    return forecast


@router.get("/weekly-background", response_model=models.WeeklyBackgroundForecast)
async def get_weekly_background(
    request: Request,
    start_date: Optional[date] = Query(None, description="Start date for forecast week (defaults to today)"),
    astro_profile_id: Optional[int] = Query(None, description="ID астро профиля для прогноза (defaults to primary)"),
    user=Depends(require_user),
    db: Session = Depends(get_session),
    transit_service: PersonalTransitService = Depends(get_personal_transit_service),
    astro_service: astro.AstroService = Depends(lambda: astro.AstroService()),
    geocoder: Geocoder = Depends(lambda: Geocoder()),
) -> models.WeeklyBackgroundForecast:
    """
    Get weekly background forecast (общий фон недели).
    
    Не детальный прогноз на каждый день, а общий контекст недели:
    - 1 текст
    - Без деталей
    - Без советов
    - Объясняет фон, на котором происходят дневные прогнозы
    """
    import logging
    logger = logging.getLogger(__name__)
    locale = request_locale(request)
    
    try:
        if start_date is None:
            start_date = date.today()
        
        # Get user's astro profile
        astro_profile = await _get_user_astro_profile(user, db, astro_profile_id, locale)
        birth_data = await _prepare_birth_data(astro_profile, geocoder, locale)
        natal_chart = await _compute_natal_chart(birth_data, astro_service, astro_profile, db)
        
        if not natal_chart or not natal_chart.positions:
            raise HTTPException(
                status_code=500,
                detail=translate("reports.errors.chartCalculationFailed", locale=locale, default="Failed to calculate natal chart")
            )
        
        # Получаем основные транзиты недели (не детальные, а общие)
        # Берем транзиты для начала недели и конца недели
        end_date = start_date + timedelta(days=6)
        
        start_forecast = await transit_service.get_daily_forecast(
            natal_chart=natal_chart,
            forecast_date=start_date,
            birth_data=birth_data,
            locale=locale,
        )
        
        end_forecast = await transit_service.get_daily_forecast(
            natal_chart=natal_chart,
            forecast_date=end_date,
            birth_data=birth_data,
            locale=locale,
        )
        
        # Определяем общий фон недели на основе транзитов
        # Собираем уникальные транзиты за неделю
        all_transits = {}
        for transit in (start_forecast.transits or []) + (end_forecast.transits or []):
            if isinstance(transit, dict):
                transit_key = f"{transit.get('planet', '')}_{transit.get('target', '')}"
                if transit_key not in all_transits:
                    all_transits[transit_key] = transit
        
        # Определяем общее направление недели
        total_tensions = len(start_forecast.tensions or []) + len(end_forecast.tensions or [])
        total_resources = len(start_forecast.resources or []) + len(end_forecast.resources or [])
        
        if total_tensions > total_resources * 1.5:
            week_direction = "tension"
        elif total_resources > total_tensions * 1.5:
            week_direction = "release"
        elif total_tensions > 0 and total_resources > 0:
            week_direction = "transition"
        else:
            week_direction = "neutral"
        
        # Генерируем общий текст недели (через DayMeaning и TextGenerator)
        from todayflow_backend.services.day_meaning_builder import DayMeaningBuilder
        from todayflow_backend.services.numerology import NumerologyService
        from todayflow_backend.services.tarot import TarotService
        from todayflow_backend.core.text_generator import TextGenerator
        from todayflow_backend.core.user_context import get_user_context
        
        day_meaning_builder = DayMeaningBuilder(
            transit_service=transit_service,
            numerology_service=NumerologyService(),
            tarot_service=TarotService() if user else None,
        )
        
        # Строим DayMeaning для середины недели
        mid_week_date = start_date + timedelta(days=3)
        day_meaning = await day_meaning_builder.build(
            user=user,
            target_date=mid_week_date,
            natal_chart=natal_chart,
            birth_data=birth_data,
            locale=locale,
            db=db,
        )
        
        # Генерируем общий текст недели
        background_text = None
        try:
            if is_llm_chat_configured():
                generator = TextGenerator()
                user_context = get_user_context(user, mid_week_date.isoformat(), db) if user else {}

                generated = generator.generate_from_meaning(
                    day_meaning=day_meaning,
                    user_context=user_context,
                    locale=locale,
                )
                
                # Берем theme как общий фон недели
                if generated.blocks:
                    theme = generated.blocks.get("theme", "")
                    if isinstance(theme, list) and theme:
                        background_text = theme[0] if isinstance(theme[0], str) else theme[0].get("text", "")
                    elif isinstance(theme, str):
                        background_text = theme
        except Exception as e:
            logger.warning(f"Failed to generate weekly background via AI: {e}", exc_info=True)
        
        # Fallback: простой текст на основе транзитов
        if not background_text:
            if week_direction == "tension":
                background_text = translate(
                    "forecast.weekly.background.tension",
                    locale=locale,
                    default="На этой неделе напряжение будет приходить волнами, а не держаться сплошным фоном. Больше всего пользы даст не спешка, а умение заранее понять, где твое участие действительно нужно."
                )
            elif week_direction == "release":
                background_text = translate(
                    "forecast.weekly.background.release",
                    locale=locale,
                    default="Эта неделя дает больше воздуха. Хорошее время, чтобы отпустить лишнее напряжение и наконец продвинуть то, до чего раньше не доходили руки."
                )
            elif week_direction == "transition":
                background_text = translate(
                    "forecast.weekly.background.transition",
                    locale=locale,
                    default="Это неделя перехода: один день может собирать, другой сбивать с темпа. Полезнее не ждать идеальной ровности, а заранее держать под рукой несколько понятных действий, к которым можно возвращаться."
                )
            else:
                background_text = translate(
                    "forecast.weekly.background.neutral",
                    locale=locale,
                    default="Фон недели относительно ровный. Здесь решает не общий драматизм периода, а то, как ты пройдешь конкретные дни, разговоры и рабочие развилки."
                )
        
        return models.WeeklyBackgroundForecast(
            week_start=start_date.isoformat(),
            week_end=end_date.isoformat(),
            background_text=background_text,
            direction=week_direction,
            key_transits=list(all_transits.values())[:5],  # Топ-5 транзитов
            intensity_score=((start_forecast.intensity_score or 0.0) + (end_forecast.intensity_score or 0.0)) / 2,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Weekly background error for user {user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=translate("reports.errors.forecastGenerationFailed", locale=locale, default=f"Failed to generate forecast: {str(e)}")
        )


@router.get("/weekly-forecast", response_model=List[models.DailyForecast], deprecated=True)
async def get_weekly_forecast(
    request: Request,
    start_date: Optional[date] = Query(None, description="Start date for forecast week (defaults to today)"),
    astro_profile_id: Optional[int] = Query(None, description="ID астро профиля для прогноза (defaults to primary)"),
    use_ai: bool = Query(True, description="Использовать ИИ для генерации (через натальную карту)"),
    user=Depends(require_user),
    db: Session = Depends(get_session),
    transit_service: PersonalTransitService = Depends(get_personal_transit_service),
    astro_service: astro.AstroService = Depends(lambda: astro.AstroService()),
    geocoder: Geocoder = Depends(lambda: Geocoder()),
) -> List[models.DailyForecast]:
    """
    Get personalized weekly forecast (7 days) based on transits to natal chart.
    Если use_ai=True — генерирует через ИИ с учётом натальной карты.
    """
    import logging
    logger = logging.getLogger(__name__)
    locale = request_locale(request)
    
    try:
        if start_date is None:
            start_date = date.today()
        
        # Get user's astro profile (same logic as daily forecast)
        logger.debug(f"Weekly forecast: Getting astro profile for user {user.id}, profile_id={astro_profile_id}")
        astro_profile = await _get_user_astro_profile(user, db, astro_profile_id, locale)
        
        logger.debug(f"Weekly forecast: Preparing birth data for profile {astro_profile.id}")
        birth_data = await _prepare_birth_data(astro_profile, geocoder, locale)
        
        logger.debug(f"Weekly forecast: Computing natal chart")
        natal_chart = await _compute_natal_chart(birth_data, astro_service, astro_profile, db)
        
        if not natal_chart or not natal_chart.positions:
            logger.error(f"Weekly forecast: Natal chart is empty or has no positions")
            raise HTTPException(
                status_code=500,
                detail=translate("reports.errors.chartCalculationFailed", locale=locale, default="Failed to calculate natal chart")
            )
        
        logger.debug(f"Weekly forecast: Generating forecast for {start_date}")
        
        # Проверяем кеш для каждого дня недели
        from todayflow_backend.services.forecast_cache import get_forecast_cache_service
        cache_service = get_forecast_cache_service(db)
        forecasts = []
        dates_to_generate = []
        
        for day_offset in range(7):
            forecast_date = start_date + timedelta(days=day_offset)
            cached = cache_service.get_cached_forecast(
                user_id=user.id,
                astro_profile_id=astro_profile.id,
                forecast_type="daily",
                forecast_date=forecast_date,
                locale=locale,
                use_ai=use_ai
            )
            
            if cached:
                forecasts.append(models.DailyForecast(**cached))
            else:
                dates_to_generate.append(forecast_date)
        
        # Если все дни в кеше, возвращаем (сортируем по дате)
        if len(dates_to_generate) == 0:
            forecasts.sort(key=lambda x: x.date)
            logger.debug(f"Weekly forecast: All 7 days from cache")
            return forecasts
        
        logger.debug(f"Weekly forecast: {len(dates_to_generate)} days to generate, {7 - len(dates_to_generate)} from cache")
        
        # Генерируем только недостающие дни
        if use_ai:
            try:
                from todayflow_backend.core.text_generator import TextGenerator, GenerationRequest
                
                if is_llm_chat_configured():
                    generator = TextGenerator()
                    
                    # Генерируем прогноз для недостающих дней через ИИ
                    for forecast_date in dates_to_generate:
                        gen_request = GenerationRequest(
                            forecast_type="daily_grounded",
                            layers=["L1", "L2"],
                            context="",
                            locale=locale
                        )
                        
                        # Генерируем через ИИ с учётом натальной карты
                        generated = generator.generate(
                            gen_request,
                            validate=True,
                            user=user,
                            db=db,
                            target_date=forecast_date.isoformat()
                        )
                        
                        # Получаем транзиты для этого дня
                        transit_forecast = await transit_service.get_daily_forecast(
                            natal_chart=natal_chart,
                            forecast_date=forecast_date,
                            birth_data=birth_data,
                            locale=locale,
                        )
                        
                        # Добавляем натальную карту и человекочитаемый ИИ-слой
                        natal_chart_data = _format_natal_chart_for_response(natal_chart)
                        forecast_result = _build_ai_enhanced_daily_forecast(
                            transit_forecast=transit_forecast,
                            generated=generated,
                            forecast_date=forecast_date,
                            natal_chart_data=natal_chart_data,
                        )
                        
                        # Сохраняем в кеш
                        cache_service.save_forecast(
                            user_id=user.id,
                            astro_profile_id=astro_profile.id,
                            forecast_type="daily",
                            forecast_date=forecast_date,
                            forecast_data=forecast_result.model_dump(),
                            locale=locale,
                            use_ai=True
                        )
                        
                        forecasts.append(forecast_result)
                    
                    logger.debug(f"Weekly forecast: Generated {len(dates_to_generate)} daily forecasts via AI")
                    # Сортируем по дате
                    forecasts.sort(key=lambda x: x.date)
                    return forecasts
            except Exception as e:
                logger.warning(f"AI generation for weekly forecast failed, falling back to transit service: {e}", exc_info=True)
                # Fallback на обычный сервис
        
        # Generate weekly forecast через transit service (fallback или если use_ai=False)
        # Генерируем только недостающие дни через transit service
        natal_chart_data = _format_natal_chart_for_response(natal_chart)
        
        for forecast_date in dates_to_generate:
            transit_forecast = await transit_service.get_daily_forecast(
                natal_chart=natal_chart,
                forecast_date=forecast_date,
                birth_data=birth_data,
                locale=locale,
            )
            
            # Добавляем натальную карту
            transit_forecast.natal_chart = natal_chart_data
            forecasts.append(transit_forecast)
            
            # Сохраняем в кеш
            cache_service.save_forecast(
                user_id=user.id,
                astro_profile_id=astro_profile.id,
                forecast_type="daily",
                forecast_date=forecast_date,
                forecast_data=transit_forecast.model_dump(),
                locale=locale,
                use_ai=False
            )
        
        # Сортируем по дате
        forecasts.sort(key=lambda x: x.date)
        logger.debug(f"Weekly forecast: Generated {len(forecasts)} daily forecasts (cached: {7 - len(dates_to_generate)}, generated: {len(dates_to_generate)})")
        return forecasts
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Weekly forecast error for user {user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=translate("reports.errors.forecastGenerationFailed", locale=locale, default=f"Failed to generate forecast: {str(e)}")
        )


@router.get("/monthly-forecast", response_model=List[models.DailyForecast])
async def get_monthly_forecast(
    request: Request,
    start_date: Optional[date] = Query(None, description="Start date for forecast month (defaults to today)"),
    astro_profile_id: Optional[int] = Query(None, description="ID астро профиля для прогноза (defaults to primary)"),
    use_ai: bool = Query(True, description="Использовать ИИ для генерации (через натальную карту)"),
    user=Depends(require_user),
    db: Session = Depends(get_session),
    transit_service: PersonalTransitService = Depends(get_personal_transit_service),
    astro_service: astro.AstroService = Depends(lambda: astro.AstroService()),
    geocoder: Geocoder = Depends(lambda: Geocoder()),
) -> List[models.DailyForecast]:
    """
    Get personalized monthly forecast (30 days) based on transits to natal chart.
    Если use_ai=True — генерирует через ИИ с учётом натальной карты (первые 7 дней).
    """
    import logging
    logger = logging.getLogger(__name__)
    locale = request_locale(request)
    
    try:
        if start_date is None:
            start_date = date.today()
        
        astro_profile = await _get_user_astro_profile(user, db, astro_profile_id, locale)
        birth_data = await _prepare_birth_data(astro_profile, geocoder, locale)
        natal_chart = await _compute_natal_chart(birth_data, astro_service, astro_profile, db)
        
        if not natal_chart or not natal_chart.positions:
            logger.error(f"Monthly forecast: Natal chart is empty or has no positions")
            raise HTTPException(
                status_code=500,
                detail=translate("reports.errors.chartCalculationFailed", locale=locale, default="Failed to calculate natal chart")
            )
        
        logger.debug(f"Monthly forecast: Generating forecast for {start_date}")
        
        # Проверяем кеш для каждого дня месяца
        from todayflow_backend.services.forecast_cache import get_forecast_cache_service
        cache_service = get_forecast_cache_service(db)
        forecasts = []
        dates_to_generate = []
        
        for day_offset in range(30):
            forecast_date = start_date + timedelta(days=day_offset)
            cached = cache_service.get_cached_forecast(
                user_id=user.id,
                astro_profile_id=astro_profile.id,
                forecast_type="daily",
                forecast_date=forecast_date,
                locale=locale,
                use_ai=use_ai
            )
            
            if cached:
                forecasts.append(models.DailyForecast(**cached))
            else:
                dates_to_generate.append(forecast_date)
        
        # Если все дни в кеше, возвращаем
        if len(dates_to_generate) == 0:
            forecasts.sort(key=lambda x: x.date)
            logger.debug(f"Monthly forecast: All 30 days from cache")
            return forecasts
        
        logger.debug(f"Monthly forecast: {len(dates_to_generate)} days to generate, {30 - len(dates_to_generate)} from cache")
        
        # Если запрошена генерация через ИИ
        if use_ai:
            try:
                from todayflow_backend.core.text_generator import TextGenerator, GenerationRequest
                
                if is_llm_chat_configured():
                    generator = TextGenerator()
                    
                    # Генерируем только недостающие дни через ИИ (первые 7 из недостающих для производительности)
                    days_to_generate_with_ai = min(7, len(dates_to_generate))
                    natal_chart_data = _format_natal_chart_for_response(natal_chart)
                    
                    for i, forecast_date in enumerate(dates_to_generate[:days_to_generate_with_ai]):
                        # Генерируем через ИИ для первых дней
                        gen_request = GenerationRequest(
                            forecast_type="daily_grounded",
                            layers=["L1", "L2"],
                            context="",
                            locale=locale
                        )
                        
                        generated = generator.generate(
                            gen_request,
                            validate=True,
                            user=user,
                            db=db,
                            target_date=forecast_date.isoformat()
                        )
                        
                        transit_forecast = await transit_service.get_daily_forecast(
                            natal_chart=natal_chart,
                            forecast_date=forecast_date,
                            birth_data=birth_data,
                            locale=locale,
                        )
                        
                        forecast_result = _build_ai_enhanced_daily_forecast(
                            transit_forecast=transit_forecast,
                            generated=generated,
                            forecast_date=forecast_date,
                            natal_chart_data=natal_chart_data,
                        )
                        
                        cache_service.save_forecast(
                            user_id=user.id,
                            astro_profile_id=astro_profile.id,
                            forecast_type="daily",
                            forecast_date=forecast_date,
                            forecast_data=forecast_result.model_dump(),
                            locale=locale,
                            use_ai=True
                        )
                        
                        forecasts.append(forecast_result)
                    
                    # Генерируем остальные дни через transit service
                    natal_chart_data = _format_natal_chart_for_response(natal_chart)
                    for forecast_date in dates_to_generate[days_to_generate_with_ai:]:
                        transit_forecast = await transit_service.get_daily_forecast(
                            natal_chart=natal_chart,
                            forecast_date=forecast_date,
                            birth_data=birth_data,
                            locale=locale,
                        )
                        transit_forecast.natal_chart = natal_chart_data
                        forecasts.append(transit_forecast)
                        
                        # Сохраняем в кеш
                        cache_service.save_forecast(
                            user_id=user.id,
                            astro_profile_id=astro_profile.id,
                            forecast_type="daily",
                            forecast_date=forecast_date,
                            forecast_data=transit_forecast.model_dump(),
                            locale=locale,
                            use_ai=False
                        )
                    
                    forecasts.sort(key=lambda x: x.date)
                    logger.debug(f"Monthly forecast: Generated {len(forecasts)} daily forecasts (cached: {30 - len(dates_to_generate)}, generated: {len(dates_to_generate)})")
                    return forecasts
            except Exception as e:
                logger.warning(f"AI generation for monthly forecast failed, falling back to transit service: {e}", exc_info=True)
                # Fallback на обычный сервис
        
        # Generate monthly forecast через transit service (fallback или если use_ai=False)
        # Генерируем только недостающие дни
        natal_chart_data = _format_natal_chart_for_response(natal_chart)
        
        for forecast_date in dates_to_generate:
            transit_forecast = await transit_service.get_daily_forecast(
                natal_chart=natal_chart,
                forecast_date=forecast_date,
                birth_data=birth_data,
                locale=locale,
            )
            
            # Добавляем натальную карту
            transit_forecast.natal_chart = natal_chart_data
            forecasts.append(transit_forecast)
            
            # Сохраняем в кеш
            cache_service.save_forecast(
                user_id=user.id,
                astro_profile_id=astro_profile.id,
                forecast_type="daily",
                forecast_date=forecast_date,
                forecast_data=transit_forecast.model_dump(),
                locale=locale,
                use_ai=False
            )
        
        forecasts.sort(key=lambda x: x.date)
        logger.debug(f"Monthly forecast: Generated {len(forecasts)} daily forecasts (cached: {30 - len(dates_to_generate)}, generated: {len(dates_to_generate)})")
        return forecasts
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Monthly forecast error for user {user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=translate("reports.errors.forecastGenerationFailed", locale=locale, default=f"Failed to generate forecast: {str(e)}")
        )


@router.get("/yearly-forecast", response_model=models.YearlyForecast)
async def get_yearly_forecast(
    request: Request,
    target_year: Optional[int] = Query(None, description="Year for forecast (defaults to current year)"),
    astro_profile_id: Optional[int] = Query(None, description="ID астро профиля для прогноза (defaults to primary)"),
    user=Depends(require_user),
    db: Session = Depends(get_session),
    transit_service: PersonalTransitService = Depends(get_personal_transit_service),
    astro_service: astro.AstroService = Depends(lambda: astro.AstroService()),
    geocoder: Geocoder = Depends(lambda: Geocoder()),
) -> models.YearlyForecast:
    """Get personalized yearly forecast based on Solar Return and transits."""
    from datetime import date
    
    locale = request_locale(request)
    
    if target_year is None:
        target_year = date.today().year
    
    # Get user's astro profile
    astro_profile = await _get_user_astro_profile(user, db, astro_profile_id, locale)
    birth_data = await _prepare_birth_data(astro_profile, geocoder, locale)
    natal_chart = await _compute_natal_chart(birth_data, astro_service, astro_profile, db)
    
    # Get birth date
    birth_date = astro_profile.birth_date
    
    # Generate yearly forecast
    forecast = await transit_service.get_yearly_forecast(
        natal_chart=natal_chart,
        target_year=target_year,
        birth_date=birth_date,
        birth_data=birth_data,
        locale=locale,
    )
    
    # Добавляем натальную карту
    natal_chart_data = _format_natal_chart_for_response(natal_chart)
    forecast.natal_chart = natal_chart_data
    
    return forecast


@router.get("/lunar-phases-forecast", response_model=models.LunarPhasesForecast)
async def get_lunar_phases_forecast(
    request: Request,
    target_month: Optional[date] = Query(None, description="Month for forecast (defaults to current month, format: YYYY-MM-DD)"),
    astro_profile_id: Optional[int] = Query(None, description="ID астро профиля для прогноза (defaults to primary)"),
    user=Depends(require_user),
    db: Session = Depends(get_session),
    transit_service: PersonalTransitService = Depends(get_personal_transit_service),
    astro_service: astro.AstroService = Depends(lambda: astro.AstroService()),
    geocoder: Geocoder = Depends(lambda: Geocoder()),
) -> models.LunarPhasesForecast:
    """Get personalized lunar phases forecast based on Lunar Return and moon phases."""
    from datetime import date
    
    locale = request_locale(request)
    
    if target_month is None:
        target_month = date.today()
    
    # Get user's astro profile
    astro_profile = await _get_user_astro_profile(user, db, astro_profile_id, locale)
    birth_data = await _prepare_birth_data(astro_profile, geocoder, locale)
    natal_chart = await _compute_natal_chart(birth_data, astro_service, astro_profile, db)
    
    # Get birth date
    birth_date = astro_profile.birth_date
    
    # Generate lunar phases forecast
    forecast = await transit_service.get_lunar_phases_forecast(
        natal_chart=natal_chart,
        target_month=target_month,
        birth_date=birth_date,
        birth_data=birth_data,
        locale=locale,
    )
    
    return forecast


@router.get("/health-analysis", response_model=models.HealthAnalysisReport)
async def get_health_analysis(
    request: Request,
    astro_profile_id: Optional[int] = Query(None, description="ID астро профиля для анализа (defaults to primary)"),
    user=Depends(require_user),
    db: Session = Depends(get_session),
    astro_service: astro.AstroService = Depends(lambda: astro.AstroService()),
    geocoder: Geocoder = Depends(lambda: Geocoder()),
) -> models.HealthAnalysisReport:
    """Get health and psychosomatic analysis based on natal chart."""
    from todayflow_backend.services.health_analysis import HealthAnalysisService
    
    locale = request_locale(request)
    
    astro_profile = await _get_user_astro_profile(user, db, astro_profile_id, locale)
    birth_data = await _prepare_birth_data(astro_profile, geocoder, locale)
    natal_chart = await _compute_natal_chart(birth_data, astro_service)
    
    health_service = HealthAnalysisService(astro_service=astro_service)
    report = await health_service.analyze_health(
        chart=natal_chart,
        locale=locale,
    )
    
    return report


# Helper functions to avoid code duplication
async def _get_user_astro_profile(
    user: db_models.User,
    db: Session,
    astro_profile_id: Optional[int],
    locale: str,
) -> db_models.AstroProfile:
    """Get user's astro profile by ID or primary."""
    if astro_profile_id:
        astro_profile = (
            db.query(db_models.AstroProfile)
            .filter(db_models.AstroProfile.id == astro_profile_id, db_models.AstroProfile.user_id == user.id)
            .first()
        )
        if not astro_profile:
            raise HTTPException(
                status_code=404,
                detail=translate("account.errors.profileNotFound", locale=locale, default="Astro profile not found")
            )
        return astro_profile
    else:
        # Get primary profile
        astro_profile = (
            db.query(db_models.AstroProfile)
            .filter(db_models.AstroProfile.user_id == user.id, db_models.AstroProfile.is_primary == True)
            .first()
        )
        if not astro_profile:
            # Try to get any profile
            astro_profile = (
                db.query(db_models.AstroProfile)
                .filter(db_models.AstroProfile.user_id == user.id)
                .first()
            )
            if not astro_profile:
                raise HTTPException(
                    status_code=404,
                    detail=translate("account.errors.noProfile", locale=locale, default="No astro profile found. Please create one.")
                )
        return astro_profile


async def _prepare_birth_data(
    astro_profile: db_models.AstroProfile,
    geocoder: Geocoder,
    locale: str,
) -> models.BirthData:
    """Prepare BirthData from AstroProfile."""
    effective_time = None
    if not getattr(astro_profile, "time_unknown", False) and astro_profile.birth_time:
        effective_time = astro_profile.birth_time.isoformat()

    birth_data = models.BirthData(
        date=astro_profile.birth_date.isoformat(),
        time=effective_time,
        location=astro_profile.location_name or "",
        coordinates=models.Coordinates(
            latitude=astro_profile.latitude if astro_profile.latitude is not None else 0.0,
            longitude=astro_profile.longitude if astro_profile.longitude is not None else 0.0,
        ) if astro_profile.latitude is not None and astro_profile.longitude is not None else None,
    )
    
    # Calculate natal chart if coordinates available
    if not birth_data.coordinates and astro_profile.location_name:
        geo = geocoder.lookup(astro_profile.location_name)
        if geo:
            birth_data.coordinates = models.Coordinates(
                latitude=geo["latitude"],
                longitude=geo["longitude"],
            )
    
    if not birth_data.coordinates:
        raise HTTPException(
            status_code=400,
            detail=translate("reports.errors.noCoordinates", locale=locale, default="Location coordinates are required for forecast")
        )
    
    return birth_data


async def _compute_natal_chart(
    birth_data: models.BirthData,
    astro_service: astro.AstroService,
    astro_profile,
    db: Session,
) -> astro.ChartResponse:
    """Compute natal chart from birth data with caching."""
    from todayflow_backend.services.natal_chart_cache import get_natal_chart_cache_service
    
    cache_service = get_natal_chart_cache_service(db)
    coordinates = {"latitude": birth_data.coordinates.latitude, "longitude": birth_data.coordinates.longitude}
    birth_payload = birth_data.model_dump(exclude={"coordinates"}, exclude_none=True)
    
    # Используем кеш: вычисляем только один раз
    return await cache_service.get_or_compute_natal_chart(
        astro_profile=astro_profile,
        astro_service=astro_service,
        birth_data=birth_payload,
        coordinates=coordinates
    )


async def try_warm_natal_chart_cache_for_profile(
    db: Session,
    astro_profile: db_models.AstroProfile,
    geocoder: Geocoder,
    locale: str,
    astro_service: astro.AstroService | None = None,
) -> None:
    """После ввода даты/времени/места рождения считает натальную карту и пишет cached_natal_charts.

    Вызывается из POST/PUT /account/astro-data, POST /account/astro-data/{id}/primary и POST /account/core-setup.
    Без координат пропускается (геокод по location_name пробуется здесь же).

    Ошибки астро-сервиса не пробрасываются — сохранение профиля не должно падать.
    """
    import logging

    logger = logging.getLogger(__name__)
    if (astro_profile.latitude is None or astro_profile.longitude is None) and astro_profile.location_name:
        geo = geocoder.lookup(astro_profile.location_name)
        if geo:
            astro_profile.latitude = geo.get("latitude")
            astro_profile.longitude = geo.get("longitude")
            db.add(astro_profile)
            db.commit()
            db.refresh(astro_profile)

    if astro_profile.latitude is None or astro_profile.longitude is None:
        logger.info("Natal cache warm skipped (no coordinates) astro_profile_id=%s", astro_profile.id)
        return

    own_client = astro_service is None
    service = astro_service or astro.AstroService()
    try:
        birth_data = await _prepare_birth_data(astro_profile, geocoder, locale)
        await _compute_natal_chart(birth_data, service, astro_profile, db)
        logger.debug("Natal cache warmed astro_profile_id=%s", astro_profile.id)
    except Exception as exc:
        logger.warning(
            "Natal cache warm failed astro_profile_id=%s: %s",
            astro_profile.id,
            exc,
            exc_info=True,
        )
    finally:
        if own_client:
            await service.close()


_ZODIAC_ORDER_EN = (
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
)

# Русские подписи знаков из движка/локали — без этого longitude не собирается и пустеют дома в API.
_ZODIAC_SIGN_TO_INDEX: dict[str, int] = {
    **{name: i for i, name in enumerate(_ZODIAC_ORDER_EN)},
    "Овен": 0,
    "Телец": 1,
    "Близнецы": 2,
    "Рак": 3,
    "Лев": 4,
    "Дева": 5,
    "Весы": 6,
    "Скорпион": 7,
    "Стрелец": 8,
    "Козерог": 9,
    "Водолей": 10,
    "Рыбы": 11,
}


def infer_ecliptic_longitude(sign: str | None, degree: float | None) -> float | None:
    """Восстановить долготу 0..360° по названию знака (en/ru) и градусу в знаке (старый кеш / ответ без longitude)."""
    if sign is None or degree is None:
        return None
    key = str(sign).strip()
    idx = _ZODIAC_SIGN_TO_INDEX.get(key)
    if idx is None:
        try:
            idx = _ZODIAC_ORDER_EN.index(key)
        except ValueError:
            return None
    return (idx * 30.0 + float(degree)) % 360.0


def infer_sign_from_longitude(longitude: Any) -> str | None:
    try:
        lon = float(longitude) % 360.0
    except (TypeError, ValueError):
        return None
    return _ZODIAC_ORDER_EN[int(lon // 30) % 12]


def _coalesce_longitude(raw_lon: Any, sign: str | None, degree: float | None) -> float | None:
    if raw_lon is not None:
        try:
            return float(raw_lon) % 360.0
        except (TypeError, ValueError):
            pass
    return infer_ecliptic_longitude(sign, degree)


def _pick_house_data(houses_dict: dict[str, Any], *keys: Any) -> dict[str, Any] | None:
    for key in keys:
        value = houses_dict.get(key)
        if isinstance(value, dict):
            return value
        str_key = str(key)
        value = houses_dict.get(str_key)
        if isinstance(value, dict):
            return value
    return None


def _pick_position_data(positions_dict: dict[str, Any], *keys: str) -> dict[str, Any] | None:
    for key in keys:
        value = positions_dict.get(key)
        if isinstance(value, dict):
            return value
    return None


def _format_natal_chart_for_response(natal_chart: astro.ChartResponse) -> dict:
    """Форматирует натальную карту для ответа API (позиции, дома, асцендент)."""
    # Формируем позиции планет
    positions_dict = {}
    for pos in natal_chart.positions:
        if isinstance(pos, dict):
            body = pos.get("body") or pos.get("name")
            if body:
                lon = _coalesce_longitude(pos.get("longitude"), pos.get("sign"), pos.get("degree"))
                positions_dict[body] = {
                    "longitude": lon,
                    "latitude": pos.get("latitude"),
                    "sign": pos.get("sign") or infer_sign_from_longitude(lon),
                    "house": pos.get("house"),
                    "degree": pos.get("degree"),
                }
    
    # Извлекаем дома и углы
    houses_dict = natal_chart.houses or {}
    ascendant = None
    mc = None
    ic = None
    descendant = None
    
    # Асцендент (1-й дом) — движок todayflow_astro кладёт куспиды в house_1..house_12
    asc_data = _pick_house_data(houses_dict, 1, "1", "house_1", "Ascendant")
    if asc_data and isinstance(asc_data, dict):
        asc_lon = _coalesce_longitude(asc_data.get("longitude"), asc_data.get("sign"), asc_data.get("degree"))
        ascendant = {
            "longitude": asc_lon,
            "sign": asc_data.get("sign") or infer_sign_from_longitude(asc_lon),
            "degree": asc_data.get("degree"),
        }
    if not ascendant:
        asc_pos = _pick_position_data(positions_dict, "Ascendant", "ASC", "rising", "Rising")
        if asc_pos:
            ascendant = {
                "longitude": asc_pos.get("longitude"),
                "sign": asc_pos.get("sign") or infer_sign_from_longitude(asc_pos.get("longitude")),
                "degree": asc_pos.get("degree"),
            }

    # MC (10-й дом)
    mc_data = _pick_house_data(houses_dict, 10, "10", "house_10", "MC", "Midheaven")
    if mc_data and isinstance(mc_data, dict):
        mc_lon = _coalesce_longitude(mc_data.get("longitude"), mc_data.get("sign"), mc_data.get("degree"))
        mc = {
            "longitude": mc_lon,
            "sign": mc_data.get("sign") or infer_sign_from_longitude(mc_lon),
            "degree": mc_data.get("degree"),
        }
    if not mc:
        mc_pos = _pick_position_data(positions_dict, "MC", "Midheaven")
        if mc_pos:
            mc = {
                "longitude": mc_pos.get("longitude"),
                "sign": mc_pos.get("sign") or infer_sign_from_longitude(mc_pos.get("longitude")),
                "degree": mc_pos.get("degree"),
            }

    # IC (4-й дом)
    ic_data = _pick_house_data(houses_dict, 4, "4", "house_4", "IC")
    if ic_data and isinstance(ic_data, dict):
        ic_lon = _coalesce_longitude(ic_data.get("longitude"), ic_data.get("sign"), ic_data.get("degree"))
        ic = {
            "longitude": ic_lon,
            "sign": ic_data.get("sign") or infer_sign_from_longitude(ic_lon),
            "degree": ic_data.get("degree"),
        }
    if not ic:
        ic_pos = _pick_position_data(positions_dict, "IC")
        if ic_pos:
            ic = {
                "longitude": ic_pos.get("longitude"),
                "sign": ic_pos.get("sign") or infer_sign_from_longitude(ic_pos.get("longitude")),
                "degree": ic_pos.get("degree"),
            }

    # Descendant (7-й дом)
    desc_data = _pick_house_data(houses_dict, 7, "7", "house_7", "Descendant")
    if desc_data and isinstance(desc_data, dict):
        desc_lon = _coalesce_longitude(desc_data.get("longitude"), desc_data.get("sign"), desc_data.get("degree"))
        descendant = {
            "longitude": desc_lon,
            "sign": desc_data.get("sign") or infer_sign_from_longitude(desc_lon),
            "degree": desc_data.get("degree"),
        }
    if not descendant:
        desc_pos = _pick_position_data(positions_dict, "Descendant", "DSC")
        if desc_pos:
            descendant = {
                "longitude": desc_pos.get("longitude"),
                "sign": desc_pos.get("sign") or infer_sign_from_longitude(desc_pos.get("longitude")),
                "degree": desc_pos.get("degree"),
            }
    
    # Формируем дома (1-12)
    houses_list = []
    for i in range(1, 13):
        house_key = str(i)
        house_data = _pick_house_data(houses_dict, i, house_key, f"house_{i}", f"{i}th", f"House{i}")
        if house_data and isinstance(house_data, dict):
            cusp_lon = _coalesce_longitude(house_data.get("longitude"), house_data.get("sign"), house_data.get("degree"))
            houses_list.append({
                "house": i,
                "cusp_longitude": cusp_lon,
                "sign": house_data.get("sign") or infer_sign_from_longitude(cusp_lon),
                "degree": house_data.get("degree"),
            })

    # Равные дома от ASC, если куспиды не пришли из движка (иначе фронт и кеш теряют сетку 1–12).
    if not houses_list and ascendant and ascendant.get("longitude") is not None:
        try:
            base = float(ascendant["longitude"]) % 360.0
        except (TypeError, ValueError):
            base = None
        if base is not None:
            zodiac_order = [
                "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
            ]
            for i in range(1, 13):
                cusp = (base + (i - 1) * 30.0) % 360.0
                sign_idx = int(cusp // 30) % 12
                deg_in_sign = cusp % 30.0
                houses_list.append({
                    "house": i,
                    "cusp_longitude": cusp,
                    "sign": zodiac_order[sign_idx],
                    "degree": deg_in_sign,
                })
    
    return {
        "positions": positions_dict,
        "houses": houses_list,
        "ascendant": ascendant,
        "mc": mc,
        "ic": ic,
        "descendant": descendant,
        "metadata": natal_chart.metadata or {}
    }
