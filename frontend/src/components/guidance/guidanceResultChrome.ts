/**
 * Тексты блока результата разбора (GuidanceStructuredResult, SpreadStrip, ResultCard).
 * Зеркало `GuidanceResultChromeCopy.swift`.
 * Строки: `CONTENT/i18n/app.{ru,en}.json` (`guidance.result.*`, `guidance.strip.*`, `guidance.resultCard.*`).
 */

import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { t } from "@/lib/i18n";

export function guidanceResultInterpolate(template: string, vars: Record<string, string>): string {
  return template.replace(/\{(\w+)\}/g, (_, key: string) => vars[key] ?? `{${key}}`);
}

export interface GuidanceResultChromeBundle {
  guidanceResultReflectionFallback: string;
  guidanceResultToastPickResonance: string;
  guidanceResultToastFeedbackThanks: string;
  guidanceResultToastFeedbackSaveFailed: string;
  guidanceResultAssessmentEyebrow: string;
  guidanceResultSafetyBanner: string;
  guidanceResultShortEyebrowClarify: string;
  guidanceResultShortEyebrowMain: string;
  guidanceResultHappeningEyebrow: string;
  guidanceResultCardsEyebrow: string;
  guidanceResultPositionLine: string;
  guidanceResultOrientationReversed: string;
  guidanceResultOrientationUpright: string;
  guidanceResultMeaningLine: string;
  guidanceResultProfileBridgeEyebrow: string;
  guidanceResultCoreEyebrow: string;
  guidanceResultWhyToggleOpenPrefix: string;
  guidanceResultWhyToggleClosedPrefix: string;
  guidanceResultWhyToggleLabel: string;
  guidanceResultContinueEyebrow: string;
  guidanceResultAvoidEyebrow: string;
  guidanceResultDoEyebrow: string;
  guidanceResultReflectionEyebrow: string;
  guidanceResultNextStepEyebrow: string;
  guidanceResultCompatTitle: string;
  guidanceResultCompatLead: string;
  guidanceResultCompatCta: string;
  guidanceResultPatternTitle: string;
  guidanceResultPatternLead: string;
  guidanceResultPatternCta: string;
  guidanceResultClarifyTitle: string;
  guidanceResultClarifyLead: string;
  guidanceResultClarifyCta: string;
  guidanceResultFeedbackEyebrow: string;
  guidanceResultResonanceHigh: string;
  guidanceResultResonancePartial: string;
  guidanceResultResonanceNone: string;
  guidanceResultMatchChipsPrompt: string;
  guidanceResultMatchChipEmotions: string;
  guidanceResultMatchChipPerson: string;
  guidanceResultMatchChipSexualTension: string;
  guidanceResultMatchChipFear: string;
  guidanceResultMatchChipAdvice: string;
  guidanceResultMatchChipNothing: string;
  guidanceResultCommentLabel: string;
  guidanceResultCommentPlaceholder: string;
  guidanceResultSubmitFeedback: string;
  guidanceResultFeedbackSaved: string;
  guidanceResultLegacyQuickLabel: string;
  guidanceResultLegacyHelpfulActive: string;
  guidanceResultLegacyHelpfulInactive: string;
  guidanceResultLegacyUnclearActive: string;
  guidanceResultLegacyUnclearInactive: string;
  guidanceResultProfileIncompleteHint: string;
  guidanceStripRevealHint: string;
  guidanceStripPositionFallback: string;
  guidanceResultCardBlockCurrent: string;
  guidanceResultCardBlockManifestation: string;
  guidanceResultCardBlockCaution: string;
  guidanceResultCardBlockNextStep: string;
}

