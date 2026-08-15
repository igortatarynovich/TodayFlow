/**
 * ScreenFlow capability matrix (Today).
 * Canon: docs/foundation/SCREEN_FLOW_V1.md §4.1 · DAY_SCENARIO_V1 I7
 * · TODAY_CONTENT_PIPELINE_V1 guest/personal omit.
 *
 * Presentation may hide a house. It must not invent Personal Day for guests.
 */

export type TodayCapabilityDepth = "guest" | "general" | "light" | "deep";

export type TodayScreenFlowCapability = {
  depth: TodayCapabilityDepth;
  /** Global Day: atmosphere, theme, strength, risk, sky, timeline */
  globalDay: boolean;
  /** Ritual lenses: card base + number (universal if no birth_date) */
  rituals: boolean;
  /** Personal Day: overlay, bridges, focus / priority / avoid */
  personalDay: boolean;
  natalTimeline: boolean;
  whyPersonal: boolean;
};

export const TODAY_SCREEN_FLOW_CAPABILITY: Record<
  TodayCapabilityDepth,
  TodayScreenFlowCapability
> = {
  guest: {
    depth: "guest",
    globalDay: true,
    rituals: true,
    personalDay: false,
    natalTimeline: false,
    whyPersonal: false,
  },
  general: {
    depth: "general",
    globalDay: true,
    rituals: true,
    personalDay: false,
    natalTimeline: false,
    whyPersonal: false,
  },
  light: {
    depth: "light",
    globalDay: true,
    rituals: true,
    personalDay: true,
    natalTimeline: false,
    whyPersonal: true,
  },
  deep: {
    depth: "deep",
    globalDay: true,
    rituals: true,
    personalDay: true,
    natalTimeline: true,
    whyPersonal: true,
  },
};

export function resolveTodayCapabilityDepth(input: {
  authenticated?: boolean;
  hasBirthDate?: boolean;
  hasBirthTimePlace?: boolean;
}): TodayCapabilityDepth {
  if (!input.authenticated) return "guest";
  if (input.hasBirthTimePlace) return "deep";
  if (input.hasBirthDate) return "light";
  return "general";
}

export function todayCapabilityAllowsPersonal(
  depth: TodayCapabilityDepth,
): boolean {
  return TODAY_SCREEN_FLOW_CAPABILITY[depth].personalDay;
}
