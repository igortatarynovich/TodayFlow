"""Domain models shared across layers."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    latitude: float
    longitude: float


class BirthData(BaseModel):
    date: str
    time: str | None = None
    location: str
    coordinates: Coordinates | None = None


class BirthIntakePayload(BaseModel):
    label: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    relation: Optional[str] = "self"
    birth_date: date
    birth_time: Optional[time] = None
    time_unknown: bool = False
    timezone_name: Optional[str] = None
    timezone_offset_minutes: Optional[int] = None
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    show_map: bool = True
    notes: Optional[str] = None


class BirthIntakePreview(BaseModel):
    normalized_label: str
    birth_date: date
    birth_time: Optional[time] = None
    time_unknown: bool = False
    timezone_name: Optional[str] = None
    timezone_offset_minutes: Optional[int] = None
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    warnings: List[str] = Field(default_factory=list)


class ChartSnapshot(BaseModel):
    sun: str
    moon: str
    rising: str
    houses: dict = Field(default_factory=dict)


class Interpretation(BaseModel):
    paragraph_id: str
    variant_id: str
    text: str
    section: str
    meaning_type: str | None = None
    selection_trace: SelectionTrace | None = None


class SelectionTrace(BaseModel):
    paragraph_id: str
    meaning_type: str
    axes_hit: list[str] = Field(default_factory=list)
    modulators_hit: list[str] = Field(default_factory=list)
    confidence_level: str
    rule_ids: list[str] = Field(default_factory=list)


class AxisValue(BaseModel):
    axis_id: str
    value: float
    confidence: str = "medium"


class ModulatorValue(BaseModel):
    modulator_id: str
    value: float
    confidence: str = "medium"


class InternalModelSnapshot(BaseModel):
    axes: List[AxisValue]
    modulators: List[ModulatorValue]
    mode: str


class LiteReport(BaseModel):
    summary: ChartSnapshot
    paragraphs: List[Interpretation]
    internal_model: InternalModelSnapshot | None = None
    content_version: str
    chart_positions: List[dict[str, Any]] | None = None
    aspects: AspectResponse | None = None


class FullReportSection(BaseModel):
    section: str
    paragraphs: List[Interpretation]


class ReportHistoryItem(BaseModel):
    """Report history item."""
    id: int
    profile_id: Optional[int]
    product_type: str  # "lite" or "full"
    content_version: str
    created_at: datetime
    profile_label: Optional[str] = None
    
    class Config:
        from_attributes = True


class ReportHistoryResponse(BaseModel):
    """Report history response."""
    history: List[ReportHistoryItem]
    total: int


class PsychologicalPattern(BaseModel):
    """Single psychological pattern interpretation."""
    pattern_type: str  # "attachment_needs", "defense_mechanisms", etc.
    title: str
    description: str
    astro_indicators: List[str]  # Which astro elements indicate this pattern
    insights: List[str]
    recommendations: List[str] | None = None


class PsychologicalLayer(BaseModel):
    """Psychological layer interpretation for Full Report."""
    attachment_needs: List[PsychologicalPattern] = Field(default_factory=list)
    defense_mechanisms: List[PsychologicalPattern] = Field(default_factory=list)
    cognitive_patterns: List[PsychologicalPattern] = Field(default_factory=list)
    relational_style: List[PsychologicalPattern] = Field(default_factory=list)
    emotional_regulation: List[PsychologicalPattern] = Field(default_factory=list)
    behavioral_scenarios: List[PsychologicalPattern] = Field(default_factory=list)


class FullReport(BaseModel):
    summary: ChartSnapshot
    internal_model: InternalModelSnapshot
    sections: List[FullReportSection]
    content_version: str
    tarot_spreads: Optional[List["TarotSpreadRecord"]] = None
    psychological_layer: Optional["PsychologicalLayer"] = None
    chart_positions: Optional[List[dict[str, Any]]] = None
    aspects: Optional["AspectResponse"] = None


class ThematicReport(BaseModel):
    theme: str  # "career", "family", "children"
    summary: ChartSnapshot
    internal_model: InternalModelSnapshot
    sections: List[FullReportSection]


class Mantra(BaseModel):
    human_text: str | None = None  # Human-readable text from Content System
    id: str
    title: str
    intention: str
    axes: List[str]
    mantra: str
    pronunciation: str
    breath_count: int | None = None
    guidance: str
    stones: List[str] = Field(default_factory=list)
    best_for_phases: List[str] = Field(default_factory=list)
    notes: str | None = None


class Ritual(BaseModel):
    human_text: str | None = None  # Human-readable text from Content System
    id: str
    title: str
    duration_minutes: int | None = None
    intention: str
    axes: List[str] = Field(default_factory=list)
    ingredients: List[str] = Field(default_factory=list)
    instructions: List[str] = Field(default_factory=list)
    pair_with: List[str] = Field(default_factory=list)
    best_for_phases: List[str] = Field(default_factory=list)
    notes: str | None = None


class TarotCard(BaseModel):
    id: int
    name: str
    keywords: List[str]
    upright: str
    reversed: str
    correspondences: dict[str, Any] = Field(default_factory=dict)


class TarotDailyDraw(BaseModel):
    date: str
    card: TarotCard
    orientation: str
    mantra: Mantra | None = None
    ritual: Ritual | None = None


class TarotHistoryResponse(BaseModel):
    today: TarotDailyDraw
    history: List[TarotDailyDraw] = Field(default_factory=list)
    streak_days: int


class TarotSpreadRequest(BaseModel):
    spread_id: str | None = None
    question: str | None = None
    selected_cards: List["TarotSelectedCard"] = Field(default_factory=list)


class TarotSelectedCard(BaseModel):
    card_id: int
    orientation: str = "upright"


class TarotDeckDrawRequest(BaseModel):
    count: int = 10  # Количество карт для вытягивания из колоды


class TarotSpreadPosition(BaseModel):
    id: str
    title: str
    prompt: str | None = None


class TarotSpreadCard(BaseModel):
    position: TarotSpreadPosition
    card: TarotCard
    orientation: str
    meaning: str
    mantra: Mantra | None = None
    ritual: Ritual | None = None


class TarotSpreadResult(BaseModel):
    spread_id: str
    title: str
    description: str | None = None
    cards: List[TarotSpreadCard]


class TarotSpreadReading(BaseModel):
    meaning: str
    manifestation: str
    caution: str
    next_step: str


class TarotSpreadRecord(BaseModel):
    draw_date: str
    spread: TarotSpreadResult
    created_at: str | None = None


class TarotSpreadHistoryResponse(BaseModel):
    history: List[TarotSpreadRecord] = Field(default_factory=list)


class MoonPhaseSnapshot(BaseModel):
    id: str
    name: str
    keywords: List[str]
    themes: str
    guidance: str
    human_text: str | None = None  # Human-readable text from Content System
    angle_degrees: float
    cycle_day: float
    cycle_percent: float


class UpcomingPhase(BaseModel):
    id: str
    name: str
    date: str
    in_days: float


class MoonPhaseResponse(BaseModel):
    current: MoonPhaseSnapshot
    next_phase: UpcomingPhase
    upcoming: List[UpcomingPhase] = Field(default_factory=list)


class PlanetEvent(BaseModel):
    id: str
    planet: str
    event_type: str
    timestamp: str
    description: str | None = None
    sign: str | None = None
    aspect: str | None = None
    keywords: List[str] = Field(default_factory=list)
    human_text: str | None = None  # Human-readable text from Content System


class PlanetaryWindow(BaseModel):
    id: str
    planet: str
    window_type: str
    status: str
    start_timestamp: str
    end_timestamp: str
    label: str | None = None
    sign: str | None = None
    description: str | None = None
    keywords: List[str] = Field(default_factory=list)


class PlanetaryTimeline(BaseModel):
    upcoming: List[PlanetEvent] = Field(default_factory=list)
    windows: List[PlanetaryWindow] = Field(default_factory=list)


class TransitHighlight(BaseModel):
    id: str
    title: str
    description: str | None = None
    timestamp: str | None = None
    kind: str
    meta: str | None = None
    tags: List[str] = Field(default_factory=list)


class TransitFeedResponse(BaseModel):
    focus: MoonPhaseResponse
    highlights: List[TransitHighlight] = Field(default_factory=list)
    events: List[PlanetEvent] = Field(default_factory=list)
    windows: List[PlanetaryWindow] = Field(default_factory=list)


class TarotReminderSettings(BaseModel):
    enabled: bool = True
    timezone: str = "UTC"
    hour: int = Field(ge=0, le=23, default=9)
    minute: int = Field(ge=0, le=59, default=0)
    next_run_at: str | None = None
    last_sent_at: str | None = None


class TarotReminderUpdate(BaseModel):
    enabled: bool
    timezone: str
    hour: int = Field(ge=0, le=23)
    minute: int = Field(ge=0, le=59)


class TarotFavoritesResponse(BaseModel):
    favorites: List[int] = Field(default_factory=list)


class TarotFavoriteUpdate(BaseModel):
    card_id: int
    favorite: bool


class LibraryForecastsResponse(BaseModel):
    """My Library — сохранённые DailyForecast (Web Canon v1)."""

    saved: List[str] = Field(default_factory=list, description="forecast_id list")


class LibraryForecastToggle(BaseModel):
    forecast_id: str


class SavedCalculationItem(BaseModel):
    calc_type: str
    key: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class LibraryCalculationsResponse(BaseModel):
    """My Library — сохранённые расчёты (Вертикаль 2)."""

    saved: List[SavedCalculationItem] = Field(default_factory=list)


class LibraryCalculationToggle(BaseModel):
    calc_type: str  # life_path | birthday_number | personal_year
    key: str
    payload: Dict[str, Any] = Field(default_factory=dict)  # { input, output, version }


class CheckInPrompt(BaseModel):
    id: str
    prompt: str
    reflection_steps: List[str] = Field(default_factory=list)
    mantra: Mantra | None = None
    ritual: Ritual | None = None
    cta: str | None = None


class CheckInResponse(BaseModel):
    prompt: CheckInPrompt


class WeeklyInsight(BaseModel):
    phase_id: str
    phase_name: str
    axis_id: str | None = None
    axis_label: str | None = None
    title: str
    summary: str
    cta: str | None = None
    human_text: str | None = None  # Human-readable text from Content System
    keywords: List[str] = Field(default_factory=list)


class WeeklyInsightResponse(BaseModel):
    insight: WeeklyInsight
    next_phase: UpcomingPhase | None = None


class AspectCallout(BaseModel):
    aspect_id: str
    label: str
    bodies: str
    keywords: List[str]
    description: str
    tension_level: str
    polarity: str
    degrees_apart: float
    orb_delta: float
    strength: str
    axes: List[str] = Field(default_factory=list)
    modulators: List[str] = Field(default_factory=list)
    section: str | None = None
    integration: str | None = None


class AspectResponse(BaseModel):
    callouts: List[AspectCallout] = Field(default_factory=list)


class ShareableSnippet(BaseModel):
    paragraph_id: str
    section: str
    text: str
    meaning_type: str | None = None


class CrossDomainBridge(BaseModel):
    source_section: str
    target_section: str
    tease: str
    full_promise: str
    target_label: str


class NumerologyNumber(BaseModel):
    title: str
    value: int
    reduced_value: int
    is_master: bool = False
    summary: str


class NumerologyProfile(BaseModel):
    name: str
    birth_date: str
    life_path: NumerologyNumber
    expression: NumerologyNumber
    soul_urge: NumerologyNumber
    personality: NumerologyNumber


class NumerologyDailyInsight(BaseModel):
    date: str
    number: NumerologyNumber


class CalcStep(BaseModel):
    """Один шаг редукции (Web Canon v1, Вертикаль 2)."""
    expression: str
    sum: int


class NumerologyCalcResult(BaseModel):
    """Результат калькулятора: number, steps, is_master, master_numbers (Вертикаль 2)."""
    calc_type: str  # life_path | birthday_number | personal_year
    input: Dict[str, Any] = Field(default_factory=dict)
    output: Dict[str, Any] = Field(default_factory=dict)  # number, steps
    is_master: bool = False
    master_numbers: List[int] = Field(default_factory=lambda: [11, 22, 33])


class TransitInsight(BaseModel):
    """Single transit interpretation with psychological layer."""
    transiting_planet: str
    natal_planet: str
    aspect: str
    strength: str
    tension_level: str
    area: str  # What area is being activated
    feeling: str  # Psychological feeling/experience
    psychological_description: str  # Human-readable description (already through Human Layer)
    recommendations: List[str] = Field(default_factory=list)


class TransitPeriod(BaseModel):
    """Period of transit intensity (peak or low)."""
    start_date: str
    end_date: str
    intensity_level: str  # "peak", "high", "medium", "low"
    description: str
    key_transits: List[str]  # Which transits are active
    focus_areas: List[str]  # What areas of life are activated


class WeeklyBackgroundForecast(BaseModel):
    """Недельный фон (общий контекст, не детальный прогноз)."""
    week_start: str  # ISO date
    week_end: str  # ISO date
    background_text: str  # Общий текст недели (1 текст, без деталей)
    direction: str  # tension | release | transition | neutral
    key_transits: list[dict[str, Any]] = Field(default_factory=list)  # Топ транзиты недели
    intensity_score: float = 0.0  # Общая интенсивность недели


class DailyForecast(BaseModel):
    """Personalized daily forecast based on transits to natal chart."""
    date: str
    transits: List[Dict[str, Any]] = Field(default_factory=list)  # Raw transit data
    tensions: List[Dict[str, Any]] = Field(default_factory=list)  # Where tension is
    resources: List[Dict[str, Any]] = Field(default_factory=list)  # Available resources
    psychological_insights: List["TransitInsight"] = Field(default_factory=list)
    conscious_actions: List[str] = Field(default_factory=list)  # What to do consciously
    intensity_score: float = Field(default=0.0)  # 0-1 scale of transit intensity
    natal_chart: Optional[Dict[str, Any]] = None  # Натальная карта (позиции, дома, асцендент)


class ForecastPeriods(BaseModel):
    """Forecast with identified periods and peaks."""
    forecasts: List[DailyForecast]
    periods: List[TransitPeriod]  # Identified periods of intensity
    peaks: List[TransitPeriod]  # Peak intensity periods
    low_periods: List[TransitPeriod]  # Low intensity periods


class YearlyForecast(BaseModel):
    """Personalized yearly forecast based on Solar Return and transits."""
    year: int
    solar_return_date: str  # Date of Solar Return
    solar_return_chart: Dict[str, Any] | None = None  # Solar Return chart data
    main_themes: List[str] = Field(default_factory=list)  # Main themes of the year
    key_periods: List[TransitPeriod] = Field(default_factory=list)  # Key periods (quarters, months)
    peak_periods: List[TransitPeriod] = Field(default_factory=list)  # Peak intensity periods
    focus_areas: List[str] = Field(default_factory=list)  # Areas of focus (career, relationships, etc.)
    recommendations: List[str] = Field(default_factory=list)  # Yearly recommendations
    monthly_overview: List[Dict[str, Any]] = Field(default_factory=list)  # Monthly summaries
    natal_chart: Optional[Dict[str, Any]] = None  # Натальная карта (позиции, дома, асцендент)
    intensity_score: float = Field(default=0.0)  # Overall intensity for the year


class LunarPhasesForecast(BaseModel):
    """Personalized lunar phases forecast based on Lunar Return and moon phases."""
    month: str  # Month name (e.g., "January 2026")
    lunar_return_date: str  # Date of Lunar Return
    lunar_return_chart: Dict[str, Any] | None = None  # Lunar Return chart data
    current_phase: str  # Current moon phase (new, waxing, full, waning)
    phase_dates: List[Dict[str, Any]] = Field(default_factory=list)  # Dates of moon phases for the month
    emotional_rhythms: List[str] = Field(default_factory=list)  # Emotional rhythm descriptions
    monthly_themes: List[str] = Field(default_factory=list)  # Main themes of the month
    key_periods: List[TransitPeriod] = Field(default_factory=list)  # Key periods aligned with lunar phases
    recommendations: List[str] = Field(default_factory=list)  # Recommendations for the month
    planning_guidance: Dict[str, List[str]] = Field(default_factory=dict)  # Guidance by phase (new, waxing, full, waning)


# Synastry models for compatibility analysis
class SynastryAspect(BaseModel):
    """Aspect between two planets in synastry."""
    planet1: str
    planet2: str
    aspect: str
    orb: float
    strength: str
    description: str


class SynastryAngleAspect(BaseModel):
    """Aspect between planet and angle (ASC/MC) in synastry."""
    planet: str
    angle: str  # "ASC" or "MC"
    person_number: int  # 1 or 2 - which person's planet aspects which person's angle
    aspect: str
    orb: float
    description: str


class HouseOverlay(BaseModel):
    """Planet from one chart in a house of another chart."""
    planet: str
    house: int
    person_number: int  # 1 or 2 - which person's planet
    description: str
    significance: str


class CompatibilitySummary(BaseModel):
    """Overall compatibility summary from synastry analysis."""
    overall_score: int  # 0-100
    relationship_type: str  # "Harmonious", "Balanced", "Challenging"
    strengths: List[str]
    triggers: List[str]
    recommendations: List[str]


class CompatibilityDimension(BaseModel):
    """Scored dimension inside compatibility engine."""
    key: str
    label: str
    score: int
    summary: str
    indicators: List[str] = Field(default_factory=list)


class CompatibilityKnowledgeContext(BaseModel):
    """Reference context used to explain compatibility."""
    relationship_mode: str | None = None
    mode_title: str | None = None
    mode_summary: str | None = None
    sign_pair_summary: str | None = None
    elemental_dynamic: str | None = None
    modality_dynamic: str | None = None
    rulers: List[str] = Field(default_factory=list)
    themes: List[str] = Field(default_factory=list)
    stones: List[str] = Field(default_factory=list)
    life_path_pair: str | None = None


class CompatibilityDeepDive(BaseModel):
    """Deeper structured payload for UI and AI interpretation."""
    relationship_archetype: str
    strongest_axis: str | None = None
    tension_axis: str | None = None
    dimensions: List[CompatibilityDimension] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    challenges: List[str] = Field(default_factory=list)
    guidance: List[str] = Field(default_factory=list)
    knowledge: CompatibilityKnowledgeContext = Field(default_factory=CompatibilityKnowledgeContext)


class CompatibilityEditorial(BaseModel):
    """Compact editorial layer generated from structured compatibility payload."""
    mode_focus: str | None = None
    pair_thesis: str
    strengths: List[str] = Field(default_factory=list)
    tensions: List[str] = Field(default_factory=list)
    next_step: str


class EnrichedCompatibilityResponse(BaseModel):
    """Unified compatibility payload for quick and deep surfaces."""
    overall_score: int
    summary: str
    relationship_type: str | None = None
    aspects: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    synastry: Dict[str, Any] = Field(default_factory=dict)
    deep_dive: CompatibilityDeepDive | None = None
    editorial: CompatibilityEditorial | None = None
    profile_1: Optional[Dict[str, Any]] = None
    profile_2: Optional[Dict[str, Any]] = None


class SynastryReport(BaseModel):
    """Full synastry analysis report."""
    planet_aspects: List[SynastryAspect]
    angle_aspects: List[SynastryAngleAspect]
    house_overlays: List[HouseOverlay]
    strong_aspects: List[SynastryAspect]
    compatibility_summary: CompatibilitySummary


# Composite chart models
class CompositeAspect(BaseModel):
    """Aspect in composite chart."""
    planet1: str
    planet2: str
    aspect: str
    orb: float
    strength: str


class CompositeInterpretation(BaseModel):
    """Interpretation of composite chart."""
    strengths: List[str]
    tensions: List[str]
    growth_areas: List[str]
    what_holds_together: List[str]
    relationship_dynamics: str


class CompositeChart(BaseModel):
    """Composite chart (midpoint method) for relationship analysis."""
    positions: List[Dict[str, Any]]
    houses: Dict[str, Any]
    aspects: List[CompositeAspect]
    interpretation: CompositeInterpretation


class DavisonChart(BaseModel):
    """Davison chart (time-space midpoint method) for relationship analysis."""
    midpoint_date: str
    midpoint_time: str
    description: str
    # Note: Full implementation would include computed chart data


# Psych Compatibility models
class ConflictStyleAnalysis(BaseModel):
    """Analysis of conflict styles for both people."""
    person1_style: str  # "fight", "flight", "freeze", "fawn", "balanced"
    person2_style: str
    compatibility: str  # "harmonious", "balanced", "challenging"
    description: str
    recommendations: List[str]


class ClosenessAutonomyAnalysis(BaseModel):
    """Analysis of closeness vs autonomy needs."""
    person1_style: str  # "anxious", "avoidant", "secure"
    person2_style: str
    person1_needs: Dict[str, str]  # {"closeness": "high/medium/low", "autonomy": "high/medium/low"}
    person2_needs: Dict[str, str]
    insights: Dict[str, Any]
    recommendations: List[str]


class BoundaryThemesAnalysis(BaseModel):
    """Analysis of boundary themes."""
    person1_patterns: List[str]
    person2_patterns: List[str]
    themes: Dict[str, bool]  # {"control": bool, "jealousy": bool, "independence": bool}
    recommendations: List[str]


class CommunicationTechnique(BaseModel):
    """Specific communication technique with example phrases."""
    technique: str
    description: str
    example_phrases: List[str]


class PsychCompatibilityReport(BaseModel):
    """Full psychological compatibility report."""
    conflict_styles: ConflictStyleAnalysis
    closeness_autonomy: ClosenessAutonomyAnalysis
    boundary_themes: BoundaryThemesAnalysis
    communication_recommendations: List[CommunicationTechnique]
    what_you_do_perfectly: List[str]
    where_youll_argue: List[str]
    what_saves_you: List[str]
    relationship_rules: List[str]


# Children charts models
class ChildTemperament(BaseModel):
    """Child's temperament analysis."""
    sun_sign: str
    moon_sign: str
    rising_sign: str
    dominant_element: str
    modality: str
    description: str
    characteristics: List[str]


