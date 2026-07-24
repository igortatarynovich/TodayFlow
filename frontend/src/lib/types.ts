export type BirthData = {
  date: string;
  time?: string;
  location: string;
  coordinates?: {
    latitude: number;
    longitude: number;
  };
};

export type BirthIntakePayload = {
  label: string;
  relation?: string;
  first_name?: string;
  last_name?: string;
  gender?: string;
  is_self?: boolean;
  birth_date: string;
  birth_time?: string;
  time_unknown?: boolean;
  country?: string;
  timezone_mode?: "auto" | "manual";
  timezone_name?: string;
  timezone_offset_minutes?: number;
  location: string;
  latitude?: number;
  longitude?: number;
  show_map?: boolean;
  partner_relationship?: boolean;
  is_twin?: boolean;
  notes?: string;
};

export type BirthIntakePreview = {
  normalized_label: string;
  birth_date: string;
  birth_time?: string | null;
  time_unknown?: boolean;
  timezone_name?: string | null;
  timezone_offset_minutes?: number | null;
  location: string;
  latitude?: number | null;
  longitude?: number | null;
  warnings: string[];
};

export type UserSettings = {
  email: string;
  greeting?: string | null;
  first_name?: string | null;
  last_name?: string | null;
  country?: string | null;
  language?: string | null;
  locale?: string | null;
  stay_logged_in?: boolean;
  newsletter_opt_in?: boolean;
  push_opt_in?: boolean;
  subscriptions: string[];
  astrology_level?: string | null;
  text_preference?: string | null;
  /** DE-8: quick | normal | deep — глубина текстов «Сегодня» (POST /today/narrative). */
  today_narrative_depth_level?: string | null;
  /** female | male | unspecified — для согласования русского «ты» */
  gender?: string | null;
};

/** UMTS-2 v0 — PIM read slice for all surfaces (`GET /account/compact-user-model`). */
export type CompactUserModel = {
  contract_version: string;
  as_of: string;
  generated_at: string;
  identity: {
    facts?: {
      birth_date?: string;
      birth_time_known?: boolean;
      timezone_name?: string | null;
    } | null;
    display_name?: string | null;
    sun_sign?: string | null;
    moon_sign?: string | null;
    rising_sign?: string | null;
    life_path?: number | null;
    archetype?: string | null;
    summary?: string | null;
    strengths?: string[];
    constraints?: string[];
  };
  current_state: {
    local_date?: string;
    mood_id?: string | null;
    mood_captured_at?: string | null;
    focus_topic_id?: string | null;
    focus_captured_at?: string | null;
    day_promise_text?: string | null;
    day_promise_captured_at?: string | null;
    day_focus_outcome?: string | null;
    day_focus_outcome_captured_at?: string | null;
    mood_energy?: {
      mood_id?: string | null;
      energy_level?: string | null;
      captured_at?: string | null;
    };
  };
  active_themes: Array<{ id: string; weight?: number; stability?: string; source?: string }>;
  behavioral_patterns: {
    works?: string[];
    does_not_work?: string[];
    hints?: string[];
    window_days?: number;
    total_events?: number;
  };
  knowledge_atoms_top_k: Array<{
    knowledge_id?: string;
    contract_version?: string;
    knowledge_type?: string;
    data_class?: string;
    claim?: string;
    claim_summary?: string;
    confidence?: number;
    evidence_count?: number;
    last_confirmed_at?: string;
    confirmation_required?: boolean;
  }>;
  interpretation_instances_top_k?: Array<{
    instance_id?: string;
    interpretation_ref_id?: string;
    level?: string;
    summary?: string;
    dominant_meaning?: string;
    confirmation_required?: boolean;
    evidence_count?: number;
    user_verdict?: string;
  }>;
  relationship_insights_top_k?: Array<{
    knowledge_id?: string;
    kind?: string;
    label?: string;
    summary?: string;
    domain?: string;
    confirmed_at?: string;
  }>;
  confidence: {
    overall?: number;
    by_domain?: {
      identity?: number;
      themes?: number;
      timing?: number;
      recommendations?: number;
    };
    uncertainty_flags?: string[];
    delta_30d?: number | null;
    meaning_events_28d?: number;
  };
  recommendations?: {
    primary: {
      id: string;
      text: string;
      timing_hint?: string | null;
      measurable?: string | null;
      source?: string;
      evidence_atom_ids?: string[];
      knowledge_type_gate?: string;
    };
    alternates?: Array<{
      id: string;
      text: string;
      timing_hint?: string | null;
      measurable?: string | null;
      source?: string;
      evidence_atom_ids?: string[];
      knowledge_type_gate?: string;
    }>;
  };
};

