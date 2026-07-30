/**
 * Static guest pitches — crawler-readable product explanation (no personal data).
 */

export const GUEST_TODAY_PITCH = {
  eyebrow: "Что такое Today",
  title: "Персональная картина твоего дня",
  lead:
    "У каждого дня есть общий фон. Твой Today добавляет к нему твою карту, число дня, настроение, намерение и контекст жизни — не общий гороскоп.",
  parts: [
    {
      id: "theme",
      label: "Тема",
      body: "На что обратить внимание сегодня — одно главное, а не пять срочных дел сразу.",
    },
    {
      id: "focus",
      label: "Фокус",
      body: "Где действовать и где беречь силы — короткий ориентир на день.",
    },
    {
      id: "memory",
      label: "Память",
      body: "Вечер и завтра: «вчера главным было…» — день не обнуляется.",
    },
  ],
  needs: "Нужны имя и дата рождения. Сначала посмотри демо — потом собери Profile.",
  ctaPrimary: "Посмотреть демо-день",
  ctaPrimaryHref: "/demo/today",
  ctaSecondary: "Уже есть аккаунт? Войти",
  ctaSecondaryHref: "/auth?mode=login",
} as const;

export const GUEST_PROFILE_PITCH = {
  eyebrow: "Что такое профиль",
  title: "Цельная история о том, кто ты",
  lead:
    "Не набор характеристик и не просто натальная карта. Профиль — фундамент: собирается один раз и делает Today, Совместимость и Таро точнее.",
  parts: [
    {
      id: "core",
      label: "Ядро",
      body: "Солнце, путь числа и устойчивые черты — кто ты в спокойном состоянии.",
    },
    {
      id: "tension",
      label: "Противоречия",
      body: "Где внутри сталкиваются разные части — и как это проявляется в выборе.",
    },
    {
      id: "relations",
      label: "Связи",
      body: "Как ты входишь в отношения и где держать границы.",
    },
    {
      id: "cycles",
      label: "Циклы",
      body: "Энергия и периоды — что сейчас на подъёме, а что просит тишины.",
    },
  ],
  needs: "Profile открывает точный Today. Сначала коротко — зачем карта, потом имя и дата рождения.",
  ctaPrimary: "Построить мой Profile",
  ctaPrimaryHref: "/onboarding/invite",
  ctaSecondary: "Уже есть аккаунт? Войти",
  ctaSecondaryHref: "/auth?mode=login",
} as const;
