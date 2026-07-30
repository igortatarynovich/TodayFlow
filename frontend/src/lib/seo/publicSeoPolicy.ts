/**
 * Public SEO policy — which routes are marketing vs app shell.
 * Canon intent: landing + guest-trial share surfaces indexable;
 * auth / onboarding / personal shells stay unique-titled but noindex.
 */
import type { Metadata } from "next";

export const SEO_NOINDEX: Metadata["robots"] = {
  index: false,
  follow: false,
  googleBot: { index: false, follow: false },
};

export const SEO_INDEX: Metadata["robots"] = {
  index: true,
  follow: true,
  googleBot: {
    index: true,
    follow: true,
    "max-video-preview": -1,
    "max-image-preview": "large",
    "max-snippet": -1,
  },
};

export type PublicSeoRoute = {
  title: string;
  description: string;
  /** Include in sitemap.xml */
  sitemap: boolean;
  robots: NonNullable<Metadata["robots"]>;
};

/** Segment-level defaults (layouts). Deeper pages may override. */
export const PUBLIC_SEO_BY_SEGMENT: Record<string, PublicSeoRoute> = {
  today: {
    title: "Сегодня",
    description:
      "Персональная картина дня: тема, фокус, практика и память о вчера — не общий гороскоп.",
    sitemap: false,
    robots: SEO_NOINDEX,
  },
  profile: {
    title: "Моя карта",
    description:
      "Цельный портрет личности: ядро, противоречия, решения, отношения и жизненные циклы.",
    sitemap: false,
    robots: SEO_NOINDEX,
  },
  account: {
    title: "Аккаунт",
    description: "Настройки аккаунта TodayFlow.",
    sitemap: false,
    robots: SEO_NOINDEX,
  },
  auth: {
    title: "Вход",
    description: "Войти в TodayFlow или создать аккаунт.",
    sitemap: false,
    robots: SEO_NOINDEX,
  },
  onboarding: {
    title: "Создать мой Today",
    description: "Имя, дата рождения и первый персональный разбор — до регистрации.",
    sitemap: false,
    robots: SEO_NOINDEX,
  },
  compatibility: {
    title: "Совместимость",
    description:
      "Динамика между двумя людьми: что сближает, где напряжение и что сделать на практике.",
    sitemap: true,
    robots: SEO_INDEX,
  },
  tarot: {
    title: "Таро",
    description:
      "Сформулируй вопрос, выбери расклад и получи ответ, который можно унести в день.",
    sitemap: true,
    robots: SEO_INDEX,
  },
  practices: {
    title: "Практики",
    description:
      "Короткие практики под состояние: дыхание, медитация и ритуалы с длительностью и уровнем.",
    sitemap: true,
    robots: SEO_INDEX,
  },
  help: {
    title: "Справка",
    description: "Как пользоваться TodayFlow: Сегодня, профиль, кольца и прогресс.",
    sitemap: true,
    robots: SEO_INDEX,
  },
  pricing: {
    title: "Тарифы",
    description: "Планы TodayFlow — персональный день с памятью о вчера.",
    sitemap: true,
    robots: SEO_INDEX,
  },
  terms: {
    title: "Условия использования",
    description: "Условия использования TodayFlow.",
    sitemap: true,
    robots: SEO_INDEX,
  },
  privacy: {
    title: "Конфиденциальность",
    description: "Политика конфиденциальности TodayFlow.",
    sitemap: true,
    robots: SEO_INDEX,
  },
  catalog: {
    title: "Каталог",
    description: "Персональные сервисы TodayFlow: профиль, день, отношения и углублённые разборы.",
    sitemap: true,
    robots: SEO_INDEX,
  },
};

/** Paths disallowed in robots.txt (prefix match). */
export const ROBOTS_DISALLOW_PREFIXES = [
  "/today",
  "/profile",
  "/account",
  "/auth",
  "/onboarding",
  "/admin",
  "/dev",
  "/dashboard",
  "/tracking",
  "/journal",
  "/affirmations",
  "/asceticisms",
  "/cycle",
  "/habits",
  "/flow",
  "/maps",
  "/lunar",
  "/numerology",
  "/reports",
  "/challenges",
  "/natal-chart",
  "/birth-chart",
  "/calendar",
  "/growth",
  "/morning-ritual",
  "/forecast",
  "/forecasts",
  "/questions",
  "/library",
  "/app",
  "/signup",
  "/login",
  "/checkout",
  "/billing",
  "/generate",
  "/demo",
] as const;

export function metadataForSegment(segment: keyof typeof PUBLIC_SEO_BY_SEGMENT): Metadata {
  const route = PUBLIC_SEO_BY_SEGMENT[segment];
  return {
    title: route.title,
    description: route.description,
    robots: route.robots,
    openGraph: {
      title: route.title,
      description: route.description,
    },
    twitter: {
      title: route.title,
      description: route.description,
    },
  };
}