/** UMTS §3.6 — confidence trend series (`GET /account/compact-user-model/confidence-history`). */
export type CompactUserModelConfidenceHistory = {
  contract_version: string;
  as_of: string;
  window_days: number;
  start_date: string;
  end_date: string;
  points: Array<{
    snapshot_date: string;
    overall: number;
    by_domain?: {
      identity?: number;
      themes?: number;
      timing?: number;
      recommendations?: number;
    };
    meaning_events_28d?: number;
  }>;
  summary: {
    point_count: number;
    overall_min?: number | null;
    overall_max?: number | null;
    delta_window?: number | null;
  };
};

export type CoreProfile = {
  profile_version: string;
  generated_at: string;
  is_ready: boolean;
  missing_fields: string[];
  profile_hash: string;
  person: {
    first_name?: string | null;
    display_name?: string | null;
    locale?: string | null;
    /** Для согласования русского «ты» в UI (`ruUserGender.ts`). Значения: female/male и т.п. — см. парсер. */
    gender?: string | null;
  };
  astro: {
    profile_id?: number | null;
    label?: string | null;
    relation?: "self" | "partner" | "child" | "close_person" | null;
    birth_date?: string | null;
    birth_time?: string | null;
    time_unknown?: boolean | null;
    location_name?: string | null;
    sun_sign?: string | null;
    sun_element?: string | null;
    sun_modality?: string | null;
  };
  numerology: {
    full_name?: string | null;
    birth_date?: string | null;
    life_path?: number | null;
    expression?: number | null;
    soul_urge?: number | null;
    personality?: number | null;
    is_master_life_path?: boolean;
  };
  baseline: {
    archetype_seed?: string | null;
    element_focus?: string | null;
    rhythm_style?: string | null;
  };
  profiles?: {
    selected_profile_id?: number | null;
    primary_profile_id?: number | null;
    has_multiple_profiles?: boolean;
    items?: Array<{
      id: number;
      label: string;
      relation: "self" | "partner" | "child" | "close_person";
      is_primary: boolean;
      is_selected: boolean;
      birth_date?: string | null;
      birth_time?: string | null;
      time_unknown?: boolean | null;
      location_name?: string | null;
      sun_sign?: string | null;
    }>;
  } | null;
    interpretation?: {
    identity?: string;
    strengths?: string[];
    watchouts?: string[];
    sex_practical_tips?: string[];
    life_areas?: {
      love?: string;
      career?: string;
      money?: string;
      family?: string;
      sex?: string;
      kids?: string;
      body?: string;
      friends?: string;
      decisions?: string;
    };
  } | null;
  profile_contract_v1?: {
    contract_version: string;
    status?: "ready" | "forming" | "partial" | string;
    forming_message?: string | null;
    /** Step-1 share line (≤120). Optional on old snapshots; normalize may fallback. */
    recognition_line?: string;
    identity_core: string;
    strengths: string[];
    growth_zones: string[];
    relationship_style: string;
    money_style: string;
    decision_style: string;
    recurring_patterns: string[];
    living_changes?: string | null;
    life_mission?: string | null;
    helps?: string[];
    life_spheres?: Record<
      string,
      {
        how?: string;
        need?: string;
        risk?: string;
        turns_on?: string;
        turns_off?: string;
        helps?: string;
      }
    >;
    /** Step-5 connected natal reading (optional on older snapshots). */
    chart_reading?: string | null;
    methodology_note?: string | null;
    unavailable_note?: string | null;
    generation_meta?: Record<string, unknown> | null;
    profile_snapshot_version?: string | null;
  } | null;
  /**
   * Step-2 why checklist (read-path only). Not stored in Snapshot.
   * selected_by = life_path→archetype; portrait_influenced_by = sun/element/rhythm/…
   */
  portrait_why_v0?: {
    projection_version?: string;
    title?: string;
    selected_by?: Array<{
      id?: string;
      class?: "selected_by" | string;
      life_path?: number | null;
      archetype_seed?: string | null;
      label?: string;
      fact_keys?: string[];
    }>;
    portrait_influenced_by?: Array<{
      id?: string;
      class?: "portrait_influenced_by" | string;
      label?: string;
      value?: string | null;
      fact_keys?: string[];
    }>;
    omitted?: Array<{ id?: string; reason?: string; opens?: string }>;
    honesty_line?: string | null;
    rules?: {
      archetype_selected_only_by?: string;
      forbid_sun_as_archetype_cause?: boolean;
    };
  } | null;
  /**
   * Step-3 story nodes (read-path only). Projects existing Snapshot strings —
   * not a second recurring_patterns schema.
   */
  insight_nodes_v0?: {
    projection_version?: string;
    nodes?: Array<{
      id?: string;
      kind?: "tension" | "repeat" | "strength" | string;
      title?: string;
      insight?: string;
      grounded_on?: Array<{ id?: string; label?: string; fact_keys?: string[]; role?: string }>;
      help?: string | null;
      living_evidence?: string[];
      source_fields?: string[];
    }>;
    rules?: Record<string, unknown>;
  } | null;
  /**
   * Step-4 effort vector (read-path only). Derived from insight_nodes_v0.nodes[0].help.
   * Null when no safe help — never invents from life_mission / Today / astrology.
   */
  effort_vector_v0?: {
    projection_version?: string;
    effort_vector?: string | null;
    source_node_id?: string | null;
    node_kind?: string | null;
    role?: string | null;
    source_fields?: string[];
    rules?: Record<string, unknown>;
  } | null;
  /** Step-5 path bridge to Today (read-path only). Not an empty CTA / day forecast. */
  bridge_line_v0?: {
    projection_version?: string;
    bridge_line?: string | null;
    cta?: string | null;
    leads_to?: string | null;
    source_node_id?: string | null;
    node_kind?: string | null;
    source_fields?: string[];
    rules?: Record<string, unknown>;
  } | null;
  capability?: {
    resolver_version?: string;
    mode?: "none" | "date_only" | "full" | string;
    access?: "guest" | "free" | "trial" | "paid" | string;
    layers?: {
      l1?: boolean;
      l2_structure?: boolean;
      l3_in_result?: boolean;
      l3_revealed?: boolean;
      l3_depth?: boolean;
      name_numerology?: boolean;
    };
    profile_slots?: {
      data_eligible?: string[];
      revealed?: string[];
      allowed?: string[];
      access_gated?: string[];
      omitted?: string[];
      gated_l3?: string[];
    };
    user_messages?: Array<{ code?: string; text?: string }>;
    angles_eligible?: boolean;
    birth_time_unsuitable_for_angles?: boolean;
  } | null;
  profile_matrix_v0?: {
    adapter_version?: string;
    slots?: Record<string, unknown>;
    revealed_slots?: Record<string, unknown>;
    access_gated_slot_ids?: string[];
    omitted_slots?: Record<string, string>;
    capability?: CoreProfile["capability"];
  } | null;
  daily_interpretation?: {
    daily_lenses?: {
      general?: string;
      love?: string;
      career?: string;
      money?: string;
      family?: string;
    };
  } | null;
  living?: {
    summary?: string;
    signal_profile?: {
      signals_days?: number;
      closure_state?: "stable" | "fragile" | "building" | "mixed" | "unknown";
      clarity_state?: "growing" | "unclear" | "mixed" | "unknown";
      dominant_focus?: string | null;
      ritual_feedback_yes_days?: number;
      ritual_feedback_no_days?: number;
      unclear_decision_days?: number;
    } | null;
    weekly_state?: {
      week_start?: string;
      week_end?: string;
      integration_text?: string;
      signals_days?: number;
      ritual_feedback_yes_days?: number;
      ritual_feedback_no_days?: number;
      unclear_decision_days?: number;
      dominant_question_focus?: string | null;
    } | null;
    recent_insights?: Array<{
      id: string;
      date: string;
      type: string;
      text: string;
      confidence?: "low" | "medium" | "high";
    }>;
    learning_context?: {
      summary?: string;
      response_style?: string;
      support_style?: string;
      dominant_lanes?: string[];
      dominant_routes?: string[];
      dominant_diary_topics?: string[];
      signal_bias?: string;
      natal_memory?: {
        preferred_targets?: Array<{
          target?: string;
          score?: number;
          opened?: number;
          completed?: number;
        }>;
        best_houses?: Array<{
          source_key?: string;
          target?: string;
          score?: number;
          opened?: number;
          completed?: number;
        }>;
        best_planets?: Array<{
          source_key?: string;
          target?: string;
          score?: number;
          opened?: number;
          completed?: number;
        }>;
        best_aspects?: Array<{
          source_key?: string;
          target?: string;
          score?: number;
          opened?: number;
          completed?: number;
        }>;
        best_editorial_targets?: Array<{
          source_key?: string;
          target?: string;
          score?: number;
          opened?: number;
          completed?: number;
        }>;
      } | null;
      stats?: {
        helpful_answers?: number;
        unclear_answers?: number;
        routes_opened?: number;
        routes_completed?: number;
        bridge_actions?: number;
        natal_actions?: number;
        diary_entries?: number;
        signal_days?: number;
      };
    } | null;
  } | null;
};

