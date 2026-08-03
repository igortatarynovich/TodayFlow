/**
 * Glance Screen 0 — tone synthesis (not Plot facts, not A/B conflict seed).
 * Canon: docs/today/TODAY_SCREEN_SCENARIO_V3.md v3.1
 *
 * Internal classification (thesis.mode) sets tone. Facts live only on Plot.
 * Never invent «A или B» from opposing_forces for Glance hero.
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

function thesisMode(conflict: NonNullable<ReturnType<typeof conflictFrom>>): string {
  const thesis = (conflict as { thesis?: { mode?: string | null } | null }).thesis;
  return clean(thesis?.mode).toLowerCase();
}

/** Tone lines from internal classification — not UI labels, not force pairs. */
function toneFromMode(mode: string): string | null {
  if (mode === "stability") return "День держит ровный темп — без резкого перелома.";
  if (mode === "opportunity") return "Сегодня есть окно для одного ясного шага.";
  if (mode === "recovery") return "День просит отпустить лишнее и набрать ресурс.";
  if (mode === "conflict" || mode === "pressure" || mode === "change") {
    return "Сегодня тон острее обычного — важна мера в каждом жесте.";
  }
  if (mode === "momentum" || mode === "communication" || mode === "decision" || mode === "connection") {
    // family sometimes leaks into mode field on older payloads
    return null;
  }
  return null;
}

/**
 * Short Glance hero (1–2 sentences of tone).
 * Prefer thesis.mode tone; lived why only when it is already feel-language (not aspect bank / facts dump).
 */
export function buildGlanceDayTexture(contract: TodayContractV1 | null | undefined): string | null {
  if (!contract) return null;
  const conflict = conflictFrom(contract);
  if (!conflict) return null;

  const mode = thesisMode(conflict);
  const fromMode = toneFromMode(mode);
  if (fromMode) return fromMode;

  const why = clean(conflict.why_arose);
  if (why && !isCalendarKitchenFact(why) && !looksLikeAspectBankWhy(why) && why.length <= 120) {
    const short = firstSentence(why);
    // Reject fact-stack joins (« · ») — those belong on Plot spine
    if (!short.includes(" · ")) return short;
  }

  // Family on thesis as soft fallback tone (not A/B)
  const family = clean(
    (conflict as { thesis?: { family?: string | null } | null }).thesis?.family,
  ).toLowerCase();
  if (family === "stability" || mode === "stability") {
    return "День держит ровный темп — без резкого перелома.";
  }

  return null;
}

/** Compact label for Glance eyebrow — short_name only when not forced A|B drama. */
export function buildGlanceThemeEyebrow(contract: TodayContractV1 | null | undefined): string | null {
  if (!contract) return null;
  const conflict = conflictFrom(contract);
  const raw =
    sanitizeConflictLabel(conflict?.short_name) || sanitizeConflictLabel(contract.day_story?.theme);
  if (!raw) return null;
  // Hide binary dramaturgy labels from eyebrow when they are the old seed form
  if (/\sили\s/i.test(raw) && raw.length < 64) {
    const mode = conflict ? thesisMode(conflict) : "";
    if (mode === "stability" || mode === "recovery" || mode === "opportunity") return null;
  }
  return raw;
}

/** Shared honest copy — Glance chips + Reading empty (v3.1). */
export const TODAY_NO_SHARP_FOCUS_COPY = "Сегодня без острого фокуса по сферам.";
