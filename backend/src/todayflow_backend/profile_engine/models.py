"""Domain contracts for the Profile Engine (birth → interpretation → living → prompt slices).

These models describe the target shape. Persistence may stay JSON (e.g. CoreProfileSnapshot.payload)
until tables are split; code should converge on this structure.

Rules:
- ProfileFacts: deterministic outputs only (no LLM).
- Interpretation modules: LLM prose + structured tags; versioned and rebuildable.
- InternalPromptProfile: compact slots for prompts; never shown raw to users.
- Living layer: events → signals → patterns with confidence and decay.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def _utc_naive_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ProfilePromptSurface(str, Enum):
    """Which product surface is asking for profile context."""

    TODAY = "today"
    GUIDANCE = "guidance"
    COMPATIBILITY = "compatibility"
    FLOW = "flow"
    PRACTICE = "practice"
    GOAL = "goal"
    EVENING = "evening"


class ProfileTaskType(str, Enum):
    """Fine-grained reason for a generation call (Profile Selector step 1).

    Same human can need different slices of the profile for different tasks.
    """

    TODAY_SUMMARY = "today_summary"
    TODAY_SPHERES = "today_spheres"
    TODAY_ACTION = "today_action"
    GUIDANCE_QUESTION = "guidance_question"
    COMPATIBILITY = "compatibility"
    FLOW_ACTION = "flow_action"
    EVENING_REFLECTION = "evening_reflection"


class ProfileTopicDomain(str, Enum):
    """Domain for gating modules (Profile Selector step 2)."""

    RELATIONSHIPS = "relationships"
    INTIMACY = "intimacy"
    MONEY = "money"
    WORK = "work"
    FAMILY = "family"
    BODY_ENERGY = "body_energy"
    DECISION = "decision"
    INNER_STATE = "inner_state"
    HABITS_DISCIPLINE = "habits_discipline"
    GENERAL = "general"


class UserOperatingMode(str, Enum):
    """Inferred or explicit user state (Profile Selector step 3)."""

    ANXIETY = "anxiety"
    OVERLOAD = "overload"
    FATIGUE = "fatigue"
    RESOURCE = "resource"
    UNCERTAINTY = "uncertainty"
    RESISTANCE = "resistance"
    HIGH_IMPULSE = "high_impulse"
    AVOIDANCE = "avoidance"
    NEUTRAL = "neutral"


class AssertionSource(str, Enum):
    """Origin of a profile claim (for confidence / weighting)."""

    NATAL = "natal"
    NUMEROLOGY = "numerology"
    BEHAVIOR = "behavior"
    SELF_REPORT = "self_report"
    TRANSIT = "transit"
    AGGREGATED_PATTERN = "aggregated_pattern"


class ProfileContentKind(str, Enum):
    """Split prose roles so LLM outputs stay separable in storage and UI."""

    DESCRIPTION = "description"
    INSTRUCTION = "instruction"
    CONSTRAINT = "constraint"
    RATIONALE = "rationale"


class PrivacyExposure(str, Enum):
    """How sensitive structured or text outputs may be shown."""

    PUBLIC_UI = "public_ui"
    ON_DEMAND = "on_demand"
    INTERNAL_ONLY = "internal_only"


class BirthTimePrecision(str, Enum):
    """How much we trust angles, houses, exact Moon degree, etc."""

    EXACT = "exact"  # known time + timezone
    WINDOW = "window"  # approximate interval
    UNKNOWN = "unknown"
    RECTIFIED = "rectified"  # user or pro marked as corrected


class ConfidenceScalar(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ModuleRef(BaseModel):
    """Pointer to a stored interpretation module (for versioning and partial rebuild)."""

    module_id: str
    module_version: str
    content_hash: str | None = None
    generated_at: datetime | None = None


class ProfileFacts(BaseModel):
    """Step 0 — deterministic core from birth data + ephemeris (no LLM).

    `chart` / `numerology_raw` stay flexible: align with CachedNatalChart and numerology JSON.
    """

    astro_profile_id: int
    computed_at: datetime = Field(default_factory=_utc_naive_now)
    birth_time_precision: BirthTimePrecision
    timezone_name: str | None = None
    timezone_offset_minutes: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    location_label: str | None = None
    chart: dict[str, Any] = Field(default_factory=dict)
    numerology_raw: dict[str, Any] = Field(default_factory=dict)
    derived_tags: list[str] = Field(
        default_factory=list,
        description="Deterministic tags, e.g. dominant_element, stellium_h10",
    )


class NatalPointInterpretation(BaseModel):
    """Three-level copy for a planet / angle / point (user-visible module)."""

    label: str
    meaning: str
    life_manifestation: str
    how_to_use: str


class CoreSynthesis(BaseModel):
    """Step 1 — short synthesis object (may be LLM or hybrid)."""

    primary_archetype: str | None = None
    supporting_archetypes: list[str] = Field(default_factory=list)
    base_rhythm: str | None = None
    main_strength: str | None = None
    main_tension: str | None = None
    decision_style: str | None = None
    core_conflict: str | None = None
    module_ref: ModuleRef | None = None


class PromptProfileSlot(BaseModel):
    """One compact behavioral slot for LLM system context."""

    key: str
    value: str
    confidence: ConfidenceScalar = ConfidenceScalar.MEDIUM
    sources: list[str] = Field(default_factory=list, description="e.g. living:state_check_in, module:relationship")


class InternalPromptProfile(BaseModel):
    """Compiled, short profile for API prompts (not for direct UI)."""

    slots: list[PromptProfileSlot] = Field(default_factory=list)
    avoid_phrases: list[str] = Field(default_factory=list)
    best_action_format: str | None = None
    risk_flags: list[str] = Field(default_factory=list)
    module_ref: ModuleRef | None = Field(default=None, description="compiler output version")
    compiled_at: datetime | None = None
    tone: str | None = Field(default=None, description="e.g. direct_supportive, soft")
    depth: str | None = Field(default=None, description="short | medium | deep")
    rationale_visibility: str | None = Field(default=None, description="hidden | on_demand | inline")


class StructuredClaim(BaseModel):
    """Single interpretive line with uncertainty and applicability (core quality layer)."""

    text: str
    confidence: ConfidenceScalar = ConfidenceScalar.MEDIUM
    sources: list[AssertionSource] = Field(default_factory=list)
    works_when: str | None = Field(default=None, description="When this claim is a good fit")
    fails_when: str | None = Field(default=None, description="When to down-weight or skip")
    contradicts_module_ids: list[str] = Field(default_factory=list)
    privacy: PrivacyExposure = PrivacyExposure.PUBLIC_UI
    content_kind: ProfileContentKind = ProfileContentKind.DESCRIPTION


class AntiPattern(BaseModel):
    """What reliably fails for this user (prompt and product guardrails)."""

    key: str
    label: str
    detail: str | None = None
    evidence_hint: str | None = Field(default=None, description="Why we believe this, without raw PII")
    confidence: ConfidenceScalar = ConfidenceScalar.MEDIUM


class DecisionLoopProfile(BaseModel):
    """How the person moves from trigger to action (Flow / Guidance)."""

    trigger_to_doubt: str | None = None
    doubt_to_check: str | None = None
    check_to_decision: str | None = None
    decision_to_action: str | None = None
    action_to_integrate: str | None = None
    typical_stuck_stage: str | None = Field(
        default=None,
        description="e.g. between doubt and decision",
    )
    minimal_viable_step: str | None = None
    module_ref: ModuleRef | None = None


class ActionDurationBand(str, Enum):
    MICRO = "5"
    SHORT = "20"
    BLOCK = "60"
    OPEN = "open"


class ActionKind(str, Enum):
    CONVERSATION = "conversation"
    WRITING = "writing"
    PHYSICAL = "physical"
    PREP = "prep"
    REFLECTION = "reflection"


class SpecificityLevel(str, Enum):
    ONE_LINE = "one_line"
    CHECKLIST = "checklist"
    SCRIPT = "script"


class ActionContext(str, Enum):
    MORNING = "morning"
    EVENING = "evening"
    ALONE = "alone"
    WITH_OTHERS = "with_others"
    WORK = "work"
    ANY = "any"


class ActionFitProfile(BaseModel):
    """Formats of actions that actually get done (Today / Flow)."""

    preferred_duration_bands: list[ActionDurationBand] = Field(default_factory=list)
    action_kinds_ok: list[ActionKind] = Field(default_factory=list)
    specificity: SpecificityLevel = SpecificityLevel.ONE_LINE
    contexts_ok: list[ActionContext] = Field(default_factory=list)
    notes: str | None = None
    module_ref: ModuleRef | None = None


class ContextModeProfile(BaseModel):
    """Sub-profile keyed by situation (stress, work, relationship, …)."""

    mode_key: str = Field(..., description="e.g. stress_mode_profile, work_mode_profile")
    summary: str | None = None
    active_when: str | None = Field(default=None, description="Human-readable activation condition")
    slots: list[PromptProfileSlot] = Field(default_factory=list)


class TimingHorizon(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    LONG_CYCLE = "long_cycle"


class TimingWindow(BaseModel):
    """Operational timing hint (not a full ephemeris)."""

    horizon: TimingHorizon
    label: str
    guidance: str | None = None
    confidence: ConfidenceScalar = ConfidenceScalar.MEDIUM


class CausalChainLink(BaseModel):
    """Explicit factor → pattern → life effect (for reuse, not one-off LLM)."""

    cause_label: str
    pattern_label: str
    effect_label: str
    confidence: ConfidenceScalar = ConfidenceScalar.MEDIUM


class ProfileVersionStage(str, Enum):
    """Coarse lifecycle of profile richness (versioning narrative)."""

    V1_BIRTH_ONLY = "v1_birth_only"
    V2_INITIAL_BEHAVIOR = "v2_initial_behavior"
    V3_STABLE_LIVING = "v3_stable_living"


class ProfileRevisionNote(BaseModel):
    """What changed between profile compilations and why."""

    changed_keys: list[str] = Field(default_factory=list)
    reason: str
    at: datetime = Field(default_factory=_utc_naive_now)
    rollback_token: str | None = None


class FeedbackOutcome(str, Enum):
    """Outcome relative to a recommendation (Outcome Feedback layer)."""

    SHOWN = "shown"
    OPENED = "opened"
    SELECTED = "selected"
    DONE = "done"
    DISMISSED = "dismissed"
    NEGATIVE_SIGNAL = "negative_signal"
    EVENING_CONFIRMED = "evening_confirmed"
    EVENING_REJECTED = "evening_rejected"


class SelectorFeedbackEvent(BaseModel):
    """Tie selector choices to downstream outcomes for weight learning."""

    selector_output_id: str | None = None
    task: ProfileTaskType
    topic: ProfileTopicDomain | None = None
    mode: UserOperatingMode | None = None
    modules_used: list[str] = Field(default_factory=list)
    advice_summary: str | None = None
    outcome: FeedbackOutcome
    observed_at: datetime = Field(default_factory=_utc_naive_now)
    payload: dict[str, Any] = Field(default_factory=dict)


class GenerationRules(BaseModel):
    """Rules passed to the LLM after selection (length, tone, must/avoid)."""

    tone: str | None = None
    depth: str | None = None
    max_actions: int = 2
    must_include: list[str] = Field(default_factory=list)
    must_avoid: list[str] = Field(default_factory=list)


class ProfileSelectorOutput(BaseModel):
    """Compact prompt context after task → topic → mode → modules → weights (step 6)."""

    task: ProfileTaskType
    topic: ProfileTopicDomain
    current_mode: UserOperatingMode = UserOperatingMode.NEUTRAL
    relevant_profile: dict[str, Any] = Field(
        default_factory=dict,
        description="Small dict: decision_style, stress_response, action_fit, avoid, etc.",
    )
    recent_signals: list[str] = Field(default_factory=list)
    generation_rules: GenerationRules = Field(default_factory=GenerationRules)
    module_refs_used: list[ModuleRef] = Field(default_factory=list)
    overall_confidence: ConfidenceScalar = ConfidenceScalar.MEDIUM
    debug_trace: dict[str, Any] | None = Field(
        default=None,
        description="Optional: which blocks were considered, for logging (not for clients by default)",
    )


class GoalsAndConstraints(BaseModel):
    """Reality layer: what the person is aiming at and what bounds advice."""

    active_goals: list[str] = Field(default_factory=list, description="1–3 short goal lines")
    constraints: list[str] = Field(default_factory=list, description="time, caregiving, work — non-clinical")
    resources: list[str] = Field(default_factory=list, description="support, time, money — coarse")


class LivingObservation(BaseModel):
    """Single user or system event (pre-pattern)."""

    event_type: str
    observed_at: datetime
    local_date: date | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    weight: float = 1.0


class LivingPattern(BaseModel):
    """Aggregated pattern with evidence (post-threshold)."""

    pattern_key: str
    summary: str
    evidence_count: int
    last_seen_at: datetime
    confidence: ConfidenceScalar
    decay_score: float = Field(1.0, ge=0.0, le=1.0)
    contradictions: list[str] = Field(default_factory=list)


class ProfileContextSelectorInput(BaseModel):
    """Input to pick which modules/slices go into a generation call."""

    surface: ProfilePromptSurface
    task: ProfileTaskType | None = Field(
        default=None,
        description="If set, overrides coarse routing from surface alone",
    )
    locale: str = "ru"
    user_question: str | None = None
    topic: ProfileTopicDomain | None = None
    topic_freeform: str | None = Field(
        default=None,
        description="Legacy / extractor output before mapped to ProfileTopicDomain",
    )
    current_mode: UserOperatingMode | None = Field(
        default=None,
        description="Explicit mode; if None, selector may infer from recent signals",
    )
    second_astro_profile_id: int | None = None
    active_goal_ids: list[str] = Field(default_factory=list)
    recent_local_dates: list[date] = Field(default_factory=list)
    goals_and_constraints: GoalsAndConstraints | None = None


# --- Lifecycle matrix (documentation via constants; not enforced at runtime) ---

COMPUTE_ONCE_KEYS = frozenset(
    {
        "profile_facts",
        "natal_positions",
        "houses",
        "aspects",
        "numerology_core",
    }
)

DAILY_DERIVED_KEYS = frozenset(
    {
        "personal_year_day_month",
        "transit_snapshot_for_date",
        "lunar_phase_today",
    }
)

EVENT_DRIVEN_KEYS = frozenset(
    {
        "living_observations",
        "living_patterns",
        "internal_prompt_profile",
        "interpretation_modules",
    }
)

# Default signal priority (Profile Selector step 5): higher index = lower default weight.
# Product code may override per user after feedback learning.
SIGNAL_WEIGHT_ORDER: tuple[str, ...] = (
    "direct_self_report_today",
    "behavior_last_7d",
    "evening_closure",
    "repeating_patterns_30d",
    "birth_natal_numerology",
    "generic_archetype_fallback",
)
