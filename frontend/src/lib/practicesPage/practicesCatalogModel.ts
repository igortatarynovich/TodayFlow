import type { PracticeHistoryItem, PracticeProgressResponse } from "@/lib/types";

/** Matches backend PracticeResponse (practices.py). */
export type PracticeCatalogItem = {
  id: string;
  title: string;
  description: string;
  category: string;
  practice_type?: string;
  duration_minutes?: number;
  difficulty: string;
  is_free: boolean;
  is_personalized: boolean;
  personalized_reason?: string;
  access_level: string;
  tags: string[];
  target_axis?: string;
  sequence_id?: string;
  step_number?: number;
  total_steps?: number;
  cycle_type?: string;
};

export type PracticeCategoryOption = {
  id: string;
  name: string;
  icon?: string;
};

export type PracticeLimitsSnapshot = {
  subscription_level: string;
  personalized_limit: number;
  used_this_week: number;
  remaining_this_week: number;
};

/** Backend GET /practices/categories/list ids → query param `category`. */
export const PRACTICE_BACKEND_CATEGORY_IDS = new Set([
  "meditation",
  "breathing",
  "gratitude",
  "affirmation",
  "ritual",
  "reflection",
  "emotional",
  "focus",
]);

export function practiceStepsCount(practice: PracticeCatalogItem): number | null {
  if (practice.total_steps != null && practice.total_steps > 0) return practice.total_steps;
  if (practice.step_number != null && practice.sequence_id) return practice.step_number;
  return null;
}

export function practiceIconGlyph(practice: PracticeCatalogItem): string {
  const haystack = `${practice.category} ${practice.tags.join(" ")}`.toLowerCase();
  if (haystack.includes("breath") || haystack.includes("дых")) return "✦";
  if (haystack.includes("medit") || haystack.includes("медит")) return "◐";
  if (haystack.includes("affirm") || haystack.includes("афф")) return "◇";
  if (haystack.includes("tarot") || haystack.includes("таро")) return "▯";
  if (haystack.includes("question") || haystack.includes("вопрос")) return "✧";
  return "☾";
}

export function practiceTagLabel(
  practice: PracticeCatalogItem,
  locale: "ru" | "en",
): string | undefined {
  if (practice.is_personalized) return locale === "ru" ? "Для тебя" : "For you";
  const haystack = `${practice.category} ${practice.tags.join(" ")}`.toLowerCase();
  if (haystack.includes("focus") || haystack.includes("фокус")) return locale === "ru" ? "Фокус" : "Focus";
  if (practice.target_axis) return practice.target_axis;
  return undefined;
}

export function matchesPracticeSearch(practice: PracticeCatalogItem, query: string): boolean {
  const q = query.trim().toLowerCase();
  if (!q) return true;
  const haystack = `${practice.title} ${practice.description} ${practice.category} ${practice.tags.join(" ")}`.toLowerCase();
  return haystack.includes(q);
}

export type PracticesProgressSummary = {
  totalCompleted: number;
  personalizedCompleted: number;
  longestStreakDays: number;
  weeksActive: number;
  byCategory: PracticesCategoryProgressRow[];
};

export type PracticesCategoryProgressRow = {
  categoryId: string;
  label: string;
  totalCompleted: number;
  personalizedCompleted: number;
  sharePercent: number;
};

export function categoryLabelFromOptions(
  categoryId: string,
  categories: PracticeCategoryOption[],
  locale: "ru" | "en",
): string {
  const match = categories.find((item) => item.id === categoryId);
  if (match) return match.name;
  return categoryId;
}

export function programCardsFromCatalog(
  practices: PracticeCatalogItem[],
  options: {
    locale: "ru" | "en";
    minutesShort: string;
    max?: number;
    preferSequences?: boolean;
  },
): Array<{
  id: string;
  href: string;
  title: string;
  description: string;
  durationLabel: string;
  tagLabel?: string;
  iconGlyph: string;
  featured?: boolean;
}> {
  const max = options.max ?? 3;
  const pool = options.preferSequences
    ? practices.filter((practice) => practice.practice_type === "guided_sequence")
    : practices;

  return pool.slice(0, max).map((practice, index) => ({
    id: practice.id,
    href: `/practices/${practice.id}`,
    title: practice.title,
    description: practice.description,
    durationLabel: sequenceDurationLabel(practice, options.locale, options.minutesShort),
    tagLabel: sequenceTagLabel(practice, options.locale) ?? practiceTagLabel(practice, options.locale),
    iconGlyph: practiceIconGlyph(practice),
    featured: index === 0,
  }));
}

export function quickItemsFromCatalog(
  practices: PracticeCatalogItem[],
  options: {
    locale: "ru" | "en";
    minutesShort: string;
    max?: number;
    excludeIds?: Set<string>;
  },
): Array<{
  id: string;
  href: string;
  title: string;
  subtitle: string;
  durationLabel: string;
  iconGlyph: string;
}> {
  const max = options.max ?? 3;
  const exclude = options.excludeIds ?? new Set<string>();

  return practices
    .filter((practice) => !exclude.has(practice.id))
    .slice(0, max)
    .map((practice) => ({
      id: practice.id,
      href: `/practices/${practice.id}`,
      title: practice.title,
      subtitle: practice.personalized_reason?.trim() || practice.category,
      durationLabel: formatPracticeDuration(practice.duration_minutes, options.minutesShort),
      iconGlyph: practiceIconGlyph(practice),
    }));
}

function formatPracticeDuration(minutes: number | undefined, minutesShort: string): string {
  if (minutes == null) return "—";
  return `${minutes} ${minutesShort}`;
}

function sequenceDurationLabel(
  practice: PracticeCatalogItem,
  locale: "ru" | "en",
  minutesShort: string,
): string {
  if (practice.practice_type === "guided_sequence" && practice.total_steps) {
    return locale === "ru" ? `${practice.total_steps} шага` : `${practice.total_steps} steps`;
  }
  return formatPracticeDuration(practice.duration_minutes, minutesShort);
}

function sequenceTagLabel(practice: PracticeCatalogItem, locale: "ru" | "en"): string | undefined {
  if (practice.practice_type !== "guided_sequence") return undefined;
  return locale === "ru" ? "Серия" : "Series";
}

export function progressSummaryFromApi(
  progress: PracticeProgressResponse | null | undefined,
  categories: PracticeCategoryOption[] = [],
  locale: "ru" | "en" = "ru",
): PracticesProgressSummary | null {
  if (!progress) return null;
  const total = Math.max(progress.total_completed, 1);
  return {
    totalCompleted: progress.total_completed,
    personalizedCompleted: progress.personalized_completed,
    longestStreakDays: progress.longest_streak_days,
    weeksActive: progress.weeks_active,
    byCategory: (progress.by_category ?? []).map((row) => ({
      categoryId: row.category,
      label: categoryLabelFromOptions(row.category, categories, locale),
      totalCompleted: row.total_completed,
      personalizedCompleted: row.personalized_completed,
      sharePercent: Math.round((row.total_completed / total) * 100),
    })),
  };
}

export function historyCompletionDates(history: PracticeHistoryItem[]): Set<string> {
  return new Set(history.map((item) => item.completed_at.slice(0, 10)));
}
