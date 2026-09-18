/**
 * Deterministic MY DAY practice from Content Library selection.
 * Canon: docs/practices/CONTENT_LIBRARY_SELECTION_V1.md · TODAY_DISPLAY_INVENTORY T3.practice
 * Meaning does not emit item_id. FE maps Global energy (closed 8-set) → need, then GET /practices/select.
 * Honest miss → omit. Never invent from /practices?limit=1.
 */

import { getJson } from "@/lib/api";
import type { PracticeResponse } from "@/components/today/todayPageUtils";

export const GLOBAL_ENERGY_NEED: Record<string, { purpose: string; direction: string }> = {
  grounded: { purpose: "grounding", direction: "stabilize" },
  flow: { purpose: "calm", direction: "downregulate" },
  radiance: { purpose: "energy", direction: "activate" },
  momentum: { purpose: "motivation", direction: "activate" },
  clarity: { purpose: "clarity", direction: "reflect" },
  tension: { purpose: "calm", direction: "downregulate" },
  renewal: { purpose: "recovery", direction: "recover" },
  depth: { purpose: "self_connection", direction: "reflect" },
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

export function needQueryFromPrimaryEnergy(energy: string | null | undefined): {
  purpose: string;
  direction: string;
} | null {
  const key = String(energy || "").trim().toLowerCase();
  if (!key) return null;
  return GLOBAL_ENERGY_NEED[key] ?? null;
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

export async function fetchCatalogPracticeForEnergy(
  energy: string | null | undefined,
): Promise<PracticeResponse | null> {
  const need = needQueryFromPrimaryEnergy(energy);
  if (!need) return null;
  const params = new URLSearchParams({
    purpose: need.purpose,
    direction: need.direction,
    locale: "ru",
  });
  const selection = await getJson<ContentLibrarySelectResponse>(`/practices/select?${params.toString()}`);
  return catalogPracticeFromSelection(selection);
}
