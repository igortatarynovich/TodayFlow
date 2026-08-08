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

export function pickRitualHookLine(
  hook:
    | {
        bridge_to_day?: string | null;
        personal_angle?: string | null;
        base?: { meaning?: string | null } | null;
      }
    | null
    | undefined,
  fallback?: string | null,
): string | null {
  const bridge = String(hook?.bridge_to_day ?? "").trim();
  if (bridge) return bridge;
  const angle = String(hook?.personal_angle ?? "").trim();
  if (angle) return angle;
  const meaning = String(hook?.base?.meaning ?? "").trim();
  if (meaning) return meaning;
  const fb = String(fallback ?? "").trim();
  return fb || null;
}