export type ProfileSummary = {
  generated_at: string;
  profile_hash: string;
  is_ready: boolean;
  missing_fields: string[];
  display_name?: string | null;
  core_trio: {
    sun_sign?: string | null;
    birth_time_known?: boolean | null;
    life_path?: number | null;
  };
  baseline: {
    archetype_seed?: string | null;
    element_focus?: string | null;
    rhythm_style?: string | null;
  };
  rings_preview: Record<string, number>;
  living_summary?: string | null;
};

export type ProfileBuildStatus = {
  status: "queued" | "building" | "ready";
  is_ready: boolean;
  profile_hash: string;
  generated_at: string;
  missing_fields: string[];
  has_snapshot: boolean;
};

export type MeaningEventType =
  | "habit_completed"
  | "ascetic_step_done"
  | "practice_completed"
  | "diary_entry"
  | "reflection_answer"
  | "guidance_ask"
  | "guidance_clarify"
  | "tarot_spread_done"
  | "tarot_session_started"
  | "tarot_question_domain_selected"
  | "tarot_question_refined"
  | "tarot_spread_selected"
  | "tarot_question_submitted"
  | "tarot_reading_resonance"
  | "tarot_reading_follow_up"
  | "tarot_deepen_started"
  | "compatibility_view"
  | "compatibility_encyclopedia_view"
  | "compatibility_topic_select"
  | "compatibility_echo"
  | "compatibility_scenario_switch"
  | "compatibility_deep_open"
  | "compatibility_attachment_confirm"
  | "cycle_log"
  | "affirmation_done"
  | "self_awareness_question"
  | "consistency_bonus"
  | "day_opened"
  | "day_soft_checkin"
  | "day_sky_fact_viewed"
  | "tarot_selected"
  | "tarot_revealed"
  | "number_selected"
  | "first_synthesis_viewed"
  | "mood_selected"
  | "head_topic_selected"
  | "sphere_opened"
  | "sphere_feedback"
  | "action_option_selected"
  | "focus_started"
  | "focus_completed"
  | "support_selected"
  | "goal_created"
  | "habit_created"
  | "evening_reflection_submitted"
  | "today_narrative_depth_changed"
  | "today_guide_why_opened"
  | "today_day_history_first_visible"
  | "today_ring_open"
  | "today_micro_reflection"
  | "today_habit_toggle"
  | "core_loop_viability_surface_visible"
  | "onboarding_intent_selected"
  | "onboarding_reality_selected"
  | "onboarding_recognition_shown"
  | "day_focus_outcome"
  | "profile_atom_correction"
  | "interpretation_instance_confirm";

