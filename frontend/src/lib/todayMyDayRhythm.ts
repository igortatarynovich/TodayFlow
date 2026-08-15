/**
 * MY DAY personal timeline — natal clocks × Engine window facts.
 * Canon: docs/today/TODAY_PRODUCT_FLOW_V1.md §3 · TODAY_CONTENT_PIPELINE_V1.
 * Glance clocks = geometry. supports/cautions = Global Engine. No invent.
 * No natal activations → empty (omit), never dump Global windows as «mine».
 */

import { GLOBAL_ACTION_TYPE_LABELS_RU } from "@/lib/todayDayBrief";
import { formatGlanceClock, type GlanceTimelineItem } from "@/lib/todayGlanceTimeline";
import type { TodayContractGlobalDayWindowV1 } from "@/lib/todayContract";

export type TodayMyDayRhythmRow = {
  id: string;
  time: string;
  /** Next clock, if any — presentation range, not a new Engine fact. */
  timeEnd: string | null;
  timeLabel: string;
  title: string;
  supports: string[];
  cautions: string[];
  detail: string | null;
};

const MAX_ROWS = 5;
const MATCH_MINUTES = 90;

function clean(s: string | null | undefined): string | null {
  const t = String(s || "").replace(/\s+/g, " ").trim();
  return t ? t : null;
}

function hhmmToMinutes(hhmm: string): number | null {
  const m = hhmm.match(/^(\d{1,2}):(\d{2})$/);
  if (!m) return null;
  return Number(m[1]) * 60 + Number(m[2]);
}

function actionLabels(raw: unknown): string[] {
  if (!Array.isArray(raw)) return [];
  const out: string[] = [];
  const seen = new Set<string>();
  for (const item of raw) {
    const key = String(item || "")
      .trim()
      .toLowerCase()
      .replace(/-/g, "_");
    const label = GLOBAL_ACTION_TYPE_LABELS_RU[key];
    if (!label || seen.has(key)) continue;
    seen.add(key);
    out.push(label);
  }
  return out.slice(0, 4);
}

function matchWindow(
  clock: string,
  driverId: string,
  windows: TodayContractGlobalDayWindowV1[],
): TodayContractGlobalDayWindowV1 | null {
  const did = String(driverId || "").trim();
  if (did) {
    const byId = windows.find((win) => String(win.driver_id || "").trim() === did);
    if (byId) return byId;
  }
  const t = hhmmToMinutes(clock);
  if (t == null) return null;
  let best: TodayContractGlobalDayWindowV1 | null = null;
  let bestDelta = MATCH_MINUTES + 1;
  for (const win of windows) {
    const wt = hhmmToMinutes(formatGlanceClock(String(win.time || "")));
    if (wt == null) continue;
    const delta = Math.abs(wt - t);
    if (delta < bestDelta) {
      bestDelta = delta;
      best = win;
    }
  }
  return bestDelta <= MATCH_MINUTES ? best : null;
}

export function buildTodayMyDayRhythm(input: {
  glanceRows?: GlanceTimelineItem[] | null;
  windows?: TodayContractGlobalDayWindowV1[] | null;
}): TodayMyDayRhythmRow[] {
  const glance = (input.glanceRows || []).filter((row) => clean(row.time_local));
  if (!glance.length) return [];
  const windows = (input.windows || []).filter((win) => clean(win.time) || clean(win.driver_id));
  const sorted = [...glance].sort((a, b) =>
    formatGlanceClock(a.time_local).localeCompare(formatGlanceClock(b.time_local)),
  );
  const out: TodayMyDayRhythmRow[] = [];
  for (let i = 0; i < sorted.length; i += 1) {
    if (out.length >= MAX_ROWS) break;
    const row = sorted[i];
    const time = formatGlanceClock(row.time_local);
    const title = clean(row.label_short);
    if (!title) continue;
    const win = matchWindow(time, String(row.driver_id || ""), windows);
    out.push({
      id: String(row.driver_id || `window-${i}`),
      time,
      timeEnd: null,
      timeLabel: time,
      title,
      supports: actionLabels(win?.supports),
      cautions: actionLabels(win?.cautions),
      detail: clean(row.detail),
    });
  }
  for (let i = 0; i < out.length; i += 1) {
    const next = out[i + 1];
    if (!next) continue;
    out[i].timeEnd = next.time;
    out[i].timeLabel = `${out[i].time}–${next.time}`;
  }
  return out;
}
