"""Aspect callout endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Request

from todayflow_backend.api.auth import require_user
from todayflow_backend.core import models
from todayflow_backend.i18n import request_locale, translate
from todayflow_backend.services.aspects import AspectEngine, get_aspect_engine
from todayflow_backend.services.lite_reports import LiteReportService, get_lite_report_service

router = APIRouter(prefix="/aspects", tags=["aspects"])


@router.get("/lite", response_model=models.AspectResponse)
async def get_latest_aspects(
    request: Request,
    user=Depends(require_user),
    lite_service: LiteReportService = Depends(get_lite_report_service),
    aspect_engine: AspectEngine = Depends(get_aspect_engine),
) -> models.AspectResponse:
    """Return aspect callouts from the latest Lite report."""
    locale = request_locale(request)
    report = lite_service._get_latest_report(user)
    if not report:
        # Возвращаем пустой ответ вместо 404, чтобы фронтенд мог обработать это корректно
        return models.AspectResponse(callouts=[])
    if not report.chart_positions:
        # Возвращаем пустой ответ вместо 404
        return models.AspectResponse(callouts=[])
    return aspect_engine.callouts(report.chart_positions, locale=locale)
