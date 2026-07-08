"""API эндпоинты для генерации текстов прогнозов."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from todayflow_backend.api.auth import require_user
from todayflow_backend.db.session import get_session
from todayflow_backend.db.models import User
from todayflow_backend.core.text_generator import (
    TextGenerator,
    GenerationRequest,
    GeneratedForecast
)

router = APIRouter(prefix="/generate", tags=["generation"])


class ForecastGenerationRequest(BaseModel):
    """Запрос на генерацию прогноза."""
    forecast_type: str  # daily_grounded, workday_focus, etc.
    date: str  # YYYY-MM-DD
    locale: str = "ru"
    layers: List[str]  # L1, L2, L3, etc.
    context: Optional[str] = None  # work, relationship, money, body
    params: Optional[Dict[str, str]] = None  # trigger, emotion, reaction
    style: Optional[Dict[str, Any]] = None  # length, structure


class ForecastGenerationResponse(BaseModel):
    """Ответ с сгенерированным прогнозом."""
    theme: str
    what_you_may_notice: List[str]  # notice
    practical_scene: List[str]  # scene
    micro_action: str
    markers: Dict[str, List[str]]
    tags: List[str]
    quality: Dict[str, Any]  # score, violations, ok


@router.post("/forecast", response_model=ForecastGenerationResponse)
def generate_forecast(
    request: ForecastGenerationRequest,
    current_user: User = Depends(require_user),
    db = Depends(get_session)
):
    """Генерирует прогноз на основе запроса."""
    generator = TextGenerator()
    
    # Формируем запрос для генератора
    # Исправляем context: если передан в params, используем его, иначе из request.context
    context_value = None
    if request.params and request.params.get('context'):
        context_value = request.params.get('context')
    elif request.context:
        context_value = request.context
    
    gen_request = GenerationRequest(
        forecast_type=request.forecast_type,
        layers=request.layers,
        context=context_value or "",
        trigger=request.params.get('trigger') if request.params else None,
        emotion=request.params.get('emotion') if request.params else None,
        reaction=request.params.get('reaction') if request.params else None,
        locale=request.locale,
        style=request.style
    )
    
    # Генерируем прогноз с контекстом пользователя
    try:
        forecast = generator.generate(
            gen_request, 
            validate=True,
            user=current_user,
            db=db,
            target_date=request.date
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[GENERATE ERROR] {str(e)}")
        print(f"[GENERATE TRACEBACK] {error_trace}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка генерации: {str(e)}"
        )
    
    # Формируем ответ
    return ForecastGenerationResponse(
        theme=forecast.blocks.get('theme', ''),
        what_you_may_notice=forecast.blocks.get('notice', []),
        practical_scene=forecast.blocks.get('scene', []),
        micro_action=forecast.blocks.get('micro_action', ''),
        markers=forecast.markers,
        tags=forecast.tags,
        quality=forecast.quality
    )


class NumerologyGenerationRequest(BaseModel):
    """Запрос на генерацию значения нумерологии."""
    number: int
    number_type: str  # life_path, birthday, personal_year, etc.
    locale: str = "ru"


@router.post("/numerology_meaning", response_model=Dict[str, Any])
def generate_numerology_meaning(
    request: NumerologyGenerationRequest,
    current_user: User = Depends(require_user),
    db = Depends(get_session)
):
    """Генерирует значение нумерологии."""
    # TODO: Реализовать генерацию значений нумерологии
    # Пока возвращаем заглушку
    return {
        "number": request.number,
        "number_type": request.number_type,
        "meaning": "Генерация значений нумерологии будет реализована позже",
        "locale": request.locale
    }


class RegenerateRequest(BaseModel):
    """Запрос на перегенерацию с изменением параметров."""
    original_forecast: Dict[str, Any]  # Исходный прогноз
    changes: Dict[str, Any]  # Изменения параметров
    locale: str = "ru"


@router.post("/regenerate", response_model=ForecastGenerationResponse)
def regenerate_forecast(
    request: RegenerateRequest,
    current_user: User = Depends(require_user),
    db = Depends(get_session)
):
    """Перегенерирует прогноз с изменением параметров."""
    # Извлекаем параметры из исходного прогноза
    original = request.original_forecast
    
    # Применяем изменения
    forecast_type = request.changes.get('forecast_type', original.get('forecast_type', 'daily_grounded'))
    layers = request.changes.get('layers', original.get('layers', ['L1', 'L2']))
    context = request.changes.get('context', original.get('context'))
    
    generator = TextGenerator()
    
    gen_request = GenerationRequest(
        forecast_type=forecast_type,
        layers=layers,
        context=context,
        locale=request.locale
    )
    
    try:
        forecast = generator.generate(gen_request, validate=True)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка перегенерации: {str(e)}"
        )
    
    return ForecastGenerationResponse(
        theme=forecast.blocks.get('theme', ''),
        what_you_may_notice=forecast.blocks.get('notice', []),
        practical_scene=forecast.blocks.get('scene', []),
        micro_action=forecast.blocks.get('micro_action', ''),
        markers=forecast.markers,
        tags=forecast.tags,
        quality=forecast.quality
    )
