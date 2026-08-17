/** Product UI web landing — brand surface, not a slogan bolted onto Guest Story.
 * Narrative SoT: docs/content/TODAYFLOW_TRUST_LAYER.md §5 (Co-Star principle: thesis before merchandising).
 * Do not invent astronomy, NASA partnership, or “one true astrology” copy.
 */

import { GUEST_ACCESS_LIMITS } from "@/lib/guestAccessLimits";

export const PRODUCT_WEB_LANDING_HERO = {
  brand: "TodayFlow",
  beats: [
    "Точные астрономические данные.",
    "Столетия астрологической интерпретации.",
    "Один личный взгляд.",
  ],
  manifesto:
    "Не гадаем по знаку. Положения планет — эфемериды NASA JPL. Смысл — из разных исторических слоёв, не из одной модной школы. Взгляд собирается для тебя.",
  primaryCtaDemo: "Посмотреть, как это работает",
  loginCta: "Войти",
  learnMore: "Узнать, на чём стоит",
} as const;

export type LandingServiceSection = {
  id: "tarot" | "compatibility" | "practices";
  eyebrow: string;
  title: string;
  body: string;
  href: string;
  cta: string;
  icon: "tarot" | "users" | "activity";
};

/** Guest chapters after the brand thesis — Compatibility stays a full chapter, not a hero dual-CTA. */
export const PRODUCT_WEB_LANDING_SERVICE_SECTIONS: LandingServiceSection[] = [
  {
    id: "compatibility",
    eyebrow: "Двое",
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

/** After the thesis — one personal perspective, with continuity as the product proof. */
export const PRODUCT_WEB_LANDING_TODAY_PROMISE = {
  eyebrow: "Один личный взгляд",
  title: "Твой Today каждое утро",
  tags: ["Тема дня", "Фокус", "Память о вчера"],
  body: "Не общий гороскоп на знак. Персональный экран дня: на что обратить внимание, один главный шаг и вечернее закрытие — чтобы завтра продолжить с того, что было.",
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
 * Trust Layer on acquisition (docs/content/TODAYFLOW_TRUST_LAYER.md).
 * Astronomy claim = NASA JPL ephemerides via Swiss, live.
 * Interpretation = method (layered Canon), not a finished in-app catalog.
 */
export const PRODUCT_WEB_LANDING_TRUST = {
  eyebrow: "Три опоры",
  title: "На чём стоит TodayFlow",
  body: "Астрологию часто считают произвольной. Мы разделяем слои: небо можно посчитать; смысл не выдаём за единственную истину одной школы. Взгляд собирается для тебя.",
  items: [
    {
      id: "sky",
      kicker: "Точность",
      title: "Астрономия, а не приближение",
      body: "Где Солнце, Луна и планеты — проверяемые положения, не таблица «на знак». Считаем по эфемеридам NASA JPL. Карта строится на координатах неба в момент рождения — не на упрощённом гороскопе.",
    },
    {
      id: "canon",
      kicker: "Глубина",
      title: "Столетия толкования — не с нуля",
      body: "Смыслы не выдумываются с чистого листа. Canon собирает разные исторические слои и школы и хранит, откуда каждое утверждение. Не одна модная трактовка как вся традиция.",
    },
    {
      id: "person",
      kicker: "Человечность",
      title: "Не таблица и не общий гороскоп",
      body: "Одна и та же карта звучит по-разному в разных школах. Мы собираем не шаблон, а один честный взгляд: твоя карта, этот день и то, что уже было вчера.",
    },
  ],
} as const;

export const PRODUCT_WEB_LANDING_FINAL = {
  title: "Точные положения неба. Смысл — именно для тебя.",
  subtitle: "Сначала посмотри демо-день — потом собери Profile, который сделает Today твоим.",
  cta: "Собрать мой Today",
} as const;

/**
 * Landing screens — brand thesis first (Trust Layer §5), then product chapters.
 * Guest Story P0 path (demo → invite) stays; dual hero CTA and #why are retired.
 */
export const PRODUCT_WEB_LANDING_SCREENS = [
  { id: "hero", role: "brand", nav: false },
  { id: "trust", role: "thesis", nav: true, navLabel: "На чём стоит" },
  { id: "today", role: "promise", nav: true, navLabel: "Сегодня" },
  { id: "compatibility", role: "guest-trial", nav: true, navLabel: "Совместимость" },
  { id: "tarot", role: "guest-trial", nav: true, navLabel: "Таро" },
  { id: "practices", role: "guest-trial", nav: false },
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

export const PRODUCT_WEB_LANDING_SEO = {
  description:
    "Точные астрономические данные. Столетия астрологической интерпретации. Один личный взгляд. Не общий гороскоп — день, собранный для тебя.",
} as const;

export const PRODUCT_WEB_LANDING_FOOTER = {
  tagline:
    "Точные астрономические данные. Столетия астрологической интерпретации. Один личный взгляд.",
  companyLinks: [
    { href: "/help", label: "О нас" },
    { href: "/help", label: "Философия" },
  ],
} as const;
