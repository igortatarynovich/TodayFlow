import type { Element } from "@/lib/zodiac-utils";

/** Переключить на `asset`, когда премиальные SVG лежат в `public/images/icons/`. */
export type VisualAssetMode = "inline" | "asset";

export const VISUAL_ASSET_MODE: VisualAssetMode = "asset";

const ICON_BASE = "/images/icons";

export type ZodiacSlug =
  | "aries"
  | "taurus"
  | "gemini"
  | "cancer"
  | "leo"
  | "virgo"
  | "libra"
  | "scorpio"
  | "sagittarius"
  | "capricorn"
  | "aquarius"
  | "pisces";

export type PlanetSlug =
  | "sun"
  | "moon"
  | "mercury"
  | "venus"
  | "mars"
  | "jupiter"
  | "saturn"
  | "uranus"
  | "neptune"
  | "pluto";

export type ElementSlug = "fire" | "earth" | "air" | "water";

export type ArchetypeSlug =
  | "sage"
  | "explorer"
  | "architect"
  | "harmonizer"
  | "observer"
  | "creator"
  | "strategist"
  | "seeker"
  | "mentor"
  | "guardian"
  | "visionary"
  | "catalyst"
  | "unknown";

/** Named profile archetypes (Foundation §2) — excludes `unknown` fallback. */
export const ARCHETYPE_SLUGS = [
  "sage",
  "explorer",
  "architect",
  "harmonizer",
  "observer",
  "creator",
  "strategist",
  "seeker",
  "mentor",
  "guardian",
  "visionary",
  "catalyst",
] as const satisfies readonly ArchetypeSlug[];

export function zodiacAssetPath(slug: ZodiacSlug): string {
  return `${ICON_BASE}/zodiac/${slug}.svg`;
}

export function planetAssetPath(slug: PlanetSlug): string {
  return `${ICON_BASE}/planets/${slug}.svg`;
}

const PLANET_SLUGS = new Set<string>([
  "sun",
  "moon",
  "mercury",
  "venus",
  "mars",
  "jupiter",
  "saturn",
  "uranus",
  "neptune",
  "pluto",
]);

export function resolvePlanetSlug(raw: string | null | undefined): PlanetSlug | null {
  const key = (raw || "").trim().toLowerCase();
  if (PLANET_SLUGS.has(key)) return key as PlanetSlug;

  const map: Record<string, PlanetSlug> = {
    солнце: "sun",
    луна: "moon",
    меркурий: "mercury",
    венера: "venus",
    марс: "mars",
    юпитер: "jupiter",
    сатурн: "saturn",
    уран: "uranus",
    нептун: "neptune",
    плутон: "pluto",
  };
  return map[key] ?? null;
}

export function archetypeAssetPath(slug: ArchetypeSlug): string {
  return `${ICON_BASE}/archetypes/${slug}.svg`;
}

export function elementAssetPath(slug: ElementSlug): string {
  return `${ICON_BASE}/elements/${slug}.svg`;
}

export function elementPatternAssetPath(element: Element): string {
  return elementAssetPath(element.toLowerCase() as ElementSlug);
}

const ELEMENT_SLUGS = new Set<string>(["fire", "earth", "air", "water"]);

export function resolveElementSlug(raw: string | null | undefined): ElementSlug | null {
  const key = (raw || "").trim().toLowerCase();
  if (ELEMENT_SLUGS.has(key)) return key as ElementSlug;

  const map: Record<string, ElementSlug> = {
    огонь: "fire",
    земля: "earth",
    воздух: "air",
    вода: "water",
  };
  return map[key] ?? null;
}

export function resolveArchetypeSlug(seed: string | null | undefined): ArchetypeSlug {
  const key = (seed || "").trim().toLowerCase();
  const map: Record<string, ArchetypeSlug> = {
    sage: "sage",
    мудрец: "sage",
    explorer: "explorer",
    исследователь: "explorer",
    architect: "architect",
    архитектор: "architect",
    harmonizer: "harmonizer",
    гармонизатор: "harmonizer",
    observer: "observer",
    наблюдатель: "observer",
    creator: "creator",
    создатель: "creator",
    strategist: "strategist",
    стратег: "strategist",
    seeker: "seeker",
    искатель: "seeker",
    initiate: "seeker",
    mentor: "mentor",
    наставник: "mentor",
    guardian: "guardian",
    хранитель: "guardian",
    visionary: "visionary",
    провидец: "visionary",
    catalyst: "catalyst",
    катализатор: "catalyst",
    alchemist: "catalyst",
    oracle: "sage",
    строитель: "architect",
  };
  return map[key] || "unknown";
}

export const ARCHETYPE_LABEL_RU: Partial<Record<ArchetypeSlug, string>> = {
  sage: "Мудрец",
  explorer: "Исследователь",
  architect: "Архитектор",
  harmonizer: "Гармонизатор",
  observer: "Наблюдатель",
  creator: "Создатель",
  strategist: "Стратег",
  seeker: "Искатель",
  mentor: "Наставник",
  guardian: "Хранитель",
  visionary: "Провидец",
  catalyst: "Катализатор",
};

export const ARCHETYPE_LABEL_EN: Partial<Record<ArchetypeSlug, string>> = {
  sage: "Sage",
  explorer: "Explorer",
  architect: "Architect",
  harmonizer: "Harmonizer",
  observer: "Observer",
  creator: "Creator",
  strategist: "Strategist",
  seeker: "Seeker",
  mentor: "Mentor",
  guardian: "Guardian",
  visionary: "Visionary",
  catalyst: "Catalyst",
};

/** User-facing archetype label; machine seed stays English in the API. */
export function archetypeDisplayLabel(
  seed: string | null | undefined,
  locale: string = "ru",
  fallback = "Личный архетип",
): string {
  const raw = (seed || "").trim();
  if (!raw) return fallback;
  const slug = resolveArchetypeSlug(raw);
  if (slug === "unknown") return raw;
  const isEn = locale.toLowerCase().startsWith("en");
  if (isEn) return ARCHETYPE_LABEL_EN[slug] || raw;
  return ARCHETYPE_LABEL_RU[slug] || raw;
}

export const STRENGTH_TRAIT_ICONS = ["🏹", "💡", "🧭", "✨", "🌿"] as const;
