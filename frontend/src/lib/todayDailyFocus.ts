import type { TodayContractV1 } from "@/lib/todayContract";
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
import { filterDailyFocusLines, isDailyFocusGuidanceLeak } from "@/lib/todayDailyFocusBoundary";

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
  const fromModel = [
    ...(dayModel?.vectorSummary ? descriptiveSentences(dayModel.vectorSummary) : []),
    ...(dayModel?.oneFocus ? descriptiveSentences(dayModel.oneFocus) : []),
    ...(dayModel?.tempoLabel && dayModel.tensionSummary
      ? descriptiveSentences(dayModel.tensionSummary.split(";")[0])
      : []),
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
  if (headline && !isDailyFocusGuidanceLeak(headline)) {
    return headline;
  }

  const subline = narrativeString(payload, "subline");
  if (subline && !isDailyFocusGuidanceLeak(subline)) {
    return subline;
  }

  return buildTodayNarrativeV1(contract).mainThought.headline || "О чём этот день";
}

function buildDailyFocusFromDayStory(contract: TodayContractV1): DailyFocusModel {
  const paragraphs = dayStoryParagraphs(contract);
  const headline = dayStoryHeadline(contract);
  const direction = contract.day_story?.direction?.trim();

  const titleCandidate = headline || paragraphs[0] || buildTodayNarrativeV1(contract).mainThought.headline;
  const title =
    titleCandidate.endsWith(".") || titleCandidate.endsWith("!") || titleCandidate.endsWith("?")
      ? titleCandidate
      : `${titleCandidate}.`;

  let lines = filterDailyFocusLines(
    paragraphs.filter((line) => line !== title.replace(/\.$/, "") && line !== title).slice(0, 2),
  );
  if (lines.length === 0 && direction && direction !== title.replace(/\.$/, "")) {
    lines = filterDailyFocusLines([direction.endsWith(".") ? direction : `${direction}.`]);
  }
  if (lines.length === 0 && contract.personal_growth?.development_point) {
    const dev = contract.personal_growth.development_point.trim();
    if (dev && !isDailyFocusGuidanceLeak(dev)) {
      lines = filterDailyFocusLines([dev]);
    }
  }
  if (lines.length === 0) {
    lines = ["Сегодня внимание смещается к одной понятной теме дня — без списка задач."];
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

  if (lines.length === 0 && contract.personal_growth?.development_point) {
    const dev = contract.personal_growth.development_point.trim();
    if (dev && !isDailyFocusGuidanceLeak(dev)) {
      lines = [dev];
    }
  }

  if (lines.length === 0) {
    lines = ["Сегодня внимание смещается к одной понятной теме дня — без списка задач."];
  }

  return {
    dailyFocusId,
    title,
    lines,
  };
}
