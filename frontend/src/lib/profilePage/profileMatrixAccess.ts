/** Profile Availability matrix 3.1 — client helpers for reveal vs data eligibility. */

import type { CoreProfile } from "@/lib/types";

export const PROFILE_SLOT_HELPS = "helps";
export const PROFILE_SLOT_IDENTITY = "identity_summary";
export const PROFILE_SLOT_LIMITATIONS = "limitations";

export function profileSlotRevealed(core: CoreProfile | null | undefined, slotId: string): boolean {
  const meta = core?.capability?.profile_slots;
  if (!meta) {
    // Legacy payloads without capability: keep prior surface behavior.
    return true;
  }
  const revealed = meta.revealed ?? meta.allowed ?? [];
  return revealed.includes(slotId);
}

export function profileSlotInResult(core: CoreProfile | null | undefined, slotId: string): boolean {
  const meta = core?.capability?.profile_slots;
  if (!meta) return true;
  const eligible = meta.data_eligible ?? meta.revealed ?? meta.allowed ?? [];
  return eligible.includes(slotId);
}

export function profileUserMessages(
  core: CoreProfile | null | undefined,
): Array<{ code: string; text: string }> {
  const fromCap = core?.capability?.user_messages;
  const fromMatrix = core?.profile_matrix_v0?.capability?.user_messages;
  const raw = (fromCap && fromCap.length ? fromCap : fromMatrix) ?? [];
  return raw
    .map((m) => ({
      code: String(m?.code || "").trim(),
      text: String(m?.text || "").trim(),
    }))
    .filter((m) => m.text.length > 0);
}

export function profileHelpsLineFromMatrix(core: CoreProfile | null | undefined): string | null {
  if (!profileSlotRevealed(core, PROFILE_SLOT_HELPS)) return null;
  const revealed = core?.profile_matrix_v0?.revealed_slots?.helps;
  if (typeof revealed === "string" && revealed.trim()) return revealed.trim();
  if (Array.isArray(revealed) && revealed.length) {
    const first = revealed.find((x) => typeof x === "string" && String(x).trim());
    if (first) return String(first).trim();
  }
  return null;
}
