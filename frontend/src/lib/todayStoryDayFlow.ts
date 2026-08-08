/**
 * Story-deck «Поток дня» — pure render of `glance_timeline`.
 *
 * SoT: clocks from geometry; label_short/detail from Kimi (bank fill-empty).
 * Row = clock + valence chrome + title; expand = detail.
 */

import type { GlanceTimelineItem } from "@/lib/todayGlanceTimeline";
import { formatGlanceClock } from "@/lib/todayGlanceTimeline";

export type StoryDayFlowValence = "favorable" | "caution" | "neutral";

export type StoryDayFlowPoint = {
  id: string;
  /** Left rail: clock from glance_timeline. */
  phase: string;
  /** label_short — activity window title. */
  body: string;
  /** Expand трактовка (Kimi detail). */
  detail: string | null;
  valence: StoryDayFlowValence;
  timed?: boolean;
};

export type BuildStoryDayFlowInput = {
  glanceWindows?: GlanceTimelineItem[] | null;
};

const MAX_TIMED_WINDOWS = 5;

function clean(text: string | null | undefined): string {
  return (text || "").replace(/\s+/g, " ").trim();
}

function asValence(raw: string | undefined): StoryDayFlowValence {
  if (raw === "favorable") return "favorable";
  if (raw === "caution") return "caution";
  return "neutral";
}

function timedPoints(windows: GlanceTimelineItem[]): StoryDayFlowPoint[] {
  const sorted = [...windows].sort((a, b) =>
    formatGlanceClock(a.time_local).localeCompare(formatGlanceClock(b.time_local)),
  );
  return sorted
    .slice(0, MAX_TIMED_WINDOWS)
    .map((row, i) => {
      const label = clean(row.label_short);
      const detail = clean(row.detail || "") || null;
      return {
        id: `window-${row.driver_id || i}`,
        phase: formatGlanceClock(row.time_local),
        valence: asValence(String(row.valence || "")),
        body: label,
        detail,
        timed: true,
      };
    })
    .filter((p) => p.body);
}

export function buildStoryDayFlow(input: BuildStoryDayFlowInput = {}): StoryDayFlowPoint[] {
  const windows = (input.glanceWindows || []).filter((w) => clean(w.time_local));
  if (windows.length === 0) return [];
  return timedPoints(windows);
}

export function valenceChromeLabel(valence: StoryDayFlowValence): string {
  if (valence === "favorable") return "Благоприятно";
  if (valence === "caution") return "Осторожнее";
  return "";
}
