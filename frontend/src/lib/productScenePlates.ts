/**
 * Public inventory → product scene plates.
 * Cover-crop via object-position — banners stay panoramic; UI picks the subject.
 */

export type ProductScenePlateId =
  | "tarot_cards"
  | "tarot_quiet"
  | "compat_night"
  | "compat_day"
  | "compat_pair"
  | "compat_map"
  | "compat_love"
  | "practice_body"
  | "practice_still"
  | "practice_stretch"
  | "reflection"
  | "landing_hero"
  | "landing_today"
  | "landing_cta";

export type ProductScenePlateSpec = {
  id: ProductScenePlateId;
  src: string;
  /** CSS object-position — crop the panoramic subject into the plate. */
  position: string;
  /** Default aspect for the plate frame. */
  aspect: "wide" | "cinema" | "square";
  tone: "daylight" | "dusk" | "night";
};

export const PRODUCT_SCENE_PLATES: Record<ProductScenePlateId, ProductScenePlateSpec> = {
  tarot_cards: {
    id: "tarot_cards",
    src: "/images/tarot_banner_2.png",
    position: "52% 82%",
    aspect: "cinema",
    tone: "dusk",
  },
  tarot_quiet: {
    id: "tarot_quiet",
    src: "/images/tarot_banner.png",
    position: "82% 42%",
    aspect: "wide",
    tone: "daylight",
  },
  compat_night: {
    id: "compat_night",
    src: "/images/night_banner.png",
    position: "72% 32%",
    aspect: "cinema",
    tone: "night",
  },
  compat_day: {
    id: "compat_day",
    src: "/images/day_banner.png",
    position: "70% 28%",
    aspect: "cinema",
    tone: "daylight",
  },
  compat_pair: {
    id: "compat_pair",
    src: "/images/day_girl_banner.png",
    position: "78% 40%",
    aspect: "wide",
    tone: "daylight",
  },
  compat_map: {
    id: "compat_map",
    src: "/images/cosmic/Celestial_Map.webp",
    position: "50% 50%",
    aspect: "square",
    tone: "night",
  },
  compat_love: {
    id: "compat_love",
    src: "/images/archetypes/liubovnik.webp",
    position: "50% 28%",
    aspect: "square",
    tone: "dusk",
  },
  practice_body: {
    id: "practice_body",
    src: "/images/praktiki_banner.png",
    position: "58% 38%",
    aspect: "cinema",
    tone: "dusk",
  },
  practice_still: {
    id: "practice_still",
    src: "/images/praktiki_banner_3.png",
    position: "62% 42%",
    aspect: "cinema",
    tone: "dusk",
  },
  practice_stretch: {
    id: "practice_stretch",
    src: "/images/praktiki_banner_2.png",
    position: "50% 40%",
    aspect: "wide",
    tone: "dusk",
  },
  reflection: {
    id: "reflection",
    src: "/images/hero/inner_reflection.webp",
    position: "50% 40%",
    aspect: "wide",
    tone: "dusk",
  },
  landing_hero: {
    id: "landing_hero",
    src: "/images/day_girl_banner.png",
    position: "78% 38%",
    aspect: "wide",
    tone: "daylight",
  },
  landing_today: {
    id: "landing_today",
    src: "/images/day_banner.png",
    position: "68% 30%",
    aspect: "cinema",
    tone: "daylight",
  },
  landing_cta: {
    id: "landing_cta",
    src: "/images/banners/dashboard_hero.png",
    position: "50% 55%",
    aspect: "cinema",
    tone: "daylight",
  },
};

/** Landing service section id → plate. */
export function landingServicePlate(
  serviceId: "tarot" | "compatibility" | "practices" | string,
): ProductScenePlateId {
  switch (serviceId) {
    case "tarot":
      return "tarot_cards";
    case "compatibility":
      return "compat_pair";
    case "practices":
      return "practice_still";
    default:
      return "landing_hero";
  }
}

/** Mode → plate for Compatibility hub direction step. */
export function compatibilityModePlate(
  modeId: string | null | undefined,
): ProductScenePlateId {
  switch ((modeId ?? "").trim()) {
    case "love":
      return "compat_love";
    case "family":
      return "compat_pair";
    case "parenting":
      return "compat_day";
    case "office":
      return "compat_map";
    default:
      return "compat_night";
  }
}

export function resolveProductScenePlate(
  id: ProductScenePlateId | null | undefined,
): ProductScenePlateSpec | null {
  if (!id) return null;
  return PRODUCT_SCENE_PLATES[id] ?? null;
}
