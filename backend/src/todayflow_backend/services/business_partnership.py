"""Business Partnership Compatibility Service."""

from __future__ import annotations

from typing import Dict, List

from todayflow_backend.core import models
from todayflow_backend.services import astro
from todayflow_backend.services.aspects import AspectEngine
from todayflow_backend.services.composite import CompositeChartService
from todayflow_backend.services.psych_compatibility import (
    PsychCompatibilityService,
    build_psych_inputs_from_natal_charts,
)
from todayflow_backend.services.synastry import SynastryService

_HARD_ASPECT_NAMES = frozenset(
    {"square", "opposition", "quincunx", "semisquare", "sesquiquadrate", "sesquisquare"}
)


class BusinessPartnershipService:
    """Service for analyzing business partnership compatibility."""
    
    def __init__(
        self,
        astro_service: astro.AstroService | None = None,
        aspect_engine: AspectEngine | None = None,
    ):
        self.astro_service = astro_service or astro.AstroService()
        self.aspect_engine = aspect_engine or AspectEngine()
        self.synastry_service = SynastryService(aspect_engine=self.aspect_engine)
        self.composite_service = CompositeChartService(aspect_engine=self.aspect_engine)
        self.psych_service = PsychCompatibilityService(aspect_engine=self.aspect_engine)
    
    async def analyze_business_partnership(
        self,
        chart1: astro.ChartResponse,
        chart2: astro.ChartResponse,
        locale: str | None = None,
    ) -> models.BusinessPartnershipReport:
        """
        Analyze business partnership compatibility between two charts.
        
        Combines:
        - Role compatibility (based on career analysis)
        - Composite chart (how the partnership functions)
        - Synastry (interpersonal dynamics)
        - Psychological compatibility (conflict styles, communication)
        """
        # Note: Career analysis requires internal_model and snapshot
        # For business partnership, we'll use simplified role analysis based on chart positions
        # Full career analysis would require FullReport generation
        roles1 = self._extract_roles_from_chart(chart1)
        roles2 = self._extract_roles_from_chart(chart2)
        
        # 2. Get Composite chart
        composite = await self.composite_service.calculate_composite_chart(
            chart1=chart1,
            chart2=chart2,
            locale=locale,
        )
        
        # 3. Get Synastry
        synastry = await self.synastry_service.calculate_synastry(
            chart1=chart1,
            chart2=chart2,
            locale=locale,
        )
        
        # 4. Get Psychological compatibility
        im1, im2, s1, s2 = build_psych_inputs_from_natal_charts(chart1, chart2)
        psych = await self.psych_service.analyze_compatibility(
            chart1,
            chart2,
            im1,
            im2,
            s1,
            s2,
            locale=locale,
        )
        
        # 5. Analyze role compatibility
        role_compatibility = self._analyze_role_compatibility_simple(roles1, roles2, locale)
        
        # 6. Generate structural recommendations
        structural_recommendations = self._generate_structural_recommendations(
            composite, synastry, psych, roles1, roles2, locale
        )
        
        # 7. Determine decision-making style
        decision_making_style = self._determine_decision_making_style(composite, psych, locale)
        
        # 8. Communication approach
        communication_approach = self._generate_communication_recommendations(psych, locale)
        
        # 9. Division of responsibilities
        division = self._suggest_division_of_responsibilities(roles1, roles2, role_compatibility, locale)
        
        # 10. Growth potential
        growth_potential = self._assess_growth_potential(composite, synastry, psych, locale)
        
        # 11. Risk factors
        risk_factors = self._identify_risk_factors(composite, synastry, psych, locale)
        
        return models.BusinessPartnershipReport(
            role_compatibility=role_compatibility,
            structural_recommendations=structural_recommendations,
            decision_making_style=decision_making_style,
            communication_approach=communication_approach,
            division_of_responsibilities=division,
            growth_potential=growth_potential,
            risk_factors=risk_factors,
        )
    
    def _extract_roles_from_chart(self, chart: astro.ChartResponse) -> List[str]:
        """Extract potential roles from chart positions (simplified)."""
        positions = {p["body"]: p for p in chart.positions if "body" in p}
        roles = []
        
        # Analyze based on planetary positions
        sun = positions.get("Sun", {})
        mars = positions.get("Mars", {})
        mercury = positions.get("Mercury", {})
        venus = positions.get("Venus", {})
        
        # Leader: Strong Sun/Mars
        if sun.get("house") in [1, 10] or mars.get("house") in [1, 10]:
            roles.append("leader")
        
        # Analyst: Strong Mercury/Saturn
        if mercury.get("house") in [6, 9] or positions.get("Saturn", {}).get("house") in [6, 9]:
            roles.append("analyst")
        
        # Creator: Strong Venus/Neptune
        if venus.get("house") in [5, 11] or positions.get("Neptune", {}).get("house") in [5, 11]:
            roles.append("creator")
        
        # Communicator: Strong Mercury/Venus
        if mercury.get("house") in [3, 7] or venus.get("house") in [3, 7]:
            roles.append("communicator")
        
        return roles if roles else ["general"]
    
    def _analyze_role_compatibility_simple(
        self,
        roles1: List[str],
        roles2: List[str],
        locale: str | None = None,
    ) -> List[models.BusinessRoleCompatibility]:
        """Analyze compatibility between career roles (simplified version)."""
        compatibilities = []
        
        # Use provided roles or defaults
        roles1 = roles1[:2] if roles1 else ["general"]
        roles2 = roles2[:2] if roles2 else ["general"]
        
        # Analyze each role combination
        for role1 in roles1:
            for role2 in roles2:
                compatibility = self._calculate_role_compatibility_score(role1, role2)
                strengths = self._get_role_strengths(role1, role2)
                challenges = self._get_role_challenges(role1, role2)
                recommendations = self._get_role_recommendations(role1, role2)
                
                compatibilities.append(models.BusinessRoleCompatibility(
                    person1_role=role1,
                    person2_role=role2,
                    compatibility_score=compatibility,
                    strengths=strengths,
                    challenges=challenges,
                    recommendations=recommendations,
                ))
        
        return compatibilities[:4]  # Return top 4 combinations
    
    def _calculate_role_compatibility_score(self, role1: str, role2: str) -> float:
        """Calculate compatibility score between two roles (0.0 to 1.0)."""
        # Complementary roles score higher
        complementary_pairs = [
            ("leader", "analyst"),
            ("leader", "creator"),
            ("analyst", "communicator"),
            ("creator", "communicator"),
        ]
        
        pair = (role1.lower(), role2.lower())
        if pair in complementary_pairs or pair[::-1] in complementary_pairs:
            return 0.85
        
        # Same roles can work but may have conflict
        if role1.lower() == role2.lower():
            return 0.65
        
        # Other combinations
        return 0.70
    
    def _get_role_strengths(self, role1: str, role2: str) -> List[str]:
        """Get strengths of role combination."""
        role1_lower = role1.lower()
        role2_lower = role2.lower()
        
        if ("leader" in role1_lower and "analyst" in role2_lower) or ("analyst" in role1_lower and "leader" in role2_lower):
            return [
                "Leader sets direction, analyst provides data-driven insights",
                "Strong strategic planning capabilities",
                "Balanced decision-making (vision + analysis)",
            ]
        elif ("leader" in role1_lower and "creator" in role2_lower) or ("creator" in role1_lower and "leader" in role2_lower):
            return [
                "Leader executes, creator innovates",
                "Strong product development potential",
                "Dynamic growth-oriented partnership",
            ]
        elif ("analyst" in role1_lower and "communicator" in role2_lower) or ("communicator" in role1_lower and "analyst" in role2_lower):
            return [
                "Analyst provides insights, communicator translates to stakeholders",
                "Strong client-facing capabilities",
                "Effective information flow",
            ]
        elif ("creator" in role1_lower and "communicator" in role2_lower) or ("communicator" in role1_lower and "creator" in role2_lower):
            return [
                "Creator develops, communicator markets",
                "Strong brand building potential",
                "Effective product-market alignment",
            ]
        else:
            return [
                "Diverse skill sets",
                "Multiple perspectives on challenges",
            ]
    
    def _get_role_challenges(self, role1: str, role2: str) -> List[str]:
        """Get challenges of role combination."""
        if role1.lower() == role2.lower():
            return [
                "Potential overlap in responsibilities",
                "Need clear boundaries",
                "Both may want to lead in same areas",
            ]
        
        return [
            "Different working styles may require adjustment",
            "Communication protocols needed",
        ]
    
    def _get_role_recommendations(self, role1: str, role2: str) -> List[str]:
        """Get recommendations for role combination."""
        return [
            "Define clear areas of responsibility",
            "Establish regular communication checkpoints",
            "Create shared decision-making framework",
            "Respect each other's expertise and style",
        ]
    
    def _generate_structural_recommendations(
        self,
        composite: models.CompositeChart,
        synastry: models.SynastryReport,
        psych: models.PsychCompatibilityReport,
        roles1: List[str],
        roles2: List[str],
        locale: str | None = None,
    ) -> List[str]:
        """Generate recommendations for business structure."""
        recommendations = []
        
        # Based on composite chart aspects
        strong_aspects = [a for a in composite.aspects if a.strength in ["exact", "tight"]]
        if len(strong_aspects) > 5:
            recommendations.append("Strong partnership foundation - consider equal partnership structure")
        
        # Based on conflict styles
        if psych.conflict_styles:
            conflict_style1 = psych.conflict_styles.person1_style if psych.conflict_styles else "collaborative"
            if "avoid" in conflict_style1.lower():
                recommendations.append("Establish formal conflict resolution process")
        
        # Based on roles
        if "leader" in str(roles1).lower() and "leader" in str(roles2).lower():
            recommendations.append("Consider rotating leadership or clear domain separation")
        
        recommendations.append("Define decision-making authority for different areas")
        recommendations.append("Establish regular business review meetings")
        
        return recommendations
    
    def _determine_decision_making_style(
        self,
        composite: models.CompositeChart,
        psych: models.PsychCompatibilityReport,
        locale: str | None = None,
    ) -> str:
        """Determine recommended decision-making style."""
        comm = psych.communication_recommendations
        if comm and len(comm) > 2:
            return "Collaborative decision-making with structured discussion process"
        
        return "Consensus-based decision-making with clear escalation process"
    
    def _generate_communication_recommendations(
        self,
        psych: models.PsychCompatibilityReport,
        locale: str | None = None,
    ) -> List[str]:
        """Generate communication recommendations."""
        recommendations = []
        
        for tech in (psych.communication_recommendations or [])[:3]:
            recommendations.append(tech.technique)
        
        recommendations.append("Schedule regular check-ins (weekly minimum)")
        recommendations.append("Use structured agenda for important discussions")
        recommendations.append("Document major decisions in writing")
        
        return recommendations
    
    def _suggest_division_of_responsibilities(
        self,
        roles1: List[str],
        roles2: List[str],
        role_compatibility: List[models.BusinessRoleCompatibility],
        locale: str | None = None,
    ) -> List[str]:
        """Suggest division of responsibilities."""
        divisions = []
        
        role1 = roles1[0] if roles1 else "general"
        role2 = roles2[0] if roles2 else "general"
        
        if "leader" in role1.lower():
            divisions.append(f"Person 1: Strategic direction and vision")
            if "analyst" in role2.lower():
                divisions.append(f"Person 2: Data analysis and operational efficiency")
            elif "creator" in role2.lower():
                divisions.append(f"Person 2: Product development and innovation")
            elif "communicator" in role2.lower():
                divisions.append(f"Person 2: Client relations and marketing")
        elif "analyst" in role1.lower():
            divisions.append(f"Person 1: Data analysis and operations")
            divisions.append(f"Person 2: Strategic and creative direction")
        else:
            divisions.append(f"Person 1: {role1.title()} responsibilities")
            divisions.append(f"Person 2: {role2.title()} responsibilities")
        
        divisions.append("Shared: Major financial decisions and hiring")
        divisions.append("Shared: Long-term strategy and vision")
        
        return divisions
    
    def _assess_growth_potential(
        self,
        composite: models.CompositeChart,
        synastry: models.SynastryReport,
        psych: models.PsychCompatibilityReport,
        locale: str | None = None,
    ) -> str:
        """Assess growth potential of the partnership."""
        # Count strong aspects
        strong_composite = len([a for a in composite.aspects if a.strength in ["exact", "tight"]])
        strong_synastry = len([a for a in synastry.planet_aspects if a.strength in ["exact", "tight"]])
        
        if strong_composite > 5 and strong_synastry > 8:
            return "High growth potential - strong compatibility and alignment"
        elif strong_composite > 3 and strong_synastry > 5:
            return "Good growth potential - solid foundation with room for development"
        else:
            return "Moderate growth potential - requires focused effort on alignment"
    
    def _identify_risk_factors(
        self,
        composite: models.CompositeChart,
        synastry: models.SynastryReport,
        psych: models.PsychCompatibilityReport,
        locale: str | None = None,
    ) -> List[str]:
        """Identify risk factors for the partnership."""
        risks = []
        
        # Check for challenging aspects (composite model has no tension_level)
        challenging_composite = [
            a
            for a in composite.aspects
            if str(getattr(a, "aspect", "")).lower() in _HARD_ASPECT_NAMES
        ]
        if len(challenging_composite) > 3:
            risks.append("Multiple challenging aspects - requires conscious conflict management")
        
        # Check conflict styles
        if psych.conflict_styles:
            if "avoid" in psych.conflict_styles.person1_style.lower() and "avoid" in psych.conflict_styles.person2_style.lower():
                risks.append("Both partners may avoid conflict - issues could accumulate")
        
        # Check boundaries
        if psych.boundary_themes:
            patterns_text = " ".join(
                psych.boundary_themes.person1_patterns + psych.boundary_themes.person2_patterns
            ).lower()
            if "porous" in patterns_text or psych.boundary_themes.themes.get("independence"):
                risks.append("Blurred boundaries may lead to role confusion")
        
        risks.append("Ensure clear financial agreements and legal structure")
        risks.append("Plan for conflict resolution and exit strategy")
        
        return risks

