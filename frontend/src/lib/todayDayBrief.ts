/**
 * Block 1 day ambassador model — assemble from existing contract fields only.
 * No invent. Honest omit when empty.
 * Canon: TODAY_SCREEN_SCENARIO_V3 § six blocks · block 1.
 */

import type { TodayContractV1 } from "@/lib/todayContract";
import type { HandoffWelcomeGlass } from "@/lib/todayHandoffWelcome";

export type TodayDayBriefModel = {
  dateLabel: string;
  salutation: string;
  /** Hero vibe title */
  vibe: string | null;
  moodPills: string[];
  activityTags: string[];
  /** Strong sphere / scene accents (labels only) */
  accents: string[];
  /** Configuration / why the day is like this */
  why: string | null;
  energy: string | null;
  energyCause: string | null;
  expect: string | null;
  trap: string | null;
  doItems: string[];
  avoidItems: string[];
  /** Closing vibe / overall tone */
  vibeClosing: string | null;
};

function clean(s: string | null | undefined): string | null {
  const t = String(s || "").trim();
  return t ? t : null;
}

function uniqTrim(items: Array<string | null | undefined>, max: number): string[] {
  const out: string[] = [];
  const seen = new Set<string>();
  for (const raw of items) {
    const t = clean(raw);
    if (!t) continue;
    const key = t.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(t);
    if (out.length >= max) break;
  }
  return out;
}

/** Prefer longer non-duplicate why sources for ambassador paragraph. */
function pickWhy(parts: Array<string | null | undefined>): string | null {
  const cleaned = parts.map(clean).filter(Boolean) as string[];
  if (!cleaned.length) return null;
  // Prefer longest substantive paragraph; drop near-duplicates.
  cleaned.sort((a, b) => b.length - a.length);
  const primary = cleaned[0];
  return primary;
}

function sceneAccents(contract: TodayContractV1): string[] {
  const scenes = contract.day_story?.day_scenario?.scenes;
  if (!Array.isArray(scenes) || !scenes.length) return [];
  const primary = scenes.filter((s) => String(s.role_in_story || "").toLowerCase() === "primary");
  const pool = primary.length ? primary : scenes;
  return uniqTrim(
    pool.map((s) => s.sphere_label_ru || s.sphere || null),
    3,
  );
}

export function buildTodayDayBriefModel(input: {
  contract: TodayContractV1;
  dateLabel: string;
  salutation: string;
  headline?: string | null;
  welcomeGlass?: HandoffWelcomeGlass | null;
  energyLine?: string | null;
  energyCause?: string | null;
  loading?: boolean;
}): TodayDayBriefModel {
  const story = input.contract.day_story;
  const glass = input.welcomeGlass;

  const vibe =
    clean(input.headline) ||
    clean(story?.headline_anchor) ||
    clean(story?.theme) ||
    clean(story?.day_thesis?.label_ru) ||
    clean(story?.day_thesis?.label) ||
    clean(input.contract.global_context?.period) ||
    null;

  const essence =
    clean(story?.day_foundation?.essence?.theme) ||
    clean(story?.day_foundation?.essence?.story_ru) ||
    null;

  const why = pickWhy([
    glass?.reasonLine,
    story?.events_lead,
    story?.day_scenario?.conflict?.why_arose,
    essence,
    story?.day_personal?.summary_ru,
  ]);

  const doItems = uniqTrim(story?.do || [], 3);
  const avoidItems = uniqTrim(story?.avoid || [], 3);

  let vibeClosing =
    clean(story?.vibe_closing) ||
    (Array.isArray(story?.vibe_strokes) && story.vibe_strokes.length
      ? uniqTrim(story.vibe_strokes, 4).join(" · ")
      : null) ||
    clean(story?.story) ||
    null;
  if (vibeClosing && (vibeClosing === vibe || vibeClosing === why)) {
    vibeClosing = null;
  }

  return {
    dateLabel: input.dateLabel,
    salutation: input.salutation,
    vibe: input.loading ? null : vibe,
    moodPills: uniqTrim(glass?.moodPills || [], 3),
    activityTags: uniqTrim(glass?.activityTags || [], 3),
    accents: sceneAccents(input.contract),
    why,
    energy: clean(input.energyLine),
    energyCause: clean(input.energyCause),
    expect: clean(story?.expect),
    trap: clean(story?.trap),
    doItems,
    avoidItems,
    vibeClosing,
  };
}
