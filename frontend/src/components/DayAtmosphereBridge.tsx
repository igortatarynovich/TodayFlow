"use client";

import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";
import {
  DAY_ATMOSPHERE_TOKEN_KEYS,
  DAY_MODE_PIN_STORAGE_KEY,
  dayAtmosphereTokens,
  readDayModePin,
  resolveDayAtmosphere,
  type DayAtmosphereTokens,
  type ResolveDayAtmosphereInput,
} from "@/lib/dayAtmosphere";
import { isAppProductRoute } from "@/lib/sectionAtmosphere";
import {
  DAY_ATMOSPHERE_ENGINE_EVENT,
  localCalendarDateISO,
  type DayAtmosphereContractWire,
} from "@/lib/todayContract";
import { readTodayDayBundle } from "@/lib/todayDayBundleCache";

/**
 * Day Atmosphere bridge (FOUNDATION_UI §13).
 *
 * Writes `data-day-mode` + inline `--day-*` on `<html>` for **all product routes**.
 * Day mood is app-wide shell SoT — not scoped to /today only.
 * Resolves: pin → engine nest (`day_atmosphere` from Today contract) → default clarity.
 */

function clearDayAtmosphere(root: HTMLElement): void {
  root.removeAttribute("data-day-mode");
  root.removeAttribute("data-day-decor");
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

function engineFromWire(
  nest: DayAtmosphereContractWire | null | undefined,
): ResolveDayAtmosphereInput {
  if (!nest || typeof nest !== "object") return {};
  return {
    visual_mode: nest.visual_mode as ResolveDayAtmosphereInput["visual_mode"],
    intensity: nest.intensity,
    warmth: nest.warmth,
    motion: nest.motion as ResolveDayAtmosphereInput["motion"],
    contrast: nest.contrast as ResolveDayAtmosphereInput["contrast"],
    decor_variant: nest.decor_variant,
    time_phase: nest.time_phase as ResolveDayAtmosphereInput["time_phase"],
  };
}

function readCachedEngine(): DayAtmosphereContractWire | null {
  const bundle = readTodayDayBundle(localCalendarDateISO());
  const nest = bundle?.contract?.day_atmosphere;
  if (!nest || typeof nest !== "object") return null;
  return nest;
}

export function DayAtmosphereBridge() {
  const pathname = usePathname();
  const engineRef = useRef<DayAtmosphereContractWire | null>(null);

  useEffect(() => {
    const root = document.documentElement;
    engineRef.current = readCachedEngine();

    const apply = () => {
      if (!isAppProductRoute(pathname)) {
        clearDayAtmosphere(root);
        return;
      }

      const reduced = prefersReducedMotion();
      const contract = resolveDayAtmosphere({
        ...engineFromWire(engineRef.current),
        pinnedMode: readDayModePin(),
        ...(reduced ? { motion: "none" as const } : {}),
      });

      root.setAttribute("data-day-mode", contract.visual_mode);
      root.setAttribute("data-day-decor", contract.decor_variant);
      applyDayTokens(root, dayAtmosphereTokens(contract));
    };

    apply();

    const onStorage = (e: StorageEvent) => {
      if (e.key === DAY_MODE_PIN_STORAGE_KEY) apply();
    };
    const onEngine = (e: Event) => {
      const detail = (e as CustomEvent<DayAtmosphereContractWire | null>).detail;
      engineRef.current = detail ?? null;
      apply();
    };
    const mq = window.matchMedia?.("(prefers-reduced-motion: reduce)");
    const onMotionPref = () => apply();
    mq?.addEventListener?.("change", onMotionPref);
    window.addEventListener("storage", onStorage);
    window.addEventListener(DAY_ATMOSPHERE_ENGINE_EVENT, onEngine);

    return () => {
      window.removeEventListener("storage", onStorage);
      window.removeEventListener(DAY_ATMOSPHERE_ENGINE_EVENT, onEngine);
      mq?.removeEventListener?.("change", onMotionPref);
      clearDayAtmosphere(root);
    };
  }, [pathname]);

  return null;
}
