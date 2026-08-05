/**
 * Story-deck photo art — per-block backgrounds (not Day Atmosphere theme).
 *
 * Roles with their own art: greeting · energy · practice.
 * Other steps keep theme `--day-bg-art` (MODE_BG).
 *
 * Greeting art follows **day phase** (morning / day / evening / night).
 * Energy + practice still key off `DayVisualMode`.
 */

import type { DayVisualMode } from "@/lib/dayAtmosphere";
import { DAY_VISUAL_MODES } from "@/lib/dayAtmosphere";
import { resolveTodayDayPhase, type TodayDayPhase } from "@/lib/todayDayGreeting";

export type TodayStoryArtRole = "greeting" | "energy" | "practice";

/** Shared theme shell (Symbols / Attributes / Insight / Close). */
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
 * Greeting — time-of-day heroes (ritual-entry packs + warm terrestrial).
 * Rotates within the phase by calendar day so the opener is not always identical.
 */
const PHASE_GREETING: Record<TodayDayPhase, readonly string[]> = {
  morning: [
    "/images/today-ritual-entry/default-morning.webp",
    "/images/hero-meditation.png",
    "/images/today-ritual-entry/default-morning.png",
  ],
  day: [
    "/images/today-ritual-entry/default-day.png",
    "/images/day_girl_banner.png",
    "/images/journal.png",
  ],
  evening: [
    "/images/today-ritual-entry/default-evening.webp",
    "/images/night_banner.png",
    "/images/Diary.png",
  ],
  night: [
    "/images/night_banner.png",
    "/images/today-ritual-entry/default-evening.webp",
    "/images/Diary.png",
  ],
};

/**
 * Energy — full-bleed cosmic washes (not cutout orbs — those read as cards on black).
 */
const MODE_ENERGY: Record<DayVisualMode, string> = {
  grounded: "/images/cosmic/moon_wash.webp",
  flow: "/images/cosmic/celestial_wash.webp",
  radiance: "/images/cosmic/moon_wash.webp",
  momentum: "/images/cosmic/nebula.webp",
  clarity: "/images/cosmic/moon_wash.webp",
  tension: "/images/cosmic/eclipse_wash.webp",
  renewal: "/images/cosmic/moon_wash.webp",
  depth: "/images/cosmic/celestial_wash.webp",
};

/** Practice — praktiki banners; rotate by calendar day + mode. */
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

function readDayPhase(): TodayDayPhase {
  if (typeof document === "undefined") return resolveTodayDayPhase();
  const raw = document.documentElement.getAttribute("data-day-phase");
  if (raw === "morning" || raw === "day" || raw === "evening" || raw === "night") return raw;
  if (raw === "first") return "morning";
  return resolveTodayDayPhase();
}

function calendarDaySeed(): number {
  const d = new Date();
  return d.getFullYear() * 372 + d.getMonth() * 31 + d.getDate();
}

function pickFromPool(pool: readonly string[], seed: number): string {
  if (pool.length === 0) return "/images/hero-meditation.png";
  return pool[Math.abs(seed) % pool.length]!;
}

/** Greeting art for a clock phase (stable within the day, varies across days). */
export function resolveGreetingArt(
  phase?: TodayDayPhase | null,
  daySeed?: number,
): string {
  const p = phase ?? readDayPhase();
  const seed = (daySeed ?? calendarDaySeed()) + (p === "morning" ? 0 : p === "day" ? 11 : p === "evening" ? 23 : 37);
  return pickFromPool(PHASE_GREETING[p], seed);
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
export function resolveTodayStoryFrameArt(
  role: TodayStoryArtRole,
  mode?: DayVisualMode | null,
  phase?: TodayDayPhase | null,
): string {
  if (role === "greeting") return resolveGreetingArt(phase);
  const m = mode && mode in MODE_BG ? mode : readDayMode();
  if (role === "energy") return MODE_ENERGY[m];
  return resolvePracticeBanner(m);
}

/** Theme-shared pages use Day Atmosphere `--day-bg-art` (no separate immersive). */
export function resolveTodayThemeArt(mode?: DayVisualMode | null): string {
  const m = mode && mode in MODE_BG ? mode : readDayMode();
  return MODE_BG[m];
}

/** Test / invariant helper — roles must never collide for a mode + phase. */
export function assertTodayStoryArtPoolsDistinct(
  mode: DayVisualMode,
  phase: TodayDayPhase = "morning",
): boolean {
  const g = resolveTodayStoryFrameArt("greeting", mode, phase);
  const e = resolveTodayStoryFrameArt("energy", mode, phase);
  const p = resolveTodayStoryFrameArt("practice", mode, phase);
  return g !== e && e !== p && g !== p;
}

export function allTodayStoryArtModesDistinct(): boolean {
  const phases: TodayDayPhase[] = ["morning", "day", "evening", "night"];
  return DAY_VISUAL_MODES.every((m) => phases.every((ph) => assertTodayStoryArtPoolsDistinct(m, ph)));
}
