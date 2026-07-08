/**
 * Cross-section PIM interaction loop — canon: PERSONAL_INTELLIGENCE_LAYER.md §3.1–§3.2
 *
 * Every surface: read CUM slice → product output → learning output → write back.
 * Not an evening-only questionnaire.
 */

export type PimSection = "today" | "tarot" | "compatibility" | "profile" | "calendar";

export type MicroSignalKind =
  | "mood"
  | "focus"
  | "ritual_tarot"
  | "ritual_number"
  | "promise"
  | "promise_outcome"
  | "evening_highlight"
  | "interpretation_confirm"
  | "tarot_question"
  | "compat_scenario"
  | "profile_correction";

/** Max explicit asks per single surface session (PIL MS6). */
export const MICRO_SIGNAL_SESSION_BUDGET = 3;

/** Default staleness before re-asking explicit state (PIL MS3). */
export const MICRO_SIGNAL_STALE_MS: Partial<Record<MicroSignalKind, number>> = {
  mood: 18 * 60 * 60 * 1000,
  focus: 24 * 60 * 60 * 1000,
};

export type SectionTouchpoint = {
  id: string;
  /** CUM / profile fields consumed for personalization */
  reads: string[];
  /** Primary event_type written on explicit interaction */
  learnEvent?: string;
};

/** Canonical touchpoints — implementation must cover these over time (web + iOS + Android). */
export const SECTION_TOUCHPOINTS: Record<PimSection, SectionTouchpoint[]> = {
  today: [
    { id: "foundation", reads: ["day_theme", "atoms_top_k", "rhythm"], learnEvent: undefined },
    { id: "mood", reads: ["last_mood", "energy_pattern"], learnEvent: "mood_selected" },
    { id: "focus", reads: ["intent_active", "head_topic"], learnEvent: "head_topic_selected" },
    { id: "tarot_ritual", reads: ["focus_topic", "atoms_top_k"], learnEvent: "tarot_selected" },
    { id: "number_ritual", reads: ["tarot_pick", "numerology_day"], learnEvent: "number_selected" },
    { id: "practice", reads: ["mood", "focus", "tarot_impact"], learnEvent: "practice_completed" },
    { id: "promise", reads: ["focus", "day_theme"], learnEvent: "action_option_selected" },
    { id: "evening_close", reads: ["day_promise", "day_theme"], learnEvent: "day_focus_outcome" },
  ],
  tarot: [
    { id: "session", reads: ["intent_history"], learnEvent: "tarot_session_started" },
    { id: "domain", reads: ["active_concerns"], learnEvent: "tarot_question_domain_selected" },
    { id: "refine", reads: ["active_concerns"], learnEvent: "tarot_question_refined" },
    { id: "spread", reads: ["recurring_themes", "intent_history"], learnEvent: "tarot_spread_selected" },
    { id: "question", reads: ["last_questions"], learnEvent: "tarot_question_submitted" },
    { id: "follow_up", reads: ["spread_id", "concern_domain"], learnEvent: "tarot_reading_follow_up" },
  ],
  compatibility: [
    { id: "hero", reads: ["relationship_atoms", "saved_person"], learnEvent: "compatibility_view" },
    { id: "scenario", reads: ["potential_tier", "conditions"], learnEvent: "compatibility_topic_select" },
    { id: "confirm", reads: ["scenario_id"], learnEvent: "compatibility_conclusion_confirm" },
  ],
  profile: [
    { id: "portrait", reads: ["cum_summary", "evolution"], learnEvent: undefined },
    { id: "correction", reads: ["atom_id"], learnEvent: "profile_atom_correction" },
    { id: "interest", reads: ["intent_model"], learnEvent: "profile_interest_added" },
  ],
  calendar: [
    { id: "rhythm", reads: ["behavior_rhythm", "closed_days"], learnEvent: "calendar_day_marked" },
  ],
};

export function isMicroSignalStale(
  kind: MicroSignalKind,
  lastCapturedAtMs: number | null | undefined,
  nowMs = Date.now(),
): boolean {
  if (lastCapturedAtMs == null || !Number.isFinite(lastCapturedAtMs)) return true;
  const ttl = MICRO_SIGNAL_STALE_MS[kind];
  if (ttl == null) return false;
  return nowMs - lastCapturedAtMs >= ttl;
}