class ChildSensitivity(BaseModel):
    """Child's sensitivity and stress analysis."""
    level: str  # "low", "medium", "high"
    indicators: List[str]
    stress_triggers: List[str]
    support_strategies: List[str]


class ChildBoundaries(BaseModel):
    """Child's relationship with boundaries and discipline."""
    boundary_style: str  # "structured", "flexible", "resistant"
    discipline_approach: str
    saturn_sign: Optional[str]
    saturn_house: Optional[int]
    recommendations: List[str]


class ChildLearning(BaseModel):
    """Child's learning style and interests."""
    learning_style: str
    interests: List[str]
    mercury_sign: str
    jupiter_sign: str
    recommendations: List[str]


class ChildrenChartReport(BaseModel):
    """Full children chart report."""
    temperament: ChildTemperament
    sensitivity: ChildSensitivity
    boundaries_discipline: ChildBoundaries
    learning_interests: ChildLearning
    parental_strategies: List[str]


# Career analysis models
class WorkStyle(BaseModel):
    """Work style analysis."""
    approach: str
    mars_sign: str
    mars_house: Optional[int]
    planets_in_6th: List[str]
    description: str


class CareerMotivation(BaseModel):
    """Career motivation and meaning."""
    motivation: str
    sun_sign: str
    sun_house: Optional[int]
    mc_house: Optional[Any]
    planets_in_10th: List[str]
    purpose_statement: str


