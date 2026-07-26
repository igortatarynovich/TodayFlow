"use client";

import type { MorningRitualData, TodayCycleData } from "@/components/today/todayPageUtils";
import { resolveCacheUserScope } from "@/lib/cacheUserScope";
import type { TodayContractV1 } from "@/lib/todayContract";

const PREFIX = "todayflow.today_day_bundle.v2";

export type TodayDayBundle = {
  savedAt: number;
  localDate: string;
  contract: TodayContractV1 | null;
  morning: MorningRitualData | null;
  cycle: TodayCycleData | null;
};

function storageKey(localDate: string): string {
  return `${PREFIX}.${resolveCacheUserScope()}.${localDate}`;
}

function isPlausibleContract(value: unknown): value is TodayContractV1 {
  return Boolean(value && typeof value === "object" && typeof (value as TodayContractV1).contract_version === "string");
}

function isPlausibleCycle(value: unknown): value is TodayCycleData {
  return Boolean(value && typeof value === "object" && typeof (value as TodayCycleData).date === "string");
}

export function readTodayDayBundle(localDate: string): TodayDayBundle | null {
  if (typeof window === "undefined" || !localDate) return null;
  try {
    const raw = sessionStorage.getItem(storageKey(localDate)) ?? localStorage.getItem(storageKey(localDate));
    if (!raw) return null;
    const parsed = JSON.parse(raw) as TodayDayBundle;
    if (!parsed || parsed.localDate !== localDate) return null;
    if (!isPlausibleContract(parsed.contract) && !isPlausibleCycle(parsed.cycle)) return null;
    return {
      savedAt: typeof parsed.savedAt === "number" ? parsed.savedAt : Date.now(),
      localDate,
      contract: isPlausibleContract(parsed.contract) ? parsed.contract : null,
      morning: parsed.morning && typeof parsed.morning === "object" ? parsed.morning : null,
      cycle: isPlausibleCycle(parsed.cycle) ? parsed.cycle : null,
    };
  } catch {
    return null;
  }
}

export function writeTodayDayBundle(
  localDate: string,
  patch: Partial<Pick<TodayDayBundle, "contract" | "morning" | "cycle">>,
): TodayDayBundle | null {
  if (typeof window === "undefined" || !localDate) return null;
  const prev = readTodayDayBundle(localDate);
  const next: TodayDayBundle = {
    savedAt: Date.now(),
    localDate,
    contract: patch.contract !== undefined ? patch.contract : prev?.contract ?? null,
    morning: patch.morning !== undefined ? patch.morning : prev?.morning ?? null,
    cycle: patch.cycle !== undefined ? patch.cycle : prev?.cycle ?? null,
  };
  if (!next.contract && !next.cycle) return null;
  try {
    const raw = JSON.stringify(next);
    sessionStorage.setItem(storageKey(localDate), raw);
    try {
      localStorage.setItem(storageKey(localDate), raw);
    } catch {
      /* quota */
    }
  } catch {
    /* ignore */
  }
  return next;
}

export function clearTodayDayBundle(localDate: string): void {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.removeItem(storageKey(localDate));
    localStorage.removeItem(storageKey(localDate));
  } catch {
    /* ignore */
  }
}

/** True when we can paint Today without waiting on network (product-ready day package). */
export function todayDayBundleIsReady(bundle: TodayDayBundle | null | undefined): boolean {
  const contract = bundle?.contract;
  if (!bundle?.cycle || !contract) return false;
  if (!contract.day_story) return false;
  const status = String(
    (contract.progress as { day_lifecycle?: { status?: string } } | undefined)?.day_lifecycle?.status || "",
  );
  if (status === "day_not_ready" || status === "assembling") return false;
  if ((contract.generation_id || "").trim() === "day-not-ready-c5") return false;
  if ((contract.generation_id || "").trim() === "day-assembling-c5") return false;
  return true;
}
