import type { MoodMapLocale } from "@/lib/moodMapModel";

const COPY = {
  ru: {
    eyebrow: "Карты",
    title: "Карта настроения",
    lead: "Каждая отметка в Today добавляет точку. Нажми на день — увидишь историю, не цифры.",
    emptyLead: "Отметь настроение в Today — здесь появится первая точка на карте.",
    howToReadTitle: "Как читать карту",
    howToReadLine1: "Один день — одна клетка. Цвет — твоё утреннее состояние.",
    howToReadLine2: "Нажми на день — увидишь фокус, обещание и как закрылся вечер.",
    observationEyebrow: "Наблюдение",
    selectedDayEyebrow: "История дня",
    selectedDayEmpty: "Выбери день с отметкой на карте.",
    linkToday: "К Today",
    linkProfile: "К профилю",
    linkHabits: "Карта привычек",
    linkRhythm: "Карта ритма",
    legendEmpty: "без отметки",
  },
  en: {
    eyebrow: "Maps",
    title: "Mood map",
    lead: "Each mark in Today adds a point. Tap a day—see a story, not a score.",
    emptyLead: "Mark your mood in Today—the first point on your map will appear here.",
    howToReadTitle: "How to read the map",
    howToReadLine1: "One day, one cell. Color is your morning state.",
    howToReadLine2: "Tap a day—see focus, promise, and how the evening closed.",
    observationEyebrow: "Observation",
    selectedDayEyebrow: "Day story",
    selectedDayEmpty: "Pick a day with a mark on the map.",
    linkToday: "To Today",
    linkProfile: "To Profile",
    linkHabits: "Habit map",
    linkRhythm: "Rhythm map",
    legendEmpty: "no mark",
  },
} as const;

export function moodMapCopy(locale: MoodMapLocale) {
  return COPY[locale];
}
