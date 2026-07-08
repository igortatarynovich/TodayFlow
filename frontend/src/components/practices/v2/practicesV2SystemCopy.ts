export type PracticesV2Locale = "ru" | "en";

export type PracticesV2Copy = {
  pageEyebrow: string;
  pageTitle: string;
  searchPlaceholder: string;
  heroEyebrow: string;
  heroTitle: string;
  heroBodyFallback: string;
  heroPrimaryCta: string;
  heroSecondaryCta: string;
  practiceOfDayEyebrow: string;
  practiceOfDayMinutes: string;
  practiceOfDaySteps: string;
  libraryTitle: string;
  viewHistory: string;
  quickEntryTitle: string;
  allPrograms: string;
  openCta: string;
  progressTitle: string;
  weeklyRhythm: string;
  streakDaysLabel: string;
  totalCompletedLabel: string;
  longestStreakLabel: string;
  weeksActiveLabel: string;
  limitsRemainingLabel: string;
  personalizedCompletedLabel: string;
  byCategoryTitle: string;
  tabAll: string;
  minutesShort: string;
  guestProgressHint: string;
};

export const PRACTICES_V2_COPY: Record<PracticesV2Locale, PracticesV2Copy> = {
  ru: {
    pageEyebrow: "ПРАКТИКИ · ВЕБ",
    pageTitle: "Центр ежедневных ритуалов",
    searchPlaceholder: "Найти практику, технику или вопрос",
    heroEyebrow: "СЕГОДНЯ",
    heroTitle: "Практики для ясного дня",
    heroBodyFallback:
      "Подборка из каталога TodayFlow: персональная практика дня, фильтры по категориям и прогресс по завершениям.",
    heroPrimaryCta: "Начать практику",
    heroSecondaryCta: "Смотреть все практики",
    practiceOfDayEyebrow: "ПРАКТИКА ДНЯ",
    practiceOfDayMinutes: "МИНУТ",
    practiceOfDaySteps: "ШАГА",
    libraryTitle: "Библиотека практик",
    viewHistory: "История и статистика",
    quickEntryTitle: "Быстрый вход",
    allPrograms: "Все программы",
    openCta: "Открыть",
    progressTitle: "Прогресс",
    weeklyRhythm: "Недельный ритм",
    streakDaysLabel: "ДНЕЙ СЕРИИ",
    totalCompletedLabel: "Завершено",
    longestStreakLabel: "Лучшая серия",
    weeksActiveLabel: "Недель с практикой",
    limitsRemainingLabel: "Персональных на неделе",
    personalizedCompletedLabel: "Персональных",
    byCategoryTitle: "По категориям",
    tabAll: "Все",
    minutesShort: "мин",
    guestProgressHint: "Войди, чтобы видеть серию и историю завершений.",
  },
  en: {
    pageEyebrow: "PRACTICES · WEB",
    pageTitle: "Daily rituals hub",
    searchPlaceholder: "Find a practice, technique, or question",
    heroEyebrow: "TODAY",
    heroTitle: "Practices for a clear day",
    heroBodyFallback:
      "TodayFlow catalog: practice of the day, category filters, and completion progress from your account.",
    heroPrimaryCta: "Start practice",
    heroSecondaryCta: "Browse all practices",
    practiceOfDayEyebrow: "PRACTICE OF THE DAY",
    practiceOfDayMinutes: "MINUTES",
    practiceOfDaySteps: "STEPS",
    libraryTitle: "Practice library",
    viewHistory: "History and stats",
    quickEntryTitle: "Quick entry",
    allPrograms: "All programs",
    openCta: "Open",
    progressTitle: "Progress",
    weeklyRhythm: "Weekly rhythm",
    streakDaysLabel: "DAY STREAK",
    totalCompletedLabel: "Completed",
    longestStreakLabel: "Best streak",
    weeksActiveLabel: "Active weeks",
    limitsRemainingLabel: "Personalized left this week",
    personalizedCompletedLabel: "Personalized",
    byCategoryTitle: "By category",
    tabAll: "All",
    minutesShort: "min",
    guestProgressHint: "Sign in to see streak and completion history.",
  },
};

export function practicesV2Copy(locale: PracticesV2Locale): PracticesV2Copy {
  return PRACTICES_V2_COPY[locale];
}
