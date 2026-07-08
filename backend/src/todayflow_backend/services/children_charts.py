"""Children charts service: specialized interpretations for children."""

from __future__ import annotations

from typing import Dict, List, Any, Optional
from todayflow_backend.core import models
from todayflow_backend.services import astro
from todayflow_backend.services.psychological_layer import PsychologicalLayerService
from todayflow_backend.services.aspects import AspectEngine


class ChildrenChartsService:
    """Service for generating specialized interpretations for children's charts."""
    
    def __init__(
        self,
        psychological_service: PsychologicalLayerService | None = None,
        aspect_engine: AspectEngine | None = None,
    ):
        self.psychological_service = psychological_service or PsychologicalLayerService()
        self.aspect_engine = aspect_engine or AspectEngine()
    
    async def generate_children_report(
        self,
        chart: astro.ChartResponse,
        internal_model: models.InternalModelSnapshot,
        snapshot: models.ChartSnapshot,
        child_age: Optional[int] = None,
        locale: str | None = None,
    ) -> models.ChildrenChartReport:
        """
        Generate specialized report for a child's chart.
        
        Focus areas:
        - Temperament (Sun/Moon/ASC + elements)
        - Sensitivity and stress (Moon/Neptune aspects)
        - Boundaries and discipline (Saturn)
        - Learning and interests (Mercury/Jupiter)
        - Parental support strategies
        """
        positions = {p["body"]: p for p in chart.positions if "body" in p}
        houses = chart.houses or {}
        
        # Get aspects
        aspect_response = self.aspect_engine.callouts(chart.positions, locale=locale)
        aspects_by_pair: Dict[str, Any] = {}
        for callout in aspect_response.callouts:
            bodies = callout.bodies.split(" · ")
            if len(bodies) == 2:
                key1 = f"{bodies[0]}-{bodies[1]}"
                key2 = f"{bodies[1]}-{bodies[0]}"
                aspects_by_pair[key1] = callout
                aspects_by_pair[key2] = callout
        
        # Analyze child-specific areas
        temperament = self._analyze_temperament(positions, snapshot, internal_model, locale=locale)
        sensitivity = self._analyze_sensitivity(positions, houses, aspects_by_pair, locale=locale)
        boundaries_discipline = self._analyze_boundaries_discipline(positions, houses, aspects_by_pair, locale=locale)
        learning_interests = self._analyze_learning_interests(positions, houses, aspects_by_pair, locale=locale)
        parental_strategies = self._generate_parental_strategies(
            temperament, sensitivity, boundaries_discipline, learning_interests, child_age, locale=locale
        )
        
        return models.ChildrenChartReport(
            temperament=temperament,
            sensitivity=sensitivity,
            boundaries_discipline=boundaries_discipline,
            learning_interests=learning_interests,
            parental_strategies=parental_strategies,
        )
    
    def _analyze_temperament(
        self,
        positions: Dict[str, Dict],
        snapshot: models.ChartSnapshot,
        internal_model: models.InternalModelSnapshot,
        locale: str | None = None,
    ) -> models.ChildTemperament:
        """Analyze child's temperament from Sun/Moon/ASC and elements."""
        sun_sign = snapshot.sun
        moon_sign = snapshot.moon
        rising_sign = snapshot.rising
        
        # Determine element balance
        elements = {"fire": 0, "earth": 0, "air": 0, "water": 0}
        element_map = {
            "Aries": "fire", "Leo": "fire", "Sagittarius": "fire",
            "Taurus": "earth", "Virgo": "earth", "Capricorn": "earth",
            "Gemini": "air", "Libra": "air", "Aquarius": "air",
            "Cancer": "water", "Scorpio": "water", "Pisces": "water",
        }
        
        if sun_sign in element_map:
            elements[element_map[sun_sign]] += 1
        if moon_sign in element_map:
            elements[element_map[moon_sign]] += 1
        if rising_sign in element_map:
            elements[element_map[rising_sign]] += 1
        
        dominant_element = max(elements, key=elements.get) if any(elements.values()) else "balanced"
        
        # Determine modality (cardinal, fixed, mutable)
        modality_map = {
            "Aries": "cardinal", "Cancer": "cardinal", "Libra": "cardinal", "Capricorn": "cardinal",
            "Taurus": "fixed", "Leo": "fixed", "Scorpio": "fixed", "Aquarius": "fixed",
            "Gemini": "mutable", "Virgo": "mutable", "Sagittarius": "mutable", "Pisces": "mutable",
        }
        
        sun_modality = modality_map.get(sun_sign, "unknown")
        moon_modality = modality_map.get(moon_sign, "unknown")
        
        # Generate temperament description
        description = self._describe_temperament(sun_sign, moon_sign, rising_sign, dominant_element, sun_modality, locale=locale)
        
        return models.ChildTemperament(
            sun_sign=sun_sign,
            moon_sign=moon_sign,
            rising_sign=rising_sign,
            dominant_element=dominant_element,
            modality=sun_modality,
            description=description,
            characteristics=self._get_temperament_characteristics(dominant_element, sun_modality),
        )
    
    def _analyze_sensitivity(
        self,
        positions: Dict[str, Dict],
        houses: Dict[str, Any],
        aspects: Dict[str, Any],
        locale: str | None = None,
    ) -> models.ChildSensitivity:
        """Analyze child's sensitivity and stress responses."""
        sensitivity_indicators = []
        stress_triggers = []
        
        # Check Moon aspects (especially Moon-Neptune, Moon-Pluto)
        moon_neptune_key = "Moon-Neptune"
        moon_pluto_key = "Moon-Pluto"
        
        if moon_neptune_key in aspects:
            sensitivity_indicators.append("Moon-Neptune aspect indicates high emotional sensitivity")
            stress_triggers.append("Overwhelming environments, emotional intensity")
        
        if moon_pluto_key in aspects:
            sensitivity_indicators.append("Moon-Pluto aspect indicates deep emotional intensity")
            stress_triggers.append("Power dynamics, emotional control issues")
        
        # Check Moon in water signs
        moon_pos = positions.get("Moon", {})
        moon_sign = moon_pos.get("sign", "")
        if moon_sign in ["Cancer", "Scorpio", "Pisces"]:
            sensitivity_indicators.append(f"Moon in {moon_sign} indicates emotional sensitivity")
        
        # Check 4th house (home environment)
        house_4 = houses.get("4") or houses.get("4th")
        if house_4:
            sensitivity_indicators.append("4th house emphasis suggests sensitivity to home environment")
        
        return models.ChildSensitivity(
            level="high" if len(sensitivity_indicators) >= 2 else "medium" if sensitivity_indicators else "low",
            indicators=sensitivity_indicators,
            stress_triggers=stress_triggers,
            support_strategies=self._generate_sensitivity_support(sensitivity_indicators, locale=locale),
        )
    
    def _analyze_boundaries_discipline(
        self,
        positions: Dict[str, Dict],
        houses: Dict[str, Any],
        aspects: Dict[str, Any],
        locale: str | None = None,
    ) -> models.ChildBoundaries:
        """Analyze child's relationship with boundaries and discipline."""
        saturn_pos = positions.get("Saturn", {})
        saturn_sign = saturn_pos.get("sign", "")
        saturn_house = saturn_pos.get("house")
        
        # Check Saturn aspects
        saturn_aspects = [k for k in aspects.keys() if "Saturn" in k]
        
        boundary_style = "structured"
        discipline_approach = "clear rules"
        
        if len(saturn_aspects) == 0:
            boundary_style = "flexible"
            discipline_approach = "gentle guidance"
        elif any("square" in k or "opposition" in k for k in saturn_aspects):
            boundary_style = "resistant"
            discipline_approach = "patient, consistent boundaries"
        
        return models.ChildBoundaries(
            boundary_style=boundary_style,
            discipline_approach=discipline_approach,
            saturn_sign=saturn_sign,
            saturn_house=saturn_house,
            recommendations=self._generate_boundary_recommendations(boundary_style, discipline_approach, locale=locale),
        )
    
    def _analyze_learning_interests(
        self,
        positions: Dict[str, Dict],
        houses: Dict[str, Any],
        aspects: Dict[str, Any],
        locale: str | None = None,
    ) -> models.ChildLearning:
        """Analyze child's learning style and interests."""
        mercury_pos = positions.get("Mercury", {})
        jupiter_pos = positions.get("Jupiter", {})
        
        mercury_sign = mercury_pos.get("sign", "")
        jupiter_sign = jupiter_pos.get("sign", "")
        
        # Determine learning style from Mercury
        learning_style = self._determine_learning_style(mercury_sign)
        
        # Determine interests from Jupiter
        interests = self._determine_interests(jupiter_sign, jupiter_pos.get("house"))
        
        # Check Mercury-Jupiter aspects
        mercury_jupiter_key = "Mercury-Jupiter"
        if mercury_jupiter_key in aspects:
            learning_style += " with expansive curiosity"
        
        return models.ChildLearning(
            learning_style=learning_style,
            interests=interests,
            mercury_sign=mercury_sign,
            jupiter_sign=jupiter_sign,
            recommendations=self._generate_learning_recommendations(learning_style, interests, locale=locale),
        )
    
    def _generate_parental_strategies(
        self,
        temperament: models.ChildTemperament,
        sensitivity: models.ChildSensitivity,
        boundaries: models.ChildBoundaries,
        learning: models.ChildLearning,
        child_age: Optional[int],
        locale: str | None = None,
    ) -> List[str]:
        """Generate specific parental support strategies."""
        strategies = []
        
        # Age-appropriate strategies
        if child_age and child_age < 5:
            strategies.append("Focus on emotional regulation and sensory support")
        elif child_age and child_age < 12:
            strategies.append("Support learning through play and exploration")
        else:
            strategies.append("Respect growing independence while maintaining structure")
        
        # Based on temperament
        if temperament.dominant_element == "fire":
            strategies.append("Provide outlets for physical energy and leadership")
        elif temperament.dominant_element == "water":
            strategies.append("Create safe emotional space and validate feelings")
        
        # Based on sensitivity
        if sensitivity.level == "high":
            strategies.append("Create calm, predictable environments")
            strategies.append("Limit overstimulation and provide quiet spaces")
        
        # Based on boundaries
        if boundaries.boundary_style == "resistant":
            strategies.append("Use consistent, patient boundary-setting")
            strategies.append("Explain reasons for rules, not just enforce them")
        
        # Based on learning
        strategies.append(f"Support learning through {learning.learning_style} approaches")
        
        return strategies
    
    # Helper methods
    def _describe_temperament(
        self, sun: str, moon: str, rising: str, element: str, modality: str, locale: str | None = None
    ) -> str:
        """Generate temperament description."""
        return f"Child with {sun} Sun, {moon} Moon, and {rising} Rising. Dominant element: {element}, modality: {modality}."
    
    def _get_temperament_characteristics(self, element: str, modality: str) -> List[str]:
        """Get characteristics based on element and modality."""
        characteristics = []
        if element == "fire":
            characteristics.extend(["Energetic", "Assertive", "Enthusiastic"])
        elif element == "earth":
            characteristics.extend(["Practical", "Stable", "Grounded"])
        elif element == "air":
            characteristics.extend(["Curious", "Communicative", "Social"])
        elif element == "water":
            characteristics.extend(["Emotional", "Intuitive", "Sensitive"])
        
        if modality == "cardinal":
            characteristics.append("Initiative-taking")
        elif modality == "fixed":
            characteristics.append("Persistent")
        elif modality == "mutable":
            characteristics.append("Adaptable")
        
        return characteristics
    
    def _determine_learning_style(self, mercury_sign: str) -> str:
        """Determine learning style from Mercury sign."""
        style_map = {
            "Aries": "hands-on, active",
            "Taurus": "practical, tactile",
            "Gemini": "verbal, interactive",
            "Cancer": "emotional, story-based",
            "Leo": "creative, expressive",
            "Virgo": "detailed, analytical",
            "Libra": "collaborative, visual",
            "Scorpio": "deep, investigative",
            "Sagittarius": "exploratory, big-picture",
            "Capricorn": "structured, goal-oriented",
            "Aquarius": "innovative, independent",
            "Pisces": "intuitive, imaginative",
        }
        return style_map.get(mercury_sign, "varied")
    
    def _determine_interests(self, jupiter_sign: str, jupiter_house: Optional[int]) -> List[str]:
        """Determine interests from Jupiter."""
        interests = []
        if jupiter_sign in ["Sagittarius", "Jupiter"]:
            interests.append("Travel and exploration")
        if jupiter_house == 9:
            interests.append("Higher learning and philosophy")
        if jupiter_house == 5:
            interests.append("Creative expression and play")
        return interests if interests else ["General curiosity and growth"]
    
    def _generate_sensitivity_support(self, indicators: List[str], locale: str | None = None) -> List[str]:
        """Generate support strategies for sensitivity."""
        strategies = []
        if indicators:
            strategies.append("Create calm, predictable routines")
            strategies.append("Provide quiet spaces for retreat")
            strategies.append("Validate emotional experiences")
        return strategies
    
    def _generate_boundary_recommendations(
        self, boundary_style: str, discipline_approach: str, locale: str | None = None
    ) -> List[str]:
        """Generate boundary recommendations."""
        recommendations = []
        if boundary_style == "resistant":
            recommendations.append("Use consistent, patient boundary-setting")
            recommendations.append("Explain reasons, not just rules")
        else:
            recommendations.append(f"Use {discipline_approach} approach")
        return recommendations
    
    def _generate_learning_recommendations(
        self, learning_style: str, interests: List[str], locale: str | None = None
    ) -> List[str]:
        """Generate learning recommendations."""
        recommendations = []
        recommendations.append(f"Support {learning_style} learning")
        if interests:
            recommendations.append(f"Encourage exploration of: {', '.join(interests)}")
        return recommendations


async def get_children_charts_service() -> ChildrenChartsService:
    """Dependency function for ChildrenChartsService."""
    return ChildrenChartsService()

