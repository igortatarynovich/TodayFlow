"""Health and Psychosomatic Analysis Service."""

from __future__ import annotations

from typing import Dict, List, Any

from todayflow_backend.core import models
from todayflow_backend.services import astro
from todayflow_backend.services.aspects import AspectEngine


class HealthAnalysisService:
    """Service for analyzing health patterns and psychosomatic connections."""
    
    def __init__(
        self,
        astro_service: astro.AstroService | None = None,
        aspect_engine: AspectEngine | None = None,
    ):
        self.astro_service = astro_service or astro.AstroService()
        self.aspect_engine = aspect_engine or AspectEngine()
    
    async def analyze_health(
        self,
        chart: astro.ChartResponse,
        locale: str | None = None,
    ) -> models.HealthAnalysisReport:
        """
        Analyze health patterns and psychosomatic connections from natal chart.
        
        Analyzes:
        - Vulnerable body systems (6th house, Mars, Ascendant, planets in 6th)
        - Stress style and response patterns
        - Preventive recommendations
        - Psychosomatic connections (emotions -> body)
        - Lifestyle guidance
        """
        positions = {p["body"]: p for p in chart.positions if "body" in p}
        houses = chart.houses or {}
        
        # Get aspects
        aspect_response = self.aspect_engine.callouts(chart.positions, locale=locale)
        
        # Analyze vulnerable systems
        vulnerable_systems = self._analyze_vulnerable_systems(positions, houses, aspect_response, locale)
        
        # Analyze stress style
        stress_style = self._analyze_stress_style(positions, houses, aspect_response, locale)
        
        # Generate preventive recommendations
        preventive_recommendations = self._generate_preventive_recommendations(
            vulnerable_systems, stress_style, positions, houses, locale
        )
        
        # Analyze psychosomatic connections
        psychosomatic_connections = self._analyze_psychosomatic_connections(
            positions, houses, aspect_response, locale
        )
        
        # Generate lifestyle guidance
        lifestyle_guidance = self._generate_lifestyle_guidance(
            positions, houses, stress_style, locale
        )
        
        return models.HealthAnalysisReport(
            vulnerable_systems=vulnerable_systems,
            stress_style=stress_style,
            preventive_recommendations=preventive_recommendations,
            psychosomatic_connections=psychosomatic_connections,
            lifestyle_guidance=lifestyle_guidance,
        )
    
    def _analyze_vulnerable_systems(
        self,
        positions: Dict[str, Dict],
        houses: Dict[str, Any],
        aspect_response: models.AspectResponse,
        locale: str | None = None,
    ) -> List[models.VulnerableSystem]:
        """Analyze vulnerable body systems from chart."""
        systems = []
        
        # Analyze 6th house (health, daily routine, work)
        sixth_house_planets = self._get_planets_in_house(positions, houses, 6)
        
        if sixth_house_planets:
            systems.append(models.VulnerableSystem(
                system="Digestive system and daily routines",
                astrological_indicator=f"Planets in 6th house: {', '.join(sixth_house_planets)}",
                description="6th house emphasizes digestive health, daily routines, and work-related stress.",
                recommendations=[
                    "Maintain regular meal times",
                    "Pay attention to dietary triggers",
                    "Establish consistent daily routines",
                    "Manage work stress proactively",
                ],
            ))
        
        # Analyze Mars (energy, inflammation, physical activity)
        mars = positions.get("Mars", {})
        mars_sign = mars.get("sign", "")
        mars_house = mars.get("house")
        
        if mars_house == 6:
            systems.append(models.VulnerableSystem(
                system="Inflammation and overexertion",
                astrological_indicator="Mars in 6th house",
                description="Mars in 6th house can indicate tendency to push physical limits, leading to inflammation and burnout.",
                recommendations=[
                    "Balance activity with rest",
                    "Pay attention to signs of overexertion",
                    "Support recovery with anti-inflammatory practices",
                ],
            ))
        
        # Analyze Ascendant (physical body, constitution)
        ascendant = positions.get("Ascendant", {})
        asc_sign = ascendant.get("sign", "")
        
        if asc_sign:
            constitution_indicators = self._get_constitution_indicators(asc_sign, positions)
            systems.append(models.VulnerableSystem(
                system="Constitutional strengths and vulnerabilities",
                astrological_indicator=f"Ascendant in {asc_sign}",
                description=f"{asc_sign} rising indicates specific constitutional patterns and potential vulnerability areas.",
                recommendations=constitution_indicators.get("recommendations", []),
            ))
        
        # Analyze Saturn (chronic conditions, structural issues)
        saturn = positions.get("Saturn", {})
        saturn_house = saturn.get("house")
        
        if saturn_house == 6:
            systems.append(models.VulnerableSystem(
                system="Chronic health conditions and structural integrity",
                astrological_indicator="Saturn in 6th house",
                description="Saturn in 6th house can indicate need for structural support and management of chronic conditions.",
                recommendations=[
                    "Focus on long-term health maintenance",
                    "Support bone and joint health",
                    "Establish sustainable health routines",
                    "Address chronic patterns early",
                ],
            ))
        
        # Analyze Neptune (sensitivity, detoxification)
        neptune = positions.get("Neptune", {})
        neptune_house = neptune.get("house")
        
        if neptune_house == 6:
            systems.append(models.VulnerableSystem(
                system="Sensitivity and detoxification",
                astrological_indicator="Neptune in 6th house",
                description="Neptune in 6th house can indicate sensitivity to environmental factors and need for detoxification support.",
                recommendations=[
                    "Minimize exposure to toxins",
                    "Support liver and detoxification pathways",
                    "Pay attention to environmental sensitivities",
                    "Consider gentle cleansing practices",
                ],
            ))
        
        return systems[:5]  # Return top 5
    
    def _analyze_stress_style(
        self,
        positions: Dict[str, Dict],
        houses: Dict[str, Any],
        aspect_response: models.AspectResponse,
        locale: str | None = None,
    ) -> models.StressStyle:
        """Analyze stress manifestation and response patterns."""
        mars = positions.get("Mars", {})
        moon = positions.get("Moon", {})
        saturn = positions.get("Saturn", {})
        
        # Determine stress response pattern
        stress_response = self._determine_stress_response(mars, moon, saturn, aspect_response)
        
        # Identify stress triggers
        stress_triggers = self._identify_stress_triggers(positions, houses, aspect_response)
        
        # Determine stress manifestation
        stress_manifestation = self._determine_stress_manifestation(positions, houses, aspect_response)
        
        # Determine recovery style
        recovery_style = self._determine_recovery_style(positions, houses, aspect_response)
        
        # Generate recommendations
        recommendations = self._generate_stress_recommendations(stress_response, stress_manifestation, recovery_style)
        
        return models.StressStyle(
            stress_manifestation=stress_manifestation,
            stress_triggers=stress_triggers,
            stress_response=stress_response,
            recovery_style=recovery_style,
            recommendations=recommendations,
        )
    
    def _analyze_psychosomatic_connections(
        self,
        positions: Dict[str, Dict],
        houses: Dict[str, Any],
        aspect_response: models.AspectResponse,
        locale: str | None = None,
    ) -> List[models.PsychosomaticConnection]:
        """Analyze connections between emotional patterns and physical symptoms."""
        connections = []
        
        # Moon-Saturn aspects (emotional repression -> physical tension)
        moon_saturn_aspects = [c for c in aspect_response.callouts if "Moon" in c.bodies and "Saturn" in c.bodies]
        if moon_saturn_aspects:
            connections.append(models.PsychosomaticConnection(
                emotional_pattern="Emotional suppression and control",
                physical_manifestation="Tension in neck, shoulders, lower back; digestive issues",
                astrological_connection="Moon-Saturn aspects",
                recommendations=[
                    "Practice emotional expression and release",
                    "Support nervous system relaxation",
                    "Address physical tension through bodywork",
                ],
            ))
        
        # Mars-Pluto aspects (repressed anger -> inflammation)
        mars_pluto_aspects = [c for c in aspect_response.callouts if "Mars" in c.bodies and "Pluto" in c.bodies]
        if mars_pluto_aspects:
            connections.append(models.PsychosomaticConnection(
                emotional_pattern="Repressed anger and power struggles",
                physical_manifestation="Inflammation, autoimmune patterns, chronic pain",
                astrological_connection="Mars-Pluto aspects",
                recommendations=[
                    "Find healthy outlets for anger and frustration",
                    "Support anti-inflammatory practices",
                    "Address power dynamics in relationships",
                ],
            ))
        
        # Moon in 12th house (unconscious emotions -> psychosomatic symptoms)
        moon = positions.get("Moon", {})
        if moon.get("house") == 12:
            connections.append(models.PsychosomaticConnection(
                emotional_pattern="Unconscious emotional patterns and suppressed feelings",
                physical_manifestation="Mysterious or hard-to-diagnose symptoms, immune system issues",
                astrological_connection="Moon in 12th house",
                recommendations=[
                    "Explore unconscious patterns through therapy or self-reflection",
                    "Support immune system health",
                    "Create safe spaces for emotional expression",
                ],
            ))
        
        # Venus-Pluto aspects (relationship stress -> reproductive/endocrine issues)
        venus_pluto_aspects = [c for c in aspect_response.callouts if "Venus" in c.bodies and "Pluto" in c.bodies]
        if venus_pluto_aspects:
            connections.append(models.PsychosomaticConnection(
                emotional_pattern="Intense relationship dynamics and attachment stress",
                physical_manifestation="Reproductive health, endocrine imbalances, skin issues",
                astrological_connection="Venus-Pluto aspects",
                recommendations=[
                    "Address relationship patterns and boundaries",
                    "Support hormonal balance",
                    "Practice self-care and emotional regulation",
                ],
            ))
        
        return connections[:4]  # Return top 4
    
    def _get_planets_in_house(self, positions: Dict[str, Dict], houses: Dict[str, Any], house_num: int) -> List[str]:
        """Get list of planets in a specific house."""
        planets_in_house = []
        house_key = str(house_num)
        
        for body, pos in positions.items():
            if body in ["Ascendant", "MC", "IC", "Descendant"]:
                continue
            if pos.get("house") == house_num:
                planets_in_house.append(body)
        
        return planets_in_house
    
    def _get_constitution_indicators(self, asc_sign: str, positions: Dict[str, Dict]) -> Dict[str, List[str]]:
        """Get constitution indicators based on Ascendant sign."""
        # Simplified - would be more detailed in full implementation
        recommendations = []
        
        fire_signs = ["Aries", "Leo", "Sagittarius"]
        earth_signs = ["Taurus", "Virgo", "Capricorn"]
        air_signs = ["Gemini", "Libra", "Aquarius"]
        water_signs = ["Cancer", "Scorpio", "Pisces"]
        
        if asc_sign in fire_signs:
            recommendations.extend([
                "Support cardiovascular health",
                "Balance high energy with adequate rest",
                "Manage heat and inflammation",
            ])
        elif asc_sign in earth_signs:
            recommendations.extend([
                "Support digestive health",
                "Maintain structural integrity (bones, joints)",
                "Balance stability with flexibility",
            ])
        elif asc_sign in air_signs:
            recommendations.extend([
                "Support nervous system health",
                "Balance mental activity with physical grounding",
                "Manage stress through breathwork",
            ])
        elif asc_sign in water_signs:
            recommendations.extend([
                "Support fluid balance and elimination",
                "Manage emotional sensitivity",
                "Support lymphatic and immune systems",
            ])
        
        return {"recommendations": recommendations}
    
    def _determine_stress_response(
        self,
        mars: Dict,
        moon: Dict,
        saturn: Dict,
        aspect_response: models.AspectResponse,
    ) -> str:
        """Determine stress response pattern (fight/flight/freeze/fawn)."""
        # Strong Mars -> fight response
        if mars and mars.get("house") in [1, 10]:
            return "Fight - Active response to stress, may push through challenges"
        
        # Moon in mutable signs -> flight response
        mutable_signs = ["Gemini", "Virgo", "Sagittarius", "Pisces"]
        if moon and moon.get("sign") in mutable_signs:
            return "Flight - Tendency to avoid or escape stress situations"
        
        # Strong Saturn -> freeze response
        if saturn and saturn.get("house") in [1, 4, 10]:
            return "Freeze - May shut down or become immobilized under stress"
        
        # Default
        return "Mixed - Stress response varies by situation"
    
    def _identify_stress_triggers(
        self,
        positions: Dict[str, Dict],
        houses: Dict[str, Any],
        aspect_response: models.AspectResponse,
    ) -> List[str]:
        """Identify common stress triggers from chart."""
        triggers = []
        
        # Saturn aspects -> pressure and responsibility
        saturn_aspects = [c for c in aspect_response.callouts if "Saturn" in c.bodies]
        if len(saturn_aspects) > 3:
            triggers.append("Pressure and responsibility overload")
        
        # Mars aspects -> conflict and urgency
        mars_aspects = [c for c in aspect_response.callouts if "Mars" in c.bodies]
        if len(mars_aspects) > 3:
            triggers.append("Conflict and time pressure")
        
        # Moon aspects -> emotional overwhelm
        moon_aspects = [c for c in aspect_response.callouts if "Moon" in c.bodies]
        if len(moon_aspects) > 3:
            triggers.append("Emotional overwhelm and sensitivity")
        
        triggers.append("Unpredictable changes")
        triggers.append("Lack of control or autonomy")
        
        return triggers[:5]
    
    def _determine_stress_manifestation(
        self,
        positions: Dict[str, Dict],
        houses: Dict[str, Any],
        aspect_response: models.AspectResponse,
    ) -> str:
        """Determine how stress manifests (physical, emotional, behavioral)."""
        mars = positions.get("Mars", {})
        moon = positions.get("Moon", {})
        
        # Strong Mars -> physical manifestation
        if mars and mars.get("house") in [1, 6]:
            return "Physical - Stress shows up as tension, inflammation, or physical symptoms"
        
        # Strong Moon -> emotional manifestation
        if moon and moon.get("house") in [1, 4]:
            return "Emotional - Stress shows up as mood changes, sensitivity, or emotional overwhelm"
        
        return "Mixed - Stress can manifest both physically and emotionally"
    
    def _determine_recovery_style(
        self,
        positions: Dict[str, Dict],
        houses: Dict[str, Any],
        aspect_response: models.AspectResponse,
    ) -> str:
        """Determine how the person recovers from stress."""
        moon = positions.get("Moon", {})
        venus = positions.get("Venus", {})
        
        # Moon in water signs -> needs emotional processing
        water_signs = ["Cancer", "Scorpio", "Pisces"]
        if moon and moon.get("sign") in water_signs:
            return "Emotional processing and self-care - Needs time to process feelings"
        
        # Venus strong -> needs pleasure and comfort
        if venus and venus.get("house") in [1, 4, 7]:
            return "Pleasure and comfort - Benefits from beauty, connection, and relaxation"
        
        return "Rest and restoration - Needs quiet time and physical rest"
    
    def _generate_stress_recommendations(
        self,
        stress_response: str,
        stress_manifestation: str,
        recovery_style: str,
    ) -> List[str]:
        """Generate recommendations based on stress patterns."""
        recommendations = []
        
        if "Fight" in stress_response:
            recommendations.append("Balance activity with restorative practices")
            recommendations.append("Practice conscious relaxation techniques")
        
        if "Flight" in stress_response:
            recommendations.append("Develop grounding practices")
            recommendations.append("Address stress directly rather than avoiding")
        
        if "Freeze" in stress_response:
            recommendations.append("Support nervous system regulation")
            recommendations.append("Practice gradual activation and movement")
        
        if "Physical" in stress_manifestation:
            recommendations.append("Address physical tension through bodywork and movement")
            recommendations.append("Support anti-inflammatory practices")
        
        if "Emotional" in stress_manifestation:
            recommendations.append("Create safe spaces for emotional expression")
            recommendations.append("Support emotional regulation through therapy or self-reflection")
        
        return recommendations[:5]
    
    def _generate_preventive_recommendations(
        self,
        vulnerable_systems: List[models.VulnerableSystem],
        stress_style: models.StressStyle | None,
        positions: Dict[str, Dict],
        houses: Dict[str, Any],
        locale: str | None = None,
    ) -> List[str]:
        """Generate preventive health recommendations."""
        recommendations = []
        
        # Based on vulnerable systems
        for system in vulnerable_systems[:2]:
            recommendations.extend(system.recommendations[:2])
        
        # Based on stress style
        if stress_style:
            recommendations.extend(stress_style.recommendations[:2])
        
        # General preventive care
        recommendations.extend([
            "Maintain regular health check-ups",
            "Support overall wellness through balanced lifestyle",
            "Pay attention to early warning signs",
            "Create sustainable health routines",
        ])
        
        return list(set(recommendations))[:8]  # Remove duplicates, return top 8
    
    def _generate_lifestyle_guidance(
        self,
        positions: Dict[str, Dict],
        houses: Dict[str, Any],
        stress_style: models.StressStyle | None,
        locale: str | None = None,
    ) -> List[str]:
        """Generate lifestyle guidance based on chart patterns."""
        guidance = []
        
        mars = positions.get("Mars", {})
        moon = positions.get("Moon", {})
        
        # Activity level recommendations
        if mars and mars.get("house") in [1, 5, 9]:
            guidance.append("Regular physical activity is important for energy balance")
        else:
            guidance.append("Moderate, consistent movement supports overall health")
        
        # Sleep and rest recommendations
        if moon and moon.get("house") in [4, 12]:
            guidance.append("Quality sleep and rest are essential for emotional and physical health")
        
        # Stress management
        if stress_style:
            guidance.append(f"Support {stress_style.recovery_style.lower()} for stress recovery")
        
        guidance.append("Balance work and rest cycles")
        guidance.append("Create routines that support both structure and flexibility")
        
        return guidance[:6]

