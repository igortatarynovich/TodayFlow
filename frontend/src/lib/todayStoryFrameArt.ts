/**
 * Story-deck photo art — reuse existing public images.
 * Three non-overlapping pools so Greeting / Energy / Practice never share art.
 * Theme frames keep Day Atmosphere `--day-bg-art` (MODE_BG).
 */

import type { DayVisualMode } from "@/lib/dayAtmosphere";
import { DAY_VISUAL_MODES } from "@/lib/dayAtmosphere";

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

/** Lived photo / banner — never cosmic, never practices banners. */
const MODE_GREETING: Record<DayVisualMode, string> = {
  grounded: "/images/day_girl_banner.png",
  flow: "/images/day_banner.png",
  radiance: "/images/self-discovery.png",
  momentum: "/images/hero/inner_reflection.webp",
  clarity: "/images/today-ritual-entry/default-day.webp",
  tension: "/images/night_banner.png",
  renewal: "/images/today-ritual-entry/default-morning.webp",
  depth: "/images/today-ritual-entry/default-evening.webp",
};

/** Cosmic only — energy screen. */
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

/** Practice / affirmation — practices & journal heroes only. */
const MODE_PRACTICE: Record<DayVisualMode, string> = {
  grounded: "/images/praktiki_banner.png",
  flow: "/images/praktiki_banner_2.png",
  radiance: "/images/hero-meditation.png",
  momentum: "/images/praktiki_banner_3.png",
  clarity: "/images/journal.png",
  tension: "/images/Diary.png",
  renewal: "/images/hero-meditation.png",
  depth: "/images/praktiki_banner.png",
};

function readDayMode(): DayVisualMode {
  if (typeof document === "undefined") return "clarity";
  const mode = document.documentElement.getAttribute("data-day-mode");
  if (mode && mode in MODE_BG) return mode as DayVisualMode;
  return "clarity";
}

function greetingByPhase(mode: DayVisualMode): string {
  if (typeof document === "undefined") return MODE_GREETING[mode];
  const phase = document.documentElement.getAttribute("data-day-phase");
  if (phase === "morning" || phase === "first") {
    return "/images/today-ritual-entry/default-morning.webp";
  }
  if (phase === "evening" || phase === "night") {
    return "/images/today-ritual-entry/default-evening.webp";
  }
  return MODE_GREETING[mode];
}

/** Resolve immersive photo for greeting / energy / practice frames. */
export function resolveTodayStoryFrameArt(role: TodayStoryArtRole, mode?: DayVisualMode | null): string {
  const m = mode && mode in MODE_BG ? mode : readDayMode();
  if (role === "greeting") return greetingByPhase(m);
  if (role === "energy") return MODE_ENERGY[m];
  return MODE_PRACTICE[m];
}

/** Theme-shared pages use Day Atmosphere `--day-bg-art` (no separate immersive). */
export function resolveTodayThemeArt(mode?: DayVisualMode | null): string {
  const m = mode && mode in MODE_BG ? mode : readDayMode();
  return MODE_BG[m];
}

/** Test / invariant helper — roles must never collide for a mode. */
export function assertTodayStoryArtPoolsDistinct(mode: DayVisualMode): boolean {
  const g = resolveTodayStoryFrameArt("greeting", mode);
  const e = resolveTodayStoryFrameArt("energy", mode);
  const p = resolveTodayStoryFrameArt("practice", mode);
  return g !== e && e !== p && g !== p;
}

export function allTodayStoryArtModesDistinct(): boolean {
  return DAY_VISUAL_MODES.every((m) => assertTodayStoryArtPoolsDistinct(m));
}
