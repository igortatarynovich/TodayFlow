/**
 * Сигналы ритуала «Сегодня»: possible / avoid / support и разбор day_layer.
 * Паритет с `TodayRitualSignals.swift` (iOS).
 */
import {
  isGarbageRitualActionCue,
  replaceQuotedEnSlugsForRuDisplay,
  repairRitualDoNotEnterLine,
} from "@/components/today/ritualCueSanitizer";

export const RITUAL_GUIDANCE_SUMMARY_FALLBACK =
  "Открой день одним действием, которое убирает шум.";

function trimS(s: string | null | undefined): string {
  return (s || "").trim();
}

export type MorningLike = {
  daily_recommendations?: {
    what_to_do?: string | null;
    what_to_avoid?: string | null;
    priorities?: unknown;
  } | null;
  daily_horoscope?: {
    spine?: {
      best_mode?: string | null;
      first_move?: string | null;
      do_not_enter?: string | null;
    } | null;
  } | null;
  daily_forecast_summary?: { summary?: string | null } | null;
} | null | undefined;

export function firstPriorityLine(morning: MorningLike): string | null {
  const raw = morning?.daily_recommendations?.priorities;
  if (!Array.isArray(raw)) return null;
  for (const x of raw) {
    if (typeof x === "string") {
      const t = x.trim();
      if (t) return t;
    }
  }
  return null;
}

/** Как в iOS: what_to_do → first_move → forecast (до 3 строк, без дублей). */
export function buildRitualPossibleSignals(morning: MorningLike): string[] {
  const a: string[] = [];
  const wtd = replaceQuotedEnSlugsForRuDisplay(trimS(morning?.daily_recommendations?.what_to_do));
  if (wtd && !isGarbageRitualActionCue(wtd)) a.push(wtd);
  const fm = replaceQuotedEnSlugsForRuDisplay(trimS(morning?.daily_horoscope?.spine?.first_move));
  if (fm && !isGarbageRitualActionCue(fm) && !a.includes(fm)) a.push(fm);
  const summary = replaceQuotedEnSlugsForRuDisplay(trimS(morning?.daily_forecast_summary?.summary));
  if (summary && !isGarbageRitualActionCue(summary) && a.length < 3) a.push(summary);
  return a.slice(0, 3);
}

export function buildRitualAvoidSignals(morning: MorningLike): string[] {
  const a: string[] = [];
  const wta = replaceQuotedEnSlugsForRuDisplay(trimS(morning?.daily_recommendations?.what_to_avoid));
  if (wta) a.push(wta);
  const dneRaw = trimS(morning?.daily_horoscope?.spine?.do_not_enter);
  const dne = dneRaw ? repairRitualDoNotEnterLine(dneRaw) : "";
  if (dne && !a.includes(dne)) a.push(dne);
  return a;
}

/**
 * Если есть best_mode — три опоры; иначе одна строка (как `dashboard.guidanceSummary` на iOS).
 */
export function buildRitualSupportSignals(bestMode: string, guidanceSummary: string): string[] {
  const b = trimS(bestMode);
  if (b) return [b, "Тишина", "Структура"];
  const g = trimS(guidanceSummary);
  return [g || RITUAL_GUIDANCE_SUMMARY_FALLBACK];
}

export function guidanceSummaryForRitual(args: {
  morning: MorningLike;
  actionPlanFirstLine: string | null | undefined;
}): string {
  const p = firstPriorityLine(args.morning);
  if (p) return p;
  const first = trimS(args.actionPlanFirstLine);
  if (first) return first;
  return RITUAL_GUIDANCE_SUMMARY_FALLBACK;
}

function str(v: unknown): string | null {
  if (typeof v !== "string") return null;
  const t = v.trim();
  return t || null;
}

export type ParsedDayLayerNarrative = {
  nudgeMessage: string | null;
  personalTitle: string | null;
  personalBody: string | null;
  chips: string[];
  lifeWeekly: string | null;
  lifeDiscipline: string | null;
  questionPrompt: string | null;
  miniDecisionCaption: string | null;
};

/** Поля payload поверхности `day_layer` из `/today/narrative`. */
export function parseDayLayerPayload(
  payload: Record<string, unknown> | null | undefined,
): ParsedDayLayerNarrative {
  if (!payload) {
    return {
      nudgeMessage: null,
      personalTitle: null,
      personalBody: null,
      chips: [],
      lifeWeekly: null,
      lifeDiscipline: null,
      questionPrompt: null,
      miniDecisionCaption: null,
    };
  }
  const chipsRaw = payload.personal_insight_chips;
  const chips = Array.isArray(chipsRaw)
    ? chipsRaw.map((x) => (typeof x === "string" ? x.trim() : "")).filter(Boolean)
    : [];
  return {
    nudgeMessage: str(payload.nudge_message),
    personalTitle: str(payload.personal_insight_title),
    personalBody: str(payload.personal_insight_body),
    chips,
    lifeWeekly: str(payload.life_now_weekly),
    lifeDiscipline: str(payload.life_now_discipline),
    questionPrompt: str(payload.question_of_day_prompt),
    miniDecisionCaption: str(payload.mini_decision_caption),
  };
}

export function dayLayerHasContent(p: ParsedDayLayerNarrative): boolean {
  return !!(
    p.nudgeMessage ||
    p.personalTitle ||
    p.personalBody ||
    p.chips.length ||
    p.lifeWeekly ||
    p.lifeDiscipline ||
    p.questionPrompt ||
    p.miniDecisionCaption
  );
}
