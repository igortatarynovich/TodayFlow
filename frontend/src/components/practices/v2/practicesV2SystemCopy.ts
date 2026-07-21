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
  practiceOfDayEyebrowPersonalized: string;
  practiceOfDayEyebrowContinue: string;
  practiceOfDayEyebrowFallback: string;
  practiceOfDayMinutes: string;
  practiceOfDaySteps: string;
  firstPracticeProgressHint: string;
  catalogLoadFailed: string;
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
    practiceOfDayEyebrowPersonalized: "ТВОЯ ПРАКТИКА ДНЯ",
    practiceOfDayEyebrowContinue: "ПРОДОЛЖИТЬ ПРАКТИКУ",
    practiceOfDayEyebrowFallback: "С ЧЕГО НАЧАТЬ",
    practiceOfDayMinutes: "МИНУТ",
    practiceOfDaySteps: "ШАГА",
    firstPracticeProgressHint: "Заверши первую практику — здесь появится твой недельный ритм.",
    catalogLoadFailed: "Не удалось загрузить каталог. Повтори попытку.",
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
    practiceOfDayEyebrowPersonalized: "YOUR PRACTICE TODAY",
    practiceOfDayEyebrowContinue: "CONTINUE PRACTICE",
    practiceOfDayEyebrowFallback: "WHERE TO START",
    practiceOfDayMinutes: "MINUTES",
    practiceOfDaySteps: "STEPS",
    firstPracticeProgressHint: "Complete your first practice — your weekly rhythm will appear here.",
    catalogLoadFailed: "Could not load the catalog. Please try again.",
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
    tabAll: "All",
    minutesShort: "min",
    limitsRemainingLabel: "Personalized left this week",
    personalizedCompletedLabel: "Personalized",
    byCategoryTitle: "By category",
    guestProgressHint: "Sign in to see streak and completion history.",
  },
};

export function practicesV2Copy(locale: PracticesV2Locale): PracticesV2Copy {
  return PRACTICES_V2_COPY[locale];
}
