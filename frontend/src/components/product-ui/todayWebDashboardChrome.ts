import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { t } from "@/lib/i18n";
import type { TodayWebPractice, TodayWebTimelineEvent } from "@/components/product-ui/TodayWebDashboard";

export type TodayWebDashboardChrome = {
  greetingMorning: string;
  greetingAfternoon: string;
  greetingEvening: string;
  railStreakTitle: string;
  railStreakDays: string;
  railWeeklyTitle: string;
  railTimelineTitle: string;
  themeEyebrow: string;
  insightsAria: string;
  insightCardLabel: string;
  insightMoonLabel: string;
  insightMoonFallback: string;
  insightNumerologyLabel: string;
  insightNumerologyTitle: string;
  practicesTitle: string;
  practicesLead: string;
  minutesShort: string;
  weekdayLabels: readonly string[];
  fallbackPractices: TodayWebPractice[];
  fallbackTimeline: TodayWebTimelineEvent[];
};

export function todayWebDashboardChromeBundle(locale: FlowPracticesChromeLocale): TodayWebDashboardChrome {
  const loc = locale === "ru" ? "ru" : "en";
  const tr = (key: string, defaultRu: string, defaultEn?: string) =>
    t(key, loc === "ru" ? defaultRu : (defaultEn ?? defaultRu), undefined, loc);
  const min = tr("today.web.minutesShort", "мин", "min");

  const fallbackPractices: TodayWebPractice[] =
    loc === "ru"
      ? [
          { id: "breath", title: "Дыхание 4-4-4", durationLabel: `5 ${min}` },
          { id: "affirm", title: "Солнечное намерение", durationLabel: `3 ${min}` },
          { id: "journal", title: "Утренний дневник", durationLabel: `7 ${min}` },
          { id: "focus", title: "Фокус 20 минут", durationLabel: `20 ${min}` },
        ]
      : [
          { id: "breath", title: "4-4-4 breathing", durationLabel: `5 ${min}` },
          { id: "affirm", title: "Solar intention", durationLabel: `3 ${min}` },
          { id: "journal", title: "Morning journal", durationLabel: `7 ${min}` },
          { id: "focus", title: "20-minute focus", durationLabel: `20 ${min}` },
        ];

  const fallbackTimeline: TodayWebTimelineEvent[] =
    loc === "ru"
      ? [
          { time: "07:00", title: "Пробуждение", active: true },
          { time: "09:30", title: "Утренняя сонастройка" },
          { time: "13:00", title: "Пик ясности" },
          { time: "21:00", title: "Вечерняя рефлексия" },
        ]
      : [
          { time: "07:00", title: "Wake up", active: true },
          { time: "09:30", title: "Morning alignment" },
          { time: "13:00", title: "Peak clarity" },
          { time: "21:00", title: "Evening reflection" },
        ];

  return {
    greetingMorning: tr("today.web.greeting.morning", "Доброе утро", "Good morning"),
    greetingAfternoon: tr("today.web.greeting.afternoon", "Добрый день", "Good afternoon"),
    greetingEvening: tr("today.web.greeting.evening", "Добрый вечер", "Good evening"),
    railStreakTitle: tr("today.web.rail.streak", "Ударный режим", "Streak mode"),
    railStreakDays: tr("today.web.rail.streakDays", "дней", "days"),
    railWeeklyTitle: tr("today.web.rail.weekly", "Ритм недели", "Weekly rhythm"),
    railTimelineTitle: tr("today.web.rail.timeline", "Таймлайн дня", "Day timeline"),
    themeEyebrow: tr("today.web.themeEyebrow", "Тема дня", "Theme of the day"),
    insightsAria: tr("today.web.insightsAria", "Символы дня", "Symbols of the day"),
    insightCardLabel: tr("today.web.insight.card", "Карта дня", "Card of the day"),
    insightMoonLabel: tr("today.web.insight.moon", "Лунное влияние", "Moon influence"),
    insightMoonFallback: tr("today.web.insight.moonFallback", "Луна в знаке", "Moon in sign"),
    insightNumerologyLabel: tr("today.web.insight.numerology", "Нумерология", "Numerology"),
    insightNumerologyTitle: tr("today.web.insight.numerologyTitle", "Путь · вибрация дня", "Path · day vibration"),
    practicesTitle: tr("today.web.practicesTitle", "Практики дня", "Practices for today"),
    practicesLead: tr("today.web.practicesLead", "Базовые ритуалы для твоего пути.", "Core rituals for your path."),
    minutesShort: min,
    weekdayLabels:
      loc === "ru"
        ? (["П", "В", "С", "Ч", "П", "С", "В"] as const)
        : (["M", "T", "W", "T", "F", "S", "S"] as const),
    fallbackPractices,
    fallbackTimeline,
  };
}

export function todayWebGreeting(
  chrome: TodayWebDashboardChrome,
  displayName: string | null,
): string {
  const hour = new Date().getHours();
  const salutation =
    hour < 12 ? chrome.greetingMorning : hour < 18 ? chrome.greetingAfternoon : chrome.greetingEvening;
  return displayName ? `${salutation}, ${displayName}.` : `${salutation}.`;
}
