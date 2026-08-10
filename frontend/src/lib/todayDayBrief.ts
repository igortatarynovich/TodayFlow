/**
 * Block 1 day ambassador model — assemble from existing contract fields only.
 * No invent. Honest omit when empty.
 * Canon: TODAY_SCREEN_SCENARIO_V3 § six blocks · block 1
 *         EXPLAIN_MEANING_NOT_MECHANISM — kitchen/ephemeris never in why.
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

/** Kitchen / ephemeris dump — defensive FE mirror of BE value gate. */
const KITCHEN_MECHANISM_RE =
  /профекц|секундарн\w*\s+прогресс|прогресс\.?\s*солнц|прогресс\.?\s*лун|solar\s*return|управител|нет\s+времени\/места|активных\s+личных\s+транзит|firdaria|vimshottari|\bzr\s*(?:fortune|spirit)\b|time[_\s-]?lords|\d+(?:[.,]\d+)?°|возраст\s+\d+(?:[.,]\d+)?\s*лет|дата\s+19\d{2}-\d{2}-\d{2}|дата\s+20\d{2}-\d{2}-\d{2}/i;

function clean(s: string | null | undefined): string | null {
  const t = String(s || "").trim();
  return t ? t : null;
}

/** Meaning-only line for ambassador why — reject kitchen dumps. */
export function cleanAmbassadorWhy(s: string | null | undefined): string | null {
  const t = clean(s);
  if (!t) return null;
  if (KITCHEN_MECHANISM_RE.test(t)) return null;
  // Long mash of several kitchen sentences — not a why paragraph.
  if (t.length > 320 && (t.match(/\./g) || []).length >= 4) return null;
  return t;
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

/** Clip to first 1–2 sentences for 3-second compass scan. No invent. */
export function clipCompassProse(s: string | null | undefined, maxChars = 180): string | null {
  const t = clean(s);
  if (!t) return null;
  if (t.length <= maxChars) return t;
  const parts = t.split(/(?<=[.!?…])\s+/).filter(Boolean);
  let out = parts[0] || t.slice(0, maxChars);
  if (parts.length > 1 && (out + " " + parts[1]).length <= maxChars + 24) {
    out = `${out} ${parts[1]}`;
  }
  if (out.length > maxChars + 40) {
    out = out.slice(0, maxChars).replace(/\s+\S*$/, "").trim();
  }
  return out.endsWith(".") || out.endsWith("!") || out.endsWith("?") || out.endsWith("…")
    ? out
    : `${out}…`;
}

/**
 * Prefer meaning slots in product order — never pick longest kitchen dump.
 * day_personal.summary_ru is kitchen evidence mash; not used for ambassador why.
 */
function pickWhy(parts: Array<string | null | undefined>): string | null {
  for (const part of parts) {
    const ok = cleanAmbassadorWhy(part);
    if (ok) return clipCompassProse(ok, 200);
  }
  return null;
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
    story?.day_scenario?.conflict?.why_arose,
    glass?.reasonLine,
    essence,
    story?.events_lead,
    // Explicitly skip day_personal.summary_ru — kitchen mash (profections/SR/…).
  ]);

  const doItems = uniqTrim(story?.do || [], 2).map((item) => clipCompassProse(item, 140) || item);
  const avoidItems = uniqTrim(story?.avoid || [], 2).map((item) => clipCompassProse(item, 120) || item);

  // Ambient list only — full scene story is not «общий вайб».
  let vibeClosing =
    clean(story?.vibe_closing) ||
    (Array.isArray(story?.vibe_strokes) && story.vibe_strokes.length
      ? uniqTrim(story.vibe_strokes, 4).join(" · ")
      : null);
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
    energy: clipCompassProse(input.energyLine, 140),
    energyCause: clipCompassProse(cleanAmbassadorWhy(input.energyCause), 120),
    expect: clipCompassProse(story?.expect, 160),
    trap: clipCompassProse(story?.trap, 140),
    doItems,
    avoidItems,
    vibeClosing: vibeClosing ? clipCompassProse(vibeClosing, 160) : null,
  };
}
