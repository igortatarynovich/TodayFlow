"""Сервис кеширования прогнозов: храним сгенерированные прогнозы."""

from datetime import date, datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from todayflow_backend.db.models import CachedForecast


class ForecastCacheService:
    """Сервис для кеширования прогнозов."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_cached_forecast(
        self,
        user_id: int,
        astro_profile_id: int,
        forecast_type: str,  # 'daily', 'weekly', 'monthly', 'yearly'
        forecast_date: date,
        locale: str = "ru",
        use_ai: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Получить прогноз из кеша."""
        cached = self.db.query(CachedForecast).filter(
            and_(
                CachedForecast.user_id == user_id,
                CachedForecast.astro_profile_id == astro_profile_id,
                CachedForecast.forecast_type == forecast_type,
                CachedForecast.forecast_date == forecast_date,
                CachedForecast.locale == locale,
                CachedForecast.use_ai == use_ai
            )
        ).first()
        
        if cached:
            return cached.forecast_data
        
        return None
    
    def save_forecast(
        self,
        user_id: int,
        astro_profile_id: int,
        forecast_type: str,
        forecast_date: date,
        forecast_data: Dict[str, Any],
        locale: str = "ru",
        use_ai: bool = False
    ) -> None:
        """Сохранить прогноз в кеш."""
        # Проверяем, есть ли уже кеш
        existing = self.db.query(CachedForecast).filter(
            and_(
                CachedForecast.user_id == user_id,
                CachedForecast.astro_profile_id == astro_profile_id,
                CachedForecast.forecast_type == forecast_type,
                CachedForecast.forecast_date == forecast_date,
                CachedForecast.locale == locale,
                CachedForecast.use_ai == use_ai
            )
        ).first()
        
        if existing:
            # Обновляем существующий
            existing.forecast_data = forecast_data
            existing.updated_at = datetime.utcnow()
        else:
            # Создаём новый
            cached = CachedForecast(
                user_id=user_id,
                astro_profile_id=astro_profile_id,
                forecast_type=forecast_type,
                forecast_date=forecast_date,
                locale=locale,
                use_ai=use_ai,
                forecast_data=forecast_data
            )
            self.db.add(cached)
        
        self.db.commit()
    
    def invalidate_user_forecasts(self, user_id: int, forecast_type: Optional[str] = None) -> None:
        """Удалить кеш прогнозов пользователя (опционально по типу)."""
        query = self.db.query(CachedForecast).filter(
            CachedForecast.user_id == user_id
        )
        
        if forecast_type:
            query = query.filter(CachedForecast.forecast_type == forecast_type)
        
        cached_forecasts = query.all()
        for cached in cached_forecasts:
            self.db.delete(cached)
        
        self.db.commit()


def get_forecast_cache_service(db: Session) -> ForecastCacheService:
    """Получить сервис кеширования прогнозов."""
    return ForecastCacheService(db)
