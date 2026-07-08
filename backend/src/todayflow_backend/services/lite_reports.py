"""Service that orchestrates astro calculations and narrative selection for Lite reports."""

from __future__ import annotations

import logging

from todayflow_backend.core import models
from todayflow_backend.core.config import settings
from todayflow_backend.db import models as db_models
from todayflow_backend.db.session import SessionLocal
from todayflow_backend.services import astro
from todayflow_backend.services.narrative import NarrativeEngine
from todayflow_backend.services.mapping import InternalModelMapper
from todayflow_backend.services.geocode import Geocoder
from todayflow_backend.data import astrology as astrology_ref
from todayflow_backend.services.aspects import AspectEngine


logger = logging.getLogger(__name__)


class LiteReportService:
    def __init__(
        self,
        astro_service: astro.AstroService | None = None,
        narrative_engine: NarrativeEngine | None = None,
        model_mapper: InternalModelMapper | None = None,
        geocoder: Geocoder | None = None,
    ):
        self.astro_service = astro_service or astro.AstroService()
        self.narrative_engine = narrative_engine or NarrativeEngine()
        self.model_mapper = model_mapper or InternalModelMapper()
        self.geocoder = geocoder or Geocoder()
        self.aspect_engine = AspectEngine()

    async def generate(
        self, birth_data: models.BirthData, user: db_models.User | None = None, *, locale: str | None = None, astro_profile_id: int | None = None
    ) -> models.LiteReport:
        # Если указан astro_profile_id, проверяем существующий report для этого профиля
        if astro_profile_id:
            existing = self._get_latest_report(user, astro_profile_id=astro_profile_id)
            if existing:
                return existing
        else:
            existing = self._get_latest_report(user)
            if existing:
                return existing

        coordinates = None
        if birth_data.coordinates:
            coordinates = birth_data.coordinates.model_dump()
        else:
            geo = self.geocoder.lookup(birth_data.location)
            if geo:
                coordinates = {"latitude": geo["latitude"], "longitude": geo["longitude"]}

        birth_payload = birth_data.model_dump(exclude={"coordinates"}, exclude_none=True)
        chart_response = await self.astro_service.compute_chart(birth_payload=birth_payload, coordinates=coordinates)
        internal_model = self.model_mapper.map(chart_response.model_dump())

        snapshot = models.ChartSnapshot(
            sun=self._lookup_sign(chart_response, "sun"),
            moon=self._lookup_sign(chart_response, "moon"),
            rising=self._lookup_sign(chart_response, "rising"),
            houses=chart_response.houses,
        )
        self._validate_reference_signs(birth_data, snapshot)

        availability_overrides, text_overrides = self._load_paragraph_overrides()
        paragraphs = self.narrative_engine.build_lite_preview(
            internal_model,
            overrides=availability_overrides,
            text_overrides=text_overrides,
            user_id=user.id if user else None,
            locale=locale,
        )

        aspect_callouts = self.aspect_engine.callouts(chart_response.positions, locale=locale)

        lite_report = models.LiteReport(
            summary=snapshot,
            paragraphs=paragraphs,
            internal_model=internal_model,
            content_version=settings.content_version,
            chart_positions=chart_response.positions,
            aspects=aspect_callouts,
        )
        self._persist_report(lite_report, user, astro_profile_id=astro_profile_id)
        return lite_report

    @staticmethod
    def _lookup_sign(chart_response: astro.ChartResponse, body: str) -> str:
        for position in chart_response.positions:
            if position["body"] == body:
                return position["sign"]
        return "Unknown"

    @staticmethod
    def _validate_reference_signs(birth_data: models.BirthData, snapshot: models.ChartSnapshot) -> None:
        if not birth_data.date:
            return
        expected = astrology_ref.sign_for_iso_date(birth_data.date)
        if expected and snapshot.sun != expected["name"]:
            logger.warning(
                "Sun sign mismatch: expected %s for %s, got %s",
                expected["name"],
                birth_data.date,
                snapshot.sun,
            )

    def _persist_report(self, report: models.LiteReport, user: db_models.User | None, astro_profile_id: int | None = None) -> None:
        session = SessionLocal()
        try:
            profile = None
            if user:
                profile = db_models.UserProfile(
                    user_id=user.id,
                    model_version=settings.narrative_model_version,
                    axes=[axis.model_dump() for axis in report.internal_model.axes],
                    modulators=[mod.model_dump() for mod in report.internal_model.modulators],
                )
                session.add(profile)
                session.flush()

            # Сохраняем astro_profile_id в data для возможности поиска по профилю
            report_data = report.model_dump()
            if astro_profile_id:
                report_data["astro_profile_id"] = astro_profile_id

            db_report = db_models.GeneratedReport(
                user_id=user.id if user else None,
                profile_id=profile.id if profile else None,
                product_type="lite",
                content_version=report.content_version,
                data=report_data,
            )
            session.add(db_report)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _get_latest_report(self, user: db_models.User | None, astro_profile_id: int | None = None) -> models.LiteReport | None:
        if user is None:
            return None
        session = SessionLocal()
        try:
            query = (
                session.query(db_models.GeneratedReport)
                .filter_by(user_id=user.id, product_type="lite")
            )
            
            # Если указан astro_profile_id, ищем report для этого профиля
            if astro_profile_id:
                # Ищем в data по astro_profile_id
                reports = query.order_by(db_models.GeneratedReport.created_at.desc()).all()
                for db_report in reports:
                    if db_report.data and db_report.data.get("astro_profile_id") == astro_profile_id:
                        return models.LiteReport(**db_report.data)
                return None
            
            # Иначе возвращаем последний report
            db_report = query.order_by(db_models.GeneratedReport.created_at.desc()).first()
            if not db_report:
                return None
            return models.LiteReport(**db_report.data)
        finally:
            session.close()

    @staticmethod
    def _load_paragraph_overrides() -> tuple[dict[str, bool], dict[tuple[str, str], str]]:
        session = SessionLocal()
        try:
            overrides = session.query(db_models.ParagraphOverride).all()
            text_overrides = session.query(db_models.ParagraphTextOverride).all()
            availability = {ov.paragraph_id: ov.lite_enabled for ov in overrides}
            text_map = {(txt.paragraph_id, txt.variant_id): txt.text for txt in text_overrides}
            return availability, text_map
        finally:
            session.close()


async def get_lite_report_service() -> LiteReportService:
    return LiteReportService()
