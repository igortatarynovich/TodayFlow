/**
 * Wave 2 / Today slots — transport failure copy.
 *
 * Forbidden: invent calm rows, sphere dictionary text, or "no signal" prose
 * when the slot did not load. Say the failure plainly.
 */

export type TodaySlotLoadFailure = "no_connection" | "unavailable";

/** Network / API throw — browser could not complete the request. */
export const TODAY_NO_CONNECTION_COPY = "Нет соединения.";

/** Server answered but flagged degraded / is_fallback — no inventable content. */
export const TODAY_UNAVAILABLE_COPY = "Не удалось загрузить.";

export function todaySlotFailureCopy(reason: TodaySlotLoadFailure): string {
  return reason === "no_connection" ? TODAY_NO_CONNECTION_COPY : TODAY_UNAVAILABLE_COPY;
}
