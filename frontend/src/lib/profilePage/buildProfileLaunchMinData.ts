import {
  buildPairCompatibilityRoute,
  type CompatibilityProfileLike,
} from "@/lib/compatibilityRoutes";
import type { PlanetInSignEntry } from "@/lib/zodiacKnowledge";

export type ProfileChartTeaserLine = {
  id: string;
  label: string;
  body: string;
};

export type ProfileCompatibilityPerson = {
  id: number;
  label: string;
  href: string;
};

function pillarSentence(layer: PlanetInSignEntry | null | undefined, fallback: string) {
  const line = layer?.bullets?.[0]?.trim();
  return line || fallback;
}

function isSelfProfile(profile: CompatibilityProfileLike, primaryProfileId?: number | null) {
  if (profile.relation === "self" || profile.is_primary) return true;
  if (primaryProfileId && profile.id === primaryProfileId) return true;
  return false;
}

export function buildProfileChartTeaserLines(input: {
  sunLayer: PlanetInSignEntry | null | undefined;
  moonLayer: PlanetInSignEntry | null | undefined;
  risingLayer: PlanetInSignEntry | null | undefined;
  risingHint: string;
}): ProfileChartTeaserLine[] {
  return [
    {
      id: "sun",
      label: "Солнце",
      body: pillarSentence(input.sunLayer, ""),
    },
    {
      id: "moon",
      label: "Луна",
      body: pillarSentence(input.moonLayer, ""),
    },
    {
      id: "rising",
      label: "Асцендент",
      body: pillarSentence(input.risingLayer, input.risingHint),
    },
  ].filter((line) => line.body.trim());
}

export function buildProfileCompatibilityPeople(
  profiles: CompatibilityProfileLike[],
  primaryProfileId?: number | null,
): ProfileCompatibilityPerson[] {
  return profiles
    .filter((profile) => !isSelfProfile(profile, primaryProfileId))
    .map((profile) => {
      const route = buildPairCompatibilityRoute(profile, primaryProfileId);
      return {
        id: profile.id,
        label: profile.label,
        href: route.href,
      };
    });
}
