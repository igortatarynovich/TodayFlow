"""Group compatibility service for analyzing 3+ people."""

from __future__ import annotations

from typing import Dict, List, Any, Optional
from datetime import date
from collections import Counter

from todayflow_backend.core import models
from todayflow_backend.services import astro
from todayflow_backend.services.synastry import SynastryService
from todayflow_backend.services.psych_compatibility import (
    PsychCompatibilityService,
    build_psych_inputs_from_natal_charts,
)
from todayflow_backend.services.aspects import AspectEngine


class GroupCompatibilityService:
    """Service for analyzing compatibility in groups of 3+ people."""
    
    def __init__(
        self,
        synastry_service: SynastryService | None = None,
        psych_compatibility_service: PsychCompatibilityService | None = None,
        aspect_engine: AspectEngine | None = None,
    ):
        self.synastry_service = synastry_service or SynastryService()
        self.psych_compatibility_service = psych_compatibility_service or PsychCompatibilityService()
        self.aspect_engine = aspect_engine or AspectEngine()
    
    async def analyze_group(
        self,
        charts: List[astro.ChartResponse],
        profile_labels: List[str] | None = None,
        locale: str | None = None,
    ) -> models.GroupCompatibilityReport:
        """
        Analyze compatibility for a group of 3+ people.
        
        Args:
            charts: List of chart responses for each person in the group
            profile_labels: Optional labels/names for each person
            locale: Locale for translations
        
        Returns:
            GroupCompatibilityReport with group dynamics, roles, and tension zones
        """
        if len(charts) < 3:
            raise ValueError("Group compatibility requires at least 3 people")
        
        if profile_labels is None:
            profile_labels = [f"Person {i+1}" for i in range(len(charts))]
        
        # 1. Analyze all pairwise synastry relationships
        pairwise_synastry = await self._analyze_pairwise_synastry(charts, profile_labels, locale)
        
        # 2. Identify group roles
        group_roles = self._identify_group_roles(charts, profile_labels)
        
        # 3. Identify tension zones
        tension_zones = self._identify_tension_zones(charts, profile_labels, pairwise_synastry)
        
        # 4. Analyze group dynamics
        group_dynamics = self._analyze_group_dynamics(charts, profile_labels, pairwise_synastry)
        
        # 5. Generate recommendations
        recommendations = self._generate_group_recommendations(
            group_roles, tension_zones, group_dynamics
        )
        
        return models.GroupCompatibilityReport(
            group_size=len(charts),
            profile_labels=profile_labels,
            pairwise_synastry=pairwise_synastry,
            group_roles=group_roles,
            tension_zones=tension_zones,
            group_dynamics=group_dynamics,
            recommendations=recommendations,
        )
    
    async def _analyze_pairwise_synastry(
        self,
        charts: List[astro.ChartResponse],
        labels: List[str],
        locale: str | None = None,
    ) -> List[models.GroupPairwiseSynastry]:
        """Analyze synastry for all pairs in the group."""
        pairwise_results = []
        
        for i in range(len(charts)):
            for j in range(i + 1, len(charts)):
                chart1 = charts[i]
                chart2 = charts[j]
                label1 = labels[i]
                label2 = labels[j]
                
                # Calculate synastry
                synastry = await self.synastry_service.calculate_synastry(
                    chart1, chart2, locale=locale
                )

                im1, im2, snap1, snap2 = build_psych_inputs_from_natal_charts(chart1, chart2)
                psych_compat = await self.psych_compatibility_service.analyze_compatibility(
                    chart1,
                    chart2,
                    im1,
                    im2,
                    snap1,
                    snap2,
                    locale=locale,
                )

                # Determine overall compatibility score
                compatibility_score = self._calculate_compatibility_score(synastry, psych_compat)

                pairwise_results.append(
                    models.GroupPairwiseSynastry(
                        person_1=label1,
                        person_2=label2,
                        compatibility_score=compatibility_score,
                        synastry_summary=synastry.compatibility_summary,
                        psych_compatibility=psych_compat,
                    )
                )
        
        return pairwise_results
    
    def _calculate_compatibility_score(
        self,
        synastry: models.SynastryReport,
        psych_compat: models.PsychCompatibilityReport,
    ) -> float:
        """Calculate overall compatibility score (0-100)."""
        score = 50.0  # Base score
        
        # Factor in synastry aspects
        strong_aspects = synastry.strong_aspects or []

        def _asp_kind(a: models.SynastryAspect) -> str:
            return str(getattr(a, "aspect", "") or "").strip().lower()

        positive_aspects = [a for a in strong_aspects if _asp_kind(a) in ("conjunction", "trine", "sextile")]
        challenging_aspects = [a for a in strong_aspects if _asp_kind(a) in ("square", "opposition")]

        score += len(positive_aspects) * 3
        score -= len(challenging_aspects) * 2

        # Factor in compatibility summary
        summary = synastry.compatibility_summary
        if summary:
            if summary.strengths:
                score += len(summary.strengths) * 2
            if summary.triggers:
                score -= len(summary.triggers) * 1.5

        # Factor in psychological compatibility
        if psych_compat and psych_compat.communication_recommendations:
            score += len(psych_compat.communication_recommendations) * 1
        
        # Clamp score between 0 and 100
        return max(0.0, min(100.0, score))
    
    def _identify_group_roles(
        self,
        charts: List[astro.ChartResponse],
        labels: List[str],
    ) -> List[models.GroupRole]:
        """Identify roles each person plays in the group."""
        roles = []
        
        # Analyze each person's chart for role indicators
        for i, chart in enumerate(charts):
            positions = {p["body"]: p for p in chart.positions if "body" in p}
            houses = chart.houses or {}
            
            role_indicators = []
            role_type = None
            
            # Check for leadership indicators (Sun, Mars, 1st house, 10th house)
            sun_pos = positions.get("Sun")
            mars_pos = positions.get("Mars")
            planets_in_1st = [p["body"] for p in chart.positions if p.get("house") == 1]
            planets_in_10th = [p["body"] for p in chart.positions if p.get("house") == 10]
            
            if sun_pos and sun_pos.get("house") in [1, 10]:
                role_indicators.append("Strong identity and public presence")
                role_type = "Leader"
            elif mars_pos and mars_pos.get("house") in [1, 10]:
                role_indicators.append("Initiative and drive")
                role_type = "Leader"
            elif len(planets_in_10th) >= 2:
                role_indicators.append("Career and authority focus")
                role_type = "Leader"
            
            # Check for support/mediator indicators (Moon, Venus, 7th house)
            moon_pos = positions.get("Moon")
            venus_pos = positions.get("Venus")
            planets_in_7th = [p["body"] for p in chart.positions if p.get("house") == 7]
            
            if not role_type and (venus_pos and venus_pos.get("house") == 7):
                role_indicators.append("Strong relationship focus")
                role_type = "Mediator"
            elif not role_type and len(planets_in_7th) >= 2:
                role_indicators.append("Partnership and harmony focus")
                role_type = "Mediator"
            
            # Check for analytical/strategic indicators (Mercury, Saturn, 3rd/9th houses)
            mercury_pos = positions.get("Mercury")
            saturn_pos = positions.get("Saturn")
            planets_in_3rd = [p["body"] for p in chart.positions if p.get("house") == 3]
            planets_in_9th = [p["body"] for p in chart.positions if p.get("house") == 9]
            
            if not role_type and (mercury_pos and mercury_pos.get("house") in [3, 9]):
                role_indicators.append("Communication and analysis")
                role_type = "Analyst"
            elif not role_type and (saturn_pos and saturn_pos.get("house") in [3, 9]):
                role_indicators.append("Structure and planning")
                role_type = "Strategist"
            
            # Check for creative/innovative indicators (Venus, 5th house, Uranus)
            uranus_pos = positions.get("Uranus")
            planets_in_5th = [p["body"] for p in chart.positions if p.get("house") == 5]
            
            if not role_type and len(planets_in_5th) >= 2:
                role_indicators.append("Creativity and innovation")
                role_type = "Innovator"
            elif not role_type and uranus_pos and uranus_pos.get("house") == 5:
                role_indicators.append("Unconventional thinking")
                role_type = "Innovator"
            
            # Default role
            if not role_type:
                role_type = "Contributor"
                role_indicators.append("Brings unique perspective to the group")
            
            roles.append(models.GroupRole(
                person_label=labels[i],
                role_type=role_type,
                description=f"Takes on {role_type.lower()} role in group dynamics",
                indicators=role_indicators,
            ))
        
        return roles
    
    def _identify_tension_zones(
        self,
        charts: List[astro.ChartResponse],
        labels: List[str],
        pairwise_synastry: List[models.GroupPairwiseSynastry],
    ) -> List[models.GroupTensionZone]:
        """Identify areas of tension in the group."""
        tension_zones = []
        
        # Find pairs with low compatibility scores
        challenging_pairs = [
            pair for pair in pairwise_synastry 
            if pair.compatibility_score < 40
        ]
        
        for pair in challenging_pairs:
            # Identify specific conflict areas
            conflict_areas = []
            
            if pair.synastry_summary and pair.synastry_summary.triggers:
                conflict_areas.extend(pair.synastry_summary.triggers)

            if pair.psych_compatibility and pair.psych_compatibility.conflict_styles:
                cs = pair.psych_compatibility.conflict_styles
                if cs.description:
                    conflict_areas.append(
                        f"Conflict styles ({cs.person1_style} / {cs.person2_style}): {cs.description[:200]}"
                    )
            
            tension_zones.append(models.GroupTensionZone(
                involved_people=[pair.person_1, pair.person_2],
                description=f"Tension between {pair.person_1} and {pair.person_2}",
                conflict_areas=conflict_areas[:5],  # Limit to 5 areas
                severity="high" if pair.compatibility_score < 30 else "medium",
            ))
        
        # Identify group-wide tension patterns
        # Check for common challenging aspects across multiple pairs
        all_challenging_aspects = []
        for pair in pairwise_synastry:
            if pair.synastry_summary and pair.synastry_summary.triggers:
                all_challenging_aspects.extend(pair.synastry_summary.triggers)
        
        # Find patterns that appear in multiple pairs
        aspect_counts = Counter(all_challenging_aspects)
        common_challenges = [aspect for aspect, count in aspect_counts.items() if count >= 2]
        
        if common_challenges:
            tension_zones.append(models.GroupTensionZone(
                involved_people=labels.copy(),
                description="Group-wide tension patterns",
                conflict_areas=common_challenges[:5],
                severity="medium",
            ))
        
        return tension_zones
    
    def _analyze_group_dynamics(
        self,
        charts: List[astro.ChartResponse],
        labels: List[str],
        pairwise_synastry: List[models.GroupPairwiseSynastry],
    ) -> models.GroupDynamics:
        """Analyze overall group dynamics and patterns."""
        # Calculate average compatibility
        avg_compatibility = sum(pair.compatibility_score for pair in pairwise_synastry) / len(pairwise_synastry) if pairwise_synastry else 50.0
        
        # Analyze element distribution
        elements = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
        for chart in charts:
            sun_pos = next((p for p in chart.positions if p.get("body") == "Sun"), None)
            if sun_pos:
                sun_sign = sun_pos.get("sign", "")
                # Map signs to elements (simplified)
                if sun_sign in ["Aries", "Leo", "Sagittarius"]:
                    elements["Fire"] += 1
                elif sun_sign in ["Taurus", "Virgo", "Capricorn"]:
                    elements["Earth"] += 1
                elif sun_sign in ["Gemini", "Libra", "Aquarius"]:
                    elements["Air"] += 1
                elif sun_sign in ["Cancer", "Scorpio", "Pisces"]:
                    elements["Water"] += 1
        
        # Determine group balance
        dominant_elements = [elem for elem, count in elements.items() if count >= 2]
        balanced = len(dominant_elements) == 0  # No single element dominates
        
        # Identify strong connections (high compatibility pairs)
        strong_connections = [
            [pair.person_1, pair.person_2] 
            for pair in pairwise_synastry 
            if pair.compatibility_score >= 70
        ]
        
        # Group strengths
        strengths = []
        if avg_compatibility >= 60:
            strengths.append("Overall good compatibility across the group")
        if balanced:
            strengths.append("Balanced elemental distribution")
        if len(strong_connections) >= len(charts) - 1:
            strengths.append("Strong connections between most members")
        
        # Group challenges
        challenges = []
        if avg_compatibility < 45:
            challenges.append("Overall compatibility needs attention")
        if len(dominant_elements) > 0:
            challenges.append(f"Elemental imbalance: {', '.join(dominant_elements)} dominant")
        low_compat_pairs = [pair for pair in pairwise_synastry if pair.compatibility_score < 40]
        if len(low_compat_pairs) > len(pairwise_synastry) / 2:
            challenges.append("Multiple challenging relationships in the group")
        
        return models.GroupDynamics(
            average_compatibility=avg_compatibility,
            element_distribution=elements,
            balanced=balanced,
            strong_connections=strong_connections,
            strengths=strengths,
            challenges=challenges,
        )
    
    def _generate_group_recommendations(
        self,
        roles: List[models.GroupRole],
        tension_zones: List[models.GroupTensionZone],
        dynamics: models.GroupDynamics,
    ) -> List[str]:
        """Generate practical recommendations for the group."""
        recommendations = []
        
        # Role-based recommendations
        role_types = [role.role_type for role in roles]
        if "Leader" in role_types:
            leaders = [role.person_label for role in roles if role.role_type == "Leader"]
            if len(leaders) > 1:
                recommendations.append(f"Multiple leaders identified ({', '.join(leaders)}): ensure clear leadership structure and shared decision-making")
        
        if "Mediator" in role_types:
            mediators = [role.person_label for role in roles if role.role_type == "Mediator"]
            recommendations.append(f"Use {mediators[0]} as mediator in conflicts" if mediators else "")
        
        # Tension zone recommendations
        high_tension = [zone for zone in tension_zones if zone.severity == "high"]
        if high_tension:
            for zone in high_tension:
                recommendations.append(f"Address tension between {', '.join(zone.involved_people[:2])}: focus on clear communication and boundaries")
        
        # Dynamics-based recommendations
        if dynamics.average_compatibility < 50:
            recommendations.append("Consider team-building activities to strengthen group bonds")
        
        if not dynamics.balanced:
            dominant = [elem for elem, count in dynamics.element_distribution.items() if count >= 2]
            recommendations.append(f"Group may benefit from perspectives of underrepresented elements (current: {', '.join(dominant)} dominant)")
        
        # General recommendations
        if len(dynamics.strong_connections) >= 2:
            recommendations.append("Leverage strong pair connections to facilitate group cohesion")
        
        recommendations.append("Establish clear group norms and communication guidelines")
        recommendations.append("Regular check-ins can help address issues before they escalate")
        
        return [r for r in recommendations if r]  # Remove empty strings


async def get_group_compatibility_service() -> GroupCompatibilityService:
    """Dependency function for GroupCompatibilityService."""
    return GroupCompatibilityService()

