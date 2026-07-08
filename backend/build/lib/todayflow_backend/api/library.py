"""My Library — сохранённые прогнозы (Web Canon v1)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from todayflow_backend.api.auth import require_user
from todayflow_backend.core import models
from todayflow_backend.db import models as db_models
from todayflow_backend.services import library as library_service

router = APIRouter(prefix="/library", tags=["library"])


@router.get("/forecasts", response_model=models.LibraryForecastsResponse)
def list_saved_forecasts(
    user: db_models.User = Depends(require_user),
) -> models.LibraryForecastsResponse:
    """Список сохранённых forecast_id пользователя."""
    saved = library_service.get_saved_forecasts(user.id)
    return models.LibraryForecastsResponse(saved=saved)


@router.post("/forecasts/toggle", response_model=models.LibraryForecastsResponse)
def toggle_saved_forecast(
    payload: models.LibraryForecastToggle,
    user: db_models.User = Depends(require_user),
) -> models.LibraryForecastsResponse:
    """Добавить прогноз в избранное или убрать. После toggle возвращаем актуальный список saved."""
    library_service.toggle_saved_forecast(user.id, payload.forecast_id)
    saved = library_service.get_saved_forecasts(user.id)
    return models.LibraryForecastsResponse(saved=saved)


@router.get("/calculations", response_model=models.LibraryCalculationsResponse)
def list_saved_calculations(
    user: db_models.User = Depends(require_user),
) -> models.LibraryCalculationsResponse:
    """Список сохранённых расчётов (calc_type, key, payload)."""
    rows = library_service.get_saved_calculations(user.id)
    items = [models.SavedCalculationItem(calc_type=r["calc_type"], key=r["key"], payload=r["payload"]) for r in rows]
    return models.LibraryCalculationsResponse(saved=items)


@router.post("/calculations/toggle", response_model=models.LibraryCalculationsResponse)
def toggle_saved_calculation(
    payload: models.LibraryCalculationToggle,
    user: db_models.User = Depends(require_user),
) -> models.LibraryCalculationsResponse:
    """Добавить расчёт в избранное или убрать. key уникален в рамках user. payload = { input, output, version }."""
    library_service.toggle_saved_calculation(user.id, payload.calc_type, payload.key, payload.payload)
    rows = library_service.get_saved_calculations(user.id)
    items = [models.SavedCalculationItem(calc_type=r["calc_type"], key=r["key"], payload=r["payload"]) for r in rows]
    return models.LibraryCalculationsResponse(saved=items)
