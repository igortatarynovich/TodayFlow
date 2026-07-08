/**
 * Каталог веб-страницы `/practices`: цели и направления + ключевые слова для фильтрации.
 * Подписи RU/EN; внутренние ключи направлений — стабильные RU-строки (совпадают с матчингом в API-текстах).
 * iOS: при нативном каталоге — паритет смыслов; ключевые слова могут дублироваться здесь.
 */

import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";

export const PRACTICE_CATALOG_DIRECTION_KEYS = [
  "Медитация",
  "Дыхательные практики",
  "Телесные практики",
  "Движение",
  "Активация",
  "Внимание",
  "Осознанность",
  "Рефлексия",
  "Дневник",
  "Практики изменений",
  "Циклы",
  "Медитация любящей доброты",
  "Открытость",
] as const;

export type PracticeCatalogDirectionKey = (typeof PRACTICE_CATALOG_DIRECTION_KEYS)[number];

export const PRACTICE_CATALOG_DIRECTION_KEYWORDS: Record<PracticeCatalogDirectionKey, string[]> = {
  Медитация: ["медитация", "медитировать", "осознанность", "mindfulness"],
  "Дыхательные практики": ["дыхание", "пранаяма", "breathing", "вдох", "выдох"],
  "Телесные практики": ["тело", "движение", "ходьба", "йога", "растяжка"],
  Движение: ["движение", "активность", "энергия", "активация"],
  Активация: ["энергия", "активация", "бодрость", "пробуждение"],
  Внимание: ["внимание", "концентрация", "фокус", "осознанность"],
  Осознанность: ["осознанность", "mindfulness", "настоящий момент", "присутствие"],
  Рефлексия: ["рефлексия", "размышление", "дневник", "вопросы", "понимание"],
  Дневник: ["дневник", "запись", "journaling", "размышление"],
  "Практики изменений": ["изменение", "рост", "развитие", "паттерн"],
  Циклы: ["цикл", "луна", "неделя", "месяц", "переход"],
  "Медитация любящей доброты": ["любовь", "доброта", "сострадание", "метта", "loving-kindness"],
  Открытость: ["открытость", "принятие", "отношения", "связь"],
};

const DIRECTION_LABELS: Record<PracticeCatalogDirectionKey, { ru: string; en: string }> = {
  Медитация: { ru: "Медитация", en: "Meditation" },
  "Дыхательные практики": { ru: "Дыхательные практики", en: "Breathwork" },
  "Телесные практики": { ru: "Телесные практики", en: "Somatic practice" },
  Движение: { ru: "Движение", en: "Movement" },
  Активация: { ru: "Активация", en: "Activation" },
  Внимание: { ru: "Внимание", en: "Attention" },
  Осознанность: { ru: "Осознанность", en: "Mindfulness" },
  Рефлексия: { ru: "Рефлексия", en: "Reflection" },
  Дневник: { ru: "Дневник", en: "Journaling" },
  "Практики изменений": { ru: "Практики изменений", en: "Change work" },
  Циклы: { ru: "Циклы", en: "Cycles" },
  "Медитация любящей доброты": { ru: "Медитация любящей доброты", en: "Loving-kindness" },
  Открытость: { ru: "Открытость", en: "Openness" },
};

export function practiceDirectionLabel(locale: FlowPracticesChromeLocale, key: PracticeCatalogDirectionKey): string {
  return locale === "ru" ? DIRECTION_LABELS[key].ru : DIRECTION_LABELS[key].en;
}

export type PracticeCatalogGoalId = "calm" | "energy" | "focus" | "connection" | "growth" | "relationships";

type GoalDef = {
  id: PracticeCatalogGoalId;
  icon: string;
  names: { ru: string; en: string };
  descriptions: { ru: string; en: string };
  directions: PracticeCatalogDirectionKey[];
};

const GOAL_DEFS: GoalDef[] = [
  {
    id: "calm",
    icon: "🧘",
    names: { ru: "Спокойствие и баланс", en: "Calm and balance" },
    descriptions: {
      ru: "Снизить тревожность, найти внутренний покой, восстановить баланс",
      en: "Ease anxiety, find inner calm, restore balance",
    },
    directions: ["Медитация", "Дыхательные практики", "Телесные практики"],
  },
  {
    id: "energy",
    icon: "⚡",
    names: { ru: "Энергия и активность", en: "Energy and activity" },
    descriptions: {
      ru: "Повысить уровень энергии, мотивации, активности",
      en: "Raise energy, motivation, and activity",
    },
    directions: ["Дыхательные практики", "Движение", "Активация"],
  },
  {
    id: "focus",
    icon: "🎯",
    names: { ru: "Фокус и концентрация", en: "Focus and concentration" },
    descriptions: {
      ru: "Улучшить концентрацию, убрать отвлечения, повысить продуктивность",
      en: "Improve concentration, cut distraction, get more done",
    },
    directions: ["Медитация", "Внимание", "Осознанность"],
  },
  {
    id: "connection",
    icon: "💫",
    names: { ru: "Связь с собой", en: "Connection with yourself" },
    descriptions: {
      ru: "Лучше понимать себя, свои потребности, эмоции",
      en: "Understand yourself, your needs, and your emotions",
    },
    directions: ["Рефлексия", "Дневник", "Осознанность"],
  },
  {
    id: "growth",
    icon: "🌱",
    names: { ru: "Рост и развитие", en: "Growth and development" },
    descriptions: {
      ru: "Развивать новые навыки, менять паттерны, расти",
      en: "Build skills, shift patterns, grow",
    },
    directions: ["Рефлексия", "Практики изменений", "Циклы"],
  },
  {
    id: "relationships",
    icon: "💝",
    names: { ru: "Отношения", en: "Relationships" },
    descriptions: {
      ru: "Улучшить отношения с близкими, открыться любви",
      en: "Improve closeness with loved ones, open to love",
    },
    directions: ["Медитация любящей доброты", "Рефлексия", "Открытость"],
  },
];

export type PracticeCatalogGoalRow = {
  id: PracticeCatalogGoalId;
  icon: string;
  name: string;
  description: string;
  directions: PracticeCatalogDirectionKey[];
};

export function getPracticeCatalogGoals(locale: FlowPracticesChromeLocale): PracticeCatalogGoalRow[] {
  const ru = locale === "ru";
  return GOAL_DEFS.map((g) => ({
    id: g.id,
    icon: g.icon,
    name: ru ? g.names.ru : g.names.en,
    description: ru ? g.descriptions.ru : g.descriptions.en,
    directions: g.directions,
  }));
}
