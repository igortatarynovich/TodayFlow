/**
 * Grammar §9 subset — findings 7, 12, 15, 17, 18 (regression).
 * Full scanner: frontend/src/lib/displayGrammar/scanDisplayGrammar.ts
 * Canon: docs/foundation/DISPLAY_CONSTRUCTION_GRAMMAR_V1.md §9
 */

import { omitIfOverlapsHeadline } from "@/lib/todayInstructionBridge";
import type { TodayContractV1 } from "@/lib/todayContract";
import {
  todayAllowsRitualLens,
  type TodayCapabilityDepth,
} from "@/lib/todayScreenFlowCapability";

export type TodayDisplayLockFinding = {
  grammar: 7 | 12 | 15 | 17 | 18;
  code:
    | "invented_fallback"
    | "guest_or_general_lens"
    | "lens_without_persist"
    | "action_as_focus_or_second_do"
    | "focus_title_paraphrases_headline";
};

/** Known FE strings that invented Today meaning when a slot was empty. */
const TODAY_INVENTED_FALLBACKS = [
  "сегодня лучше двигаться последовательно, чем быстро.",
  "главный фокус дня",
  "один шаг на сегодня.",
  "сегодня без отдельного задания.",
];

function norm(s: string): string {
  return s.replace(/\s+/g, " ").trim().toLowerCase();
}

/** Finding 7 — canned or CE fill when the slot should omit. */
export function auditTodayInventedFallback(input: {
  texts?: Array<string | null | undefined>;
  developmentPoint?: string | null;
}): TodayDisplayLockFinding[] {
  const ce = String(input.developmentPoint ?? "").trim();
  const ceNorm = ce ? norm(ce) : "";
  for (const raw of input.texts ?? []) {
    const text = String(raw ?? "").trim();
    if (!text) continue;
    const n = norm(text);
    if (TODAY_INVENTED_FALLBACKS.includes(n)) {
      return [{ grammar: 7, code: "invented_fallback" }];
    }
    if (ceNorm && n === ceNorm) {
      return [{ grammar: 7, code: "invented_fallback" }];
    }
  }
  return [];
}

export function auditTodayRitualLensLock(input: {
  depth: TodayCapabilityDepth;
  contract: TodayContractV1 | null | undefined;
  lensText: string | null | undefined;
}): TodayDisplayLockFinding[] {
  const lens = String(input.lensText ?? "").trim();
  if (!lens) return [];
  const findings: TodayDisplayLockFinding[] = [];
  if (input.depth === "guest" || input.depth === "general") {
    findings.push({ grammar: 12, code: "guest_or_general_lens" });
  }
  if (!todayAllowsRitualLens(input.depth, input.contract)) {
    findings.push({ grammar: 15, code: "lens_without_persist" });
  }
  return findings;
}

/** Finding 17 — T3.action / second slot on the Priority question. */
export function auditTodayActionSlotLock(input: {
  focusTitle?: string | null;
  primaryAction?: string | null;
  priorities?: string[];
  emptyTasksChrome?: boolean;
}): TodayDisplayLockFinding[] {
  const findings: TodayDisplayLockFinding[] = [];
  const title = String(input.focusTitle ?? "").trim();
  const action = String(input.primaryAction ?? "").trim();
  const priorities = (input.priorities ?? []).map((p) => p.trim()).filter(Boolean);
  if (title && action && norm(title) === norm(action)) {
    findings.push({ grammar: 17, code: "action_as_focus_or_second_do" });
  } else if (title && priorities.some((p) => norm(p) === norm(title))) {
    findings.push({ grammar: 17, code: "action_as_focus_or_second_do" });
  }
  if (input.emptyTasksChrome && priorities.length > 0) {
    findings.push({ grammar: 17, code: "action_as_focus_or_second_do" });
  }
  return findings;
}

/** Finding 18 — T3.focus_title paraphrases T3.headline (not an overlay axis). */
export function auditTodayFocusSplitLock(input: {
  headline?: string | null;
  focusTitle?: string | null;
}): TodayDisplayLockFinding[] {
  const headline = String(input.headline ?? "").trim();
  const title = String(input.focusTitle ?? "").trim();
  if (!headline || !title) return [];
  if (omitIfOverlapsHeadline(title, headline) == null) {
    return [{ grammar: 18, code: "focus_title_paraphrases_headline" }];
  }
  return [];
}
