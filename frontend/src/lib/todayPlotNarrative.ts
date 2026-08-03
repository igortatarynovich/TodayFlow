/**
 * Plot Screen 1 — conflict narrative (not Glance short_name duplicate).
 * Canon: docs/today/TODAY_SCREEN_SCENARIO_V3.md
 */

import type { TodayContractV1 } from "@/lib/todayContract";
import { isCalendarKitchenFact, sanitizeConflictLabel } from "@/lib/todayScenarioChapters";

function clean(text: string | null | undefined): string {
  return (text ?? "").replace(/\s+/g, " ").trim();
}

function isKitchenNatalLead(text: string): boolean {
  return /Firdaria|ZR\s*Fortune|ZR\s*Spirit|Лоты\s*soft|Vimshottari|BaZi|HD\s*soft|Variables\s*soft|Solar\s*return|time[_\s-]?lords|управител|нет\s+ASC/i.test(
    text,
  );
}

export type PlotConflictNarrative = {
  /** Optional tension line from opposing_forces */
  tension: string | null;
  /** why_arose — main story */
  why: string | null;
  /** why_personal when profile_depth=deep only */
  personal: string | null;
};

export function buildPlotConflictNarrative(contract: TodayContractV1 | null | undefined): PlotConflictNarrative | null {
  if (!contract) return null;
  const conflict = contract.day_story?.day_scenario?.conflict;
  if (!conflict) return null;

  const depth = String(
    (conflict as { profile_depth?: string | null }).profile_depth || "",
  )
    .trim()
    .toLowerCase();
  const forceA = clean(conflict.opposing_forces?.a);
  const forceB = clean(conflict.opposing_forces?.b);
  const tension = forceA && forceB ? `Натяжение между «${forceA}» и «${forceB}».` : null;

  const whyRaw = clean(conflict.why_arose);
  const whyDeduped = whyRaw
    ? whyRaw
        .split(/(?<=[.!?])\s+/)
        .map((s) => s.trim())
        .filter(Boolean)
        .filter((s, i, arr) => {
          const key = s.toLowerCase().replace(/[.!?]+$/u, "");
          return arr.findIndex((x) => x.toLowerCase().replace(/[.!?]+$/u, "") === key) === i;
        })
        .join(" ")
    : "";
  const why = whyDeduped && !isCalendarKitchenFact(whyDeduped) ? whyDeduped : null;

  const personalRaw = clean(conflict.why_personal);
  const personal =
    depth === "deep" && personalRaw && !isKitchenNatalLead(personalRaw) ? personalRaw : null;

  if (!tension && !why && !personal) return null;
  return { tension, why, personal };
}

/** True when plot body would only restate the Glance short_name — omit duplicate title. */
export function plotWouldDuplicateGlanceLabel(
  narrative: PlotConflictNarrative | null,
  glanceLabel: string | null | undefined,
): boolean {
  if (!narrative || !glanceLabel) return false;
  const label = sanitizeConflictLabel(glanceLabel).toLowerCase();
  if (!label) return false;
  const blob = [narrative.why, narrative.tension, narrative.personal]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
  if (!blob) return true;
  return blob === label || (blob.length < label.length + 8 && blob.includes(label));
}
