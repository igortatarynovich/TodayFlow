"use client";

import { useCallback, useEffect, useState } from "react";
import { getTimeOfDayByHour, type TimeOfDay } from "@/lib/time-of-day";
import {
  readMoodPin,
  resolveProductMood,
  themeModeFromMood,
  writeMoodPin,
  type ProductMood,
  type ProductThemeMode,
} from "@/lib/productMoodTheme";

export type { ProductMood, ProductThemeMode } from "@/lib/productMoodTheme";
export {
  dayPhaseFromMood,
  moodFromTimeOfDay,
  resolveProductMood,
  themeModeFromMood,
} from "@/lib/productMoodTheme";

export type ProductMoodThemeState = {
  mood: ProductMood;
  theme: ProductThemeMode;
  pinned: boolean;
  pinMood: (mood: ProductMood) => void;
  clearPin: () => void;
};

/**
 * Emotional mood + derived light/dark for product chrome (FOUNDATION_UI §8).
 * Pin persists in localStorage; auto follows clock / first-day.
 */
export function useProductMoodTheme(options?: { isFirstDay?: boolean }): ProductMoodThemeState {
  const isFirstDay = options?.isFirstDay ?? false;
  const [pinnedMood, setPinnedMood] = useState<ProductMood | null>(null);
  const [mood, setMood] = useState<ProductMood>(() =>
    resolveProductMood({ isFirstDay, timeOfDay: getTimeOfDayByHour() }),
  );

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
  }, [isFirstDay]);

  useEffect(() => {
    refresh();
    const id = window.setInterval(refresh, 60_000);
    const onStorage = (e: StorageEvent) => {
      if (e.key === "todayflow_mood_pin_v1") refresh();
    };
    window.addEventListener("storage", onStorage);
    return () => {
      window.clearInterval(id);
      window.removeEventListener("storage", onStorage);
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

  return {
    mood,
    theme: themeModeFromMood(mood),
    pinned: pinnedMood != null,
    pinMood,
    clearPin,
  };
}

export function themeFromTimeOfDay(tod: TimeOfDay): ProductThemeMode {
  return themeModeFromMood(resolveProductMood({ timeOfDay: tod }));
}

export function resolveProductDayNightTheme(now: Date = new Date()): ProductThemeMode {
  const hour = now.getHours();
  const tod: TimeOfDay = hour >= 5 && hour < 11 ? "morning" : hour >= 11 && hour < 18 ? "day" : "evening";
  return themeModeFromMood(resolveProductMood({ timeOfDay: tod }));
}

/**
 * Clock → light/dark (backward compatible). Derives from mood mapping (§8).
 */
export function useProductDayNightTheme(): ProductThemeMode {
  const { theme } = useProductMoodTheme();
  return theme;
}
