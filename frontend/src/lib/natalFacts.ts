/** NatalChartFacts — client types for Generation Contract natal_facts. */

export type NatalFactAngle = {
  sign: string;
  degree?: number;
  absolute_longitude?: number;
} | null;

export type NatalFactPlanet = {
  id: string;
  sign: string;
  degree?: number;
  absolute_longitude?: number;
  house?: number | null;
  retrograde?: boolean | null;
};

export type NatalUnavailableFact = {
  key: string;
  reason: string;
};

export type NatalChartFacts = {
  contract_version: string;
  provider: string;
  provider_version?: string;
  calculation_id?: string;
  house_system?: string | null;
  zodiac?: string;
  mode: "date_only" | "full" | string;
  confidence?: number;
  planets: NatalFactPlanet[];
  angles?: {
    ascendant?: NatalFactAngle;
    mc?: NatalFactAngle;
    ic?: NatalFactAngle;
    descendant?: NatalFactAngle;
  };
  houses?: Array<{ house: number; sign: string; degree?: number; absolute_longitude?: number }>;
  aspects?: unknown[];
  unavailable_facts?: NatalUnavailableFact[];
  prompt_id?: string;
  prompt_version?: string;
};

export type NatalFactsApiResponse = {
  available_input: Record<string, unknown>;
  natal_facts: NatalChartFacts;
};

export function planetSignFromFacts(facts: NatalChartFacts | null | undefined, id: string): string | null {
  if (!facts?.planets?.length) return null;
  const hit = facts.planets.find((p) => p.id.toLowerCase() === id.toLowerCase());
  return hit?.sign ?? null;
}

export function limitationsFromNatalFacts(facts: NatalChartFacts | null | undefined): string[] {
  if (!facts?.unavailable_facts?.length) return [];
  const labels: Record<string, string> = {
    ascendant: "Асцендент",
    houses: "Дома",
    mc: "MC",
    ic: "IC",
    descendant: "Десцендент",
    moon: "Луна (точнее со временем)",
  };
  return facts.unavailable_facts
    .map((u) => labels[u.key] || u.key)
    .filter((v, i, arr) => arr.indexOf(v) === i);
}
