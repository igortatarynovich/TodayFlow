"""Full report endpoint."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session

from todayflow_backend.api.auth import require_user
from todayflow_backend.core import models
from todayflow_backend.db import models as db_models
from todayflow_backend.db.session import get_session
from todayflow_backend.i18n import request_locale, translate
from todayflow_backend.services.full_reports import FullReportService
from todayflow_backend.services.pdf import FullReportRenderer

router = APIRouter(prefix="/reports/full", tags=["reports"])

full_service = FullReportService()
pdf_renderer = FullReportRenderer()


@router.post("", response_model=models.FullReport)
async def generate_full_report(request: Request, payload: models.BirthData, user=Depends(require_user)) -> models.FullReport:
    if not user.is_paid:
        raise HTTPException(
            status_code=403, detail=translate("reports.full.requiresPayment", locale=request_locale(request))
        )
    return await full_service.generate(payload, user, locale=request_locale(request))


@router.get("", response_model=models.FullReport)
async def get_full_report(
    request: Request,
    regenerate: bool = Query(False, description="Force regeneration of report"),
    user=Depends(require_user),
    db: Session = Depends(get_session)
) -> models.FullReport:
    locale = request_locale(request)
    
    # Если требуется регенерация, удаляем старый отчет
    if regenerate:
        old_report = (
            db.query(db_models.GeneratedReport)
            .filter_by(user_id=user.id, product_type="full")
            .first()
        )
        if old_report:
            db.delete(old_report)
            db.commit()
            import logging
            logging.info(f"Deleted old report for user {user.id} to force regeneration")
    
    # Проверяем существующий отчет
    report = (
        db.query(db_models.GeneratedReport)
        .filter_by(user_id=user.id, product_type="full")
        .order_by(db_models.GeneratedReport.created_at.desc())
        .first()
    )
    
    # Если отчета нет, но пользователь платный - создаем его автоматически
    if not report and user.is_paid:
        # Получаем primary профиль пользователя
        primary_profile = (
            db.query(db_models.AstroProfile)
            .filter_by(user_id=user.id, is_primary=True)
            .first()
        ) or (
            db.query(db_models.AstroProfile)
            .filter_by(user_id=user.id)
            .order_by(db_models.AstroProfile.created_at.asc())
            .first()
        )
        
        if primary_profile and primary_profile.latitude is not None and primary_profile.longitude is not None:
            try:
                from todayflow_backend.core.models import BirthData
                birth_data = BirthData(
                    date=str(primary_profile.birth_date),
                    time=primary_profile.birth_time.isoformat() if primary_profile.birth_time and not primary_profile.time_unknown else None,
                    location=primary_profile.location_name or "",
                    coordinates={
                        "latitude": primary_profile.latitude,
                        "longitude": primary_profile.longitude
                    }
                )
                # Создаем отчет
                return await full_service.generate(birth_data, user, locale=locale)
            except Exception as e:
                # Если не удалось создать, возвращаем 404
                import logging
                logging.error(f"Failed to auto-generate full report for user {user.id}: {e}")
    
    if not report:
        raise HTTPException(
            status_code=404, detail=translate("reports.full.notFound", locale=locale)
        )
    
    # Load report data
    report_data = report.data
    
    # Log report data for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Loading FullReport for user {user.id}")
    logger.info(f"Report data type: {type(report_data)}")
    logger.info(f"Report data keys: {list(report_data.keys()) if isinstance(report_data, dict) else 'Not a dict'}")
    logger.info(f"Has chart_positions: {bool(report_data.get('chart_positions'))}")
    if report_data.get('chart_positions'):
        chart_pos = report_data.get('chart_positions')
        logger.info(f"chart_positions type: {type(chart_pos)}")
        if isinstance(chart_pos, list):
            logger.info(f"chart_positions length: {len(chart_pos)}")
            if chart_pos:
                logger.info(f"First position: {chart_pos[0]}")
                logger.info(f"First position keys: {list(chart_pos[0].keys()) if isinstance(chart_pos[0], dict) else 'Not a dict'}")
    
    # Ensure report_data is a dict
    if not isinstance(report_data, dict):
        logger.error(f"Report data is not a dict! Type: {type(report_data)}")
        report_data = {}
    
    # Ensure chart_positions is a list (handle case where it might be stored incorrectly)
    if report_data.get('chart_positions') and not isinstance(report_data.get('chart_positions'), list):
        logger.warning(f"chart_positions is not a list, converting...")
        report_data['chart_positions'] = []
    
    # If chart_positions is missing or empty, try to regenerate it from existing data
    if not report_data.get('chart_positions') or len(report_data.get('chart_positions', [])) == 0:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"FullReport for user {user.id} has no chart_positions, attempting to regenerate...")
        
        # Try to get astro profile and regenerate chart
        primary_profile = (
            db.query(db_models.AstroProfile)
            .filter_by(user_id=user.id, is_primary=True)
            .first()
        ) or (
            db.query(db_models.AstroProfile)
            .filter_by(user_id=user.id)
            .order_by(db_models.AstroProfile.created_at.asc())
            .first()
        )
        
        if primary_profile and primary_profile.latitude is not None and primary_profile.longitude is not None:
            try:
                from todayflow_backend.core.models import BirthData
                from todayflow_backend.services import astro
                
                astro_service = astro.AstroService()
                
                birth_data = BirthData(
                    date=str(primary_profile.birth_date),
                    time=primary_profile.birth_time.isoformat() if primary_profile.birth_time and not primary_profile.time_unknown else None,
                    location=primary_profile.location_name or "",
                    coordinates={
                        "latitude": primary_profile.latitude,
                        "longitude": primary_profile.longitude
                    }
                )
                
                # Recalculate chart to get positions
                # Use coordinates directly from profile, no need to geocode again
                coordinates_dict = {
                    "latitude": primary_profile.latitude,
                    "longitude": primary_profile.longitude
                }
                
                chart_response = await astro_service.compute_chart(
                    birth_payload={
                        "date": birth_data.date,
                        "time": birth_data.time,
                        "location": birth_data.location
                    },
                    coordinates=coordinates_dict
                )
                
                # Update report_data with chart_positions
                report_data['chart_positions'] = chart_response.positions
                
                # Also update houses if they're missing or incorrect
                if 'summary' in report_data and report_data['summary'].get('houses'):
                    report_data['summary']['houses'] = chart_response.houses
                
                # Update stored report - need to mark JSON field as modified for SQLAlchemy
                from sqlalchemy.orm.attributes import flag_modified
                report.data = report_data
                flag_modified(report, 'data')  # Explicitly mark JSON field as modified
                db.add(report)
                db.commit()
                db.refresh(report)
                
                logger.info(f"Successfully regenerated chart_positions for user {user.id}, saved {len(chart_response.positions)} positions")
                logger.info(f"Chart positions sample: {chart_response.positions[:2] if chart_response.positions else 'None'}")
                logger.info(f"Report data keys after update: {list(report_data.keys())}")
                logger.info(f"Has chart_positions in report_data: {bool(report_data.get('chart_positions'))}")
                
                # Reload report from database to verify data was saved
                db.refresh(report)
                refreshed_data = report.data if hasattr(report, 'data') else {}
                logger.info(f"After refresh - Has chart_positions: {bool(refreshed_data.get('chart_positions'))}")
                if refreshed_data.get('chart_positions'):
                    logger.info(f"After refresh - Chart positions count: {len(refreshed_data.get('chart_positions', []))}")
                    # Update report_data with refreshed data to ensure consistency
                    report_data = refreshed_data
                else:
                    logger.error(f"WARNING: chart_positions were NOT saved to database! report_data has {len(report_data.get('chart_positions', []))} positions but refreshed report has none!")
            except Exception as e:
                logger.error(f"Failed to regenerate chart_positions for user {user.id}: {e}", exc_info=True)
    
    # Ensure chart_positions is included in the response
    final_report = models.FullReport(**report_data)
    
    # Log final report structure
    logger.info(f"Returning FullReport for user {user.id}")
    logger.info(f"Final report has chart_positions: {bool(final_report.chart_positions)}")
    logger.info(f"Chart positions count: {len(final_report.chart_positions) if final_report.chart_positions else 0}")
    if final_report.chart_positions:
        logger.info(f"First chart position: {final_report.chart_positions[0]}")
    
    return final_report


@router.get("/download")
async def download_full_report(
    request: Request, 
    report_id: int | None = Query(None, description="ID конкретного разбора для скачивания"),
    user=Depends(require_user), 
    db: Session = Depends(get_session)
):
    """Download full report PDF. If report_id is provided, download that specific report."""
    if report_id:
        report = (
            db.query(db_models.GeneratedReport)
            .filter_by(id=report_id, user_id=user.id, product_type="full")
            .first()
        )
    else:
        # Fallback to latest report
        report = (
            db.query(db_models.GeneratedReport)
            .filter_by(user_id=user.id, product_type="full")
            .order_by(db_models.GeneratedReport.created_at.desc())
            .first()
        )
    if not report:
        raise HTTPException(
            status_code=404, detail=translate("reports.full.downloadMissing", locale=request_locale(request))
        )
    try:
        pdf_bytes = pdf_renderer.render(models.FullReport(**report.data), user.email)
    except Exception as exc:
        from todayflow_backend.services.pdf import PDFGenerationError
        if isinstance(exc, PDFGenerationError):
            raise HTTPException(
                status_code=500,
                detail=translate("reports.full.pdfGenerationFailed", locale=request_locale(request), default="PDF generation failed")
            ) from exc
        raise HTTPException(
            status_code=500,
            detail=translate("reports.full.downloadError", locale=request_locale(request), default="Failed to generate PDF")
        ) from exc
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="todayflow_full_report.pdf"',
            "Content-Length": str(len(pdf_bytes))
        }
    )
