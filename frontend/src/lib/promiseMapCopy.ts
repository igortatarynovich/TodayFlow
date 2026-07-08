import type { MoodMapLocale } from "@/lib/moodMapModel";

const COPY = {
  ru: {
    eyebrow: "Карты",
    title: "Карта обещаний",
    lead: "Каждое обещание дня и вечернее закрытие оставляют след. Нажми на день — увидишь историю, не статистику.",
    emptyLead: "Дай обещание дня в Today и закрой вечер — здесь появится первая точка.",
    howToReadTitle: "Как читать карту",
    howToReadLine1: "Один день — одна клетка. Цвет — исход обещания: сделал, частично, не сделал или ещё открыто.",
    howToReadLine2: "Нажми на день — увидишь, что обещал себе и как закрылся вечер.",
    observationEyebrow: "Наблюдение",
    selectedDayEyebrow: "История дня",
    selectedDayEmpty: "Выбери день с обещанием на карте.",
    linkToday: "К Today",
    linkProfile: "К профилю",
    linkMood: "Карта настроения",
    linkEnergy: "Карта энергии",
    linkHabits: "Карта привычек",
    linkRhythm: "Карта ритма",
    legendEmpty: "без отметки",
    legendDone: "сделал",
    legendPartial: "частично",
    legendNotDone: "не сделал",
    legendOpen: "открыто",
  },
  en: {
    eyebrow: "Maps",
    title: "Promise map",
    lead: "Each day’s promise and evening close leave a trace. Tap a day—see a story, not stats.",
    emptyLead: "Set a promise in Today and close the evening—the first point appears here.",
    howToReadTitle: "How to read the map",
    howToReadLine1: "One day, one cell. Color is the promise outcome: done, partial, not done, or still open.",
    howToReadLine2: "Tap a day—see what you promised and how the evening closed.",
    observationEyebrow: "Observation",
    selectedDayEyebrow: "Day story",
    selectedDayEmpty: "Pick a day with a promise on the map.",
    linkToday: "To Today",
    linkProfile: "To Profile",
    linkMood: "Mood map",
    linkEnergy: "Energy map",
    linkHabits: "Habit map",
    linkRhythm: "Rhythm map",
    legendEmpty: "no mark",
    legendDone: "done",
    legendPartial: "partial",
    legendNotDone: "not done",
    legendOpen: "open",
  },
} as const;

export function promiseMapCopy(locale: MoodMapLocale) {
  return COPY[locale];
}
