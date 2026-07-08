/**
 * PR1 — Experience spine S0–S5 (без mood / check-in / evening).
 * Legacy `TodayRitualFlow` по-прежнему использует `isRitualSpineComplete` в `todayRitualPersisted.ts`.
 */

export type ExperienceSpineSlice = {
  tarotMainId: number | null;
  tarotContinueAck: boolean;
  numberRevealed: boolean;
};

/** S4 complete → можно запрашивать S5 DRE. */
export function isExperienceSpineComplete(s: ExperienceSpineSlice): boolean {
  return Boolean(s.tarotMainId != null && s.tarotContinueAck && s.numberRevealed);
}
