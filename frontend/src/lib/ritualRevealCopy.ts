/**
 * Ritual reveal copy helpers — handoff UX on top of existing hook_reveal / impact text.
 * Does not invent SoT meaning; only formats existing lines.
 */

export function formatRitualTarotPersonalToday(input: {
  personalLine: string | null | undefined;
  dayNumber: string | null | undefined;
  dayNumberTitle?: string | null | undefined;
}): string | null {
  const personal = String(input.personalLine ?? "").trim();
  if (!personal) return null;
  const n = String(input.dayNumber ?? "").trim();
  if (!n || n === "—" || n === "-" || n === "…") return personal;
  const title = String(input.dayNumberTitle ?? "").trim();
  const numPart = title ? `числе дня ${n} (${title})` : `числе дня ${n}`;
  return `При ${numPart} эта карта — ${personal}`;
}

type RitualHook = {
  bridge_to_day?: string | null;
  personal_angle?: string | null;
  base?: { meaning?: string | null } | null;
} | null | undefined;

export function pickRitualHookLine(hook: RitualHook, fallback?: string | null): string | null {
  const bridge = String(hook?.bridge_to_day ?? "").trim();
  if (bridge) return bridge;
  const angle = String(hook?.personal_angle ?? "").trim();
  if (angle) return angle;
  const meaning = String(hook?.base?.meaning ?? "").trim();
  if (meaning) return meaning;
  const fb = String(fallback ?? "").trim();
  return fb || null;
}

function normLens(s: string): string {
  return s.replace(/\s+/g, " ").replace(/[.!?]+$/u, "").trim().toLowerCase();
}

/** T2.lens_number — Personal Day × F11/F12 after persist. Not Global chorus tempo/bridge. */
export function pickRitualNumberLens(
  hook: RitualHook,
  allowPersonal: boolean,
): string | null {
  if (!allowPersonal) return null;
  const angle = String(hook?.personal_angle ?? "").trim();
  if (!angle || angle.toLowerCase() === "omit") return null;
  const catalog = String(hook?.base?.meaning ?? "").trim();
  if (catalog && normLens(angle) === normLens(catalog)) return null;
  const bridge = String(hook?.bridge_to_day ?? "").trim();
  if (bridge && normLens(angle) === normLens(bridge)) return null;
  return angle.length <= 280 ? angle : `${angle.slice(0, 280).trim()}`;
}

/** T2.lens_card — Personal Day × F13 after persist. Not Global chorus bridge. */
export function pickRitualCardLens(
  hook: RitualHook,
  allowPersonal: boolean,
): string | null {
  if (!allowPersonal) return null;
  const angle = String(hook?.personal_angle ?? "").trim();
  if (!angle || angle.toLowerCase() === "omit") return null;
  const catalog = String(hook?.base?.meaning ?? "").trim();
  if (catalog && normLens(angle) === normLens(catalog)) return null;
  const bridge = String(hook?.bridge_to_day ?? "").trim();
  if (bridge && normLens(angle) === normLens(bridge)) return null;
  return angle.length <= 280 ? angle : `${angle.slice(0, 280).trim()}`;
}
