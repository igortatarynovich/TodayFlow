/**
 * Product appearance (light/dark) — independent of mood and day-phase.
 *
 * Canon:
 * - appearance: light | dark — UI chrome preference
 * - dayPhase: morning | day | evening | night | first — clock / first-day
 * - mood: calm | focus | night | clarity — emotional palette
 *
 * Appearance must NEVER be derived from mood. Mood "night" is atmosphere, not dark mode.
 */

export type ProductAppearance = "light" | "dark";
export type ProductAppearanceMode = "light" | "dark" | "system";

const STORAGE_KEY = "todayflow_appearance_v1";

export function readAppearanceMode(): ProductAppearanceMode {
  if (typeof window === "undefined") return "system";
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return "system";
    const parsed = JSON.parse(raw) as { mode?: string };
    if (parsed?.mode === "light" || parsed?.mode === "dark" || parsed?.mode === "system") {
      return parsed.mode;
    }
    return "system";
  } catch {
    return "system";
  }
}

export function writeAppearanceMode(mode: ProductAppearanceMode): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ mode }));
}

export function systemPrefersDark(getMatcher?: () => boolean): boolean {
  if (getMatcher) return getMatcher();
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") return false;
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

/**
 * Resolve light/dark chrome. Pin (light|dark) wins; system follows OS; default light.
 * Mood is intentionally ignored.
 */
export function resolveAppearance(input?: {
  mode?: ProductAppearanceMode | null;
  systemDark?: boolean;
}): ProductAppearance {
  const mode = input?.mode ?? "system";
  if (mode === "light") return "light";
  if (mode === "dark") return "dark";
  const systemDark = input?.systemDark ?? systemPrefersDark();
  return systemDark ? "dark" : "light";
}
