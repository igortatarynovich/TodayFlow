import type { MoodMapLocale } from "@/lib/moodMapModel";

const COPY = {
  ru: {
    eyebrow: "Карты",
    title: "Карта желаний",
    lead: "Желания — якоря, не чеклист. Маленький шаг важнее большого плана.",
    emptyLead: "Добавь месячную цель в Flow или якорь здесь — соз созвездие начнёт складываться.",
    observationEyebrow: "Наблюдение",
    selectedEyebrow: "История якоря",
    selectedEmpty: "Выбери якорь на карте.",
    shareCta: "Скопировать историю",
    shareCopied: "Скопировано",
    addPlaceholder: "Новое желание…",
    addCta: "Добавить якорь",
    linkToday: "К Today",
    linkProfile: "К профилю",
    linkRhythm: "Карта ритма",
    howToReadTitle: "Как читать карту",
    howToRead: "Каждая точка — желание или месячная цель. Близость шагов — не соревнование, а внимание.",
  },
  en: {
    eyebrow: "Maps",
    title: "Wish map",
    lead: "Wishes are anchors, not a checklist. A small step beats a big plan.",
    emptyLead: "Add a monthly goal in Flow or an anchor here—the constellation will begin.",
    observationEyebrow: "Observation",
    selectedEyebrow: "Anchor story",
    selectedEmpty: "Pick an anchor on the map.",
    shareCta: "Copy story",
    shareCopied: "Copied",
    addPlaceholder: "New wish…",
    addCta: "Add anchor",
    linkToday: "To Today",
    linkProfile: "To Profile",
    linkRhythm: "Rhythm map",
    howToReadTitle: "How to read the map",
    howToRead: "Each dot is a wish or monthly goal. Closeness is attention, not a race.",
  },
} as const;

export function wishMapCopy(locale: MoodMapLocale) {
  return COPY[locale];
}
