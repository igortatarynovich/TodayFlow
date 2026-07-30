/**
 * Wave 2 Phase D.1 — day_facts_v1 client (slot envelope).
 * One GET for VerdictStrip + GlanceTimeline; short TTL + in-flight dedupe.
 */

import { getJson } from "@/lib/api";
import type { DomainVerdict } from "@/lib/todayDomainVerdicts";
import type { GlanceTimelineItem } from "@/lib/todayGlanceTimeline";

export type DayFactsProvenance = {
  conflict_driver_ids: string[];
  verdict_driver_ids: Record<string, string[]>;
  timeline_driver_ids: string[];
};

export type DayFactsResponse = {
  schema_version: string;
  id: string;
  user_id: string;
  date: string;
  timezone: string;
  generated_at: string;
  natal_activations: Record<string, unknown>[];
  domain_verdicts: DomainVerdict[];
  glance_timeline: GlanceTimelineItem[];
  generation_provenance: DayFactsProvenance;
  degraded?: boolean;
  is_fallback?: boolean;
  partial?: boolean;
};

const TTL_MS = 60_000;
const cache = new Map<string, { at: number; data: DayFactsResponse }>();
const inFlight = new Map<string, Promise<DayFactsResponse>>();

function cacheKey(dateISO: string): string {
  return dateISO || "__today__";
}

/** Drop client day-facts cache (tests / day rollover). */
export function clearDayFactsCache(): void {
  cache.clear();
  inFlight.clear();
}

export async function fetchDayFacts(dateISO: string): Promise<DayFactsResponse> {
  const key = cacheKey(dateISO);
  const hit = cache.get(key);
  if (hit && Date.now() - hit.at < TTL_MS) return hit.data;

  const pending = inFlight.get(key);
  if (pending) return pending;

  const q = dateISO ? `?local_date=${encodeURIComponent(dateISO)}` : "";
  const promise = getJson<DayFactsResponse>(`/today/day-facts${q}`)
    .then((data) => {
      cache.set(key, { at: Date.now(), data });
      return data;
    })
    .finally(() => {
      inFlight.delete(key);
    });

  inFlight.set(key, promise);
  return promise;
}
