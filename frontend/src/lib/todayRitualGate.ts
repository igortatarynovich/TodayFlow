import type { DayEngagementState } from "@/lib/todayDayEngagement";

/** Ritual progression: foundation → tarot → number → personalized day. */
export type TodayRitualPhase = "tarot_pending" | "number_pending" | "complete";

export function resolveTodayRitualPhase(engagement: Pick<DayEngagementState, "tarotPickedName" | "numberConfirmed">): TodayRitualPhase {
  if (!engagement.tarotPickedName) return "tarot_pending";
  if (!engagement.numberConfirmed) return "number_pending";
  return "complete";
}

export function isTodayPersonalized(
  engagement: Pick<DayEngagementState, "tarotPickedName" | "numberConfirmed">,
): boolean {
  return resolveTodayRitualPhase(engagement) === "complete";
}
