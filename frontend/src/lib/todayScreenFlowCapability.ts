/**
 * ScreenFlow capability matrix (Today).
 * Canon: docs/today/TODAY_PRODUCT_FLOW_V1.md · SCREEN_FLOW_V1 §4.1
 *
 * Four surfaces: today · ritual · my_day · evening.
 * Presentation may hide a house. It must not invent Personal Day for guests.
 * Personal natal timeline never on `today`. Global day clock (windows[]) may show on TODAY.
 * MY DAY: natal clocks when present, else Global windows × driver facts as «Ритм дня».
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

/** DOB evidence from Core Profile — not a UI wish. */
export function profileHasBirthDate(profile?: {
  astro?: { birth_date?: string | null };
  numerology?: { birth_date?: string | null };
} | null): boolean {
  return Boolean(
    String(profile?.astro?.birth_date || "").trim() ||
      String(profile?.numerology?.birth_date || "").trim(),
  );
}

/** Time + place on top of DOB. `time_unknown` blocks deep. */
export function profileHasBirthTimePlace(profile?: {
  astro?: {
    birth_date?: string | null;
    birth_time?: string | null;
    time_unknown?: boolean | null;
    location_name?: string | null;
  };
} | null): boolean {
  const astro = profile?.astro;
  if (!String(astro?.birth_date || "").trim()) return false;
  if (astro?.time_unknown) return false;
  if (!String(astro?.birth_time || "").trim()) return false;
  return Boolean(String(astro?.location_name || "").trim());
}

export function resolveTodayCapabilityFromProfile(input: {
  authenticated?: boolean;
  coreProfile?: {
    astro?: {
      birth_date?: string | null;
      birth_time?: string | null;
      time_unknown?: boolean | null;
      location_name?: string | null;
    };
    numerology?: { birth_date?: string | null };
  } | null;
}): TodayCapabilityDepth {
  return resolveTodayCapabilityDepth({
    authenticated: Boolean(input.authenticated),
    hasBirthDate: profileHasBirthDate(input.coreProfile),
    hasBirthTimePlace: profileHasBirthTimePlace(input.coreProfile),
  });
}