export type MeaningEventSource = "today" | "flow" | "insight" | "compatibility" | "profile" | "onboarding";

export type MeaningEventInput = {
  event_id?: string | null;
  event_type: MeaningEventType;
  event_source: MeaningEventSource;
  event_time?: string | null;
  local_date?: string | null;
  quality_score?: number;
  payload?: Record<string, unknown> | null;
  idempotency_key: string;
};

export type MeaningRingsResponse = {
  window_days: number;
  generated_at: string;
  rings: Array<{
    ring: "Mind" | "Body" | "Love" | "Wealth" | "Purpose" | "Energy";
    score: number;
    trend_7d: number;
    confidence: "low" | "medium" | "high";
    top_contributors: string[];
  }>;
};

export type AstroProfile = {
  id: number;
  label: string;
  relation?: "self" | "partner" | "child" | "close_person";
  birth_date: string;
  birth_time?: string | null;
  time_unknown?: boolean;
  location_name?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  is_primary?: boolean;
  /** Сколько раз уже менялись дата/время/место рождения (PUT); название роли не считается. */
  birth_facts_corrections_used?: number;
  birth_facts_corrections_max?: number;
  birth_facts_corrections_remaining?: number;
  /** Сколько секунд ждать до следующего изменения даты/времени/места; 0 — можно менять. */
  birth_facts_cooldown_remaining_seconds?: number;
};

