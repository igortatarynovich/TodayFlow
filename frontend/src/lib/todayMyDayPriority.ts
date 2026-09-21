/**
 * T3.priority / T3.caution — Personal Narrative after bind.
 * Not Global recommended_action / do_not / chips / expect.
 * Empty → omit. Canon: TODAY_INFORMATION_CONTRACT_V1 K09 · K10
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

function sceneFieldLines(contract: TodayContractV1, keys: readonly string[]): string[] {
  const out: string[] = [];
  const scenes = contract.day_story?.day_scenario?.scenes;
  if (!Array.isArray(scenes)) return out;
  for (const sc of scenes) {
    if (!sc || typeof sc !== "object") continue;
    const row = sc as Record<string, unknown>;
    for (const key of keys) {
      const text = String(row[key] ?? "").trim();
      if (text) out.push(text);
    }
  }
  return out;
}

function globalSceneActionLines(contract: TodayContractV1): string[] {
  const out = sceneFieldLines(contract, ["recommended_action"]);
  const goals = contract.day_story?.day_scenario?.props?.goals;
  if (Array.isArray(goals)) {
    for (const g of goals) {
      const text = String(g?.text ?? "").trim();
      if (text) out.push(text);
    }
  }
  return out;
}

function globalSceneCautionLines(contract: TodayContractV1): string[] {
  return sceneFieldLines(contract, ["do_not", "avoid_action"]);
}

function isGlobalSceneAction(line: string, contract: TodayContractV1): boolean {
  const n = norm(line);
  if (!n) return false;
  return globalSceneActionLines(contract).some((item) => norm(item) === n);
}

function isGlobalSceneCaution(line: string, contract: TodayContractV1): boolean {
  const n = norm(line);
  if (!n) return false;
  return globalSceneCautionLines(contract).some((item) => norm(item) === n);
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

/** T3.caution list: Personal avoid after bind. Not Global do_not and not inverted do[]. */
export function pickMyDayCautionLines(input: {
  contract: TodayContractV1;
  avoidItems: string[];
  priorityLines?: string[];
}): string[] {
  if (isTodayInterpretationUnavailable(input.contract)) return [];
  if (!contractHasPersistedPersonalDay(input.contract)) return [];
  const priority = new Set((input.priorityLines ?? []).map((line) => norm(line)).filter(Boolean));
  return input.avoidItems
    .map((item) => item.trim())
    .filter(Boolean)
    .filter((line) => !isGlobalChipLine(line, input.contract))
    .filter((line) => !isGlobalSceneCaution(line, input.contract))
    .filter((line) => !isGlobalSceneAction(line, input.contract))
    .filter((line) => !priority.has(norm(line)))
    .slice(0, 2)
    .map((line) => clipCompassProse(line, 180) || line);
}
