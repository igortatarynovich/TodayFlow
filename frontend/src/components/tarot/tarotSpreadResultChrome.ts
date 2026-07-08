/**
 * Тексты страницы `/tarot/result` (расклад после draw).
 * Зеркало `TarotSpreadResultChromeCopy.swift`.
 * Ключи: `CONTENT/i18n/app.{ru,en}.json` — `tarot.spreadResult.*`.
 */

import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { t } from "@/lib/i18n";

const POSITION_IDS = ["past", "present", "future", "answer", "situation", "action", "outcome"] as const;

export type TarotSpreadResultPosition = string | { id: string; title: string; prompt?: string };

export interface TarotSpreadResultChromeBundle {
  tarotSpreadResultErrorLoadFailed: string;
  tarotSpreadResultErrorNotFound: string;
  tarotSpreadResultBackToTarot: string;
  tarotSpreadResultShareTitle: string;
  tarotSpreadResultShareText: string;
  tarotSpreadResultToastLinkCopied: string;
  tarotSpreadResultToastFavoriteAdded: string;
  tarotSpreadResultToastFavoriteRemoved: string;
  tarotSpreadResultToastFavoriteFailed: string;
  tarotSpreadResultFavoriteSaving: string;
  tarotSpreadResultFavoriteAdd: string;
  tarotSpreadResultFavoriteRemove: string;
  tarotSpreadResultDefaultSpreadTitle: string;
  tarotSpreadResultQuestionPrefix: string;
  tarotSpreadResultProfileFallbackFocus: string;
  tarotSpreadResultKeyMeaningFallback: string;
  tarotSpreadResultManifestationOneCard: string;
  tarotSpreadResultManifestationThreeCards: string;
  tarotSpreadResultCautionDefault: string;
  tarotSpreadResultNextStepOneCard: string;
  tarotSpreadResultNextStepThreeCards: string;
  tarotSpreadResultNextStepLabelCardOfDay: string;
  tarotSpreadResultNextStepLabelToday: string;
  tarotSpreadResultReturnSpreadOneCard: string;
  tarotSpreadResultReturnSpreadThreeCards: string;
  tarotSpreadResultSectionProfile: string;
  tarotSpreadResultSectionNext: string;
  tarotSpreadResultJournal: string;
  tarotSpreadResultThreeCardsCta: string;
  tarotSpreadResultShare: string;
  tarotSpreadResultPositionDetailsSummary: string;
  tarotSpreadResultPositionSingleCard: string;
  tarotSpreadResultModeLabel: string;
  tarotSpreadResultProfileHintWithProfile: string;
  tarotSpreadResultOrientationSubtitleUpright: string;
  tarotSpreadResultOrientationSubtitleReversed: string;
  positionLabels: Record<string, string>;
}

