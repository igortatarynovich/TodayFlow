/** Profile v2 — first-screen recognition + full-profile depth.
 *  Platform gate: docs/EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md
 *  IA: Pattern-style first surface; CHANI-style daily loop lives on Today.
 */

export const PROFILE_V2_DEPTH_NAV = [
  { id: "recognition", step: "01", title: "Кто ты", hint: "Узнавание" },
  { id: "traits", step: "02", title: "Особенности", hint: "Три черты" },
  { id: "contradiction", step: "03", title: "Противоречие", hint: "Наблюдаемое" },
  { id: "helps", step: "04", title: "Что помогает", hint: "Один вывод" },
  { id: "full", step: "05", title: "Полный профиль", hint: "Разделы" },
] as const;

export type ProfileV2ZoneId = (typeof PROFILE_V2_DEPTH_NAV)[number]["id"];

export const PROFILE_V2_COPY = {
  heroEyebrow: "Профиль",
  liveBadge: "Личный профиль",
  mapsCta: "Карты и наблюдения",
  mapsCtaHint: "Как жизнь меняется со временем — отдельно от профиля.",
  zones: {
    recognition: {
      title: "Кто ты",
      lead: "Одно предложение, в котором себя узнаёшь.",
    },
    traits: {
      title: "Три главные особенности",
      decisions: "Как принимаешь решения",
      intimacy: "Как строишь близость",
      selfFriction: "Где сам себе мешаешь",
    },
    contradiction: {
      title: "Главное внутреннее противоречие",
    },
    helps: {
      title: "Что тебе помогает",
      lead: "Один практически применимый вывод.",
    },
    actions: {
      fullProfile: "Открыть полный профиль",
      hideFullProfile: "Свернуть полный профиль",
      today: "Открыть Today",
      todayLead: "День продолжается отдельно от портрета.",
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
    sources: {
      title: "Основа карты",
      lead: "Натальная карта и числа — фундамент личности.",
      explore: "Исследовать глубже",
      exploreHint: "Полная карта, дома и аспекты — за раскрытием.",
      updatedNote: "Карта пересчитывается при изменении данных рождения.",
    },
    // Legacy keys kept for DepthRail / unused callers during transition.
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
    evidence: {
      nextLabel: "Что откроет больше ясности",
      levelPrefix: "Насколько уже видны повторы",
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
