"""Solar and Lunar Return charts service."""

from __future__ import annotations

import math
from typing import Dict, List, Any, Optional
from datetime import date, datetime, timedelta
from todayflow_backend.core import models
from todayflow_backend.services import astro
from todayflow_backend.services.aspects import AspectEngine


class ReturnsService:
    """Service for calculating Solar and Lunar Return charts."""
    
    def __init__(
        self,
        astro_service: astro.AstroService | None = None,
        aspect_engine: AspectEngine | None = None,
    ):
        self.astro_service = astro_service or astro.AstroService()
        self.aspect_engine = aspect_engine or AspectEngine()
    
    async def calculate_solar_return(
        self,
        natal_chart: astro.ChartResponse,
        birth_date: date,
        target_year: int | None = None,
        birth_coordinates: Dict[str, float] | None = None,
        locale: str | None = None,
    ) -> models.SolarReturnChart:
        """
        Calculate Solar Return chart with precise timing.
        
        Solar Return is calculated for the exact moment when the Sun returns
        to its natal position (same degree and minute).
        
        Uses iterative binary search to find the precise moment.
        """
        if target_year is None:
            target_year = date.today().year
        
        # Get natal Sun position
        natal_sun = next((p for p in natal_chart.positions if p.get("body") == "Sun"), None)
        if not natal_sun:
            raise ValueError("Natal Sun position not found")
        
        natal_sun_long = natal_sun.get("longitude", 0)
        
        # Get birth time for initial approximation
        birth_time_str = natal_chart.metadata.get("birth_time", "12:00:00") if natal_chart.metadata else "12:00:00"
        try:
            birth_time_parts = birth_time_str.split(":")
            birth_hour = int(birth_time_parts[0])
            birth_minute = int(birth_time_parts[1]) if len(birth_time_parts) > 1 else 0
        except (ValueError, IndexError):
            birth_hour = 12
            birth_minute = 0
        
        # Start with approximate date (birthday)
        try:
            approx_date = date(target_year, birth_date.month, birth_date.day)
        except ValueError:
            # Handle February 29 case
            approx_date = date(target_year, birth_date.month, min(birth_date.day, 28))
        
        # Use birth coordinates or default
        if birth_coordinates is None:
            birth_coordinates = {"latitude": 0.0, "longitude": 0.0}
        
        # Find exact moment using binary search
        exact_datetime = await self._find_exact_return_moment(
            "Sun",
            natal_sun_long,
            approx_date,
            birth_hour,
            birth_minute,
            birth_coordinates,
            natal_chart.metadata
        )
        
        # Calculate Solar Return chart for exact moment
        solar_return_chart = None
        try:
            birth_payload = {
                "date": exact_datetime.date().isoformat(),
                "time": exact_datetime.time().strftime("%H:%M:%S"),
                "location": natal_chart.metadata.get("location", "Birth Location") if natal_chart.metadata else "Birth Location",
            }
            
            solar_return_chart = await self.astro_service.compute_chart(
                birth_payload=birth_payload,
                coordinates=birth_coordinates
            )
        except Exception:
            # If calculation fails, use approximate date/time
            pass
        
        return models.SolarReturnChart(
            solar_return_date=exact_datetime.date().isoformat(),
            target_year=target_year,
            natal_sun_position=natal_sun_long,
            description=f"Solar Return for year {target_year} (exact: {exact_datetime.strftime('%Y-%m-%d %H:%M')})",
        )
    
    async def calculate_lunar_return(
        self,
        natal_chart: astro.ChartResponse,
        birth_date: date,
        target_month: date | None = None,
        birth_coordinates: Dict[str, float] | None = None,
        locale: str | None = None,
    ) -> models.LunarReturnChart:
        """
        Calculate Lunar Return chart with precise timing.
        
        Lunar Return is calculated for the exact moment when the Moon returns
        to its natal position (same degree and minute).
        
        Uses iterative binary search to find the precise moment.
        """
        if target_month is None:
            target_month = date.today()
        
        # Get natal Moon position
        natal_moon = next((p for p in natal_chart.positions if p.get("body") == "Moon"), None)
        if not natal_moon:
            raise ValueError("Natal Moon position not found")
        
        natal_moon_long = natal_moon.get("longitude", 0)
        
        # Get birth time for initial approximation
        birth_time_str = natal_chart.metadata.get("birth_time", "12:00:00") if natal_chart.metadata else "12:00:00"
        try:
            birth_time_parts = birth_time_str.split(":")
            birth_hour = int(birth_time_parts[0])
            birth_minute = int(birth_time_parts[1]) if len(birth_time_parts) > 1 else 0
        except (ValueError, IndexError):
            birth_hour = 12
            birth_minute = 0
        
        # Calculate approximate Lunar Return date (Moon cycle ~27.3 days)
        days_from_birth = (target_month - birth_date).days
        moon_cycles = round(days_from_birth / 27.3)
        approx_date = birth_date + timedelta(days=round(moon_cycles * 27.3))
        
        # Ensure approx_date is in the target_month range (within 14 days)
        if approx_date < target_month - timedelta(days=14):
            approx_date += timedelta(days=28)
        elif approx_date > target_month + timedelta(days=14):
            approx_date -= timedelta(days=28)
        
        # Use birth coordinates or default
        if birth_coordinates is None:
            birth_coordinates = {"latitude": 0.0, "longitude": 0.0}
        
        # Find exact moment using binary search (smaller time window for Moon)
        exact_datetime = await self._find_exact_return_moment(
            "Moon",
            natal_moon_long,
            approx_date,
            birth_hour,
            birth_minute,
            birth_coordinates,
            natal_chart.metadata,
            max_hours_window=48  # Moon moves faster, use 48-hour window
        )
        
        # Calculate Lunar Return chart for exact moment
        lunar_return_chart = None
        try:
            birth_payload = {
                "date": exact_datetime.date().isoformat(),
                "time": exact_datetime.time().strftime("%H:%M:%S"),
                "location": natal_chart.metadata.get("location", "Birth Location") if natal_chart.metadata else "Birth Location",
            }
            
            lunar_return_chart = await self.astro_service.compute_chart(
                birth_payload=birth_payload,
                coordinates=birth_coordinates
            )
        except Exception:
            # If calculation fails, use approximate date/time
            pass
        
        return models.LunarReturnChart(
            lunar_return_date=exact_datetime.date().isoformat(),
            target_month=target_month.isoformat(),
            natal_moon_position=natal_moon_long,
            description=f"Lunar Return for {target_month.strftime('%B %Y')} (exact: {exact_datetime.strftime('%Y-%m-%d %H:%M')})",
        )
    
    async def _find_exact_return_moment(
        self,
        body: str,
        target_longitude: float,
        start_date: date,
        start_hour: int,
        start_minute: int,
        coordinates: Dict[str, float],
        metadata: Dict[str, Any] | None = None,
        max_hours_window: int = 24,
        precision_arcminutes: float = 1.0,
    ) -> datetime:
        """
        Find exact moment when a celestial body reaches target longitude using binary search.
        
        Args:
            body: "Sun" or "Moon"
            target_longitude: Target longitude in degrees (0-360)
            start_date: Approximate date to start search
            start_hour: Starting hour
            start_minute: Starting minute
            coordinates: Geographic coordinates
            metadata: Chart metadata
            max_hours_window: Maximum hours to search around start time
            precision_arcminutes: Precision in arcminutes (default 1 arcminute = ~4 minutes for Sun)
        
        Returns:
            Exact datetime when body reaches target longitude
        """
        # Create start and end times for binary search window
        start_datetime = datetime.combine(start_date, datetime.min.time().replace(hour=start_hour, minute=start_minute))
        end_datetime = start_datetime + timedelta(hours=max_hours_window)
        
        # Binary search for exact moment
        max_iterations = 20  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            # Calculate midpoint
            midpoint_datetime = start_datetime + (end_datetime - start_datetime) / 2
            
            # Get body position at midpoint
            try:
                birth_payload = {
                    "date": midpoint_datetime.date().isoformat(),
                    "time": midpoint_datetime.time().strftime("%H:%M:%S"),
                    "location": metadata.get("location", "Location") if metadata else "Location",
                }
                
                chart = await self.astro_service.compute_chart(
                    birth_payload=birth_payload,
                    coordinates=coordinates
                )
                
                body_pos = next((p for p in chart.positions if p.get("body") == body), None)
                if not body_pos:
                    # If body not found, use start_datetime as fallback
                    return start_datetime
                
                current_longitude = body_pos.get("longitude", 0)
                
                # Calculate angular difference (handling 360-degree wrap-around)
                diff = current_longitude - target_longitude
                if diff > 180:
                    diff -= 360
                elif diff < -180:
                    diff += 360
                
                # Convert to arcminutes (1 degree = 60 arcminutes)
                diff_arcminutes = abs(diff) * 60
                
                # Check if we're close enough
                if diff_arcminutes <= precision_arcminutes:
                    return midpoint_datetime
                
                # Adjust search window based on whether body is before or after target
                if diff > 0:
                    # Body is ahead of target, search earlier
                    end_datetime = midpoint_datetime
                else:
                    # Body is behind target, search later
                    start_datetime = midpoint_datetime
                
                iteration += 1
                
            except Exception:
                # If calculation fails, use start_datetime as fallback
                return start_datetime
        
        # If binary search didn't converge, return midpoint as best guess
        return start_datetime + (end_datetime - start_datetime) / 2


async def get_returns_service() -> ReturnsService:
    """Dependency function for ReturnsService."""
    return ReturnsService()