export function tarotSpreadResultChromeBundle(locale: FlowPracticesChromeLocale): TarotSpreadResultChromeBundle {
  const loc = locale === "ru" ? "ru" : "en";
  const tr = (key: string, defaultEn: string) => t(key, defaultEn, undefined, loc);

  const positionDefaultsEn: Record<(typeof POSITION_IDS)[number], string> = {
    past: "Past",
    present: "Present",
    future: "Future",
    answer: "Answer",
    situation: "Situation",
    action: "Action",
    outcome: "Outcome",
  };

  const positionLabels = Object.fromEntries(
    POSITION_IDS.map((id) => [id, tr(`tarot.spreadResult.position.${id}`, positionDefaultsEn[id])])
  ) as Record<string, string>;

  return {
    tarotSpreadResultErrorLoadFailed: tr(
      "tarot.spreadResult.error.loadFailed",
      "Couldn’t load the spread result",
    ),
    tarotSpreadResultErrorNotFound: tr("tarot.spreadResult.error.notFound", "Result not found"),
    tarotSpreadResultBackToTarot: tr("tarot.spreadResult.backToTarot", "Back to Tarot"),
    tarotSpreadResultShareTitle: tr("tarot.spreadResult.shareTitle", "Tarot"),
    tarotSpreadResultShareText: tr("tarot.spreadResult.shareText", "Spread result"),
    tarotSpreadResultToastLinkCopied: tr("tarot.spreadResult.toast.linkCopied", "Link copied"),
    tarotSpreadResultToastFavoriteAdded: tr("tarot.spreadResult.toast.favoriteAdded", "Saved to favorites"),
    tarotSpreadResultToastFavoriteRemoved: tr("tarot.spreadResult.toast.favoriteRemoved", "Removed from favorites"),
    tarotSpreadResultToastFavoriteFailed: tr("tarot.spreadResult.toast.favoriteFailed", "Couldn’t update favorites"),
    tarotSpreadResultFavoriteSaving: tr("tarot.spreadResult.favorite.saving", "Saving…"),
    tarotSpreadResultFavoriteAdd: tr("tarot.spreadResult.favorite.add", "Add to favorites"),
    tarotSpreadResultFavoriteRemove: tr("tarot.spreadResult.favorite.remove", "Remove from favorites"),
    tarotSpreadResultDefaultSpreadTitle: tr("tarot.spreadResult.defaultSpreadTitle", "Spread"),
    tarotSpreadResultQuestionPrefix: tr("tarot.spreadResult.questionPrefix", "Question:"),
    tarotSpreadResultProfileFallbackFocus: tr(
      "tarot.spreadResult.profileFallbackFocus",
      "Focus on the next small step, not a “forever answer.”",
    ),
    tarotSpreadResultKeyMeaningFallback: tr(
      "tarot.spreadResult.keyMeaningFallback",
      "The main meaning is in the sections below.",
    ),
    tarotSpreadResultManifestationOneCard: tr(
      "tarot.spreadResult.manifestation.oneCard",
      "One step, one conversation, or one decision—without endless postponing.",
    ),
    tarotSpreadResultManifestationThreeCards: tr(
      "tarot.spreadResult.manifestation.threeCards",
      "A line: past · now · how you move next.",
    ),
    tarotSpreadResultCautionDefault: tr(
      "tarot.spreadResult.cautionDefault",
      "Don’t turn the spread into a verdict—look for one precise step.",
    ),
    tarotSpreadResultNextStepOneCard: tr(
      "tarot.spreadResult.nextStep.oneCard",
      "Check the card of the day for the tone.",
    ),
    tarotSpreadResultNextStepThreeCards: tr(
      "tarot.spreadResult.nextStep.threeCards",
      "See in Today how the line fits your day.",
    ),
    tarotSpreadResultNextStepLabelCardOfDay: tr("tarot.spreadResult.nextStepLabel.cardOfDay", "Card of the day"),
    tarotSpreadResultNextStepLabelToday: tr("tarot.spreadResult.nextStepLabel.today", "My Today"),
    tarotSpreadResultReturnSpreadOneCard: tr("tarot.spreadResult.returnSpread.oneCard", "Another single card"),
    tarotSpreadResultReturnSpreadThreeCards: tr("tarot.spreadResult.returnSpread.threeCards", "Three cards again"),
    tarotSpreadResultSectionProfile: tr("tarot.spreadResult.section.profile", "Profile"),
    tarotSpreadResultSectionNext: tr("tarot.spreadResult.section.next", "Next"),
    tarotSpreadResultJournal: tr("tarot.spreadResult.journal", "Journal"),
    tarotSpreadResultThreeCardsCta: tr("tarot.spreadResult.threeCardsCta", "Three cards"),
    tarotSpreadResultShare: tr("tarot.spreadResult.share", "Share"),
    tarotSpreadResultPositionDetailsSummary: tr("tarot.spreadResult.positionDetailsSummary", "More by positions"),
    tarotSpreadResultPositionSingleCard: tr("tarot.spreadResult.positionSingleCard", "Card"),
    tarotSpreadResultModeLabel: tr("tarot.spreadResult.modeLabel", loc === "ru" ? "Таро" : "Tarot"),
    tarotSpreadResultProfileHintWithProfile: tr("tarot.spreadResult.profileHintWithProfile", "With profile in mind"),
    tarotSpreadResultOrientationSubtitleUpright: tr(
      "tarot.spreadResult.orientationSubtitle.upright",
      "Upright",
    ),
    tarotSpreadResultOrientationSubtitleReversed: tr(
      "tarot.spreadResult.orientationSubtitle.reversed",
      "Reversed",
    ),
    positionLabels,
  };
}

export function tarotSpreadResultResolvePositionLabel(
  position: TarotSpreadResultPosition,
  bundle: TarotSpreadResultChromeBundle,
): string {
  const id = typeof position === "string" ? position : position.id;
  const mapped = bundle.positionLabels[id];
  if (mapped) return mapped;
  if (typeof position !== "string" && position.title?.trim()) return position.title;
  return id;
}
