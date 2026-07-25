/**
 * Mood themes (FOUNDATION_UI §8) — emotional atmosphere only.
 *
 * Independent of:
 * - appearance (light/dark) — see productAppearance.ts
 * - dayPhase (morning/day/evening/night) — see dayPhaseAtmosphere.ts
 *
 * Mood "night" means nocturnal *palette*, not dark mode and not evening photography.
 */

import { getTimeOfDayByHour, type TimeOfDay } from "@/lib/time-of-day";

export type ProductMood = "calm" | "focus" | "night" | "clarity";
/** @deprecated Use ProductAppearance from productAppearance.ts */
export type ProductThemeMode = "light" | "dark";
/** @deprecated Day-phase must not follow mood. */
export type DayPhaseFromMood = "morning" | "day" | "evening" | "first";

export const PRODUCT_MOODS: readonly ProductMood[] = ["calm", "focus", "night", "clarity"] as const;

export const PRODUCT_MOOD_LABELS_RU: Record<ProductMood, string> = {
  calm: "Спокойствие",
  focus: "Фокус",
  night: "Ночь",
  clarity: "Ясность",
};

const PIN_STORAGE_KEY = "todayflow_mood_pin_v1";

export function moodFromTimeOfDay(tod: TimeOfDay): Exclude<ProductMood, "clarity"> {
  if (tod === "morning") return "calm";
  if (tod === "day") return "focus";
  return "night";
}

/**
 * @deprecated Appearance is independent. Prefer resolveAppearance().
 * Kept only so legacy call sites that still import this don't crash; night mood
 * no longer drives product chrome.
 */
export function themeModeFromMood(_mood: ProductMood): ProductThemeMode {
  return "light";
}

/** @deprecated Informational only — do not drive day-phase or hero assets. */
export function dayPhaseFromMood(mood: ProductMood): DayPhaseFromMood {
  switch (mood) {
    case "calm":
      return "morning";
    case "focus":
      return "day";
    case "night":
      return "evening";
    case "clarity":
      return "first";
  }
}

export type ResolveProductMoodInput = {
  timeOfDay?: TimeOfDay;
  /** First-day / onboarding — suggests clarity when not pinned. */
  isFirstDay?: boolean;
  /** Manual pin — wins over clock and first-day. */
  pinnedMood?: ProductMood | null;
};

export function resolveProductMood(input: ResolveProductMoodInput = {}): ProductMood {
  if (input.pinnedMood) return input.pinnedMood;
  if (input.isFirstDay) return "clarity";
  const tod = input.timeOfDay ?? getTimeOfDayByHour();
  return moodFromTimeOfDay(tod);
}

export function readMoodPin(): ProductMood | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(PIN_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as { mood?: string };
    if (parsed?.mood && (PRODUCT_MOODS as readonly string[]).includes(parsed.mood)) {
      return parsed.mood as ProductMood;
    }
    return null;
  } catch {
    return null;
  }
}

export function writeMoodPin(mood: ProductMood | null): void {
  if (typeof window === "undefined") return;
  if (mood == null) {
    localStorage.removeItem(PIN_STORAGE_KEY);
    return;
  }
  localStorage.setItem(PIN_STORAGE_KEY, JSON.stringify({ mood }));
}

/** Theme-color / PWA chrome accents per mood (not appearance). */
export const MOOD_THEME_COLORS: Record<ProductMood, string> = {
  calm: "#fdf8f0",
  focus: "#f4f2ef",
  night: "#1a1714",
  clarity: "#fffdfb",
};
