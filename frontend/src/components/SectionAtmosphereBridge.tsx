"use client";

import { useEffect } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import {
  DAY_PHASE_THEME_COLORS,
  resolveDayPhase,
} from "@/lib/dayPhaseAtmosphere";
import { hasCompletedFirstToday } from "@/lib/firstTodayState";
import { resolveSectionAtmosphere, SECTION_THEME_COLORS } from "@/lib/sectionAtmosphere";
import { getTimeOfDayByHour } from "@/lib/time-of-day";

/**
 * Syncs route atmosphere + day-phase on `<html>`.
 * Day-phase only on `/today` (FOUNDATION_UI §9) — extends section atmosphere, no second SoT.
 */
export function SectionAtmosphereBridge() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const atmosphere = resolveSectionAtmosphere(pathname);

  useEffect(() => {
    document.documentElement.setAttribute("data-atmosphere", atmosphere);

    const firstQuery = searchParams?.get("first") === "1";
    const isFirstDay = firstQuery || (pathname?.startsWith("/today") === true && !hasCompletedFirstToday());
    const dayPhase = resolveDayPhase({
      pathname,
      isFirstDay,
      timeOfDay: getTimeOfDayByHour(),
    });

    if (dayPhase) {
      document.documentElement.setAttribute("data-day-phase", dayPhase);
    } else {
      document.documentElement.removeAttribute("data-day-phase");
    }

    const color = dayPhase ? DAY_PHASE_THEME_COLORS[dayPhase] : SECTION_THEME_COLORS[atmosphere];
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", color);

    const id = window.setInterval(() => {
      const next = resolveDayPhase({
        pathname,
        isFirstDay,
        timeOfDay: getTimeOfDayByHour(),
      });
      if (next) {
        document.documentElement.setAttribute("data-day-phase", next);
        const nextColor = DAY_PHASE_THEME_COLORS[next];
        if (meta) meta.setAttribute("content", nextColor);
      }
    }, 60_000);

    return () => {
      window.clearInterval(id);
      document.documentElement.removeAttribute("data-day-phase");
    };
  }, [atmosphere, pathname, searchParams]);

  return null;
}
