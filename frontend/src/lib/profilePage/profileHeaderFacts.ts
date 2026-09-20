/**
 * Compact P2 header facts for PIC-K13 / PIC-K14.
 * Not journey acts. Not Identity Core. Lookup only.
 *
 * K13 Matrix bag (producer `core_profile`): `expression` · `soul_urge` · `personality`.
 * `*_number` aliases are read-only fallbacks, not the live write shape.
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

function pickNameNumber(bag: Record<string, unknown>, keys: string[]): string {
  for (const key of keys) {
    const raw = bag[key];
    if (raw == null || raw === "") continue;
    const n = Number(raw);
    if (Number.isFinite(n)) return String(n);
    const text = trim(raw);
    if (text) return text;
  }
  return "";
}

function nameNumerologyLine(bag: unknown): string {
  if (!bag || typeof bag !== "object") return "";
  const o = bag as Record<string, unknown>;
  const bits: string[] = [];
  const expression = pickNameNumber(o, ["expression", "expression_number"]);
  const soul = pickNameNumber(o, ["soul_urge", "soul_urge_number"]);
  const personality = pickNameNumber(o, ["personality", "personality_number"]);
  if (expression) bits.push(`выражение ${expression}`);
  if (soul) bits.push(`душа ${soul}`);
  if (personality) bits.push(`образ ${personality}`);
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
