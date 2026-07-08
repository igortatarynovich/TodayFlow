"""Thematic report service for focused reports (Career, Family, Children)."""

from __future__ import annotations

import logging
from typing import Sequence

from todayflow_backend.core import models
from todayflow_backend.db import models as db_models
from todayflow_backend.db.session import SessionLocal
from todayflow_backend.services import astro
from todayflow_backend.services.mapping import InternalModelMapper
from todayflow_backend.services.narrative import NarrativeEngine
from todayflow_backend.services.geocode import Geocoder

logger = logging.getLogger(__name__)


# Планы для тематических разборов
CAREER_THEMATIC_PLAN: Sequence[dict] = [
    {
        "section": "Career & Responsibility",
        "source_section": "Career & Responsibility",
        "sub_blocks": [
            {"name": "Career Baseline", "limit": 2},
            {"name": "Pressure & Burnout", "limit": 1},
            {"name": "Recovery & Sustainability", "limit": 1},
            {"name": "Growth Levers", "limit": 1},
        ],
    },
    {
        "section": "Money & Security",
        "source_section": "Money & Security",
        "sub_blocks": [
            {"name": "Security Orientation", "limit": 1},
            {"name": "Risk & Control", "limit": 1},
        ],
    },
]

FAMILY_THEMATIC_PLAN: Sequence[dict] = [
    {
        "section": "Relationships",
        "source_section": "Relationships",
        "sub_blocks": [
            {"name": "Connection Style", "limit": 2},
            {"name": "Attachment & Boundaries", "limit": 1},
            {"name": "Conflict Patterns", "limit": 1},
            {"name": "Growth in Relationships", "limit": 1},
        ],
    },
    {
        "section": "Emotional Patterns",
        "source_section": "Emotional Patterns",
        "sub_blocks": [
            {"name": "Emotional Baseline", "limit": 1},
            {"name": "Stress Response", "limit": 1},
        ],
    },
]

CHILDREN_THEMATIC_PLAN: Sequence[dict] = [
    {
        "section": "Relationships",
        "source_section": "Relationships",
        "sub_blocks": [
            {"name": "Connection Style", "limit": 1},
            {"name": "Attachment & Boundaries", "limit": 2},
            {"name": "Growth in Relationships", "limit": 1},
        ],
    },
    {
        "section": "Emotional Patterns",
        "source_section": "Emotional Patterns",
        "sub_blocks": [
            {"name": "Emotional Baseline", "limit": 1},
            {"name": "Recovery & Regulation", "limit": 1},
        ],
    },
]

LOVE_THEMATIC_PLAN: Sequence[dict] = [
    {
        "section": "Relationships",
        "source_section": "Relationships",
        "sub_blocks": [
            {"name": "Connection Style", "limit": 2},
            {"name": "Attachment & Boundaries", "limit": 2},
            {"name": "Conflict Patterns", "limit": 1},
            {"name": "Growth in Relationships", "limit": 1},
        ],
    },
    {
        "section": "Emotional Patterns",
        "source_section": "Emotional Patterns",
        "sub_blocks": [
            {"name": "Emotional Baseline", "limit": 1},
            {"name": "Stress Response", "limit": 1},
            {"name": "Recovery & Regulation", "limit": 1},
        ],
    },
]


class ThematicReportService:
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

    async def generate_career_report(
        self, birth_data: models.BirthData, user: db_models.User, *, locale: str | None = None
    ) -> models.ThematicReport:
        """Generate a career-focused thematic report."""
        return await self._generate_thematic_report(
            birth_data, user, "career", CAREER_THEMATIC_PLAN, locale=locale
        )

    async def generate_family_report(
        self, birth_data: models.BirthData, user: db_models.User, *, locale: str | None = None
    ) -> models.ThematicReport:
        """Generate a family-focused thematic report."""
        return await self._generate_thematic_report(
            birth_data, user, "family", FAMILY_THEMATIC_PLAN, locale=locale
        )

    async def generate_children_report(
        self, birth_data: models.BirthData, user: db_models.User, *, locale: str | None = None
    ) -> models.ThematicReport:
        """Generate a children-focused thematic report."""
        return await self._generate_thematic_report(
            birth_data, user, "children", CHILDREN_THEMATIC_PLAN, locale=locale
        )

    async def generate_love_report(
        self, birth_data: models.BirthData, user: db_models.User, *, locale: str | None = None
    ) -> models.ThematicReport:
        """Generate a love/romantic relationships-focused thematic report."""
        return await self._generate_thematic_report(
            birth_data, user, "love", LOVE_THEMATIC_PLAN, locale=locale
        )

    async def _generate_thematic_report(
        self,
        birth_data: models.BirthData,
        user: db_models.User,
        theme: str,
        plan: Sequence[dict],
        *,
        locale: str | None = None,
    ) -> models.ThematicReport:
        """Generate a thematic report based on the provided plan."""
        # Получаем координаты
        coordinates = None
        if birth_data.coordinates:
            coordinates = birth_data.coordinates.model_dump()
        else:
            geo = self.geocoder.lookup(birth_data.location)
            if geo:
                coordinates = {"latitude": geo["latitude"], "longitude": geo["longitude"]}

        # Вычисляем карту
        birth_payload = birth_data.model_dump(exclude={"coordinates"}, exclude_none=True)
        chart_response = await self.astro_service.compute_chart(birth_payload=birth_payload, coordinates=coordinates)
        internal_model = self.model_mapper.map(chart_response.model_dump())

        # Создаем snapshot
        snapshot = models.ChartSnapshot(
            sun=self._lookup_sign(chart_response, "sun"),
            moon=self._lookup_sign(chart_response, "moon"),
            rising=self._lookup_sign(chart_response, "rising"),
            houses=chart_response.houses,
        )

        # Строим секции по плану
        sections = self.narrative_engine.build_thematic_sections(
            snapshot=snapshot,
            internal_model=internal_model,
            plan=plan,
            theme=theme,
            user_id=user.id,
            locale=locale,
        )

        report = models.ThematicReport(
            theme=theme,
            summary=snapshot,
            internal_model=internal_model,
            sections=sections,
        )
        self._persist_report(report, user, theme)
        return report

    @staticmethod
    def _lookup_sign(chart_response: astro.ChartResponse, body: str) -> str:
        for position in chart_response.positions:
            if position["body"] == body:
                return position["sign"]
        return "Unknown"

    def _persist_report(
        self, report: models.ThematicReport, user: db_models.User, theme: str
    ) -> None:
        """Save thematic report to database."""
        session = SessionLocal()
        try:
            db_report = db_models.GeneratedReport(
                user_id=user.id,
                profile_id=None,
                product_type=f"thematic_{theme}",
                content_version="1.0.0",
                data=report.model_dump(),
            )
            session.add(db_report)
            session.commit()
            session.refresh(db_report)
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to persist thematic report: {e}")
            raise
        finally:
            session.close()

