/**
 * Glance Screen 0 — day texture from conflict (not short_name label).
 * Canon: docs/today/TODAY_SCREEN_SCENARIO_V3.md
 *
 * Glance = short feel (≤1 sentence). Full why_arose belongs on Plot.
 * Aspect-bank jargon («Связь Солнца и Марса описывает…») is not Glance texture —
 * prefer opposing_forces tension instead.
 */

import type { TodayContractV1 } from "@/lib/todayContract";
import { isCalendarKitchenFact, sanitizeConflictLabel } from "@/lib/todayScenarioChapters";

function clean(text: string | null | undefined): string {
  return (text ?? "").replace(/\s+/g, " ").trim();
}

function conflictFrom(contract: TodayContractV1) {
  return contract.day_story?.day_scenario?.conflict ?? null;
}

/** Sticky B5/natal dictionary lines — not a 2-second day feel. */
export function looksLikeAspectBankWhy(text: string | null | undefined): boolean {
  const t = clean(text);
  if (!t) return false;
  return (
    /связь\s+.+\s+и\s+.+\s+описывает/i.test(t) ||
    /связка\s+.+[–—-].+\s+показывает/i.test(t) ||
    /мотор напора/i.test(t)
  );
}

function firstSentence(text: string): string {
  const m = text.match(/^(.+?[.!?…])(?:\s|$)/u);
  return (m?.[1] || text).trim();
}

function tensionLine(a: string, b: string): string {
  return `Сегодня натяжение: «${a}» или «${b}».`;
}

/**
 * Short Glance hero (one sentence).
 * Prefer lived opposing_forces when why_arose is aspect-bank / calendar junk.
 */
export function buildGlanceDayTexture(contract: TodayContractV1 | null | undefined): string | null {
  if (!contract) return null;
  const conflict = conflictFrom(contract);
  if (!conflict) return null;

  const forceA = clean(conflict.opposing_forces?.a);
  const forceB = clean(conflict.opposing_forces?.b);
  const why = clean(conflict.why_arose);

  if (forceA && forceB && (!why || isCalendarKitchenFact(why) || looksLikeAspectBankWhy(why))) {
    return tensionLine(forceA, forceB);
  }

  if (why && !isCalendarKitchenFact(why)) {
    const short = firstSentence(why);
    if (short.length > 140) return `${short.slice(0, 137).replace(/\s+\S*$/, "")}…`;
    return short;
  }

  if (forceA && forceB) return tensionLine(forceA, forceB);
  return null;
}

/** Compact label for Glance eyebrow — short_name only, never the texture body. */
export function buildGlanceThemeEyebrow(contract: TodayContractV1 | null | undefined): string | null {
  if (!contract) return null;
  const conflict = conflictFrom(contract);
  const raw =
    sanitizeConflictLabel(conflict?.short_name) || sanitizeConflictLabel(contract.day_story?.theme);
  return raw || null;
}
