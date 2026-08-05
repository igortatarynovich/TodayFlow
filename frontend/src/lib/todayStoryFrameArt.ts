/**
 * Story-deck photo art — reuse existing public images.
 * Later: swap per visual_mode / energy with a fuller catalog.
 * SoT for mode seeds remains day-atmosphere.css `--day-bg-art`.
 */

import type { DayVisualMode } from "@/lib/dayAtmosphere";

export type TodayStoryArtRole = "greeting" | "energy" | "practice";

const MODE_BG: Record<DayVisualMode, string> = {
  grounded: "/images/backgrounds/1.png",
  flow: "/images/backgrounds/2.png",
  radiance: "/images/backgrounds/3.png",
  momentum: "/images/backgrounds/4.png",
  clarity: "/images/backgrounds/5.png",
  tension: "/images/backgrounds/4.png",
  renewal: "/images/backgrounds/1.png",
  depth: "/images/backgrounds/2.png",
};

const MODE_ENERGY: Record<DayVisualMode, string> = {
  grounded: "/images/cosmic/moon_wash.webp",
  flow: "/images/cosmic/celestial_wash.webp",
  radiance: "/images/cosmic/moon_orb.webp",
  momentum: "/images/cosmic/eclipse_wash.webp",
  clarity: "/images/cosmic/moon.webp",
  tension: "/images/cosmic/eclipse.webp",
  renewal: "/images/cosmic/nebula.webp",
  depth: "/images/cosmic/stars.webp",
};

const MODE_PRACTICE: Record<DayVisualMode, string> = {
  grounded: "/images/today-ritual-entry/default-morning.webp",
  flow: "/images/today-ritual-entry/default-day.webp",
  radiance: "/images/today-ritual-entry/default-day.webp",
  momentum: "/images/today-ritual-entry/default-evening.webp",
  clarity: "/images/today-ritual-entry/default.webp",
  tension: "/images/today-ritual-entry/default-evening.webp",
  renewal: "/images/today-ritual-entry/default-morning.webp",
  depth: "/images/today-ritual-entry/default-evening.webp",
};

function readDayMode(): DayVisualMode {
  if (typeof document === "undefined") return "clarity";
  const mode = document.documentElement.getAttribute("data-day-mode");
  if (mode && mode in MODE_BG) return mode as DayVisualMode;
  return "clarity";
}

function greetingByPhase(): string {
  if (typeof document === "undefined") return "/images/today-ritual-entry/default-day.webp";
  const phase = document.documentElement.getAttribute("data-day-phase");
  if (phase === "morning" || phase === "first") return "/images/today-ritual-entry/default-morning.webp";
  if (phase === "evening" || phase === "night") return "/images/today-ritual-entry/default-evening.webp";
  return "/images/today-ritual-entry/default-day.webp";
}

/** Resolve immersive photo for greeting / energy / practice frames. */
export function resolveTodayStoryFrameArt(role: TodayStoryArtRole, mode?: DayVisualMode | null): string {
  const m = mode && mode in MODE_BG ? mode : readDayMode();
  if (role === "greeting") {
    // Prefer ritual-entry photo (mockup welcome); fall back to mode bg seed.
    return greetingByPhase() || MODE_BG[m];
  }
  if (role === "energy") return MODE_ENERGY[m];
  return MODE_PRACTICE[m];
}

/** Theme-shared pages use Day Atmosphere `--day-bg-art` (no separate immersive). */
export function resolveTodayThemeArt(mode?: DayVisualMode | null): string {
  const m = mode && mode in MODE_BG ? mode : readDayMode();
  return MODE_BG[m];
}
