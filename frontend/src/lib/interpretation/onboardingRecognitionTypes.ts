/** Onboarding preview · interpretation engine types (ILR-aligned, no LLM). */

export type OnboardingRecognitionLens =
  | "strengthens"
  | "tension"
  | "noticed_by_others"
  | "recovery"
  | "today_focus";

export type ObservationSource =
  | "natal.sun"
  | "natal.sign"
  | "natal.modality"
  | "numerology.life_path"
  | "numerology.personal_year"
  | "calendar.personal_day"
  | "calendar.birth_season"
  | "calendar.birth_weekday"
  | "culture.chinese_zodiac";

export type ObservationEvidence = {
  source: ObservationSource;
  referenceKey: string;
  weight: number;
  contribution: number;
};

export type ObservationCandidate = {
  id: string;
  lens: OnboardingRecognitionLens;
  text: string;
  evidence: ObservationEvidence[];
  score: number;
};

export type RecognitionSelectionAudit = {
  candidateCount: number;
  selectedIds: string[];
  selections: Array<{
    id: string;
    lens: OnboardingRecognitionLens;
    score: number;
    evidence: ObservationEvidence[];
  }>;
};

export type OnboardingRecognitionHit = {
  id: string;
  lens: OnboardingRecognitionLens;
  lensLabel: string;
  body: string;
  /** Internal proof — not shown in UI v1 */
  audit: {
    score: number;
    evidence: ObservationEvidence[];
  };
};

export const ONBOARDING_RECOGNITION_LENS_LABELS: Record<OnboardingRecognitionLens, string> = {
  strengthens: "Что тебя усиливает",
  tension: "Где чаще всего возникает напряжение",
  noticed_by_others: "Что люди обычно замечают в тебе",
  recovery: "Что помогает быстрее восстанавливаться",
  today_focus: "На что стоит обратить внимание уже сегодня",
};

export const SOURCE_WEIGHT: Record<ObservationSource, number> = {
  "natal.sun": 0.35,
  "natal.sign": 0.28,
  "natal.modality": 0.18,
  "numerology.life_path": 0.25,
  "numerology.personal_year": 0.15,
  "calendar.personal_day": 0.12,
  "calendar.birth_season": 0.14,
  "calendar.birth_weekday": 0.12,
  "culture.chinese_zodiac": 0.16,
};

/** Gate: no card without explainable evidence above this total */
export const MIN_RECOGNITION_SCORE = 0.28;

export const TARGET_RECOGNITION_COUNT = 5;

export const LENS_SELECTION_ORDER: OnboardingRecognitionLens[] = [
  "strengthens",
  "tension",
  "noticed_by_others",
  "recovery",
  "today_focus",
];
