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
        
        if cached and self._cache_usable_for_birth(astro_profile, cached, birth_data):
            return ChartResponse(
                mode="natal",
                positions=cached.positions,
                houses=cached.houses,
                metadata=cached.chart_metadata or {}
            )
        if cached:
            # Stale / TZ-less precise cache — drop rather than serve wrong ASC/houses.
            self.db.delete(cached)
            self.db.commit()

        # Вычисляем натальную карту
        chart = await astro_service.compute_chart(
            birth_payload=birth_data,
            coordinates=coordinates
        )

        # Never cache timezone_required / empty precise failures — would poison ASC/houses.
        meta = chart.metadata if isinstance(chart.metadata, dict) else {}
        if (
            str(getattr(chart, "mode", "") or "") == "timezone_required"
            or meta.get("timezone_required")
            or not (chart.positions or [])
        ):
            return chart

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

    @staticmethod
    def _cache_usable_for_birth(
        astro_profile: AstroProfile,
        cached: CachedNatalChart,
        birth_data: dict,
    ) -> bool:
        """Reject precise-time caches computed without timezone (civil-as-UT poison)."""
        time_unknown = bool(getattr(astro_profile, "time_unknown", False))
        has_time = bool(birth_data.get("time") or getattr(astro_profile, "birth_time", None))
        if time_unknown or not has_time:
            return True
        meta = cached.chart_metadata if isinstance(cached.chart_metadata, dict) else {}
        # Only trust conversion provenance on the cache itself — never borrow from
        # current birth_data (that would re-serve civil-as-UT poison after TZ backfill).
        source = str(meta.get("timezone_source") or "").strip()
        cached_tz = str(meta.get("timezone_name") or "").strip()
        profile_tz = (
            getattr(astro_profile, "timezone_name", None) or birth_data.get("timezone_name") or ""
        ).strip()
        if source not in {"iana", "offset"} and not cached_tz:
            return False
        if profile_tz and cached_tz and profile_tz != cached_tz:
            return False
        return True


def get_natal_chart_cache_service(db: Session) -> NatalChartCacheService:
    """Получить сервис кеширования натальной карты."""
    return NatalChartCacheService(db)
