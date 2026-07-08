"use client";

import {
  postTodayNarrative,
  type TodayGuideRitualContext,
  type TodayNarrativeApiResponse,
  type TodayNarrativeDepthLevel,
  type TodayNarrativeSurface,
} from "@/lib/todayNarrativeApi";

const CACHE_PREFIX = "todayflow.today_narrative.v1";

type NarrativeRequestBody = Parameters<typeof postTodayNarrative>[0];

type CacheEntry = {
  fetchedAtMs: number;
  targetDate: string;
  cacheKey: string;
  response: TodayNarrativeApiResponse;
};

const inFlight = new Map<string, Promise<TodayNarrativeApiResponse>>();

/** Stable fingerprint for ritual_context — mirrors backend ritual_fp inputs. */
export function ritualContextFingerprint(
  ritual: TodayGuideRitualContext | null | undefined,
): string {
  if (!ritual) return "";
  return [
    ritual.tarot_main_id != null ? String(ritual.tarot_main_id) : "",
    ritual.numerology_value ?? "",
    ritual.mood ?? "",
    ritual.head_topic ?? "",
  ].join("|");
}

/** Client cache key aligned with backend stable narrative cache (date/surface/parent/topic/depth/ritual). */
export function buildTodayNarrativeCacheKey(body: NarrativeRequestBody): string {
  const parent = body.parent_generation_id ?? -1;
  const topic = (body.deepen_topic ?? "").trim().toLowerCase();
  const depth = body.depth_level ?? "";
  const ritual = ritualContextFingerprint(body.ritual_context);
  return `${body.target_date}|${body.surface}|${parent}|${topic}|${depth}|${ritual}`;
}

function storageKey(cacheKey: string): string {
  return `${CACHE_PREFIX}.${cacheKey}`;
}

export function readTodayNarrativeCache(
  body: NarrativeRequestBody,
): TodayNarrativeApiResponse | null {
  if (typeof window === "undefined") return null;
  const cacheKey = buildTodayNarrativeCacheKey(body);
  try {
    const raw = window.sessionStorage.getItem(storageKey(cacheKey));
    if (!raw) return null;
    const entry = JSON.parse(raw) as CacheEntry;
    if (
      entry?.response &&
      entry.targetDate === body.target_date &&
      entry.cacheKey === cacheKey
    ) {
      return entry.response;
    }
  } catch {
    /* ignore corrupt entry */
  }
  return null;
}

export function writeTodayNarrativeCache(
  body: NarrativeRequestBody,
  response: TodayNarrativeApiResponse,
): void {
  if (typeof window === "undefined") return;
  const cacheKey = buildTodayNarrativeCacheKey(body);
  const entry: CacheEntry = {
    fetchedAtMs: Date.now(),
    targetDate: body.target_date,
    cacheKey,
    response,
  };
  try {
    window.sessionStorage.setItem(storageKey(cacheKey), JSON.stringify(entry));
  } catch {
    /* quota */
  }
}

/** Drop cached narrative responses (e.g. on calendar day rollover or sign-out). */
export function clearTodayNarrativeCache(targetDate?: string): void {
  inFlight.clear();
  if (typeof window === "undefined") return;
  if (targetDate) {
    for (let i = window.sessionStorage.length - 1; i >= 0; i -= 1) {
      const key = window.sessionStorage.key(i);
      if (key?.startsWith(CACHE_PREFIX) && key.includes(targetDate)) {
        window.sessionStorage.removeItem(key);
      }
    }
    return;
  }
  for (let i = window.sessionStorage.length - 1; i >= 0; i -= 1) {
    const key = window.sessionStorage.key(i);
    if (key?.startsWith(CACHE_PREFIX)) window.sessionStorage.removeItem(key);
  }
}

/**
 * POST /today/narrative with same-day client dedup:
 * sessionStorage hit → no network; in-flight coalesce → one request per stable key.
 * Use `force: true` after ritual completion or explicit depth change.
 */
export async function fetchTodayNarrativeCached(
  body: NarrativeRequestBody,
  options?: { force?: boolean },
): Promise<TodayNarrativeApiResponse> {
  const force = options?.force ?? false;

  if (!force) {
    const cached = readTodayNarrativeCache(body);
    if (cached) return cached;

    const cacheKey = buildTodayNarrativeCacheKey(body);
    const pending = inFlight.get(cacheKey);
    if (pending) return pending;
  }

  const cacheKey = buildTodayNarrativeCacheKey(body);
  const promise = postTodayNarrative(body)
    .then((response) => {
      writeTodayNarrativeCache(body, response);
      return response;
    })
    .finally(() => {
      inFlight.delete(cacheKey);
    });

  inFlight.set(cacheKey, promise);
  return promise;
}

export type { TodayNarrativeDepthLevel, TodayNarrativeSurface };
