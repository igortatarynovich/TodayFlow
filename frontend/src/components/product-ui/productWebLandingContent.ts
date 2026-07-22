/** Product UI web landing — editorial copy (RU). Nav links: `@/lib/appNavConfig` guest order. */

import { GUEST_ACCESS_LIMITS } from "@/lib/guestAccessLimits";

export const PRODUCT_WEB_LANDING_HERO = {
  titleLead: "Интересно, что",
  titleTail: "сегодня для тебя?",
  subtitle:
    "Собери свой профиль по дате рождения — и открой персональный день, совместимость и практики. Можно начать с профиля или сразу проверить пару.",
  primaryCta: "Построить мой профиль",
  secondaryCta: "Совместимость",
  loginCta: "Войти",
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
  lead: "Игровая совместимость, Таро и практики — сразу. Полный профиль и Today — после сохранения через email.",
} as const;

/** После регистрации — обещание Today (статичное превью, без персональных данных). */
export const PRODUCT_WEB_LANDING_TODAY_PROMISE = {
  eyebrow: "После регистрации",
  title: "Твой Today каждое утро",
  tags: ["Тема дня", "Фокус", "Память о вчера"],
  body: "Не общий гороскоп. Персональный экран дня: на что обратить внимание, один главный шаг и вечернее закрытие — чтобы завтра продолжить с того, что было.",
  cards: [
    { id: "theme", label: "Тема", value: "«Сегодня лучше не спешить — выбери одно главное»" },
    { id: "focus", label: "Фокус", value: "Где действовать · где беречь силы" },
    { id: "memory", label: "Завтра", value: "«Вчера главным было…» — без потери контекста" },
  ],
} as const;

export const PRODUCT_WEB_LANDING_TESTIMONIALS = {
  title: "Зачем возвращаются",
  items: [
    {
      quote:
        "Утром открываю Today — понятно, куда смотреть. Вечером закрываю день, и на следующий день это не теряется.",
      name: "Елена Р.",
      role: "Креативный директор",
    },
    {
      quote:
        "Сначала попробовал совместимость и расклад — потом собрал Today. Наконец ощущение, что приложение помнит меня.",
      name: "Юлиан В.",
      role: "Системный архитектор",
    },
    {
      quote: "Ценю, что продукт про сегодня, а не про бесконечные «карты личности» с первого экрана.",
      name: "Сара Л.",
      role: "Клинический психолог",
    },
  ],
} as const;

export const PRODUCT_WEB_LANDING_FINAL = {
  title: "Начни с себя — сохрани профиль.",
  subtitle: "Дата рождения создаёт основу. Время и место откроют Асцендент и дома. Email закрепит результат в аккаунте.",
  cta: "Построить мой профиль",
} as const;

export const PRODUCT_WEB_LANDING_FOOTER = {
  tagline: "Персональный ориентир на день — с памятью о вчера.",
  companyLinks: [
    { href: "/help", label: "О нас" },
    { href: "/help", label: "Философия" },
    { href: "/privacy", label: "Конфиденциальность" },
  ],
} as const;