/** Ответ POST/PUT /account/astro-data и POST /account/astro-data/:id/primary после сохранения и прогрева натала. */
export type AstroProfileSaveResponse = AstroProfile & {
  timezone_offset_minutes?: number | null;
  timezone_name?: string | null;
  notes?: string | null;
  created_at?: string | null;
  core_profile: CoreProfile;
};

export type Interpretation = {
  paragraph_id: string;
  variant_id: string;
  text: string;
  section: string;
  meaning_type?: string;
};

export type ChartSnapshot = {
  sun: string;
  moon: string;
  rising: string;
  houses?: Record<string, unknown>;
};

export type LiteReport = {
  summary: ChartSnapshot;
  paragraphs: Interpretation[];
  internal_model?: InternalModelSnapshot;
  content_version: string;
  chart_positions?: Record<string, unknown>[];
  aspects?: AspectResponse;
};

export type InsightDepthTier = "free" | "pro" | "premium";

/** Биллинг: free | lite (Plus и т.п.) | pro (Full и т.п.) — с бэкенда get_subscription_snapshot */
export type SubscriptionBillingLevel = "free" | "lite" | "pro";

export type AccountProfile = {
  user_id: number;
  email: string;
  is_admin?: boolean;
  is_paid: boolean;
  has_lite_report: boolean;
  has_full_report: boolean;
  subscription_level?: SubscriptionBillingLevel;
  /** Активный plan_id из Stripe / checkout (если есть подписка) */
  active_plan_id?: string | null;
  /** active | trialing или null, если подписки нет */
  subscription_status?: string | null;
  /** Глубина инсайтов на «Сегодня» (см. spec/product/INSIGHT_DEPTH_MODEL.md) */
  insight_depth_tier?: InsightDepthTier;
};

export type GeocodeResult = {
  name: string;
  local_name?: string | null;
  display_name?: string | null;
  country: string;
  latitude: number;
  longitude: number;
};

export type JTBDLane =
  | "love"
  | "money_career"
  | "self"
  | "future"
  | "decision"
  | "daily"
  | "state"
  | "pattern";

export type QuestionAnswerResponse = {
  generation_log_id?: number | null;
  question: string;
  lane: JTBDLane;
  lane_title: string;
  profile_ready: boolean;
  answer: {
    clarity: string;
    explanation: string;
    forecast: string;
    decision: string;
    today: string;
  };
  suggested_route: {
    href: string;
    label: string;
    reason: string;
  };
  editorial?: {
    current_focus: string;
    carried_context?: string | null;
    next_step: string;
  } | null;
  memory_context?: {
    lane: string;
    question_signature: string;
    repeated_questions_count: number;
    prior_summary?: string | null;
    focus_hint?: string | null;
    history: Array<{
      question: string;
      thesis?: string | null;
      next_step?: string | null;
    }>;
  } | null;
};

