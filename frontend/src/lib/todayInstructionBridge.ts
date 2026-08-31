/**
 * T3.focus_body — personal overlay how-it-shows.
 * LIVE contract fields only. No invent.
 * Canon: TODAY_DISPLAY_INVENTORY_V1 T3.focus_body.
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
    const title = cleanAmbassadorWhy(beat?.title);
    const story = cleanAmbassadorWhy(beat?.story_ru);
    if (title && story) return title;
    if (title) return title;
    if (story) return story;
  }
  return null;
}

function normalizeOverlapKey(s: string): string {
  return s.replace(/\s+/g, " ").trim().toLowerCase();
}

/** Inventory: drop focus_body if it overlaps T3.headline (substring ≥24). */
export function omitIfOverlapsHeadline(
  body: string | null | undefined,
  headline: string | null | undefined,
): string | null {
  const lead = String(body ?? "").trim() || null;
  const head = String(headline ?? "").trim() || null;
  if (!lead) return null;
  if (!head) return lead;
  const aa = normalizeOverlapKey(lead);
  const bb = normalizeOverlapKey(head);
  if (aa === bb) return null;
  if (aa.length >= 24 && bb.includes(aa.slice(0, Math.min(48, aa.length)))) return null;
  if (bb.length >= 24 && aa.includes(bb.slice(0, Math.min(48, bb.length)))) return null;
  return lead;
}

/**
 * Pick T3.focus_body from live overlay slots only.
 * why_personal → natal transit story → personal_astrology.summary_ru.
 * Not day_personal.summary_ru (headline) and not development_point (CE).
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
