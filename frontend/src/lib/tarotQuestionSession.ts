import type { TarotConcernDomain, TarotFlowStep } from "@/lib/tarotQuestionFlowCanon";

const STORAGE_KEY = "todayflow:tarot-question-flow:v1";

export type TarotQuestionSession = {
  sessionId: string;
  step: TarotFlowStep;
  concernDomain: TarotConcernDomain | null;
  refinementId: string | null;
  customQuestion: string;
  spreadId: string | null;
  startedAt: string;
};

function newSessionId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `tarot-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export function createTarotQuestionSession(): TarotQuestionSession {
  return {
    sessionId: newSessionId(),
    step: "hero",
    concernDomain: null,
    refinementId: null,
    customQuestion: "",
    spreadId: null,
    startedAt: new Date().toISOString(),
  };
}

export function readTarotQuestionSession(): TarotQuestionSession | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as TarotQuestionSession;
    if (!parsed?.sessionId) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function writeTarotQuestionSession(session: TarotQuestionSession): void {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  } catch {
    /* quota / private mode */
  }
}

export function patchTarotQuestionSession(patch: Partial<TarotQuestionSession>): TarotQuestionSession {
  const base = readTarotQuestionSession() ?? createTarotQuestionSession();
  const next = { ...base, ...patch };
  writeTarotQuestionSession(next);
  return next;
}

export function clearTarotQuestionSession(): void {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    /* noop */
  }
}