export type DecisionAnswerResponse = {
  generation_log_id?: number | null;
  question: string;
  profile_ready: boolean;
  option_a?: string | null;
  option_b?: string | null;
  answer: {
    window: string;
    risk: string;
    best_next_step: string;
    check_before_deciding: string;
    revisit_when: string;
  };
  suggested_route: {
    href: string;
    label: string;
    reason: string;
  };
  editorial?: {
    current_focus: string;
    carried_context?: string | null;
    next_step: string;
  } | null;
  memory_context?: {
    lane: string;
    question_signature: string;
    repeated_questions_count: number;
    prior_summary?: string | null;
    focus_hint?: string | null;
    history: Array<{
      question: string;
      thesis?: string | null;
      next_step?: string | null;
    }>;
  } | null;
};

export type QuestionsHubContextResponse = {
  preferred_lane?: JTBDLane | null;
  summary: string;
  lane_suggestions: Array<{
    lane: JTBDLane;
    count: number;
    last_question?: string | null;
    last_thesis?: string | null;
    focus_hint?: string | null;
  }>;
};

export type QuestionsHistoryItem = {
  generation_log_id: number;
  created_at: string;
  mode: "question" | "decision" | "guidance" | "guidance_clarify" | string;
  lane?: string | null;
  question: string;
  focus?: string | null;
  next_step?: string | null;
  route_label?: string | null;
  surface?: string | null;
  spread_id?: string | null;
  topic?: string | null;
  lead_card_name?: string | null;
  lead_card_orientation?: string | null;
};

export type QuestionsHistoryResponse = {
  history: QuestionsHistoryItem[];
};

export type AxisValue = {
  axis_id: string;
  value: number;
  confidence?: string;
};

export type ModulatorValue = {
  modulator_id: string;
  value: number;
  confidence?: string;
};

export type InternalModelSnapshot = {
  axes: AxisValue[];
  modulators: ModulatorValue[];
  mode?: string;
};

export type ZodiacReference = {
  id: string;
  name: string;
  start: string;
  end: string;
  element: string;
  modality: string;
  themes: string[];
  stones?: string[];
};

export type HouseReference = {
  id: string;
  name: string;
  description: string;
  number?: number;
};

export type Mantra = {
  id: string;
  title: string;
  intention: string;
  human_text?: string | null;
  axes: string[];
  mantra: string;
  pronunciation: string;
  breath_count?: number;
  guidance: string;
  stones?: string[];
  best_for_phases?: string[];
  notes?: string;
};

export type Ritual = {
  id: string;
  title: string;
  duration_minutes?: number;
  intention: string;
  axes: string[];
  ingredients?: string[];
  instructions?: string[];
  pair_with?: string[];
  best_for_phases?: string[];
  notes?: string;
};

export type TarotCard = {
  id: number;
  name: string;
  keywords: string[];
  upright: string;
  reversed: string;
  correspondences: Record<string, unknown>;
};

export type TarotDailyDraw = {
  date: string;
  /** not_selected = identity must not be shown; selected = card fields present */
  selection_status?: "not_selected" | "selected" | string;
  card?: TarotCard | null;
  orientation?: string | null;
  mantra?: Mantra | null;
  ritual?: Ritual | null;
};

export type TarotHistoryResponse = {
  today: TarotDailyDraw;
  history: TarotDailyDraw[];
  streak_days: number;
};

export type TarotSpreadRequest = {
  spread_id?: string | null;
};

export type TarotSpreadPosition = {
  id: string;
  title: string;
  prompt?: string;
};

export type TarotSpreadCard = {
  position: TarotSpreadPosition;
  card: TarotCard;
  orientation: string;
  meaning: string;
  mantra?: Mantra | null;
  ritual?: Ritual | null;
};

export type TarotSpreadResult = {
  spread_id: string;
  title: string;
  description?: string;
  cards: TarotSpreadCard[];
  human_text?: string | null;
};

export type TarotSpreadRecord = {
  draw_date: string;
  created_at?: string | null;
  spread: TarotSpreadResult;
};

