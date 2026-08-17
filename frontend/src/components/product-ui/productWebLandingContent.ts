/** Product UI web landing — editorial copy (RU). Guest Story Surface P0.
 * Brand/trust claims (NASA/JPL, layered Canon): docs/content/TODAYFLOW_TRUST_LAYER.md
 * Do not invent astronomy or “one true astrology” copy outside that canon.
 */

import { GUEST_ACCESS_LIMITS } from "@/lib/guestAccessLimits";

export const PRODUCT_WEB_LANDING_HERO = {
  titleLead: "TodayFlow видит не только твой день,",
  titleTail: "а то, как дни складываются в тебя",
  subtitle:
    "Не предсказание на сегодня, а история, которая помнит вчера. Тема, фокус и короткий шаг — в том же формате, что будет у твоего Today.",
  fragmentEyebrow: "Пример дня",
  fragmentThemeLabel: "Тема",
  fragmentTheme:
    "Если с утра уже пять «срочных» дел — день скорее про одно главное, не про все сразу",
  fragmentFocusLabel: "Фокус",
  fragmentFocus: "Где действовать · где беречь силы",
  primaryCtaDemo: "Посмотреть, как это работает",
  primaryCtaCompat: "Посмотреть динамику вашей связи",
  loginCta: "Войти",
  toolsEyebrow: "Инструменты для момента",
  toolsTarotLabel: "Таро",
  toolsPracticesLabel: "Практики",
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
    id: "compatibility",
    eyebrow: "Без регистрации",
    title: "Совместимость — две карты рядом",
    body: `${GUEST_ACCESS_LIMITS.compatibilityChecks} проверки пар бесплатно: увидишь, где вы усиливаете друг друга и где лучше беречь границы.`,
    href: "/compatibility",
    cta: "Проверить пару",
    icon: "users",
  },
  {
    id: "tarot",
    eyebrow: "Инструмент для момента",
    title: "Таро — вопрос и ясный расклад",
    body: `${GUEST_ACCESS_LIMITS.tarotSpreads} расклад бесплатно: задай вопрос, открой карты и получи ответ, который можно унести в день.`,
    href: "/tarot",
    cta: "Открыть Таро",
    icon: "tarot",
  },
  {
    id: "practices",
    eyebrow: "Инструмент для момента",
    title: "Практики — короткий шаг в теле",
    body: "Базовые практики для спокойного дня: дыхание, фокус и короткие ритуалы, когда нужна опора без длинного разбора.",
    href: "/practices",
    cta: "К практикам",
    icon: "activity",
  },
];

/** После регистрации — обещание Today (статичное превью, без персональных данных). */
export const PRODUCT_WEB_LANDING_TODAY_PROMISE = {
  eyebrow: "После демо и Profile",
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
  subtitle: "Сначала посмотри демо-день — потом собери Profile, который сделает Today твоим.",
  cta: "Собрать мой Today",
} as const;

/**
 * Landing screens — Guest Story Surface P0.
 * Compatibility stays strong in nav; Tarot is nav; Practices section only (low-weight).
 */
export const PRODUCT_WEB_LANDING_SCREENS = [
  { id: "hero", role: "curiosity", nav: false },
  { id: "compatibility", role: "guest-trial", nav: true, navLabel: "Совместимость" },
  { id: "tarot", role: "guest-trial", nav: true, navLabel: "Таро" },
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
 * Top marketing nav — in-page anchors.
 * Practices has a section + CTA but no separate top-nav item (secondary tool).
 */
export const PRODUCT_WEB_LANDING_NAV = (
  PRODUCT_WEB_LANDING_SCREENS.filter((s): s is LandingNavScreen => s.nav) as LandingNavScreen[]
).map((s) => ({
  id: s.id,
  href: `#${s.id}` as const,
  label: s.navLabel,
}));

export const PRODUCT_WEB_LANDING_FOOTER = {
  tagline: "Не только день — история, которая помнит вчера.",
  companyLinks: [
    { href: "/help", label: "О нас" },
    { href: "/help", label: "Философия" },
  ],
} as const;
