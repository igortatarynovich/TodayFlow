"use client";

import { useEffect } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import {
  DAY_PHASE_THEME_COLORS,
  resolveDayPhase,
} from "@/lib/dayPhaseAtmosphere";
import { hasCompletedFirstToday } from "@/lib/firstTodayState";
import {
  MOOD_THEME_COLORS,
  readMoodPin,
  resolveProductMood,
} from "@/lib/productMoodTheme";
import { resolveSectionAtmosphere, SECTION_THEME_COLORS } from "@/lib/sectionAtmosphere";
import { getTimeOfDayByHour } from "@/lib/time-of-day";

/**
 * Syncs route atmosphere + day-phase on `<html>`.
 *
 * Day-phase only on `/today`. When mood is resolved (pin or auto), day-phase
 * follows that mood so §8 and §9 stay aligned (FOUNDATION_UI).
 */
export function SectionAtmosphereBridge() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const atmosphere = resolveSectionAtmosphere(pathname);

  useEffect(() => {
    document.documentElement.setAttribute("data-atmosphere", atmosphere);

    const firstQuery = searchParams?.get("first") === "1";
    const isFirstDay =
      firstQuery || (pathname?.startsWith("/today") === true && !hasCompletedFirstToday());

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
        timeOfDay: getTimeOfDayByHour(),
        mood,
      });

      if (dayPhase) {
        document.documentElement.setAttribute("data-day-phase", dayPhase);
      } else {
        document.documentElement.removeAttribute("data-day-phase");
      }

      const meta = document.querySelector('meta[name="theme-color"]');
      if (meta) {
        const content = dayPhase
          ? DAY_PHASE_THEME_COLORS[dayPhase]
          : MOOD_THEME_COLORS[mood] ?? SECTION_THEME_COLORS[atmosphere];
        meta.setAttribute("content", content);
      }
    };

    apply();
    const id = window.setInterval(apply, 60_000);
    const onStorage = (e: StorageEvent) => {
      if (e.key === "todayflow_mood_pin_v1") apply();
    };
    window.addEventListener("storage", onStorage);

    return () => {
      window.clearInterval(id);
      window.removeEventListener("storage", onStorage);
      document.documentElement.removeAttribute("data-day-phase");
      document.documentElement.removeAttribute("data-mood");
    };
  }, [atmosphere, pathname, searchParams]);

  return null;
}
