"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";
import {
  DAY_ATMOSPHERE_TOKEN_KEYS,
  DAY_MODE_PIN_STORAGE_KEY,
  dayAtmosphereTokens,
  readDayModePin,
  resolveDayAtmosphere,
  type DayAtmosphereTokens,
} from "@/lib/dayAtmosphere";
import { isAppProductRoute } from "@/lib/sectionAtmosphere";

/**
 * Day Atmosphere bridge (FOUNDATION_UI §13).
 *
 * Writes `data-day-mode` + inline `--day-*` on `<html>` for product routes.
 * Resolves pin → default `clarity` for now; day-narrative engine wiring is backlog (§13.4).
 * Mirrors `SectionAtmosphereBridge` placement in the root layout — not per-page.
 */

function clearDayAtmosphere(root: HTMLElement): void {
  root.removeAttribute("data-day-mode");
  for (const key of DAY_ATMOSPHERE_TOKEN_KEYS) {
    root.style.removeProperty(key);
  }
}

function applyDayTokens(root: HTMLElement, tokens: DayAtmosphereTokens): void {
  for (const key of DAY_ATMOSPHERE_TOKEN_KEYS) {
    root.style.setProperty(key, tokens[key]);
  }
}

function prefersReducedMotion(): boolean {
  return window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches === true;
}

export function DayAtmosphereBridge() {
  const pathname = usePathname();

  useEffect(() => {
    const root = document.documentElement;

    const apply = () => {
      if (!isAppProductRoute(pathname)) {
        clearDayAtmosphere(root);
        return;
      }

      const reduced = prefersReducedMotion();
      const contract = resolveDayAtmosphere({
        pinnedMode: readDayModePin(),
        ...(reduced ? { motion: "none" as const } : {}),
      });

      root.setAttribute("data-day-mode", contract.visual_mode);
      applyDayTokens(root, dayAtmosphereTokens(contract));
    };

    apply();

    const onStorage = (e: StorageEvent) => {
      if (e.key === DAY_MODE_PIN_STORAGE_KEY) apply();
    };
    const mq = window.matchMedia?.("(prefers-reduced-motion: reduce)");
    const onMotionPref = () => apply();
    mq?.addEventListener?.("change", onMotionPref);
    window.addEventListener("storage", onStorage);

    return () => {
      window.removeEventListener("storage", onStorage);
      mq?.removeEventListener?.("change", onMotionPref);
      clearDayAtmosphere(root);
    };
  }, [pathname]);

  return null;
}
