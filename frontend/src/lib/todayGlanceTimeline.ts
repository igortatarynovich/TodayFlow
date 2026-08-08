/**
 * Wave 2 Phase C — GlanceTimeline client.
 */

import { getJson } from "@/lib/api";

export type GlanceValence = "favorable" | "caution";

export type GlanceTimelineItem = {
  time_local: string;
  label_short: string;
  valence: GlanceValence | string;
  driver_id: string;
  /** Kimi expand body — activity window трактовка. */
  detail?: string | null;
  copy_source?: "kimi_v1" | "bank_fill" | string | null;
};

export type GlanceTimelineResponse = {
  schema_version: string;
  local_date: string;
  day_facts_id: string;
  glance_timeline: GlanceTimelineItem[];
  degraded?: boolean;
  is_fallback?: boolean;
};

export async function fetchGlanceTimeline(dateISO: string): Promise<GlanceTimelineResponse> {
  const q = dateISO ? `?local_date=${encodeURIComponent(dateISO)}` : "";
  return getJson<GlanceTimelineResponse>(`/today/glance-timeline${q}`);
}

/** Format HH:MM in local display from ISO / datetime string. */
export function formatGlanceClock(timeLocal: string): string {
  const raw = (timeLocal || "").trim();
  if (!raw) return "—";
  // Already HH:MM
  if (/^\d{1,2}:\d{2}$/.test(raw)) return raw;
  const m = raw.match(/T(\d{2}):(\d{2})/);
  if (m) return `${m[1]}:${m[2]}`;
  try {
    const d = new Date(raw);
    if (!Number.isNaN(d.getTime())) {
      return d.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" });
    }
  } catch {
    /* noop */
  }
  return raw.slice(0, 5);
}

/** True when now is within ±45 minutes of the marker (live-now class). */
export function isGlanceLiveNow(timeLocal: string, now: Date = new Date()): boolean {
  const raw = (timeLocal || "").trim();
  if (!raw) return false;
  let target: Date | null = null;
  try {
    const parsed = new Date(raw);
    if (!Number.isNaN(parsed.getTime())) target = parsed;
  } catch {
    target = null;
  }
  if (!target) {
    const m = raw.match(/T(\d{2}):(\d{2})/);
    if (m) {
      target = new Date(now);
      target.setHours(Number(m[1]), Number(m[2]), 0, 0);
    }
  }
  if (!target) return false;
  const deltaMs = Math.abs(now.getTime() - target.getTime());
  return deltaMs <= 45 * 60 * 1000;
}
