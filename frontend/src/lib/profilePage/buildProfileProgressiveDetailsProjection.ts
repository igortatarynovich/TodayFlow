/**
 * Explore-fold materials from matrix revealed_slots.
 * Not Profile Journey IA — catalog, natal, styles, unused character lists.
 */
import type { CoreProfile } from "@/lib/types";
import {
  PROFILE_SLOT_HELPS,
  profileUserMessages,
} from "@/lib/profilePage/profileMatrixAccess";

export { PROFILE_SLOT_HELPS };

export const PROFILE_SLOT_CATALOG = "cultural_catalog";
export const PROFILE_SLOT_NAME = "name_numerology";
export const PROFILE_SLOT_NATAL = "natal_structure";
export const PROFILE_SLOT_EMOTIONAL = "emotional_style";
export const PROFILE_SLOT_DECISION = "decision_style";
export const PROFILE_SLOT_RELATIONSHIP = "relationship_style";
export const PROFILE_SLOT_WORK = "work_and_realization";
export const PROFILE_SLOT_MONEY = "money_patterns";
export const PROFILE_SLOT_HOME = "home_and_security";
export const PROFILE_SLOT_STRENGTHS = "strengths";
export const PROFILE_SLOT_TENSIONS = "tensions_growth";

/** Explore-only slot order — never primary Journey scroll. */
export const PROGRESSIVE_DETAILS_SLOT_ORDER = [
  PROFILE_SLOT_CATALOG,
  PROFILE_SLOT_NAME,
  PROFILE_SLOT_NATAL,
  PROFILE_SLOT_EMOTIONAL,
  PROFILE_SLOT_DECISION,
  PROFILE_SLOT_RELATIONSHIP,
  PROFILE_SLOT_WORK,
  PROFILE_SLOT_MONEY,
  PROFILE_SLOT_HOME,
  PROFILE_SLOT_STRENGTHS,
  PROFILE_SLOT_TENSIONS,
  PROFILE_SLOT_HELPS,
] as const;

export type ProgressiveDetailKind =
  | "catalog"
  | "name_numerology"
  | "natal_structure"
  | "style"
  | "strengths"
  | "tensions"
  | "helps";

export type ProgressiveDetailItem = {
  id: string;
  kind: ProgressiveDetailKind;
  label: string;
  lines: string[];
  payload: unknown;
};

export type ProgressiveDetailsProjection = {
  hasMatrix: boolean;
  items: ProgressiveDetailItem[];
  userMessages: Array<{ code: string; text: string }>;
  accessGatedHelps: boolean;
};

const STYLE_LABELS: Record<string, string> = {
  [PROFILE_SLOT_EMOTIONAL]: "Эмоции",
  [PROFILE_SLOT_DECISION]: "Решения",
  [PROFILE_SLOT_RELATIONSHIP]: "Близость",
  [PROFILE_SLOT_WORK]: "Работа",
  [PROFILE_SLOT_MONEY]: "Деньги",
  [PROFILE_SLOT_HOME]: "Дом",
};

function asLines(value: unknown): string[] {
  if (typeof value === "string" && value.trim()) return [value.trim()];
  if (Array.isArray(value)) {
    return value
      .map((x) => (typeof x === "string" ? x.trim() : ""))
      .filter(Boolean);
  }
  if (value && typeof value === "object") {
    const o = value as Record<string, unknown>;
    for (const key of ["text", "summary", "line", "value"]) {
      if (typeof o[key] === "string" && String(o[key]).trim()) {
        return [String(o[key]).trim()];
      }
    }
  }
  return [];
}

function isEmpty(value: unknown): boolean {
  if (value == null) return true;
  if (typeof value === "string") return !value.trim();
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === "object") {
    return Object.values(value as Record<string, unknown>).every(
      (v) => v == null || v === "" || (Array.isArray(v) && v.length === 0),
    );
  }
  return false;
}

function catalogLines(bag: unknown): string[] {
  if (!bag || typeof bag !== "object") return [];
  const o = bag as Record<string, unknown>;
  const lines: string[] = [];
  const traditions = Array.isArray(o.traditions) ? o.traditions : [];
  for (const t of traditions) {
    if (!t || typeof t !== "object") continue;
    const row = t as Record<string, unknown>;
    const label = String(row.label || "").trim();
    const value = String(row.value || "").trim();
    if (label && value) lines.push(`${label}: ${value}`);
  }
  if (o.color) lines.push(`Цвет знака: ${String(o.color)}`);
  const stones = Array.isArray(o.stones) ? o.stones : [];
  const stoneLabels = stones
    .map((s) => {
      if (typeof s === "string") return s;
      if (s && typeof s === "object" && "label" in s) {
        return String((s as { label?: unknown }).label || "");
      }
      return "";
    })
    .filter(Boolean);
  if (stoneLabels.length) lines.push(`Камни знака: ${stoneLabels.join(", ")}`);
  return lines;
}

