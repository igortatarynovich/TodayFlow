import { getZodiacEntry, normalizeSignId } from "@/lib/zodiacKnowledge";

export type NatalAtmosphereElement = "fire" | "earth" | "air" | "water";

const RU_TO_EL: Record<string, NatalAtmosphereElement> = {
  огонь: "fire",
  fire: "fire",
  земля: "earth",
  earth: "earth",
  воздух: "air",
  air: "air",
  вода: "water",
  water: "water",
};

/** Jewel rim + soft bloom for planet discs — by sign element, not planet identity alone. */
export type NatalPlanetJewelStyle = {
  element: NatalAtmosphereElement;
  stroke: string;
  glow: string;
  wash: string;
};

const ELEMENT_JEWEL: Record<NatalAtmosphereElement, Omit<NatalPlanetJewelStyle, "element">> = {
  fire: {
    stroke: "#c4782a",
    glow: "rgba(196, 120, 42, 0.42)",
    wash: "rgba(255, 186, 110, 0.38)",
  },
  earth: {
    stroke: "#8b6a3e",
    glow: "rgba(139, 106, 62, 0.38)",
    wash: "rgba(210, 180, 130, 0.32)",
  },
  air: {
    stroke: "#6a849e",
    glow: "rgba(74, 93, 115, 0.4)",
    wash: "rgba(170, 198, 220, 0.34)",
  },
  water: {
    stroke: "#5a7a8c",
    glow: "rgba(72, 110, 132, 0.42)",
    wash: "rgba(130, 175, 200, 0.36)",
  },
};

function elementFromSign(sign?: string | null): NatalAtmosphereElement | null {
  const entry = getZodiacEntry(normalizeSignId(sign));
  const raw = String(entry?.element || "")
    .trim()
    .toLowerCase();
  return RU_TO_EL[raw] || null;
}

/**
 * Atmosphere tint for Decode-layer natal stage — from Sun sign element when known.
 */
export function resolveNatalAtmosphereElement(
  sunSign?: string | null,
): NatalAtmosphereElement {
  return elementFromSign(sunSign) || "earth";
}

/** Per-planet jewel tint from the sign the body occupies. */
export function resolveNatalPlanetJewel(sign?: string | null): NatalPlanetJewelStyle | null {
  const element = elementFromSign(sign);
  if (!element) return null;
  return { element, ...ELEMENT_JEWEL[element] };
}

export function sunSignFromPositions(
  positions: Array<{ body?: string; sign?: string }> | null | undefined,
): string | null {
  if (!positions?.length) return null;
  const sun = positions.find((p) => String(p.body || "").toLowerCase() === "sun");
  return sun?.sign?.trim() || null;
}
