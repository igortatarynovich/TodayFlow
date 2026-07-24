/**
 * Day-phase atmosphere (FOUNDATION_UI §9).
 * Extends section atmosphere — does not replace route `data-atmosphere`.
 * Procedural CSS only; no raster stock.
 */

import { getTimeOfDayByHour, type TimeOfDay } from "@/lib/time-of-day";
import { dayPhaseFromMood, type ProductMood } from "@/lib/productMoodTheme";

export type DayPhase = "morning" | "day" | "evening" | "first";

export const DAY_PHASE_REVEAL_FLASH_MS = 2500;

export const DAY_PHASE_THEME_COLORS: Record<DayPhase, string> = {
  morning: "#fdf8f0",
  day: "#f9f3ee",
  evening: "#1a1714",
  first: "#fffdfb",
};

export function dayPhaseFromTimeOfDay(tod: TimeOfDay): Exclude<DayPhase, "first"> {
  return tod;
}

export type ResolveDayPhaseInput = {
  pathname: string | null | undefined;
  /** First-day / onboarding clarity — wins over clock when true (unless mood set). */
  isFirstDay?: boolean;
  timeOfDay?: TimeOfDay;
  /**
   * Resolved mood (auto or pinned). When set, day-phase follows mood so
   * `/today` textures never fight the product-wide palette (FOUNDATION_UI §8↔§9).
   */
  mood?: ProductMood | null;
};

/**
 * Day-phase applies only on `/today`. Elsewhere → null (clear attribute).
 *
 * Precedence: mood (pin or auto) → first-day → clock.
 * Callers should pass the same resolved mood used for `data-mood` on the shell.
 */
export function resolveDayPhase(input: ResolveDayPhaseInput): DayPhase | null {
  const path = input.pathname ?? "";
  if (!path.startsWith("/today")) return null;
  if (input.mood) return dayPhaseFromMood(input.mood);
  if (input.isFirstDay) return "first";
  const tod = input.timeOfDay ?? getTimeOfDayByHour();
  return dayPhaseFromTimeOfDay(tod);
}

const FLASH_ATTR = "data-day-phase-flash";

/** Short reveal flash (card/number) — 2–3s overlay, not a persistent phase. */
export function pulseDayPhaseRevealFlash(durationMs = DAY_PHASE_REVEAL_FLASH_MS): void {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  root.setAttribute(FLASH_ATTR, "1");
  window.setTimeout(() => {
    if (root.getAttribute(FLASH_ATTR) === "1") {
      root.removeAttribute(FLASH_ATTR);
    }
  }, durationMs);
}
