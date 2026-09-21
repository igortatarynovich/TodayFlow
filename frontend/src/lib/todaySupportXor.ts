/**
 * TIC-K17: XOR affirmation vs practice on the locked Today surface.
 * Existing content mode is the K16 F10 need-cell class (practice), not a second
 * selector, date-hash, catalog availability, or scene rec kind.
 * Canon: TODAY_INFORMATION_CONTRACT_V1 K17 · TODAY_DISPLAY_INVENTORY T3.affirmation
 */

import type { TodayContractV1 } from "@/lib/todayContract";
import {
  contractHasPersistedPersonalDay,
  isTodayInterpretationUnavailable,
} from "@/lib/todayContract";
import { pickPersonalFocusAxisId } from "@/lib/todayPersonalFocusAxis";
import { contentClassFromFocusAxis } from "@/lib/todayPracticeSelect";

export type TodaySupportSlot = "practice" | "affirmation";

function sceneAffirmationLines(contract: TodayContractV1): string[] {
  const out: string[] = [];
  const scenes = contract.day_story?.day_scenario?.scenes;
  if (Array.isArray(scenes)) {
    for (const sc of scenes) {
      if (!sc || typeof sc !== "object") continue;
      const row = sc as Record<string, unknown>;
      for (const key of ["recommended_action", "trap"] as const) {
        const text = String(row[key] ?? "").trim();
        if (text) out.push(text);
      }
    }
  }
  const affirms = contract.day_story?.day_scenario?.props?.affirmations;
  if (Array.isArray(affirms)) {
    for (const row of affirms) {
      const text = String(row?.text ?? "").trim();
      if (text) out.push(text);
    }
  }
  return out;
}

function norm(s: string): string {
  return s.replace(/\s+/g, " ").replace(/[.!?]+$/u, "").trim().toLowerCase();
}

/**
 * Personal verbal support for T3.affirmation.
 * Scene affirmations / trap / recommended_action are not this field.
 * Locked overlay has no Personal-owned affirmation writer → omit.
 */
export function pickLockedAffirmationLine(
  contract: TodayContractV1 | null | undefined,
): string | null {
  if (!contract) return null;
  if (isTodayInterpretationUnavailable(contract)) return null;
  if (!contractHasPersistedPersonalDay(contract)) return null;
  const rec = contract.day_story?.practice_recommendation;
  const kind = String(rec?.kind || "").trim().toLowerCase();
  const text = String(rec?.text || "").trim();
  if (kind !== "affirmation" || !text) return null;
  const n = norm(text);
  if (sceneAffirmationLines(contract).some((line) => norm(line) === n)) return null;
  // No Personal-owned affirmation field on the locked overlay schema.
  return null;
}

/**
 * Existing content mode of the F10 need cell. K16 already retrieves that cell
 * as content_class=practice. Not a ranker of practice vs affirmation items.
 */
export function pickLockedSupportMode(
  contract: TodayContractV1 | null | undefined,
): TodaySupportSlot | null {
  if (!contract) return null;
  if (isTodayInterpretationUnavailable(contract)) return null;
  if (!contractHasPersistedPersonalDay(contract)) return null;
  const axis = pickPersonalFocusAxisId(contract);
  const mode = contentClassFromFocusAxis(axis);
  if (mode === "practice" || mode === "affirmation") return mode;
  return null;
}

/**
 * Exactly one Inventory slot, or omit. Empty selected branch does not switch
 * to the other type for fill. Catalog presence does not choose the mode.
 */
export function pickLockedSupportSlot(input: {
  contract: TodayContractV1 | null | undefined;
  practiceReady: boolean;
}): TodaySupportSlot | null {
  const mode = pickLockedSupportMode(input.contract);
  if (mode === "practice") return input.practiceReady ? "practice" : null;
  if (mode === "affirmation") {
    return pickLockedAffirmationLine(input.contract) ? "affirmation" : null;
  }
  return null;
}
