import type { MoodMapLocale } from "@/lib/moodMapModel";

const COPY = {
  ru: {
    eyebrow: "Карты",
    title: "Карта связей",
    lead: "Круги — к кому и к каким темам возвращается внимание. Не рейтинг совместимости.",
    emptyLead: "Открой разбор в Совместимости — здесь появятся первые узлы сети.",
    observationEyebrow: "Наблюдение",
    selectedEyebrow: "История узла",
    selectedEmpty: "Выбери круг на карте.",
    shareCta: "Скопировать историю",
    shareCopied: "Скопировано",
    linkCompat: "К совместимости",
    linkProfile: "К профилю",
    howToReadTitle: "Как читать карту",
    howToRead: "Размер — не «лучше/хуже», а сколько раз ты возвращался к этой связи.",
  },
  en: {
    eyebrow: "Maps",
    title: "Relationship map",
    lead: "Circles show who and what themes draw your attention—not a compatibility score.",
    emptyLead: "Open a reading in Compatibility—the first nodes will appear here.",
    observationEyebrow: "Observation",
    selectedEyebrow: "Node story",
    selectedEmpty: "Pick a circle on the map.",
    shareCta: "Copy story",
    shareCopied: "Copied",
    linkCompat: "To Compatibility",
    linkProfile: "To Profile",
    howToReadTitle: "How to read the map",
    howToRead: "Size isn't better or worse—it's how often you returned to this connection.",
  },
} as const;

export function relationshipMapCopy(locale: MoodMapLocale) {
  return COPY[locale];
}
