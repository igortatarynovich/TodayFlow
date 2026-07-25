/**
 * Raster hero washes by day-phase / mood texture.
 * Uses existing cosmic plates — moon only for evening; day never shows a night moon.
 */

import type { DayPhase } from "@/lib/dayPhaseAtmosphere";

export type DayPhaseHeroWash = {
  src: string;
  /** CSS class tone for hero chrome: light copy on dark plate vs dark copy on light plate. */
  tone: "dark" | "light";
};

const WASH: Record<DayPhase, DayPhaseHeroWash> = {
  morning: { src: "/images/cosmic/celestial_wash.webp", tone: "light" },
  day: { src: "/images/cosmic/zodiac_wash.webp", tone: "light" },
  evening: { src: "/images/cosmic/moon_wash.webp", tone: "dark" },
  first: { src: "/images/cosmic/stars.webp", tone: "light" },
};

export function resolveDayPhaseHeroWash(phase: DayPhase | null | undefined): DayPhaseHeroWash {
  if (phase && WASH[phase]) return WASH[phase];
  return WASH.day;
}
