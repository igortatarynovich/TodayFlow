/**
 * Day Map — one causal day picture for Today UI.
 *
 * Prefer authoritative day_story (expect/trap/do/avoid) over guide funnel.
 * Slot semantics for UI:
 * - eventsLead → «Почему такой день» only
 * - whatWorks → «Чего ожидать» (day_story.expect scene)
 * - whereConflict → «Ловушка» (day_story.trap only)
 * - doHints / avoidHints → instruction only
 * - primaryConflict → hero only (not reprinted in chapters)
 */

import type { TodayContractV1 } from "@/lib/todayContract";
import { dayStoryAvoidItems, dayStoryDoItems } from "@/lib/todayContractMapper";
import { scenarioConflictLabel } from "@/lib/todayDaySpine";
import { nearDuplicateClaim, scrubUserFacingText } from "@/lib/todayValueGate";

export type TodayDayMap = {
  /** Primary conflict label when known — hero only. */
  primaryConflict: string | null;
  /** Sky drivers paragraph — «Почему такой день». */
  eventsLead: string | null;
  /** Short pulse distinct from expect; not a third plot dump. */
  whatHappens: string;
  whereConflict: string | null;
  whereYouBreak: string | null;
  whatWorks: string | null;
  oneConcreteMove: string | null;
  whyLayers: string[];
  avoidHints: string[];
  doHints: string[];
  vibeClosing: string | null;
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

function gate(text: string | null | undefined): string {
  return scrubUserFacingText(text) ?? "";
}

function firstSentences(text: string, max = 2): string {
  const t = clean(text);
  if (!t) return "";
  const parts = t.split(/(?<=[.!?…])\s+/).filter(Boolean);
  if (parts.length <= max) return t;
  return parts.slice(0, max).join(" ");
}

function pushDistinct(out: string[], used: Set<string>, raw: string | null | undefined, maxLen = 320) {
  const t = gate(raw);
  if (!t || t.length < 8) return;
  const key = t.toLowerCase();
  if (used.has(key)) return;
  if (Array.from(used).some((u) => nearDuplicateClaim(u, key))) return;
  used.add(key);
  out.push(t.length > maxLen ? `${t.slice(0, maxLen - 1).trim()}…` : t);
}

function nearDuplicate(a: string, b: string): boolean {
  return nearDuplicateClaim(a, b);
}

function fromFunnelInterpretation(payload: Record<string, unknown> | null | undefined): TodayDayMap | null {
  if (!payload || typeof payload !== "object") return null;
  const interp =
    (payload.funnel_interpretation as Record<string, unknown> | undefined) ||
    (payload.day_map as Record<string, unknown> | undefined) ||
    (String(payload.contract_version || "").includes("guide_funnel_interpretation") ? payload : null);
  if (!interp || typeof interp !== "object") return null;

  const expectScene = ensurePeriod(
    firstSentences(gate(String(interp.events_lead || interp.what_happens || "")), 2),
  );
  const whatHappens = ensurePeriod(firstSentences(gate(String(interp.what_happens || "")), 2));
  if (whatHappens.length < 20 && expectScene.length < 20) return null;

  const whyRaw = Array.isArray(interp.why_layers) ? interp.why_layers : [];
  const avoidRaw = Array.isArray(interp.avoid_hints) ? interp.avoid_hints : [];
  const used = new Set<string>();
  const whyLayers: string[] = [];
  for (const w of whyRaw) pushDistinct(whyLayers, used, String(w), 200);
  const avoidHints: string[] = [];
  const avoidUsed = new Set<string>();
  for (const a of avoidRaw) pushDistinct(avoidHints, avoidUsed, String(a), 160);

  const pulse = whatHappens.length >= 20 ? whatHappens : expectScene;
  const expectPanel =
    expectScene && !nearDuplicate(expectScene, pulse)
      ? expectScene
      : ensurePeriod(gate(String(interp.what_works || ""))) || null;

  return {
    primaryConflict: gate(String(interp.primary_conflict || "")) || null,
    eventsLead: ensurePeriod(gate(String(interp.events_lead || ""))) || null,
    whatHappens: pulse,
    whereConflict: ensurePeriod(gate(String(interp.where_conflict || ""))) || null,
    whereYouBreak: ensurePeriod(gate(String(interp.where_you_break || ""))) || null,
    whatWorks: expectPanel,
    oneConcreteMove: gate(String(interp.one_concrete_move || "")) || null,
    whyLayers: whyLayers.slice(0, 3),
    avoidHints: avoidHints.slice(0, 3),
    doHints: [],
    vibeClosing: null,
    source: "funnel_interpretation",
  };
}

function fromDayStory(contract: TodayContractV1): TodayDayMap | null {
  const ds = contract.day_story;
  if (!ds) return null;

  const foundation = ds.day_foundation;
  const essence = gate(foundation?.essence?.story_ru);
  const expect = gate(ds.expect);
  const eventsLead = gate(ds.events_lead);
  const direction = gate(ds.direction);
  const story = gate(ds.story);
  const thesisLabel =
    scenarioConflictLabel(contract) ||
    gate(ds.day_thesis?.label_ru) ||
    gate(ds.day_thesis?.label) ||
    gate(ds.primary_conflict) ||
    gate(ds.headline_anchor);
  const conflict = thesisLabel;

  // Expect panel = everyday scene from day_story.expect (not advantage/do).
  const expectPanel = ensurePeriod(firstSentences(expect || direction, 2));
  // Pulse for hero subtitle only — prefer events, never reprint expect.
  let pulse = ensurePeriod(firstSentences(eventsLead || essence || story, 1));
  if (!pulse || nearDuplicate(pulse, expectPanel) || nearDuplicate(pulse, conflict)) {
    pulse = "";
  }
  if (expectPanel.length < 16 && !eventsLead && !conflict) return null;
  if (!pulse && expectPanel) {
    pulse = ensurePeriod(firstSentences(expectPanel, 1));
  }

  const trap = ensurePeriod(gate(ds.trap) || gate(ds.abstain));
  const move =
    gate(ds.today_move) ||
    gate(contract.primary_action) ||
    dayStoryDoItems(contract).map(gate).find(Boolean) ||
    null;

  const used = new Set<string>([pulse.toLowerCase(), expectPanel.toLowerCase()].filter(Boolean));
  const whyLayers: string[] = [];
  pushDistinct(whyLayers, used, eventsLead, 240);
  pushDistinct(whyLayers, used, gate(foundation?.astro?.summary_ru), 200);
  pushDistinct(whyLayers, used, gate(foundation?.lunar?.summary_ru), 200);
  pushDistinct(whyLayers, used, gate(ds.symbolic_note), 200);

  const avoidHints: string[] = [];
  const avoidUsed = new Set<string>();
  for (const a of dayStoryAvoidItems(contract).slice(0, 3)) {
    pushDistinct(avoidHints, avoidUsed, a, 160);
  }

  const doHints: string[] = [];
  const doUsed = new Set<string>();
  for (const d of dayStoryDoItems(contract).slice(0, 3)) {
    pushDistinct(doHints, doUsed, d, 160);
  }

  // whereYouBreak stays domain risk only — never tarot/profile dumps.
  let whereYouBreak: string | null = null;
  const domains = contract.domains;
  for (const key of ["money_work", "relationships", "family"] as const) {
    const lens = domains?.[key];
    const risk = lens && typeof lens === "object" ? gate((lens as { risk?: string }).risk) : "";
    if (risk && risk.length >= 12 && !nearDuplicate(risk, trap)) {
      whereYouBreak = ensurePeriod(firstSentences(risk, 2));
      break;
    }
  }

  return {
    primaryConflict: conflict || null,
    eventsLead: ensurePeriod(eventsLead) || null,
    whatHappens: pulse || expectPanel || conflict || "",
    whereConflict: trap || null,
    whereYouBreak,
    whatWorks: expectPanel && !nearDuplicate(expectPanel, conflict) ? expectPanel : null,
    oneConcreteMove: move,
    whyLayers: whyLayers.slice(0, 3),
    avoidHints: avoidHints.slice(0, 3),
    doHints: doHints.slice(0, 3),
    vibeClosing: resolveVibeClosing(ds),
    source: "day_story",
  };
}

function resolveVibeClosing(ds: NonNullable<TodayContractV1["day_story"]>): string | null {
  const strokes = Array.isArray(ds.vibe_strokes)
    ? ds.vibe_strokes.map((s) => gate(s)).filter(Boolean)
    : [];
  if (strokes.length) return strokes.join("; ");
  return gate(ds.vibe_closing) || null;
}

/**
 * Prefer day_story when it has expect/trap (authoritative plot slots).
 * Funnel only fills when day_story is thin — never invent a second plot.
 */
export function buildTodayDayMap(input: {
  contract: TodayContractV1 | null | undefined;
  guideNarrativePayload?: Record<string, unknown> | null;
}): TodayDayMap | null {
  const fromStory = input.contract ? fromDayStory(input.contract) : null;
  const thesisLabel =
    (input.contract ? scenarioConflictLabel(input.contract) : null) ||
    gate(input.contract?.day_story?.day_thesis?.label_ru) ||
    gate(input.contract?.day_story?.day_thesis?.label) ||
    gate(input.contract?.day_story?.primary_conflict) ||
    "";

  const storyHasPlot =
    Boolean(fromStory?.whatWorks || fromStory?.whereConflict) &&
    fromStory?.source === "day_story";

  if (storyHasPlot && fromStory) {
    if (thesisLabel) return { ...fromStory, primaryConflict: thesisLabel };
    return fromStory;
  }

  const fromGuide = fromFunnelInterpretation(input.guideNarrativePayload);
  if (fromGuide) {
    if (thesisLabel) return { ...fromGuide, primaryConflict: thesisLabel };
    return fromGuide;
  }
  return fromStory;
}
