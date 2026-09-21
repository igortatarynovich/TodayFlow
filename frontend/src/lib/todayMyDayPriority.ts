/**
 * T3.priority — Personal Narrative do after bind.
 * Not Global recommended_action / goals / strength chips / expect.
 * Glance leftover only if that line is personal today_move. Empty → omit.
 * Canon: TODAY_INFORMATION_CONTRACT_V1 K09 · TODAY_DISPLAY_INVENTORY_V1 T3.priority
 */

import type { TodayContractV1 } from "@/lib/todayContract";
import {
  contractHasPersistedPersonalDay,
  isTodayInterpretationUnavailable,
} from "@/lib/todayContract";
import { clipCompassProse, GLOBAL_ACTION_TYPE_LABELS_RU } from "@/lib/todayDayBrief";

function norm(s: string): string {
  return s.replace(/\s+/g, " ").replace(/[.!?]+$/u, "").trim().toLowerCase();
}

function isGlobalChipLine(line: string, contract: TodayContractV1): boolean {
  const n = norm(line);
  if (!n) return false;
  const closed = Object.values(GLOBAL_ACTION_TYPE_LABELS_RU);
  if (closed.some((label) => norm(label) === n)) return true;
  const raw = [
    ...(Array.isArray(contract.global_day?.strength) ? contract.global_day.strength : []),
    ...(Array.isArray(contract.global_day?.risk) ? contract.global_day.risk : []),
  ];
  return raw.some((id) => {
    const key = String(id || "")
      .trim()
      .toLowerCase()
      .replace(/-/g, "_");
    return Boolean(key) && (n === key || n === norm(GLOBAL_ACTION_TYPE_LABELS_RU[key] ?? ""));
  });
}

function isGlobalExpectOrPeriod(line: string, contract: TodayContractV1): boolean {
  const n = norm(line);
  if (!n) return false;
  const expect = String(contract.day_story?.expect ?? "").trim();
  if (expect && norm(expect) === n) return true;
  const period = String(contract.global_context?.period ?? "").trim();
  return Boolean(period) && norm(period) === n;
}

function globalSceneActionLines(contract: TodayContractV1): string[] {
  const out: string[] = [];
  const scenes = contract.day_story?.day_scenario?.scenes;
  if (Array.isArray(scenes)) {
    for (const sc of scenes) {
      const rec = String(sc?.recommended_action ?? "").trim();
      if (rec) out.push(rec);
    }
  }
  const goals = contract.day_story?.day_scenario?.props?.goals;
  if (Array.isArray(goals)) {
    for (const g of goals) {
      const text = String(g?.text ?? "").trim();
      if (text) out.push(text);
    }
  }
  return out;
}

function isGlobalSceneAction(line: string, contract: TodayContractV1): boolean {
  const n = norm(line);
  if (!n) return false;
  return globalSceneActionLines(contract).some((item) => norm(item) === n);
}

/** Glance Daily Focus line may feed T3.priority only when it is the personal move. */
export function isPersonalGlancePriorityFallback(
  line: string | null | undefined,
  contract: TodayContractV1,
): boolean {
  const text = String(line ?? "").trim();
  if (!text) return false;
  if (isGlobalChipLine(text, contract)) return false;
  if (isGlobalExpectOrPeriod(text, contract)) return false;
  if (isGlobalSceneAction(text, contract)) return false;
  const move = String(contract.day_story?.today_move ?? "").trim();
  if (!move || isGlobalSceneAction(move, contract)) return false;
  return norm(move) === norm(text);
}

/** T3.priority list: Personal do[] after bind; glance leftover only if personal. */
export function pickMyDayPriorityLines(input: {
  contract: TodayContractV1;
  doItems: string[];
  glancePrioritize?: string | null;
}): string[] {
  if (isTodayInterpretationUnavailable(input.contract)) return [];
  if (!contractHasPersistedPersonalDay(input.contract)) return [];
  const dos = input.doItems
    .map((item) => item.trim())
    .filter(Boolean)
    .filter((line) => !isGlobalChipLine(line, input.contract))
    .filter((line) => !isGlobalExpectOrPeriod(line, input.contract))
    .filter((line) => !isGlobalSceneAction(line, input.contract))
    .slice(0, 3);
  if (dos.length) return dos;
  const glance = String(input.glancePrioritize ?? "").trim();
  if (!glance) return [];
  if (!isPersonalGlancePriorityFallback(glance, input.contract)) return [];
  return [clipCompassProse(glance, 200) || glance];
}
