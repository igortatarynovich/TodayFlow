import type { MoodMapLocale } from "@/lib/moodMapModel";

const COPY = {
  ru: {
    observationEyebrow: "Наблюдение",
    selectedDayEyebrow: "История дня",
    selectedDayEmpty: "Нажми на отмеченный день на карте привычки.",
    linkMood: "Карта настроения",
    linkEnergy: "Карта энергии",
    legendMarked: "отмечено",
    legendEmpty: "без отметки",
    howToReadGridLine: "35 дней — мягкая сетка 7×5. Цвет — твой узор по каждой привычке.",
  },
  en: {
    observationEyebrow: "Observation",
    selectedDayEyebrow: "Day story",
    selectedDayEmpty: "Tap a marked day on a habit strip.",
    linkMood: "Mood map",
    linkEnergy: "Energy map",
    legendMarked: "marked",
    legendEmpty: "no mark",
    howToReadGridLine: "35 days—a soft 7×5 grid. Color is your weave for each habit.",
  },
} as const;

export function habitMapCopy(locale: MoodMapLocale) {
  return COPY[locale];
}
