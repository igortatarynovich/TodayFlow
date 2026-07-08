/**
 * Веб `/guidance/history` — зеркало `GuidanceHistoryChromeCopy.swift`.
 * Строки: `CONTENT/i18n/app.{ru,en}.json` (`nav.guidance.hub`, `guidance.history.*`).
 */

import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { t } from "@/lib/i18n";

export interface GuidanceHistoryChromeBundle {
  guidanceHistoryNavHub: string;
  guidanceHistoryBackToday: string;
  guidanceHistoryTitle: string;
  guidanceHistoryHeroLead: string;
  guidanceHistoryNewSpreadCta: string;
  guidanceHistoryLinkHub: string;
  guidanceHistoryTopNavAria: string;
  guidanceHistoryFiltersAria: string;
  guidanceHistoryFilterAll: string;
  guidanceHistoryFilterGuidance: string;
  guidanceHistoryFilterQuestions: string;
  guidanceHistoryFilterDecisions: string;
  guidanceHistoryFilterTarot: string;
  guidanceHistoryLoading: string;
  guidanceHistoryError: string;
  guidanceHistoryEmptyCategory: string;
  guidanceHistoryListAria: string;
  guidanceHistoryKindGuidance: string;
  guidanceHistoryKindClarify: string;
  guidanceHistoryKindDecision: string;
  guidanceHistoryKindQuestion: string;
  guidanceHistoryKindTarot: string;
  guidanceHistoryRouteOpenReading: string;
  guidanceHistoryRouteDecisionMode: string;
  guidanceHistoryRouteQuestionMode: string;
  guidanceHistoryRouteCardOfDay: string;
  guidanceHistoryRouteTarot: string;
  guidanceHistoryTarotSpreadNoBody: string;
  guidanceHistoryTarotDailyNextStep: string;
  guidanceHistoryTarotNextStepCta: string;
  guidanceHistoryFocusFallback: string;
  guidanceHistoryNextStepFallback: string;
  guidanceHistoryMetaTopic: string;
  guidanceHistoryMetaSpread: string;
  guidanceHistoryMetaLeadCard: string;
  guidanceHistoryMetaShort: string;
  guidanceHistoryMetaNextStep: string;
}

export function guidanceHistoryChromeBundle(locale: FlowPracticesChromeLocale): GuidanceHistoryChromeBundle {
  const loc = locale === "ru" ? "ru" : "en";
  const tr = (key: string, defaultEn: string) => t(key, defaultEn, undefined, loc);

  return {
    guidanceHistoryNavHub: tr("nav.guidance.hub", "Guidance hub"),
    guidanceHistoryBackToday: tr("guidance.history.backToday", "← Today"),
    guidanceHistoryTitle: tr("guidance.history.title", "History"),
    guidanceHistoryHeroLead: tr(
      "guidance.history.heroLead",
      "Readings from the same screen—your question, spread, and cards—plus quick answers without tarot and your card-of-the-day draws. One feed to spot recurring themes.",
    ),
    guidanceHistoryNewSpreadCta: tr("guidance.history.newSpreadCta", "New spread"),
    guidanceHistoryLinkHub: tr("guidance.history.linkHub", "Guidance hub"),
    guidanceHistoryTopNavAria: tr("guidance.history.topNavAria", "History — navigation"),
    guidanceHistoryFiltersAria: tr("guidance.history.filtersAria", "Filter entries"),
    guidanceHistoryFilterAll: tr("guidance.history.filterAll", "All"),
    guidanceHistoryFilterGuidance: tr("guidance.history.filterGuidance", "Guidance"),
    guidanceHistoryFilterQuestions: tr("guidance.history.filterQuestions", "Questions"),
    guidanceHistoryFilterDecisions: tr("guidance.history.filterDecisions", "Decisions"),
    guidanceHistoryFilterTarot: tr("guidance.history.filterTarot", "Tarot"),
    guidanceHistoryLoading: tr("guidance.history.loading", "Loading history…"),
    guidanceHistoryError: tr("guidance.history.error", "Couldn’t load history."),
    guidanceHistoryEmptyCategory: tr("guidance.history.emptyCategory", "No entries in this filter yet."),
    guidanceHistoryListAria: tr("guidance.history.listAria", "History entries"),
    guidanceHistoryKindGuidance: tr("guidance.history.kind.guidance", "Guidance"),
    guidanceHistoryKindClarify: tr("guidance.history.kind.clarify", "Guidance · clarify"),
    guidanceHistoryKindDecision: tr("guidance.history.kind.decision", "Decision"),
    guidanceHistoryKindQuestion: tr("guidance.history.kind.question", "Question"),
    guidanceHistoryKindTarot: tr("guidance.history.kind.tarot", "Tarot"),
    guidanceHistoryRouteOpenReading: tr("guidance.history.route.openReading", "Open Guidance"),
    guidanceHistoryRouteDecisionMode: tr("guidance.history.route.decisionMode", "Decision mode"),
    guidanceHistoryRouteQuestionMode: tr("guidance.history.route.questionMode", "Question mode"),
    guidanceHistoryRouteCardOfDay: tr("guidance.history.route.cardOfDay", "Card of the day"),
    guidanceHistoryRouteTarot: tr("guidance.history.route.tarot", "Tarot"),
    guidanceHistoryTarotSpreadNoBody: tr(
      "guidance.history.tarot.spreadNoBody",
      "Spread saved without an in-app reading text.",
    ),
    guidanceHistoryTarotDailyNextStep: tr(
      "guidance.history.tarot.dailyNextStep",
      "Notice how this theme shows up in one concrete action today.",
    ),
    guidanceHistoryTarotNextStepCta: tr(
      "guidance.history.tarot.nextStepCta",
      "If you want a reading for a question, open the Guidance hub on one screen, lay the spread, and tap “Get reading”.",
    ),
    guidanceHistoryFocusFallback: tr("guidance.history.focusFallback", "Focus sharpens from your latest answers."),
    guidanceHistoryNextStepFallback: tr(
      "guidance.history.nextStepFallback",
      "Take one small step on the topic of your question.",
    ),
    guidanceHistoryMetaTopic: tr("guidance.history.meta.topic", "Topic:"),
    guidanceHistoryMetaSpread: tr("guidance.history.meta.spread", "Spread:"),
    guidanceHistoryMetaLeadCard: tr("guidance.history.meta.leadCard", "Lead card:"),
    guidanceHistoryMetaShort: tr("guidance.history.meta.short", "In short:"),
    guidanceHistoryMetaNextStep: tr("guidance.history.meta.nextStep", "Next step:"),
  };
}