class MoneyPatterns(BaseModel):
    """Money and financial patterns."""
    attitude: str
    venus_sign: str
    venus_house: Optional[int]
    planets_in_2nd: List[str]
    recommendations: List[str]


class BurnoutRisks(BaseModel):
    """Burnout risk analysis."""
    risk_level: str  # "low", "medium", "high"
    risk_factors: List[str]
    planets_in_12th: List[str]
    prevention_strategies: List[str]


class CareerRole(BaseModel):
    """Strong career role identification."""
    role: str  # "leader", "analyst", "creator", "communicator", "versatile"
    strength: str  # "high", "medium", "low"
    description: str
    examples: List[str]


class CareerStrategies(BaseModel):
    """Career strategies for different timeframes."""
    year: str
    quarter: str
    month: str


class CareerAnalysis(BaseModel):
    """Full career analysis report."""
    work_style: WorkStyle
    motivation: CareerMotivation
    money_patterns: MoneyPatterns
    burnout_risks: BurnoutRisks
    strong_roles: List[CareerRole]
    strategies: CareerStrategies


class BusinessRoleCompatibility(BaseModel):
    """Role compatibility analysis for business partnership."""
    person1_role: str  # e.g., "leader", "analyst", "creator", "communicator"
    person2_role: str
    compatibility_score: float  # 0.0 to 1.0
    strengths: List[str] = Field(default_factory=list)  # What works well together
    challenges: List[str] = Field(default_factory=list)  # Potential conflicts
    recommendations: List[str] = Field(default_factory=list)  # How to work together


