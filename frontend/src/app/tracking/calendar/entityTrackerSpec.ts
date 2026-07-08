/** Типы и числовые лимиты трекера сущностей. Копирайт — `flowPracticesMainTabChrome.ts` / `FlowTrackerChromeCopy`. */

export type ScreenHeroKind = "empty" | "in_flow" | "unstable" | "dropped" | "overloaded";

export type GoalCategoryTone = "empty" | "mixed" | "strong" | "weak" | "overloaded";

export type HabitCategoryTone = "empty" | "strong" | "mixed" | "weak";

export type AsceticCategoryTone = "empty" | "strong" | "mixed" | "weak";

export type PracticeCategoryTone = "empty" | "active" | "ignored" | "neutral";

export const FREE_LIMITS = { goals: 1, habits: 2, ascetics: 1 } as const;
export const PRO_LIMITS = { goals: 3, habits: 5, ascetics: 2 } as const;