export type TarotSpreadHistoryResponse = {
  history: TarotSpreadRecord[];
};

export type TarotReminderSettings = {
  enabled: boolean;
  timezone: string;
  hour: number;
  minute: number;
  next_run_at?: string | null;
  last_sent_at?: string | null;
};

export type TarotFavoritesResponse = {
  favorites: number[];
};

export type TarotFavoriteUpdate = {
  card_id: number;
  favorite: boolean;
};

export type MoonPhaseSnapshot = {
  human_text?: string | null;
  id: string;
  name: string;
  keywords: string[];
  themes: string;
  guidance: string;
  angle_degrees: number;
  cycle_day: number;
  cycle_percent: number;
};

export type UpcomingPhase = {
  id: string;
  name: string;
  date: string;
  in_days: number;
};

export type MoonPhaseResponse = {
  current: MoonPhaseSnapshot;
  next_phase: UpcomingPhase;
  upcoming: UpcomingPhase[];
};

export type PlanetEvent = {
  id: string;
  planet: string;
  event_type: string;
  timestamp: string;
  description?: string;
  sign?: string;
  aspect?: string;
  keywords: string[];
  human_text?: string | null;
};

export type PlanetaryWindow = {
  id: string;
  planet: string;
  window_type: string;
  status: "active" | "upcoming";
  start_timestamp: string;
  end_timestamp: string;
  label?: string | null;
  sign?: string | null;
  description?: string | null;
  keywords: string[];
};

export type PlanetaryTimeline = {
  upcoming: PlanetEvent[];
  windows?: PlanetaryWindow[];
};

export type TransitHighlight = {
  id: string;
  title: string;
  description?: string;
  timestamp?: string;
  kind: string;
  meta?: string | null;
  tags: string[];
};

export type TransitFeedResponse = {
  focus: MoonPhaseResponse;
  highlights: TransitHighlight[];
  events: PlanetEvent[];
  windows: PlanetaryWindow[];
};

export type CheckInPrompt = {
  id: string;
  prompt: string;
  reflection_steps: string[];
  mantra?: Mantra | null;
  ritual?: Ritual | null;
  cta?: string | null;
};

export type CheckInResponse = {
  prompt: CheckInPrompt;
};

export type WeeklyInsight = {
  phase_id: string;
  phase_name: string;
  axis_id?: string | null;
  axis_label?: string | null;
  title: string;
  summary: string;
  cta?: string | null;
  keywords?: string[] | null;
  human_text?: string | null;  // Human-readable text from Content System
};

export type WeeklyInsightResponse = {
  insight: WeeklyInsight;
  next_phase?: UpcomingPhase | null;
};

export type AspectCallout = {
  aspect_id: string;
  label: string;
  bodies: string;
  keywords: string[];
  description: string;
  tension_level: string;
  polarity: string;
  degrees_apart: number;
  orb_delta: number;
  strength: string;
  axes?: string[];
  modulators?: string[];
  section?: string | null;
  integration?: string | null;
};

export type AspectResponse = {
  callouts: AspectCallout[];
};

export type ShareableSnippet = {
  paragraph_id: string;
  section: string;
  text: string;
  meaning_type?: string | null;
};

export type NumerologyNumber = {
  title: string;
  value: number;
  reduced_value: number;
  is_master: boolean;
  summary: string;
};

export type NumerologyProfile = {
  name: string;
  birth_date: string;
  life_path: NumerologyNumber;
  expression: NumerologyNumber;
  soul_urge: NumerologyNumber;
  personality: NumerologyNumber;
};

export type NumerologyDailyInsight = {
  date: string;
  number: NumerologyNumber;
};

export type SubscriptionPlan = {
  name: string;
  features: string[];
};

export type SubscriptionPlansResponse = {
  plans: Record<string, SubscriptionPlan>;
};

export type Subscription = {
  id: number;
  plan_id: string;
  status: string;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  trial_start?: string | null;
  trial_end?: string | null;
};

export type SubscriptionsListResponse = {
  subscriptions: Subscription[];
};

