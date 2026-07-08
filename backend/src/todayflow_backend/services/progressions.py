"""Secondary progressions service for predictive astrology."""

from __future__ import annotations

from typing import Dict, List, Any, Optional
from datetime import date, datetime, timedelta
from todayflow_backend.core import models
from todayflow_backend.services import astro
from todayflow_backend.services.aspects import AspectEngine


class ProgressionsService:
    """Service for calculating secondary progressions."""
    
    def __init__(
        self,
        astro_service: astro.AstroService | None = None,
        aspect_engine: AspectEngine | None = None,
    ):
        self.astro_service = astro_service or astro.AstroService()
        self.aspect_engine = aspect_engine or AspectEngine()
    
    async def calculate_progressions(
        self,
        natal_chart: astro.ChartResponse,
        birth_date: date,
        birth_coordinates: Dict[str, float] | None = None,
        target_date: date | None = None,
        locale: str | None = None,
    ) -> models.ProgressedChart:
        """
        Calculate secondary progressions for a target date.
        
        Secondary progressions use the formula: 1 day = 1 year
        So progressions for a person born on Jan 1, 2000, for the year 2024,
        would use the chart positions for Jan 25, 2000 (24 days = 24 years).
        
        Steps:
        1. Calculate progression date (birth_date + (target_date - birth_date) days)
        2. Calculate progressed chart positions for that date using AstroService
        3. Compare with natal positions
        4. Calculate progressed aspects
        """
        if target_date is None:
            target_date = date.today()
        
        # Calculate progression date
        days_since_birth = (target_date - birth_date).days
        progression_date = birth_date + timedelta(days=days_since_birth)
        
        # Use birth coordinates or default to equator/prime meridian
        if birth_coordinates is None:
            birth_coordinates = {"latitude": 0.0, "longitude": 0.0}
        
        # Calculate progressed chart using AstroService
        progressed_chart = None
        progressed_aspects = []
        
        try:
            # Create birth payload for progression date (same location as birth)
            birth_payload = {
                "date": progression_date.isoformat(),
                "time": natal_chart.metadata.get("birth_time", "12:00:00") if natal_chart.metadata else "12:00:00",
                "location": natal_chart.metadata.get("location", "Birth Location") if natal_chart.metadata else "Birth Location",
            }
            
            # Calculate progressed chart
            progressed_chart = await self.astro_service.compute_chart(
                birth_payload=birth_payload,
                coordinates=birth_coordinates
            )
            
            # Calculate progressed aspects (progressed planets to natal planets)
            progressed_aspects = await self.calculate_progressed_aspects(
                natal_chart=natal_chart,
                progressed_chart=progressed_chart,
                locale=locale,
            )
        except Exception:
            # If calculation fails, return basic structure
            pass
        
        return models.ProgressedChart(
            progression_date=progression_date.isoformat(),
            target_date=target_date.isoformat(),
            days_progressed=days_since_birth,
            description=f"Secondary progression: {days_since_birth} days = {days_since_birth} years",
            progressed_aspects=progressed_aspects,
        )
    
    async def calculate_progressed_aspects(
        self,
        natal_chart: astro.ChartResponse,
        progressed_chart: astro.ChartResponse,
        locale: str | None = None,
    ) -> List[models.ProgressedAspect]:
        """Calculate aspects between progressed and natal planets."""
        progressed_aspects = []
        
        natal_positions = {p["body"]: p for p in natal_chart.positions if "body" in p and "longitude" in p}
        progressed_positions = {p["body"]: p for p in progressed_chart.positions if "body" in p and "longitude" in p}
        
        aspect_map = self.aspect_engine.aspect_map
        from math import fabs
        
        key_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
        
        for planet in key_planets:
            if planet not in progressed_positions or planet not in natal_positions:
                continue
            
            prog_long = progressed_positions[planet]["longitude"]
            natal_long = natal_positions[planet]["longitude"]
            
            # Calculate aspect
            raw_difference = fabs(prog_long - natal_long) % 360
            if raw_difference > 180:
                raw_difference = 360 - raw_difference
            
            aspect_id = None
            orb_delta = 999
            
            for aspect_key, aspect_record in aspect_map.items():
                angle = aspect_record.get("angle")
                orb = aspect_record.get("orb", 0)
                if angle is None:
                    continue
                delta = fabs(raw_difference - angle)
                if delta <= orb and delta < orb_delta:
                    aspect_id = aspect_key
                    orb_delta = delta
            
            if aspect_id and orb_delta <= 5:
                progressed_aspects.append(models.ProgressedAspect(
                    progressed_planet=planet,
                    natal_planet=planet,
                    aspect=aspect_id,
                    orb=round(orb_delta, 2),
                    description=f"Progressed {planet} {aspect_id} natal {planet}",
                ))
        
        return progressed_aspects


async def get_progressions_service() -> ProgressionsService:
    """Dependency function for ProgressionsService."""
    return ProgressionsService()

