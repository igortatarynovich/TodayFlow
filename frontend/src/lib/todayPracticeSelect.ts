/**
 * Deterministic MY DAY practice from Content Library selection.
 * Canon: docs/practices/CONTENT_LIBRARY_SELECTION_V1.md · TODAY_DISPLAY_INVENTORY T3.practice
 * Meaning does not emit item_id. FE maps Personal F10 focus_axis (closed 4-set) → need,
 * then GET /practices/select. Global primary_energy is not K16 input.
 * Honest miss → omit. Never invent from /practices?limit=1.
 */

import { getJson } from "@/lib/api";
import type { PracticeResponse } from "@/components/today/todayPageUtils";
import type { TodayContractDomainId } from "@/lib/todayContract";

/** Closed F10 4-set → existing selector purpose/direction/context. Not a second ranker. */
export const PERSONAL_FOCUS_NEED: Record<
  TodayContractDomainId,
  { purpose: string; direction: string; context: string }
> = {
  work: { purpose: "decision_making", direction: "focus", context: "work" },
  money: { purpose: "clarity", direction: "reflect", context: "money" },
  relationships: { purpose: "connection", direction: "connect", context: "relationships" },
  energy: { purpose: "grounding", direction: "stabilize", context: "body" },
};

export type ContentLibrarySelectResponse = {
  item_id: string | null;
  title: string;
  body: string;
  outcome_label: string;
  duration: number | null;
  matched: boolean;
  reason: string;
};

export function needQueryFromFocusAxis(axis: string | null | undefined): {
  purpose: string;
  direction: string;
  context: string;
} | null {
  const key = String(axis || "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "_");
  if (key !== "work" && key !== "money" && key !== "relationships" && key !== "energy") {
    return null;
  }
  return PERSONAL_FOCUS_NEED[key];
}

export function catalogPracticeFromSelection(
  selection: ContentLibrarySelectResponse | null | undefined,
): PracticeResponse | null {
  if (!selection?.matched || !selection.item_id || !selection.title.trim()) return null;
  return {
    id: selection.item_id,
    title: selection.title.trim(),
    description: (selection.body || selection.outcome_label || "").trim(),
    duration_minutes: selection.duration ?? undefined,
  };
}

export async function fetchCatalogPracticeForFocusAxis(
  axis: string | null | undefined,
): Promise<PracticeResponse | null> {
  const need = needQueryFromFocusAxis(axis);
  if (!need) return null;
  const params = new URLSearchParams({
    purpose: need.purpose,
    direction: need.direction,
    context: need.context,
    content_class: "practice",
    locale: "ru",
  });
  const selection = await getJson<ContentLibrarySelectResponse>(`/practices/select?${params.toString()}`);
  return catalogPracticeFromSelection(selection);
}
