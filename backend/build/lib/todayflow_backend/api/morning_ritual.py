"""Ритуал начала дня: карта таро + число дня + объяснение через ИИ."""

from datetime import date, timedelta
from time import perf_counter
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from todayflow_backend.api.auth import require_user
from todayflow_backend.core import models
from todayflow_backend.i18n import request_locale
from todayflow_backend.services.tarot import TarotService
from todayflow_backend.services.numerology import NumerologyService, get_numerology_service
from todayflow_backend.services.personal_transits import PersonalTransitService, get_personal_transit_service
from todayflow_backend.services import astro
from todayflow_backend.services.geocode import Geocoder
from todayflow_backend.db.session import get_session
from todayflow_backend.core.tarot_explainer import explain_tarot_card
from todayflow_backend.core.numerology_explainer import explain_numerology_number
from todayflow_backend.api.reports import _get_user_astro_profile, _prepare_birth_data, _compute_natal_chart
from todayflow_backend.services.core_profile import CoreProfileService, get_core_profile_service
from todayflow_backend.services.interpretation_orchestrator import (
    InterpretationOrchestrator,
    get_interpretation_orchestrator,
)
from todayflow_backend.core.text_quality import has_action_verb, is_meaningful_sentence
from todayflow_backend.services.learning import get_learning_service
from todayflow_backend.services.day_logic_shared_v0 import humanize_day_focus_key
from sqlalchemy import or_

from todayflow_backend.db import models as db_models

router = APIRouter(prefix="/morning-ritual", tags=["morning-ritual"])
DAILY_FOUNDATION_PROMPT_VERSION = "daily-foundation-v3"
DAILY_RECOMMENDATION_PROMPT_VERSION = "daily-recommendation-v2"

DAILY_RECOMMENDATION_PROMPT = """Ты пишешь краткую персональную рекомендацию дня для TodayFlow.

Это не эзотерическое описание и не общий совет. Ты собираешь три вещи:
- что сегодня реально поддержит человека;
- что сегодня его быстрее всего собьет;
- куда направить первый ход.

Пиши:
- коротко;
- конкретно;
- по-человечески;
- без пустых формул и мистического тумана;
- так, будто ты говоришь с умным человеком, у которого нет времени на расплывчатые фразы и лишнюю мотивационную риторику;
- через реальные жизненные ситуации: работа, деньги, отношения, дом, тело, решения.

Не пиши:
- "будь в потоке", "слушай себя", "доверься дню";
- "не распыляйся", "держи фокус", "сохраняй внутреннюю ось", "не создавай лишний шум";
- "сегодня многое зависит от тебя", "день может принести важные осознания", "старайся сохранять баланс";
- советы, которые подходят всем;
- слишком длинные объяснения.

Правило качества:
- `what_to_do` должен звать к одному наблюдаемому действию;
- `what_to_avoid` должен предупреждать о конкретном типе срыва, а не о туманном "негативе";
- оба поля должны звучать как текст редактора продукта, а не как заготовка для гороскопа.

Верни только JSON:
{
  "what_to_do": "...",
  "what_to_avoid": "...",
  "key_focus": "general|love|career|money|family|body|dialogue|home"
}
"""

DAILY_HOROSCOPE_PROMPT = """Ты собираешь персональный стержень дня для TodayFlow.

Это не общий зодиакальный текст и не развлекательный гороскоп. Это опора конкретного дня для конкретного человека через базу его профиля:
- базовый профиль и жизненный паттерн;
- знак и личные числа;
- общий ритм дня;
- одна и та же дата, но разные жизненные сценарии.

Твоя задача:
- собрать короткий headline дня;
- объяснить, как база профиля формирует именно этот день;
- дать 5 сценариев: общий, любовь, семья, карьера, деньги;
- в каждом сценарии показать не абстракцию, а реальное проявление дня;
- дать ощущение стержня, а не просто описания;
- писать красиво, но конкретно, без эзотерического тумана.

Пиши:
- тепло, уверенно, редакторски чисто;
- короткими насыщенными абзацами;
- так, чтобы человек узнал в тексте свой день;
- с акцентом на реальные сцены: разговоры, работа, дом, близость, деньги, решения.

Не пиши:
- универсальные фразы, которые подходят всем;
- штампы вроде "будь в потоке", "доверься вселенной", "слушай энергию";
- абстрактный коучинг и язык "ресурсности";
- одинаковые формулировки между сценариями;
- длинные предисловия.

Каждый текст должен делать одно из трех:
- поддержать;
- предупредить;
- сдвинуть в ясное действие.

Если не можешь написать живо и конкретно, выбери простоту и редакторскую ясность вместо "красивости".

Верни только JSON:
{
  "headline": "...",
  "profile_prism": "...",
  "spine": {
    "day_axis": "...",
    "main_risk": "...",
    "best_mode": "...",
    "first_move": "...",
    "do_not_enter": "...",
    "next_action": {
      "href": "...",
      "label": "...",
      "kind": "profile|compatibility|question|practice|today"
    }
  },
  "scenarios": [
    {"slug": "general", "title": "Общий", "summary": "...", "focus": "..."},
    {"slug": "love", "title": "Любовь", "summary": "...", "focus": "..."},
    {"slug": "family", "title": "Семья", "summary": "...", "focus": "..."},
    {"slug": "career", "title": "Карьера", "summary": "...", "focus": "..."},
    {"slug": "money", "title": "Деньги", "summary": "...", "focus": "..."}
  ]
}
"""


class MorningRitualResponse(BaseModel):
    """Ответ с ритуалом начала дня."""
    date: str
    tarot_card: dict
    tarot_explanation: dict
    numerology_number: dict
    numerology_explanation: dict
    daily_forecast_link: Optional[str] = None  # Ссылка на прогноз дня
    daily_forecast_summary: Optional[dict] = None  # Общее резюме прогноза дня
    daily_horoscope: Optional[dict] = None  # Стержень дня как набор сценариев поверх базы профиля
    daily_horoscope_generation_log_id: Optional[int] = None
    celestial_events: Optional[dict] = None  # Луна, планеты и т.д.
    daily_recommendations: Optional[dict] = None  # Общая рекомендация по дню
    decision_engine: Optional[dict] = None  # Deterministic hero/actions/limits for Today
    core_profile: Optional[dict] = None
    consistency: Optional[dict] = None


class DailyDecisionHero(BaseModel):
    energy_score: int
    energy_label: str
    focus: list[str] = Field(default_factory=list)
    risk: str


class DailyDecisionEngine(BaseModel):
    version: str = "today-decision-v1"
    hero: DailyDecisionHero
    actions: list[str] = Field(default_factory=list)
    limits: list[str] = Field(default_factory=list)
    signals: dict[str, Any] = Field(default_factory=dict)


@router.get("/today", response_model=MorningRitualResponse)
async def get_morning_ritual(
    request: Request,
    target_date: Optional[str] = None,
    fast_mode: bool = False,
    user=Depends(require_user),
    db=Depends(get_session),
    numerology_service: NumerologyService = Depends(get_numerology_service),
    transit_service: PersonalTransitService = Depends(get_personal_transit_service),
    astro_service: astro.AstroService = Depends(lambda: astro.AstroService()),
    geocoder: Geocoder = Depends(lambda: Geocoder()),
    core_profile_service: CoreProfileService = Depends(get_core_profile_service),
    orchestrator: InterpretationOrchestrator = Depends(get_interpretation_orchestrator),
) -> MorningRitualResponse:
    """
    Ритуал начала дня: открытие карты таро и числа дня с объяснением через ИИ.
    Показывает пользователю:
    - Карту таро дня и её значение через призму его натальной карты
    - Число дня и его значение через призму его натальной карты
    - Что делать, чего избегать, какие события могут произойти и почему
    - Как день выглядит под призмой его натальной карты
    """
    if not target_date:
        target_date = date.today().isoformat()
    
    target_date_obj = date.fromisoformat(target_date) if isinstance(target_date, str) else target_date
    
    locale = request_locale(request)
    
    # Получаем карту таро дня
    tarot_service = TarotService()
    daily_draw = tarot_service.get_daily_draw(user, locale=locale)
    if not daily_draw or not daily_draw.card:
        raise HTTPException(status_code=404, detail="Карта дня не найдена")
    
    # Проверяем подписку для персонализации
    from todayflow_backend.api.practices import get_subscription_level
    subscription_level = get_subscription_level(user, db)
    is_paid = subscription_level in ["lite", "pro"] or user.is_paid
    core_profile = core_profile_service.build(db, user)
    
    # Объясняем карту таро через ИИ только вне fast_mode.
    if is_paid and not fast_mode:
        tarot_explanation = explain_tarot_card(
            user=user,
            db=db,
            card_name=daily_draw.card.name,
            orientation=daily_draw.orientation or "upright",
            target_date=target_date
        )
    else:
        # Бесплатное объяснение - базовое описание карты
        tarot_explanation = {
            "summary": daily_draw.card.upright if daily_draw.orientation == "upright" else daily_draw.card.reversed,
            "keywords": daily_draw.card.keywords or [],
            "personalized": False,
        }
    
    # Получаем число дня
    daily_insight = numerology_service.daily_number(reference_date=target_date_obj, locale=locale)
    if not daily_insight or not daily_insight.number:
        raise HTTPException(status_code=404, detail="Число дня не найдено")
    
    # Объясняем число дня через ИИ только вне fast_mode.
    if is_paid and not fast_mode:
        numerology_explanation = explain_numerology_number(
            user=user,
            db=db,
            number=daily_insight.number.value or daily_insight.number.reduced_value,
            number_type="day",
            target_date=target_date
        )
    else:
        # Бесплатное объяснение - базовое описание числа
        numerology_explanation = {
            "summary": daily_insight.number.summary or "",
            "title": daily_insight.number.title or "",
            "personalized": False,
        }
    
    # Получаем данные о небесных событиях (луна, планеты)
    celestial_events = _get_celestial_events(target_date_obj, locale)
    
    # Получаем общую рекомендацию по дню (что делать, что не делать)
    # Только для платных пользователей
    daily_recommendations = None
    if is_paid and not fast_mode:
        daily_recommendations = await _get_daily_recommendations(
            user, target_date_obj, locale, db
        )
    elif is_paid and fast_mode:
        daily_recommendations = {
            "what_to_do": "До переписки и чужих задач выбери один результат, который хочешь получить к вечеру, и сделай по нему первый короткий шаг.",
            "what_to_avoid": "Не отдавай маршрут дня чужой срочности и не обещай лишнего раньше времени.",
            "key_focus": "general",
        }
    consistency = orchestrator.build_daily_guidance(
        core_profile=core_profile,
        numerology={
            "dayNumber": daily_insight.number.value or daily_insight.number.reduced_value
        },
        needs=daily_recommendations.get("key_focus") if isinstance(daily_recommendations, dict) else None,
    )
    
    # Получаем прогноз дня (общее резюме) - для платных персонализированный, для бесплатных базовый
    daily_forecast_summary = await _get_daily_forecast_summary(
        user, target_date_obj, locale, db, transit_service, astro_service, geocoder, is_paid=is_paid, fast_mode=fast_mode
    )
    daily_horoscope, daily_horoscope_generation_log_id = await _get_daily_horoscope(
        user=user,
        target_date=target_date_obj,
        locale=locale,
        db=db,
        core_profile=core_profile,
        daily_forecast_summary=daily_forecast_summary,
        daily_recommendations=daily_recommendations,
        consistency=consistency,
    )
    decision_engine = await _build_daily_decision_engine(
        user=user,
        target_date=target_date_obj,
        locale=locale,
        db=db,
        numerology_number={
            "value": daily_insight.number.value,
            "reduced_value": daily_insight.number.reduced_value,
        },
        core_profile=core_profile,
        daily_forecast_summary=daily_forecast_summary,
        daily_recommendations=daily_recommendations,
        daily_horoscope=daily_horoscope,
        transit_service=transit_service,
        astro_service=astro_service,
        geocoder=geocoder,
    )
    
    # Автоматически создаем day_connection, если его еще нет (для удобства пользователя)
    from todayflow_backend.db.models import DayConnection
    day_connection = db.query(DayConnection).filter(
        DayConnection.user_id == user.id,
        DayConnection.date == target_date_obj
    ).first()
    
    if not day_connection:
        # Создаем новую связку дня с фокусом из прогноза (без сырого slug вроде general в UI)
        morning_focus = None
        if daily_forecast_summary:
            raw_theme = daily_forecast_summary.get("key_theme")
            if isinstance(raw_theme, str) and raw_theme.strip():
                morning_focus = humanize_day_focus_key(raw_theme.strip())
        day_connection = DayConnection(
            user_id=user.id,
            date=target_date_obj,
            morning_focus=morning_focus,
            morning_completed=False,
            day_completed=False,
            evening_completed=False,
        )
        db.add(day_connection)
        db.commit()
        db.refresh(day_connection)
    
    return MorningRitualResponse(
        date=target_date,
        tarot_card={
            "id": daily_draw.card.id,
            "name": daily_draw.card.name,
            "orientation": daily_draw.orientation,
            "meaning": daily_draw.card.upright if daily_draw.orientation == "upright" else daily_draw.card.reversed,
        },
        tarot_explanation=tarot_explanation,
        numerology_number={
            "value": daily_insight.number.value,
            "reduced_value": daily_insight.number.reduced_value,
            "title": daily_insight.number.title,
            "summary": daily_insight.number.summary,
        },
        numerology_explanation=numerology_explanation,
        daily_forecast_link=f"/forecasts/{target_date}",
        daily_forecast_summary=daily_forecast_summary,
        daily_horoscope=daily_horoscope,
        daily_horoscope_generation_log_id=daily_horoscope_generation_log_id,
        celestial_events=celestial_events,
        daily_recommendations=daily_recommendations,
        decision_engine=decision_engine,
        core_profile=core_profile,
        consistency=consistency,
    )


