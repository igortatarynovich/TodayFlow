import type { MoodMapLocale } from "@/lib/moodMapModel";

const COPY = {
  ru: {
    eyebrow: "Карты",
    title: "Карта аскез",
    lead: "Каждый отмеченный день — камень на тропе. Не проценты — история пути.",
    emptyLead: "Выбери аскезу в Flow — здесь появится первая тропа.",
    observationEyebrow: "Наблюдение",
    selectedDayEyebrow: "История дня",
    selectedDayEmpty: "Выбери день на тропе.",
    shareCta: "Скопировать историю",
    shareCopied: "Скопировано",
    linkToday: "К Today",
    linkProfile: "К профилю",
    linkRhythm: "Карта ритма",
    linkPromise: "Карта обещаний",
    howToReadTitle: "Как читать карту",
    howToRead: "Вертикальная тропа — последние недели. Зелёный камень — день с отметкой.",
    legendDone: "день отмечен",
    legendEmpty: "без отметки",
  },
  en: {
    eyebrow: "Maps",
    title: "Ascetic map",
    lead: "Each marked day is a stone on the path. Story, not percentages.",
    emptyLead: "Pick an ascetic in Flow—the first path will appear here.",
    observationEyebrow: "Observation",
    selectedDayEyebrow: "Day story",
    selectedDayEmpty: "Pick a day on the path.",
    shareCta: "Copy story",
    shareCopied: "Copied",
    linkToday: "To Today",
    linkProfile: "To Profile",
    linkRhythm: "Rhythm map",
    linkPromise: "Promise map",
    howToReadTitle: "How to read the map",
    howToRead: "The vertical path is recent weeks. A green stone is a marked day.",
    legendDone: "marked",
    legendEmpty: "no mark",
  },
} as const;

export function asceticMapCopy(locale: MoodMapLocale) {
  return COPY[locale];
}
