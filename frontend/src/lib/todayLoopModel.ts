/**
 * Block 6 — promise loop + evening checkout.
 * LIVE slots only (promise suggestions / dayGoal / trap / evening_closure). No invent.
 * Canon: TODAY_SCREEN_SCENARIO_V3 § useful Today · block 6.
 */

import type { TodayContractV1 } from "@/lib/todayContract";
import { clipCompassProse, cleanAmbassadorWhy } from "@/lib/todayDayBrief";
import type { TodayPromiseSuggestion } from "@/lib/todayDayDialogue";

export type TodayLoopMode = "morning" | "evening";

export type TodayLoopModel = {
  mode: TodayLoopMode;
  /** One manifesto line (accepted or primary suggestion). */
  manifesto: string | null;
  /** Accepted by user. */
  accepted: boolean;
  /** Alternate suggestions (omit primary if already shown as manifesto). */
  alternatives: TodayPromiseSuggestion[];
  /** Clipped trap for evening check question. */
  trapCheck: string | null;
  /** Live evening_closure if present. */
  eveningClosure: string | null;
};

export function buildTodayLoopModel(input: {
  contract: TodayContractV1;
  dayGoal?: string | null;
  promiseSuggestions?: TodayPromiseSuggestion[];
  isEveningSurface?: boolean;
}): TodayLoopModel {
  const acceptedText = String(input.dayGoal || "").trim() || null;
  const suggestions = input.promiseSuggestions ?? [];
  const primary = suggestions[0]?.text?.trim() || null;
  const manifesto = acceptedText || primary;

  const alternatives = acceptedText
    ? suggestions.filter((s) => s.text.trim() !== acceptedText).slice(0, 2)
    : suggestions.slice(1, 3);

  const trapRaw = cleanAmbassadorWhy(input.contract.day_story?.trap);
  const trapCheck = trapRaw ? clipCompassProse(trapRaw, 140) : null;

  const eveningRaw = String(input.contract.day_story?.evening_closure || "").trim();
  const eveningClosure = eveningRaw
    ? cleanAmbassadorWhy(eveningRaw) || clipCompassProse(eveningRaw, 180)
    : null;

  return {
    mode: input.isEveningSurface ? "evening" : "morning",
    manifesto,
    accepted: Boolean(acceptedText),
    alternatives,
    trapCheck,
    eveningClosure,
  };
}