def _get_celestial_events(target_date: date, locale: str) -> dict:
    """Получает данные о небесных событиях дня (луна, планеты)."""
    try:
        from todayflow_backend.services.lunar import LunarService
        from datetime import datetime, timezone
        
        lunar_service = LunarService()
        # Получаем текущую фазу луны
        moon_phase = lunar_service.current_phase(locale=locale)
        
        return {
            "lunar_phase": {
                "id": moon_phase.current.id if moon_phase.current else None,
                "name": moon_phase.current.name if moon_phase.current else None,
                "themes": moon_phase.current.themes if moon_phase.current else None,
                "guidance": moon_phase.current.guidance if moon_phase.current else None,
                "keywords": moon_phase.current.keywords if moon_phase.current else [],
                "cycle_day": moon_phase.current.cycle_day if moon_phase.current else None,
                "next_phase": {
                    "name": moon_phase.next_phase.name if moon_phase.next_phase else None,
                    "date": moon_phase.next_phase.date if moon_phase.next_phase else None,
                    "in_days": moon_phase.next_phase.in_days if moon_phase.next_phase else None,
                } if moon_phase.next_phase else None,
            },
            "planets": [],  # TODO: добавить информацию о планетах
        }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to get celestial events: {e}", exc_info=True)
        return {}


