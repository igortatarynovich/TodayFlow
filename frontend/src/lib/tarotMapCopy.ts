import type { MoodMapLocale } from "@/lib/moodMapModel";

const COPY = {
  ru: {
    eyebrow: "Карты",
    title: "Карта таро",
    lead: "Архетипическое путешествие — какие темы и карты сопровождали вопросы.",
    emptyLead: "Сделай несколько раскладов — появится личная линия, не отчёт.",
    shareCta: "Скопировать историю",
    shareCopied: "Скопировано",
    linkTarot: "К вопросам",
    linkJourney: "Полная история",
    linkProfile: "К профилю",
  },
  en: {
    eyebrow: "Maps",
    title: "Tarot arc",
    lead: "An archetypal journey—which themes and cards walked with your questions.",
    emptyLead: "Do a few readings—a personal line will appear, not a report.",
    shareCta: "Copy story",
    shareCopied: "Copied",
    linkTarot: "To questions",
    linkJourney: "Full history",
    linkProfile: "To Profile",
  },
} as const;

export function tarotMapCopy(locale: MoodMapLocale) {
  return COPY[locale];
}
