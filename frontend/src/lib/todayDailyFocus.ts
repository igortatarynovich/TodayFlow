import type { TodayContractV1 } from "@/lib/todayContract";
import { isTodayInterpretationUnavailable } from "@/lib/todayContract";
import {
  dayStoryHeadline,
  dayStoryParagraphs,
  hasAuthoritativeDayStory,
} from "@/lib/todayContractMapper";
import {
  parseCoreMessageForUi,
  parseDayEngineBriefFromGuide,
  parseDayModelBriefFromGuide,
} from "@/components/today/todayGuideActionable";
import { buildTodayNarrativeV1 } from "@/lib/todayNarrativeFromContract";
import {
  filterDailyFocusLines,
  isDailyFocusKitchenLeak,
  isDailyFocusReject,
} from "@/lib/todayDailyFocusBoundary";
import { isHonestUnavailableCopy } from "@/lib/todaySlotAvailability";

export type DailyFocusModel = {
  dailyFocusId: string;
  title: string;
  lines: string[];
};

function narrativeString(payload: Record<string, unknown> | null | undefined, key: string): string | null {
  if (!payload || typeof payload !== "object") return null;
  const v = payload[key];
  return typeof v === "string" && v.trim() ? v.trim() : null;
}

function splitSentences(text: string): string[] {
  return text
    .split(/(?<=[.!?])\s+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

function isInternalGuideDump(text: string): boolean {
  const low = text.replace(/\s+/g, " ").trim().toLowerCase();
  if (!low) return true;
  return (
    low.startsWith("что происходит") ||
    low.includes("состояние после чек-") ||
    (low.includes("карта дня") && low.includes("число дня")) ||
    low.includes("по расчёту дня —")
  );
}

function descriptiveSentences(text: string | null | undefined): string[] {
  if (!text?.trim()) return [];
  return filterDailyFocusLines(splitSentences(text));
}

function descriptiveCandidatesFromGuide(payload: Record<string, unknown> | null): string[] {
  if (!payload) return [];
  const dayModel = parseDayModelBriefFromGuide(payload);
  const brief = parseDayEngineBriefFromGuide(payload);
  // Never promote tension.summary (kitchen diagnostic) into Daily Focus.
  const fromModel = [
    ...(dayModel?.vectorSummary ? descriptiveSentences(dayModel.vectorSummary) : []),
    ...(dayModel?.oneFocus ? descriptiveSentences(dayModel.oneFocus) : []),
  ];
  if (fromModel.length > 0) return fromModel;

  if (brief?.anchor) {
    const fromAnchor = descriptiveSentences(brief.anchor);
    if (fromAnchor.length > 0) return fromAnchor;
  }

  const parsed = parseCoreMessageForUi(payload);
  if (!parsed) return [];
  const raw =
    parsed.kind === "structured"
      ? [parsed.body]
      : parsed.paragraphs.filter((p) => !isInternalGuideDump(p));
  return filterDailyFocusLines(raw.flatMap((chunk) => splitSentences(chunk)));
}

function pickTitle(payload: Record<string, unknown> | null, contract: TodayContractV1): string {
  const candidates = descriptiveCandidatesFromGuide(payload);
  if (candidates[0]) {
    const first = candidates[0];
    return first.endsWith(".") || first.endsWith("!") || first.endsWith("?") ? first : `${first}.`;
  }

  const brief = parseDayEngineBriefFromGuide(payload);
  if (brief?.anchor) {
    const first = descriptiveSentences(brief.anchor)[0];
    if (first) {
      return first.endsWith(".") ? first : `${first}.`;
    }
  }

  const headline = narrativeString(payload, "headline");
  if (headline && !isDailyFocusReject(headline)) {
    return headline;
  }

  const subline = narrativeString(payload, "subline");
  if (subline && !isDailyFocusReject(subline)) {
    return subline;
  }

  const fallback = buildTodayNarrativeV1(contract).mainThought.headline || "";
  if (fallback && !isDailyFocusReject(fallback)) return fallback;
  return "";
}

function buildDailyFocusFromDayStory(contract: TodayContractV1): DailyFocusModel {
  const paragraphs = dayStoryParagraphs(contract);
  const headline = dayStoryHeadline(contract);
  const direction = contract.day_story?.direction?.trim();

  const titleRaw =
    (headline && !isDailyFocusReject(headline) ? headline : null) ||
    (paragraphs[0] && !isDailyFocusReject(paragraphs[0]) ? paragraphs[0] : null) ||
    (() => {
      const h = buildTodayNarrativeV1(contract).mainThought.headline || "";
      return h && !isDailyFocusReject(h) ? h : "";
    })();
  const title = !titleRaw
    ? ""
    : titleRaw.endsWith(".") || titleRaw.endsWith("!") || titleRaw.endsWith("?")
      ? titleRaw
      : `${titleRaw}.`;

  let lines = filterDailyFocusLines(
    paragraphs.filter((line) => line !== title.replace(/\.$/, "") && line !== title).slice(0, 2),
  );
  if (lines.length === 0 && direction && direction !== title.replace(/\.$/, "")) {
    lines = filterDailyFocusLines([direction.endsWith(".") ? direction : `${direction}.`]);
  }

  return {
    dailyFocusId: "day_story_v1",
    title,
    lines,
  };
}

/** S5 — Daily Focus only (не goal guidance, не action, не do_hint / best_move). */
export function buildDailyFocusModel(
  contract: TodayContractV1,
  guidePayload: Record<string, unknown> | null,
): DailyFocusModel {
  if (isTodayInterpretationUnavailable(contract)) {
    return { dailyFocusId: "day_focus", title: "", lines: [] };
  }
  if (hasAuthoritativeDayStory(contract)) {
    return buildDailyFocusFromDayStory(contract);
  }

  const fromPayload =
    typeof guidePayload?.daily_focus_id === "string" ? guidePayload.daily_focus_id.trim() : "";
  const dayModel = parseDayModelBriefFromGuide(guidePayload);
  const dailyFocusId = fromPayload || (dayModel ? "day_model_focus" : "day_focus");

  const candidates = descriptiveCandidatesFromGuide(guidePayload);
  const title = pickTitle(guidePayload, contract);
  let lines = candidates.filter((line) => line !== title.replace(/\.$/, "") && line !== title).slice(0, 2);

  if (lines.length === 0 && candidates[0]) {
    lines = candidates.slice(0, 2);
  }

  if (lines.length === 0) {
    const brief = parseDayEngineBriefFromGuide(guidePayload);
    if (brief?.anchor) {
      lines = descriptiveSentences(brief.anchor).slice(0, 2);
    }
  }

  return {
    dailyFocusId,
    title,
    lines,
  };
}

/** Fold card trap into Daily Focus lines — trap inside the scene, not a block after it. */
export function mergeTarotTrapIntoDailyFocus(
  focus: DailyFocusModel,
  trapLine: string | null | undefined,
): DailyFocusModel {
  const trap = (trapLine ?? "").replace(/\s+/g, " ").trim();
  if (!trap || trap.length < 12) return focus;
  const key = trap.slice(0, 28).toLowerCase();
  if (
    focus.title.toLowerCase().includes(key) ||
    focus.lines.some((l) => l.toLowerCase().includes(key))
  ) {
    return focus;
  }
  return {
    ...focus,
    lines: [...focus.lines.filter(Boolean).slice(0, 2), trap].slice(0, 3),
  };
}

/** Glance Screen 0 — one Daily Focus with prioritize / avoid (replaces ≤2 domain chips). */
export type GlanceDailyFocusModel = {
  dailyFocusId: string;
  title: string;
  /** What to keep in priority today — from day_story, not guide do_hint. */
  prioritize: string | null;
  /** What to avoid — from day_story.avoid / trap, not guide avoid_hint. */
  avoid: string | null;
};

function cleanDirectionLine(raw: string | null | undefined, title: string): string | null {
  const text = (raw ?? "").replace(/\s+/g, " ").trim();
  if (!text || text.length < 8) return null;
  if (isHonestUnavailableCopy(text)) return null;
  if (isDailyFocusKitchenLeak(text)) return null;
  // day_story do/avoid/trap are intentional direction — not guide do_hint / avoid_hint.
  // Kitchen/meta only here; keep intentional do/avoid even if imperative.
  const titleKey = title.replace(/[.!?]+$/u, "").trim().toLowerCase();
  if (titleKey && text.toLowerCase().startsWith(titleKey)) return null;
  if (titleKey && text.toLowerCase() === titleKey) return null;
  return text.endsWith(".") || text.endsWith("!") || text.endsWith("?") ? text : `${text}.`;
}

/**
 * Single Glance focus: title + direction (priority / avoid).
 * Canon: TODAY_SCREEN_V1 §7.7 / R15–R17 — not equal sphere chips.
 * Also used by legacy `?experience=1` synthesis (TodayDailyFocusBlock).
 */
export function buildGlanceDailyFocus(
  contract: TodayContractV1,
  guidePayload: Record<string, unknown> | null,
): GlanceDailyFocusModel {
  if (isTodayInterpretationUnavailable(contract)) {
    return { dailyFocusId: "day_focus", title: "", prioritize: null, avoid: null };
  }
  const base = buildDailyFocusModel(contract, guidePayload);
  const ds = contract.day_story;
  const prioritize =
    cleanDirectionLine(ds?.do?.[0], base.title) ||
    cleanDirectionLine(ds?.today_move, base.title) ||
    cleanDirectionLine(ds?.expect, base.title) ||
    cleanDirectionLine(base.lines[0], base.title);

  const avoid =
    cleanDirectionLine(ds?.avoid?.[0], base.title) ||
    cleanDirectionLine(ds?.trap, base.title) ||
    cleanDirectionLine(ds?.abstain, base.title);

  return {
    dailyFocusId: base.dailyFocusId,
    title: base.title,
    prioritize,
    avoid: avoid && avoid !== prioritize ? avoid : null,
  };
}

/**
 * Fold card trap into Glance avoid — only when day_story left avoid empty.
 * Does not overwrite day_story avoid (SoT).
 */
export function mergeTarotTrapIntoGlanceDailyFocus(
  focus: GlanceDailyFocusModel,
  trapLine: string | null | undefined,
): GlanceDailyFocusModel {
  if (focus.avoid) return focus;
  const trap = cleanDirectionLine(trapLine, focus.title);
  if (!trap || trap === focus.prioritize) return focus;
  return { ...focus, avoid: trap };
}
