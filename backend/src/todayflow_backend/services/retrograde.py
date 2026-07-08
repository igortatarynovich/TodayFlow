"""Planet retrograde status service."""

from __future__ import annotations

from typing import Dict, List, Any, Optional
from datetime import date, timedelta
from todayflow_backend.core import models
from todayflow_backend.services import astro


class RetrogradeService:
    """Service for determining planet retrograde status."""
    
    def __init__(self, astro_service: astro.AstroService | None = None):
        self.astro_service = astro_service or astro.AstroService()
    
    async def get_retrograde_status(
        self,
        forecast_date: date | None = None,
        coordinates: Dict[str, float] | None = None,
        locale: str | None = None,
    ) -> models.RetrogradeStatus:
        """
        Get retrograde status of planets for a given date.
        
        Calculates planetary positions for forecast_date and previous day,
        then compares longitude changes to determine retrograde motion.
        
        Args:
            forecast_date: Date to check retrograde status (defaults to today)
            coordinates: Optional coordinates for chart calculation (if None, uses default location)
            locale: Optional locale for descriptions
        """
        if forecast_date is None:
            forecast_date = date.today()
        
        # Use default coordinates if not provided (equator/prime meridian)
        if coordinates is None:
            coordinates = {"latitude": 0.0, "longitude": 0.0}
        
        # Calculate positions for forecast date and previous day
        current_positions = await self._get_planet_positions(forecast_date, coordinates)
        previous_positions = await self._get_planet_positions(forecast_date - timedelta(days=1), coordinates)
        
        # Determine which planets are retrograde
        retrograde_planets = self._calculate_retrograde_status(current_positions, previous_positions)
        
        # Generate descriptions for retrograde planets
        descriptions = self._generate_retrograde_descriptions(retrograde_planets, locale=locale)
        
        # Calculate planetary ingresses (planets entering new signs)
        ingresses = await self._calculate_ingresses(forecast_date, coordinates)
        
        return models.RetrogradeStatus(
            date=forecast_date.isoformat(),
            retrograde_planets=retrograde_planets,
            descriptions=descriptions,
            ingresses=ingresses,
        )
    
    async def _get_planet_positions(
        self,
        target_date: date,
        coordinates: Dict[str, float],
    ) -> List[Dict[str, Any]]:
        """Calculate planet positions for a given date using AstroService."""
        # Create a birth payload for the target date (using midday for general transits)
        birth_payload = {
            "date": target_date.isoformat(),
            "time": "12:00:00",
            "location": "Equator",  # Location name doesn't matter if coordinates are provided
        }
        
        try:
            chart_response = await self.astro_service.compute_chart(
                birth_payload=birth_payload,
                coordinates=coordinates
            )
            return chart_response.positions
        except Exception:
            # If calculation fails, return empty list
            return []
    
    def _calculate_retrograde_status(
        self,
        current_positions: List[Dict[str, Any]],
        previous_positions: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Calculate which planets are retrograde by comparing positions.
        
        A planet is retrograde if its longitude decreased from previous day to current day
        (normal motion is forward/increasing longitude).
        """
        retrograde = []
        
        current_dict = {p.get("body"): p for p in current_positions if "body" in p and "longitude" in p}
        previous_dict = {p.get("body"): p for p in previous_positions if "body" in p and "longitude" in p}
        
        # Planets that can be retrograde (not Sun/Moon - they don't retrograde)
        retrograde_capable = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "Chiron"]
        
        for planet in retrograde_capable:
            if planet not in current_dict or planet not in previous_dict:
                continue
            
            current_long = current_dict[planet].get("longitude")
            previous_long = previous_dict[planet].get("longitude")
            
            if current_long is None or previous_long is None:
                continue
            
            # Calculate longitude difference, handling wrap-around (0-360 degrees)
            diff = current_long - previous_long
            
            # Normalize difference to -180 to +180 range
            if diff > 180:
                diff -= 360
            elif diff < -180:
                diff += 360
            
            # If longitude decreased (negative diff), planet is retrograde
            # Use small threshold to account for calculation precision
            if diff < -0.01:  # Small threshold to avoid false positives from rounding
                retrograde.append(planet)
        
        return retrograde
    
    def _generate_retrograde_descriptions(
        self,
        retrograde_planets: List[str],
        locale: str | None = None,
    ) -> Dict[str, str]:
        """Generate human-readable descriptions for retrograde planets."""
        descriptions = {}
        
        # Basic descriptions (can be localized later)
        planet_descriptions = {
            "Mercury": "Mercury is retrograde - communication, technology, and travel may be affected. Review and reflect rather than starting new projects.",
            "Venus": "Venus is retrograde - relationships and values are under review. Reassess what you truly value and want in connections.",
            "Mars": "Mars is retrograde - energy and action may feel blocked or redirected. Focus on internal motivation rather than external goals.",
            "Jupiter": "Jupiter is retrograde - expansion and growth opportunities may be internal. Review your beliefs and philosophy.",
            "Saturn": "Saturn is retrograde - structures and responsibilities are being re-examined. Internalize lessons about boundaries and discipline.",
            "Uranus": "Uranus is retrograde - innovation and change may come from within. Review your need for freedom and independence.",
            "Neptune": "Neptune is retrograde - intuition and dreams may be more accessible. Reflect on your spiritual and creative needs.",
            "Pluto": "Pluto is retrograde - transformation happens at deeper levels. Review power dynamics and patterns of control.",
            "Chiron": "Chiron is retrograde - healing and wound work is internal. Focus on self-compassion and understanding your pain patterns.",
        }
        
        for planet in retrograde_planets:
            descriptions[planet] = planet_descriptions.get(planet, f"{planet} is retrograde.")
        
        return descriptions
    
    async def _calculate_ingresses(
        self,
        forecast_date: date,
        coordinates: Dict[str, float],
        days_ahead: int = 30,
    ) -> List[models.PlanetaryIngress]:
        """
        Calculate upcoming planetary ingresses (planets entering new zodiac signs).
        
        An ingress occurs when a planet's longitude crosses a sign boundary (0°, 30°, 60°, etc.).
        
        Args:
            forecast_date: Starting date for ingress detection
            coordinates: Coordinates for chart calculation
            days_ahead: Number of days to look ahead for ingresses
        """
        ingresses = []
        
        # Signs in order (0° = Aries, 30° = Taurus, etc.)
        signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                 "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        
        # Planets that have ingresses (all planets)
        ingress_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
        
        # Get current positions
        current_positions = await self._get_planet_positions(forecast_date, coordinates)
        current_dict = {p.get("body"): p for p in current_positions if "body" in p and "longitude" in p}
        
        # Check each planet for upcoming ingresses
        for planet in ingress_planets:
            if planet not in current_dict:
                continue
            
            current_long = current_dict[planet].get("longitude")
            if current_long is None:
                continue
            
            current_sign_index = int(current_long / 30) % 12
            current_sign = signs[current_sign_index]
            
            # Check future positions to detect sign changes
            for day_offset in range(1, days_ahead + 1):
                check_date = forecast_date + timedelta(days=day_offset)
                try:
                    future_positions = await self._get_planet_positions(check_date, coordinates)
                    future_dict = {p.get("body"): p for p in future_positions if "body" in p and "longitude" in p}
                    
                    if planet not in future_dict:
                        continue
                    
                    future_long = future_dict[planet].get("longitude")
                    if future_long is None:
                        continue
                    
                    future_sign_index = int(future_long / 30) % 12
                    future_sign = signs[future_sign_index]
                    
                    # If sign changed, this is an ingress
                    if future_sign_index != current_sign_index:
                        # Check if we already added this ingress
                        existing = next((i for i in ingresses if i.planet == planet and i.sign == future_sign), None)
                        if not existing:
                            ingresses.append(models.PlanetaryIngress(
                                planet=planet,
                                sign=future_sign,
                                ingress_date=check_date.isoformat(),
                            ))
                            # Update current sign for next check
                            current_sign_index = future_sign_index
                            current_sign = future_sign
                        break  # Found ingress for this planet, move to next planet
                except Exception:
                    # If calculation fails, skip this day
                    continue
        
        # Sort ingresses by date
        ingresses.sort(key=lambda x: x.ingress_date)
        
        return ingresses


async def get_retrograde_service() -> RetrogradeService:
    """Dependency function for RetrogradeService."""
    return RetrogradeService()

