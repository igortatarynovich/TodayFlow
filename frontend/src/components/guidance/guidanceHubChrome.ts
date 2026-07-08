/**
 * Веб `/guidance` (хаб расклада) — зеркало `GuidanceHubChromeCopy.swift`.
 * Строки: `CONTENT/i18n/app.{ru,en}.json` (`nav.guidance.hub`, `guidance.page.*`, `guidance.catalog.spreadField`, `guidance.catalog.section.*`).
 */

import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import type { GuidanceSpreadSection } from "@/lib/guidance/catalog";
import { t } from "@/lib/i18n";

export function guidanceHubInterpolate(template: string, vars: Record<string, string>): string {
  return template.replace(/\{(\w+)\}/g, (_, key: string) => vars[key] ?? `{${key}}`);
}

/** Секционные маркеры без локали. */
const GLYPH_CLARIFY_SECTION = "→";
const GLYPH_RESULT_SECTION = "✓";

export interface GuidanceHubChromeBundle {
  guidanceHubNavHub: string;
  guidanceHubBackToday: string;
  guidanceHubHeroTitle: string;
  guidanceHubHeroLead: string;
  guidanceHubHistoryLink: string;
  guidanceHubStartOver: string;
  guidanceHubTopNavAria: string;
  guidanceHubCompatHint: string;
  guidanceHubUnauthTitle: string;
  guidanceHubUnauthLead: string;
  guidanceHubPlansLink: string;
  guidanceHubSectionSpreadTitle: string;
  guidanceHubSpreadField: string;
  guidanceHubCatalogSectionQuick: string;
  guidanceHubCatalogSectionMedium: string;
  guidanceHubCatalogSectionDeep: string;
  guidanceHubSectionSpreadLead: string;
  guidanceHubClarifyOneCardLockedNote: string;
  guidanceHubSectionQuestionTitle: string;
  guidanceHubSectionQuestionLead: string;
  guidanceHubQuestionPlaceholder: string;
  guidanceHubQuestionAriaLabel: string;
  guidanceHubQuestionLockedMain: string;
  guidanceHubQuestionAvoidHint: string;
  guidanceHubSectionContextTitle: string;
  guidanceHubSectionContextLead: string;
  guidanceHubFieldTopic: string;
  guidanceHubFieldOutcome: string;
  guidanceHubFieldRelationshipRole: string;
  guidanceHubFieldIntimacyFocus: string;
  guidanceHubClarifyGoalTitle: string;
  guidanceHubClarifyGoalLead: string;
  guidanceHubClarifySectionGlyph: string;
  guidanceHubSectionCardsTitle: string;
  guidanceHubCardsLeadClarify: string;
  guidanceHubCardsLeadNormal: string;
  guidanceHubDealDrawing: string;
  guidanceHubDealReshuffle: string;
  guidanceHubDealShuffle: string;
  guidanceHubDealReadyHint: string;
  guidanceHubCardsRevealHint: string;
  guidanceHubSubmitClarify: string;
  guidanceHubSubmitReading: string;
  guidanceHubSubmitHintClarify: string;
  guidanceHubSubmitHintQuestion: string;
  guidanceHubLoadingTitle: string;
  guidanceHubLoadingLeadClarify: string;
  guidanceHubLoadingLeadMain: string;
  guidanceHubResultSectionGlyph: string;
  guidanceHubResultTitle: string;
  guidanceHubNewSpreadCta: string;
  guidanceHubToastNoSessionToken: string;
  guidanceHubToastSessionExpired: string;
  guidanceHubToastDealFailed: string;
  guidanceHubToastQuestionVague: string;
  guidanceHubToastRevealAllFirst: string;
  guidanceHubToastNoSessionReading: string;
  guidanceHubToastClarifyOneCardOnly: string;
  guidanceHubToastClarifyAlready409: string;
  guidanceHubToastReadingFailed: string;
  guidanceHubToastFeedbackSavedHelpful: string;
  guidanceHubToastFeedbackSavedUnclear: string;
  guidanceHubToastFeedbackSaveFailed: string;
  guidanceHubToastNeedMainReading: string;
  guidanceHubToastClarifyAlreadyUsed: string;
}

