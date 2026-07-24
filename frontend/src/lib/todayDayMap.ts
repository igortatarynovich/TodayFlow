/**
 * Day Map — one causal day picture for Today UI.
 *
 * Prefer guide funnel interpretation fields when present; otherwise map
 * authoritative day_story structured fields into the same slots.
 * This is the screen contract for pulse / glance / move / why — not a second design.
 */

import type { TodayContractV1 } from "@/lib/todayContract";
import { dayStoryAvoidItems, dayStoryDoItems } from "@/lib/todayContractMapper";

export type TodayDayMap = {
  whatHappens: string;
  whereConflict: string | null;
  whereYouBreak: string | null;
  whatWorks: string | null;
  oneConcreteMove: string | null;
  whyLayers: string[];
  avoidHints: string[];
  source: "funnel_interpretation" | "day_story";
};

function clean(text: string | null | undefined): string {
  return (text ?? "").replace(/\s+/g, " ").trim();
}

function ensurePeriod(text: string): string {
  const t = clean(text);
  if (!t) return "";
  return /[.!?…]$/.test(t) ? t : `${t}.`;
}

function firstSentences(text: string, max = 2): string {
  const t = clean(text);
  if (!t) return "";
  const parts = t.split(/(?<=[.!?…])\s+/).filter(Boolean);
  if (parts.length <= max) return t;
  return parts.slice(0, max).join(" ");
}

function pushDistinct(out: string[], used: Set<string>, raw: string | null | undefined, maxLen = 320) {
  const t = clean(raw);
  if (!t || t.length < 8) return;
  const key = t.toLowerCase();
  if (used.has(key)) return;
  if ([...used].some((u) => u.includes(key.slice(0, 40)) || key.includes(u.slice(0, 40)))) return;
  used.add(key);
  out.push(t.length > maxLen ? `${t.slice(0, maxLen - 1).trim()}…` : t);
}

function fromFunnelInterpretation(payload: Record<string, unknown> | null | undefined): TodayDayMap | null {
  if (!payload || typeof payload !== "object") return null;
  const interp =
    (payload.funnel_interpretation as Record<string, unknown> | undefined) ||
    (payload.day_map as Record<string, unknown> | undefined) ||
    (String(payload.contract_version || "").includes("guide_funnel_interpretation") ? payload : null);
  if (!interp || typeof interp !== "object") return null;

  const whatHappens = ensurePeriod(firstSentences(String(interp.what_happens || ""), 3));
  if (whatHappens.length < 20) return null;

  const whyRaw = Array.isArray(interp.why_layers) ? interp.why_layers : [];
  const avoidRaw = Array.isArray(interp.avoid_hints) ? interp.avoid_hints : [];
  const used = new Set<string>();
  const whyLayers: string[] = [];
  for (const w of whyRaw) pushDistinct(whyLayers, used, String(w), 200);
  const avoidHints: string[] = [];
  const avoidUsed = new Set<string>();
  for (const a of avoidRaw) pushDistinct(avoidHints, avoidUsed, String(a), 160);

  return {
    whatHappens,
    whereConflict: ensurePeriod(String(interp.where_conflict || "")) || null,
    whereYouBreak: ensurePeriod(String(interp.where_you_break || "")) || null,
    whatWorks: ensurePeriod(String(interp.what_works || "")) || null,
    oneConcreteMove: clean(String(interp.one_concrete_move || "")) || null,
    whyLayers: whyLayers.slice(0, 3),
    avoidHints: avoidHints.slice(0, 3),
    source: "funnel_interpretation",
  };
}

function fromDayStory(contract: TodayContractV1): TodayDayMap | null {
  const ds = contract.day_story;
  if (!ds) return null;

  const foundation = ds.day_foundation;
  const essence = clean(foundation?.essence?.story_ru);
  const direction = clean(ds.direction);
  const story = clean(ds.story);
  const whatHappens = ensurePeriod(
    firstSentences(direction || essence || story, direction ? 2 : 2),
  );
  if (whatHappens.length < 16) return null;

  const abstain = ensurePeriod(clean(ds.abstain));
  const advantage = ensurePeriod(clean(ds.advantage));
  const move =
    clean(ds.today_move) ||
    clean(ds.primary_action) ||
    dayStoryDoItems(contract)[0] ||
    null;

  const used = new Set<string>([whatHappens.toLowerCase()]);
  const whyLayers: string[] = [];
  pushDistinct(whyLayers, used, clean(foundation?.astro?.summary_ru), 200);
  pushDistinct(whyLayers, used, clean(foundation?.lunar?.summary_ru), 200);
  pushDistinct(whyLayers, used, clean(ds.symbolic_note), 200);
  // Never dump global_period / development_point into why — those are the fact wall.

  const avoidHints: string[] = [];
  const avoidUsed = new Set<string>();
  for (const a of dayStoryAvoidItems(contract).slice(0, 3)) {
    pushDistinct(avoidHints, avoidUsed, a, 160);
  }
  if (!avoidHints.length && abstain) pushDistinct(avoidHints, avoidUsed, abstain, 160);

  // Soft "where you break": prefer domain risk over repeating abstain.
  let whereYouBreak: string | null = null;
  const domains = contract.domains;
  for (const key of ["money_work", "relationships", "family"] as const) {
    const lens = domains?.[key];
    const risk = lens && typeof lens === "object" ? clean((lens as { risk?: string }).risk) : "";
    if (risk && risk.length >= 12 && risk.toLowerCase() !== abstain.toLowerCase()) {
      whereYouBreak = ensurePeriod(firstSentences(risk, 2));
      break;
    }
  }

  return {
    whatHappens,
    whereConflict: abstain || null,
    whereYouBreak,
    whatWorks: advantage || null,
    oneConcreteMove: move,
    whyLayers: whyLayers.slice(0, 2),
    avoidHints: avoidHints.slice(0, 3),
    source: "day_story",
  };
}

/** Resolve Day Map for UI — funnel interpretation first, day_story fallback. */
export function buildTodayDayMap(input: {
  contract: TodayContractV1 | null | undefined;
  guideNarrativePayload?: Record<string, unknown> | null;
}): TodayDayMap | null {
  const fromGuide = fromFunnelInterpretation(input.guideNarrativePayload);
  if (fromGuide) return fromGuide;
  if (input.contract) return fromDayStory(input.contract);
  return null;
}
