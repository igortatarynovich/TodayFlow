/** Product UI web landing — editorial copy (RU). Nav links: `@/lib/appNavConfig` guest order. */

import { GUEST_ACCESS_LIMITS } from "@/lib/guestAccessLimits";

export const PRODUCT_WEB_LANDING_HERO = {
  titleLead: "Интересно, что",
  titleTail: "сегодня для тебя?",
  subtitle:
    "TodayFlow — персональный ориентир на день: тема, фокус, практика и память о вчера. Сначала попробуй бесплатно — потом собери свой Today.",
  primaryCta: "Создать мой Today",
  secondaryCta: "Войти",
} as const;

export const PRODUCT_WEB_LANDING_ORBIT_NODES = [
  { id: "sun", label: "Фокус", style: { top: "18%", left: "68%" } },
  { id: "moon", label: "Темп", style: { top: "32%", left: "14%" } },
  { id: "path", label: "Шаг", style: { top: "58%", left: "72%" } },
  { id: "star", label: "Вечер", style: { top: "72%", left: "20%" } },
  { id: "sage", label: "Память", style: { top: "82%", left: "52%" } },
] as const;

/** Без регистрации — то, что можно попробовать сразу. */
export const PRODUCT_WEB_LANDING_GUEST_TRIALS = [
  {
    id: "tarot",
    href: "/tarot",
    title: "Расклад Таро",
    body: `${GUEST_ACCESS_LIMITS.tarotSpreads} расклад бесплатно — задай вопрос и открой карты.`,
    icon: "tarot" as const,
    cta: "Открыть Таро",
  },
  {
    id: "compatibility",
    href: "/compatibility",
    title: "Совместимость",
    body: `${GUEST_ACCESS_LIMITS.compatibilityChecks} проверки пар бесплатно — без аккаунта.`,
    icon: "users" as const,
    cta: "Проверить пару",
  },
  {
    id: "practices",
    href: "/practices",
    title: "Практики",
    body: "Базовые практики для спокойного дня — дыхание, фокус, короткие ритуалы.",
    icon: "activity" as const,
    cta: "К практикам",
  },
] as const;

export const PRODUCT_WEB_LANDING_GUEST_SECTION = {
  eyebrow: "Без регистрации",
  title: "Попробуй сейчас",
  lead: "Today и профиль откроются после регистрации. До этого — три инструмента, чтобы почувствовать продукт.",
} as const;

/** После регистрации — обещание Today (статичное превью, без персональных данных). */
export const PRODUCT_WEB_LANDING_TODAY_PROMISE = {
  eyebrow: "После регистрации",
  title: "Твой Today каждое утро",
  tags: ["Тема дня", "Фокус", "Память о вчера"],
  body: "Не общий гороскоп. Персональный экран дня: на что обратить внимание, один главный шаг и вечернее закрытие — чтобы завтра продолжить с того, что было.",
  cards: [
    {
      id: "theme",
      label: "Тема",
      value: "Если с утра уже пять «срочных» дел — день скорее про одно главное, не про все сразу",
    },
    { id: "focus", label: "Фокус", value: "Где действовать · где беречь силы" },
    { id: "memory", label: "Завтра", value: "«Вчера главным было…» — без потери контекста" },
  ],
} as const;

/**
 * Почему возвращаются — product reasons, не фейковые отзывы с именем+должностью
 * (FOUNDATION_UI §12 · TODAY_LANGUAGE antipatterns: no invented testimonials).
 */
export const PRODUCT_WEB_LANDING_RETURN_REASONS = {
  title: "Зачем возвращаются",
  items: [
    {
      id: "morning",
      title: "Утро с направлением",
      body: "Открываешь Today — видно, куда смотреть сегодня, без общей ленты советов на все случаи жизни.",
    },
    {
      id: "memory",
      title: "День не обнуляется",
      body: "Вечернее закрытие сохраняет нить: завтра начинается не с нуля, а с того, что уже было важным.",
    },
    {
      id: "today-not-portrait",
      title: "Про сегодня, не про анкету",
      body: "Сначала день и один шаг. Глубокая карта личности — когда она нужна, а не как стена на входе.",
    },
  ],
} as const;

export const PRODUCT_WEB_LANDING_FINAL = {
  title: "Завтра утром TodayFlow вспомнит сегодня.",
  subtitle: "Создай свой Today — тема, фокус и история дня начнут складываться с первого утра.",
  cta: "Создать мой Today",
} as const;

export const PRODUCT_WEB_LANDING_FOOTER = {
  tagline: "Персональный ориентир на день — с памятью о вчера.",
  companyLinks: [
    { href: "/help", label: "О нас" },
    { href: "/help", label: "Философия" },
    { href: "/privacy", label: "Конфиденциальность" },
  ],
} as const;
