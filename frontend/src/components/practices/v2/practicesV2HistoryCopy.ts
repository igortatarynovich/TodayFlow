import type { PracticesV2Locale } from "@/components/practices/v2/practicesV2SystemCopy";

export type PracticesV2HistoryCopy = {
  pageTitle: string;
  pageSubtitle: string;
  backLink: string;
  statsTitle: string;
  currentStreakLabel: string;
  streakDaysSuffix: string;
  historyTitle: string;
  historyCountSuffix: string;
  personalizedBadge: string;
  seriesStepLabel: string;
  repeatCta: string;
  emptyTitle: string;
  emptyBody: string;
  browseCta: string;
  authRequired: string;
};

const COPY: Record<PracticesV2Locale, PracticesV2HistoryCopy> = {
  ru: {
    pageTitle: "История и статистика",
    pageSubtitle: "Завершённые практики и прогресс по категориям",
    backLink: "← К практикам",
    statsTitle: "Статистика",
    currentStreakLabel: "Текущая серия",
    streakDaysSuffix: "дн.",
    historyTitle: "История",
    historyCountSuffix: "записей",
    personalizedBadge: "Персональная",
    seriesStepLabel: "Шаг",
    repeatCta: "Повторить",
    emptyTitle: "Пока нет завершённых практик",
    emptyBody: "Начни с практики дня — она появится здесь после завершения.",
    browseCta: "К каталогу",
    authRequired: "Войди, чтобы видеть историю практик.",
  },
  en: {
    pageTitle: "History and stats",
    pageSubtitle: "Completed practices and category progress",
    backLink: "← Back to practices",
    statsTitle: "Statistics",
    currentStreakLabel: "Current streak",
    streakDaysSuffix: "days",
    historyTitle: "History",
    historyCountSuffix: "entries",
    personalizedBadge: "Personalized",
    seriesStepLabel: "Step",
    repeatCta: "Repeat",
    emptyTitle: "No completed practices yet",
    emptyBody: "Start with today's practice—it will show up here after completion.",
    browseCta: "Browse catalog",
    authRequired: "Sign in to view practice history.",
  },
};

export function practicesV2HistoryCopy(locale: PracticesV2Locale): PracticesV2HistoryCopy {
  return COPY[locale];
}
