/** Profile Journey + Explore copy — five human steps, then research fold. */
export const PROFILE_V2_DEPTH_NAV = [
  { id: "recognition", step: "01", title: "Твоя суть", hint: "Узнавание" },
  { id: "why", step: "02", title: "Почему именно так", hint: "Опоры" },
  { id: "insight", step: "03", title: "Что важно понять", hint: "Узел" },
  { id: "effort", step: "04", title: "Куда усилия", hint: "Вектор" },
  { id: "bridge", step: "05", title: "Мост в день", hint: "В день" },
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
      title: "Твоя суть",
      lead: "Одно предложение, в котором себя узнаёшь.",
    },
    why: {
      title: "Главное, что формирует тебя",
      selectedLabel: "Что выбрало архетип",
      influencedLabel: "Что влияет на портрет",
      honestyFallbackTitle: "На чём держится",
    },
    insight: {
      title: "Что важно понять о себе",
      giftLabel: "Твой дар",
      trapLabel: "Твоя ловушка",
      restoreLabel: "Что помогает расти",
      groundedLabel: "На чём стоит вывод",
      helpLabel: "Что помогает",
      livingLabel: "Как это уже проявлялось",
      livingNote: "Контекст из отметок — не доказательство этого узла.",
    },
    effort: {
      title: "Твой вектор на развитие",
      lead: "Одно направление усилия — не план дня.",
      spheresLabel: "Где это проявится сильнее",
    },
    bridge: {
      title: "Твоя история продолжается",
      cta: "Открыть историю дня",
      lead: "Продолжение пути, не второй совет «что делать».",
    },
    explore: {
      title: "Твоя натальная карта",
      lead: "Карта души и детали — исследовательский слой после путешествия.",
      natalTitle: "Карта твоей души",
      detailsTitle: "Карта и детали",
      open: "Исследовать карту",
      hide: "Свернуть карту",
      exploreHint: "Полная карта, дома и аспекты — за раскрытием.",
      updatedNote: "Карта пересчитывается при изменении данных рождения.",
      stepBadge: "6",
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
