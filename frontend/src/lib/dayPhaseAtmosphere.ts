/**
 * Day-phase atmosphere (FOUNDATION_UI §9).
 * Extends section atmosphere — does not replace route `data-atmosphere`.
 *
 * Canon (independent of mood / appearance):
 *   date + timezone (browser local clock) → dayPhase → visual asset
 * Appearance + mood only tint/overlay the asset — they never replace it.
 */

export type DayPhase = "morning" | "day" | "evening" | "night" | "first";

export const DAY_PHASE_REVEAL_FLASH_MS = 2500;

export const DAY_PHASE_THEME_COLORS: Record<DayPhase, string> = {
  morning: "#fdf8f0",
  day: "#f9f3ee",
  evening: "#1a1714",
  night: "#121018",
  first: "#fffdfb",
};

/** Clock → phase. Night is late evening / early morning, not UI dark mode. */
export function dayPhaseFromHour(hour: number): Exclude<DayPhase, "first"> {
  const h = ((hour % 24) + 24) % 24;
  if (h >= 5 && h < 11) return "morning";
  if (h >= 11 && h < 18) return "day";
  if (h >= 18 && h < 22) return "evening";
  return "night";
}

export type ResolveDayPhaseInput = {
  pathname: string | null | undefined;
  /** First-day / onboarding — wins over clock. */
  isFirstDay?: boolean;
  /** Explicit hour (0–23). Defaults to local browser hour. */
  hour?: number;
  /** @deprecated Ignored — day-phase must not follow mood. Kept for call-site compat. */
  mood?: unknown;
  /** @deprecated Use `hour`. Mapped via morning→5, day→12, evening→19. */
  timeOfDay?: "morning" | "day" | "evening";
};

function hourFromInput(input: ResolveDayPhaseInput): number {
  if (typeof input.hour === "number" && Number.isFinite(input.hour)) return input.hour;
  if (input.timeOfDay === "morning") return 8;
  if (input.timeOfDay === "day") return 14;
  if (input.timeOfDay === "evening") return 19;
  if (typeof Date !== "undefined") return new Date().getHours();
  return 12;
}

/**
 * Day-phase applies only on `/today`. Elsewhere → null (clear attribute).
 *
 * Precedence: first-day → clock (local timezone). Mood is never consulted.
 */
export function resolveDayPhase(input: ResolveDayPhaseInput): DayPhase | null {
  const path = input.pathname ?? "";
  if (!path.startsWith("/today")) return null;
  if (input.isFirstDay) return "first";
  return dayPhaseFromHour(hourFromInput(input));
}

/** @deprecated Use dayPhaseFromHour. Kept for older tests/callers. */
export function dayPhaseFromTimeOfDay(tod: "morning" | "day" | "evening"): Exclude<DayPhase, "first" | "night"> {
  return tod;
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
