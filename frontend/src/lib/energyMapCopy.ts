import type { MoodMapLocale } from "@/lib/moodMapModel";

const COPY = {
  ru: {
    eyebrow: "Карты",
    title: "Карта энергии",
    lead: "Каждый день в Today оставляет след темпа. Нажми на день — увидишь историю, не цифры.",
    emptyLead: "Поживи день в Today — отметки и вечернее закрытие добавят первые точки на карте.",
    loading: "Подтягиваю историю энергии…",
    howToReadTitle: "Как читать карту",
    howToReadLine1: "Один день — одна клетка. Цвет — темп дня: от тихого к подвижному.",
    howToReadLine2: "Нажми на день — увидишь, что поддерживало или забирало силы.",
    observationEyebrow: "Наблюдение",
    selectedDayEyebrow: "История дня",
    selectedDayEmpty: "Выбери день с отметкой на карте.",
    linkToday: "К Today",
    linkProfile: "К профилю",
    linkMood: "Карта настроения",
    linkHabits: "Карта привычек",
    linkRhythm: "Карта ритма",
    legendEmpty: "без отметки",
    legendQuiet: "тихий",
    legendCalm: "спокойный",
    legendSteady: "ровный",
    legendActive: "подвижный",
  },
  en: {
    eyebrow: "Maps",
    title: "Energy map",
    lead: "Each day in Today leaves a trace of your tempo. Tap a day—see a story, not a score.",
    emptyLead: "Live a day in Today—marks and evening close add the first points here.",
    loading: "Loading your energy history…",
    howToReadTitle: "How to read the map",
    howToReadLine1: "One day, one cell. Color is the day’s tempo—from quiet to active.",
    howToReadLine2: "Tap a day—see what supported or drained your energy.",
    observationEyebrow: "Observation",
    selectedDayEyebrow: "Day story",
    selectedDayEmpty: "Pick a day with a mark on the map.",
    linkToday: "To Today",
    linkProfile: "To Profile",
    linkMood: "Mood map",
    linkHabits: "Habit map",
    linkRhythm: "Rhythm map",
    legendEmpty: "no mark",
    legendQuiet: "quiet",
    legendCalm: "calm",
    legendSteady: "steady",
    legendActive: "active",
  },
} as const;

export function energyMapCopy(locale: MoodMapLocale) {
  return COPY[locale];
}
