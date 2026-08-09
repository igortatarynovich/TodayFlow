/**
 * Welcome activity tags — explicit SoT compose (TODAY_MAKE_YOURS_AND_WELCOME_SOT §2).
 * Prefer short day_story.do nouns; fall back to morning priorities ≤18 chars.
 */

import type { TodayContractV1 } from "@/lib/todayContract";

function clean(text: string | null | undefined): string {
  return (text ?? "").replace(/\s+/g, " ").trim();
}

function pushUnique(out: string[], raw: string, maxLen: number) {
  const t = clean(raw);
  if (!t || t.length > maxLen) return;
  if (out.some((x) => x.toLowerCase() === t.toLowerCase())) return;
  out.push(t);
}

export function resolveWelcomeActivityTags(input: {
  contract?: TodayContractV1 | null;
  morningPriorities?: unknown;
  max?: number;
}): string[] {
  const max = input.max ?? 3;
  const out: string[] = [];
  const doItems = input.contract?.day_story?.do;
  if (Array.isArray(doItems)) {
    for (const row of doItems) {
      if (out.length >= max) break;
      if (typeof row === "string") pushUnique(out, row, 18);
    }
  }
  if (out.length < max && Array.isArray(input.morningPriorities)) {
    for (const row of input.morningPriorities) {
      if (out.length >= max) break;
      if (typeof row === "string") pushUnique(out, row, 18);
    }
  }
  return out;
}
