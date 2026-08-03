/**
 * Reading Screen 3 (v3.1) — sphere cards from day_scenario.scenes.
 * Conflict → Plot; symbols/astro → Symbols; color + day action → Move.
 * Per sphere: why / opportunity / trap only — no recommended_action (Move owns do/avoid).
 * Canon: docs/today/TODAY_SCREEN_SCENARIO_V3.md · docs/DAY_SCENARIO_V1.md
 */

import type { TodayContractV1 } from "@/lib/todayContract";
import type { TodayDayColorGuide } from "@/lib/todayDayColorGuide";
import type { TodayDayNarrativeChapter } from "@/lib/todayDayNarrative";

function clean(text: string | null | undefined): string {
  return (text ?? "").replace(/\s+/g, " ").trim();
}

/** Strip mashed "A или B — пока <fact…>" / calendar glue from cached short_name / theme. */
export function sanitizeConflictLabel(text: string | null | undefined): string {
  let t = clean(text);
  if (!t) return "";
  const mashed = t.match(/^(.+?\s+или\s+.+?)\s+[—–-]\s+(?:пока\s+|календарн)/iu);
  if (mashed?.[1]) t = mashed[1].trim();
  if (/\sили\s/iu.test(t) && /\s+[—–-]\s+/.test(t)) {
    const [before, after = ""] = t.split(/\s+[—–-]\s+/);
    if (
      before &&
      /\sили\s/iu.test(before) &&
      (/^пока\s/iu.test(after) || /календарн/iu.test(after) || after.includes("…"))
    ) {
      t = before.trim();
    }
  }
  if (t.includes("…") && /\sили\s/iu.test(t)) {
    const before = t.split(/\s+[—–-]\s+/)[0]?.trim();
    if (before && /\sили\s/iu.test(before)) t = before;
  }
  return t.replace(/[.!?]+$/u, "").trim();
}

/** Calendar DOY — date already in greeting chrome; never user-facing day prose. */
export function isCalendarKitchenFact(text: string | null | undefined): boolean {
  return /календарн\w*\s+день|\d+-й\s+день\s+года|день\s+года\s+\d+|calendar-doy/i.test(
    clean(text),
  );
}

/** Scenario ready for C2 chapters: conflict + ≥1 scene, not unavailable. */
export function isDayScenarioReadyForChapters(contract: TodayContractV1): boolean {
  const story = contract.day_story;
  if (!story) return false;
  if (String(story.interpretation_status || "").trim() === "unavailable") return false;
  const scenario = story.day_scenario;
  if (!scenario || typeof scenario !== "object") return false;
  if (scenario.ready === false) return false;
  const conflict = scenario.conflict;
  const scenes = Array.isArray(scenario.scenes) ? scenario.scenes : [];
  const hasConflict = Boolean(clean(conflict?.short_name) || clean(conflict?.why_arose));
  return hasConflict && scenes.length > 0;
}

/**
 * Reading Screen 3 (v3.1) — sphere cards only (why → opportunity → trap).
 * Conflict → Plot; symbols/astro → Symbols; color + day action → Move.
 * Cap: at most 2 chapters (canon). Prefer scenes with opportunity or trap signal.
 */
export type ScenarioSymbolImpact = {
  title?: string | null;
  headline?: string | null;
  body?: string | null;
};

const READING_CHAPTER_CAP = 2;

function sceneSignalScore(sc: {
  opportunity?: string | null;
  trap?: string | null;
  what_happens?: string | null;
  role_in_story?: string | null;
}): number {
  let score = 0;
  if (clean(sc.trap)) score += 3;
  if (clean(sc.opportunity)) score += 2;
  if (clean(sc.what_happens)) score += 1;
  const role = clean(sc.role_in_story).toLowerCase();
  if (role === "primary") score += 2;
  else if (role === "caution" || role === "peak") score += 1;
  return score;
}

export function buildScenarioStoryChapters(input: {
  contract: TodayContractV1;
  colorGuide?: TodayDayColorGuide | null;
  /** @deprecated v3 — symbols live on Symbols screen; kept for call-site compat */
  tarotImpact?: ScenarioSymbolImpact | null;
  numberImpact?: ScenarioSymbolImpact | null;
}): TodayDayNarrativeChapter[] | null {
  if (!isDayScenarioReadyForChapters(input.contract)) return null;

  const dayStory = input.contract.day_story!;
  const scenario = dayStory.day_scenario!;
  const scenes = (scenario.scenes ?? []).filter((s) => s && typeof s === "object");
  const chapters: TodayDayNarrativeChapter[] = [];

  const looksLikeForcePaste = (text: string | null | undefined): boolean => {
    const t = clean(text);
    if (!t) return false;
    return (
      /^Шанс выбрать «.+» именно здесь/i.test(t) ||
      /тот же выбор — «/i.test(t) ||
      /день упирается в выбор: «/i.test(t) ||
      /^Ловушка — скатиться в «/i.test(t)
    );
  };

  const ranked = [...scenes].sort((a, b) => sceneSignalScore(b) - sceneSignalScore(a));

  for (const sc of ranked) {
    if (chapters.length >= READING_CHAPTER_CAP) break;

    const sphereKey = clean(sc.sphere) || "sphere";
    const label = clean(sc.sphere_label_ru) || clean(sc.sphere) || "Сфера дня";
    const what = clean(sc.what_happens);
    const domestic = clean(sc.domestic_example);
    const opportunity = clean(sc.opportunity);
    const trap = clean(sc.trap);
    // v3.1: recommended_action / do_not belong on Move — never paste into Reading.

    const leadLine = looksLikeForcePaste(what) ? domestic : [what, domestic].filter(Boolean).join(" ");
    const paras: string[] = [];
    if (leadLine && !looksLikeForcePaste(leadLine)) {
      paras.push(leadLine);
    } else if (domestic) {
      paras.push(domestic);
    }

    const strengthen: string[] = [];
    const soften: string[] = [];
    if (opportunity && !looksLikeForcePaste(opportunity)) strengthen.push(opportunity);
    if (trap && !looksLikeForcePaste(trap)) soften.push(trap);

    if (!paras.length && !strengthen.length && !soften.length) continue;

    chapters.push({
      id: `sphere-${sphereKey}`,
      kicker: label,
      lead: paras[0] ?? null,
      paragraphs: paras.slice(1),
      accent: strengthen.length || soften.length ? "dual" : "default",
      dual:
        strengthen.length || soften.length
          ? { strengthen: strengthen.slice(0, 2), soften: soften.slice(0, 2) }
          : null,
    });
  }

  return chapters.length ? chapters : null;
}
