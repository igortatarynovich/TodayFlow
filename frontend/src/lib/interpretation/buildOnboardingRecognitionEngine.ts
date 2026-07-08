import { generateObservationCandidates } from "@/lib/interpretation/generateObservationCandidates";
import {
  ONBOARDING_RECOGNITION_LENS_LABELS,
  type OnboardingRecognitionHit,
  type RecognitionSelectionAudit,
} from "@/lib/interpretation/onboardingRecognitionTypes";
import { rankObservationCandidates } from "@/lib/interpretation/rankObservationCandidates";
import { resolveBirthSignals } from "@/lib/interpretation/resolveBirthSignals";
import type { GuestProfileDraft } from "@/lib/guestProfileDraft";

export type OnboardingRecognitionEngineResult = {
  hits: OnboardingRecognitionHit[];
  audit: RecognitionSelectionAudit;
};

export function buildOnboardingRecognitionEngine(
  draft: GuestProfileDraft,
  refDate: Date = new Date(),
): OnboardingRecognitionEngineResult {
  const signals = resolveBirthSignals(draft, refDate);
  const candidates = generateObservationCandidates(signals);
  const selected = rankObservationCandidates(candidates);

  const hits: OnboardingRecognitionHit[] = selected.map((candidate) => ({
    id: candidate.id,
    lens: candidate.lens,
    lensLabel: ONBOARDING_RECOGNITION_LENS_LABELS[candidate.lens],
    body: candidate.text,
    audit: {
      score: candidate.score,
      evidence: candidate.evidence,
    },
  }));

  return {
    hits,
    audit: {
      candidateCount: candidates.length,
      selectedIds: hits.map((h) => h.id),
      selections: hits.map((h) => ({
        id: h.id,
        lens: h.lens,
        score: h.audit.score,
        evidence: h.audit.evidence,
      })),
    },
  };
}

export function buildOnboardingRecognitionHits(
  draft: GuestProfileDraft,
  refDate?: Date,
): OnboardingRecognitionHit[] {
  return buildOnboardingRecognitionEngine(draft, refDate).hits;
}
