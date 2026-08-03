/**
 * Raster hero washes.
 * Clock day-phase is the default; Plot may override by thesis.mode (dynamics class).
 * Appearance (light/dark) applies as chrome tone — never invents a new plate set.
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

/** Internal dynamics class — drives visual; never rendered as UI tag. */
export type PlotDynamicsClass = "tension" | "build" | "dominant" | "even";

const WASH: Record<DayPhase, DayPhaseHeroWash> = {
  morning: { src: "/images/cosmic/nebula.webp", plate: "daylight" },
  day: { src: "/images/cosmic/observe.webp", plate: "daylight" },
  evening: { src: "/images/cosmic/moon_wash.webp", plate: "night" },
  night: { src: "/images/cosmic/moon_wash.webp", plate: "night" },
  first: { src: "/images/cosmic/stars.webp", plate: "daylight" },
};

const CALM_DAYLIGHT: DayPhaseHeroWash = {
  src: "/images/cosmic/observe.webp",
  plate: "daylight",
};
const SOFT_LUMINOUS: DayPhaseHeroWash = {
  src: "/images/cosmic/nebula.webp",
  plate: "daylight",
};
const DENSE_DAYLIGHT: DayPhaseHeroWash = {
  src: "/images/cosmic/stars.webp",
  plate: "daylight",
};

export function resolveDayPhaseHeroWash(phase: DayPhase | null | undefined): DayPhaseHeroWash {
  if (phase && WASH[phase]) return WASH[phase];
  return WASH.day;
}

/**
 * Map thesis.mode → internal dynamics class (canon RU labels, not UI).
 * conflict/pressure/change → напряжение; opportunity/transition → усиление;
 * recovery soft → доминанта soft; stability → ровный.
 */
export function dynamicsClassFromThesisMode(mode: string | null | undefined): PlotDynamicsClass | null {
  const m = (mode || "").trim().toLowerCase();
  if (!m) return null;
  if (m === "stability") return "even";
  if (m === "recovery") return "dominant";
  if (m === "opportunity" || m === "transition") return "build";
  if (m === "conflict" || m === "pressure" || m === "change") return "tension";
  return null;
}

/**
 * Plot hero wash: classification wins over morning drama on even days.
 * Night phase may keep moon wash except on even (calm daylight preferred).
 */
export function resolvePlotHeroWash(
  mode: string | null | undefined,
  phase: DayPhase | null | undefined,
): DayPhaseHeroWash {
  const dyn = dynamicsClassFromThesisMode(mode);
  const phaseWash = resolveDayPhaseHeroWash(phase);
  if (!dyn) return phaseWash;

  if (dyn === "even") {
    // Ровный → спокойный кадр; never morning nebula drama
    if (phase === "evening" || phase === "night") {
      return { src: "/images/cosmic/celestial_wash.webp", plate: "daylight" };
    }
    return CALM_DAYLIGHT;
  }
  if (dyn === "dominant") {
    // Recovery — soft calm; keep night moon if already night
    if (phase === "evening" || phase === "night") return phaseWash;
    return CALM_DAYLIGHT;
  }
  if (dyn === "build") {
    return SOFT_LUMINOUS;
  }
  // tension
  if (phase === "evening" || phase === "night") return phaseWash;
  return DENSE_DAYLIGHT;
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
