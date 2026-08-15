/**
 * ScreenFlow capability matrix (Today).
 * Canon: docs/today/TODAY_PRODUCT_FLOW_V1.md · SCREEN_FLOW_V1 §4.1
 *
 * Four surfaces: today · ritual · my_day · evening.
 * Presentation may hide a house. It must not invent Personal Day for guests.
 * Timeline is never shown on `today` (Global). Personal timeline only on `my_day`.
 */

export type TodayCapabilityDepth = "guest" | "general" | "light" | "deep";

export type TodayProductScreenId = "today" | "ritual" | "my_day" | "evening";

export type TodayScreenFlowCapability = {
  depth: TodayCapabilityDepth;
  /** Global Day dashboard */
  today: boolean;
  /** Card + number lenses */
  ritual: boolean;
  /** Personal Day */
  myDay: boolean;
  /** Gratitude — user response, not a rewrite of the day */
  evening: boolean;
  /** @deprecated use today — Global Day */
  globalDay: boolean;
  /** @deprecated use ritual */
  rituals: boolean;
  /** @deprecated use myDay */
  personalDay: boolean;
  /** Personal timeline on MY DAY only; never on TODAY */
  personalTimeline: boolean;
  /** @deprecated alias of personalTimeline */
  natalTimeline: boolean;
  whyPersonal: boolean;
};

export const TODAY_SCREEN_FLOW_CAPABILITY: Record<
  TodayCapabilityDepth,
  TodayScreenFlowCapability
> = {
  guest: {
    depth: "guest",
    today: true,
    ritual: true,
    myDay: false,
    evening: true,
    globalDay: true,
    rituals: true,
    personalDay: false,
    personalTimeline: false,
    natalTimeline: false,
    whyPersonal: false,
  },
  general: {
    depth: "general",
    today: true,
    ritual: true,
    myDay: false,
    evening: true,
    globalDay: true,
    rituals: true,
    personalDay: false,
    personalTimeline: false,
    natalTimeline: false,
    whyPersonal: false,
  },
  light: {
    depth: "light",
    today: true,
    ritual: true,
    myDay: true,
    evening: true,
    globalDay: true,
    rituals: true,
    personalDay: true,
    personalTimeline: false,
    natalTimeline: false,
    whyPersonal: true,
  },
  deep: {
    depth: "deep",
    today: true,
    ritual: true,
    myDay: true,
    evening: true,
    globalDay: true,
    rituals: true,
    personalDay: true,
    personalTimeline: true,
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
  return TODAY_SCREEN_FLOW_CAPABILITY[depth].myDay;
}

export function todayCapabilityShowsTimelineOnToday(): false {
  return false;
}
