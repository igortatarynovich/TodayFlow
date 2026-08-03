/**
 * Plot Screen 1 — conflict narrative (not Glance short_name duplicate).
 * Canon: docs/today/TODAY_SCREEN_SCENARIO_V3.md
 *
 * opposing_forces is an optional data outcome — never invent a default
 * «Натяжение между A и B» opener when both poles exist. why_arose leads.
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
  /**
   * @deprecated Always null — FE must not invent binary tension openers.
   * Kept for call-site compat / tests that still read the field.
   */
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
  // v3.1: do not render opposing_forces as default «X против Y» dramaturgy.
  const tension = null;

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
  // Drop invented binary openers already baked into why_arose by older models.
  const whySansBinaryOpener = whyDeduped
    ? whyDeduped
        .replace(
          /^Натяжение\s+между\s+«[^»]+»\s+и\s+«[^»]+»\.?\s*/iu,
          "",
        )
        .replace(
          /^Напряжение\s+между\s+«[^»]+»\s+и\s+«[^»]+»\.?\s*/iu,
          "",
        )
        .trim()
    : "";
  const why =
    whySansBinaryOpener && !isCalendarKitchenFact(whySansBinaryOpener)
      ? whySansBinaryOpener
      : null;

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
