/** Profile v2 — PR-4 origin layers (Identity · Interpretation · Evidence · Sources).
 *  Platform gate: docs/EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md (umbrella wins on conflict).
 *  Surface IA: docs/PR4_PROFILE_CANON.md — applies umbrella; does not invent a separate gate.
 */

export const PROFILE_V2_DEPTH_NAV = [
  { id: "identity", step: "01", title: "Идентичность", hint: "Что не меняется" },
  { id: "character", step: "02", title: "Характер", hint: "Как устроен" },
  { id: "direction", step: "03", title: "Направление", hint: "Куда расти" },
  { id: "evidence", step: "04", title: "Обоснование", hint: "Почему так" },
  { id: "sources", step: "05", title: "Источники", hint: "Натал и числа" },
] as const;

export type ProfileV2ZoneId = (typeof PROFILE_V2_DEPTH_NAV)[number]["id"];

export const PROFILE_V2_COPY = {
  heroEyebrow: "Профиль",
  heroTitle: "Твой личный профиль",
  liveBadge: "Личный профиль",
  mapsCta: "Карты и наблюдения",
  mapsCtaHint: "Как жизнь меняется со временем — отдельно от профиля.",
  zones: {
    identity: {
      title: "Идентичность",
      lead: "Факты и расчёты, которые формируют ядро — без дневного состояния.",
      cards: {
        archetype: "Архетип",
        astro: "Базовые сигнатуры",
      },
      astroHint: "Солнце, Луна, ASC, стихия, число пути.",
    },
    character: {
      title: "Характер",
      lead: "Сильные стороны, что забирает силу, и как принимаешь решения.",
      strengthens: "Сильные стороны",
      drains: "Что забирает силу",
      helps: "Внутренние опоры",
      decisions: "Как принимаешь решения",
      patterns: "Повторяющиеся паттерны",
      forming: "Как это складывается",
    },
    direction: {
      title: "Направление",
      lead: "Главная задача и сферы — куда расти и что поддерживать.",
      missionLabel: "Главная задача",
    },
    evidence: {
      title: "Обоснование",
      lead: "Почему портрет звучит так — и чего ещё не хватает для уверенности.",
      nextLabel: "Что уточнит портрет",
      levelPrefix: "Зрелость наблюдений",
    },
    sources: {
      title: "Источники",
      lead: "Натальная карта и числа — фундамент личности, не отдельный продукт.",
      explore: "Исследовать глубже",
      exploreHint: "Полная карта, дома и аспекты — за раскрытием.",
      updatedNote: "Карта пересчитывается при изменении данных рождения.",
    },
  },
} as const;

/** Forbidden day-state lexicon on production Profile V2 copy. */
export const PROFILE_V2_FORBIDDEN_LEXICON = [
  "Сегодня",
  "сегодня",
  "Камень дня",
  "Опоры дня",
  "опоры дня",
] as const;
