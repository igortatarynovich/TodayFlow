import type { DayEngagementState } from "@/lib/todayDayEngagement";
import { isTodayPersonalized } from "@/lib/todayRitualGate";

export type TodayCompositionVariant = "default" | "firstToday";

export type TodayCompositionZoneFlags = {
  continuity: boolean;
  greeting: boolean;
  pulse: boolean;
  hero: boolean;
  glance: boolean;
  astroContext: boolean;
  ritualTarot: boolean;
  ritualNumber: boolean;
  whyStory: boolean;
  /** Practice / meditation / affirmation — preview before ritual, full after. */
  strengthen: boolean;
  /** Day promise / goal chips — stays visible until user sets one (incl. evening). */
  promise: boolean;
  /** Forward-looking action cards (practice shortcuts) — hidden in evening. */
  actions: boolean;
  growthPromise: boolean;
  evening: boolean;
};

const EMPTY_ENGAGEMENT: Pick<DayEngagementState, "tarotPickedName" | "numberConfirmed"> = {
  tarotPickedName: null,
  numberConfirmed: false,
};

/**
 * Authoritative day_story → one literary reading, not a widget gallery.
 * Ritual gates stay; glance / sky / hero / multi-tool chrome go away.
 */
export function applySingleVoiceZones(flags: TodayCompositionZoneFlags): TodayCompositionZoneFlags {
  return {
    ...flags,
    pulse: false,
    hero: false,
    glance: false,
    astroContext: false,
    whyStory: false,
    actions: false,
  };
}

/** Today Day Story — zone visibility per path and ritual phase. */
export function todayCompositionZones(
  variant: TodayCompositionVariant,
  engagement: Pick<DayEngagementState, "tarotPickedName" | "numberConfirmed"> = EMPTY_ENGAGEMENT,
): TodayCompositionZoneFlags {
  const personalized = isTodayPersonalized(engagement);
  const tarotDone = Boolean(engagement.tarotPickedName);

  return {
    continuity: variant !== "firstToday",
    greeting: true,
    pulse: true,
    hero: true,
    /** Dashboard panels — hidden on first session (conversation path). */
    glance: variant !== "firstToday",
    astroContext: variant !== "firstToday",
    ritualTarot: true,
    ritualNumber: tarotDone,
    whyStory: personalized,
    strengthen: variant !== "firstToday",
    promise: personalized,
    actions: personalized,
    growthPromise: personalized,
    evening: personalized,
  };
}

/** Evening surface hides forward actions; keeps promise + recap + close. */
export function todayEveningStoryZones(variant: TodayCompositionVariant): TodayCompositionZoneFlags {
  return {
    continuity: false,
    greeting: true,
    pulse: true,
    hero: true,
    glance: true,
    astroContext: false,
    ritualTarot: false,
    ritualNumber: false,
    whyStory: false,
    strengthen: false,
    promise: true,
    actions: false,
    growthPromise: true,
    evening: true,
  };
}

/** Evening/night only after ritual is complete; otherwise keep the morning path so card/number stay available. */
export function resolveTodayCompositionZones(input: {
  variant: TodayCompositionVariant;
  engagement: Pick<DayEngagementState, "tarotPickedName" | "numberConfirmed" | "dayGoal">;
  isEveningSurface: boolean;
  personalizedReady: boolean;
  /** When true (authoritative day_story), suppress widget gallery zones. */
  singleVoice?: boolean;
}): TodayCompositionZoneFlags {
  let flags: TodayCompositionZoneFlags;
  if (input.isEveningSurface && input.personalizedReady) {
    flags = todayEveningStoryZones(input.variant);
  } else {
    flags = todayCompositionZones(input.variant, input.engagement);
  }
  if (input.singleVoice) {
    flags = applySingleVoiceZones(flags);
    if (input.isEveningSurface && input.personalizedReady) {
      flags = { ...flags, pulse: false, hero: false, glance: false };
    }
  }
  return flags;
}
