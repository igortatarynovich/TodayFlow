/**
 * Wave 2 / Today slots — transport failure copy.
 *
 * Forbidden: invent calm rows, sphere dictionary text, or "no signal" prose
 * when the slot did not load. Say the failure plainly.
 */

import { ApiError, isRequestAborted, isTransportFailure } from "@/lib/api";

export type TodaySlotLoadFailure = "no_connection" | "unavailable";

/** Network / API throw — browser could not complete the request. */
export const TODAY_NO_CONNECTION_COPY = "Нет соединения.";

/** Server answered but flagged degraded / is_fallback — no inventable content. */
export const TODAY_UNAVAILABLE_COPY = "Не удалось загрузить.";

export function isHonestUnavailableCopy(value: string | null | undefined): boolean {
  const t = String(value || "")
    .replace(/\s+/g, " ")
    .trim();
  if (!t) return false;
  return t === TODAY_UNAVAILABLE_COPY || t === TODAY_NO_CONNECTION_COPY;
}

export function todaySlotFailureCopy(reason: TodaySlotLoadFailure): string {
  return reason === "no_connection" ? TODAY_NO_CONNECTION_COPY : TODAY_UNAVAILABLE_COPY;
}

function isTimeoutLike(error: unknown): boolean {
  if (typeof DOMException !== "undefined" && error instanceof DOMException) {
    if (error.name === "TimeoutError") return true;
  }
  if (error instanceof Error && error.name === "TimeoutError") return true;
  const message =
    error instanceof Error
      ? error.message
      : typeof error === "string"
        ? error
        : "";
  const lower = message.toLowerCase();
  return lower.includes("timeout") || lower.includes("timed out");
}

/**
 * Map day-facts / slot fetch rejection → failure kind.
 * Remount/navigation AbortError → null (caller should not paint).
 * Client timeouts and transport failures → no_connection (never leave a slot spinning).
 * Auth / 5xx → unavailable. Auth errors ≠ "no connection".
 */
export function todaySlotFailureFromError(error: unknown): TodaySlotLoadFailure | null {
  // fetchDayFacts aborts with TimeoutError / "Request timed out." — that is a
  // visible failure. isRequestAborted() also matches those; check timeout first
  // or the pane stays data-loading forever.
  if (isTimeoutLike(error)) return "unavailable";
  if (isRequestAborted(error)) return null;
  if (error instanceof ApiError) {
    if (error.status === 0) return "no_connection";
    if (error.status === 401 || error.status === 403) return "unavailable";
    if (error.status >= 500) return "unavailable";
    return "unavailable";
  }
  if (isTransportFailure(error)) return "no_connection";
  return "unavailable";
}
