"use client";

import { useEffect, useState } from "react";
import { getTimeOfDayByHour, type TimeOfDay } from "@/lib/time-of-day";

export type ProductThemeMode = "light" | "dark";

export function themeFromTimeOfDay(tod: TimeOfDay): ProductThemeMode {
  return tod === "evening" ? "dark" : "light";
}

/**
 * Product chrome follows local clock: morning/day → light, evening → dark.
 * Re-checks periodically so evening transition updates without reload.
 */
export function resolveProductDayNightTheme(now: Date = new Date()): ProductThemeMode {
  const hour = now.getHours();
  // Same boundaries as getTimeOfDayByHour: evening after 18:00 or before 05:00.
  if (hour >= 18 || hour < 5) return "dark";
  return "light";
}

export function useProductDayNightTheme(): ProductThemeMode {
  const [theme, setTheme] = useState<ProductThemeMode>(() =>
    themeFromTimeOfDay(getTimeOfDayByHour()),
  );

  useEffect(() => {
    const apply = () => setTheme(themeFromTimeOfDay(getTimeOfDayByHour()));
    apply();
    const id = window.setInterval(apply, 60_000);
    return () => window.clearInterval(id);
  }, []);

  return theme;
}
