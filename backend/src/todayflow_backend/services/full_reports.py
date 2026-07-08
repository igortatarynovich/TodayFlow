"""Full report assembly service."""

from __future__ import annotations

import logging

from todayflow_backend.core import models
from todayflow_backend.core.config import settings
from todayflow_backend.db import models as db_models
from todayflow_backend.db.session import SessionLocal
from todayflow_backend.services import astro
from todayflow_backend.services.mapping import InternalModelMapper
from todayflow_backend.services.narrative import NarrativeEngine
from todayflow_backend.services.geocode import Geocoder
from todayflow_backend.services.tarot import TarotService
from todayflow_backend.services.psychological_layer import PsychologicalLayerService
from todayflow_backend.services.aspects import AspectEngine
from todayflow_backend.data import astrology as astrology_ref


logger = logging.getLogger(__name__)


class FullReportService:
    def __init__(
        self,
        astro_service: astro.AstroService | None = None,
        narrative_engine: NarrativeEngine | None = None,
        model_mapper: InternalModelMapper | None = None,
        geocoder: Geocoder | None = None,
        tarot_service: TarotService | None = None,
        psychological_layer_service: PsychologicalLayerService | None = None,
        aspect_engine: AspectEngine | None = None,
    ):
        self.astro_service = astro_service or astro.AstroService()
        self.narrative_engine = narrative_engine or NarrativeEngine()
        self.model_mapper = model_mapper or InternalModelMapper()
        self.geocoder = geocoder or Geocoder()
        self.tarot_service = tarot_service or TarotService()
        self.psychological_layer_service = psychological_layer_service or PsychologicalLayerService()
        self.aspect_engine = aspect_engine or AspectEngine()

    async def generate(
        self, birth_data: models.BirthData, user: db_models.User, *, locale: str | None = None
    ) -> models.FullReport:
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
        sections = self.narrative_engine.build_full_sections(
            snapshot,
            internal_model,
            overrides=availability_overrides,
            text_overrides=text_overrides,
            user_id=user.id,
            locale=locale,
        )

        spread_history = self.tarot_service.get_spread_history(user, limit=5, locale=locale).history

        # Generate psychological layer
        psychological_layer = self.psychological_layer_service.generate_psychological_patterns(
            chart_response=chart_response,
            internal_model=internal_model,
            snapshot=snapshot,
            locale=locale,
        )

        # Calculate aspects
        aspects = self.aspect_engine.callouts(chart_response.positions, locale=locale)

        # Prepare chart positions (positions are already dicts from ChartResponse)
        chart_positions = chart_response.positions
        
        # Log chart positions for debugging
        logger.info(f"Generated chart_positions: {len(chart_positions)} positions")
        if chart_positions:
            logger.info(f"First position sample: {chart_positions[0]}")
            logger.info(f"Position keys: {list(chart_positions[0].keys()) if chart_positions else 'N/A'}")
            
            # Check if positions have longitude, and add it if missing (convert from sign + degree)
            if chart_positions and not any(pos.get("longitude") for pos in chart_positions if isinstance(pos, dict)):
                logger.warning("Chart positions missing longitude, converting from sign + degree")
                sign_map = {
                    "Aries": 0, "Taurus": 1, "Gemini": 2, "Cancer": 3,
                    "Leo": 4, "Virgo": 5, "Libra": 6, "Scorpio": 7,
                    "Sagittarius": 8, "Capricorn": 9, "Aquarius": 10, "Pisces": 11
                }
                for pos in chart_positions:
                    if isinstance(pos, dict) and not pos.get("longitude"):
                        sign = pos.get("sign")
                        degree = pos.get("degree")
                        if sign and degree is not None:
                            sign_index = sign_map.get(sign, 0)
                            pos["longitude"] = (sign_index * 30) + degree
                            logger.info(f"Converted {pos.get('body')} {sign} {degree}° to longitude {pos['longitude']}°")

        report = models.FullReport(
            summary=snapshot,
            internal_model=internal_model,
            sections=sections,
            content_version=settings.content_version,
            tarot_spreads=spread_history,
            psychological_layer=psychological_layer,
            chart_positions=chart_positions,
            aspects=aspects,
        )
        self._persist_report(report, user)
        return report

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

    def _persist_report(self, report: models.FullReport, user: db_models.User) -> None:
        session = SessionLocal()
        try:
            profile = db_models.UserProfile(
                user_id=user.id,
                model_version=settings.narrative_model_version,
                axes=[axis.model_dump() for axis in report.internal_model.axes],
                modulators=[mod.model_dump() for mod in report.internal_model.modulators],
            )
            session.add(profile)
            session.flush()

            # Log chart_positions before saving
            report_dict = report.model_dump()
            logger.info(f"Persisting FullReport for user {user.id}")
            logger.info(f"chart_positions in report_dict: {bool(report_dict.get('chart_positions'))}")
            if report_dict.get('chart_positions'):
                chart_pos = report_dict.get('chart_positions')
                logger.info(f"chart_positions type before save: {type(chart_pos)}")
                if isinstance(chart_pos, list):
                    logger.info(f"chart_positions length before save: {len(chart_pos)}")
                    if chart_pos:
                        logger.info(f"First position before save: {chart_pos[0]}")

            db_report = db_models.GeneratedReport(
                user_id=user.id,
                profile_id=profile.id,
                product_type="full",
                content_version=report.content_version,
                data=report_dict,
            )
            session.add(db_report)
            session.commit()
            logger.info(f"Successfully persisted FullReport for user {user.id}")
        except Exception as e:
            logger.error(f"Error persisting FullReport for user {user.id}: {e}", exc_info=True)
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def _load_paragraph_overrides() -> tuple[dict[str, bool], dict[tuple[str, str], str]]:
        session = SessionLocal()
        try:
            overrides = session.query(db_models.ParagraphOverride).all()
            text_overrides = session.query(db_models.ParagraphTextOverride).all()
            availability = {ov.paragraph_id: ov.full_enabled for ov in overrides}
            text_map = {(txt.paragraph_id, txt.variant_id): txt.text for txt in text_overrides}
            return availability, text_map
        finally:
            session.close()