export type SubscriptionHistoryItem = {
  id: number;
  subscription_id: number;
  amount: number;
  currency: string;
  status: string;
  period_start: string;
  period_end: string;
  created_at: string;
  stripe_invoice_id?: string | null;
};

export type SubscriptionHistoryResponse = {
  history: SubscriptionHistoryItem[];
};

export type CreateCheckoutResponse = {
  session_id: string;
  checkout_url: string;
  mode?: string;
};

export type ChineseHoroscope = {
  animal: string;
  element: string;
  chinese_year: number;
  description: string;
  traits: string[];
  compatibility: string[];
};

export type ZoroastrianHoroscope = {
  month: string;
  day: string;
  description: string;
  traits: string[];
  deity: {
    name: string;
    domain: string;
    symbol: string;
  };
};

export type TibetanHoroscope = {
  animal: string;
  element: string;
  mewa: string;
  year: number;
  description: string;
  traits: string[];
  mewa_meaning: string;
};

export type AllHoroscopesResponse = {
  chinese: ChineseHoroscope;
  zoroastrian: ZoroastrianHoroscope;
  tibetan: TibetanHoroscope;
  vedic?: {
    sun: string;
    moon: string;
    summary: string;
    traits: string[];
  };
  astrology?: {
    sun?: string | null;
    moon?: string | null;
    rising?: string | null;
    description: string;
  };
  numerology?: {
    life_path: number;
    life_path_summary: string;
    expression: number;
    expression_summary: string;
  };
};

// Report History Types
export type ReportHistoryItem = {
  id: number;
  profile_id: number | null;
  product_type: string; // "lite" | "full"
  content_version: string;
  created_at: string;
  profile_label: string | null;
};

export type ReportHistoryResponse = {
  history: ReportHistoryItem[];
  total: number;
};

export type PracticeHistoryItem = {
  id: number;
  practice_id: string;
  practice_title?: string | null;
  category?: string | null;
  completed_at: string; // ISO format datetime string
  is_personalized: boolean;
  sequence_id?: string | null;
  step_number?: number | null;
};

export type PracticeHistoryResponse = {
  history: PracticeHistoryItem[];
  total: number;
};

export type CategoryProgress = {
  category: string;
  total_completed: number;
  personalized_completed: number;
};

export type PracticeProgressResponse = {
  total_completed: number;
  personalized_completed: number;
  general_completed: number;
  by_category: CategoryProgress[];
  current_streak_days: number;
  longest_streak_days: number;
  weeks_active: number;
};

export type JournalAnalyticsResponse = {
  total_entries: number;
  wishes_count: number;
  gratitude_count: number;
  entries_by_type: {
    wish: number;
    gratitude: number;
  };
  activity_by_month: Array<{
    month: string;
    wishes: number;
    gratitude: number;
  }>;
  activity_by_week: Array<{
    week: string;
    wishes: number;
    gratitude: number;
  }>;
  recent_activity_days: number;
  most_common_words: Array<{
    word: string;
    count: number;
  }>;
  avg_entries_per_week: number;
};

export type FullReportSection = {
  section: string;
  paragraphs: Interpretation[];
};

export type PsychologicalPattern = {
  pattern_type: string;
  title: string;
  description: string;
  astro_indicators: string[];
  insights: string[];
  recommendations?: string[] | null;
};

export type PsychologicalLayer = {
  attachment_needs: PsychologicalPattern[];
  defense_mechanisms: PsychologicalPattern[];
  cognitive_patterns: PsychologicalPattern[];
  relational_style: PsychologicalPattern[];
  emotional_regulation: PsychologicalPattern[];
  behavioral_scenarios: PsychologicalPattern[];
};

export type FullReport = {
  summary: ChartSnapshot;
  internal_model: InternalModelSnapshot;
  sections: FullReportSection[];
  content_version: string;
  tarot_spreads?: TarotSpreadRecord[];
  psychological_layer?: PsychologicalLayer | null;
  chart_positions?: Record<string, unknown>[];
  aspects?: AspectResponse;
};

export type ThematicReport = {
  theme: string; // "career", "love", "family", "children"
  summary: ChartSnapshot;
  internal_model: InternalModelSnapshot;
  sections: FullReportSection[];
};
