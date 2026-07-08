"""Personal transit service: calculating transits to natal chart."""

from __future__ import annotations

from datetime import date, datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple

from todayflow_backend.core import models
from todayflow_backend.services import astro
from todayflow_backend.services.aspects import AspectEngine
from todayflow_backend.services.psychological_layer import PsychologicalLayerService

# Import Human Layer (assuming it's available as a module)
try:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../CONTENT/human_layer"))
    from human_layer import HumanLayer
except ImportError:
    # Fallback if Human Layer not available
    HumanLayer = None


class TransitToNatal:
    """A single transit aspect from a transiting planet to a natal planet."""
    
    def __init__(
        self,
        transiting_planet: str,
        natal_planet: str,
        aspect_id: str,
        degrees_apart: float,
        orb_delta: float,
        strength: str,
        tension_level: str,
    ):
        self.transiting_planet = transiting_planet
        self.natal_planet = natal_planet
        self.aspect_id = aspect_id
        self.degrees_apart = degrees_apart
        self.orb_delta = orb_delta
        self.strength = strength
        self.tension_level = tension_level


class PersonalTransitService:
    """Service for calculating transits to natal chart and generating daily forecast."""
    
    def __init__(
        self,
        astro_service: astro.AstroService | None = None,
        aspect_engine: AspectEngine | None = None,
        psychological_service: PsychologicalLayerService | None = None,
        human_layer: Any | None = None,
    ):
        self.astro_service = astro_service or astro.AstroService()
        self.aspect_engine = aspect_engine or AspectEngine()
        self.psychological_service = psychological_service or PsychologicalLayerService(aspect_engine)
        self.human_layer = human_layer
        if self.human_layer is None and HumanLayer is not None:
            self.human_layer = HumanLayer()
    
    async def get_daily_forecast(
        self,
        natal_chart: astro.ChartResponse,
        forecast_date: date | None = None,
        birth_data: models.BirthData | None = None,
        locale: str | None = None,
    ) -> models.DailyForecast:
        """
        Generate personalized daily forecast based on transits to natal chart.
        
        Returns a forecast with:
        - Active transits (what's activating now)
        - Psychological interpretation
        - Tensions and resources
        - Conscious actions
        """
        if forecast_date is None:
            forecast_date = date.today()
        
        # Calculate transiting planets positions for the forecast date
        transits = await self._calculate_transits(natal_chart, forecast_date, birth_data=birth_data)
        
        return await self._build_forecast(transits, natal_chart, forecast_date, locale)
    
    async def get_weekly_forecast(
        self,
        natal_chart: astro.ChartResponse,
        start_date: date | None = None,
        birth_data: models.BirthData | None = None,
        locale: str | None = None,
    ) -> List[models.DailyForecast]:
        """
        Generate weekly forecast (7 days) based on transits to natal chart.
        
        Returns a list of daily forecasts for the week.
        """
        if start_date is None:
            start_date = date.today()
        
        forecasts = []
        for day_offset in range(7):
            forecast_date = start_date + timedelta(days=day_offset)
            transits = await self._calculate_transits(natal_chart, forecast_date, birth_data=birth_data)
            forecast = await self._build_forecast(transits, natal_chart, forecast_date, locale)
            forecasts.append(forecast)
        
        return forecasts
    
    async def get_monthly_forecast(
        self,
        natal_chart: astro.ChartResponse,
        start_date: date | None = None,
        birth_data: models.BirthData | None = None,
        locale: str | None = None,
    ) -> List[models.DailyForecast]:
        """
        Generate monthly forecast (30 days) based on transits to natal chart.
        
        Returns a list of daily forecasts for the month.
        """
        if start_date is None:
            start_date = date.today()
        
        forecasts = []
        for day_offset in range(30):
            forecast_date = start_date + timedelta(days=day_offset)
            transits = await self._calculate_transits(natal_chart, forecast_date, birth_data=birth_data)
            forecast = await self._build_forecast(transits, natal_chart, forecast_date, locale)
            forecasts.append(forecast)
        
        return forecasts
    
    async def get_forecast_with_periods(
        self,
        natal_chart: astro.ChartResponse,
        start_date: date | None = None,
        days: int = 30,
        birth_data: models.BirthData | None = None,
        locale: str | None = None,
    ) -> models.ForecastPeriods:
        """
        Generate forecast with identified periods and peaks.
        
        Analyzes transit intensity over time to identify:
        - Peak periods (high intensity)
        - Low periods (calm)
        - Intensity trends
        """
        if start_date is None:
            start_date = date.today()
        
        # Generate forecasts for the period
        forecasts = []
        for day_offset in range(days):
            forecast_date = start_date + timedelta(days=day_offset)
            transits = await self._calculate_transits(natal_chart, forecast_date, birth_data=birth_data)
            forecast = await self._build_forecast(transits, natal_chart, forecast_date, locale)
            
            # Calculate intensity score
            intensity = self._calculate_intensity_score(transits)
            forecast.intensity_score = intensity
            
            forecasts.append(forecast)
        
        # Identify periods and peaks
        periods = self._identify_periods(forecasts, start_date, locale=locale)
        peaks = [p for p in periods if p.intensity_level in ["peak", "high"]]
        low_periods = [p for p in periods if p.intensity_level == "low"]
        
        return models.ForecastPeriods(
            forecasts=forecasts,
            periods=periods,
            peaks=peaks,
            low_periods=low_periods,
        )
    
    async def get_yearly_forecast(
        self,
        natal_chart: astro.ChartResponse,
        target_year: int | None = None,
        birth_date: date | None = None,
        birth_data: models.BirthData | None = None,
        locale: str | None = None,
    ) -> models.YearlyForecast:
        """
        Generate personalized yearly forecast based on Solar Return and transits.
        
        Combines:
        - Solar Return chart (main themes of the year)
        - Monthly transit analysis (key periods and peaks)
        - Yearly recommendations
        """
        from todayflow_backend.services.returns import ReturnsService
        
        if target_year is None:
            target_year = date.today().year
        
        if birth_date is None and birth_data:
            birth_date = date.fromisoformat(birth_data.date)
        elif birth_date is None:
            # Try to extract from natal_chart metadata
            if natal_chart.metadata and natal_chart.metadata.get("birth_date"):
                birth_date = date.fromisoformat(natal_chart.metadata["birth_date"])
            else:
                raise ValueError("birth_date is required for yearly forecast")
        
        # Calculate Solar Return
        returns_service = ReturnsService(
            astro_service=self.astro_service,
            aspect_engine=self.aspect_engine
        )
        
        birth_coordinates = None
        if birth_data and birth_data.coordinates:
            birth_coordinates = {"latitude": birth_data.coordinates.latitude, "longitude": birth_data.coordinates.longitude}
        
        solar_return = await returns_service.calculate_solar_return(
            natal_chart=natal_chart,
            birth_date=birth_date,
            target_year=target_year,
            birth_coordinates=birth_coordinates,
            locale=locale,
        )
        
        # Calculate monthly forecasts for the year (sample 12 months)
        # Start from Solar Return date
        solar_return_date = date.fromisoformat(solar_return.solar_return_date)
        monthly_overview = []
        all_forecasts = []
        
        # Sample one day per month for overview
        for month_offset in range(12):
            sample_date = solar_return_date + timedelta(days=month_offset * 30)
            # Get forecast for middle of each month
            monthly_date = date(sample_date.year, sample_date.month, min(15, sample_date.day))
            
            try:
                monthly_forecast = await self.get_daily_forecast(
                    natal_chart=natal_chart,
                    forecast_date=monthly_date,
                    birth_data=birth_data,
                    locale=locale,
                )
                all_forecasts.append(monthly_forecast)
                monthly_overview.append({
                    "month": monthly_date.month,
                    "month_name": monthly_date.strftime("%B"),
                    "intensity_score": monthly_forecast.intensity_score,
                    "key_themes": [self._humanize_focus_area(insight.area, locale) for insight in monthly_forecast.psychological_insights[:3]],
                    "summary": self._compose_monthly_overview_summary(monthly_forecast, monthly_date, locale),
                })
            except Exception:
                # Skip if forecast fails for this month
                pass
        
        # Get forecast with periods for the year (sample every 2 weeks for performance)
        # This gives us ~26 data points for the year
        yearly_periods_forecast = await self.get_forecast_with_periods(
            natal_chart=natal_chart,
            start_date=solar_return_date,
            days=365,
            birth_data=birth_data,
            locale=locale,
        )
        
        # Extract main themes from Solar Return and transit patterns
        main_themes = self._extract_yearly_themes(solar_return, yearly_periods_forecast, locale=locale)
        focus_areas = self._extract_focus_areas(yearly_periods_forecast, locale=locale)
        recommendations = self._generate_yearly_recommendations(solar_return, yearly_periods_forecast, locale)
        
        # Calculate overall intensity
        if all_forecasts:
            overall_intensity = sum(f.intensity_score for f in all_forecasts) / len(all_forecasts)
        else:
            overall_intensity = 0.5
        
        # SolarReturnChart doesn't include chart data yet (per model definition)
        # This will be None for now, but structure is ready for future enhancement
        solar_return_chart_dict = None
        
        return models.YearlyForecast(
            year=target_year,
            solar_return_date=solar_return.solar_return_date,
            solar_return_chart=solar_return_chart_dict,
            main_themes=main_themes,
            key_periods=yearly_periods_forecast.periods,
            peak_periods=yearly_periods_forecast.peaks,
            focus_areas=focus_areas,
            recommendations=recommendations,
            monthly_overview=monthly_overview,
            intensity_score=overall_intensity,
        )
    
    def _extract_yearly_themes(
        self,
        solar_return: models.SolarReturnChart,
        periods_forecast: models.ForecastPeriods,
        locale: str | None = None,
    ) -> List[str]:
        """Extract main themes for the year from Solar Return and transit patterns."""
        themes = []
        
        # Extract themes from peak periods
        peak_focus_areas = []
        for peak in periods_forecast.peaks[:5]:  # Top 5 peak periods
            peak_focus_areas.extend(peak.focus_areas)
        
        # Most common focus areas become themes
        from collections import Counter
        focus_counter = Counter(peak_focus_areas)
        common_focus = [self._humanize_focus_area(area, locale) for area, count in focus_counter.most_common(3)]
        themes.extend(common_focus)
        
        if (locale or "").startswith("ru"):
            themes.append(
                f"{solar_return.target_year} год просит меньше распыления и больше верности тем линиям, которые действительно определяют твою опору."
            )
        else:
            themes.append(
                f"{solar_return.target_year} asks for less scattering and more commitment to the few themes that truly define your foundation."
            )
        
        return list(set(themes))[:5]  # Return up to 5 unique themes
    
    def _extract_focus_areas(self, periods_forecast: models.ForecastPeriods, locale: str | None = None) -> List[str]:
        """Extract focus areas from transit periods."""
        all_focus_areas = []
        for period in periods_forecast.periods:
            all_focus_areas.extend(period.focus_areas)
        
        from collections import Counter
        focus_counter = Counter(all_focus_areas)
        return [self._humanize_focus_area(area, locale) for area, count in focus_counter.most_common(5)]
    
    def _generate_yearly_recommendations(
        self,
        solar_return: models.SolarReturnChart,
        periods_forecast: models.ForecastPeriods,
        locale: str | None = None,
    ) -> List[str]:
        """Generate yearly recommendations based on Solar Return and transit patterns."""
        recommendations = []
        
        # Recommendations based on peak periods
        if periods_forecast.peaks:
            recommendations.append(f"Plan for {len(periods_forecast.peaks)} high-intensity periods throughout the year")
        
        # Recommendations based on focus areas
        focus_areas = self._extract_focus_areas(periods_forecast, locale=locale)
        if focus_areas:
            if (locale or "").startswith("ru"):
                recommendations.append(
                    f"Главные линии года: {', '.join(focus_areas[:3])}. Возвращайся к ним, когда начнешь распыляться или терять ясность."
                )
            else:
                recommendations.append(
                    f"The year keeps returning you to: {', '.join(focus_areas[:3])}. Use them as anchors whenever clarity starts to fade."
                )
        
        # Solar Return recommendation
        if (locale or "").startswith("ru"):
            recommendations.append(
                "Это год обновления через зрелые решения. В сильные периоды двигай важное вперед, а в спокойные давай себе время на сборку, отдых и переоценку."
            )
        else:
            recommendations.append(
                "This is a year of renewal through mature decisions. Use stronger periods to move key matters forward, and quieter ones for integration and rest."
            )
        
        return recommendations
    
    async def get_lunar_phases_forecast(
        self,
        natal_chart: astro.ChartResponse,
        target_month: date | None = None,
        birth_date: date | None = None,
        birth_data: models.BirthData | None = None,
        locale: str | None = None,
    ) -> models.LunarPhasesForecast:
        """
        Generate personalized lunar phases forecast based on Lunar Return and moon phases.
        
        Combines:
        - Lunar Return chart (emotional themes of the month)
        - Moon phases (new, waxing, full, waning) for the month
        - Emotional rhythms and planning guidance
        """
        from todayflow_backend.services.returns import ReturnsService
        
        if target_month is None:
            target_month = date.today()
        
        if birth_date is None and birth_data:
            birth_date = date.fromisoformat(birth_data.date)
        elif birth_date is None:
            # Try to extract from natal_chart metadata
            if natal_chart.metadata and natal_chart.metadata.get("birth_date"):
                birth_date = date.fromisoformat(natal_chart.metadata["birth_date"])
            else:
                raise ValueError("birth_date is required for lunar phases forecast")
        
        # Calculate Lunar Return
        returns_service = ReturnsService(
            astro_service=self.astro_service,
            aspect_engine=self.aspect_engine
        )
        
        birth_coordinates = None
        if birth_data and birth_data.coordinates:
            birth_coordinates = {"latitude": birth_data.coordinates.latitude, "longitude": birth_data.coordinates.longitude}
        
        lunar_return = await returns_service.calculate_lunar_return(
            natal_chart=natal_chart,
            birth_date=birth_date,
            target_month=target_month,
            birth_coordinates=birth_coordinates,
            locale=locale,
        )
        
        # Calculate moon phases for the month (simplified - would need ephemeris for exact dates)
        # For now, use approximate dates
        lunar_return_date = date.fromisoformat(lunar_return.lunar_return_date)
        phase_dates = self._calculate_monthly_moon_phases(target_month)
        current_phase = self._get_current_phase(phase_dates, target_month)
        
        # Generate monthly themes from Lunar Return
        monthly_themes = self._extract_monthly_themes(lunar_return)
        emotional_rhythms = self._generate_emotional_rhythms(lunar_return, phase_dates, locale)
        recommendations = self._generate_lunar_recommendations(lunar_return, phase_dates, locale)
        planning_guidance = self._generate_planning_guidance(phase_dates, locale)
        
        # Get key periods (sample forecasts for major phases)
        key_periods = []
        for phase_date_info in phase_dates:
            if phase_date_info.get("phase") in ["new", "full"]:  # Key phases
                try:
                    phase_date = date.fromisoformat(phase_date_info["date"])
                    forecast = await self.get_daily_forecast(
                        natal_chart=natal_chart,
                        forecast_date=phase_date,
                        birth_data=birth_data,
                        locale=locale,
                    )
                    # Create a period for this phase (3-day window)
                    key_periods.append(models.TransitPeriod(
                        start_date=(phase_date - timedelta(days=1)).isoformat(),
                        end_date=(phase_date + timedelta(days=1)).isoformat(),
                        intensity_level=self._classify_intensity(forecast.intensity_score),
                        description=self._describe_lunar_window(phase_date_info["phase"], phase_date_info.get("description", ""), locale),
                        key_transits=[t.get("transiting_planet", "") + " " + t.get("aspect", "") + " " + t.get("natal_planet", "") for t in forecast.transits[:3]],
                        focus_areas=[self._humanize_focus_area(insight.area, locale) for insight in forecast.psychological_insights[:3]],
                    ))
                except Exception:
                    pass
        
        return models.LunarPhasesForecast(
            month=target_month.strftime("%B %Y"),
            lunar_return_date=lunar_return.lunar_return_date,
            lunar_return_chart=None,  # Future enhancement
            current_phase=current_phase,
            phase_dates=phase_dates,
            emotional_rhythms=emotional_rhythms,
            monthly_themes=monthly_themes,
            key_periods=key_periods,
            recommendations=recommendations,
            planning_guidance=planning_guidance,
        )
    
    def _calculate_monthly_moon_phases(self, target_month: date) -> List[Dict[str, Any]]:
        """Calculate approximate moon phases for a month."""
        # Simplified calculation - approximate moon phases
        # Moon cycle is ~29.5 days
        # Phases: new (0°), waxing (0-180°), full (180°), waning (180-360°)
        
        phases = []
        # Approximate: new moon every ~29.5 days
        # For simplicity, estimate phases for the month
        first_day = date(target_month.year, target_month.month, 1)
        
        # Estimate new moon dates (simplified)
        # In reality, this would require ephemeris calculations
        estimated_new_moon = first_day.day % 30  # Rough estimate
        
        phases.append({
            "date": date(target_month.year, target_month.month, min(estimated_new_moon, 28)).isoformat(),
            "phase": "new",
            "description": "New Moon - time for new beginnings and setting intentions",
        })
        
        phases.append({
            "date": date(target_month.year, target_month.month, min(estimated_new_moon + 7, 28)).isoformat(),
            "phase": "waxing",
            "description": "Waxing Moon - time for growth and taking action",
        })
        
        phases.append({
            "date": date(target_month.year, target_month.month, min(estimated_new_moon + 15, 28)).isoformat(),
            "phase": "full",
            "description": "Full Moon - time for release and culmination",
        })
        
        phases.append({
            "date": date(target_month.year, target_month.month, min(estimated_new_moon + 22, 28)).isoformat(),
            "phase": "waning",
            "description": "Waning Moon - time for reflection and letting go",
        })
        
        return sorted(phases, key=lambda x: x["date"])
    
    def _get_current_phase(self, phase_dates: List[Dict[str, Any]], target_date: date) -> str:
        """Get current moon phase based on dates."""
        # Find closest phase date
        closest_phase = "new"
        min_diff = float('inf')
        
        for phase_info in phase_dates:
            phase_date = date.fromisoformat(phase_info["date"])
            diff = abs((target_date - phase_date).days)
            if diff < min_diff:
                min_diff = diff
                closest_phase = phase_info["phase"]
        
        return closest_phase
    
    def _extract_monthly_themes(self, lunar_return: models.LunarReturnChart) -> List[str]:
        """Extract monthly themes from Lunar Return."""
        themes = []
        themes.append(f"Lunar Return month: {lunar_return.description}")
        themes.append("Emotional cycles and rhythms")
        themes.append("Monthly patterns and cycles")
        return themes
    
    def _generate_emotional_rhythms(
        self,
        lunar_return: models.LunarReturnChart,
        phase_dates: List[Dict[str, Any]],
        locale: str | None = None,
    ) -> List[str]:
        """Generate emotional rhythm descriptions."""
        rhythms = []
        rhythms.append("Emotional patterns align with lunar cycles this month")
        rhythms.append("Pay attention to how your emotions shift with moon phases")
        rhythms.append("Use lunar phases as markers for emotional awareness")
        return rhythms
    
    def _generate_lunar_recommendations(
        self,
        lunar_return: models.LunarReturnChart,
        phase_dates: List[Dict[str, Any]],
        locale: str | None = None,
    ) -> List[str]:
        """Generate recommendations based on lunar phases."""
        recommendations = []
        recommendations.append("Plan new projects around New Moon phases")
        recommendations.append("Use Full Moon periods for release and completion")
        recommendations.append("Waxing phases are good for action and growth")
        recommendations.append("Waning phases support reflection and rest")
        return recommendations
    
    def _generate_planning_guidance(
        self,
        phase_dates: List[Dict[str, Any]],
        locale: str | None = None,
    ) -> Dict[str, List[str]]:
        """Generate planning guidance by phase."""
        guidance = {
            "new": [
                "Set new intentions and start fresh projects",
                "Focus on what you want to create",
                "Plant seeds for the month ahead",
            ],
            "waxing": [
                "Take action on your goals",
                "Build momentum and move forward",
                "Make decisions and commitments",
            ],
            "full": [
                "Release what no longer serves you",
                "Celebrate completions and achievements",
                "Pay attention to emotional peaks",
            ],
            "waning": [
                "Reflect on the month's experiences",
                "Let go and prepare for new cycle",
                "Rest and integrate lessons learned",
            ],
        }
        return guidance
    
    def _calculate_intensity_score(self, transits: List[TransitToNatal]) -> float:
        """Calculate intensity score (0-1) based on transits."""
        if not transits:
            return 0.0
        
        # Weight by aspect type and strength
        score = 0.0
        for transit in transits:
            aspect_weight = {
                "conjunction": 0.8,
                "square": 0.9,
                "opposition": 0.9,
                "trine": 0.5,
                "sextile": 0.4,
            }.get(transit.aspect_id, 0.5)
            
            strength_weight = {
                "exact": 1.0,
                "strong": 0.8,
                "medium": 0.6,
                "weak": 0.3,
            }.get(transit.strength, 0.5)
            
            score += aspect_weight * strength_weight
        
        # Normalize to 0-1 scale
        max_possible = len(transits) * 1.0
        return min(1.0, score / max_possible if max_possible > 0 else 0.0)
    
    def _identify_periods(
        self,
        forecasts: List[models.DailyForecast],
        start_date: date,
        locale: str | None = None,
    ) -> List[models.TransitPeriod]:
        """Identify periods of intensity from forecasts."""
        periods = []
        
        if not forecasts:
            return periods
        
        # Group consecutive days with similar intensity
        current_period_start = None
        current_intensity = None
        current_transits = []
        
        for i, forecast in enumerate(forecasts):
            forecast_date = date.fromisoformat(forecast.date)
            intensity_level = self._classify_intensity(forecast.intensity_score)
            
            if current_intensity is None:
                current_period_start = forecast_date
                current_intensity = intensity_level
                current_transits = [t.get("transiting_planet", "") + " " + t.get("aspect", "") + " " + t.get("natal_planet", "") for t in forecast.transits]
            elif intensity_level == current_intensity:
                # Continue current period
                current_transits.extend([t.get("transiting_planet", "") + " " + t.get("aspect", "") + " " + t.get("natal_planet", "") for t in forecast.transits])
            else:
                # End current period, start new one
                if current_period_start:
                    periods.append(models.TransitPeriod(
                        start_date=current_period_start.isoformat(),
                        end_date=(forecast_date - timedelta(days=1)).isoformat(),
                        intensity_level=current_intensity,
                        description=self._describe_period(current_intensity, current_transits, locale),
                        key_transits=list(set(current_transits))[:5],  # Top 5 unique transits
                        focus_areas=self._identify_focus_areas(current_transits, locale),
                    ))
                
                current_period_start = forecast_date
                current_intensity = intensity_level
                current_transits = [t.get("transiting_planet", "") + " " + t.get("aspect", "") + " " + t.get("natal_planet", "") for t in forecast.transits]
        
        # Add final period
        if current_period_start:
            last_date = date.fromisoformat(forecasts[-1].date)
            periods.append(models.TransitPeriod(
                start_date=current_period_start.isoformat(),
                end_date=last_date.isoformat(),
                intensity_level=current_intensity or "medium",
                description=self._describe_period(current_intensity or "medium", current_transits, locale),
                key_transits=list(set(current_transits))[:5],
                focus_areas=self._identify_focus_areas(current_transits, locale),
            ))
        
        return periods
    
    def _classify_intensity(self, score: float) -> str:
        """Classify intensity level from score."""
        if score >= 0.8:
            return "peak"
        elif score >= 0.6:
            return "high"
        elif score >= 0.3:
            return "medium"
        else:
            return "low"
    
    def _describe_period(self, intensity: str, transits: List[str], locale: str | None = None) -> str:
        """Generate description for a period."""
        if (locale or "").startswith("ru"):
            if intensity == "peak":
                return "Плотный период: события и внутренние реакции будут ощущаться сильнее обычного. Здесь важнее выбирать главное, чем пытаться успеть все."
            elif intensity == "high":
                return "Активный период: движения и поводы включаться станет больше. Поможет заранее понимать, где ты действительно хочешь участвовать."
            elif intensity == "low":
                return "Спокойный период: хорошее окно для восстановления, завершения хвостов и мягкой сборки без лишнего давления."
            else:
                return "Ровный период: без резких перегрузок, но с хорошим потенциалом для последовательных, аккуратных шагов."
        if intensity == "peak":
            return "A dense period: events and emotions may feel stronger than usual, so choosing what matters is better than trying to hold everything."
        elif intensity == "high":
            return "An active period: more movement and more reasons to engage. It helps to know in advance where you truly want to invest attention."
        elif intensity == "low":
            return "A calmer period: a good window for recovery, closure, and steady integration without extra pressure."
        else:
            return "A steady period: less dramatic, but well suited for consistent and careful progress."
    
    def _identify_focus_areas(self, transits: List[str], locale: str | None = None) -> List[str]:
        """Identify focus areas from transit descriptions."""
        areas = []
        planet_areas = {
            "Sun": "identity",
            "Moon": "emotions",
            "Mercury": "communication",
            "Venus": "relationships",
            "Mars": "action",
            "Jupiter": "growth",
            "Saturn": "structure",
            "Uranus": "change",
            "Neptune": "intuition",
            "Pluto": "transformation",
        }
        
        for transit in transits:
            for planet, area in planet_areas.items():
                if planet in transit:
                    if area not in areas:
                        areas.append(area)
        
        return [self._humanize_focus_area(area, locale) for area in areas[:5]]  # Top 5 focus areas

    def _humanize_focus_area(self, area: str, locale: str | None = None) -> str:
        normalized = (area or "").strip().lower()
        labels_ru = {
            "identity": "самоопределение и личный голос",
            "identity and self-expression": "самоопределение и личный голос",
            "emotions": "эмоции и внутренняя опора",
            "emotions and security": "эмоции и внутренняя опора",
            "communication": "разговоры, договоренности и обучение",
            "communication and learning": "разговоры, договоренности и обучение",
            "relationships": "отношения и личные ценности",
            "relationships and values": "отношения и личные ценности",
            "action": "действие, смелость и границы",
            "action and desire": "действие, смелость и границы",
            "growth": "рост, возможности и расширение",
            "growth and expansion": "рост, возможности и расширение",
            "structure": "структура, обязательства и опора",
            "structure and responsibility": "структура, обязательства и опора",
            "change": "перемены и обновление",
            "change and innovation": "перемены и обновление",
            "intuition": "интуиция, воображение и тонкое восприятие",
            "intuition and creativity": "интуиция, воображение и тонкое восприятие",
            "transformation": "глубокие перемены и перераспределение силы",
            "transformation and power": "глубокие перемены и перераспределение силы",
        }
        labels_en = {
            "identity": "identity and personal voice",
            "identity and self-expression": "identity and personal voice",
            "emotions": "emotions and inner stability",
            "emotions and security": "emotions and inner stability",
            "communication": "conversations, agreements, and learning",
            "communication and learning": "conversations, agreements, and learning",
            "relationships": "relationships and personal values",
            "relationships and values": "relationships and personal values",
            "action": "action, courage, and boundaries",
            "action and desire": "action, courage, and boundaries",
            "growth": "growth, opportunity, and expansion",
            "growth and expansion": "growth, opportunity, and expansion",
            "structure": "structure, commitments, and support",
            "structure and responsibility": "structure, commitments, and support",
            "change": "change and renewal",
            "change and innovation": "change and renewal",
            "intuition": "intuition, imagination, and sensitivity",
            "intuition and creativity": "intuition, imagination, and sensitivity",
            "transformation": "deep change and power shifts",
            "transformation and power": "deep change and power shifts",
        }
        if (locale or "").startswith("ru"):
            return labels_ru.get(normalized, area)
        return labels_en.get(normalized, area)

    def _compose_monthly_overview_summary(
        self,
        monthly_forecast: models.DailyForecast,
        monthly_date: date,
        locale: str | None = None,
    ) -> str:
        if monthly_forecast.psychological_insights:
            lead = monthly_forecast.psychological_insights[0].psychological_description
            if lead:
                return lead
        if (locale or "").startswith("ru"):
            return f"{monthly_date.strftime('%B')} лучше проживать через один ясный фокус и несколько последовательных решений, а не через спешку и попытку удержать все сразу."
        return f"{monthly_date.strftime('%B')} is better lived through one clear focus and a few steady decisions rather than scattered urgency."

    def _describe_lunar_window(self, phase: str, description: str, locale: str | None = None) -> str:
        if (locale or "").startswith("ru"):
            mapping = {
                "new": "Новолуние открывает окно для новых намерений и тихого старта без лишнего давления.",
                "waxing": "Растущая Луна помогает набирать темп и укреплять то, что ты уже выбрала.",
                "full": "Полнолуние делает чувства и результаты заметнее, поэтому важно не перегреть реакцию.",
                "waning": "Убывающая Луна поддерживает завершение, отпускание лишнего и восстановление ритма.",
            }
            return mapping.get(phase, description or "Это окно лучше читать через ритм, а не через спешку.")
        mapping = {
            "new": "New Moon opens a window for quiet beginnings and clean intentions.",
            "waxing": "Waxing Moon supports momentum and the strengthening of what you already chose.",
            "full": "Full Moon makes emotions and outcomes more visible, so reactions need extra care.",
            "waning": "Waning Moon supports completion, release, and a calmer rhythm.",
        }
        return mapping.get(phase, description or "Read this window through rhythm rather than urgency.")
    
    async def _build_forecast(
        self,
        transits: List[TransitToNatal],
        natal_chart: astro.ChartResponse,
        forecast_date: date,
        locale: str | None = None,
    ) -> models.DailyForecast:
        """
        Build DailyForecast from calculated transits.
        """
        
        # Generate psychological interpretation
        psychological_insights = self._interpret_transits(
            transits,
            natal_chart,
            locale=locale
        )
        
        # Organize by tension/resource/action
        tensions = [t for t in transits if t.tension_level in ["high", "medium"]]
        resources = [t for t in transits if t.tension_level == "low" and t.aspect_id in ["trine", "sextile", "conjunction"]]
        
        # Generate conscious actions
        conscious_actions = self._generate_conscious_actions(transits, tensions, resources, locale=locale)
        conscious_actions = self._apply_human_layer(conscious_actions)
        
        # Convert psychological insights to models (find matching transit for strength/tension)
        insight_models = []
        for insight in psychological_insights:
            # Find matching transit for strength and tension_level
            matching_transit = next((t for t in transits if t.transiting_planet == insight["transiting_planet"] and t.natal_planet == insight["natal_planet"]), None)
            insight_models.append(models.TransitInsight(
                transiting_planet=insight["transiting_planet"],
                natal_planet=insight["natal_planet"],
                aspect=insight["aspect"],
                strength=matching_transit.strength if matching_transit else "medium",
                tension_level=matching_transit.tension_level if matching_transit else "medium",
                area=insight.get("area", ""),
                feeling=insight.get("feeling", ""),
                psychological_description=self._apply_human_layer_text(insight.get("psychological_description", "")),
                recommendations=[self._apply_human_layer_text(r) for r in insight.get("recommendations", [])],
            ))
        
        return models.DailyForecast(
            date=forecast_date.isoformat(),
            transits=[
                {
                    "transiting_planet": t.transiting_planet,
                    "natal_planet": t.natal_planet,
                    "aspect": t.aspect_id,
                    "strength": t.strength,
                    "tension_level": t.tension_level,
                }
                for t in transits
            ],
            tensions=[
                {
                    "transiting_planet": t.transiting_planet,
                    "natal_planet": t.natal_planet,
                    "aspect": t.aspect_id,
                    "description": self._apply_human_layer_text(self._describe_tension(t)),
                }
                for t in tensions
            ],
            resources=[
                {
                    "transiting_planet": t.transiting_planet,
                    "natal_planet": t.natal_planet,
                    "aspect": t.aspect_id,
                    "description": self._apply_human_layer_text(self._describe_resource(t)),
                }
                for t in resources
            ],
            psychological_insights=insight_models,
            conscious_actions=conscious_actions,
            intensity_score=self._calculate_intensity_score(transits),
        )
    
    async def _calculate_transits(
        self,
        natal_chart: astro.ChartResponse,
        forecast_date: date,
        birth_data: models.BirthData | None = None,
    ) -> List[TransitToNatal]:
        """
        Calculate transiting planets' aspects to natal planets.
        
        Steps:
        1. Calculate current positions of transiting planets for forecast_date
        2. Extract natal planet positions from natal_chart
        3. Calculate aspects between transiting and natal planets
        4. Return list of TransitToNatal objects
        """
        from math import fabs
        
        transits: List[TransitToNatal] = []
        
        # Extract natal planet positions
        natal_positions = {p["body"]: p for p in natal_chart.positions if "body" in p and "longitude" in p}
        if not natal_positions:
            return transits
        
        # Calculate transit chart for forecast_date
        # For transits, we use the same location as birth but current date/time
        # If birth_data provided, use its location; otherwise use noon at same location
        transit_chart = None
        if birth_data and birth_data.coordinates:
            try:
                # Compute transit chart (current positions of planets on forecast_date)
                # Use noon on forecast_date at birth location
                transit_birth_payload = {
                    "date": forecast_date.isoformat(),
                    "time": "12:00",  # Use noon for transits
                    "location": birth_data.location,
                }
                transit_chart = await self.astro_service.compute_chart(
                    birth_payload=transit_birth_payload,
                    coordinates={"latitude": birth_data.coordinates.latitude, "longitude": birth_data.coordinates.longitude}
                )
            except Exception:
                # If transit chart calculation fails, return empty list
                return transits
        
        if not transit_chart:
            # Fallback: can't calculate transits without location
            return transits
        
        # Extract transiting planet positions
        transit_positions = {p["body"]: p for p in transit_chart.positions if "body" in p and "longitude" in p}
        
        # Key transiting planets to check (including Chiron and Nodes if available)
        transiting_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "Chiron", "North Node", "South Node"]
        # Key natal planets/points to check (including Chiron, Nodes, Lilith, Part of Fortune if available)
        natal_points = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "Chiron", "North Node", "South Node", "Ascendant", "MC", "Lilith", "Part of Fortune"]
        
        # Get aspect_map from AspectEngine (aspect_map is a public attribute)
        aspect_map = self.aspect_engine.aspect_map
        
        # Calculate aspects between transiting planets and natal points
        for trans_planet in transiting_planets:
            if trans_planet not in transit_positions:
                continue
            
            trans_long = transit_positions[trans_planet]["longitude"]
            
            for natal_point in natal_points:
                if natal_point not in natal_positions:
                    continue
                
                natal_long = natal_positions[natal_point]["longitude"]
                
                # Calculate aspect using same logic as AspectEngine
                raw_difference = fabs(trans_long - natal_long) % 360
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
                    # Determine tension level based on aspect type
                    tension_map = {
                        "conjunction": "medium",
                        "square": "high",
                        "opposition": "high",
                        "trine": "low",
                        "sextile": "low",
                    }
                    tension_level = tension_map.get(aspect_id, "medium")
                    
                    # Determine strength based on orb
                    if orb_delta <= 1:
                        strength = "exact"
                    elif orb_delta <= 3:
                        strength = "strong"
                    elif orb_delta <= 5:
                        strength = "medium"
                    else:
                        strength = "weak"
                    
                    # Only include significant aspects (medium or stronger)
                    if strength in ["exact", "strong", "medium"]:
                        transits.append(TransitToNatal(
                            transiting_planet=trans_planet,
                            natal_planet=natal_point,
                            aspect_id=aspect_id,
                            degrees_apart=round(raw_difference, 2),
                            orb_delta=round(orb_delta, 2),
                            strength=strength,
                            tension_level=tension_level,
                        ))
        
        return transits
    
    def _interpret_transits(
        self,
        transits: List[TransitToNatal],
        natal_chart: astro.ChartResponse,
        locale: str | None = None,
    ) -> List[Dict[str, Any]]:
        """Generate psychological interpretation of transits."""
        insights = []
        
        for transit in transits:
            insight = self._interpret_single_transit(transit, natal_chart, locale=locale)
            if insight:
                insights.append(insight)
        
        return insights
    
    def _interpret_single_transit(
        self,
        transit: TransitToNatal,
        natal_chart: astro.ChartResponse,
        locale: str | None = None,
    ) -> Dict[str, Any] | None:
        """Interpret a single transit from psychological perspective."""
        # Map transit to psychological meaning
        # This is where we translate "Mars square Saturn" to "You may feel irritation and restraint simultaneously"
        
        planet_meanings = {
            "Sun": {"area": "identity", "energy": "vitality"},
            "Moon": {"area": "emotions", "energy": "feelings"},
            "Mercury": {"area": "communication", "energy": "thinking"},
            "Venus": {"area": "relationships", "energy": "love"},
            "Mars": {"area": "action", "energy": "desire"},
            "Jupiter": {"area": "expansion", "energy": "growth"},
            "Saturn": {"area": "structure", "energy": "restraint"},
            "Uranus": {"area": "change", "energy": "breakthrough"},
            "Neptune": {"area": "intuition", "energy": "dissolution"},
            "Pluto": {"area": "transformation", "energy": "power"},
        }
        
        transiting_area = planet_meanings.get(transit.transiting_planet, {}).get("area", "life")
        natal_area = planet_meanings.get(transit.natal_planet, {}).get("area", "self")
        
        aspect_meanings = {
            "conjunction": {"feeling": "intense focus", "action": "integration"},
            "square": {"feeling": "tension and conflict", "action": "resolution"},
            "trine": {"feeling": "flow and ease", "action": "utilization"},
            "opposition": {"feeling": "polarization", "action": "balance"},
            "sextile": {"feeling": "opportunity", "action": "activation"},
        }
        
        aspect_meaning = aspect_meanings.get(transit.aspect_id, {})
        
        return {
            "transiting_planet": transit.transiting_planet,
            "natal_planet": transit.natal_planet,
            "aspect": transit.aspect_id,
            "area": f"{transiting_area} activating {natal_area}",
            "feeling": aspect_meaning.get("feeling", ""),
            "psychological_description": self._create_psychological_description(transit, planet_meanings),
            "recommendations": self._generate_recommendations(transit, aspect_meaning),
        }
    
    def _create_psychological_description(
        self,
        transit: TransitToNatal,
        planet_meanings: Dict[str, Dict[str, str]],
    ) -> str:
        """Create human-readable psychological description of transit."""
        # This is where Human Layer principles apply
        # Instead of "Mars square Saturn", we say:
        # "You may feel irritation and simultaneously a stop. You want to act, but something is holding you back."
        
        transiting_info = planet_meanings.get(transit.transiting_planet, {})
        natal_info = planet_meanings.get(transit.natal_planet, {})
        
        transit_energy = transiting_info.get("energy", "energy")
        natal_energy = natal_info.get("energy", "energy")
        
        if transit.aspect_id == "square":
            return f"You may feel {transit_energy} and simultaneously a restraint. You want to {transit_energy.lower()}, but something is holding you back."
        elif transit.aspect_id == "conjunction":
            return f"There's an intense focus on {natal_energy.lower()}. This is a time of integration and concentration."
        elif transit.aspect_id == "trine":
            return f"There's a natural flow around {natal_energy.lower()}. This is an opportunity to utilize this energy."
        elif transit.aspect_id == "opposition":
            return f"There's a tension between {transit_energy.lower()} and {natal_energy.lower()}. Finding balance is key."
        elif transit.aspect_id == "sextile":
            return f"There's an opportunity around {natal_energy.lower()}. This is a good time to activate this energy."
        
        return f"The {transit.transiting_planet} is activating your {transit.natal_planet}."
    
    def _generate_recommendations(
        self,
        transit: TransitToNatal,
        aspect_meaning: Dict[str, str],
    ) -> List[str]:
        """Generate conscious action recommendations."""
        recommendations = []
        
        if transit.tension_level in ["high", "medium"]:
            recommendations.append("Notice where you feel tension without immediately acting on it")
            recommendations.append("Take pauses between trigger and reaction")
            recommendations.append("Practice staying present with difficult feelings")
        else:
            recommendations.append(f"Utilize this {aspect_meaning.get('feeling', 'energy')}")
            recommendations.append("Notice what wants to flow naturally")
        
        return recommendations
    
    def _describe_tension(self, transit: TransitToNatal) -> str:
        """Describe where tension is happening."""
        return f"{transit.transiting_planet} {transit.aspect_id} {transit.natal_planet} creates tension around {transit.natal_planet.lower()} energy"
    
    def _describe_resource(self, transit: TransitToNatal) -> str:
        """Describe available resources."""
        return f"{transit.transiting_planet} {transit.aspect_id} {transit.natal_planet} supports {transit.natal_planet.lower()} energy"
    
    def _generate_conscious_actions(
        self,
        transits: List[TransitToNatal],
        tensions: List[TransitToNatal],
        resources: List[TransitToNatal],
        locale: str | None = None,
    ) -> List[str]:
        """Generate conscious actions based on transits."""
        actions = []
        
        if tensions:
            actions.append("Where tension: Notice without pushing. Let the intensity settle before acting.")
        
        if resources:
            actions.append("Where resource: Use this energy consciously. What wants to flow naturally?")
        
        if not tensions and not resources:
            actions.append("This is a neutral day. Good time for routine and maintenance.")
        
        return actions
    
    def _apply_human_layer(self, texts: List[str]) -> List[str]:
        """Apply Human Layer transformation to list of texts."""
        if not self.human_layer:
            return texts
        try:
            # HumanLayer uses transform_text method
            transform_method = getattr(self.human_layer, "transform_text", None) or getattr(self.human_layer, "transform", None)
            if transform_method:
                return [transform_method(t) for t in texts]
        except Exception:
            pass
        return texts
    
    def _apply_human_layer_text(self, text: str) -> str:
        """Apply Human Layer transformation to single text."""
        if not self.human_layer:
            return text
        try:
            # HumanLayer uses transform_text method
            transform_method = getattr(self.human_layer, "transform_text", None) or getattr(self.human_layer, "transform", None)
            if transform_method:
                return transform_method(text)
        except Exception:
            pass
        return text


async def get_personal_transit_service() -> PersonalTransitService:
    """Dependency function for PersonalTransitService."""
    return PersonalTransitService()
