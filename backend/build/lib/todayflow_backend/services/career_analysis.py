"""Career analysis service: roles, strategies, and career guidance."""

from __future__ import annotations

from typing import Dict, List, Any, Optional
from datetime import date
from todayflow_backend.core import models
from todayflow_backend.services import astro
from todayflow_backend.services.aspects import AspectEngine


class CareerAnalysisService:
    """Service for analyzing career patterns, roles, and strategies."""
    
    def __init__(self, aspect_engine: AspectEngine | None = None):
        self.aspect_engine = aspect_engine or AspectEngine()
    
    async def analyze_career(
        self,
        chart: astro.ChartResponse,
        internal_model: models.InternalModelSnapshot,
        snapshot: models.ChartSnapshot,
        locale: str | None = None,
    ) -> models.CareerAnalysis:
        """
        Analyze career patterns, roles, and strategies.
        
        Returns:
        - Work style (6 house, Mars)
        - Motivation and meaning (Sun/MC)
        - Money patterns (2 house, Venus)
        - Burnout risks (Saturn/Neptune, 12 house)
        - Strong roles (leader/analyst/creator/communicator)
        - Strategic recommendations (year/quarter/month)
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
        
        # Analyze career areas
        work_style = self._analyze_work_style(positions, houses, aspects_by_pair, locale=locale)
        motivation = self._analyze_motivation(positions, houses, snapshot, locale=locale)
        money_patterns = self._analyze_money_patterns(positions, houses, aspects_by_pair, locale=locale)
        burnout_risks = self._analyze_burnout_risks(positions, houses, aspects_by_pair, locale=locale)
        strong_roles = self._identify_strong_roles(positions, houses, aspects_by_pair, locale=locale)
        strategies = self._generate_career_strategies(
            work_style, motivation, money_patterns, burnout_risks, strong_roles, locale=locale
        )
        
        return models.CareerAnalysis(
            work_style=work_style,
            motivation=motivation,
            money_patterns=money_patterns,
            burnout_risks=burnout_risks,
            strong_roles=strong_roles,
            strategies=strategies,
        )
    
    def _analyze_work_style(
        self,
        positions: Dict[str, Dict],
        houses: Dict[str, Any],
        aspects: Dict[str, Any],
        locale: str | None = None,
    ) -> models.WorkStyle:
        """Analyze work style from 6th house and Mars."""
        mars_pos = positions.get("Mars", {})
        mars_sign = mars_pos.get("sign", "")
        mars_house = mars_pos.get("house")
        
        # Check 6th house
        house_6 = houses.get("6") or houses.get("6th")
        planets_in_6th = [body for body, pos in positions.items() if pos.get("house") == 6]
        
        # Determine work style
        if mars_sign in ["Aries", "Leo", "Sagittarius"]:
            work_approach = "dynamic, action-oriented"
        elif mars_sign in ["Taurus", "Virgo", "Capricorn"]:
            work_approach = "methodical, detail-focused"
        elif mars_sign in ["Gemini", "Libra", "Aquarius"]:
            work_approach = "collaborative, communication-focused"
        else:
            work_approach = "intuitive, process-oriented"
        
        return models.WorkStyle(
            approach=work_approach,
            mars_sign=mars_sign,
            mars_house=mars_house,
            planets_in_6th=planets_in_6th,
            description=self._describe_work_style(work_approach, mars_sign, planets_in_6th),
        )
    
    def _analyze_motivation(
        self,
        positions: Dict[str, Dict],
        houses: Dict[str, Any],
        snapshot: models.ChartSnapshot,
        locale: str | None = None,
    ) -> models.CareerMotivation:
        """Analyze motivation and meaning from Sun/MC."""
        sun_pos = positions.get("Sun", {})
        sun_sign = snapshot.sun
        sun_house = sun_pos.get("house")
        
        # MC (Midheaven) - 10th house
        mc_house = houses.get("10") or houses.get("MC") or houses.get("Midheaven")
        planets_in_10th = [body for body, pos in positions.items() if pos.get("house") == 10]
        
        # Determine motivation
        if sun_house == 10:
            motivation = "Public recognition and career achievement"
        elif sun_sign in ["Leo", "Aries", "Sagittarius"]:
            motivation = "Creative expression and leadership"
        elif sun_sign in ["Capricorn", "Virgo", "Taurus"]:
            motivation = "Stability, mastery, and tangible results"
        else:
            motivation = "Meaningful contribution and service"
        
        return models.CareerMotivation(
            motivation=motivation,
            sun_sign=sun_sign,
            sun_house=sun_house,
            mc_house=mc_house,
            planets_in_10th=planets_in_10th,
            purpose_statement=self._generate_purpose_statement(sun_sign, sun_house, planets_in_10th),
        )
    
    def _analyze_money_patterns(
        self,
        positions: Dict[str, Dict],
        houses: Dict[str, Any],
        aspects: Dict[str, Any],
        locale: str | None = None,
    ) -> models.MoneyPatterns:
        """Analyze money patterns from 2nd house and Venus."""
        venus_pos = positions.get("Venus", {})
        venus_sign = venus_pos.get("sign", "")
        venus_house = venus_pos.get("house")
        
        # 2nd house (money/resources)
        house_2 = houses.get("2") or houses.get("2nd")
        planets_in_2nd = [body for body, pos in positions.items() if pos.get("house") == 2]
        
        # Determine money attitude
        if venus_sign in ["Taurus", "Capricorn"]:
            money_attitude = "practical, security-focused"
        elif venus_sign in ["Gemini", "Aquarius"]:
            money_attitude = "flexible, value-based"
        elif venus_sign in ["Scorpio", "Pluto"]:
            money_attitude = "transformative, investment-focused"
        else:
            money_attitude = "balanced, relationship to value"
        
        return models.MoneyPatterns(
            attitude=money_attitude,
            venus_sign=venus_sign,
            venus_house=venus_house,
            planets_in_2nd=planets_in_2nd,
            recommendations=self._generate_money_recommendations(money_attitude, planets_in_2nd),
        )
    
    def _analyze_burnout_risks(
        self,
        positions: Dict[str, Dict],
        houses: Dict[str, Any],
        aspects: Dict[str, Any],
        locale: str | None = None,
    ) -> models.BurnoutRisks:
        """Analyze burnout risks from Saturn/Neptune and 12th house."""
        saturn_pos = positions.get("Saturn", {})
        neptune_pos = positions.get("Neptune", {})
        
        # 12th house (hidden, burnout)
        house_12 = houses.get("12") or houses.get("12th")
        planets_in_12th = [body for body, pos in positions.items() if pos.get("house") == 12]
        
        # Check Saturn-Neptune aspects
        saturn_neptune_key = "Saturn-Neptune"
        has_saturn_neptune = saturn_neptune_key in aspects
        
        # Assess risk level
        risk_factors = []
        if planets_in_12th:
            risk_factors.append("12th house emphasis suggests need for rest and boundaries")
        if has_saturn_neptune:
            risk_factors.append("Saturn-Neptune aspects indicate potential for overwork and disillusionment")
        if saturn_pos.get("house") == 6:
            risk_factors.append("Saturn in 6th house suggests perfectionism in work")
        
        risk_level = "high" if len(risk_factors) >= 2 else "medium" if risk_factors else "low"
        
        return models.BurnoutRisks(
            risk_level=risk_level,
            risk_factors=risk_factors,
            planets_in_12th=planets_in_12th,
            prevention_strategies=self._generate_burnout_prevention(risk_level, risk_factors),
        )
    
    def _identify_strong_roles(
        self,
        positions: Dict[str, Dict],
        houses: Dict[str, Any],
        aspects: Dict[str, Any],
        locale: str | None = None,
    ) -> List[models.CareerRole]:
        """Identify strong career roles (leader/analyst/creator/communicator)."""
        roles = []
        
        # Leader role (Sun/Leo, Mars, 10th house emphasis)
        sun_pos = positions.get("Sun", {})
        mars_pos = positions.get("Mars", {})
        if (sun_pos.get("sign") == "Leo" or sun_pos.get("house") == 10 or
            mars_pos.get("sign") in ["Aries", "Leo"]):
            roles.append(models.CareerRole(
                role="leader",
                strength="high",
                description="Natural leadership and initiative-taking",
                examples=["Executive", "Entrepreneur", "Team Lead"],
            ))
        
        # Analyst role (Mercury, Virgo, 6th house)
        mercury_pos = positions.get("Mercury", {})
        if (mercury_pos.get("sign") == "Virgo" or mercury_pos.get("house") == 6):
            roles.append(models.CareerRole(
                role="analyst",
                strength="high",
                description="Detail-oriented analysis and problem-solving",
                examples=["Data Analyst", "Researcher", "Quality Assurance"],
            ))
        
        # Creator role (Venus, Neptune, 5th house)
        venus_pos = positions.get("Venus", {})
        neptune_pos = positions.get("Neptune", {})
        if (venus_pos.get("sign") in ["Libra", "Pisces"] or
            neptune_pos.get("house") == 5):
            roles.append(models.CareerRole(
                role="creator",
                strength="high",
                description="Creative expression and artistic vision",
                examples=["Artist", "Designer", "Writer", "Musician"],
            ))
        
        # Communicator role (Mercury, Gemini, 3rd house)
        if (mercury_pos.get("sign") == "Gemini" or mercury_pos.get("house") == 3):
            roles.append(models.CareerRole(
                role="communicator",
                strength="high",
                description="Strong communication and networking skills",
                examples=["Journalist", "Marketing", "Sales", "Public Relations"],
            ))
        
        return roles if roles else [
            models.CareerRole(
                role="versatile",
                strength="medium",
                description="Adaptable across multiple roles",
                examples=["Generalist", "Project Manager"],
            )
        ]
    
    def _generate_career_strategies(
        self,
        work_style: models.WorkStyle,
        motivation: models.CareerMotivation,
        money: models.MoneyPatterns,
        burnout: models.BurnoutRisks,
        roles: List[models.CareerRole],
        locale: str | None = None,
    ) -> models.CareerStrategies:
        """Generate strategic recommendations for year/quarter/month."""
        current_date = date.today()
        
        # Year strategy (long-term)
        year_strategy = self._generate_year_strategy(motivation, roles, locale=locale)
        
        # Quarter strategy (medium-term)
        quarter_strategy = self._generate_quarter_strategy(work_style, money, locale=locale)
        
        # Month strategy (short-term)
        month_strategy = self._generate_month_strategy(burnout, work_style, locale=locale)
        
        return models.CareerStrategies(
            year=year_strategy,
            quarter=quarter_strategy,
            month=month_strategy,
        )
    
    # Helper methods
    def _describe_work_style(self, approach: str, mars_sign: str, planets_in_6th: List[str]) -> str:
        """Generate work style description."""
        desc = f"Work approach: {approach}"
        if planets_in_6th:
            desc += f". Planets in 6th house: {', '.join(planets_in_6th)}"
        return desc
    
    def _generate_purpose_statement(self, sun_sign: str, sun_house: Optional[int], planets_in_10th: List[str]) -> str:
        """Generate career purpose statement."""
        if sun_house == 10:
            return "Your career is central to your identity and purpose"
        elif planets_in_10th:
            return f"Your career purpose involves: {', '.join(planets_in_10th)} themes"
        else:
            return f"Your purpose is expressed through {sun_sign} qualities"
    
    def _generate_money_recommendations(self, attitude: str, planets_in_2nd: List[str]) -> List[str]:
        """Generate money recommendations."""
        recommendations = []
        if "security-focused" in attitude:
            recommendations.append("Build stable income streams")
            recommendations.append("Focus on long-term financial planning")
        elif "value-based" in attitude:
            recommendations.append("Align money with your values")
            recommendations.append("Consider value-based investments")
        return recommendations
    
    def _generate_burnout_prevention(self, risk_level: str, risk_factors: List[str]) -> List[str]:
        """Generate burnout prevention strategies."""
        strategies = []
        if risk_level == "high":
            strategies.append("Set strict boundaries between work and rest")
            strategies.append("Schedule regular breaks and recovery time")
            strategies.append("Practice saying no to overcommitment")
        elif risk_level == "medium":
            strategies.append("Monitor stress levels regularly")
            strategies.append("Maintain work-life balance")
        return strategies
    
    def _generate_year_strategy(self, motivation: models.CareerMotivation, roles: List[models.CareerRole], locale: str | None = None) -> str:
        """Generate year-long strategy."""
        primary_role = roles[0].role if roles else "versatile"
        return f"Focus on {primary_role} strengths. Long-term goal: {motivation.motivation}"
    
    def _generate_quarter_strategy(self, work_style: models.WorkStyle, money: models.MoneyPatterns, locale: str | None = None) -> str:
        """Generate quarter strategy."""
        return f"Apply {work_style.approach} work style. Financial focus: {money.attitude}"
    
    def _generate_month_strategy(self, burnout: models.BurnoutRisks, work_style: models.WorkStyle, locale: str | None = None) -> str:
        """Generate month strategy."""
        if burnout.risk_level == "high":
            return "Prioritize rest and boundaries. Monitor energy levels closely."
        return f"Maintain {work_style.approach} approach while staying balanced."


async def get_career_analysis_service() -> CareerAnalysisService:
    """Dependency function for CareerAnalysisService."""
    return CareerAnalysisService()

