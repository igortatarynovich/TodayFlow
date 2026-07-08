"""Thematic report endpoints (Career, Family, Children)."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from todayflow_backend.api.auth import require_user
from todayflow_backend.core import models
from todayflow_backend.db import models as db_models
from todayflow_backend.db.session import get_session
from todayflow_backend.i18n import request_locale, translate
from todayflow_backend.services.thematic_reports import ThematicReportService

router = APIRouter(prefix="/reports/thematic", tags=["reports"])


def get_thematic_report_service() -> ThematicReportService:
    """Dependency to get thematic report service."""
    return ThematicReportService()


@router.post("/career", response_model=models.ThematicReport)
async def generate_career_report(
    request: Request,
    payload: models.BirthData,
    user=Depends(require_user),
    service: ThematicReportService = Depends(get_thematic_report_service),
) -> models.ThematicReport:
    """Generate a career-focused thematic report."""
    locale = request_locale(request)
    return await service.generate_career_report(payload, user, locale=locale)


@router.post("/family", response_model=models.ThematicReport)
async def generate_family_report(
    request: Request,
    payload: models.BirthData,
    user=Depends(require_user),
    service: ThematicReportService = Depends(get_thematic_report_service),
) -> models.ThematicReport:
    """Generate a family-focused thematic report."""
    locale = request_locale(request)
    return await service.generate_family_report(payload, user, locale=locale)


@router.post("/children", response_model=models.ThematicReport)
async def generate_children_report(
    request: Request,
    payload: models.BirthData,
    user=Depends(require_user),
    service: ThematicReportService = Depends(get_thematic_report_service),
) -> models.ThematicReport:
    """Generate a children-focused thematic report."""
    locale = request_locale(request)
    return await service.generate_children_report(payload, user, locale=locale)


@router.post("/love", response_model=models.ThematicReport)
async def generate_love_report(
    request: Request,
    payload: models.BirthData,
    user=Depends(require_user),
    service: ThematicReportService = Depends(get_thematic_report_service),
) -> models.ThematicReport:
    """Generate a love/romantic relationships-focused thematic report."""
    locale = request_locale(request)
    return await service.generate_love_report(payload, user, locale=locale)


@router.get("/career", response_model=models.ThematicReport)
async def get_career_report(
    request: Request,
    user=Depends(require_user),
    db: Session = Depends(get_session),
) -> models.ThematicReport:
    """Get the latest career report for the user."""
    locale = request_locale(request)
    report = (
        db.query(db_models.GeneratedReport)
        .filter_by(user_id=user.id, product_type="thematic_career")
        .order_by(db_models.GeneratedReport.created_at.desc())
        .first()
    )
    if not report:
        raise HTTPException(
            status_code=404, detail=translate("reports.thematic.career.notFound", locale=locale, default="Career report not found")
        )
    return models.ThematicReport(**report.data)


@router.get("/family", response_model=models.ThematicReport)
async def get_family_report(
    request: Request,
    user=Depends(require_user),
    db: Session = Depends(get_session),
) -> models.ThematicReport:
    """Get the latest family report for the user."""
    locale = request_locale(request)
    report = (
        db.query(db_models.GeneratedReport)
        .filter_by(user_id=user.id, product_type="thematic_family")
        .order_by(db_models.GeneratedReport.created_at.desc())
        .first()
    )
    if not report:
        raise HTTPException(
            status_code=404, detail=translate("reports.thematic.family.notFound", locale=locale, default="Family report not found")
        )
    return models.ThematicReport(**report.data)


@router.get("/children", response_model=models.ThematicReport)
async def get_children_report(
    request: Request,
    user=Depends(require_user),
    db: Session = Depends(get_session),
) -> models.ThematicReport:
    """Get the latest children report for the user."""
    locale = request_locale(request)
    report = (
        db.query(db_models.GeneratedReport)
        .filter_by(user_id=user.id, product_type="thematic_children")
        .order_by(db_models.GeneratedReport.created_at.desc())
        .first()
    )
    if not report:
        raise HTTPException(
            status_code=404, detail=translate("reports.thematic.children.notFound", locale=locale, default="Children report not found")
        )
    return models.ThematicReport(**report.data)


@router.get("/love", response_model=models.ThematicReport)
async def get_love_report(
    request: Request,
    user=Depends(require_user),
    db: Session = Depends(get_session),
) -> models.ThematicReport:
    """Get the latest love/romantic relationships report for the user."""
    locale = request_locale(request)
    report = (
        db.query(db_models.GeneratedReport)
        .filter_by(user_id=user.id, product_type="thematic_love")
        .order_by(db_models.GeneratedReport.created_at.desc())
        .first()
    )
    if not report:
        raise HTTPException(
            status_code=404, detail=translate("reports.thematic.love.notFound", locale=locale, default="Love report not found")
        )
    return models.ThematicReport(**report.data)