class BusinessPartnershipReport(BaseModel):
    """Business partnership compatibility report."""
    role_compatibility: List[BusinessRoleCompatibility] = Field(default_factory=list)
    structural_recommendations: List[str] = Field(default_factory=list)  # Organizational structure advice
    decision_making_style: str | None = None  # How decisions should be made
    communication_approach: List[str] = Field(default_factory=list)  # Communication recommendations
    division_of_responsibilities: List[str] = Field(default_factory=list)  # Who does what
    growth_potential: str | None = None  # Potential for business growth
    risk_factors: List[str] = Field(default_factory=list)  # What to watch out for


# Retrograde models
class PlanetaryIngress(BaseModel):
    """Planet ingress (entering a new zodiac sign)."""
    planet: str
    sign: str  # Sign the planet is entering
    ingress_date: str  # Date when ingress occurs (approximate)


class RetrogradeStatus(BaseModel):
    """Planet retrograde status for a date."""
    date: str
    retrograde_planets: List[str]  # List of planet names that are retrograde
    descriptions: Dict[str, str]  # Description for each retrograde planet
    ingresses: List[PlanetaryIngress] = Field(default_factory=list)  # Upcoming planetary ingresses


# Progressions models
class ProgressedAspect(BaseModel):
    """Aspect between progressed and natal planet."""
    progressed_planet: str
    natal_planet: str
    aspect: str
    orb: float
    description: str


