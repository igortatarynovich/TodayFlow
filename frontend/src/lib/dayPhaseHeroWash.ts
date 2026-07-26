/**
 * Raster hero washes by day-phase only.
 * Appearance (light/dark) and mood apply as overlay/tint — never swap the plate.
 *
 * Morning/day use luminous plates (nebula / observatory) so mobile opacity + dark
 * appearance still leave a readable photograph. Evening/night keep moon wash.
 */

import type { DayPhase } from "@/lib/dayPhaseAtmosphere";
import type { ProductAppearance } from "@/lib/productAppearance";

export type DayPhaseHeroWash = {
  src: string;
  /**
   * Base plate luminance from the photograph.
   * Separately, `appearance` may force a darkened treatment on a light plate.
   */
  plate: "daylight" | "night";
};

const WASH: Record<DayPhase, DayPhaseHeroWash> = {
  morning: { src: "/images/cosmic/nebula.webp", plate: "daylight" },
  day: { src: "/images/cosmic/observe.webp", plate: "daylight" },
  evening: { src: "/images/cosmic/moon_wash.webp", plate: "night" },
  night: { src: "/images/cosmic/moon_wash.webp", plate: "night" },
  first: { src: "/images/cosmic/stars.webp", plate: "daylight" },
};

export function resolveDayPhaseHeroWash(phase: DayPhase | null | undefined): DayPhaseHeroWash {
  if (phase && WASH[phase]) return WASH[phase];
  return WASH.day;
}

/**
 * Hero chrome tone for copy contrast.
 * Daytime + dark appearance → still the day plate, but darkened for readable light text.
 */
export function resolveHeroChromeTone(
  wash: DayPhaseHeroWash,
  appearance: ProductAppearance,
): "light" | "dark" {
  if (wash.plate === "night") return "dark";
  return appearance === "dark" ? "dark" : "light";
}
