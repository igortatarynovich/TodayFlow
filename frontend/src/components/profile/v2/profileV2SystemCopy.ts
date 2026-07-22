/** Profile v2 — journey Steps 1–5 (above Freeze inventory).
 *  Platform gate: docs/EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md
 *  Journey SoT: docs/PROFILE_PRODUCT_JOURNEY_FORMS_V1.md · PRODUCT_BLOCK_SIX_QUESTIONS.md
 */

export const PROFILE_V2_DEPTH_NAV = [
  { id: "recognition", step: "01", title: "Узнавание", hint: "Кто ты" },
  { id: "why", step: "02", title: "Почему так", hint: "Откуда портрет" },
  { id: "insight", step: "03", title: "Узел", hint: "Главный сдвиг" },
  { id: "effort", step: "04", title: "Усилие", hint: "Один вектор" },
  { id: "bridge", step: "05", title: "Дальше", hint: "Зачем Today" },
  { id: "sources", step: "06", title: "Источники", hint: "Натал и числа" },
] as const;

export type ProfileV2ZoneId = (typeof PROFILE_V2_DEPTH_NAV)[number]["id"];

export const PROFILE_V2_COPY = {
  heroEyebrow: "Профиль",
  liveBadge: "Личный профиль",
  mapsCta: "Карты и наблюдения",
  mapsCtaHint: "Как жизнь меняется со временем — отдельно от профиля.",
  zones: {
    recognition: {
      title: "Узнавание",
      lead: "Одно имя и одна фраза, в которой себя узнаёшь.",
    },
    why: {
      title: "Почему портрет такой",
      selectedLabel: "Что выбрало архетип",
      influencedLabel: "Что влияет на портрет",
      honestyFallbackTitle: "На чём держится",
    },
    insight: {
      title: "Главный узел",
      groundedLabel: "На чём стоит",
      helpLabel: "Что помогает",
      livingLabel: "Рядом из жизни",
      livingNote: "Контекст из отметок — не доказательство этого узла.",
    },
    effort: {
      title: "Вектор усилия",
      lead: "Одно действие из выбранного узла — не план дня.",
    },
    bridge: {
      title: "Зачем открыть Today",
      cta: "Открыть Today",
      lead: "Продолжение пути, не второй совет «что делать».",
    },
    characterMore: {
      title: "Ещё о характере",
      strengthens: "Сильные стороны",
      drains: "Что забирает силу",
      helps: "Внутренние опоры",
      decisions: "Как принимаешь решения",
      patterns: "Повторяющиеся паттерны",
    },
    direction: {
      missionLabel: "Главная задача",
    },
    evidence: {
      nextLabel: "Что откроет больше ясности",
      levelPrefix: "Насколько уже видны повторы",
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

/** Forbidden day-state and system-status lexicon on production Profile V2 copy. */
export const PROFILE_V2_FORBIDDEN_LEXICON = [
  "Сегодня",
  "сегодня",
  "Камень дня",
  "Опоры дня",
  "опоры дня",
  "Недостаточно данных",
  "недостаточно данных",
  "Профиль готов",
  "профиль сформирован",
  "Мы рассчитали",
  "Нам не хватает",
] as const;