class ProgressedChart(BaseModel):
    """Secondary progressed chart."""
    progression_date: str  # Date used for progression calculation
    target_date: str  # Target date for progression
    days_progressed: int  # Days since birth (equals years progressed)
    description: str
    progressed_aspects: List[ProgressedAspect] = Field(default_factory=list)  # Progressed planet aspects to natal planets


# Returns models
class SolarReturnChart(BaseModel):
    """Solar Return chart."""
    solar_return_date: str
    target_year: int
    natal_sun_position: float
    description: str
    # Note: Full implementation would include Solar Return chart data and comparison with natal


class LunarReturnChart(BaseModel):
    """Lunar Return chart."""
    lunar_return_date: str
    target_month: str
    natal_moon_position: float
    description: str
    # Note: Full implementation would include Lunar Return chart data and comparison with natal


class VulnerableSystem(BaseModel):
    """Vulnerable body system identified from chart."""
    system: str  # e.g., "nervous system", "digestive system", "circulatory system"
    astrological_indicator: str  # What in the chart indicates this (e.g., "6th house emphasis", "Mars in Virgo")
    description: str
    recommendations: List[str] = Field(default_factory=list)


class StressStyle(BaseModel):
    """How stress manifests and is managed."""
    stress_manifestation: str  # How stress shows up (physical, emotional, behavioral)
    stress_triggers: List[str] = Field(default_factory=list)
    stress_response: str  # Fight/flight/freeze/fawn pattern
    recovery_style: str  # How the person recovers from stress
    recommendations: List[str] = Field(default_factory=list)


