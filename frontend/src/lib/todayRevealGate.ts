/**
 * P0.2 — gate user-facing card name / day number until ritual reveal completes.
 * Values may exist in state/API; UI must not render them before the gate opens.
 */

export function canShowTarotCardName(tarotMainId: number | null): boolean {
  return tarotMainId != null;
}

export function canShowDayNumber(numberRevealed: boolean): boolean {
  return numberRevealed;
}

/** Синтез «Твой день» — только после обоих reveal (карта ack + число). */
export function canShowTodaySynthesis(input: {
  tarotContinueAck: boolean;
  numberRevealed: boolean;
}): boolean {
  return input.tarotContinueAck && input.numberRevealed;
}
