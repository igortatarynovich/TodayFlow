"use client";

/**
 * Prefetch today's contract + morning into day-bundle cache so /today opens from memory.
 * Safe to call from product shell while user is on other routes.
 */

import { getJson } from "@/lib/api";
import type { MorningRitualData, TodayCycleData } from "@/components/today/todayPageUtils";
import { fetchTodayContractV1, isDayAssembling, isDayNotReady, localCalendarDateISO, type TodayContractV1 } from "@/lib/todayContract";
import { readTodayDayBundle, todayDayBundleIsReady, writeTodayDayBundle } from "@/lib/todayDayBundleCache";

let inFlight: Promise<void> | null = null;
let lastWarmKey = "";

export function warmTodayDayBundle(options?: { force?: boolean }): Promise<void> {
  if (typeof window === "undefined") return Promise.resolve();
  const localDate = localCalendarDateISO();
  const key = localDate;
  if (!options?.force && todayDayBundleIsReady(readTodayDayBundle(localDate))) {
    return Promise.resolve();
  }
  if (!options?.force && inFlight && lastWarmKey === key) return inFlight;

  lastWarmKey = key;
  inFlight = (async () => {
    try {
      const [contract, morning, opening, bundle] = await Promise.all([
        fetchTodayContractV1(localDate).catch(() => null),
        getJson<MorningRitualData>(
          `/morning-ritual/today?target_date=${encodeURIComponent(localDate)}&fast_mode=1`,
        ).catch(() => null),
        getJson<Record<string, unknown>>("/today/opening").catch(() => null),
        getJson<Record<string, unknown>>("/today/bundle").catch(() => null),
      ]);

      let cycle: TodayCycleData | null = null;
      if (opening && bundle) {
        const { assembleTodayCycleFromProgressive } = await import("@/components/today/todayPageUtils");
        cycle = assembleTodayCycleFromProgressive(opening, bundle);
      }

      // Only cache a product-ready day — never warm not_ready/assembling shells as "ready".
      if (contract && (isDayNotReady(contract) || isDayAssembling(contract) || !contract.day_story)) {
        return;
      }

      writeTodayDayBundle(localDate, {
        contract: (contract as TodayContractV1 | null) ?? undefined,
        morning: morning ?? undefined,
        cycle: cycle ?? undefined,
      });
    } catch {
      /* soft warm */
    } finally {
      inFlight = null;
    }
  })();

  return inFlight;
}
