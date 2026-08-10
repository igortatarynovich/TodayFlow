/**
 * Persist handoff day promise into Day Connection `morning_intention` (B2 SoT bridge).
 * Fire-and-forget — local engagement remains primary UX store.
 */

import { postJson } from "@/lib/api";

export async function syncDayPromiseToConnection(
  dateISO: string,
  promiseText: string,
): Promise<void> {
  const text = promiseText.replace(/\s+/g, " ").trim();
  if (!dateISO || !text) return;
  try {
    await postJson(`/day-connection/${encodeURIComponent(dateISO)}`, {
      morning_intention: text.slice(0, 500),
      morning_completed: true,
    });
  } catch {
    /* transport — engagement already saved; evening can still read CUM */
  }
}
