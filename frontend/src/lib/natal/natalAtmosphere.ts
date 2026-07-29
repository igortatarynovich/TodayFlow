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

/**
 * Atmosphere tint for Decode-layer natal stage — from Sun sign element when known.
 */
export function resolveNatalAtmosphereElement(
  sunSign?: string | null,
): NatalAtmosphereElement {
  const entry = getZodiacEntry(normalizeSignId(sunSign));
  const raw = String(entry?.element || "")
    .trim()
    .toLowerCase();
  return RU_TO_EL[raw] || "earth";
}

export function sunSignFromPositions(
  positions: Array<{ body?: string; sign?: string }> | null | undefined,
): string | null {
  if (!positions?.length) return null;
  const sun = positions.find((p) => String(p.body || "").toLowerCase() === "sun");
  return sun?.sign?.trim() || null;
}
