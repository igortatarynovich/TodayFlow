import type { OnboardingRecognitionLens } from "@/lib/interpretation/onboardingRecognitionTypes";

export type PortraitDimensionId =
  | "decisions"
  | "energy_drain"
  | "strength_zone"
  | "balance"
  | "growth"
  | "social_perception";

export type PortraitCardType = "observation" | "question" | "recommendation" | "fact" | "paradox";

export type PortraitDimensionSpec = {
  id: PortraitDimensionId;
  icon: string;
  title: string;
  cardType: PortraitCardType;
  preferredLens?: OnboardingRecognitionLens;
  preferredReferenceKeys?: string[];
  /** Avoid candidates whose dominant theme already used */
  themeFocus: string;
};

export const PORTRAIT_DIMENSIONS: PortraitDimensionSpec[] = [
  {
    id: "decisions",
    icon: "🧠",
    title: "Как ты чаще принимаешь решения",
    cardType: "observation",
    preferredLens: "strengthens",
    preferredReferenceKeys: ["sign.decisions", "life_path.driver"],
    themeFocus: "thinking",
  },
  {
    id: "energy_drain",
    icon: "⚡",
    title: "Что быстрее всего забирает энергию",
    cardType: "recommendation",
    preferredLens: "tension",
    preferredReferenceKeys: ["sign.dislikes", "life_path.minus_side", "sign.hurts", "metadata.modality"],
    themeFocus: "energy",
  },
  {
    id: "strength_zone",
    icon: "🎯",
    title: "Где ты раскрываешься сильнее всего",
    cardType: "observation",
    preferredLens: "strengthens",
    preferredReferenceKeys: ["sign.work", "life_path.money_work", "metadata.season"],
    themeFocus: "environment",
  },
  {
    id: "balance",
    icon: "❤️",
    title: "Что помогает сохранять равновесие",
    cardType: "fact",
    preferredLens: "recovery",
    preferredReferenceKeys: ["sign.support", "life_path.lesson", "metadata.chinese"],
    themeFocus: "balance",
  },
  {
    id: "growth",
    icon: "🌱",
    title: "Что помогает тебе развиваться",
    cardType: "recommendation",
    preferredLens: "recovery",
    preferredReferenceKeys: ["life_path.growth", "sign.growth"],
    themeFocus: "growth",
  },
  {
    id: "social_perception",
    icon: "🔍",
    title: "Что люди замечают в тебе раньше всего",
    cardType: "question",
    preferredLens: "noticed_by_others",
    preferredReferenceKeys: ["sun.bullets", "sign.communication", "metadata.weekday"],
    themeFocus: "social",
  },
];

export const PORTRAIT_VISIBLE_COUNT = 4;
export const PORTRAIT_POOL_TARGET = 8;
