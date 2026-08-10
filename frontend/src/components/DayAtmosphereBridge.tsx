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
 * Mode change: two-layer wash crossfade via `--day-prev-*` + `data-day-crossfade`.
 */

const CROSSFADE_MS = 520;

function clearDayAtmosphere(root: HTMLElement): void {
  root.removeAttribute("data-day-mode");
  root.removeAttribute("data-day-decor");
  root.removeAttribute("data-day-crossfade");
  for (const key of DAY_ATMOSPHERE_TOKEN_KEYS) {
    root.style.removeProperty(key);
  }
  root.style.removeProperty("--day-prev-bg-base");
  root.style.removeProperty("--day-prev-surface-tint");
  root.style.removeProperty("--day-prev-bg-art");
  root.style.removeProperty("--day-crossfade-ms");
}

function applyDayTokens(root: HTMLElement, tokens: DayAtmosphereTokens): void {
  for (const key of DAY_ATMOSPHERE_TOKEN_KEYS) {
    root.style.setProperty(key, tokens[key]);
  }
}

function prefersReducedMotion(): boolean {
  return window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches === true;
}

/** Phones / touch-first — no ambient atmosphere motion (GPU heat). */
function prefersLiteAtmosphere(): boolean {
  return (
    window.matchMedia?.("(max-width: 48rem)")?.matches === true ||
    window.matchMedia?.("(pointer: coarse)")?.matches === true
  );
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

function readComputedWash(root: HTMLElement): {
  base: string;
  tint: string;
  art: string;
} {
  const cs = getComputedStyle(root);
  return {
    base: cs.getPropertyValue("--day-bg-base").trim() || "#f1f2f4",
    tint: cs.getPropertyValue("--day-surface-tint").trim() || "rgba(241,242,244,0.92)",
    art: cs.getPropertyValue("--day-bg-art").trim() || "none",
  };
}

export function DayAtmosphereBridge() {
  const pathname = usePathname();
  const engineRef = useRef<DayAtmosphereContractWire | null>(null);
  const modeRef = useRef<string | null>(null);
  const crossfadeTimer = useRef<number | null>(null);

  useEffect(() => {
    const root = document.documentElement;
    engineRef.current = readCachedEngine();

    const apply = () => {
      if (!isAppProductRoute(pathname)) {
        clearDayAtmosphere(root);
        modeRef.current = null;
        return;
      }

      const reduced =
        prefersReducedMotion() ||
        prefersLiteAtmosphere() ||
        document.visibilityState === "hidden";
      const contract = resolveDayAtmosphere({
        ...engineFromWire(engineRef.current),
        pinnedMode: readDayModePin(),
        ...(reduced ? { motion: "none" as const } : {}),
      });

      const nextMode = contract.visual_mode;
      const prevMode = modeRef.current;
      const canCrossfade =
        Boolean(prevMode) && prevMode !== nextMode && !prefersReducedMotion() && !prefersLiteAtmosphere();

      if (canCrossfade) {
        const wash = readComputedWash(root);
        root.style.setProperty("--day-prev-bg-base", wash.base);
        root.style.setProperty("--day-prev-surface-tint", wash.tint);
        root.style.setProperty("--day-prev-bg-art", wash.art === "none" ? "none" : wash.art);
        root.style.setProperty("--day-crossfade-ms", `${CROSSFADE_MS}ms`);
        // Hold previous wash on ::after at full opacity (no fade-in), then fade out.
        root.setAttribute("data-day-crossfade", "hold");
      }

      root.setAttribute("data-day-mode", nextMode);
      root.setAttribute("data-day-decor", contract.decor_variant);
      applyDayTokens(root, dayAtmosphereTokens(contract));
      modeRef.current = nextMode;

      if (canCrossfade) {
        if (crossfadeTimer.current) window.clearTimeout(crossfadeTimer.current);
        // Double rAF: paint hold layer, then start opacity→0 transition.
        window.requestAnimationFrame(() => {
          window.requestAnimationFrame(() => {
            root.setAttribute("data-day-crossfade", "out");
            crossfadeTimer.current = window.setTimeout(() => {
              root.removeAttribute("data-day-crossfade");
              root.style.removeProperty("--day-prev-bg-base");
              root.style.removeProperty("--day-prev-surface-tint");
              root.style.removeProperty("--day-prev-bg-art");
              crossfadeTimer.current = null;
            }, CROSSFADE_MS + 40);
          });
        });
      }
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
    const mqReduce = window.matchMedia?.("(prefers-reduced-motion: reduce)");
    const mqNarrow = window.matchMedia?.("(max-width: 48rem)");
    const mqCoarse = window.matchMedia?.("(pointer: coarse)");
    const onMotionPref = () => apply();
    const onVisibility = () => apply();
    mqReduce?.addEventListener?.("change", onMotionPref);
    mqNarrow?.addEventListener?.("change", onMotionPref);
    mqCoarse?.addEventListener?.("change", onMotionPref);
    document.addEventListener("visibilitychange", onVisibility);
    window.addEventListener("storage", onStorage);
    window.addEventListener(DAY_ATMOSPHERE_ENGINE_EVENT, onEngine);

    return () => {
      window.removeEventListener("storage", onStorage);
      window.removeEventListener(DAY_ATMOSPHERE_ENGINE_EVENT, onEngine);
      document.removeEventListener("visibilitychange", onVisibility);
      mqReduce?.removeEventListener?.("change", onMotionPref);
      mqNarrow?.removeEventListener?.("change", onMotionPref);
      mqCoarse?.removeEventListener?.("change", onMotionPref);
      if (crossfadeTimer.current) window.clearTimeout(crossfadeTimer.current);
    };
  }, [pathname]);

  return null;
}
