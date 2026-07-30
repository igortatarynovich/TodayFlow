/** Product UI web landing — editorial copy (RU). */

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

export type LandingServiceSection = {
  id: "tarot" | "compatibility" | "practices";
  eyebrow: string;
  title: string;
  body: string;
  href: string;
  cta: string;
  icon: "tarot" | "users" | "activity";
};

/** One viewport per guest service — nav scrolls here; CTA opens the product route. */
export const PRODUCT_WEB_LANDING_SERVICE_SECTIONS: LandingServiceSection[] = [
  {
    id: "tarot",
    eyebrow: "Без регистрации",
    title: "Таро — вопрос и ясный расклад",
    body: `${GUEST_ACCESS_LIMITS.tarotSpreads} расклад бесплатно: задай вопрос, открой карты и получи ответ, который можно унести в день.`,
    href: "/tarot",
    cta: "Открыть Таро",
    icon: "tarot",
  },
  {
    id: "compatibility",
    eyebrow: "Без регистрации",
    title: "Совместимость — две карты рядом",
    body: `${GUEST_ACCESS_LIMITS.compatibilityChecks} проверки пар бесплатно: увидишь, где вы усиливаете друг друга и где лучше беречь границы.`,
    href: "/compatibility",
    cta: "Проверить пару",
    icon: "users",
  },
  {
    id: "practices",
    eyebrow: "Без регистрации",
    title: "Практики — короткий шаг в теле",
    body: "Базовые практики для спокойного дня: дыхание, фокус и короткие ритуалы, когда нужна опора без длинного разбора.",
    href: "/practices",
    cta: "К практикам",
    icon: "activity",
  },
];

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

/**
 * Landing screens — Plan v4 SoT (tracker 2026-07-29).
 * One viewport screen per id; top nav anchors scroll to these only.
 * Guest trials split from legacy `#try` → tarot / compatibility / practices.
 */
export const PRODUCT_WEB_LANDING_SCREENS = [
  { id: "hero", role: "curiosity", nav: false },
  { id: "tarot", role: "guest-trial", nav: true, navLabel: "Таро" },
  { id: "compatibility", role: "guest-trial", nav: true, navLabel: "Совместимость" },
  { id: "practices", role: "guest-trial", nav: false },
  { id: "today", role: "promise", nav: true, navLabel: "Как это работает" },
  { id: "why", role: "return", nav: true, navLabel: "Почему возвращаются" },
  { id: "cta", role: "close", nav: false },
] as const;

export type LandingScreenId = (typeof PRODUCT_WEB_LANDING_SCREENS)[number]["id"];

export const PRODUCT_WEB_LANDING_SECTION_IDS: LandingScreenId[] = PRODUCT_WEB_LANDING_SCREENS.map(
  (screen) => screen.id,
);

type LandingNavScreen = Extract<(typeof PRODUCT_WEB_LANDING_SCREENS)[number], { nav: true }>;

/**
 * Top marketing nav — all in-page anchors (SoT v4).
 * Practices has a section + CTA but no separate top-nav item.
 */
export const PRODUCT_WEB_LANDING_NAV = (
  PRODUCT_WEB_LANDING_SCREENS.filter((s): s is LandingNavScreen => s.nav) as LandingNavScreen[]
).map((s) => ({
  id: s.id,
  href: `#${s.id}` as const,
  label: s.navLabel,
}));

export const PRODUCT_WEB_LANDING_FOOTER = {
  tagline: "Персональный ориентир на день — с памятью о вчера.",
  companyLinks: [
    { href: "/help", label: "О нас" },
    { href: "/help", label: "Философия" },
    { href: "/privacy", label: "Конфиденциальность" },
  ],
} as const;
