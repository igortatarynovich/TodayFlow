/**
 * Finding 1 live ratchet: meaning-bearing FE literals must be Inventory chrome
 * or they fail the audit. Copy-file presence is not authority.
 */

import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { chromeSlotForLiteral, NON_UI_FILTER_LITERALS } from "@/lib/displayGrammar/chromeRegistry";
import type { DisplayGrammarFinding } from "@/lib/displayGrammar/types";

const QUOTED = /(?<!`)["']([^"'\n]{8,})["']/g;
const CYR = /[А-Яа-яЁё]/;

export function extractCyrillicLiterals(source: string): string[] {
  const out: string[] = [];
  QUOTED.lastIndex = 0;
  let match: RegExpExecArray | null;
  while ((match = QUOTED.exec(source))) {
    const text = match[1].trim();
    if (!CYR.test(text)) continue;
    if (NON_UI_FILTER_LITERALS.has(text)) continue;
    out.push(text);
  }
  return out;
}

export function scanInventedFeCopy(source: string, fileLabel?: string): DisplayGrammarFinding[] {
  const findings: DisplayGrammarFinding[] = [];
  for (const text of extractCyrillicLiterals(source)) {
    if (chromeSlotForLiteral(text)) continue;
    findings.push({
      grammar: 1,
      code: "invented_fe_copy",
      detail: fileLabel ? `${fileLabel}: ${text}` : text,
    });
  }
  return findings;
}

/** Locked Profile/Today path components — not Glance / legacy experience. */
export const GRAMMAR_PATH_SCAN_REL = [
  "src/components/today/composition/TodayMyDayPane.tsx",
  "src/components/today/composition/TodayDayBrief.tsx",
  "src/components/today/composition/TodayRitualLensPair.tsx",
  "src/components/today/composition/TodayEveningGratitudeBlock.tsx",
  "src/components/today/composition/TodayProductScreenFlow.tsx",
  "src/components/today/composition/TodayMyDayRhythm.tsx",
  "src/components/today/composition/TodayDayTasksBlock.tsx",
  "src/components/profile/v2/scenes/ProfileRecognitionScene.tsx",
  "src/components/profile/v2/scenes/ProfileWhyScene.tsx",
  "src/components/profile/v2/scenes/ProfileInsightScene.tsx",
  "src/components/profile/v2/scenes/ProfileEffortScene.tsx",
  "src/components/profile/v2/scenes/ProfileBridgeScene.tsx",
] as const;

export function scanPathComponentCopy(frontendRoot: string): DisplayGrammarFinding[] {
  const findings: DisplayGrammarFinding[] = [];
  for (const rel of GRAMMAR_PATH_SCAN_REL) {
    const abs = join(frontendRoot, rel);
    const source = readFileSync(abs, "utf8");
    findings.push(...scanInventedFeCopy(source, rel));
  }
  return findings;
}

export function listTsxFiles(dir: string): string[] {
  const out: string[] = [];
  for (const name of readdirSync(dir)) {
    const abs = join(dir, name);
    const st = statSync(abs);
    if (st.isDirectory()) {
      if (name === "__tests__" || name === "node_modules") continue;
      out.push(...listTsxFiles(abs));
    } else if (name.endsWith(".tsx") && !name.includes(".test.")) {
      out.push(abs);
    }
  }
  return out;
}
