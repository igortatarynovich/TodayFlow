"""Composite and Davison chart service for relationship analysis."""

from __future__ import annotations

from typing import Dict, List, Any, Optional
from datetime import date, datetime, time
from math import fabs

from todayflow_backend.core import models
from todayflow_backend.services import astro
from todayflow_backend.services.aspects import AspectEngine


class CompositeChartService:
    """Service for calculating Composite and Davison charts."""
    
    def __init__(self, aspect_engine: AspectEngine | None = None):
        self.aspect_engine = aspect_engine or AspectEngine()

    @staticmethod
    def _positions_dict_for_composite(chart: astro.ChartResponse) -> Dict[str, Dict]:
        """Единый ключ тела (как в key_planets), иначе midpoints пустые при body в другом регистре."""
        out: Dict[str, Dict] = {}
        for p in chart.positions:
            if not isinstance(p, dict) or "body" not in p or "longitude" not in p:
                continue
            raw = str(p["body"]).strip()
            key = raw.title() if raw else raw
            out[key] = p
        return out
    
    async def calculate_composite_chart(
        self,
        chart1: astro.ChartResponse,
        chart2: astro.ChartResponse,
        locale: str | None = None,
    ) -> models.CompositeChart:
        """
        Calculate Composite chart (midpoint method).
        
        Composite chart uses midpoints between two people's planetary positions
        to create a "relationship chart" that shows how the relationship functions.
        
        Steps:
        1. Calculate midpoints for each planet pair
        2. Calculate midpoints for house cusps
        3. Calculate aspects in the composite chart
        4. Interpret the composite chart
        """
        positions1 = self._positions_dict_for_composite(chart1)
        positions2 = self._positions_dict_for_composite(chart2)
        houses1 = chart1.houses or {}
        houses2 = chart2.houses or {}
        
        # Calculate composite positions (midpoints)
        composite_positions = self._calculate_midpoints(positions1, positions2)
        
        # Calculate composite houses (midpoints of house cusps)
        composite_houses = self._calculate_composite_houses(houses1, houses2)
        
        # Calculate aspects in composite chart
        composite_aspects = self._calculate_composite_aspects(composite_positions, locale=locale)
        
        # Interpret composite chart
        interpretation = self._interpret_composite_chart(
            composite_positions, composite_houses, composite_aspects, locale=locale
        )
        
        return models.CompositeChart(
            positions=composite_positions,
            houses=composite_houses,
            aspects=composite_aspects,
            interpretation=interpretation,
        )
    
    async def calculate_davison_chart(
        self,
        chart1: astro.ChartResponse,
        chart2: astro.ChartResponse,
        birth_date1: date,
        birth_time1: time | None,
        birth_date2: date,
        birth_time2: time | None,
        locale: str | None = None,
    ) -> models.DavisonChart:
        """
        Calculate Davison chart (time-space midpoint method).
        
        Davison chart uses the midpoint of:
        - Birth dates/times
        - Birth locations (lat/long)
        
        This creates a chart for the "relationship moment" at the midpoint
        of when and where the two people were born.
        """
        # Calculate midpoint date/time
        midpoint_datetime = self._calculate_midpoint_datetime(
            birth_date1, birth_time1, birth_date2, birth_time2
        )
        
        # Calculate midpoint location (requires coordinates from charts)
        # For now, we'll use a simplified approach
        # In full implementation, we'd need coordinates from birth data
        
        # The Davison chart would be calculated by calling AstroService
        # with the midpoint date/time and location
        # For now, this is a placeholder structure
        
        return models.DavisonChart(
            midpoint_date=midpoint_datetime.date().isoformat(),
            midpoint_time=midpoint_datetime.time().isoformat(),
            description="Davison chart calculated from midpoint of birth data",
            # Note: Full implementation would compute actual chart via AstroService
        )
    
    def _calculate_midpoints(
        self,
        positions1: Dict[str, Dict],
        positions2: Dict[str, Dict],
    ) -> List[Dict[str, Any]]:
        """Calculate midpoints between two sets of planetary positions."""
        composite_positions = []
        # Include Chiron and Nodes if available
        key_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "Chiron", "North Node", "South Node"]
        
        for planet in key_planets:
            if planet not in positions1 or planet not in positions2:
                continue
            
            long1 = positions1[planet]["longitude"]
            long2 = positions2[planet]["longitude"]
            
            # Calculate midpoint longitude
            midpoint_long = self._midpoint_longitude(long1, long2)
            
            # Determine sign for midpoint (simplified)
            midpoint_sign = self._longitude_to_sign(midpoint_long)
            
            composite_positions.append({
                "body": planet,
                "longitude": midpoint_long,
                "sign": midpoint_sign,
                "description": f"{planet} midpoint",
            })
        
        return composite_positions
    
    def _calculate_composite_houses(
        self,
        houses1: Dict[str, Any],
        houses2: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Calculate composite house cusps (midpoints of house cusps)."""
        composite_houses = {}
        
        for house_num in range(1, 13):
            house_key = str(house_num)
            
            # Get cusp longitudes from both charts
            cusp1 = self._get_house_cusp(houses1, house_num)
            cusp2 = self._get_house_cusp(houses2, house_num)
            
            if cusp1 is not None and cusp2 is not None:
                midpoint_cusp = self._midpoint_longitude(cusp1, cusp2)
                composite_houses[house_key] = {
                    "longitude": midpoint_cusp,
                    "cusp": midpoint_cusp,
                }
        
        return composite_houses
    
    def _calculate_composite_aspects(
        self,
        composite_positions: List[Dict[str, Any]],
        locale: str | None = None,
    ) -> List[models.CompositeAspect]:
        """Calculate aspects in the composite chart."""
        aspects = []
        aspect_map = self.aspect_engine.aspect_map
        
        # Convert to dict for easier lookup
        positions_dict = {p["body"]: p for p in composite_positions}
        
        # Calculate aspects between all planet pairs
        planet_list = list(positions_dict.keys())
        for i, planet1 in enumerate(planet_list):
            for planet2 in planet_list[i+1:]:
                long1 = positions_dict[planet1]["longitude"]
                long2 = positions_dict[planet2]["longitude"]
                
                # Calculate aspect
                raw_difference = fabs(long1 - long2) % 360
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
                    aspects.append(models.CompositeAspect(
                        planet1=planet1,
                        planet2=planet2,
                        aspect=aspect_id,
                        orb=round(orb_delta, 2),
                        strength="exact" if orb_delta <= 1 else "strong" if orb_delta <= 3 else "medium",
                    ))
        
        return aspects
    
    def _interpret_composite_chart(
        self,
        composite_positions: List[Dict[str, Any]],
        composite_houses: Dict[str, Any],
        composite_aspects: List[models.CompositeAspect],
        locale: str | None = None,
    ) -> models.CompositeInterpretation:
        """Interpret the composite chart for relationship dynamics."""
        # Analyze key areas
        sun_pos = next((p for p in composite_positions if p["body"] == "Sun"), None)
        moon_pos = next((p for p in composite_positions if p["body"] == "Moon"), None)
        venus_pos = next((p for p in composite_positions if p["body"] == "Venus"), None)
        mars_pos = next((p for p in composite_positions if p["body"] == "Mars"), None)
        
        # Analyze aspects
        venus_mars_aspect = next((a for a in composite_aspects if 
                                  (a.planet1 == "Venus" and a.planet2 == "Mars") or
                                  (a.planet1 == "Mars" and a.planet2 == "Venus")), None)
        
        sun_moon_aspect = next((a for a in composite_aspects if 
                               (a.planet1 == "Sun" and a.planet2 == "Moon") or
                               (a.planet1 == "Moon" and a.planet2 == "Sun")), None)
        
        # Generate interpretation
        strengths = []
        tensions = []
        growth_areas = []
        what_holds_together = []
        
        if venus_mars_aspect and venus_mars_aspect.aspect in ["trine", "sextile", "conjunction"]:
            strengths.append("Strong romantic and sexual chemistry")
            what_holds_together.append("Physical and emotional attraction")
        
        if sun_moon_aspect and sun_moon_aspect.aspect in ["trine", "sextile"]:
            strengths.append("Emotional compatibility and understanding")
            what_holds_together.append("Mutual emotional support")
        elif sun_moon_aspect and sun_moon_aspect.aspect in ["square", "opposition"]:
            tensions.append("Different emotional needs and expression styles")
            growth_areas.append("Learning to understand each other's emotional language")
        
        # Analyze houses
        sun_house = self._planet_in_house(sun_pos, composite_houses) if sun_pos else None
        moon_house = self._planet_in_house(moon_pos, composite_houses) if moon_pos else None
        
        if sun_house == 7:
            what_holds_together.append("Partnership is central to the relationship")
        if moon_house == 4:
            strengths.append("Strong sense of home and emotional security together")
        
        return models.CompositeInterpretation(
            strengths=strengths,
            tensions=tensions,
            growth_areas=growth_areas,
            what_holds_together=what_holds_together,
            relationship_dynamics=self._describe_relationship_dynamics(composite_positions, composite_aspects),
        )
    
    def _midpoint_longitude(self, long1: float, long2: float) -> float:
        """Calculate midpoint longitude between two longitudes."""
        # Handle wrap-around (0-360 degrees)
        diff = fabs(long1 - long2)
        if diff > 180:
            # Wrap around case
            if long1 < long2:
                long1 += 360
            else:
                long2 += 360
        
        midpoint = (long1 + long2) / 2.0
        return midpoint % 360
    
    def _longitude_to_sign(self, longitude: float) -> str:
        """Convert longitude to zodiac sign."""
        signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                 "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        sign_index = int(longitude / 30)
        return signs[sign_index % 12]
    
    def _get_house_cusp(self, houses: Dict[str, Any], house_num: int) -> float | None:
        """Get house cusp longitude from houses dict."""
        house_key = str(house_num)
        house_data = houses.get(house_key) or houses.get(f"{house_num}th")
        
        if house_data is None:
            return None
        
        if isinstance(house_data, dict):
            return house_data.get("longitude") or house_data.get("cusp")
        elif isinstance(house_data, (int, float)):
            return float(house_data)
        
        return None
    
    def _planet_in_house(self, planet_pos: Dict[str, Any], houses: Dict[str, Any]) -> int | None:
        """Determine which house a planet is in."""
        if not planet_pos or "longitude" not in planet_pos:
            return None
        
        planet_long = planet_pos["longitude"]
        
        # Find house by checking cusps
        for house_num in range(1, 13):
            cusp = self._get_house_cusp(houses, house_num)
            next_cusp = self._get_house_cusp(houses, (house_num % 12) + 1)
            
            if cusp is None:
                continue
            
            if next_cusp is None:
                next_cusp = cusp + 30  # Approximate if missing
            
            # Handle wrap-around
            if cusp > next_cusp:
                if planet_long >= cusp or planet_long < next_cusp:
                    return house_num
            else:
                if cusp <= planet_long < next_cusp:
                    return house_num
        
        return None
    
    def _calculate_midpoint_datetime(
        self,
        date1: date,
        time1: time | None,
        date2: date,
        time2: time | None,
    ) -> datetime:
        """Calculate midpoint datetime between two birth dates/times."""
        # Convert to datetime
        dt1 = datetime.combine(date1, time1 or time(12, 0))
        dt2 = datetime.combine(date2, time2 or time(12, 0))
        
        # Calculate midpoint
        midpoint_timestamp = (dt1.timestamp() + dt2.timestamp()) / 2.0
        return datetime.fromtimestamp(midpoint_timestamp)
    
    def _describe_relationship_dynamics(
        self,
        composite_positions: List[Dict[str, Any]],
        composite_aspects: List[models.CompositeAspect],
    ) -> str:
        """Generate description of relationship dynamics from composite chart."""
        # Analyze key aspects and positions
        challenging_aspects = sum(1 for a in composite_aspects if a.aspect in ["square", "opposition"])
        harmonious_aspects = sum(1 for a in composite_aspects if a.aspect in ["trine", "sextile"])
        
        if harmonious_aspects > challenging_aspects * 2:
            return "The relationship flows naturally with mutual support and understanding."
        elif challenging_aspects > harmonious_aspects * 2:
            return "The relationship involves significant growth through challenges and differences."
        else:
            return "The relationship has a balanced dynamic of harmony and growth opportunities."


async def get_composite_chart_service() -> CompositeChartService:
    """Dependency function for CompositeChartService."""
    return CompositeChartService()

