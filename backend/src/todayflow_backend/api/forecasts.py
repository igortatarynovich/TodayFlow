"""Daily Forecast (Web Canon v1) — редакционный контент на дату.

GET /forecasts?locale=&from=&to=
GET /forecasts/by-date?date=&locale=
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query

from todayflow_backend.data import content_system

router = APIRouter(prefix="/forecasts", tags=["forecasts"])


@router.get("", response_model=List[Dict[str, Any]])
def list_forecasts(
    locale: Optional[str] = Query(None, description="Filter by locale (ru, en)"),
    from_date: Optional[str] = Query(None, description="From date YYYY-MM-DD"),
    to_date: Optional[str] = Query(None, description="To date YYYY-MM-DD"),
    published_only: bool = Query(True, description="Only published + Quality Gate passed"),
) -> List[Dict[str, Any]]:
    """Список DailyForecast. Фильтр по locale, from_date, to_date."""
    return content_system.load_daily_forecasts(
        locale=locale,
        from_date=from_date,
        to_date=to_date,
        published_only=published_only,
    )


@router.get("/by-date", response_model=Dict[str, Any])
def get_forecast_by_date(
    date: str = Query(..., description="Date YYYY-MM-DD"),
    locale: str = Query(..., description="Locale (ru, en)"),
) -> Dict[str, Any]:
    """Один DailyForecast по дате и языку. Только published + Quality Gate passed."""
    out = content_system.get_daily_forecast_by_date(date=date, locale=locale)
    if out is None:
        raise HTTPException(status_code=404, detail="forecast_not_found")
    return out
