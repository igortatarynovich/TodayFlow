/** Profile Journey + Explore copy — five human steps, then research fold. */
export const PROFILE_V2_DEPTH_NAV = [
  { id: "recognition", step: "01", title: "Кто я", hint: "Узнавание" },
  { id: "why", step: "02", title: "Почему", hint: "Опоры" },
  { id: "insight", step: "03", title: "Главный узел", hint: "Закономерность" },
  { id: "effort", step: "04", title: "Куда усилия", hint: "Вектор" },
  { id: "bridge", step: "05", title: "Мост", hint: "В день" },
] as const;

export const PROFILE_V2_EXPLORE_NAV = [
  { id: "explore", title: "Исследовать профиль", hint: "Детали" },
  { id: "natal", title: "Натальная карта", hint: "Основа" },
] as const;

export type ProfileV2ZoneId =
  | (typeof PROFILE_V2_DEPTH_NAV)[number]["id"]
  | (typeof PROFILE_V2_EXPLORE_NAV)[number]["id"];

export const PROFILE_V2_COPY = {
  mapsCta: "Карты и наблюдения",
  mapsCtaHint: "Как жизнь меняется со временем — отдельно от профиля.",
  zones: {
    recognition: {
      title: "Кто я",
      lead: "Одно предложение, в котором себя узнаёшь.",
    },
    why: {
      title: "Главное, что формирует тебя",
      selectedLabel: "Что выбрало архетип",
      influencedLabel: "Что влияет на портрет",
      honestyFallbackTitle: "На чём держится",
    },
    insight: {
      title: "Главный узел",
      giftLabel: "Твой дар",
      trapLabel: "Где он становится ловушкой",
      restoreLabel: "Что возвращает его в силу",
      groundedLabel: "На чём стоит вывод",
      helpLabel: "Что помогает",
      livingLabel: "Как это уже проявлялось",
      livingNote: "Контекст из отметок — не доказательство этого узла.",
    },
    effort: {
      title: "Твой вектор сейчас",
      lead: "Одно направление усилия — не план дня.",
      spheresLabel: "Сильнее всего проявляется",
    },
    bridge: {
      title: "Твоя история продолжается",
      cta: "Открыть историю дня",
      lead: "Продолжение пути, не второй совет «что делать».",
    },
    explore: {
      title: "Исследовать глубже",
      lead: "Карта, традиции и детали — исследовательский слой, не часть путешествия.",
      natalTitle: "Твоя натальная карта",
      detailsTitle: "Карта и детали",
      open: "Исследовать глубже",
      hide: "Свернуть детали",
      exploreHint: "Полная карта, дома и аспекты — за раскрытием.",
      updatedNote: "Карта пересчитывается при изменении данных рождения.",
    },
    /** Legacy keys for fallback first-screen when journey surface absent. */
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
      fullProfile: "Исследовать глубже",
      hideFullProfile: "Свернуть детали",
      today: "Открыть историю дня",
      todayLead: "День — следующий шаг после портрета: фокус и один шаг.",
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
