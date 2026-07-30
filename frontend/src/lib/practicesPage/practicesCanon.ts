/**
 * Practices Screen v1.1 — locked need/format IDs (SoT: docs/practices/PRACTICES_SCREEN_V1.md).
 * Legacy catalog keys are not SoT; map via keywords for client filter until API supports needs.
 */

export const PRACTICE_NEED_IDS = [
  "calm",
  "focus",
  "recover",
  "body",
  "understand",
  "sleep",
] as const;

export type PracticeNeedId = (typeof PRACTICE_NEED_IDS)[number];

export const PRACTICE_FORMAT_IDS = [
  "meditation",
  "breath",
  "yoga",
  "stretch",
  "visualization",
  "affirmation",
  "reflection",
  "music",
  "sleep",
] as const;

export type PracticeFormatId = (typeof PRACTICE_FORMAT_IDS)[number];

export type PracticeCanonLocale = "ru" | "en";

const NEED_LABELS: Record<PracticeNeedId, { ru: string; en: string }> = {
  calm: { ru: "Успокоиться", en: "Settle" },
  focus: { ru: "Собраться", en: "Gather" },
  recover: { ru: "Восстановиться", en: "Recover" },
  body: { ru: "Почувствовать тело", en: "Feel the body" },
  understand: { ru: "Понять себя", en: "Understand" },
  sleep: { ru: "Уснуть", en: "Sleep" },
};

const FORMAT_LABELS: Record<PracticeFormatId, { ru: string; en: string }> = {
  meditation: { ru: "Медитация", en: "Meditation" },
  breath: { ru: "Дыхание", en: "Breath" },
  yoga: { ru: "Йога", en: "Yoga" },
  stretch: { ru: "Растяжка", en: "Stretch" },
  visualization: { ru: "Визуализация", en: "Visualization" },
  affirmation: { ru: "Аффирмации", en: "Affirmations" },
  reflection: { ru: "Рефлексия", en: "Reflection" },
  music: { ru: "Музыка", en: "Music" },
  sleep: { ru: "Сон", en: "Sleep" },
};

/** Keywords for client-side match against title/description/category/tags. */
export const PRACTICE_NEED_KEYWORDS: Record<PracticeNeedId, string[]> = {
  calm: ["calm", "спокой", "тревог", "успоко", "relax", "тишин", "отпускан", "мягк"],
  focus: ["focus", "фокус", "собр", "концентрац", "вниман", "ясн"],
  recover: ["recover", "восстан", "устал", "ресурс", "энерг", "перезагруз"],
  body: ["body", "тело", "йог", "yoga", "растяж", "stretch", "сомат", "движен", "размин"],
  understand: ["reflect", "рефлек", "понят", "дневник", "journal", "вопрос", "ясность", "себе"],
  sleep: ["sleep", "сон", "уснуть", "вечер", "bedtime", "ноч", "засып"],
};

export const PRACTICE_FORMAT_KEYWORDS: Record<PracticeFormatId, string[]> = {
  meditation: ["meditat", "медит", "mindfulness", "осознан"],
  breath: ["breath", "дых", "пранаям", "вдох", "выдох"],
  yoga: ["yoga", "йог", "asana", "асан"],
  stretch: ["stretch", "растяж", "мобилит"],
  visualization: ["visual", "визуал", "образ", "воображ"],
  affirmation: ["affirm", "афф", "мантр", "mantra"],
  reflection: ["reflect", "рефлек", "дневник", "journal", "письм", "gratitude", "благодар"],
  music: ["music", "музык", "sound", "звук", "ambient"],
  sleep: ["sleep", "сон", "bedtime", "засып", "ночн"],
};

export function practiceNeedLabel(locale: PracticeCanonLocale, id: PracticeNeedId): string {
  return NEED_LABELS[id][locale];
}

export function practiceFormatLabel(locale: PracticeCanonLocale, id: PracticeFormatId): string {
  return FORMAT_LABELS[id][locale];
}

export type PracticeMatchable = {
  title: string;
  description?: string;
  category?: string;
  tags?: string[];
  practice_type?: string;
};

function haystackOf(practice: PracticeMatchable): string {
  return [
    practice.title,
    practice.description,
    practice.category,
    practice.practice_type,
    ...(practice.tags ?? []),
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
}

function matchesKeywords(haystack: string, keywords: string[]): boolean {
  return keywords.some((kw) => haystack.includes(kw.toLowerCase()));
}

export function practiceMatchesNeed(practice: PracticeMatchable, need: PracticeNeedId): boolean {
  return matchesKeywords(haystackOf(practice), PRACTICE_NEED_KEYWORDS[need]);
}

export function practiceMatchesFormat(
  practice: PracticeMatchable,
  format: PracticeFormatId,
): boolean {
  const haystack = haystackOf(practice);
  if (matchesKeywords(haystack, PRACTICE_FORMAT_KEYWORDS[format])) return true;
  // Backend categories often equal format-ish ids
  const cat = (practice.category || "").toLowerCase();
  if (format === "breath" && (cat === "breathing" || cat === "breath")) return true;
  if (format === "meditation" && cat === "meditation") return true;
  if (format === "affirmation" && cat === "affirmation") return true;
  if (format === "reflection" && (cat === "reflection" || cat === "gratitude")) return true;
  if (format === "sleep" && cat === "sleep") return true;
  if (format === "music" && cat === "music") return true;
  return false;
}

export function inferPracticeFormat(practice: PracticeMatchable): PracticeFormatId | null {
  for (const id of PRACTICE_FORMAT_IDS) {
    if (practiceMatchesFormat(practice, id)) return id;
  }
  return null;
}

/** Outcome-first card title hint when catalog title is technical — keep catalog title; use for subtitle line. */
export function formatPracticeMetaLine(
  locale: PracticeCanonLocale,
  minutes: number | null | undefined,
  formatId: PracticeFormatId | null,
  minutesShort: string,
): string {
  const parts: string[] = [];
  if (minutes != null && minutes > 0) parts.push(`${minutes} ${minutesShort}`);
  if (formatId) parts.push(practiceFormatLabel(locale, formatId));
  return parts.join(" · ") || (locale === "ru" ? "Практика" : "Practice");
}
