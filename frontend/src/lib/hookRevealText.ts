/**
 * Safe text helpers for hook_reveal nests.
 * BE props.color.where_to_use is an object — never call .trim() on it raw.
 */

const WHERE_KEYS = ["clothing", "accessory", "workspace", "makeup", "ui_or_bg"] as const;

/** True for leaked machine ids like ``conflict.intensity_without_drama``. */
export function isMachineToken(value: string): boolean {
  const t = value.trim();
  if (!t) return false;
  if (/[А-Яа-яЁё]/.test(t) || /\s/.test(t)) return false;
  const lower = t.toLowerCase();
  if (lower.startsWith("conflict.")) return true;
  if (lower.includes(".") && /^[a-z0-9_.]+$/.test(lower)) return true;
  if (lower.includes("_") && /^[a-z0-9_]+$/.test(lower)) return true;
  return false;
}

/** Trim only real strings; never throw on objects/numbers. */
export function asTrimmedText(value: unknown): string | null {
  if (typeof value === "string") {
    const t = value.trim();
    if (!t || isMachineToken(t)) return null;
    return t;
  }
  return null;
}

/** Format day_scenario.props.color.where_to_use (object or string) for UI.

 * One concrete tip — clothing first, then accessory/workspace/… No «шарф · стикер» mash.
 */
export function formatColorWhereToUse(value: unknown): string | null {
  const asString = asTrimmedText(value);
  if (asString) return asString;
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  const row = value as Record<string, unknown>;
  for (const k of WHERE_KEYS) {
    const part = asTrimmedText(row[k]);
    if (part) return part;
  }
  return null;
}
