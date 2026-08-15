/**
 * MY DAY day clock — natal clocks × Engine windows, else Global windows × drivers.
 * Canon: docs/today/TODAY_PRODUCT_FLOW_V1.md §3 · TODAY_CONTENT_PIPELINE_V1.
 * Natal spine when glance clocks exist. Otherwise timed Global transits (not labelled «mine»).
 * No invent. Untitled windows omit.
 */

import {
  GLOBAL_ACTION_TYPE_LABELS_RU,
  driverKindLabel,
  driverPlanets,
} from "@/lib/todayDayBrief";
import { formatGlanceClock, type GlanceTimelineItem } from "@/lib/todayGlanceTimeline";
import type { TodayContractGlobalDayWindowV1 } from "@/lib/todayContract";

export type TodayMyDayRhythmSource = "natal" | "global";

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
  source: TodayMyDayRhythmSource;
  planets: string[];
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

export type TodayRhythmDriver = {
  id?: string;
  kind?: string;
  fact_ru?: string;
};

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

function applyRanges(rows: TodayMyDayRhythmRow[]): TodayMyDayRhythmRow[] {
  for (let i = 0; i < rows.length; i += 1) {
    const next = rows[i + 1];
    if (!next) continue;
    rows[i].timeEnd = next.time;
    rows[i].timeLabel = `${rows[i].time}–${next.time}`;
  }
  return rows;
}

function buildFromNatal(
  glance: GlanceTimelineItem[],
  windows: TodayContractGlobalDayWindowV1[],
): TodayMyDayRhythmRow[] {
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
    const id = String(row.driver_id || `window-${i}`);
    out.push({
      id,
      time,
      timeEnd: null,
      timeLabel: time,
      title,
      supports: actionLabels(win?.supports),
      cautions: actionLabels(win?.cautions),
      detail: clean(row.detail),
      source: "natal",
      planets: driverPlanets(null, title, id),
    });
  }
  return applyRanges(out);
}

function buildFromGlobalWindows(
  windows: TodayContractGlobalDayWindowV1[],
  drivers: TodayRhythmDriver[],
): TodayMyDayRhythmRow[] {
  const driverById = new Map<string, TodayRhythmDriver>();
  for (let i = 0; i < drivers.length; i += 1) {
    const id = String(drivers[i].id || "").trim();
    if (id) driverById.set(id, drivers[i]);
  }
  const timed: TodayContractGlobalDayWindowV1[] = [];
  for (let i = 0; i < windows.length; i += 1) {
    const time = clean(windows[i].time);
    if (!time || hhmmToMinutes(formatGlanceClock(time)) == null) continue;
    timed.push(windows[i]);
  }
  timed.sort((a, b) =>
    formatGlanceClock(String(a.time || "")).localeCompare(formatGlanceClock(String(b.time || ""))),
  );
  const out: TodayMyDayRhythmRow[] = [];
  const seen = new Set<string>();
  for (let i = 0; i < timed.length; i += 1) {
    if (out.length >= MAX_ROWS) break;
    const win = timed[i];
    const time = formatGlanceClock(String(win.time || ""));
    const did = String(win.driver_id || "").trim();
    const driver = did ? driverById.get(did) : undefined;
    const title = clean(driver?.fact_ru) || driverKindLabel(driver?.kind);
    if (!title) continue;
    const key = `${time}:${title}`;
    if (seen.has(key)) continue;
    seen.add(key);
    const id = did || `win-${i}`;
    out.push({
      id,
      time,
      timeEnd: null,
      timeLabel: time,
      title,
      supports: actionLabels(win.supports),
      cautions: actionLabels(win.cautions),
      detail: null,
      source: "global",
      planets: driverPlanets(driver?.kind, driver?.fact_ru, id),
    });
  }
  return applyRanges(out);
}

export function buildTodayMyDayRhythm(input: {
  glanceRows?: GlanceTimelineItem[] | null;
  windows?: TodayContractGlobalDayWindowV1[] | null;
  drivers?: TodayRhythmDriver[] | null;
}): TodayMyDayRhythmRow[] {
  const glance = (input.glanceRows || []).filter((row) => clean(row.time_local));
  const windows = (input.windows || []).filter((win) => clean(win.time) || clean(win.driver_id));
  if (glance.length) {
    return buildFromNatal(glance, windows);
  }
  return buildFromGlobalWindows(windows, input.drivers || []);
}
