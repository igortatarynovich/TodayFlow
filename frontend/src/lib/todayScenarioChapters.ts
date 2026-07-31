/**
 * Reading Screen 3 (v3) — sphere cards from day_scenario.scenes.
 * Conflict → Plot; symbols/astro → Symbols; color → Move.
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
 * Reading Screen 3 (v3) — sphere cards only.
 * Conflict narrative → Plot; symbols/astro → Symbols; color → Move.
 * Canon: docs/today/TODAY_SCREEN_SCENARIO_V3.md
 */
export type ScenarioSymbolImpact = {
  title?: string | null;
  headline?: string | null;
  body?: string | null;
};

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

  for (const sc of scenes) {
    const sphereKey = clean(sc.sphere) || "sphere";
    const label = clean(sc.sphere_label_ru) || clean(sc.sphere) || "Сфера дня";
    const what = clean(sc.what_happens);
    const domestic = clean(sc.domestic_example);
    const opportunity = clean(sc.opportunity);
    const trap = clean(sc.trap);
    const action = clean(sc.recommended_action);
    const avoid = clean(sc.do_not);

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
    if (action) {
      paras.push(action.endsWith(".") || action.endsWith("!") ? action : `${action}.`);
    }
    if (avoid) {
      const avoidLine =
        avoid.startsWith("Не ") || avoid.startsWith("не ")
          ? avoid
          : `Не ${avoid.replace(/[.!?]+$/, "")}`;
      paras.push(avoidLine.endsWith(".") ? avoidLine : `${avoidLine}.`);
    }

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