class PsychosomaticConnection(BaseModel):
    """Connection between emotional patterns and physical symptoms."""
    emotional_pattern: str  # Emotional/psychological pattern
    physical_manifestation: str  # How it shows in the body
    astrological_connection: str  # Chart indicators
    recommendations: List[str] = Field(default_factory=list)


class HealthAnalysisReport(BaseModel):
    """Health and psychosomatic analysis report."""
    vulnerable_systems: List[VulnerableSystem] = Field(default_factory=list)
    stress_style: StressStyle | None = None
    preventive_recommendations: List[str] = Field(default_factory=list)
    psychosomatic_connections: List[PsychosomaticConnection] = Field(default_factory=list)
    lifestyle_guidance: List[str] = Field(default_factory=list)


# Group compatibility models
class GroupPairwiseSynastry(BaseModel):
    """Synastry analysis for a pair within a group."""
    person_1: str
    person_2: str
    compatibility_score: float  # 0-100
    synastry_summary: Optional[CompatibilitySummary] = None
    psych_compatibility: Optional[PsychCompatibilityReport] = None


class GroupRole(BaseModel):
    """Role a person plays in a group."""
    person_label: str
    role_type: str  # "Leader", "Mediator", "Analyst", "Strategist", "Innovator", "Contributor"
    description: str
    indicators: List[str] = Field(default_factory=list)


