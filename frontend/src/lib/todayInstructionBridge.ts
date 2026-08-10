/**
 * Block 3 — personal bridge (trend × person).
 * LIVE contract fields only. No invent.
 * Canon: TODAY_SCREEN_SCENARIO_V3 § useful Today · block 3.
 */

import type { TodayContractV1 } from "@/lib/todayContract";
import { cleanAmbassadorWhy, clipCompassProse } from "@/lib/todayDayBrief";

export type TodayInstructionBridgeModel = {
  /** Soft personal lead (2–3 sentences max after clip). */
  lead: string | null;
};

function firstNatalTransitSoft(
  contract: TodayContractV1,
): string | null {
  const beats = contract.day_story?.day_personal?.personal_astrology?.beats;
  if (!Array.isArray(beats)) return null;
  for (const beat of beats) {
    if (String(beat?.kind || "") !== "natal_transit") continue;
    const line = cleanAmbassadorWhy(beat?.story_ru || beat?.title);
    if (line) return line;
  }
  return null;
}

/**
 * Pick a person-facing bridge line from live slots.
 * Prefer why_personal → soft natal transit → soft astrology summary → development_point.
 */
export function pickInstructionPersonalBridge(
  contract: TodayContractV1 | null | undefined,
): string | null {
  if (!contract?.day_story) return null;
  const story = contract.day_story;
  const conflict = story.day_scenario?.conflict;

  const candidates: Array<string | null | undefined> = [
    conflict?.why_personal,
    firstNatalTransitSoft(contract),
    story.day_personal?.personal_astrology?.summary_ru,
    story.day_personal?.summary_ru,
    contract.personal_growth?.development_point,
  ];

  for (const raw of candidates) {
    const ok = cleanAmbassadorWhy(raw);
    if (!ok) continue;
    return clipCompassProse(ok, 220);
  }
  return null;
}

export function buildTodayInstructionBridgeModel(
  contract: TodayContractV1 | null | undefined,
): TodayInstructionBridgeModel {
  return { lead: pickInstructionPersonalBridge(contract) };
}