export function guidanceHubChromeBundle(locale: FlowPracticesChromeLocale): GuidanceHubChromeBundle {
  const loc = locale === "ru" ? "ru" : "en";
  const tr = (key: string, defaultEn: string) => t(key, defaultEn, undefined, loc);

  return {
    guidanceHubNavHub: tr("nav.guidance.hub", "Guidance hub"),
    guidanceHubBackToday: tr("guidance.page.backToday", "← Today"),
    guidanceHubHeroTitle: tr("guidance.page.heroTitle", "A grounded reading with cards"),
    guidanceHubHeroLead: tr(
      "guidance.page.heroLead",
      "Everything on one page: scroll top to bottom—spread, question, optional context, then cards and your reading request.",
    ),
    guidanceHubHistoryLink: tr("guidance.page.historyLink", "History"),
    guidanceHubStartOver: tr("guidance.page.startOver", "Start over"),
    guidanceHubTopNavAria: tr("guidance.page.topNavAria", "Guidance — navigation"),
    guidanceHubCompatHint: tr(
      "guidance.page.compatHint",
      "For couples there’s also Compatibility—this reading flow still handles relationship dynamics well.",
    ),
    guidanceHubUnauthTitle: tr("guidance.page.unauthTitle", "A grounded reading with cards"),
    guidanceHubUnauthLead: tr(
      "guidance.page.unauthLead",
      "Sign in to lay a spread on one screen and get a personal answer that respects your profile.",
    ),
    guidanceHubPlansLink: tr("guidance.page.plansLink", "Plans"),
    guidanceHubSectionSpreadTitle: tr("guidance.page.sectionSpreadTitle", "Spread format"),
    guidanceHubSpreadField: tr("guidance.catalog.spreadField", "Spread"),
    guidanceHubCatalogSectionQuick: tr("guidance.catalog.section.quick", "Quick spreads"),
    guidanceHubCatalogSectionMedium: tr("guidance.catalog.section.medium", "Medium spreads"),
    guidanceHubCatalogSectionDeep: tr("guidance.catalog.section.deep", "Deep spreads"),
    guidanceHubSectionSpreadLead: tr(
      "guidance.page.sectionSpreadLead",
      "Short or expanded—match the situation. Changing the format clears any cards you already dealt.",
    ),
    guidanceHubClarifyOneCardLockedNote: tr(
      "guidance.page.clarifyOneCardLockedNote",
      "Right now only the clarifying “one card” spread is available—the main spread stays locked until you finish or choose “{startOver}”.",
    ),
    guidanceHubSectionQuestionTitle: tr("guidance.page.sectionQuestionTitle", "Your question"),
    guidanceHubSectionQuestionLead: tr(
      "guidance.page.sectionQuestionLead",
      "Ask for clarity and action—not a guaranteed outcome. The more concrete the wording, the more useful the answer.",
    ),
    guidanceHubQuestionPlaceholder: tr(
      "guidance.page.questionPlaceholder",
      "Examples:\n• What's important for me to understand here?\n• What's the wisest move for me right now?\n• What am I missing in my own reaction?",
    ),
    guidanceHubQuestionAriaLabel: tr("guidance.page.questionAriaLabel", "Your question for the spread"),
    guidanceHubQuestionLockedMain: tr(
      "guidance.page.questionLockedMain",
      "The main question is locked for this reading: “{question}”",
    ),
    guidanceHubQuestionAvoidHint: tr(
      "guidance.page.questionAvoidHint",
      "Avoid “will they definitely…” and “will I definitely get…”—this isn’t about predicting outcomes.",
    ),
    guidanceHubSectionContextTitle: tr("guidance.page.sectionContextTitle", "Context (optional)"),
    guidanceHubSectionContextLead: tr(
      "guidance.page.sectionContextLead",
      "Topic and intent help tailor the reading. You can leave everything unset.",
    ),
    guidanceHubFieldTopic: tr("guidance.page.fieldTopic", "Topic"),
    guidanceHubFieldOutcome: tr("guidance.page.fieldOutcome", "What you want from this"),
    guidanceHubFieldRelationshipRole: tr("guidance.page.fieldRelationshipRole", "Who this person is to you"),
    guidanceHubFieldIntimacyFocus: tr("guidance.page.fieldIntimacyFocus", "What worries you most"),
    guidanceHubClarifyGoalTitle: tr("guidance.page.clarifyGoalTitle", "Goal of the clarifying card"),
    guidanceHubClarifyGoalLead: tr(
      "guidance.page.clarifyGoalLead",
      "Pick one narrow focus—so the reading doesn't turn into endless back-and-forth.",
    ),
    guidanceHubClarifySectionGlyph: GLYPH_CLARIFY_SECTION,
    guidanceHubSectionCardsTitle: tr("guidance.page.sectionCardsTitle", "Cards"),
    guidanceHubCardsLeadClarify: tr(
      "guidance.page.cardsLeadClarify",
      "One card in the “Focus” position. Deal and reveal it—then request clarification (the server allows at most one per main reading).",
    ),
    guidanceHubCardsLeadNormal: tr(
      "guidance.page.cardsLeadNormal",
      "Shuffle for “{spreadTitle}”, then reveal each position one at a time. When everything is open and your question is ready—request the reading.",
    ),
    guidanceHubDealDrawing: tr("guidance.page.dealDrawing", "Shuffling…"),
    guidanceHubDealReshuffle: tr("guidance.page.dealReshuffle", "Re-deal cards"),
    guidanceHubDealShuffle: tr("guidance.page.dealShuffle", "Deal cards"),
    guidanceHubDealReadyHint: tr(
      "guidance.page.dealReadyHint",
      "Tap “Deal cards” when you're ready to focus on your question.",
    ),
    guidanceHubCardsRevealHint: tr(
      "guidance.page.cardsRevealHint",
      "Reveal every position—then the “Get reading” button becomes active.",
    ),
    guidanceHubSubmitClarify: tr("guidance.page.submitClarify", "Get clarification"),
    guidanceHubSubmitReading: tr("guidance.page.submitReading", "Get reading"),
    guidanceHubSubmitHintClarify: tr("guidance.page.submitHintClarify", "Pick a clarification goal above and reveal the card."),
    guidanceHubSubmitHintQuestion: tr(
      "guidance.page.submitHintQuestion",
      "Refine your question above first (at least three characters).",
    ),
    guidanceHubLoadingTitle: tr("guidance.page.loadingTitle", "Building your reading…"),
    guidanceHubLoadingLeadClarify: tr(
      "guidance.page.loadingLeadClarify",
      "We're linking one card to your main reading and the goal you chose.",
    ),
    guidanceHubLoadingLeadMain: tr(
      "guidance.page.loadingLeadMain",
      "We weigh your question, positions, and profile—it's a coherent take for your situation, not a dictionary of meanings.",
    ),
    guidanceHubResultSectionGlyph: GLYPH_RESULT_SECTION,
    guidanceHubResultTitle: tr("guidance.page.resultTitle", "Reading"),
    guidanceHubNewSpreadCta: tr("guidance.page.newSpreadCta", "New spread"),
    guidanceHubToastNoSessionToken: tr(
      "guidance.page.toast.noSessionToken",
      "No session token in the browser. Sign out and back in—without an Authorization header the API returns 401.",
    ),
    guidanceHubToastSessionExpired: tr("guidance.page.toast.sessionExpired", "Session invalid or expired. Please sign in again."),
    guidanceHubToastDealFailed: tr("guidance.page.toast.dealFailed", "Could not deal the cards. Try again."),
    guidanceHubToastQuestionVague: tr("guidance.page.toast.questionVague", "Make your question a bit more specific"),
    guidanceHubToastRevealAllFirst: tr("guidance.page.toast.revealAllFirst", "Reveal every position in the spread first"),
    guidanceHubToastNoSessionReading: tr(
      "guidance.page.toast.noSessionReading",
      "No active session to request a reading. Sign in again.",
    ),
    guidanceHubToastClarifyOneCardOnly: tr(
      "guidance.page.toast.clarifyOneCardOnly",
      "Clarification is only for the “one card” spread with one open position",
    ),
    guidanceHubToastClarifyAlready409: tr(
      "guidance.page.toast.clarifyAlready409",
      "You already used a clarification for this reading—start a new session with a spread.",
    ),
    guidanceHubToastReadingFailed: tr("guidance.page.toast.readingFailed", "Could not assemble the reading. Check your network and try again."),
    guidanceHubToastFeedbackSavedHelpful: tr("guidance.page.toast.feedbackSavedHelpful", "Feedback saved"),
    guidanceHubToastFeedbackSavedUnclear: tr("guidance.page.toast.feedbackSavedUnclear", "Noted that you need more clarity"),
    guidanceHubToastFeedbackSaveFailed: tr("guidance.page.toast.feedbackSaveFailed", "Could not save feedback"),
    guidanceHubToastNeedMainReading: tr("guidance.page.toast.needMainReading", "Get the main reading first"),
    guidanceHubToastClarifyAlreadyUsed: tr("guidance.page.toast.clarifyAlreadyUsed", "Clarification for this reading was already used"),
  };
}

/** Подписи `<optgroup>` в `GuidanceSpreadPicker` — паритет `GuidanceHubChromeCopy` (`guidanceHubCatalogSection*`). */
export function guidanceHubSpreadSectionLabelsFromBundle(gh: GuidanceHubChromeBundle): Record<GuidanceSpreadSection, string> {
  return {
    quick: gh.guidanceHubCatalogSectionQuick,
    medium: gh.guidanceHubCatalogSectionMedium,
    deep: gh.guidanceHubCatalogSectionDeep,
  };
}
