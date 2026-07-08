"""Сбор контекста пользователя для улучшения генерации прогнозов."""

from datetime import date, datetime, timedelta, time
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from todayflow_backend.db.models import (
    User,
    UserProfile,
    AstroProfile,
    ObservationDiaryEntry,
    NumerologyProfileRecord,
    TarotDraw,
    PracticeUsage,
    ProgressTrackerEntry
)
from todayflow_backend.services.numerology import NumerologyService, get_numerology_service


def get_user_context(
    user: User,
    target_date: str,
    db: Session,
    numerology_service: Optional[NumerologyService] = None,
    needs: Optional[str] = None  # Потребности: "money", "love", "calm", "work", "health" и т.д.
) -> Dict[str, Any]:
    """
    Собирает контекст пользователя для генерации прогноза:
    - Натальная карта (AstroProfile) - индивидуальность пользователя
    - Профиль пользователя (модель, оси, модуляторы) - психологический профиль
    - Нумерология дня и личная нумерология
    - Последние записи дневника
    - Практики и активность
    - Карта таро дня (если есть)
    - Потребности пользователя (needs) - что ему нужно сейчас
    """
    context: Dict[str, Any] = {
        "user_id": user.id,
        "target_date": target_date,
        "needs": needs,  # Потребности пользователя
        "natal_chart": None,  # Натальная карта
        "profile": None,  # Психологический профиль
        "numerology": None,
        "recent_diary": [],
        "practices": [],
        "tarot_card": None,
        "activity_patterns": {}
    }
    
    # Натальная карта (AstroProfile) - индивидуальность пользователя
    astro_profile = db.query(AstroProfile).filter(
        AstroProfile.user_id == user.id,
        AstroProfile.is_primary == True
    ).first()
    
    if astro_profile:
        context["natal_chart"] = {
            "birth_date": astro_profile.birth_date.isoformat() if astro_profile.birth_date else None,
            "birth_time": astro_profile.birth_time.strftime('%H:%M') if astro_profile.birth_time else None,
            "location": astro_profile.location_name,
            "latitude": astro_profile.latitude,
            "longitude": astro_profile.longitude,
            "timezone": astro_profile.timezone_name,
            "label": astro_profile.label
        }
        
        # Пытаемся получить данные о планетах/знаках через astro service (если доступен)
        try:
            from todayflow_backend.core.config import settings
            import requests
            
            if settings.astro_service_url and astro_profile.birth_time and not astro_profile.time_unknown and astro_profile.latitude is not None and astro_profile.longitude is not None:
                birth_date = astro_profile.birth_date if isinstance(astro_profile.birth_date, date) else date.fromisoformat(str(astro_profile.birth_date))
                
                if isinstance(astro_profile.birth_time, time):
                    birth_time_str = astro_profile.birth_time.strftime("%H:%M:%S")
                else:
                    birth_time_str = str(astro_profile.birth_time)
                    if ":" not in birth_time_str:
                        birth_time_str = f"{birth_time_str}:00:00"
                
                # Используем правильный эндпоинт /chart вместо /chart/natal
                loc = (astro_profile.location_name or "").strip()
                if not loc:
                    loc = f"{astro_profile.latitude},{astro_profile.longitude}"
                astro_response = requests.post(
                    f"{settings.astro_service_url}/chart",
                    json={
                        "birth": {
                            "date": birth_date.isoformat(),
                            "time": birth_time_str,
                            "location": loc,
                        },
                        "coordinates": {
                            "latitude": astro_profile.latitude,
                            "longitude": astro_profile.longitude,
                        }
                    },
                    timeout=5
                )
                if astro_response.status_code == 200:
                    chart_data = astro_response.json()
                    # Извлекаем ключевые данные о натальной карте
                    if "positions" in chart_data:
                        planets_info = []
                        for pos in chart_data.get("positions", []):
                            if isinstance(pos, dict):
                                planets_info.append({
                                    "name": pos.get("body"),
                                    "sign": pos.get("sign"),
                                    "house": pos.get("house"),
                                    "degree": pos.get("degree")
                                })
                        if planets_info:
                            context["natal_chart"]["planets"] = planets_info
                    
                    # Солнце, Луна, Асцендент - ключевые элементы
                    if "sun" in chart_data:
                        context["natal_chart"]["sun_sign"] = chart_data["sun"].get("sign") if isinstance(chart_data["sun"], dict) else None
                    if "moon" in chart_data:
                        context["natal_chart"]["moon_sign"] = chart_data["moon"].get("sign") if isinstance(chart_data["moon"], dict) else None
                    if "ascendant" in chart_data:
                        context["natal_chart"]["ascendant"] = chart_data["ascendant"].get("sign") if isinstance(chart_data["ascendant"], dict) else None
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Failed to get astro chart data: {e}", exc_info=True)
    
    # Профиль пользователя (психологический профиль)
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if profile:
        context["profile"] = {
            "model_version": profile.model_version,
            "axes": profile.axes,  # Оси личности (например, эмоциональная обработка)
            "modulators": profile.modulators  # Модуляторы (как человек реагирует)
        }
    
    # Нумерология дня
    try:
        if numerology_service is None:
            numerology_service = get_numerology_service()
        
        # Получаем нумерологию дня
        target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
        numerology_insight = numerology_service.daily_number(
            reference_date=target_date_obj,
            locale="ru"
        )
        
        if numerology_insight:
            context["numerology"] = {
                "day_number": numerology_insight.number.value if numerology_insight.number else None,
                "day_meaning": numerology_insight.number.summary if numerology_insight.number else None,
                "day_title": numerology_insight.number.title if numerology_insight.number else None,
            }
        
        # Получаем профиль нумерологии пользователя для life_path и personal_year
        numerology_profile = db.query(NumerologyProfileRecord).filter(
            NumerologyProfileRecord.user_id == user.id
        ).order_by(NumerologyProfileRecord.created_at.desc()).first()
        
        if numerology_profile and numerology_profile.data:
            profile_data = numerology_profile.data if isinstance(numerology_profile.data, dict) else {}
            if "life_path" in profile_data and profile_data["life_path"]:
                life_path = profile_data["life_path"]
                if isinstance(life_path, dict):
                    # Может быть value или reduced_value
                    life_path_value = life_path.get("value") or life_path.get("reduced_value")
                    if life_path_value:
                        if context["numerology"] is None:
                            context["numerology"] = {}
                        context["numerology"]["life_path"] = life_path_value
            
            # Вычисляем personal_year, если есть дата рождения
            if "birth_date" in profile_data:
                try:
                    birth_date = datetime.strptime(profile_data["birth_date"], "%Y-%m-%d").date()
                    birth_day = birth_date.day
                    birth_month = birth_date.month
                    target_year = target_date_obj.year
                    personal_year_calc = numerology_service.personal_year_calc(birth_day, birth_month, target_year)
                    if personal_year_calc and personal_year_calc.output and "number" in personal_year_calc.output:
                        if context["numerology"] is None:
                            context["numerology"] = {}
                        context["numerology"]["personal_year"] = personal_year_calc.output["number"]
                except Exception:
                    pass
    except Exception as e:
        # Если нумерология недоступна, продолжаем без неё
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Failed to get numerology context: {e}", exc_info=True)
    
    # Последние записи дневника (за последние 7 дней)
    target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
    week_ago = target_date_obj - timedelta(days=7)
    
    diary_entries = db.query(ObservationDiaryEntry).filter(
        ObservationDiaryEntry.user_id == user.id,
        ObservationDiaryEntry.date >= week_ago,
        ObservationDiaryEntry.date < target_date_obj
    ).order_by(ObservationDiaryEntry.date.desc()).limit(5).all()
    
    context["recent_diary"] = [
        {
            "date": entry.date.isoformat(),
            "noticed": entry.noticed,
            "hardest": entry.hardest,
            "easier_than_expected": entry.easier_than_expected
        }
        for entry in diary_entries
    ]
    
    # Практики за последние 7 дней
    from sqlalchemy import func
    practices = db.query(PracticeUsage).filter(
        PracticeUsage.user_id == user.id,
        func.date(PracticeUsage.completed_at) >= week_ago,
        func.date(PracticeUsage.completed_at) <= target_date_obj
    ).all()
    
    practice_counts: Dict[str, int] = {}
    for practice in practices:
        practice_id = practice.practice_id or "unknown"
        practice_counts[practice_id] = practice_counts.get(practice_id, 0) + 1
    
    context["practices"] = [
        {"practice_id": pid, "count": count}
        for pid, count in sorted(practice_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    # Карта таро дня (если есть)
    tarot_draw = db.query(TarotDraw).filter(
        TarotDraw.user_id == user.id,
        TarotDraw.draw_date == target_date_obj
    ).first()
    
    if tarot_draw:
        context["tarot_card"] = {
            "card_id": tarot_draw.card_id,
            "orientation": tarot_draw.orientation
        }
    
    # Паттерны активности (стрики, частота)
    recent_tracker = db.query(ProgressTrackerEntry).filter(
        ProgressTrackerEntry.user_id == user.id,
        ProgressTrackerEntry.date >= week_ago,
        ProgressTrackerEntry.date < target_date_obj
    ).all()
    
    activity_by_type: Dict[str, List[str]] = {}
    for entry in recent_tracker:
        # Определяем тип активности из полей
        if entry.asceticism_id:
            activity_type = "asceticism"
        elif entry.affirmation_id:
            activity_type = "affirmation"
        else:
            activity_type = "unknown"
        
        if activity_type not in activity_by_type:
            activity_by_type[activity_type] = []
        activity_by_type[activity_type].append(entry.date.isoformat())
    
    context["activity_patterns"] = {
        activity_type: {
            "count": len(dates),
            "dates": dates[:3]  # Последние 3 даты
        }
        for activity_type, dates in activity_by_type.items()
    }
    
    return context
