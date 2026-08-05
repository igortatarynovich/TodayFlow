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

/**
 * Greeting — former practice heroes (meditation / journal), not cosmic, not praktiki banners.
 */
const MODE_GREETING: Record<DayVisualMode, string> = {
  grounded: "/images/hero-meditation.png",
  flow: "/images/journal.png",
  radiance: "/images/hero-meditation.png",
  momentum: "/images/Diary.png",
  clarity: "/images/journal.png",
  tension: "/images/Diary.png",
  renewal: "/images/hero-meditation.png",
  depth: "/images/hero-meditation.png",
};

/** Energy — moon family only. */
const MODE_ENERGY: Record<DayVisualMode, string> = {
  grounded: "/images/cosmic/moon_wash.webp",
  flow: "/images/cosmic/moon.webp",
  radiance: "/images/cosmic/moon_orb.webp",
  momentum: "/images/cosmic/moon_cutout.webp",
  clarity: "/images/cosmic/moon.webp",
  tension: "/images/cosmic/moon_orb.webp",
  renewal: "/images/cosmic/moon_wash.webp",
  depth: "/images/cosmic/moon.webp",
};

/** Practice — praktiki banners only; rotate by calendar day + mode. */
export const PRAKTIKI_STORY_BANNERS = [
  "/images/praktiki_banner.png",
  "/images/praktiki_banner_2.png",
  "/images/praktiki_banner_3.png",
] as const;

function readDayMode(): DayVisualMode {
  if (typeof document === "undefined") return "clarity";
  const mode = document.documentElement.getAttribute("data-day-mode");
  if (mode && mode in MODE_BG) return mode as DayVisualMode;
  return "clarity";
}

function calendarDaySeed(): number {
  const d = new Date();
  return d.getFullYear() * 372 + d.getMonth() * 31 + d.getDate();
}

/** Pick a praktiki banner for the practice frame (stable per day+mode). */
export function resolvePracticeBanner(mode?: DayVisualMode | null, daySeed?: number): string {
  const m = mode && mode in MODE_BG ? mode : readDayMode();
  const modeIdx = Math.max(0, DAY_VISUAL_MODES.indexOf(m));
  const seed = daySeed ?? calendarDaySeed();
  const i = Math.abs(seed + modeIdx) % PRAKTIKI_STORY_BANNERS.length;
  return PRAKTIKI_STORY_BANNERS[i]!;
}

/** Resolve immersive photo for greeting / energy / practice frames. */
export function resolveTodayStoryFrameArt(role: TodayStoryArtRole, mode?: DayVisualMode | null): string {
  const m = mode && mode in MODE_BG ? mode : readDayMode();
  if (role === "greeting") return MODE_GREETING[m];
  if (role === "energy") return MODE_ENERGY[m];
  return resolvePracticeBanner(m);
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
