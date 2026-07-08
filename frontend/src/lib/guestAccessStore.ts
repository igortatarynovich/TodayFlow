import { GUEST_ACCESS_LIMITS } from "@/lib/guestAccessLimits";
import { VALUE_FIRST_PATHS } from "@/lib/guestProfileDraft";

const STORAGE_KEY = "todayflow_guest_access_v1";

export type GuestAccessState = {
  version: 1;
  tarotSpreadsUsed: number;
  compatibilityChecksUsed: number;
  consumedTarotSessions: string[];
  consumedCompatibilityKeys: string[];
};

export type GuestPracticeLike = {
  is_free: boolean;
  is_personalized?: boolean;
  access_level?: string;
};

function emptyState(): GuestAccessState {
  return {
    version: 1,
    tarotSpreadsUsed: 0,
    compatibilityChecksUsed: 0,
    consumedTarotSessions: [],
    consumedCompatibilityKeys: [],
  };
}

function normalizeState(raw: unknown): GuestAccessState {
  if (!raw || typeof raw !== "object") return emptyState();
  const value = raw as Partial<GuestAccessState>;
  return {
    version: 1,
    tarotSpreadsUsed: Math.max(0, Number(value.tarotSpreadsUsed) || 0),
    compatibilityChecksUsed: Math.max(0, Number(value.compatibilityChecksUsed) || 0),
    consumedTarotSessions: Array.isArray(value.consumedTarotSessions)
      ? value.consumedTarotSessions.filter((item): item is string => typeof item === "string")
      : [],
    consumedCompatibilityKeys: Array.isArray(value.consumedCompatibilityKeys)
      ? value.consumedCompatibilityKeys.filter((item): item is string => typeof item === "string")
      : [],
  };
}

export function readGuestAccessState(): GuestAccessState {
  if (typeof window === "undefined") return emptyState();
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return emptyState();
    return normalizeState(JSON.parse(raw));
  } catch {
    return emptyState();
  }
}

function writeGuestAccessState(state: GuestAccessState): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

export function guestSignupHref(): string {
  return `${VALUE_FIRST_PATHS.welcome}?fresh=1`;
}

export function guestTarotRemaining(): number {
  const state = readGuestAccessState();
  return Math.max(0, GUEST_ACCESS_LIMITS.tarotSpreads - state.tarotSpreadsUsed);
}

export function guestCompatibilityRemaining(): number {
  const state = readGuestAccessState();
  return Math.max(0, GUEST_ACCESS_LIMITS.compatibilityChecks - state.compatibilityChecksUsed);
}

export function isGuestTarotLimitReached(): boolean {
  return guestTarotRemaining() <= 0;
}

export function isGuestCompatibilityLimitReached(): boolean {
  return guestCompatibilityRemaining() <= 0;
}

/** New spread allowed, or reopening an already consumed session. */
export function canGuestAccessTarotSpread(sessionKey: string): boolean {
  const state = readGuestAccessState();
  if (state.consumedTarotSessions.includes(sessionKey)) return true;
  return state.tarotSpreadsUsed < GUEST_ACCESS_LIMITS.tarotSpreads;
}

export function canGuestAccessCompatibility(checkKey: string): boolean {
  const state = readGuestAccessState();
  if (state.consumedCompatibilityKeys.includes(checkKey)) return true;
  return state.compatibilityChecksUsed < GUEST_ACCESS_LIMITS.compatibilityChecks;
}

export function tryConsumeGuestTarotSpread(sessionKey: string): boolean {
  const state = readGuestAccessState();
  if (state.consumedTarotSessions.includes(sessionKey)) return true;
  if (state.tarotSpreadsUsed >= GUEST_ACCESS_LIMITS.tarotSpreads) return false;
  writeGuestAccessState({
    ...state,
    tarotSpreadsUsed: state.tarotSpreadsUsed + 1,
    consumedTarotSessions: [...state.consumedTarotSessions, sessionKey],
  });
  return true;
}

export function tryConsumeGuestCompatibility(checkKey: string): boolean {
  const state = readGuestAccessState();
  if (state.consumedCompatibilityKeys.includes(checkKey)) return true;
  if (state.compatibilityChecksUsed >= GUEST_ACCESS_LIMITS.compatibilityChecks) return false;
  writeGuestAccessState({
    ...state,
    compatibilityChecksUsed: state.compatibilityChecksUsed + 1,
    consumedCompatibilityKeys: [...state.consumedCompatibilityKeys, checkKey],
  });
  return true;
}

export function buildCompatibilityCheckKey(parts: Record<string, string | undefined | null>): string {
  return Object.entries(parts)
    .filter(([, value]) => Boolean(value?.trim()))
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([key, value]) => `${key}:${String(value).trim().toLowerCase()}`)
    .join("|");
}

export function isGuestPracticeAllowed(practice: GuestPracticeLike): boolean {
  if (!practice.is_free) return false;
  if (practice.is_personalized) return false;
  const level = (practice.access_level || "free").trim().toLowerCase();
  return level === "free" || level === "basic" || level === "starter" || level === "public";
}
