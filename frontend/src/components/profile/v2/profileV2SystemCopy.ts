/** Profile v2 — copy aligned with Figma `profile-v2-system` (154:2). */

export const PROFILE_V2_DEPTH_NAV = [
  { id: "facts", step: "01", title: "ФАКТЫ", hint: "30 секунд: якоря" },
  { id: "character", step: "02", title: "ХАРАКТЕР", hint: "как я устроен" },
  { id: "direction", step: "03", title: "НАПРАВЛЕНИЕ", hint: "куда расти" },
  { id: "history", step: "04", title: "НАБЛЮДЕНИЯ", hint: "как меняется день за днём" },
  { id: "sky", step: "05", title: "НЕБО", hint: "источник глубины" },
] as const;

export type ProfileV2ZoneId = (typeof PROFILE_V2_DEPTH_NAV)[number]["id"];

export const PROFILE_V2_COPY = {
  heroEyebrow: "ПРОФИЛЬ",
  heroTitle: "Твой личный профиль",
  liveBadge: "личный профиль",
  updatedPrefix: "обновлено сегодня",
  awarenessTitle: "ТОЧНОСТЬ ЛИЧНЫХ НАБЛЮДЕНИЙ",
  awarenessLead: "Растёт с закрытыми днями и накопленной историей — без выдуманных процентов.",
  stonePrefix: "Камень дня",
  supportsPrefix: "Опоры",
  zones: {
    facts: {
      title: "Факты",
      lead: "Что я знаю о себе сразу: быстрые якоря без длинной интерпретации.",
      cards: {
        archetype: "АРХЕТИП",
        astro: "АСТРО-ФАКТЫ",
        awareness: "ТОЧНОСТЬ НАБЛЮДЕНИЙ",
        anchors: "ОПОРЫ ДНЯ",
      },
      astroHint: "Солнце, Луна, ASC, стихия, дата рождения.",
      anchorsHint: "Камень · Цвет · Тотем · Планета.",
    },
    character: {
      title: "Характер",
      lead: "Сильные стороны, что забирает силу, и как ты принимаешь решения.",
      strengthens: "Сильные стороны",
      drains: "Что забирает силу",
      helps: "3 опоры",
      decisions: "Как принимаешь решения",
    },
    direction: {
      title: "Направление",
      lead: "Главная задача и девять сфер — куда расти и что поддерживать.",
      missionLabel: "Главная задача",
    },
    history: {
      title: "Наблюдения",
      lead: "Тепловые карты, динамика и «Мои дни» — как меняется состояние.",
    },
    sky: {
      title: "Небо",
      lead: "Глубина после понимания себя: натальная карта, транзиты, планеты и дома раскрываются внутри этой зоны.",
      updatedNote: "Карта пересчитывается при изменении данных рождения.",
    },
  },
} as const;