export function guidanceResultChromeBundle(locale: FlowPracticesChromeLocale): GuidanceResultChromeBundle {
  const loc = locale === "ru" ? "ru" : "en";
  const tr = (key: string, defaultEn: string) => t(key, defaultEn, undefined, loc);

  return {
    guidanceResultReflectionFallback: tr(
      "guidance.result.reflectionFallback",
      "What matters more for you right now: easing the tension quickly, or getting clarity you can test with one action?",
    ),
    guidanceResultToastPickResonance: tr("guidance.result.toast.pickResonance", "Pick how much this resonated"),
    guidanceResultToastFeedbackThanks: tr(
      "guidance.result.toast.feedbackThanks",
      "Thanks—that helps us improve future readings",
    ),
    guidanceResultToastFeedbackSaveFailed: tr("guidance.result.toast.feedbackSaveFailed", "Couldn’t save your response"),
    guidanceResultAssessmentEyebrow: tr("guidance.result.assessmentEyebrow", "Your question and the spread’s strength"),
    guidanceResultSafetyBanner: tr(
      "guidance.result.safetyBanner",
      "This reading can help you see emotions and inner conflict, but it isn’t a substitute for professional support or checking facts on the ground. If safety, money, health, or paperwork is involved—rely on real information and qualified help.",
    ),
    guidanceResultShortEyebrowClarify: tr("guidance.result.shortEyebrowClarify", "Clarifying card"),
    guidanceResultShortEyebrowMain: tr("guidance.result.shortEyebrowMain", "In short"),
    guidanceResultHappeningEyebrow: tr("guidance.result.happeningEyebrow", "What’s going on here"),
    guidanceResultCardsEyebrow: tr("guidance.result.cardsEyebrow", "Card by card"),
    guidanceResultPositionLine: tr("guidance.result.positionLine", "Position: {position}"),
    guidanceResultOrientationReversed: tr("guidance.result.orientationReversed", "reversed"),
    guidanceResultOrientationUpright: tr("guidance.result.orientationUpright", "upright"),
    guidanceResultMeaningLine: tr("guidance.result.meaningLine", "Reference meaning in this position: {meaning}"),
    guidanceResultProfileBridgeEyebrow: tr("guidance.result.profileBridgeEyebrow", "What this means for you"),
    guidanceResultCoreEyebrow: tr("guidance.result.coreEyebrow", "The main knot in the situation"),
    guidanceResultWhyToggleOpenPrefix: tr("guidance.result.whyToggleOpenPrefix", "▼"),
    guidanceResultWhyToggleClosedPrefix: tr("guidance.result.whyToggleClosedPrefix", "▶"),
    guidanceResultWhyToggleLabel: tr("guidance.result.whyToggleLabel", "Why this interpretation?"),
    guidanceResultContinueEyebrow: tr("guidance.result.continueEyebrow", "If you want to go further"),
    guidanceResultAvoidEyebrow: tr("guidance.result.avoidEyebrow", "What to avoid"),
    guidanceResultDoEyebrow: tr("guidance.result.doEyebrow", "What to do instead"),
    guidanceResultReflectionEyebrow: tr("guidance.result.reflectionEyebrow", "A question for yourself"),
    guidanceResultNextStepEyebrow: tr("guidance.result.nextStepEyebrow", "Next step"),
    guidanceResultCompatTitle: tr("guidance.result.compatTitle", "Explore your compatibility"),
    guidanceResultCompatLead: tr(
      "guidance.result.compatLead",
      "If there’s a specific person, you can go deeper on the dynamic—emotions, conflict, closeness, and perspective.",
    ),
    guidanceResultCompatCta: tr("guidance.result.compatCta", "Open Compatibility"),
    guidanceResultPatternTitle: tr("guidance.result.patternTitle", "Understand your pattern"),
    guidanceResultPatternLead: tr(
      "guidance.result.patternLead",
      "If this keeps showing up, your portrait is a good place to see the script.",
    ),
    guidanceResultPatternCta: tr("guidance.result.patternCta", "Open profile"),
    guidanceResultClarifyTitle: tr("guidance.result.clarifyTitle", "Clarifying spread"),
    guidanceResultClarifyLead: tr(
      "guidance.result.clarifyLead",
      "One card with a specific aim. The server allows at most one clarification per main reading.",
    ),
    guidanceResultClarifyCta: tr("guidance.result.clarifyCta", "Draw a clarifying card"),
    guidanceResultFeedbackEyebrow: tr("guidance.result.feedbackEyebrow", "Did this land?"),
    guidanceResultResonanceHigh: tr("guidance.result.resonanceHigh", "yes, very accurate"),
    guidanceResultResonancePartial: tr("guidance.result.resonancePartial", "partly"),
    guidanceResultResonanceNone: tr("guidance.result.resonanceNone", "no, not about me"),
    guidanceResultMatchChipsPrompt: tr("guidance.result.matchChipsPrompt", "What matched?"),
    guidanceResultMatchChipEmotions: tr("guidance.result.matchChip.emotions", "emotions"),
    guidanceResultMatchChipPerson: tr("guidance.result.matchChip.person", "the person"),
    guidanceResultMatchChipSexualTension: tr("guidance.result.matchChip.sexualTension", "sexual tension"),
    guidanceResultMatchChipFear: tr("guidance.result.matchChip.fear", "fear"),
    guidanceResultMatchChipAdvice: tr("guidance.result.matchChip.advice", "the advice"),
    guidanceResultMatchChipNothing: tr("guidance.result.matchChip.nothing", "none of these"),
    guidanceResultCommentLabel: tr("guidance.result.commentLabel", "What should we remember for your next readings?"),
    guidanceResultCommentPlaceholder: tr("guidance.result.commentPlaceholder", "In your own words, briefly…"),
    guidanceResultSubmitFeedback: tr("guidance.result.submitFeedback", "Send feedback"),
    guidanceResultFeedbackSaved: tr("guidance.result.feedbackSaved", "Saved"),
    guidanceResultLegacyQuickLabel: tr("guidance.result.legacyQuickLabel", "Quick mark"),
    guidanceResultLegacyHelpfulActive: tr("guidance.result.legacyHelpfulActive", "Helpful"),
    guidanceResultLegacyHelpfulInactive: tr("guidance.result.legacyHelpfulInactive", "It clarified things"),
    guidanceResultLegacyUnclearActive: tr("guidance.result.legacyUnclearActive", "Noted"),
    guidanceResultLegacyUnclearInactive: tr("guidance.result.legacyUnclearInactive", "Still unclear"),
    guidanceResultProfileIncompleteHint: tr(
      "guidance.result.profileIncompleteHint",
      "This answer was assembled without a full profile—fill in your portrait for more precise readings.",
    ),
    guidanceStripRevealHint: tr("guidance.strip.revealHint", "Tap to reveal"),
    guidanceStripPositionFallback: tr("guidance.strip.positionFallback", "Card"),
    guidanceResultCardBlockCurrent: tr("guidance.resultCard.blockCurrent", "The heart of it now"),
    guidanceResultCardBlockManifestation: tr("guidance.resultCard.blockManifestation", "How it shows up"),
    guidanceResultCardBlockCaution: tr("guidance.resultCard.blockCaution", "Risk"),
    guidanceResultCardBlockNextStep: tr("guidance.resultCard.blockNextStep", "Next step"),
  };
}

