import type { AspectCallout } from "@/lib/types";

export type HouseInterpretation = {
  name: string;
  theme: string;
  description: string;
};

export type LifeMapSection = {
  house: number;
  title: string;
  routeTitle: string;
  href: string;
  accent: string;
  summary: string;
};

export type NatalChartPreview = {
  positions: Record<string, { longitude?: number; sign?: string; house?: number; degree?: number }>;
  houses: Array<{ house: number; cusp_longitude?: number; sign?: string; degree?: number }>;
  ascendant?: { longitude?: number; sign?: string; degree?: number };
  mode?: string;
  time_unknown?: boolean;
  ascendant_precision?: string;
  aspects?: {
    callouts?: AspectCallout[];
  };
  interpretations?: {
    houses?: Record<number, HouseInterpretation>;
  };
};

export type CombinedPlanetaryProfile = {
  placements: Array<{
    key: "sun" | "moon" | "venus" | "mars" | "mercury" | "rising" | "jupiter" | "saturn" | "uranus" | "neptune" | "pluto";
    label: string;
    signLabel: string;
  }>;
  recognition: string;
  explanation: string;
  tension: string;
  strength: string;
  manifestation: string;
  risk: string;
  lifeVector: string;
  expressionLine: string;
  mind: string;
  firstContact: string;
  growthLine: string;
  constraintLine: string;
  rebellionLine: string;
  magicLine: string;
  transformationLine: string;
  manifestationAreas: Array<{
    planet: string;
    signLabel: string;
    house: number;
    houseTitle: string;
    text: string;
  }>;
  houseFocus: {
    house: number;
    title: string;
    text: string;
    planets: string[];
  } | null;
  aspectInsights: Array<{
    key: string;
    title: string;
    category: "fusion" | "tension" | "polarity" | "strength" | "potential";
    text: string;
    bodies: string;
  }>;
  aspectSummary: {
    coherence: string;
    conflict: string;
    advantage: string;
    selfBlock: string;
  } | null;
  scenarios: Array<{
    id: string;
    title: string;
    summary: string;
    evidence: string[];
    bullets: string[];
    reading: string[];
    layers: Array<{
      label: string;
      reason: string;
    }>;
  }>;
};