class GroupTensionZone(BaseModel):
    """Area of tension in a group."""
    involved_people: List[str] = Field(default_factory=list)
    description: str
    conflict_areas: List[str] = Field(default_factory=list)
    severity: str  # "low", "medium", "high"


class GroupDynamics(BaseModel):
    """Overall group dynamics analysis."""
    average_compatibility: float  # 0-100
    element_distribution: Dict[str, int] = Field(default_factory=dict)  # {"Fire": int, "Earth": int, "Air": int, "Water": int}
    balanced: bool
    strong_connections: List[List[str]] = Field(default_factory=list)  # Pairs with high compatibility [person1, person2]
    strengths: List[str] = Field(default_factory=list)
    challenges: List[str] = Field(default_factory=list)


class GroupCompatibilityReport(BaseModel):
    """Full group compatibility report for 3+ people."""
    group_size: int
    profile_labels: List[str] = Field(default_factory=list)
    pairwise_synastry: List[GroupPairwiseSynastry] = Field(default_factory=list)
    group_roles: List[GroupRole] = Field(default_factory=list)
    tension_zones: List[GroupTensionZone] = Field(default_factory=list)
    group_dynamics: GroupDynamics
    recommendations: List[str] = Field(default_factory=list)


# Rebuild models to resolve forward references
# This is needed for models that reference each other (like DailyForecast -> TransitInsight)
DailyForecast.model_rebuild()
