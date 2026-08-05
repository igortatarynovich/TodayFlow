/**
 * Wave 2 Phase D.1 / D.1b — day_facts_v1 client.
 * One GET for slots (+ narrative when partial=false); short TTL + in-flight dedupe.
 */

import { getJson } from "@/lib/api";
import type { DomainVerdict } from "@/lib/todayDomainVerdicts";
import type { GlanceTimelineItem } from "@/lib/todayGlanceTimeline";

export type DayFactsProvenance = {
  conflict_driver_ids: string[];
  verdict_driver_ids: Record<string, string[]>;
  timeline_driver_ids: string[];
};

export type DayFactsConflict = {
  short_name: string;
  thesis: string | null;
  opposing_forces: { a: string; b: string };
  why_arose: string;
  why_personal: string | null;
  driver_ids: string[];
};

export type DayFactsScene = {
  id: string;
  sphere: string;
  role_in_story: string;
  what_happens: string;
  opportunity: string;
  trap: string;
  recommended_action: string;
  do_not: string;
  domestic_example: string | null;
  driver_ids: string[];
};

export type DayFactsProps = {
  color: { name: string; link_to_conflict?: string | null; where_to_use?: string | null } | null;
  avoid_color: { name: string; amplifies_trap?: string | null } | null;
  practice_or_promise: {
    text: string;
    window?: string | null;
    serves_conflict?: string | null;
  } | null;
  affirmation: { text: string; compensates_trap?: string | null } | null;
  humor: { text: string; serves_conflict?: string | null } | null;
  evening_payoff: string | null;
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
  conflict?: DayFactsConflict | null;
  scenes?: DayFactsScene[];
  props?: DayFactsProps | null;
  /** Removed from contract 2026-08-01 — wire may still send []; ignore. */
  sky_drivers?: Array<Record<string, unknown>>;
  moon_phase?: {
    illumination_pct: number | null;
    phase: string | null;
    is_new: boolean;
    is_full: boolean;
  } | null;
  numerology?: { personal_day: number; source: string } | null;
  generation_provenance: DayFactsProvenance;
  degraded?: boolean;
  is_fallback?: boolean;
  /** true when narrative omitted (cache miss or temporal gate) */
  partial?: boolean;
};

const TTL_MS = 60_000;
const FETCH_TIMEOUT_MS = 8_000;
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
  const controller = new AbortController();
  const timeoutId = setTimeout(() => {
    try {
      controller.abort(
        typeof DOMException !== "undefined"
          ? new DOMException("Request timed out.", "TimeoutError")
          : undefined,
      );
    } catch {
      controller.abort();
    }
  }, FETCH_TIMEOUT_MS);

  const promise = getJson<DayFactsResponse>(`/today/day-facts${q}`, { signal: controller.signal })
    .then((data) => {
      cache.set(key, { at: Date.now(), data });
      return data;
    })
    .finally(() => {
      clearTimeout(timeoutId);
      inFlight.delete(key);
    });

  inFlight.set(key, promise);
  return promise;
}