async def _get_daily_recommendations(
    user,
    target_date: date,
    locale: str,
    db
) -> dict:
    """Получает общую рекомендацию по дню (что делать, что не делать)."""
    def _is_valid_recommendation_payload(payload: dict) -> bool:
        if not isinstance(payload, dict):
            return False
        what_to_do = payload.get("what_to_do")
        what_to_avoid = payload.get("what_to_avoid")
        key_focus = payload.get("key_focus")
        if not isinstance(what_to_do, str) or not isinstance(what_to_avoid, str):
            return False
        ok_do, _ = is_meaningful_sentence(what_to_do, min_words=5)
        ok_avoid, _ = is_meaningful_sentence(what_to_avoid, min_words=5)
        if not ok_do or not ok_avoid:
            return False
        if not has_action_verb(what_to_do):
            return False
        if key_focus is not None and not isinstance(key_focus, str):
            return False
        return True

    learning_service = get_learning_service()
    prompt_version = learning_service.get_or_create_prompt_version(
        db,
        module="daily_recommendation",
        version=DAILY_RECOMMENDATION_PROMPT_VERSION,
        prompt_kind="system",
        prompt_text=DAILY_RECOMMENDATION_PROMPT,
        label="daily_recommendation",
        metadata={"surface": "daily_recommendation"},
    )
    latest_snapshot = _get_latest_core_profile_snapshot(db, user.id)
    cached_generation = _load_cached_generation_response(
        db=db,
        user_id=user.id,
        module="daily_recommendation",
        target_date=target_date,
        core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
    )
    if cached_generation is not None:
        return cached_generation.normalized_response

    started_at = perf_counter()
    user_prompt = None

    try:
        from todayflow_backend.core.user_context import get_user_context
        from todayflow_backend.core.config import settings
        from todayflow_backend.core.llm_openai_compatible import (
            chat_completion_plain,
            get_openai_compatible_client,
            is_llm_chat_configured,
        )
        
        # Получаем контекст пользователя
        user_context = get_user_context(user, target_date.isoformat(), db)
        
        # Если есть ИИ, генерируем рекомендацию
        if is_llm_chat_configured():
            try:
                client = get_openai_compatible_client()
                if client is None:
                    raise RuntimeError("llm_client_unavailable")
                model_id = settings.llm_default_model
                
                # Формируем промпт на основе контекста
                prompt_parts = [
                    f"Дата: {target_date.isoformat()}",
                    "",
                    "=== ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ ===",
                ]
                
                if user_context.get("natal_chart"):
                    natal = user_context["natal_chart"]
                    if natal.get("sun_sign"):
                        prompt_parts.append(f"Солнце в {natal['sun_sign']}")
                    if natal.get("moon_sign"):
                        prompt_parts.append(f"Луна в {natal['moon_sign']}")
                    if natal.get("ascendant"):
                        prompt_parts.append(f"Асцендент в {natal['ascendant']}")
                else:
                    prompt_parts.append("Полной натальной карты нет.")

                if user_context.get("numerology"):
                    numerology = user_context["numerology"]
                    if numerology.get("day_number"):
                        prompt_parts.append(f"Число дня: {numerology['day_number']}")
                    if numerology.get("day_meaning"):
                        prompt_parts.append(f"Смысл числа дня: {numerology['day_meaning']}")

                if user_context.get("tarot_card"):
                    tarot = user_context["tarot_card"]
                    prompt_parts.append(
                        f"Карта дня: {tarot.get('card_name', 'не указана')} ({tarot.get('orientation', 'upright')})"
                    )
                
                prompt_parts.extend([
                    "",
                    "Сформируй общую рекомендацию по дню на основе профиля и контекста.",
                    "Что должно получиться:",
                    "- одно понятное действие, которое стоит сделать сегодня;",
                    "- один понятный тип поведения, которого лучше не усиливать;",
                    "- одна фокусная область дня;",
                    "Только JSON, без markdown.",
                ])
                
                user_prompt = "\n".join(prompt_parts)
                import json
                import re

                raw = chat_completion_plain(
                    client,
                    model=model_id,
                    messages=[
                        {"role": "system", "content": DAILY_RECOMMENDATION_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.65,
                    max_tokens=300,
                )
                if not raw:
                    raise ValueError("empty_llm_response")
                content = raw.strip()
                m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
                if m:
                    content = m.group(1).strip()
                
                recommendations = json.loads(content)
                if _is_valid_recommendation_payload(recommendations):
                    learning_service.log_generation(
                        db,
                        module="daily_recommendation",
                        surface="daily_recommendation",
                        user_id=user.id,
                        core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
                        prompt_version_id=prompt_version.id,
                        model=model_id,
                        locale=locale,
                        input_payload={"target_date": target_date.isoformat()},
                        system_prompt=DAILY_RECOMMENDATION_PROMPT,
                        user_prompt=user_prompt,
                        raw_response=content,
                        normalized_response=recommendations,
                        status="success",
                        used_fallback=False,
                        duration_ms=int((perf_counter() - started_at) * 1000),
                    )
                    return recommendations
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to generate recommendations with AI: {e}", exc_info=True)
        
        # Fallback: базовая рекомендация
        fallback = {
            "what_to_do": "Назови один результат дня и закрой по нему первый шаг до того, как мелкие дела разорвут внимание.",
            "what_to_avoid": "Не позволяй сообщениям, чужим просьбам и случайным задачам решить за тебя, чему этот день служит.",
            "key_focus": "general",
        }
        learning_service.log_generation(
            db,
            module="daily_recommendation",
            surface="daily_recommendation",
            user_id=user.id,
            core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
            prompt_version_id=prompt_version.id,
            model=None if user_prompt is None else settings.llm_default_model,
            locale=locale,
            input_payload={"target_date": target_date.isoformat()},
            system_prompt=DAILY_RECOMMENDATION_PROMPT,
            user_prompt=user_prompt,
            normalized_response=fallback,
            status="fallback",
            used_fallback=True,
            duration_ms=int((perf_counter() - started_at) * 1000),
        )
        return fallback
    except Exception as e:
        import logging
        from todayflow_backend.core.config import settings as _settings_for_log

        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to get daily recommendations: {e}", exc_info=True)
        fallback = {
            "what_to_do": "Назови один результат дня и закрой по нему первый шаг до того, как мелкие дела разорвут внимание.",
            "what_to_avoid": "Не позволяй сообщениям, чужим просьбам и случайным задачам решить за тебя, чему этот день служит.",
            "key_focus": "general",
        }
        learning_service.log_generation(
            db,
            module="daily_recommendation",
            surface="daily_recommendation",
            user_id=user.id,
            core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
            prompt_version_id=prompt_version.id,
            model=_settings_for_log.llm_default_model if user_prompt else None,
            locale=locale,
            input_payload={"target_date": target_date.isoformat()},
            system_prompt=DAILY_RECOMMENDATION_PROMPT,
            user_prompt=user_prompt,
            normalized_response=fallback,
            status="error",
            used_fallback=True,
            error_message=str(e),
            duration_ms=int((perf_counter() - started_at) * 1000),
        )
        return fallback


async def _get_daily_forecast_summary(
    user,
    target_date: date,
    locale: str,
    db,
    transit_service,
    astro_service,
    geocoder,
    is_paid: bool = False,
    fast_mode: bool = False,
) -> dict:
    """Получает общее резюме прогноза дня (краткая версия).
    
    Для платных - персонализированное через DayMeaning и ИИ.
    Для бесплатных - базовое описание.
    """
    try:
        # Для бесплатных - возвращаем базовое резюме
        if not is_paid:
            return {
                "summary": "Этот день не требует размаха. Он становится яснее, если выбрать один приоритет, не хвататься за все подряд и не жить в режиме мгновенного ответа на каждый сигнал.",
                "key_theme": "general",
                "intensity": 0.5,
                "direction": "neutral",
            }
        
        # Быстрый режим: только кэш/редакционный контент, без тяжелых персональных вычислений.
        if fast_mode:
            from todayflow_backend.services.forecast_cache import get_forecast_cache_service
            cache_service = get_forecast_cache_service(db)
            astro_profile = await _get_user_astro_profile(user, db, None, locale)
            cached_forecast = cache_service.get_cached_forecast(
                user_id=user.id,
                astro_profile_id=astro_profile.id if astro_profile else None,
                forecast_type="daily",
                forecast_date=target_date,
                locale=locale,
                use_ai=True,
            )
            if cached_forecast:
                forecast = models.DailyForecast(**cached_forecast)
                summary_text = _extract_forecast_summary_text(forecast)
                return {
                    "summary": summary_text or "День держится на одном внятном приоритете. Когда он выбран, остальное уже проще расставить по местам без суеты.",
                    "key_theme": _extract_forecast_focus(forecast),
                    "intensity": forecast.intensity_score,
                }

            from todayflow_backend.data import content_system
            editorial = content_system.get_daily_forecast_by_date(date=target_date.isoformat(), locale=locale)
            if editorial:
                return {
                    "summary": (editorial.get("blocks") or {}).get("theme") or "Не пытайся прожить день во все стороны сразу. Сначала доведи до движения одну важную линию, потом решай, что действительно стоит добавлять.",
                    "key_theme": "general",
                    "intensity": 0.5,
                    "direction": "neutral",
                }
            return {
                "summary": "Если с утра выбрать одну рабочую линию и не сойти с нее после первого отвлечения, день получится заметно собраннее.",
                "key_theme": "general",
                "intensity": 0.5,
                "direction": "neutral",
            }

        # Для платных - персонализированное резюме
        # Получаем натальную карту и данные для прогноза
        astro_profile = await _get_user_astro_profile(user, db, None, locale)
        birth_data = await _prepare_birth_data(astro_profile, geocoder, locale)
        natal_chart = await _compute_natal_chart(birth_data, astro_service, astro_profile, db)
        
        # Получаем прогноз дня (используем кеш если есть)
        from todayflow_backend.services.forecast_cache import get_forecast_cache_service
        cache_service = get_forecast_cache_service(db)
        cached_forecast = cache_service.get_cached_forecast(
            user_id=user.id,
            astro_profile_id=astro_profile.id,
            forecast_type="daily",
            forecast_date=target_date,
            locale=locale,
            use_ai=True
        )
        
        if cached_forecast:
            # Формируем краткое резюме из кешированного прогноза
            forecast = models.DailyForecast(**cached_forecast)
            summary_text = _extract_forecast_summary_text(forecast)
            return {
                "summary": summary_text or "У этого дня есть главная тема. Когда ты ее видишь, легче не расходовать силы на второстепенное и не спорить с ритмом дня.",
                "key_theme": _extract_forecast_focus(forecast),
                "intensity": forecast.intensity_score,
            }
        
        # Если нет кеша, формируем минимальное резюме из DayMeaning
        from todayflow_backend.services.day_meaning_builder import DayMeaningBuilder
        from todayflow_backend.services.numerology import get_numerology_service
        from todayflow_backend.services.tarot import TarotService
        
        numerology_service = get_numerology_service()
        tarot_service = TarotService()
        
        builder = DayMeaningBuilder(
            transit_service=transit_service,
            numerology_service=numerology_service,
            tarot_service=tarot_service,
        )
        
        day_meaning = await builder.build(
            user=user,
            target_date=target_date,
            natal_chart=natal_chart,
            birth_data=birth_data,
            locale=locale,
            db=db,
        )
        
        return {
            "summary": _compose_daily_summary(day_meaning),
            "key_theme": _normalize_focus_area(day_meaning.focus_area),
            "intensity": day_meaning.intensity,
            "direction": day_meaning.interpretation_direction,
        }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to get daily forecast summary: {e}", exc_info=True)
        return {
            "summary": "Сегодня не нужен широкий размах. Гораздо полезнее понять, что здесь действительно важно, и двигать именно это без распыления.",
            "key_theme": "general",
            "intensity": 0.5,
        }


def _normalize_focus_area(area: str | None) -> str:
    if area in {"work", "career"}:
        return "career"
    if area in {"identity", "self"}:
        return "general"
    if area in {"body", "health"}:
        return "body"
    if area in {"dialogue", "relationship", "relationships", "communication"}:
        return "dialogue"
    if area in {"home", "family"}:
        return "family"
    if area in {"money", "finance"}:
        return "money"
    return "general"


def _extract_forecast_summary_text(forecast: models.DailyForecast) -> str | None:
    if forecast.psychological_insights:
        first = forecast.psychological_insights[0]
        text = first.psychological_description if hasattr(first, "psychological_description") else str(first)
        if isinstance(text, str) and text.strip():
            return text.strip()
    if forecast.conscious_actions:
        first_action = forecast.conscious_actions[0]
        if isinstance(first_action, str) and first_action.strip():
            return f"Сегодня день раскрывается через конкретный шаг: {first_action.strip()}"
    return None


def _extract_forecast_focus(forecast: models.DailyForecast) -> str:
    if forecast.psychological_insights:
        first = forecast.psychological_insights[0]
        area = getattr(first, "area", None)
        if isinstance(area, str) and area.strip():
            return _normalize_focus_area(area)
    if forecast.tensions:
        area = forecast.tensions[0].get("area")
        if isinstance(area, str) and area.strip():
            return _normalize_focus_area(area)
    if forecast.resources:
        area = forecast.resources[0].get("area")
        if isinstance(area, str) and area.strip():
            return _normalize_focus_area(area)
    return "general"


def _is_valid_horoscope_payload(payload: dict) -> bool:
    if not isinstance(payload, dict):
        return False
    headline = payload.get("headline")
    profile_prism = payload.get("profile_prism")
    spine = payload.get("spine")
    scenarios = payload.get("scenarios")
    if not isinstance(headline, str) or not isinstance(profile_prism, str):
        return False
    if not isinstance(spine, dict):
        return False
    for key in ("day_axis", "main_risk", "best_mode", "first_move", "do_not_enter"):
        value = spine.get(key)
        if not isinstance(value, str):
            return False
        ok, _ = is_meaningful_sentence(value, min_words=4)
        if not ok:
            return False
    next_action = spine.get("next_action")
    if not isinstance(next_action, dict):
        return False
    if not all(isinstance(next_action.get(key), str) for key in ("href", "label", "kind")):
        return False
    if not isinstance(scenarios, list) or len(scenarios) < 5:
        return False

    expected = ["general", "love", "family", "career", "money"]
    seen: list[str] = []
    for item in scenarios:
        if not isinstance(item, dict):
            return False
        slug = item.get("slug")
        title = item.get("title")
        summary = item.get("summary")
        focus = item.get("focus")
        if not all(isinstance(value, str) for value in [slug, title, summary, focus]):
            return False
        ok_summary, _ = is_meaningful_sentence(summary, min_words=6)
        if not ok_summary:
            return False
        seen.append(slug)
    return all(slug in seen for slug in expected)


def _build_horoscope_fallback(
    core_profile: dict | None,
    daily_forecast_summary: dict | None,
    daily_recommendations: dict | None,
    consistency: dict | None,
) -> dict:
    interpretation = (core_profile or {}).get("interpretation") or {}
    daily_interpretation = (core_profile or {}).get("daily_interpretation") or {}
    person = (core_profile or {}).get("person") or {}
    astro = (core_profile or {}).get("astro") or {}
    baseline = (core_profile or {}).get("baseline") or {}

    name = person.get("first_name") or person.get("display_name") or "Твой день"
    sign = astro.get("sun_sign") or "твой знак"
    rhythm = baseline.get("rhythm_style") or "спокойный устойчивый ритм"
    focus = baseline.get("element_focus") or "понятную опору"
    summary = (daily_forecast_summary or {}).get("summary") or (
        "День складывается лучше, если не распылять внимание и сначала собрать главную линию."
    )
    what_to_do = (daily_recommendations or {}).get("what_to_do") or (
        "Сначала выбери один результат дня, а потом уже отвечай на все остальное."
    )
    what_to_avoid = (daily_recommendations or {}).get("what_to_avoid") or (
        "Не отдавай маршрут дня случайным сообщениям и чужой срочности."
    )

    deterministic_spine = _build_deterministic_spine(
        core_profile=core_profile,
        daily_forecast_summary=daily_forecast_summary,
        daily_recommendations=daily_recommendations,
        consistency=consistency,
    )

    return {
        "headline": f"{name}: сегодня день лучше раскрывается через {focus.lower()}, а не через резкие развороты и реакцию на каждый внешний сигнал.",
        "profile_prism": (
            interpretation.get("identity")
            or f"Через знак {sign.lower()} и ритм '{rhythm}' день читается не как общий фон, а как личная история о том, где тебе важнее устойчивость, чем скорость."
        ),
        "spine": deterministic_spine,
        "scenarios": [
            {
                "slug": "general",
                "title": "Общий",
                "summary": summary,
                "focus": "Главная тема дня",
            },
            {
                "slug": "love",
                "title": "Любовь",
                "summary": (
                    interpretation.get("life_areas", {}).get("love")
                    or "В близости день просит меньше догадок и больше прямоты: один честный разговор сегодня полезнее, чем длинная внутренняя интерпретация чужих сигналов."
                ),
                "focus": "Тон близости и контакта",
            },
            {
                "slug": "family",
                "title": "Семья",
                "summary": (
                    interpretation.get("life_areas", {}).get("family")
                    or "Домашние и семейные темы лучше держать в простом порядке: ясная договоренность и бытовая конкретика снизят лишнее напряжение."
                ),
                "focus": "Дом и восстановление",
            },
            {
                "slug": "career",
                "title": "Карьера",
                "summary": (
                    interpretation.get("life_areas", {}).get("career")
                    or f"В делах день лучше раскрывается через {what_to_do.lower()} Здесь не нужен широкий размах, нужен один понятный вектор."
                ),
                "focus": "Работа и решения",
            },
            {
                "slug": "money",
                "title": "Деньги",
                "summary": (
                    interpretation.get("life_areas", {}).get("money")
                    or f"Денежная линия дня чувствительна к тому, как ты оцениваешь свое время и границы. {what_to_avoid}"
                ),
                "focus": "Цена времени и устойчивость",
            },
        ],
    }


async def _get_daily_horoscope(
    user,
    target_date: date,
    locale: str,
    db,
    core_profile: dict | None,
    daily_forecast_summary: dict | None,
    daily_recommendations: dict | None,
    consistency: dict | None,
) -> tuple[dict, int | None]:
    deterministic_spine = _build_deterministic_spine(
        core_profile=core_profile,
        daily_forecast_summary=daily_forecast_summary,
        daily_recommendations=daily_recommendations,
        consistency=consistency,
    )
    fallback = _build_horoscope_fallback(core_profile, daily_forecast_summary, daily_recommendations, consistency)
    learning_service = get_learning_service()
    prompt_version = learning_service.get_or_create_prompt_version(
        db,
        module="daily_foundation",
        version=DAILY_FOUNDATION_PROMPT_VERSION,
        prompt_kind="system",
        prompt_text=DAILY_HOROSCOPE_PROMPT,
        label="daily_foundation",
        metadata={"surface": "daily_foundation"},
    )
    latest_snapshot = (
        _get_latest_core_profile_snapshot(db, user.id)
    )
    cached_generation = _load_cached_generation_response(
        db=db,
        user_id=user.id,
        module="daily_foundation",
        target_date=target_date,
        core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
    )
    if cached_generation is not None:
        cached_payload = cached_generation.normalized_response or fallback
        if _is_valid_horoscope_payload(cached_payload):
            cached_payload["spine"] = _merge_spine_with_deterministic(
                cached_payload.get("spine"),
                deterministic_spine,
            )
        else:
            cached_payload = fallback
        return cached_payload, cached_generation.id

    started_at = perf_counter()
    user_prompt = None
    model_id = None

    try:
        from todayflow_backend.core.config import settings
        from todayflow_backend.core.llm_openai_compatible import (
            chat_completion_plain,
            get_openai_compatible_client,
            is_llm_chat_configured,
        )

        if not is_llm_chat_configured():
            generation = learning_service.log_generation(
                db,
                module="daily_foundation",
                surface="daily_foundation",
                user_id=user.id,
                core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
                prompt_version_id=prompt_version.id,
                model=None,
                locale=locale,
                input_payload={"target_date": target_date.isoformat()},
                system_prompt=DAILY_HOROSCOPE_PROMPT,
                user_prompt=None,
                normalized_response=fallback,
                status="fallback",
                used_fallback=True,
                duration_ms=int((perf_counter() - started_at) * 1000),
            )
            return fallback, generation.id

        import json
        import re

        client = get_openai_compatible_client()
        if client is None:
            raise RuntimeError("llm_client_unavailable")
        model_id = settings.llm_default_model

        interpretation = (core_profile or {}).get("interpretation") or {}
        daily_interpretation = (core_profile or {}).get("daily_interpretation") or {}
        astro = (core_profile or {}).get("astro") or {}
        numerology = (core_profile or {}).get("numerology") or {}
        baseline = (core_profile or {}).get("baseline") or {}
        person = (core_profile or {}).get("person") or {}

        prompt_parts = [
            f"Дата: {target_date.isoformat()}",
            f"Локаль: {locale}",
            "=== ПРОФИЛЬ ===",
            f"Имя: {person.get('first_name') or person.get('display_name') or 'не указано'}",
            f"Знак: {astro.get('sun_sign') or 'не определен'}",
            f"Элемент: {astro.get('sun_element') or 'не определен'}",
            f"Модальность: {astro.get('sun_modality') or 'не определена'}",
            f"Число пути: {numerology.get('life_path') or 'не определено'}",
            f"Архетип: {baseline.get('archetype_seed') or 'не определен'}",
            f"Ритм: {baseline.get('rhythm_style') or 'не определен'}",
            f"Фокус: {baseline.get('element_focus') or 'не определен'}",
            "",
            "=== ИНТЕРПРЕТАЦИЯ ПРОФИЛЯ ===",
            f"Identity: {interpretation.get('identity') or ''}",
            f"Daily general lens: {(daily_interpretation.get('daily_lenses') or {}).get('general') or ''}",
            f"Daily love lens: {(daily_interpretation.get('daily_lenses') or {}).get('love') or ''}",
            f"Daily family lens: {(daily_interpretation.get('daily_lenses') or {}).get('family') or ''}",
            f"Daily career lens: {(daily_interpretation.get('daily_lenses') or {}).get('career') or ''}",
            f"Daily money lens: {(daily_interpretation.get('daily_lenses') or {}).get('money') or ''}",
            f"Love: {(interpretation.get('life_areas') or {}).get('love') or ''}",
            f"Career: {(interpretation.get('life_areas') or {}).get('career') or ''}",
            f"Money: {(interpretation.get('life_areas') or {}).get('money') or ''}",
            f"Family: {(interpretation.get('life_areas') or {}).get('family') or ''}",
            f"Sex: {(interpretation.get('life_areas') or {}).get('sex') or ''}",
            f"Kids: {(interpretation.get('life_areas') or {}).get('kids') or ''}",
            f"Body: {(interpretation.get('life_areas') or {}).get('body') or ''}",
            f"Friends: {(interpretation.get('life_areas') or {}).get('friends') or ''}",
            f"Decisions: {(interpretation.get('life_areas') or {}).get('decisions') or ''}",
            "",
            "=== КОНТЕКСТ ДНЯ ===",
            f"Общий summary дня: {(daily_forecast_summary or {}).get('summary') or ''}",
            f"Ключевая тема дня: {(daily_forecast_summary or {}).get('key_theme') or 'general'}",
            f"Что сделать: {(daily_recommendations or {}).get('what_to_do') or ''}",
            f"Чего избегать: {(daily_recommendations or {}).get('what_to_avoid') or ''}",
            f"Deterministic focus: {(consistency or {}).get('focus') or ''}",
            f"Deterministic do_focus: {(consistency or {}).get('do_focus') or ''}",
            f"Deterministic avoid_focus: {(consistency or {}).get('avoid_focus') or ''}",
            f"Deterministic tone: {(consistency or {}).get('tone') or ''}",
            "",
            "Собери день как персональный стержень по сценариям. Не пересказывай профиль буквально: покажи, как именно база этого профиля формирует сегодняшний день.",
            "Сначала выдели backbone дня: главную ось, главный риск, лучший режим проживания дня, первый ход и зону, куда сегодня лучше не заходить.",
            f"Базовый системный каркас дня, от которого нельзя отходить слишком далеко: {deterministic_spine}",
            "Верни только JSON.",
        ]
        user_prompt = "\n".join(prompt_parts)

        raw = chat_completion_plain(
            client,
            model=model_id,
            messages=[
                {"role": "system", "content": DAILY_HOROSCOPE_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=1200,
        )
        content = (raw or "").strip()
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
        if match:
            content = match.group(1).strip()
        payload = json.loads(content)
        if _is_valid_horoscope_payload(payload):
            payload["spine"] = _merge_spine_with_deterministic(payload.get("spine"), deterministic_spine)
            generation = learning_service.log_generation(
                db,
                module="daily_foundation",
                surface="daily_foundation",
                user_id=user.id,
                core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
                prompt_version_id=prompt_version.id,
                model=model_id,
                locale=locale,
                input_payload={"target_date": target_date.isoformat()},
                system_prompt=DAILY_HOROSCOPE_PROMPT,
                user_prompt=user_prompt,
                raw_response=content,
                normalized_response=payload,
                status="success",
                used_fallback=False,
                duration_ms=int((perf_counter() - started_at) * 1000),
            )
            return payload, generation.id
        generation = learning_service.log_generation(
            db,
            module="daily_foundation",
            surface="daily_foundation",
            user_id=user.id,
            core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
            prompt_version_id=prompt_version.id,
            model=model_id,
            locale=locale,
            input_payload={"target_date": target_date.isoformat()},
            system_prompt=DAILY_HOROSCOPE_PROMPT,
            user_prompt=user_prompt,
            raw_response=content,
            normalized_response=fallback,
            status="fallback",
            used_fallback=True,
            duration_ms=int((perf_counter() - started_at) * 1000),
        )
        return fallback, generation.id
    except Exception as error:
        generation = learning_service.log_generation(
            db,
            module="daily_foundation",
            surface="daily_foundation",
            user_id=user.id,
            core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
            prompt_version_id=prompt_version.id,
            model=model_id if user_prompt else None,
            locale=locale,
            input_payload={"target_date": target_date.isoformat()},
            system_prompt=DAILY_HOROSCOPE_PROMPT,
            user_prompt=user_prompt,
            normalized_response=fallback,
            status="error",
            used_fallback=True,
            error_message=str(error),
            duration_ms=int((perf_counter() - started_at) * 1000),
        )
        return fallback, generation.id


def _build_deterministic_spine(
    core_profile: dict | None,
    daily_forecast_summary: dict | None,
    daily_recommendations: dict | None,
    consistency: dict | None,
) -> dict[str, str]:
    baseline = (core_profile or {}).get("baseline") or {}
    focus = (consistency or {}).get("focus") or baseline.get("rhythm_style") or "ясный устойчивый ритм"
    do_focus = (consistency or {}).get("do_focus") or (daily_recommendations or {}).get("what_to_do") or "один понятный шаг"
    avoid_focus = (consistency or {}).get("avoid_focus") or (daily_recommendations or {}).get("what_to_avoid") or "реактивные решения и распыление"
    tone = (consistency or {}).get("tone") or "grounded"
    day_summary = (daily_forecast_summary or {}).get("summary") or "День лучше раскрывается через одну собранную линию, а не через попытку удержать всё сразу."
    key_focus = (daily_recommendations or {}).get("key_focus") or (daily_forecast_summary or {}).get("key_theme") or "general"
    focus_label_ru = humanize_day_focus_key(str(key_focus))

    tone_hint = {
        "directive": "спокойно, но с внутренним лидерством",
        "supportive": "бережно и через качество контакта",
        "structured": "структурно и без лишних переключений",
        "grounded": "ровно и без суеты",
        "neutral": "спокойно и без перегиба",
    }.get(str(tone), "ровно и без суеты")

    return {
        "day_axis": day_summary,
        "main_risk": str(avoid_focus),
        "best_mode": f"Проживать день через {focus.lower()} и действовать {tone_hint}.",
        "first_move": str(do_focus),
        "do_not_enter": (
            f"Осторожнее с темой «{focus_label_ru}», если она начинает проживаться как хаос, "
            "резкие реакции и потеря своего ритма."
        ),
        "next_action": _build_spine_next_action(key_focus=key_focus, tone=str(tone)),
    }


def _get_latest_core_profile_snapshot(db, user_id: int) -> db_models.CoreProfileSnapshot | None:
    return (
        db.query(db_models.CoreProfileSnapshot)
        .filter(db_models.CoreProfileSnapshot.user_id == user_id)
        .order_by(db_models.CoreProfileSnapshot.updated_at.desc())
        .first()
    )


def _load_cached_generation_response(
    *,
    db,
    user_id: int,
    module: str,
    target_date: date,
    core_profile_snapshot_id: int | None,
) -> db_models.GenerationLog | None:
    target_date_iso = target_date.isoformat()
    query = (
        db.query(db_models.GenerationLog)
        .filter(
            db_models.GenerationLog.user_id == user_id,
            db_models.GenerationLog.module == module,
            db_models.GenerationLog.status.in_(("success", "fallback")),
        )
        .order_by(db_models.GenerationLog.created_at.desc())
    )
    if core_profile_snapshot_id is not None:
        query = query.filter(
            db_models.GenerationLog.core_profile_snapshot_id == core_profile_snapshot_id
        )

    for generation in query.limit(20).all():
        payload = generation.input_payload or {}
        if payload.get("target_date") != target_date_iso:
            continue
        if not isinstance(generation.normalized_response, dict):
            continue
        return generation
    return None


def _merge_spine_with_deterministic(raw_spine: dict | None, deterministic_spine: dict[str, str]) -> dict[str, str]:
    payload = raw_spine if isinstance(raw_spine, dict) else {}
    return {
        "day_axis": _prefer_longer_text(payload.get("day_axis"), deterministic_spine["day_axis"]),
        "main_risk": _prefer_longer_text(payload.get("main_risk"), deterministic_spine["main_risk"]),
        "best_mode": _prefer_longer_text(payload.get("best_mode"), deterministic_spine["best_mode"]),
        "first_move": _prefer_longer_text(payload.get("first_move"), deterministic_spine["first_move"]),
        "do_not_enter": _prefer_longer_text(payload.get("do_not_enter"), deterministic_spine["do_not_enter"]),
        "next_action": _merge_next_action(payload.get("next_action"), deterministic_spine["next_action"]),
    }


def _prefer_longer_text(primary: object, fallback: str) -> str:
    if isinstance(primary, str) and len(primary.split()) >= max(4, len(fallback.split()) // 2):
        return primary
    return fallback


def _build_spine_next_action(*, key_focus: str, tone: str) -> dict[str, str]:
    normalized_focus = (key_focus or "general").lower()
    normalized_tone = (tone or "").lower()

    if normalized_focus in {"love", "dialogue"}:
        return {
            "href": "/questions/love",
            "label": "Разобрать линию любви для себя",
            "kind": "personal_love",
        }
    if normalized_focus in {"family", "home"}:
        return {
            "href": "/journal",
            "label": "Записать про семью и дом",
            "kind": "personal_family",
        }
    if normalized_focus in {"money", "career", "work"}:
        return {
            "href": "/questions/money-career",
            "label": "Разобрать ход в деньгах и карьере",
            "kind": "question",
        }
    if normalized_focus == "body" or normalized_tone in {"structured", "supportive"}:
        return {
            "href": "/practices",
            "label": "Подобрать практику на день",
            "kind": "practice",
        }
    return {
        "href": "/profile",
        "label": "Вернуться к базе профиля",
        "kind": "profile",
    }


def _merge_next_action(raw_action: object, fallback_action: dict[str, str]) -> dict[str, str]:
    if not isinstance(raw_action, dict):
        return fallback_action
    href = raw_action.get("href")
    label = raw_action.get("label")
    kind = raw_action.get("kind")
    if not all(isinstance(value, str) and value.strip() for value in [href, label, kind]):
        return fallback_action
    return {
        "href": href,
        "label": label,
        "kind": kind,
    }


async def _build_daily_decision_engine(
    *,
    user,
    target_date: date,
    locale: str,
    db,
    numerology_number: dict | None,
    core_profile: dict | None,
    daily_forecast_summary: dict | None,
    daily_recommendations: dict | None,
    daily_horoscope: dict | None,
    transit_service: PersonalTransitService,
    astro_service: astro.AstroService,
    geocoder: Geocoder,
) -> dict:
    forecast, natal_chart, transit_chart = await _load_daily_forecast_context(
        user=user,
        target_date=target_date,
        locale=locale,
        db=db,
        transit_service=transit_service,
        astro_service=astro_service,
        geocoder=geocoder,
    )
    user_state = _load_latest_user_state(db, user.id, target_date)
    previous_signal_context = _load_recent_day_signal_context(db, user.id, target_date)
    learning_context = _extract_learning_context(core_profile)
    goal_signal = _load_active_weekly_goal(db, user.id, target_date)
    discipline_signal = _load_active_discipline(db, user.id)
    house_signals = _collect_activated_house_signals(transit_chart, natal_chart)

    transit_payloads = forecast.transits if forecast else []
    energy_score, energy_signals = _calculate_decision_energy(
        transits=transit_payloads,
        personal_day=(numerology_number or {}).get("value") or (numerology_number or {}).get("reduced_value"),
        user_state=user_state,
        previous_signal_context=previous_signal_context,
    )
    energy_label = _label_energy_band(energy_score)
    focus_items, focus_signals = _select_day_focus(
        transits=transit_payloads,
        house_signals=house_signals,
        user_state=user_state,
        goal_signal=goal_signal,
        discipline_signal=discipline_signal,
        daily_forecast_summary=daily_forecast_summary,
        daily_recommendations=daily_recommendations,
        previous_signal_context=previous_signal_context,
        learning_context=learning_context,
    )
    risk_label, risk_detail = _select_day_risk(
        transits=transit_payloads,
        user_state=user_state,
        energy_score=energy_score,
        horoscope_spine=(daily_horoscope or {}).get("spine") if isinstance(daily_horoscope, dict) else None,
        previous_signal_context=previous_signal_context,
        learning_context=learning_context,
    )
    actions = _build_day_actions(
        energy_score=energy_score,
        focus_items=focus_items,
        goal_signal=goal_signal,
        discipline_signal=discipline_signal,
        daily_recommendations=daily_recommendations,
        daily_horoscope=daily_horoscope,
        previous_signal_context=previous_signal_context,
        learning_context=learning_context,
    )
    limits = _build_day_limits(
        risk_label=risk_label,
        energy_score=energy_score,
        user_state=user_state,
        discipline_signal=discipline_signal,
        daily_recommendations=daily_recommendations,
        previous_signal_context=previous_signal_context,
        learning_context=learning_context,
    )

    payload = DailyDecisionEngine(
        hero=DailyDecisionHero(
            energy_score=energy_score,
            energy_label=energy_label,
            focus=focus_items,
            risk=risk_label,
        ),
        actions=actions,
        limits=limits,
        signals={
            "energy": energy_signals,
            "focus": focus_signals,
            "risk_detail": risk_detail,
            "personal_day": (numerology_number or {}).get("value") or (numerology_number or {}).get("reduced_value"),
            "user_state": user_state,
            "previous_day_signals": previous_signal_context,
            "goal": goal_signal,
            "discipline": discipline_signal,
            "learning_context": {
                "response_style": learning_context.get("response_style"),
                "support_style": learning_context.get("support_style"),
                "dominant_topics": learning_context.get("dominant_diary_topics"),
                "dominant_lanes": learning_context.get("dominant_lanes"),
                "signal_bias": learning_context.get("signal_bias"),
            },
            "activated_houses": house_signals,
            "forecast_summary": (daily_forecast_summary or {}).get("summary"),
        },
    )
    return payload.model_dump()


async def _load_daily_forecast_context(
    *,
    user,
    target_date: date,
    locale: str,
    db,
    transit_service: PersonalTransitService,
    astro_service: astro.AstroService,
    geocoder: Geocoder,
) -> tuple[models.DailyForecast | None, Any | None, Any | None]:
    try:
        from todayflow_backend.services.forecast_cache import get_forecast_cache_service

        astro_profile = await _get_user_astro_profile(user, db, None, locale)
        if not astro_profile:
            return None, None, None

        cache_service = get_forecast_cache_service(db)
        cached_forecast = cache_service.get_cached_forecast(
            user_id=user.id,
            astro_profile_id=astro_profile.id,
            forecast_type="daily",
            forecast_date=target_date,
            locale=locale,
            use_ai=True,
        )

        birth_data = await _prepare_birth_data(astro_profile, geocoder, locale)
        natal_chart = await _compute_natal_chart(birth_data, astro_service, astro_profile, db)
        transit_chart = None
        if birth_data and birth_data.coordinates:
            transit_chart = await astro_service.compute_chart(
                birth_payload={
                    "date": target_date.isoformat(),
                    "time": "12:00",
                    "location": birth_data.location,
                },
                coordinates={
                    "latitude": birth_data.coordinates.latitude,
                    "longitude": birth_data.coordinates.longitude,
                },
            )

        if cached_forecast:
            return models.DailyForecast.model_validate(cached_forecast), natal_chart, transit_chart

        forecast = await transit_service.get_daily_forecast(
            natal_chart=natal_chart,
            forecast_date=target_date,
            birth_data=birth_data,
            locale=locale,
        )
        return forecast, natal_chart, transit_chart
    except Exception:
        return None, None, None


def _load_latest_user_state(db, user_id: int, target_date: date) -> dict[str, Any]:
    entries = (
        db.query(db_models.ProgressTrackerEntry)
        .filter(
            db_models.ProgressTrackerEntry.user_id == user_id,
            db_models.ProgressTrackerEntry.date <= target_date,
            db_models.ProgressTrackerEntry.date >= target_date - timedelta(days=3),
        )
        .order_by(
            db_models.ProgressTrackerEntry.date.desc(),
            db_models.ProgressTrackerEntry.updated_at.desc(),
        )
        .all()
    )
    for entry in entries:
        parsed = _parse_user_state(entry.state or "")
        if parsed["energy"] or parsed["stress"] or parsed["mood"] or entry.state_scale:
            parsed["date"] = entry.date.isoformat()
            parsed["state_scale"] = entry.state_scale
            return parsed
    return {"energy": None, "stress": None, "mood": None, "date": None, "state_scale": None}


def _load_recent_day_signal_context(db, user_id: int, target_date: date) -> dict[str, Any] | None:
    recent_connection = (
        db.query(db_models.DayConnection)
        .filter(
            db_models.DayConnection.user_id == user_id,
            db_models.DayConnection.date < target_date,
            db_models.DayConnection.date >= target_date - timedelta(days=7),
        )
        .order_by(db_models.DayConnection.date.desc(), db_models.DayConnection.updated_at.desc())
        .all()
    )
    for connection in recent_connection:
        signal_count = int(bool(connection.ritual_feedback)) + int(bool(connection.quick_decision_answer)) + int(bool(connection.question_of_day_answer))
        if signal_count == 0:
            continue
        return {
            "date": connection.date.isoformat(),
            "ritual_feedback": connection.ritual_feedback,
            "quick_decision_answer": connection.quick_decision_answer,
            "question_of_day_answer": connection.question_of_day_answer,
            "signal_count": signal_count,
        }
    return None


def _extract_learning_context(core_profile: dict | None) -> dict[str, Any]:
    if not isinstance(core_profile, dict):
        return {}
    living = core_profile.get("living")
    if not isinstance(living, dict):
        return {}
    learning = living.get("learning_context")
    return learning if isinstance(learning, dict) else {}


def _parse_user_state(raw_state: str) -> dict[str, str | None]:
    state = (raw_state or "").lower()

    def pick(mapping: list[tuple[str, str]]) -> str | None:
        for needle, value in mapping:
            if needle in state:
                return value
        return None

    return {
        "energy": pick([
            ("энергия: низкая", "low"),
            ("энергия: средняя", "medium"),
            ("энергия: высокая", "high"),
            ("low energy", "low"),
            ("high energy", "high"),
        ]),
        "stress": pick([
            ("стресс: высокий", "high"),
            ("стресс: средний", "medium"),
            ("стресс: низкий", "low"),
            ("stress: high", "high"),
            ("stress: low", "low"),
        ]),
        "mood": pick([
            ("настроение: хорошее", "good"),
            ("настроение: спокойное", "calm"),
            ("настроение: ровное", "steady"),
            ("настроение: напряженное", "tense"),
            ("calm", "calm"),
            ("tense", "tense"),
        ]),
    }


def _load_active_weekly_goal(db, user_id: int, target_date: date) -> dict[str, Any] | None:
    week_start = target_date - timedelta(days=target_date.weekday())
    goal = (
        db.query(db_models.WeeklyGoal)
        .filter(
            db_models.WeeklyGoal.user_id == user_id,
            db_models.WeeklyGoal.week_start == week_start,
            or_(db_models.WeeklyGoal.scope == "week", db_models.WeeklyGoal.scope.is_(None)),
        )
        .order_by(
            db_models.WeeklyGoal.completed.asc(),
            db_models.WeeklyGoal.progress_days.desc(),
            db_models.WeeklyGoal.created_at.asc(),
        )
        .first()
    )
    if not goal:
        return None
    return {
        "title": goal.title,
        "completed": bool(goal.completed),
        "progress_days": goal.progress_days,
        "last_progress_date": goal.last_progress_date.isoformat() if goal.last_progress_date else None,
    }


def _load_active_discipline(db, user_id: int) -> dict[str, Any] | None:
    ascetic = (
        db.query(db_models.AsceticContract)
        .filter(
            db_models.AsceticContract.user_id == user_id,
            db_models.AsceticContract.status == "active",
        )
        .order_by(db_models.AsceticContract.updated_at.desc())
        .first()
    )
    if ascetic:
        return {
            "type": "ascetic",
            "title": ascetic.title,
            "streak_days": ascetic.streak_days,
        }

    habit = (
        db.query(db_models.Habit)
        .filter(
            db_models.Habit.user_id == user_id,
            db_models.Habit.is_active.is_(True),
        )
        .order_by(db_models.Habit.updated_at.desc())
        .first()
    )
    if habit:
        return {
            "type": "habit",
            "title": habit.name,
            "streak_days": None,
        }
    return None


def _calculate_decision_energy(
    *,
    transits: list[dict],
    personal_day: int | None,
    user_state: dict[str, Any],
    previous_signal_context: dict[str, Any] | None,
) -> tuple[int, dict[str, Any]]:
    base = 50
    transit_delta = 0.0
    transit_notes: list[str] = []
    positive_weights = {"Mars": 10, "Sun": 8, "Jupiter": 8, "Venus": 6, "Moon": 5}
    negative_weights = {"Saturn": -10, "Neptune": -6, "Moon": -5, "Uranus": -5, "Mars": -4}
    conjunction_weights = {"Mars": 5, "Sun": 4, "Jupiter": 4, "Venus": 3, "Saturn": -6, "Neptune": -4, "Moon": 3}

    for transit in transits or []:
        planet = str(transit.get("transiting_planet") or "")
        aspect = str(transit.get("aspect") or "")
        weight = 0.0
        if aspect in {"trine", "sextile"}:
            weight = positive_weights.get(planet, 0)
        elif aspect in {"square", "opposition"}:
            weight = negative_weights.get(planet, 0)
        elif aspect == "conjunction":
            weight = conjunction_weights.get(planet, 0)
        if not weight:
            continue
        weight *= _strength_multiplier(transit.get("strength"))
        transit_delta += weight
        if len(transit_notes) < 4:
            transit_notes.append(f"{planet} {aspect} {weight:+.0f}")
    transit_delta = max(-20, min(20, round(transit_delta)))

    personal_day_delta = 0
    if personal_day in {1, 5, 8}:
        personal_day_delta = 8
    elif personal_day in {4, 6}:
        personal_day_delta = 2
    elif personal_day in {2, 7, 9}:
        personal_day_delta = -5

    state_delta = 0
    if user_state.get("energy") == "low":
        state_delta -= 10
    elif user_state.get("energy") == "high":
        state_delta += 6
    if user_state.get("stress") == "high":
        state_delta -= 10
    elif user_state.get("stress") == "medium":
        state_delta -= 4
    if user_state.get("mood") == "good":
        state_delta += 5
    elif user_state.get("mood") == "calm":
        state_delta += 2
    elif user_state.get("mood") == "tense":
        state_delta -= 4
    state_delta = max(-15, min(15, state_delta))

    signal_delta = 0
    if previous_signal_context:
        if previous_signal_context.get("ritual_feedback") == "yes":
            signal_delta += 4
        elif previous_signal_context.get("ritual_feedback") == "partial":
            signal_delta += 1
        elif previous_signal_context.get("ritual_feedback") == "no":
            signal_delta -= 4
        if previous_signal_context.get("quick_decision_answer") == "yes":
            signal_delta += 2
        elif previous_signal_context.get("quick_decision_answer") == "unclear":
            signal_delta -= 3
    signal_delta = max(-8, min(8, signal_delta))

    score = max(0, min(100, int(round(base + transit_delta + personal_day_delta + state_delta + signal_delta))))
    return score, {
        "base": base,
        "transits": int(transit_delta),
        "transit_notes": transit_notes,
        "personal_day": personal_day_delta,
        "user_state": state_delta,
        "previous_day_signals": signal_delta,
    }


def _label_energy_band(score: int) -> str:
    if score <= 30:
        return "бережный режим"
    if score <= 70:
        return "стабильный день"
    return "день действий"


def _select_day_focus(
    *,
    transits: list[dict],
    house_signals: list[dict[str, Any]],
    user_state: dict[str, Any],
    goal_signal: dict[str, Any] | None,
    discipline_signal: dict[str, Any] | None,
    daily_forecast_summary: dict | None,
    daily_recommendations: dict | None,
    previous_signal_context: dict[str, Any] | None,
    learning_context: dict[str, Any] | None,
) -> tuple[list[str], dict[str, Any]]:
    scores: dict[str, float] = {
        "работа": 0.0,
        "деньги": 0.0,
        "отношения": 0.0,
        "восстановление": 0.0,
        "завершение": 0.0,
    }
    reasons: dict[str, list[str]] = {key: [] for key in scores}

    for signal in house_signals:
        area = signal.get("area")
        if area not in scores:
            continue
        scores[area] += float(signal.get("weight", 0))
        reasons[area].append(f"дом {signal.get('house')}")

    transit_area_map = {
        "Venus": "отношения",
        "Moon": "восстановление",
        "Saturn": "работа",
        "Mars": "завершение",
        "Mercury": "работа",
        "Sun": "работа",
        "Neptune": "восстановление",
    }
    for transit in transits or []:
        area = transit_area_map.get(str(transit.get("transiting_planet") or ""))
        if not area:
            continue
        weight = 2.5 * _strength_multiplier(transit.get("strength"))
        scores[area] += weight
        reasons[area].append(f"транзит {transit.get('transiting_planet')}")

    goal_title = (goal_signal or {}).get("title") or ""
    goal_area = _classify_focus_text(goal_title)
    if goal_area in scores:
        scores[goal_area] += 6
        reasons[goal_area].append("активная цель")
    if goal_title and _looks_like_completion(goal_title):
        scores["завершение"] += 4
        reasons["завершение"].append("цель про завершение")

    key_focus = _normalize_focus_key(
        (daily_recommendations or {}).get("key_focus") or (daily_forecast_summary or {}).get("key_theme")
    )
    if key_focus in scores:
        scores[key_focus] += 5
        reasons[key_focus].append("выбранная линия дня")

    if user_state.get("stress") == "high" or user_state.get("energy") == "low":
        scores["восстановление"] += 7
        reasons["восстановление"].append("стресс/низкая энергия")
    if discipline_signal:
        scores["восстановление"] += 3
        reasons["восстановление"].append("активная дисциплина")
    if previous_signal_context:
        previous_focus = _classify_focus_text(previous_signal_context.get("question_of_day_answer"))
        if previous_focus in scores:
            scores[previous_focus] += 5
            reasons[previous_focus].append("вчерашний ответ дня")
        if previous_signal_context.get("ritual_feedback") == "no":
            scores["восстановление"] += 5
            reasons["восстановление"].append("вчерашний день не собрался")
        elif previous_signal_context.get("ritual_feedback") == "partial":
            scores["завершение"] += 3
            reasons["завершение"].append("нужно дособрать вчерашний ритм")
        if previous_signal_context.get("quick_decision_answer") == "unclear":
            scores["завершение"] += 4
            reasons["завершение"].append("вчера осталась неясность")

    learning = learning_context or {}
    signal_bias = str(learning.get("signal_bias") or "").lower()
    dominant_topics = [str(item).lower() for item in (learning.get("dominant_diary_topics") or []) if item]
    dominant_lanes = [str(item).lower() for item in (learning.get("dominant_lanes") or []) if item]

    for topic in dominant_topics[:2]:
        mapped_focus = _map_learning_topic_to_focus(topic)
        if mapped_focus in scores:
            scores[mapped_focus] += 4
            reasons[mapped_focus].append("повторяющаяся тема пользователя")

    lane_focus_map = {
        "love": "отношения",
        "money_career": "работа",
        "state": "восстановление",
        "pattern": "завершение",
        "daily": "завершение",
        "self": "восстановление",
        "decision": "завершение",
    }
    for lane in dominant_lanes[:2]:
        mapped_focus = lane_focus_map.get(lane)
        if mapped_focus in scores:
            scores[mapped_focus] += 3
            reasons[mapped_focus].append("доминирующий способ входа")

    if signal_bias == "needs_closure":
        scores["завершение"] += 5
        scores["восстановление"] += 3
        reasons["завершение"].append("пользователю сейчас важнее closure")
        reasons["восстановление"].append("нужен бережный ритм")
    elif signal_bias == "needs_clarity":
        scores["завершение"] += 4
        reasons["завершение"].append("нужно быстрее прояснять зависшее")

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    focus_items = [label for label, score in ranked if score > 0][:2]
    if not focus_items:
        focus_items = ["работа", "восстановление"]
    return focus_items, {
        "scores": {key: round(value, 2) for key, value in scores.items()},
        "reasons": {key: value[:3] for key, value in reasons.items() if value},
    }


def _select_day_risk(
    *,
    transits: list[dict],
    user_state: dict[str, Any],
    energy_score: int,
    horoscope_spine: dict | None,
    previous_signal_context: dict[str, Any] | None,
    learning_context: dict[str, Any] | None,
) -> tuple[str, str]:
    candidates: dict[str, float] = {
        "конфликт": 0.0,
        "импульсивность": 0.0,
        "ошибки": 0.0,
        "перегруз": 0.0,
        "усталость": 0.0,
    }

    for transit in transits or []:
        planet = str(transit.get("transiting_planet") or "")
        natal = str(transit.get("natal_planet") or "")
        aspect = str(transit.get("aspect") or "")
        if aspect not in {"square", "opposition", "conjunction"}:
            continue
        weight = 4 * _strength_multiplier(transit.get("strength"))
        if planet == "Mars" and natal in {"Moon", "Mercury", "Venus", "Sun"}:
            candidates["конфликт"] += weight
            candidates["импульсивность"] += weight - 0.5
        if {planet, natal} == {"Mercury", "Neptune"}:
            candidates["ошибки"] += weight + 2
        if planet == "Saturn":
            candidates["перегруз"] += weight + 1.5
        if planet == "Neptune" and natal in {"Mercury", "Sun", "Moon"}:
            candidates["ошибки"] += weight + 1
        if planet == "Moon" and natal in {"Saturn", "Mars"}:
            candidates["усталость"] += weight + 1

    if user_state.get("stress") == "high":
        candidates["конфликт"] += 3
        candidates["перегруз"] += 4
    if energy_score <= 30:
        candidates["усталость"] += 6
        candidates["перегруз"] += 2
    if previous_signal_context:
        if previous_signal_context.get("ritual_feedback") == "no":
            candidates["перегруз"] += 4
            candidates["усталость"] += 3
        elif previous_signal_context.get("ritual_feedback") == "partial":
            candidates["перегруз"] += 2
        if previous_signal_context.get("quick_decision_answer") == "unclear":
            candidates["ошибки"] += 4
            candidates["импульсивность"] += 2

    learning = learning_context or {}
    signal_bias = str(learning.get("signal_bias") or "").lower()
    support_style = str(learning.get("support_style") or "").lower()
    dominant_topics = [str(item).lower() for item in (learning.get("dominant_diary_topics") or []) if item]

    if signal_bias == "needs_clarity":
        candidates["ошибки"] += 4
        candidates["импульсивность"] += 2
    elif signal_bias == "needs_closure":
        candidates["перегруз"] += 4
        candidates["усталость"] += 2

    if "конкретных решений" in support_style or any(topic in {"работа", "деньги"} for topic in dominant_topics):
        candidates["ошибки"] += 2
    if any(topic in {"отношения", "семья"} for topic in dominant_topics):
        candidates["конфликт"] += 2

    selected = max(candidates.items(), key=lambda item: item[1])
    label = selected[0]
    detail_map = {
        "конфликт": "Главный негативный сигнал дня связан с резкими реакциями и напряжением в контакте.",
        "импульсивность": "Есть риск ответить слишком быстро и потом разбирать последствия.",
        "ошибки": "Сегодня выше вероятность путаницы, неверного чтения деталей и поспешных выводов.",
        "перегруз": "День легко превращается в давление, если взять лишнее или не сузить фронт.",
        "усталость": "Риск не в событиях, а в том, что ресурс закончится раньше, чем ты это заметишь.",
    }
    if selected[1] <= 0 and isinstance(horoscope_spine, dict):
        spine_risk = str(horoscope_spine.get("main_risk") or "").strip()
        if spine_risk:
            return _normalize_risk_label(spine_risk), spine_risk
    return label, detail_map[label]


def _build_day_actions(
    *,
    energy_score: int,
    focus_items: list[str],
    goal_signal: dict | None,
    discipline_signal: dict | None,
    daily_recommendations: dict | None,
    daily_horoscope: dict | None,
    previous_signal_context: dict[str, Any] | None,
    learning_context: dict[str, Any] | None,
) -> list[str]:
    actions: list[str] = []
    learning = learning_context or {}
    signal_bias = str(learning.get("signal_bias") or "").lower()
    support_style = str(learning.get("support_style") or "").lower()
    dominant_topics = [str(item).lower() for item in (learning.get("dominant_diary_topics") or []) if item]

    if signal_bias == "needs_closure":
        actions.append("довести один открытый контур до понятного итога")
    elif signal_bias == "needs_clarity":
        actions.append("проверить один факт перед новыми решениями")

    goal_title = (goal_signal or {}).get("title")
    if goal_title and not (goal_signal or {}).get("completed"):
        actions.append(f"сделать один шаг по цели: {_shorten_title(str(goal_title))}")

    for focus in focus_items:
        action = _action_for_focus(focus, energy_score)
        if action:
            actions.append(action)

    if discipline_signal:
        actions.append(f"удержать ритм: {_shorten_title(str(discipline_signal.get('title') or 'дисциплина'))}")
    if previous_signal_context:
        if previous_signal_context.get("quick_decision_answer") == "unclear":
            actions.append("прояснить один зависший вопрос до новых шагов")
        elif previous_signal_context.get("ritual_feedback") == "no":
            actions.append("сузить день до одного обязательного результата")

    if "конкретных решений" in support_style or any(topic in {"работа", "деньги"} for topic in dominant_topics):
        actions.append("зафиксировать один результат в цифре, письме или решении")
    if any(topic in {"отношения", "семья"} for topic in dominant_topics):
        actions.append("сказать прямо, а не достраивать в голове")

    horoscope_first_move = (
        ((daily_horoscope or {}).get("spine") or {}).get("first_move")
        if isinstance(daily_horoscope, dict)
        else None
    )
    if isinstance(horoscope_first_move, str) and 2 <= len(horoscope_first_move.split()) <= 9:
        actions.append(horoscope_first_move.strip().rstrip("."))

    fallback_do = (daily_recommendations or {}).get("what_to_do")
    if isinstance(fallback_do, str) and 2 <= len(fallback_do.split()) <= 10:
        actions.append(fallback_do.strip().rstrip("."))

    return _dedupe_short_lines(actions)[:3]


def _build_day_limits(
    *,
    risk_label: str,
    energy_score: int,
    user_state: dict[str, Any],
    discipline_signal: dict | None,
    daily_recommendations: dict | None,
    previous_signal_context: dict[str, Any] | None,
    learning_context: dict[str, Any] | None,
) -> list[str]:
    risk_map = {
        "конфликт": ["не спорить", "не отвечать резко"],
        "импульсивность": ["не принимать решения на скорости", "не реагировать с первого импульса"],
        "ошибки": ["не принимать решения без перепроверки", "не отправлять важное с первого раза"],
        "перегруз": ["не брать новое", "не пытаться вытянуть всё за раз"],
        "усталость": ["не перегружать себя", "не давить на темп"],
    }
    limits = list(risk_map.get(risk_label, []))
    learning = learning_context or {}
    signal_bias = str(learning.get("signal_bias") or "").lower()
    dominant_topics = [str(item).lower() for item in (learning.get("dominant_diary_topics") or []) if item]

    if energy_score <= 30:
        limits.append("не начинать новое")
    if user_state.get("stress") == "high":
        limits.append("не жить в режиме немедленного ответа")
    if discipline_signal:
        limits.append("не срывать ритм вечером")
    if previous_signal_context:
        if previous_signal_context.get("ritual_feedback") == "no":
            limits.append("не тащить вчерашний перегруз в новый день")
        if previous_signal_context.get("quick_decision_answer") == "unclear":
            limits.append("не решать, пока картина не ясна")

    if signal_bias == "needs_closure":
        limits.append("не открывать новые контуры без необходимости")
    elif signal_bias == "needs_clarity":
        limits.append("не решать по догадке")

    if any(topic in {"отношения", "семья"} for topic in dominant_topics):
        limits.append("не копить напряжение молча")
    if any(topic in {"работа", "деньги"} for topic in dominant_topics):
        limits.append("не обещать больше, чем помещается в день")

    fallback_avoid = (daily_recommendations or {}).get("what_to_avoid")
    if isinstance(fallback_avoid, str) and 2 <= len(fallback_avoid.split()) <= 10:
        limits.append(fallback_avoid.strip().rstrip("."))

    return _dedupe_short_lines(limits)[:3]


def _strength_multiplier(strength: object) -> float:
    return {
        "exact": 1.0,
        "strong": 0.85,
        "medium": 0.65,
        "weak": 0.4,
    }.get(str(strength or "").lower(), 0.5)


def _classify_focus_text(raw: str | None) -> str | None:
    text = (raw or "").lower()
    if not text:
        return None
    if any(token in text for token in ["деньг", "доход", "финанс", "оплат", "бюдж"]):
        return "деньги"
    if any(token in text for token in ["отнош", "люб", "сем", "контакт", "партнер"]):
        return "отношения"
    if any(token in text for token in ["восстанов", "здоров", "состоя", "сон", "ритм", "энерг"]):
        return "восстановление"
    if any(token in text for token in ["закры", "заверш", "довест", "хвост"]):
        return "завершение"
    if any(token in text for token in ["работ", "карьер", "дел", "задач", "проект"]):
        return "работа"
    return None


def _map_learning_topic_to_focus(raw: str | None) -> str | None:
    topic = (raw or "").lower()
    if topic in {"отношения", "семья"}:
        return "отношения"
    if topic == "состояние":
        return "восстановление"
    if topic == "работа":
        return "работа"
    if topic == "деньги":
        return "деньги"
    return None


def _looks_like_completion(raw: str) -> bool:
    text = (raw or "").lower()
    return any(token in text for token in ["заверш", "закры", "довест", "хвост"])


def _normalize_focus_key(raw: str | None) -> str | None:
    value = (raw or "").lower()
    mapping = {
        "career": "работа",
        "work": "работа",
        "money": "деньги",
        "love": "отношения",
        "family": "отношения",
        "dialogue": "отношения",
        "body": "восстановление",
        "home": "отношения",
        "general": None,
    }
    return mapping.get(value, _classify_focus_text(value))


def _collect_activated_house_signals(transit_chart: Any | None, natal_chart: Any | None) -> list[dict[str, Any]]:
    if not transit_chart or not natal_chart:
        return []
    houses = getattr(natal_chart, "houses", None) or {}
    positions = getattr(transit_chart, "positions", None) or []
    house_weights: dict[int, float] = {}
    tracked_planets = {
        "Sun": 2.5,
        "Moon": 2.5,
        "Mercury": 1.5,
        "Venus": 2.0,
        "Mars": 2.0,
        "Saturn": 1.5,
    }
    for position in positions:
        planet = position.get("body")
        longitude = position.get("longitude")
        if planet not in tracked_planets or longitude is None:
            continue
        house_num = _calculate_house_for_longitude(float(longitude), houses)
        if house_num is None:
            continue
        house_weights[house_num] = house_weights.get(house_num, 0.0) + tracked_planets[planet]

    mapping = {
        10: "работа",
        2: "деньги",
        7: "отношения",
        6: "восстановление",
        4: "отношения",
        1: "восстановление",
    }
    ranked = sorted(house_weights.items(), key=lambda item: item[1], reverse=True)
    result: list[dict[str, Any]] = []
    for house_num, weight in ranked[:3]:
        area = mapping.get(house_num)
        if not area:
            continue
        result.append({"house": house_num, "area": area, "weight": round(weight, 2)})
    return result


def _calculate_house_for_longitude(longitude: float, houses: dict[str, Any]) -> int | None:
    if not houses:
        return None
    cusps: list[tuple[int, float]] = []
    for house_num in range(1, 13):
        house_key = str(house_num)
        raw = (
            houses.get(house_key)
            or houses.get(f"house{house_key}")
            or houses.get(f"{house_key}th")
            or houses.get(f"House{house_key}")
        )
        if raw is None:
            continue
        cusp = None
        if isinstance(raw, dict):
            cusp = raw.get("longitude") or raw.get("cusp") or raw.get("cusp_longitude") or raw.get("position")
        elif isinstance(raw, (int, float)):
            cusp = raw
        elif isinstance(raw, str):
            try:
                cusp = float(raw)
            except (TypeError, ValueError):
                cusp = None
        if cusp is not None:
            cusps.append((house_num, float(cusp) % 360))
    if len(cusps) < 10:
        return None

    cusps.sort(key=lambda item: item[1])
    normalized_longitude = longitude % 360
    for index, (house_num, cusp) in enumerate(cusps):
        next_house, next_cusp = cusps[(index + 1) % len(cusps)]
        if cusp > next_cusp:
            if normalized_longitude >= cusp or normalized_longitude < next_cusp:
                return house_num
        elif cusp <= normalized_longitude < next_cusp:
            return house_num
    return cusps[0][0] if cusps else None


def _normalize_risk_label(raw: str) -> str:
    text = (raw or "").lower()
    if any(token in text for token in ["конфликт", "ссора", "резк"]):
        return "конфликт"
    if any(token in text for token in ["импульс", "спеш", "на скорости"]):
        return "импульсивность"
    if any(token in text for token in ["ошиб", "путан", "невер", "перепров"]):
        return "ошибки"
    if any(token in text for token in ["перегруз", "давлен", "слишком много"]):
        return "перегруз"
    if any(token in text for token in ["устал", "ресурс", "сил"]):
        return "усталость"
    return "импульсивность"


def _action_for_focus(focus: str, energy_score: int) -> str | None:
    if focus == "работа":
        return "двинуть одну ключевую рабочую задачу" if energy_score > 70 else "закрыть одну рабочую задачу"
    if focus == "деньги":
        return "довести до решения один денежный вопрос"
    if focus == "отношения":
        return "выйти в один прямой разговор вместо догадок"
    if focus == "восстановление":
        return "оставить один обязательный шаг и снизить темп"
    if focus == "завершение":
        return "закрыть один хвост до вечера"
    return None


def _shorten_title(raw: str, limit: int = 44) -> str:
    title = " ".join((raw or "").split())
    if len(title) <= limit:
        return title
    return f"{title[:limit - 1].rstrip()}…"


def _dedupe_short_lines(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        normalized = " ".join((item or "").strip().split())
        if not normalized:
            continue
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(normalized)
    return result


def _compose_daily_summary(day_meaning) -> str:
    direction = getattr(day_meaning, "interpretation_direction", None)
    focus_area = getattr(day_meaning, "focus_area", None)
    intensity = getattr(day_meaning, "intensity", 0.5) or 0.5

    direction_text = {
        "tension": "не стоит отвечать миру слишком быстро: сегодня цена поспешных реакций выше обычного",
        "release": "день помогает отпустить старое напряжение и перестать тащить то, что уже не работает",
        "transition": "день идет через сдвиг, поэтому привычный способ действий может ощущаться тесным",
        "neutral": "фон дня ровнее обычного, и многое зависит не от внешней драмы, а от того, как ты расставишь приоритеты",
        "fixation": "одна тема может занять слишком много места, если вовремя не вернуть себе масштаб",
    }.get(direction or "neutral", "день читается лучше, когда не суетишься и не пытаешься сразу охватить все")

    focus_text = {
        "work": "Больше всего внимания сегодня просят задачи, роль и то, на что ты тратишь лучшие часы дня.",
        "career": "Больше всего внимания сегодня просят задачи, роль и то, на что ты тратишь лучшие часы дня.",
        "body": "Главная тема дня проходит через тело, режим и честный разговор с собой о ресурсе.",
        "dialogue": "Ключевые события дня будут раскрываться через разговоры, договоренности и интонацию общения.",
        "family": "Сегодня многое решается дома и рядом с близкими: не только делами, но и атмосферой.",
        "home": "Сегодня многое решается дома и рядом с близкими: не только делами, но и атмосферой.",
        "money": "День особенно ясно показывает цену времени, денег и решений, которые ты откладывала.",
    }.get(focus_area or "general", "День становится понятнее, когда перестаешь отвечать на все подряд и выбираешь одну главную линию.")

    intensity_tail = (
        " Темп стоит держать простым: не раздувать список задач и не пытаться закрыть всю жизнь за один день."
        if intensity >= 0.72
        else " Здесь сильнее сработает один точный шаг, чем россыпь мелких действий без результата."
        if intensity >= 0.45
        else " От тебя не требуется рывок: спокойная работа и внимательность к деталям дадут больше, чем лишний нажим."
    )

    return f"Сегодня {direction_text}. {focus_text}{intensity_tail}"
