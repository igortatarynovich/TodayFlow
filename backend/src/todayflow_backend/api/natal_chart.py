"""API для получения натальной карты пользователя."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from todayflow_backend.api.auth import require_user
from todayflow_backend.db.session import get_session
from todayflow_backend.db.models import User
from todayflow_backend.services.natal_chart_cache import get_natal_chart_cache_service
from todayflow_backend.services.astro import AstroService
from todayflow_backend.api.reports import _get_user_astro_profile, _prepare_birth_data
from todayflow_backend.i18n import request_locale
from todayflow_backend.services.geocode import Geocoder
from todayflow_backend.services.core_profile import CoreProfileService, get_core_profile_service
from todayflow_backend.services.natal_chart_personalization import apply_profile_lens_to_natal_interpretations
from todayflow_backend.services.natal_chart_editorial import generate_natal_chart_editorial

router = APIRouter(prefix="/natal-chart", tags=["natal-chart"])


@router.get("/")
async def get_natal_chart(
    request: Request,
    astro_profile_id: int = None,
    include_interpretations: bool = True,
    user: User = Depends(require_user),
    db: Session = Depends(get_session),
    astro_service: AstroService = Depends(lambda: AstroService()),
    geocoder: Geocoder = Depends(lambda: Geocoder()),
    core_profile_service: CoreProfileService = Depends(get_core_profile_service),
):
    """
    Получить полную натальную карту пользователя (из кеша или вычислить).
    Возвращает позиции планет, дома, асцендент, MC и интерпретации.
    
    Args:
        include_interpretations: Включить интерпретации (что в каком доме значит, планеты в знаках)
    """
    locale = request_locale(request)
    
    # Get user's astro profile
    astro_profile = await _get_user_astro_profile(user, db, astro_profile_id, locale)
    
    # Сначала пробуем кеш, чтобы не падать из-за отсутствующих координат у уже рассчитанного профиля.
    cache_service = get_natal_chart_cache_service(db)
    cached = cache_service.get_cached_natal_chart(astro_profile.id)
    
    if cached:
        chart_response = cached
        from_cache = True
    else:
        # Попробуем автодозаполнить координаты по location_name перед расчетом.
        if (astro_profile.latitude is None or astro_profile.longitude is None) and astro_profile.location_name:
            geo = geocoder.lookup(astro_profile.location_name)
            if geo:
                astro_profile.latitude = geo.get("latitude")
                astro_profile.longitude = geo.get("longitude")
                db.add(astro_profile)
                db.commit()
                db.refresh(astro_profile)

        birth_data = await _prepare_birth_data(astro_profile, geocoder, locale)
        # Если нет в кеше, вычисляем
        from todayflow_backend.api.reports import _compute_natal_chart
        chart_response = await _compute_natal_chart(birth_data, astro_service, astro_profile, db)
        from_cache = False
    
    # Форматируем базовые данные
    from todayflow_backend.api.reports import _format_natal_chart_for_response
    formatted = _format_natal_chart_for_response(chart_response)
    
    result = {
        "astro_profile_id": astro_profile.id,
        **formatted,
        "cached": from_cache
    }
    
    core_profile = core_profile_service.build(db, user, astro_profile_id=astro_profile.id)

    # Добавляем интерпретации если запрошено
    if include_interpretations:
        from todayflow_backend.services.natal_chart_interpreter import get_natal_chart_interpreter
        interpreter = get_natal_chart_interpreter()
        interpretations = interpreter.interpret_full_chart(chart_response)
        interpretations = apply_profile_lens_to_natal_interpretations(interpretations, core_profile)
        result["interpretations"] = interpretations
    
    # Добавляем аспекты между планетами
    if chart_response.positions:
        from todayflow_backend.api.reports import infer_ecliptic_longitude
        from todayflow_backend.services.aspects import get_aspect_engine
        aspect_engine = get_aspect_engine()
        # Преобразуем positions в формат для aspect_engine (longitude из astro или знак+градус из кеша)
        positions_for_aspects = []
        for pos in chart_response.positions:
            if not isinstance(pos, dict) or not pos.get("body"):
                continue
            lon = pos.get("longitude")
            if lon is None:
                lon = infer_ecliptic_longitude(pos.get("sign"), pos.get("degree"))
            if lon is not None:
                positions_for_aspects.append({
                    "body": str(pos.get("body")).lower(),
                    "longitude": float(lon) % 360.0,
                })
        
        if positions_for_aspects:
            aspect_response = aspect_engine.callouts(positions_for_aspects, locale=locale)
            result["aspects"] = {
                "callouts": [
                    {
                        "aspect_id": callout.aspect_id,
                        "label": callout.label,
                        "bodies": callout.bodies,
                        "keywords": callout.keywords,
                        "description": callout.description,
                        "tension_level": callout.tension_level,
                        "polarity": callout.polarity,
                        "degrees_apart": callout.degrees_apart,
                        "orb_delta": callout.orb_delta,
                        "strength": callout.strength,
                        "integration": callout.integration
                    }
                    for callout in aspect_response.callouts
                ]
            }

    result["editorial"] = generate_natal_chart_editorial(
        db,
        user=user,
        core_profile=core_profile,
        natal_summary=core_profile.get("natal_summary") if isinstance(core_profile, dict) else None,
        interpretations=result.get("interpretations") if isinstance(result.get("interpretations"), dict) else None,
        aspects=result.get("aspects") if isinstance(result.get("aspects"), dict) else None,
        locale=locale,
    )
    
    return result
