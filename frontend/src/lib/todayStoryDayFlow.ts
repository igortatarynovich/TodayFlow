/**
 * Story-deck «Поток дня» — pure render of `glance_timeline`.
 *
 * SoT: docs/today/TODAY_WAVE2_CONTRACT_V1.md §1/§4 + tracker
 * «Поток дня ← real glance_timeline (no invented phase copy)».
 * No invented Утро/День/Вечер/Ночь bodies. Empty windows → [].
 */

import type { GlanceTimelineItem } from "@/lib/todayGlanceTimeline";
import { formatGlanceClock } from "@/lib/todayGlanceTimeline";

export type StoryDayFlowValence = "favorable" | "caution" | "neutral";

export type StoryDayFlowPoint = {
  id: string;
  /** Left rail: clock from glance_timeline. */
  phase: string;
  /** label_short from API — no FE prose invent. */
  body: string;
  valence: StoryDayFlowValence;
  /** Cue from valence only (chrome, not product plot). */
  cue: string;
  /** Always true for glance rows. */
  timed?: boolean;
};

export type BuildStoryDayFlowInput = {
  /** Real exact-time windows from day_facts.glance_timeline. */
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
  return sorted.slice(0, MAX_TIMED_WINDOWS).map((row, i) => {
    const valence = asValence(String(row.valence || ""));
    const label = clean(row.label_short);
    return {
      id: `window-${row.driver_id || i}`,
      phase: formatGlanceClock(row.time_local),
      cue: valence === "favorable" ? "Благоприятно" : valence === "caution" ? "Осторожнее" : "Окно",
      valence,
      body: label,
      timed: true,
    };
  }).filter((p) => p.body);
}

/**
 * Поток дня = only timed glance rows. No phase framing invent.
 */
export function buildStoryDayFlow(input: BuildStoryDayFlowInput = {}): StoryDayFlowPoint[] {
  const windows = (input.glanceWindows || []).filter((w) => clean(w.time_local));
  if (windows.length === 0) return [];
  return timedPoints(windows);
}
