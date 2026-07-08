import type { ReactNode } from "react";
import {
  IconHeart,
  IconMountain,
  IconRoute,
  IconSparkles,
  IconSun,
  IconMoon,
  IconWaves,
} from "@/design-system";
import type { ProfileFrameworkAnchor } from "@/lib/profilePage/buildProfileQuickMapData";
import type { CoreProfile } from "@/lib/types";
import { ZODIAC_OPTIONS } from "@/lib/zodiacOptions";
import { zodiacRuName } from "@/lib/zodiacKnowledge";

const ZODIAC_GLYPH: Record<string, string> = {
  aries: "♈",
  taurus: "♉",
  gemini: "♊",
  cancer: "♋",
  leo: "♌",
  virgo: "♍",
  libra: "♎",
  scorpio: "♏",
  sagittarius: "♐",
  capricorn: "♑",
  aquarius: "♒",
  pisces: "♓",
};

const RAIL_LABELS: Record<string, string> = {
  sun: "Солнце",
  moon: "Луна",
  rising: "ASC",
  mc: "MC",
  lp: "Путь",
  archetype: "Тип",
};

const PILL_PREFIX: Record<string, string> = {
  sun: "☉",
  moon: "☽",
  rising: "ASC",
  lp: "Путь",
};

export type ProfileRailAnchor = {
  id: string;
  label: string;
  value: string;
  icon: ReactNode;
};

function signGlyphFromText(text: string): string | null {
  const lower = text.toLowerCase();
  for (const option of ZODIAC_OPTIONS) {
    if (lower.includes(option.name.toLowerCase())) {
      return ZODIAC_GLYPH[option.id] ?? null;
    }
  }
  return null;
}

function extractAnchorValue(label: string, id: string): string {
  const trimmed = label.trim();
  if (id === "lp") {
    const match = trimmed.match(/(\d+)/);
    return match?.[1] ?? trimmed.replace(/^число пути\s*/i, "").trim();
  }
  if (id === "archetype") {
    return trimmed.replace(/^архетип\s*/i, "").trim();
  }
  if (id === "rising") {
    const glyph = signGlyphFromText(trimmed);
    if (glyph) return glyph;
    const sign = trimmed.replace(/^асцендент\s*(в\s*)?/i, "").trim();
    return sign || trimmed;
  }
  const inMatch = trimmed.match(/\sв\s+(.+)$/i);
  if (inMatch?.[1]) return inMatch[1].trim();
  return trimmed.replace(/^(солнце|луна|mc)\s*(в\s*)?/i, "").trim() || trimmed;
}

function railIconFor(id: string): ReactNode {
  switch (id) {
    case "sun":
      return <IconSun />;
    case "moon":
      return <IconMoon />;
    case "lp":
    case "mc":
      return <IconRoute />;
    case "archetype":
      return <IconSparkles />;
    default:
      return <IconSun />;
  }
}

export function buildProfileIdentityPills(
  anchors: ProfileFrameworkAnchor[],
  coreProfile?: CoreProfile | null,
): string[] {
  const byId = new Map(anchors.map((anchor) => [anchor.id, anchor]));
  const pills: string[] = [];

  const sunAnchor = byId.get("sun");
  if (sunAnchor) {
    const value = extractAnchorValue(sunAnchor.label, "sun");
    pills.push(`${PILL_PREFIX.sun} ${value}`);
  } else if (coreProfile?.astro?.sun_sign) {
    pills.push(`${PILL_PREFIX.sun} ${zodiacRuName(coreProfile.astro.sun_sign)}`);
  }

  const moonAnchor = byId.get("moon");
  if (moonAnchor) {
    pills.push(`${PILL_PREFIX.moon} ${extractAnchorValue(moonAnchor.label, "moon")}`);
  }

  const risingAnchor = byId.get("rising");
  if (risingAnchor) {
    const value = extractAnchorValue(risingAnchor.label, "rising");
    pills.push(`${PILL_PREFIX.rising} ${value}`);
  }

  const pathAnchor = byId.get("lp");
  const lifePath = coreProfile?.numerology?.life_path;
  if (pathAnchor) {
    pills.push(`${PILL_PREFIX.lp} ${extractAnchorValue(pathAnchor.label, "lp")}`);
  } else if (lifePath != null) {
    pills.push(`${PILL_PREFIX.lp} ${lifePath}`);
  }

  return pills.slice(0, 4);
}

export function buildProfileRailAnchors(anchors: ProfileFrameworkAnchor[]): ProfileRailAnchor[] {
  const order = ["sun", "moon", "lp", "archetype"] as const;
  const byId = new Map(anchors.map((anchor) => [anchor.id, anchor]));

  return order.flatMap((id) => {
    const anchor = byId.get(id);
    if (!anchor) return [];
    return [
      {
        id,
        label: RAIL_LABELS[id] ?? anchor.label,
        value: extractAnchorValue(anchor.label, id),
        icon: railIconFor(id),
      },
    ];
  });
}

export function profileSphereIcon(title: string): ReactNode {
  const key = title.trim().toLowerCase();
  if (key.includes("отнош")) return <IconHeart />;
  if (key.includes("работ")) return <IconMountain />;
  if (key.includes("деньг") || key.includes("финанс")) return <IconWaves />;
  if (key.includes("здоров")) return <IconSparkles />;
  if (key.includes("семь")) return <IconMoon />;
  if (key.includes("рост")) return <IconRoute />;
  return <IconSparkles />;
}

export function buildProfileHeroQuote(archetype: string, identitySummary: string | null): string | null {
  if (archetype && identitySummary) {
    const summary = identitySummary.replace(/\.$/, "");
    return `«${archetype}. ${summary}.»`;
  }
  if (archetype) return `«${archetype}»`;
  if (identitySummary) return `«${identitySummary}»`;
  return null;
}
