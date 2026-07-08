"""Synastry service: compatibility analysis between two natal charts."""

from __future__ import annotations

from typing import Dict, List, Any, Optional
from math import fabs

from todayflow_backend.core import models
from todayflow_backend.services import astro
from todayflow_backend.services.aspects import AspectEngine


class SynastryService:
    """Service for calculating synastry (compatibility) between two natal charts."""
    
    def __init__(self, aspect_engine: AspectEngine | None = None):
        self.aspect_engine = aspect_engine or AspectEngine()
    
    async def calculate_synastry(
        self,
        chart1: astro.ChartResponse,
        chart2: astro.ChartResponse,
        locale: str | None = None,
    ) -> models.SynastryReport:
        """
        Calculate full synastry between two natal charts.
        
        Returns:
        - Planet-to-planet aspects
        - Planet-to-angle aspects (ASC/MC)
        - House overlays (his planets in her houses, vice versa)
        - Strong aspects (Venus/Mars/Moon/Saturn/Pluto emphasis)
        - Compatibility summary
        """
        positions1 = {p["body"]: p for p in chart1.positions if "body" in p and "longitude" in p}
        positions2 = {p["body"]: p for p in chart2.positions if "body" in p and "longitude" in p}
        houses1 = chart1.houses or {}
        houses2 = chart2.houses or {}
        
        # Calculate planet-to-planet aspects
        planet_aspects = self._calculate_planet_aspects(positions1, positions2)
        
        # Calculate planet-to-angle aspects (ASC/MC)
        angle_aspects = self._calculate_angle_aspects(positions1, positions2, houses1, houses2)
        
        # Calculate house overlays
        house_overlays = self._calculate_house_overlays(positions1, positions2, houses1, houses2)
        
        # Identify strong aspects (Venus/Mars/Moon/Saturn/Pluto emphasis)
        strong_aspects = self._identify_strong_aspects(planet_aspects, angle_aspects)
        
        # Generate compatibility summary
        compatibility_summary = self._generate_compatibility_summary(
            planet_aspects, angle_aspects, house_overlays, strong_aspects, locale=locale
        )
        
        return models.SynastryReport(
            planet_aspects=planet_aspects,
            angle_aspects=angle_aspects,
            house_overlays=house_overlays,
            strong_aspects=strong_aspects,
            compatibility_summary=compatibility_summary,
        )
    
    def _calculate_planet_aspects(
        self,
        positions1: Dict[str, Dict],
        positions2: Dict[str, Dict],
    ) -> List[models.SynastryAspect]:
        """Calculate aspects between person1's planets and person2's planets."""
        aspects = []
        aspect_map = self.aspect_engine.aspect_map
        
        # Key planets to analyze (including Chiron and Nodes if available)
        key_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "Chiron", "North Node", "South Node"]
        
        for planet1 in key_planets:
            if planet1 not in positions1:
                continue
            
            long1 = positions1[planet1]["longitude"]
            
            for planet2 in key_planets:
                if planet2 not in positions2:
                    continue
                
                long2 = positions2[planet2]["longitude"]
                
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
                
                if aspect_id:
                    # Determine strength
                    if orb_delta <= 1:
                        strength = "exact"
                    elif orb_delta <= 3:
                        strength = "strong"
                    elif orb_delta <= 5:
                        strength = "medium"
                    else:
                        strength = "weak"
                    
                    # Only include significant aspects
                    if strength in ["exact", "strong", "medium"]:
                        aspects.append(models.SynastryAspect(
                            planet1=planet1,
                            planet2=planet2,
                            aspect=aspect_id,
                            orb=round(orb_delta, 2),
                            strength=strength,
                            description=self._describe_synastry_aspect(planet1, planet2, aspect_id),
                        ))
        
        return aspects
    
    def _calculate_angle_aspects(
        self,
        positions1: Dict[str, Dict],
        positions2: Dict[str, Dict],
        houses1: Dict[str, Any],
        houses2: Dict[str, Any],
    ) -> List[models.SynastryAngleAspect]:
        """Calculate aspects between planets and angles (ASC/MC)."""
        aspects = []
        aspect_map = self.aspect_engine.aspect_map
        
        # Get ASC and MC from houses (house 1 = ASC, house 10 = MC)
        asc1_long = self._get_house_cusp(houses1, 1) or houses1.get("Ascendant")
        mc1_long = self._get_house_cusp(houses1, 10) or houses1.get("MC") or houses1.get("Midheaven")
        asc2_long = self._get_house_cusp(houses2, 1) or houses2.get("Ascendant")
        mc2_long = self._get_house_cusp(houses2, 10) or houses2.get("MC") or houses2.get("Midheaven")
        
        # If ASC/MC are dicts, extract longitude
        if isinstance(asc1_long, dict):
            asc1_long = asc1_long.get("longitude") or asc1_long.get("cusp")
        if isinstance(mc1_long, dict):
            mc1_long = mc1_long.get("longitude") or mc1_long.get("cusp")
        if isinstance(asc2_long, dict):
            asc2_long = asc2_long.get("longitude") or asc2_long.get("cusp")
        if isinstance(mc2_long, dict):
            mc2_long = mc2_long.get("longitude") or mc2_long.get("cusp")
        
        # Key planets
        key_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
        
        # Person 1's planets to Person 2's angles
        if asc2_long is not None:
            for planet in key_planets:
                if planet not in positions1:
                    continue
                aspect_id, orb = self._resolve_aspect_to_angle(positions1[planet]["longitude"], asc2_long, aspect_map)
                if aspect_id:
                    aspects.append(models.SynastryAngleAspect(
                        planet=planet,
                        angle="ASC",
                        person_number=1,
                        aspect=aspect_id,
                        orb=orb,
                        description=f"{planet} aspects Person 2's ASC",
                    ))
        
        if mc2_long is not None:
            for planet in key_planets:
                if planet not in positions1:
                    continue
                aspect_id, orb = self._resolve_aspect_to_angle(positions1[planet]["longitude"], mc2_long, aspect_map)
                if aspect_id:
                    aspects.append(models.SynastryAngleAspect(
                        planet=planet,
                        angle="MC",
                        person_number=1,
                        aspect=aspect_id,
                        orb=orb,
                        description=f"{planet} aspects Person 2's MC",
                    ))
        
        # Person 2's planets to Person 1's angles
        if asc1_long is not None:
            for planet in key_planets:
                if planet not in positions2:
                    continue
                aspect_id, orb = self._resolve_aspect_to_angle(positions2[planet]["longitude"], asc1_long, aspect_map)
                if aspect_id:
                    aspects.append(models.SynastryAngleAspect(
                        planet=planet,
                        angle="ASC",
                        person_number=2,
                        aspect=aspect_id,
                        orb=orb,
                        description=f"{planet} aspects Person 1's ASC",
                    ))
        
        if mc1_long is not None:
            for planet in key_planets:
                if planet not in positions2:
                    continue
                aspect_id, orb = self._resolve_aspect_to_angle(positions2[planet]["longitude"], mc1_long, aspect_map)
                if aspect_id:
                    aspects.append(models.SynastryAngleAspect(
                        planet=planet,
                        angle="MC",
                        person_number=2,
                        aspect=aspect_id,
                        orb=orb,
                        description=f"{planet} aspects Person 1's MC",
                    ))
        
        return aspects
    
    def _calculate_house_overlays(
        self,
        positions1: Dict[str, Dict],
        positions2: Dict[str, Dict],
        houses1: Dict[str, Any],
        houses2: Dict[str, Any],
    ) -> List[models.HouseOverlay]:
        """Calculate house overlays (person1's planets in person2's houses and vice versa)."""
        overlays = []
        
        # Person 1's planets in Person 2's houses
        for planet, pos in positions1.items():
            planet_long = pos.get("longitude")
            if planet_long is None:
                continue
            
            # Find which house in chart2 this planet falls into
            house_number = self._calculate_house_for_longitude(planet_long, houses2)
            if house_number:
                overlays.append(models.HouseOverlay(
                    planet=planet,
                    house=house_number,
                    person_number=1,
                    description=f"Person 1's {planet} in Person 2's {house_number}th house",
                    significance=self._house_overlay_significance(planet, house_number),
                ))
        
        # Person 2's planets in Person 1's houses
        for planet, pos in positions2.items():
            planet_long = pos.get("longitude")
            if planet_long is None:
                continue
            
            # Find which house in chart1 this planet falls into
            house_number = self._calculate_house_for_longitude(planet_long, houses1)
            if house_number:
                overlays.append(models.HouseOverlay(
                    planet=planet,
                    house=house_number,
                    person_number=2,
                    description=f"Person 2's {planet} in Person 1's {house_number}th house",
                    significance=self._house_overlay_significance(planet, house_number),
                ))
        
        return overlays
    
    def _identify_strong_aspects(
        self,
        planet_aspects: List[models.SynastryAspect],
        angle_aspects: List[models.SynastryAngleAspect],
    ) -> List[models.SynastryAspect]:
        """Identify especially significant aspects (Venus/Mars/Moon/Saturn/Pluto emphasis)."""
        strong_planets = ["Venus", "Mars", "Moon", "Saturn", "Pluto"]
        strong = []
        
        for aspect in planet_aspects:
            if aspect.planet1 in strong_planets or aspect.planet2 in strong_planets:
                if aspect.strength in ["exact", "strong"]:
                    strong.append(aspect)
        
        return strong
    
    def _generate_compatibility_summary(
        self,
        planet_aspects: List[models.SynastryAspect],
        angle_aspects: List[models.SynastryAngleAspect],
        house_overlays: List[models.HouseOverlay],
        strong_aspects: List[models.SynastryAspect],
        locale: str | None = None,
    ) -> models.CompatibilitySummary:
        """Generate overall compatibility summary."""
        # Count harmonious vs challenging aspects
        harmonious = sum(1 for a in planet_aspects if a.aspect in ["trine", "sextile", "conjunction"])
        challenging = sum(1 for a in planet_aspects if a.aspect in ["square", "opposition"])
        
        # Key relationship indicators
        venus_mars_aspects = [a for a in planet_aspects if 
                             (a.planet1 == "Venus" and a.planet2 == "Mars") or
                             (a.planet1 == "Mars" and a.planet2 == "Venus")]
        moon_aspects = [a for a in planet_aspects if a.planet1 == "Moon" or a.planet2 == "Moon"]
        
        # House overlays significance
        seventh_house_overlays = [o for o in house_overlays if o.house == 7]
        fourth_house_overlays = [o for o in house_overlays if o.house == 4]
        
        # Generate summary text
        strengths = []
        triggers = []
        relationship_type = "Balanced"

        if venus_mars_aspects:
            strengths.append("Между вами быстро возникает притяжение: здесь легко загорается интерес, флирт и ощущение живого контакта." if (locale or "").startswith("ru") else "Strong romantic and physical attraction")
        if moon_aspects:
            strengths.append("Есть эмоциональный отклик: вы довольно быстро считываете состояние друг друга, даже когда слова еще не найдены." if (locale or "").startswith("ru") else "Emotional connection and understanding")
        if seventh_house_overlays:
            strengths.append("Связь естественно тянется к партнерству: здесь проще думать в логике «мы», а не только «я»." if (locale or "").startswith("ru") else "Natural partnership dynamics")
        if challenging > harmonious * 2:
            triggers.append("Разница в реакциях может быстро поднимать напряжение: если молчать об ожиданиях, спор легко уйдет не в суть, а в форму." if (locale or "").startswith("ru") else "Potential for conflict and tension")
            relationship_type = "Challenging"
        elif harmonious > challenging * 2:
            relationship_type = "Harmonious"
        
        return models.CompatibilitySummary(
            overall_score=min(100, max(0, 50 + (harmonious - challenging) * 5)),
            relationship_type=relationship_type,
            strengths=strengths,
            triggers=triggers,
            recommendations=self._generate_recommendations(planet_aspects, angle_aspects, house_overlays, locale=locale),
        )
    
    def _resolve_aspect_to_angle(self, planet_long: float, angle_long: float, aspect_map: Dict) -> tuple[str | None, float]:
        """Resolve aspect between planet and angle."""
        raw_difference = fabs(planet_long - angle_long) % 360
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
            return aspect_id, round(orb_delta, 2)
        return None, 0.0
    
    def _calculate_house_for_longitude(self, longitude: float, houses: Dict[str, Any]) -> int | None:
        """
        Calculate which house a longitude falls into based on house cusps.
        
        Supports multiple formats:
        1. {"1": 120.5, "2": 150.3, ...} - direct longitude values
        2. {"1": {"longitude": 120.5}, "2": {"longitude": 150.3}, ...} - dict with longitude key
        3. {"1": {"cusp": 120.5}, "2": {"cusp": 150.3}, ...} - dict with cusp key
        4. {"house1": 120.5, "house2": 150.3, ...} - house prefix format
        5. {"1th": 120.5, "2th": 150.3, ...} - th suffix format (less common)
        """
        if not houses:
            return None
        
        # Try to find house cusps
        house_cusps = []
        for house_num in range(1, 13):
            house_key = str(house_num)
            
            # Try various key formats
            house_data = (
                houses.get(house_key) or
                houses.get(f"house{house_key}") or
                houses.get(f"{house_key}th") or
                houses.get(f"House{house_key}")
            )
            
            if house_data is None:
                continue
            
            # Extract longitude from various formats
            cusp_long = None
            if isinstance(house_data, dict):
                cusp_long = (
                    house_data.get("longitude") or
                    house_data.get("cusp") or
                    house_data.get("cusp_longitude") or
                    house_data.get("position")
                )
            elif isinstance(house_data, (int, float)):
                cusp_long = house_data
            elif isinstance(house_data, str):
                # Try to parse string as float
                try:
                    cusp_long = float(house_data)
                except (ValueError, TypeError):
                    continue
            
            if cusp_long is not None:
                house_cusps.append((house_num, float(cusp_long)))
        
        if len(house_cusps) < 10:
            # Need at least 10 house cusps for reasonable accuracy
            # (some house systems may not have all 12, but 10+ is minimum)
            return None
        
        # Sort by longitude and find which house the planet falls into
        # Normalize longitudes to 0-360
        house_cusps_normalized = [(num, long_val % 360) for num, long_val in house_cusps]
        house_cusps_normalized.sort(key=lambda x: x[1])
        
        planet_long_norm = longitude % 360
        
        # Find the house: planet is in the house that starts at or before its longitude
        # and ends before the next house's cusp
        for i in range(len(house_cusps_normalized)):
            current_house, current_cusp = house_cusps_normalized[i]
            next_house, next_cusp = house_cusps_normalized[(i + 1) % len(house_cusps_normalized)]
            
            # Handle wrap-around (house 12 to house 1)
            if current_cusp > next_cusp:
                # Wrap-around case: house spans across 0/360 boundary
                if planet_long_norm >= current_cusp or planet_long_norm < next_cusp:
                    return current_house
            else:
                # Normal case: house is within a continuous longitude range
                if current_cusp <= planet_long_norm < next_cusp:
                    return current_house
        
        # Fallback: if we have cusps but calculation failed, return house of closest cusp
        if house_cusps_normalized:
            # Find closest cusp
            min_dist = 360
            closest_house = house_cusps_normalized[0][0]
            for house_num, cusp_long in house_cusps_normalized:
                dist = abs(planet_long_norm - cusp_long)
                if dist > 180:
                    dist = 360 - dist
                if dist < min_dist:
                    min_dist = dist
                    closest_house = house_num
            return closest_house
        
        return None
    
    def _get_house_cusp(self, houses: Dict[str, Any], house_num: int) -> Any:
        """
        Extract house cusp longitude from houses dict.
        Supports multiple formats similar to _calculate_house_for_longitude.
        """
        if not houses:
            return None
        
        house_key = str(house_num)
        
        # Try various key formats
        house_data = (
            houses.get(house_key) or
            houses.get(f"house{house_key}") or
            houses.get(f"{house_key}th") or
            houses.get(f"House{house_key}")
        )
        
        if house_data is None:
            return None
        
        # Return the raw data (caller will extract longitude if needed)
        return house_data
    
    def _house_overlay_significance(self, planet: str, house: int) -> str:
        """Return significance of planet in house overlay."""
        significances = {
            (1,): "Identity and first impressions",
            (4,): "Home and family life",
            (7,): "Partnership and relationship dynamics",
            (10,): "Public image and career",
        }
        return significances.get((house,), f"{planet} activates {house}th house themes")
    
    def _describe_synastry_aspect(self, planet1: str, planet2: str, aspect: str) -> str:
        """Generate description of synastry aspect."""
        return f"{planet1} {aspect} {planet2}"
    
    def _generate_recommendations(
        self,
        planet_aspects: List[models.SynastryAspect],
        angle_aspects: List[models.SynastryAngleAspect],
        house_overlays: List[models.HouseOverlay],
        locale: str | None = None,
    ) -> List[str]:
        """Generate relationship recommendations based on synastry."""
        recommendations = []
        
        # Analyze aspects for recommendations
        venus_aspects = [a for a in planet_aspects if a.planet1 == "Venus" or a.planet2 == "Venus"]
        mars_aspects = [a for a in planet_aspects if a.planet1 == "Mars" or a.planet2 == "Mars"]
        saturn_aspects = [a for a in planet_aspects if a.planet1 == "Saturn" or a.planet2 == "Saturn"]
        
        if venus_aspects and any(a.aspect in ["trine", "sextile"] for a in venus_aspects):
            recommendations.append("Не считайте симпатию чем-то само собой разумеющимся: чаще проговаривайте, за что именно вы цените друг друга и почему вам хорошо рядом." if (locale or "").startswith("ru") else "Focus on shared values and appreciation")
        
        if mars_aspects and any(a.aspect in ["square", "opposition"] for a in mars_aspects):
            recommendations.append("Следите не только за предметом спора, но и за тем, кто давит, кто замолкает и в какой момент разговор превращается в борьбу за контроль." if (locale or "").startswith("ru") else "Be mindful of power dynamics and conflict styles")
        
        if saturn_aspects:
            recommendations.append("Этой связи полезна структура: ясные договоренности, выдержка и готовность возвращаться к важным темам без театра и накопленных обид." if (locale or "").startswith("ru") else "Structure and commitment are important themes")
        
        if not recommendations:
            recommendations.append("Чем честнее вы говорите о своих нуждах, границах и темпе сближения, тем меньше связь зависит от догадок и случайных обид." if (locale or "").startswith("ru") else "Explore and communicate openly about your needs")
        
        return recommendations


async def get_synastry_service() -> SynastryService:
    """Dependency function for SynastryService."""
    return SynastryService()
