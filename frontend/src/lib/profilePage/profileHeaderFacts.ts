/**
 * Compact P2 header facts for PIC-K13 / PIC-K14.
 * Not journey acts. Not Identity Core. Lookup only.
 */
import type { CoreProfile } from "@/lib/types";

export type ProfileHeaderFact = {
  slot_id: "P2.correspondence" | "P2.name_numerology";
  text: string;
};

function trim(value: unknown): string {
  return String(value ?? "").trim();
}

function revealedBag(core: CoreProfile | null | undefined, slot: string): unknown {
  const revealed = core?.profile_matrix_v0?.revealed_slots;
  if (!revealed || typeof revealed !== "object") return null;
  return (revealed as Record<string, unknown>)[slot];
}

function correspondenceLine(bag: unknown): string {
  if (!bag || typeof bag !== "object") return "";
  const o = bag as Record<string, unknown>;
  const parts: string[] = [];
  if (o.color) parts.push(trim(o.color));
  const stones = Array.isArray(o.stones) ? o.stones : [];
  const stone = stones
    .map((s) => {
      if (typeof s === "string") return s.trim();
      if (s && typeof s === "object" && "label" in s) return trim((s as { label?: unknown }).label);
      return "";
    })
    .find(Boolean);
  if (stone) parts.push(stone);
  const traditions = Array.isArray(o.traditions) ? o.traditions : [];
  for (const t of traditions) {
    if (!t || typeof t !== "object") continue;
    const row = t as Record<string, unknown>;
    const value = trim(row.value);
    if (value) parts.push(value);
    if (parts.length >= 3) break;
  }
  return parts.join(" · ");
}

function nameNumerologyLine(bag: unknown): string {
  if (!bag || typeof bag !== "object") return "";
  const o = bag as Record<string, unknown>;
  const bits: string[] = [];
  if (o.expression_number != null) bits.push(`выражение ${o.expression_number}`);
  if (o.soul_urge_number != null) bits.push(`душа ${o.soul_urge_number}`);
  if (o.personality_number != null) bits.push(`образ ${o.personality_number}`);
  if (!bits.length) return "";
  return `Числа имени: ${bits.join(" · ")}`;
}

export function profileHeaderFacts(core: CoreProfile | null | undefined): ProfileHeaderFact[] {
  const out: ProfileHeaderFact[] = [];
  const correspondence = correspondenceLine(revealedBag(core, "cultural_catalog"));
  if (correspondence) {
    out.push({ slot_id: "P2.correspondence", text: correspondence });
  }
  const name = nameNumerologyLine(revealedBag(core, "name_numerology"));
  if (name) {
    out.push({ slot_id: "P2.name_numerology", text: name });
  }
  return out;
}