/** Убирает хвост «Расклад (…)» / «Spread (…)» из текста пояснения, если модель его добавила. */
export function stripTarotAppendFromExplanation(explanation: string): string {
  const needles = ["\nРасклад (", " Расклад (", "\nSpread (", " Spread ("];
  let best = -1;
  for (const n of needles) {
    const i = explanation.lastIndexOf(n);
    if (i > best) best = i;
  }
  if (best === -1) return explanation;
  return explanation.slice(0, best).trim();
}

export function guidanceResultMatchChipIds(gr: GuidanceResultChromeBundle): string[] {
  return [
    gr.guidanceResultMatchChipEmotions,
    gr.guidanceResultMatchChipPerson,
    gr.guidanceResultMatchChipSexualTension,
    gr.guidanceResultMatchChipFear,
    gr.guidanceResultMatchChipAdvice,
    gr.guidanceResultMatchChipNothing,
  ];
}

/** Эвристика «вопрос про любовь/партнёра» для карточки совместимости — паритет `GuidanceResultChromeCopy.guidanceResultLoveQuestionHeuristic`. */
export function guidanceResultLoveQuestionHeuristic(locale: FlowPracticesChromeLocale, question: string): boolean {
  return locale === "ru"
    ? /любов|партн|близост|чувств|он |она /i.test(question)
    : /love|partner|relationship|feel|closeness|crush|dating|them |him |her |they /i.test(question);
}

/** Показывать ли блок «совместимость» при теме relationships — паритет `GuidanceResultChromeCopy.guidanceResultShowCompatHint`. */
export function guidanceResultShowCompatHint(
  locale: FlowPracticesChromeLocale,
  topicId: string | null,
  lane: string,
  question: string,
): boolean {
  if (topicId !== "relationships") return false;
  if (lane === "love") return true;
  return guidanceResultLoveQuestionHeuristic(locale, question);
}
