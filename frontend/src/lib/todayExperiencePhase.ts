/**
 * PR1 — Today Experience phase machine S0–S5 (director layer).
 */

import type { TodayRitualSpineSnapshot } from "@/lib/todayRitualSpineMachine";

/** S0 entry → S1–S2 tarot → S3–S4 number → S5 synthesis */
export type TodayExperiencePhase = "entry" | "tarot_reveal" | "number_reveal" | "day_synthesis";

export type TodayExperiencePhaseInput = Pick<
  TodayRitualSpineSnapshot,
  "dayOpened" | "tarotContinueAck" | "numberRevealed"
>;

export function todayExperiencePhase(input: TodayExperiencePhaseInput): TodayExperiencePhase {
  if (!input.dayOpened) return "entry";
  if (!input.tarotContinueAck) return "tarot_reveal";
  if (!input.numberRevealed) return "number_reveal";
  return "day_synthesis";
}

export const TODAY_EXPERIENCE_PHASE_ORDER: TodayExperiencePhase[] = [
  "entry",
  "tarot_reveal",
  "number_reveal",
  "day_synthesis",
];

export function todayExperiencePhaseIndex(phase: TodayExperiencePhase): number {
  return TODAY_EXPERIENCE_PHASE_ORDER.indexOf(phase);
}
