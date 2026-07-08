import { getJson } from "@/lib/api";
import { getLocale, resolveClientLocale } from "@/lib/i18n";
import {
  COMPATIBILITY_EXPLORE_CATEGORIES,
  COMPATIBILITY_POPULAR_READINGS,
  COMPATIBILITY_SERIES,
  type CompatibilityExploreCategory,
  type CompatibilityPopularReading,
  type CompatibilitySeries,
} from "@/lib/compatibilityEncyclopediaCatalog";

export type EncyclopediaIntroBlock = {
  kind: "paragraph" | "question" | "bullet_list";
  text?: string | null;
  items?: string[] | null;
};

export type EncyclopediaAnalyzeParams = {
  topic?: string | null;
  reading?: string | null;
  series?: string | null;
};

export type CompatibilityEncyclopediaResponse = {
  content_locale: string;
  version: string;
  hero: {
    eyebrow: string;
    title: string;
    lead: string;
  };
  categories: Array<{
    id: string;
    emoji: string;
    title: string;
    subtitle: string;
    analyze_params: EncyclopediaAnalyzeParams;
    intro_blocks?: EncyclopediaIntroBlock[];
  }>;
  popular_readings: Array<{
    id: string;
    title: string;
    analyze_params: EncyclopediaAnalyzeParams;
    intro_blocks?: EncyclopediaIntroBlock[];
  }>;
  series: Array<{
    id: string;
    title: string;
    subtitle: string;
    analyze_params: EncyclopediaAnalyzeParams;
    intro_blocks?: EncyclopediaIntroBlock[];
    scenario_bullets?: string[];
  }>;
  entry_routes: Record<string, string>;
};

function analyzeHref(params: EncyclopediaAnalyzeParams): string {
  const q = new URLSearchParams();
  if (params.topic) q.set("topic", params.topic);
  if (params.reading) q.set("reading", params.reading);
  if (params.series) q.set("series", params.series);
  const qs = q.toString();
  return qs ? `/compatibility/analyze?${qs}` : "/compatibility/analyze";
}

function fallbackCatalog(): CompatibilityEncyclopediaResponse {
  return {
    content_locale: getLocale() === "ru" ? "ru" : "en",
    version: "fallback",
    hero: {
      eyebrow: "Совместимость",
      title: "Совместимость — это намного больше, чем любовь.",
      lead: "Сегодня можно посмотреть, как два человека взаимодействуют в десятках жизненных ситуаций — от романтики до совместного бизнеса.",
    },
    categories: COMPATIBILITY_EXPLORE_CATEGORIES.map((c) => ({
      id: c.id,
      emoji: c.emoji,
      title: c.title,
      subtitle: c.subtitle,
      analyze_params: { topic: c.id === "living" ? "living_together" : c.id },
    })),
    popular_readings: COMPATIBILITY_POPULAR_READINGS.map((r) => ({
      id: r.id,
      title: r.title,
      analyze_params: { reading: r.id },
    })),
    series: COMPATIBILITY_SERIES.map((s) => ({
      id: s.id,
      title: s.title,
      subtitle: s.subtitle,
      analyze_params: { series: s.id },
    })),
    entry_routes: {
      analyze: "/compatibility/analyze",
      signs: "/compatibility/signs",
      birthdates: "/compatibility/birthdates",
      profiles: "/compatibility",
    },
  };
}

export async function fetchCompatibilityEncyclopedia(locale?: string): Promise<CompatibilityEncyclopediaResponse> {
  const loc = locale || resolveClientLocale();
  try {
    return await getJson<CompatibilityEncyclopediaResponse>(`/compatibility/encyclopedia?locale=${encodeURIComponent(loc)}`);
  } catch {
    return fallbackCatalog();
  }
}

export function mapEncyclopediaToHubCards(catalog: CompatibilityEncyclopediaResponse): {
  categories: CompatibilityExploreCategory[];
  popularReadings: CompatibilityPopularReading[];
  series: CompatibilitySeries[];
} {
  return {
    categories: catalog.categories.map((c) => ({
      id: c.id,
      emoji: c.emoji,
      title: c.title,
      subtitle: c.subtitle,
      href: analyzeHref(c.analyze_params),
    })),
    popularReadings: catalog.popular_readings.map((r) => ({
      id: r.id,
      title: r.title,
      href: analyzeHref(r.analyze_params),
    })),
    series: catalog.series.map((s) => ({
      id: s.id,
      title: s.title,
      subtitle: s.subtitle,
      href: analyzeHref(s.analyze_params),
    })),
  };
}

export function findEncyclopediaSelection(
  catalog: CompatibilityEncyclopediaResponse,
  params: { topic?: string | null; reading?: string | null; series?: string | null },
): { label: string; introBlocks: EncyclopediaIntroBlock[] } | null {
  if (params.topic) {
    const item = catalog.categories.find((c) => c.id === params.topic || c.analyze_params.topic === params.topic);
    if (item) return { label: item.title, introBlocks: item.intro_blocks || [] };
  }
  if (params.reading) {
    const item = catalog.popular_readings.find((r) => r.id === params.reading);
    if (item) return { label: item.title, introBlocks: item.intro_blocks || [] };
  }
  if (params.series) {
    const item = catalog.series.find((s) => s.id === params.series);
    if (item) return { label: item.title, introBlocks: item.intro_blocks || [] };
  }
  return null;
}
