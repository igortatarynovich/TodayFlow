/**
 * Map day lunar SoT → CelestialMoon.phase (0 = new, 0.5 = full, 1 = new).
 * Prefer continuous cycle_day; discrete id/name only as fill-empty.
 */

export const SYNODIC_PERIOD_DAYS = 29.53058867;

/** Mid-bin angles for astrology_reference moon_phases.json ids (+ aliases). */
const PHASE_ID_TO_UNIT: Record<string, number> = {
  new: 0,
  new_moon: 0,
  waxing_crescent: 0.125,
  first_quarter: 0.25,
  waxing_gibbous: 0.375,
  full: 0.5,
  full_moon: 0.5,
  waning_gibbous: 0.625,
  last_quarter: 0.75,
  third_quarter: 0.75,
  waning_crescent: 0.875,
};

const PHASE_NAME_TO_UNIT: Array<{ re: RegExp; phase: number }> = [
  { re: /новолун/i, phase: 0 },
  { re: /\bnew\s*moon\b/i, phase: 0 },
  { re: /молод(ая|ой)\s*лун/i, phase: 0.125 },
  { re: /waxing\s*crescent/i, phase: 0.125 },
  { re: /перв(ая|ой)\s*четверт/i, phase: 0.25 },
  { re: /first\s*quarter/i, phase: 0.25 },
  { re: /растущ/i, phase: 0.375 },
  { re: /waxing\s*gibbous/i, phase: 0.375 },
  { re: /полнолун/i, phase: 0.5 },
  { re: /\bfull\s*moon\b/i, phase: 0.5 },
  { re: /убывающ/i, phase: 0.625 },
  { re: /waning\s*gibbous/i, phase: 0.625 },
  { re: /последн(яя|ей)\s*четверт|third\s*quarter|last\s*quarter/i, phase: 0.75 },
  { re: /стар(ая|ой)\s*лун|waning\s*crescent/i, phase: 0.875 },
];

function normalizeUnit(t: number): number {
  const x = t % 1;
  return x < 0 ? x + 1 : x;
}

export function celestialPhaseFromCycleDay(cycleDay: number): number {
  return normalizeUnit(cycleDay / SYNODIC_PERIOD_DAYS);
}

export function celestialPhaseFromPhaseId(id: string | null | undefined): number | null {
  const key = String(id || "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "_");
  if (!key) return null;
  const hit = PHASE_ID_TO_UNIT[key];
  return hit === undefined ? null : hit;
}

export function celestialPhaseFromPhaseName(name: string | null | undefined): number | null {
  const raw = String(name || "").trim();
  if (!raw) return null;
  for (const row of PHASE_NAME_TO_UNIT) {
    if (row.re.test(raw)) return row.phase;
  }
  return null;
}

export function resolveCelestialMoonPhase(input: {
  cycleDay?: number | null;
  phaseId?: string | null;
  phaseName?: string | null;
}): number | null {
  const day = input.cycleDay;
  if (typeof day === "number" && Number.isFinite(day)) {
    return celestialPhaseFromCycleDay(day);
  }
  return (
    celestialPhaseFromPhaseId(input.phaseId) ?? celestialPhaseFromPhaseName(input.phaseName) ?? null
  );
}
