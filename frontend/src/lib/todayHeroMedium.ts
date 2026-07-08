import type { ReactNode } from "react";
import { createElement } from "react";
import { ArchetypeSymbol } from "@/components/visualIdentity/ArchetypeSymbol";
import { ZodiacIcon } from "@/components/visualIdentity/ZodiacIcon";
import type { HeroMediumPillar } from "@/components/foundation/HeroMedium";
import type { CoreProfile } from "@/lib/types";
import { layerSignLabel } from "@/lib/profilePage/buildProfilePlanetaryData";
import { getSunInSignEntry, resolveZodiacSignId } from "@/lib/zodiacKnowledge";

const PILLAR_ICON_SIZE = 20;
const HERO_SYMBOL_SIZE = 80;

export function buildTodayHeroSymbol(coreProfile?: CoreProfile | null): ReactNode {
  const archetypeSeed = coreProfile?.baseline?.archetype_seed?.trim();
  if (archetypeSeed) {
    return createElement(ArchetypeSymbol, {
      seed: archetypeSeed,
      size: HERO_SYMBOL_SIZE,
      stroke: "currentColor",
    });
  }

  const sunSign = coreProfile?.astro?.sun_sign;
  if (sunSign?.trim()) {
    return createElement(ZodiacIcon, {
      sign: sunSign,
      size: HERO_SYMBOL_SIZE,
      stroke: "currentColor",
    });
  }

  return createElement(ArchetypeSymbol, {
    seed: "unknown",
    size: HERO_SYMBOL_SIZE,
    stroke: "currentColor",
  });
}

export function resolveTodaySunSignLabel(coreProfile?: CoreProfile | null): string | null {
  const sunSign = coreProfile?.astro?.sun_sign?.trim();
  if (!sunSign) return null;
  const signId = resolveZodiacSignId(sunSign, null);
  const entry = signId ? getSunInSignEntry(signId) : undefined;
  return entry ? layerSignLabel(entry, sunSign) : sunSign;
}

export function buildTodayHeroPillars(coreProfile?: CoreProfile | null): HeroMediumPillar[] {
  const sunSign = coreProfile?.astro?.sun_sign?.trim();
  if (!sunSign) return [];

  const signId = resolveZodiacSignId(sunSign, null);
  const entry = signId ? getSunInSignEntry(signId) : undefined;
  const label = entry ? `Солнце · ${layerSignLabel(entry, sunSign)}` : `Солнце · ${sunSign}`;

  return [
    {
      id: "sun",
      label,
      icon: createElement(ZodiacIcon, { sign: sunSign, size: PILLAR_ICON_SIZE, stroke: "currentColor" }),
    },
  ];
}
