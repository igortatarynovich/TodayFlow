"""Сервис кеширования натальной карты: вычисляем один раз и храним."""

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from todayflow_backend.db.models import CachedNatalChart, AstroProfile
from todayflow_backend.services.astro import ChartResponse, AstroService


class NatalChartCacheService:
    """Сервис для кеширования натальных карт."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_or_compute_natal_chart(
        self,
        astro_profile: AstroProfile,
        astro_service: AstroService,
        birth_data: dict,
        coordinates: dict
    ) -> ChartResponse:
        """
        Получить натальную карту из кеша или вычислить и сохранить.
        Вычисляет только один раз, затем использует кеш.
        """
        # Проверяем кеш
        cached = self.db.query(CachedNatalChart).filter(
            CachedNatalChart.astro_profile_id == astro_profile.id
        ).first()
        
        if cached:
            # Возвращаем из кеша
            return ChartResponse(
                mode="natal",
                positions=cached.positions,
                houses=cached.houses,
                metadata=cached.chart_metadata or {}
            )
        
        # Вычисляем натальную карту
        chart = await astro_service.compute_chart(
            birth_payload=birth_data,
            coordinates=coordinates
        )
        
        # Сохраняем в кеш
        cached_chart = CachedNatalChart(
            astro_profile_id=astro_profile.id,
            positions=chart.positions,
            houses=chart.houses,
            chart_metadata=chart.metadata
        )
        self.db.add(cached_chart)
        self.db.commit()
        self.db.refresh(cached_chart)
        
        return chart
    
    def get_cached_natal_chart(self, astro_profile_id: int) -> Optional[ChartResponse]:
        """Получить натальную карту из кеша без вычисления."""
        cached = self.db.query(CachedNatalChart).filter(
            CachedNatalChart.astro_profile_id == astro_profile_id
        ).first()
        
        if cached:
            return ChartResponse(
                mode="natal",
                positions=cached.positions,
                houses=cached.houses,
                metadata=cached.chart_metadata or {}
            )
        return None
    
    def invalidate_cache(self, astro_profile_id: int) -> None:
        """Удалить кеш натальной карты (например, при изменении данных профиля)."""
        cached = self.db.query(CachedNatalChart).filter(
            CachedNatalChart.astro_profile_id == astro_profile_id
        ).first()
        
        if cached:
            self.db.delete(cached)
            self.db.commit()


def get_natal_chart_cache_service(db: Session) -> NatalChartCacheService:
    """Получить сервис кеширования натальной карты."""
    return NatalChartCacheService(db)
