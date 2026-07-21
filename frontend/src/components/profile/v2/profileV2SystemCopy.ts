/** Profile v2 — copy aligned with Figma `profile-v2-system` (154:2). */

export const PROFILE_V2_DEPTH_NAV = [
  { id: "facts", step: "01", title: "Факты", hint: "Якоря за полминуты" },
  { id: "character", step: "02", title: "Характер", hint: "Как устроен" },
  { id: "direction", step: "03", title: "Направление", hint: "Куда расти" },
  { id: "history", step: "04", title: "Наблюдения", hint: "День за днём" },
  { id: "sky", step: "05", title: "Небо", hint: "Источник глубины" },
] as const;

export type ProfileV2ZoneId = (typeof PROFILE_V2_DEPTH_NAV)[number]["id"];

export const PROFILE_V2_COPY = {
  heroEyebrow: "Профиль",
  heroTitle: "Твой личный профиль",
  liveBadge: "Личный профиль",
  updatedPrefix: "обновлено сегодня",
  awarenessTitle: "Точность наблюдений",
  awarenessLead: "Растёт с закрытыми днями и накопленной историей — без выдуманных процентов.",
  stonePrefix: "Камень дня",
  supportsPrefix: "Опоры",
  zones: {
    facts: {
      title: "Факты",
      lead: "Быстрые якоря без длинной интерпретации.",
      cards: {
        archetype: "Архетип",
        astro: "Астро-факты",
        awareness: "Точность наблюдений",
        anchors: "Опоры дня",
      },
      astroHint: "Солнце, Луна, ASC, стихия, дата рождения.",
      anchorsHint: "Камень · Цвет · Тотем · Планета.",
    },
    character: {
      title: "Характер",
      lead: "Сильные стороны, что забирает силу, и как принимаешь решения.",
      strengthens: "Сильные стороны",
      drains: "Что забирает силу",
      helps: "Опоры",
      decisions: "Как принимаешь решения",
    },
    direction: {
      title: "Направление",
      lead: "Главная задача и сферы — куда расти и что поддерживать.",
      missionLabel: "Главная задача",
    },
    history: {
      title: "Наблюдения",
      lead: "Как меняется состояние день за днём.",
    },
    sky: {
      title: "Небо",
      lead: "Натальная карта, транзиты, планеты и дома — когда уже понятно, кто ты.",
      updatedNote: "Карта пересчитывается при изменении данных рождения.",
    },
  },
} as const;