function natalLines(bag: unknown): string[] {
  if (!bag || typeof bag !== "object") return [];
  const o = bag as Record<string, unknown>;
  const angles =
    o.angles && typeof o.angles === "object"
      ? (o.angles as Record<string, unknown>)
      : {};
  const lines: string[] = [];
  const asc = angles.ascendant;
  if (asc && typeof asc === "object") {
    const a = asc as Record<string, unknown>;
    if (a.sign) lines.push(`Асцендент: ${String(a.sign)}`);
  }
  const mc = angles.mc;
  if (mc && typeof mc === "object") {
    const m = mc as Record<string, unknown>;
    if (m.sign) lines.push(`MC: ${String(m.sign)}`);
  }
  // Omit technical cusp counts — not human-facing explore copy.
  return lines;
}

function tensionLines(bag: unknown): string[] {
  if (Array.isArray(bag)) return asLines(bag);
  if (!bag || typeof bag !== "object") return [];
  const o = bag as Record<string, unknown>;
  return [
    ...asLines(o.growth_zones),
    ...asLines(o.internal_tensions),
    ...asLines(o.blind_spots),
  ];
}

function kindFor(slotId: string): ProgressiveDetailKind {
  if (slotId === PROFILE_SLOT_CATALOG) return "catalog";
  if (slotId === PROFILE_SLOT_NAME) return "name_numerology";
  if (slotId === PROFILE_SLOT_NATAL) return "natal_structure";
  if (slotId === PROFILE_SLOT_STRENGTHS) return "strengths";
  if (slotId === PROFILE_SLOT_TENSIONS) return "tensions";
  if (slotId === PROFILE_SLOT_HELPS) return "helps";
  return "style";
}

function labelFor(slotId: string): string {
  if (slotId === PROFILE_SLOT_CATALOG) return "Традиции и соответствия";
  if (slotId === PROFILE_SLOT_NAME) return "Числа имени";
  if (slotId === PROFILE_SLOT_NATAL) return "Структура карты";
  if (slotId === PROFILE_SLOT_STRENGTHS) return "Сильные стороны";
  if (slotId === PROFILE_SLOT_TENSIONS) return "Напряжения и рост";
  if (slotId === PROFILE_SLOT_HELPS) return "Что помогает";
  return STYLE_LABELS[slotId] || slotId;
}

function linesFor(slotId: string, value: unknown): string[] {
  if (slotId === PROFILE_SLOT_CATALOG) return catalogLines(value);
  if (slotId === PROFILE_SLOT_NATAL) return natalLines(value);
  if (slotId === PROFILE_SLOT_TENSIONS) return tensionLines(value);
  if (slotId === PROFILE_SLOT_NAME && value && typeof value === "object") {
    const o = value as Record<string, unknown>;
    const parts: string[] = [];
    if (o.expression != null) parts.push(`выражение ${o.expression}`);
    if (o.soul_urge != null) parts.push(`душа ${o.soul_urge}`);
    if (o.personality != null) parts.push(`личность ${o.personality}`);
    return parts.length ? [parts.join(" · ")] : [];
  }
  return asLines(value);
}

export type ProgressiveDetailsOptions = {
  /** Slot ids already consumed by the insight node — omit duplicate lists. */
  omitSlotIds?: string[];
};

/**
 * Build explore-fold items from revealed_slots only.
 * Empty bags omitted. Access-gated slots are not in revealed_slots.
 */
export function buildProfileProgressiveDetailsProjection(
  core: CoreProfile | null | undefined,
  opts?: ProgressiveDetailsOptions,
): ProgressiveDetailsProjection {
  const revealed = core?.profile_matrix_v0?.revealed_slots;
  const hasMatrix = Boolean(revealed && typeof revealed === "object");
  const userMessages = profileUserMessages(core);
  const accessGatedHelps = Boolean(
    core?.profile_matrix_v0?.access_gated_slot_ids?.includes(PROFILE_SLOT_HELPS) ||
      userMessages.some((m) => m.code === "l3_gated"),
  );
  const omit = new Set(opts?.omitSlotIds ?? []);

  if (!hasMatrix || !revealed) {
    return {
      hasMatrix: false,
      items: [],
      userMessages,
      accessGatedHelps,
    };
  }

  const items: ProgressiveDetailItem[] = [];
  for (const slotId of PROGRESSIVE_DETAILS_SLOT_ORDER) {
    if (omit.has(slotId)) continue;
    if (!(slotId in revealed)) continue;
    const value = revealed[slotId];
    if (isEmpty(value)) continue;
    const lines = linesFor(slotId, value);
    if (!lines.length && slotId !== PROFILE_SLOT_CATALOG) continue;
    items.push({
      id: slotId,
      kind: kindFor(slotId),
      label: labelFor(slotId),
      lines,
      payload: value,
    });
  }

  return {
    hasMatrix: true,
    items,
    userMessages,
    accessGatedHelps,
  };
}
