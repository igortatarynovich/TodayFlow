/**
 * Defensive display helpers for Today/Profile copy.
 *
 * Meaning rules (system leak, textbook, address mix) live on the backend
 * value gate only. Frontend may hide null / empty / trivial exact duplicates.
 */

function norm(text: string): string {
  return (text ?? "").replace(/\s+/g, " ").trim();
}

function low(text: string): string {
  return norm(text).toLowerCase().replace(/ё/g, "е");
}

/** Defensive: hide null / empty / whitespace-only. Not a meaning gate. */
export function scrubUserFacingText(text: string | null | undefined): string | null {
  const raw = norm(text ?? "");
  return raw || null;
}

/** Exact or near-exact claim overlap for composition dedupe (not a meaning gate). */
export function nearDuplicateClaim(a: string, b: string): boolean {
  const x = low(a).replace(/[^a-zа-яё0-9\s]+/g, " ").replace(/\s+/g, " ").trim();
  const y = low(b).replace(/[^a-zа-яё0-9\s]+/g, " ").replace(/\s+/g, " ").trim();
  if (!x || !y) return false;
  if (x === y) return true;
  if (x.length >= 24 && (x.includes(y) || y.includes(x))) return true;
  const aw = new Set(x.match(/[a-zа-яё0-9]{4,}/g) ?? []);
  const bw = y.match(/[a-zа-яё0-9]{4,}/g) ?? [];
  if (!aw.size || !bw.length) return false;
  const overlap = bw.filter((w) => aw.has(w)).length;
  return overlap >= Math.max(3, Math.ceil(bw.length * 0.55));
}
