import type { GuestProfileDraft } from "@/lib/guestProfileDraft";
import { buildFirstResultModel, type FirstResultModel } from "@/lib/buildFirstResultModel";

export type { FirstResultModel } from "@/lib/buildFirstResultModel";
export type { OnboardingRecognitionHit } from "@/lib/interpretation/onboardingRecognitionTypes";
export type { RecognitionSelectionAudit } from "@/lib/interpretation/onboardingRecognitionTypes";

/** @deprecated Use FirstResultModel */
export type OnboardingPreviewModel = FirstResultModel;

export function buildOnboardingPreviewModel(draft: GuestProfileDraft): FirstResultModel {
  return buildFirstResultModel(draft);
}
