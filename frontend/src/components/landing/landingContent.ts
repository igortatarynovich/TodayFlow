/** Landing editorial — demo copy, not user-specific. */

export const LANDING_HERO = {
  title: "Каждый день открывает что-то новое о тебе.",
  lead:
    "TodayFlow собирает твою личную карту жизни: день, карту, число, настроение, практики, цели и историю, которая становится глубже каждый день.",
  primaryCta: "Узнать, что уже видно",
  secondaryCta: "Войти",
} as const;

export const LANDING_TODAY_PREVIEW = {
  eyebrow: "Сегодня",
  footnote:
    "Каждый день складывается из темы, символов, рекомендаций и вечернего итога.",
} as const;

export type LandingProductFragment = {
  id: string;
  label: string;
  title?: string;
  lines: string[];
};

export const LANDING_PRODUCT_FRAGMENTS: LandingProductFragment[] = [
  {
    id: "theme",
    label: "Тема дня",
    lines: ["Сегодня лучше всего работает спокойная концентрация."],
  },
  {
    id: "tarot",
    label: "Карта дня",
    title: "Отшельник",
    lines: ["Иногда лучший ответ появляется после паузы."],
  },
  {
    id: "caution",
    label: "Предостережение",
    lines: ["Сегодня легче распылиться. Лучше выбрать одно главное направление."],
  },
  {
    id: "strength",
    label: "Источник силы",
    lines: ["Тишина, порядок и короткая практика перед первым важным делом."],
  },
];

export const LANDING_INSIGHT = {
  title: "Завтра TodayFlow вспомнит сегодняшний день.",
  lead:
    "Через неделю появятся первые повторения. Через месяц начнут складываться карты настроения, энергии, привычек, целей и личных циклов.",
  layers: ["Энергия", "Настроение", "Привычки", "Карты Таро", "Цели", "Личные циклы"],
} as const;

export const LANDING_FINAL = {
  lead: "Две минуты — и ты увидишь, что TodayFlow уже может рассказать именно о тебе.",
  cta: "Узнать, что уже видно",
} as const;

/** Static demo cells for landing heatmap (intensity 0–3). */
export const LANDING_HEATMAP_DEMO: number[][] = [
  [0, 1, 2, 1, 0, 2, 3],
  [1, 2, 3, 2, 1, 2, 1],
  [0, 1, 2, 3, 2, 1, 0],
  [1, 0, 1, 2, 3, 2, 1],
  [2, 1, 0, 1, 2, 3, 2],
  [1, 2, 2, 1, 3, 2, 1],
  [0, 1, 1, 2, 2, 3, 2],
];

export function landingHeatmapCellClass(intensity: number): string {
  if (intensity >= 3) return "heatHigh";
  if (intensity === 2) return "heatMid";
  if (intensity === 1) return "heatLow";
  return "heatEmpty";
}
