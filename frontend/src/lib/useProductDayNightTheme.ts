"use client";

import { useCallback, useEffect, useState } from "react";
import { getTimeOfDayByHour, type TimeOfDay } from "@/lib/time-of-day";
import {
  readAppearanceMode,
  resolveAppearance,
  systemPrefersDark,
  writeAppearanceMode,
  type ProductAppearance,
  type ProductAppearanceMode,
} from "@/lib/productAppearance";
import {
  readMoodPin,
  resolveProductMood,
  writeMoodPin,
  type ProductMood,
  type ProductThemeMode,
} from "@/lib/productMoodTheme";

export type { ProductMood, ProductThemeMode } from "@/lib/productMoodTheme";
export type { ProductAppearance, ProductAppearanceMode } from "@/lib/productAppearance";
export {
  dayPhaseFromMood,
  moodFromTimeOfDay,
  resolveProductMood,
  themeModeFromMood,
} from "@/lib/productMoodTheme";
export { resolveAppearance, readAppearanceMode, writeAppearanceMode } from "@/lib/productAppearance";

export type ProductMoodThemeState = {
  mood: ProductMood;
  /** UI chrome light/dark — independent of mood. */
  theme: ProductAppearance;
  appearance: ProductAppearance;
  appearanceMode: ProductAppearanceMode;
  pinned: boolean;
  pinMood: (mood: ProductMood) => void;
  clearPin: () => void;
  setAppearanceMode: (mode: ProductAppearanceMode) => void;
};

/**
 * Mood (emotional) + appearance (light/dark) for product chrome.
 * Appearance never follows mood; day-phase is resolved separately.
 */
export function useProductMoodTheme(options?: { isFirstDay?: boolean }): ProductMoodThemeState {
  const isFirstDay = options?.isFirstDay ?? false;
  const [pinnedMood, setPinnedMood] = useState<ProductMood | null>(null);
  const [mood, setMood] = useState<ProductMood>(() =>
    resolveProductMood({ isFirstDay, timeOfDay: getTimeOfDayByHour() }),
  );
  const [appearanceMode, setAppearanceModeState] = useState<ProductAppearanceMode>("system");
  const [appearance, setAppearance] = useState<ProductAppearance>("light");

  const refresh = useCallback(() => {
    const pin = readMoodPin();
    setPinnedMood(pin);
    setMood(
      resolveProductMood({
        pinnedMood: pin,
        isFirstDay,
        timeOfDay: getTimeOfDayByHour(),
      }),
    );
    const mode = readAppearanceMode();
    setAppearanceModeState(mode);
    setAppearance(resolveAppearance({ mode, systemDark: systemPrefersDark() }));
  }, [isFirstDay]);

  useEffect(() => {
    refresh();
    const id = window.setInterval(refresh, 60_000);
    const onStorage = (e: StorageEvent) => {
      if (e.key === "todayflow_mood_pin_v1" || e.key === "todayflow_appearance_v1") refresh();
    };
    const mq = window.matchMedia?.("(prefers-color-scheme: dark)");
    const onScheme = () => refresh();
    mq?.addEventListener?.("change", onScheme);
    window.addEventListener("storage", onStorage);
    return () => {
      window.clearInterval(id);
      window.removeEventListener("storage", onStorage);
      mq?.removeEventListener?.("change", onScheme);
    };
  }, [refresh]);

  const pinMood = useCallback((next: ProductMood) => {
    writeMoodPin(next);
    setPinnedMood(next);
    setMood(next);
  }, []);

  const clearPin = useCallback(() => {
    writeMoodPin(null);
    setPinnedMood(null);
    setMood(
      resolveProductMood({
        pinnedMood: null,
        isFirstDay,
        timeOfDay: getTimeOfDayByHour(),
      }),
    );
  }, [isFirstDay]);

  const setAppearanceMode = useCallback((mode: ProductAppearanceMode) => {
    writeAppearanceMode(mode);
    setAppearanceModeState(mode);
    setAppearance(resolveAppearance({ mode, systemDark: systemPrefersDark() }));
  }, []);

  return {
    mood,
    theme: appearance,
    appearance,
    appearanceMode,
    pinned: pinnedMood != null,
    pinMood,
    clearPin,
    setAppearanceMode,
  };
}

export function themeFromTimeOfDay(tod: TimeOfDay): ProductThemeMode {
  // Appearance is independent; keep light as default for clock-only helpers.
  void tod;
  return "light";
}

export function resolveProductDayNightTheme(now: Date = new Date()): ProductThemeMode {
  void now;
  return resolveAppearance({ mode: readAppearanceMode(), systemDark: systemPrefersDark() });
}

/**
 * Clock → light/dark via appearance preference (not mood).
 */
export function useProductDayNightTheme(): ProductThemeMode {
  const { theme } = useProductMoodTheme();
  return theme;
}
