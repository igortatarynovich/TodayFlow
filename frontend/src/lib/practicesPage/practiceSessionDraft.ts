/**
 * In-progress practice session draft — powers hub «Продолжить» (canon §3.2).
 * Client-only until a server resume API exists.
 */

export const PRACTICE_SESSION_DRAFT_KEY = "todayflow_practice_session_draft_v1";

export type PracticeSessionDraft = {
  practiceId: string;
  title: string;
  durationMinutes: number;
  /** Elapsed active seconds (excluding paused time). */
  elapsedSeconds: number;
  updatedAt: string;
};

function isBrowser(): boolean {
  return typeof window !== "undefined";
}

export function readPracticeSessionDraft(): PracticeSessionDraft | null {
  if (!isBrowser()) return null;
  try {
    const raw = localStorage.getItem(PRACTICE_SESSION_DRAFT_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as PracticeSessionDraft;
    if (!parsed?.practiceId || !parsed.title) return null;
    if (!Number.isFinite(parsed.durationMinutes) || parsed.durationMinutes <= 0) return null;
    if (!Number.isFinite(parsed.elapsedSeconds) || parsed.elapsedSeconds < 0) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function writePracticeSessionDraft(draft: PracticeSessionDraft): void {
  if (!isBrowser()) return;
  localStorage.setItem(
    PRACTICE_SESSION_DRAFT_KEY,
    JSON.stringify({ ...draft, updatedAt: new Date().toISOString() }),
  );
}

export function clearPracticeSessionDraft(practiceId?: string): void {
  if (!isBrowser()) return;
  if (practiceId) {
    const current = readPracticeSessionDraft();
    if (current && current.practiceId !== practiceId) return;
  }
  localStorage.removeItem(PRACTICE_SESSION_DRAFT_KEY);
}

export type PracticeStateAfter = "better" | "same" | "harder";

export function isPracticeStateAfter(value: string): value is PracticeStateAfter {
  return value === "better" || value === "same" || value === "harder";
}
