"use client";

import { useEffect } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import {
  DAY_PHASE_THEME_COLORS,
  resolveDayPhase,
} from "@/lib/dayPhaseAtmosphere";
import { resolveIsFirstDay } from "@/lib/firstTodayState";
import {
  readAppearanceMode,
  resolveAppearance,
  systemPrefersDark,
} from "@/lib/productAppearance";
import {
  MOOD_THEME_COLORS,
  readMoodPin,
  resolveProductMood,
} from "@/lib/productMoodTheme";
import { resolveSectionAtmosphere, SECTION_THEME_COLORS } from "@/lib/sectionAtmosphere";
import { getTimeOfDayByHour } from "@/lib/time-of-day";

/**
 * Syncs route atmosphere + day-phase + mood on `<html>`.
 *
 * Day-phase only on `/today`, from clock / first-day — never from mood.
 * Appearance (`data-theme`) is applied on the product shell frame only
 * (ProductWebAppShell) — do not set it on `<html>` or mood/night + system dark
 * will fight Day Atmosphere ink/sidebar chrome.
 */
export function SectionAtmosphereBridge() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const atmosphere = resolveSectionAtmosphere(pathname);

  useEffect(() => {
    document.documentElement.setAttribute("data-atmosphere", atmosphere);

    const isFirstDay = resolveIsFirstDay(pathname, searchParams);

    const apply = () => {
      const mood = resolveProductMood({
        pinnedMood: readMoodPin(),
        isFirstDay,
        timeOfDay: getTimeOfDayByHour(),
      });
      document.documentElement.setAttribute("data-mood", mood);

      const dayPhase = resolveDayPhase({
        pathname,
        isFirstDay,
        hour: new Date().getHours(),
      });

      if (dayPhase) {
        document.documentElement.setAttribute("data-day-phase", dayPhase);
      } else {
        document.documentElement.removeAttribute("data-day-phase");
      }

      // Clear legacy html theme — product chrome follows Day Atmosphere / frame theme.
      document.documentElement.removeAttribute("data-theme");

      const appearance = resolveAppearance({
        mode: readAppearanceMode(),
        systemDark: systemPrefersDark(),
      });

      const meta = document.querySelector('meta[name="theme-color"]');
      if (meta) {
        const dayMode = document.documentElement.getAttribute("data-day-mode");
        // Product chrome is day-tinted light — do not push evening/night dark into theme-color.
        const content = dayMode
          ? SECTION_THEME_COLORS.today ?? SECTION_THEME_COLORS[atmosphere]
          : appearance === "dark"
            ? "#121018"
            : dayPhase
              ? DAY_PHASE_THEME_COLORS[dayPhase]
              : MOOD_THEME_COLORS[mood] ?? SECTION_THEME_COLORS[atmosphere];
        meta.setAttribute("content", content);
      }
    };

    apply();
    const id = window.setInterval(apply, 60_000);
    const onStorage = (e: StorageEvent) => {
      if (e.key === "todayflow_mood_pin_v1" || e.key === "todayflow_appearance_v1") apply();
    };
    const mq = window.matchMedia?.("(prefers-color-scheme: dark)");
    const onScheme = () => apply();
    mq?.addEventListener?.("change", onScheme);
    window.addEventListener("storage", onStorage);

    return () => {
      window.clearInterval(id);
      window.removeEventListener("storage", onStorage);
      mq?.removeEventListener?.("change", onScheme);
      document.documentElement.removeAttribute("data-day-phase");
      document.documentElement.removeAttribute("data-mood");
      document.documentElement.removeAttribute("data-theme");
    };
  }, [atmosphere, pathname, searchParams]);

  return null;
}
