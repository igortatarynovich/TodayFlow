"use client";

import { clearAuthMeCache } from "@/lib/api";
import { flushMeaningOutbox } from "@/lib/meaningRuntime";
import {
  AUTH_TOKEN_KEY,
  AUTH_SNAPSHOT_KEY,
  AUTH_LAST_SNAPSHOT_SAVED_AT_KEY,
  clearAuthCredentialStorage,
  clearAuthenticatedUserCaches,
  clearAuthSessionEnded,
  markAuthSessionEnded,
} from "@/lib/authSessionStorage";

export {
  AUTH_TOKEN_KEY,
  AUTH_SNAPSHOT_KEY,
  AUTH_LAST_VALIDATED_AT_KEY,
  AUTH_LAST_SNAPSHOT_SAVED_AT_KEY,
  AUTH_SESSION_ENDED_KEY,
  hasAuthSessionEnded,
  clearAuthSessionEnded,
} from "@/lib/authSessionStorage";

export function notifyAuthSessionChanged(): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new Event("auth:update"));
}

function writeBootstrapAuthSnapshot(token: string): void {
  try {
    const savedAt = Date.now();
    localStorage.setItem(
      AUTH_SNAPSHOT_KEY,
      JSON.stringify({ token, profile: null, savedAt }),
    );
    localStorage.setItem(AUTH_LAST_SNAPSHOT_SAVED_AT_KEY, String(savedAt));
  } catch {
    /* private mode / quota */
  }
}

/** After signup/login/OAuth — drop stale user caches, persist token, notify subscribers. */
export function beginAuthSession(token: string): void {
  if (typeof window === "undefined") return;
  const trimmed = token.trim();
  if (!trimmed) return;
  clearAuthenticatedUserCaches();
  clearAuthCredentialStorage();
  clearAuthSessionEnded();
  clearAuthMeCache();
  try {
    localStorage.setItem(AUTH_TOKEN_KEY, trimmed);
    writeBootstrapAuthSnapshot(trimmed);
  } catch {
    /* private mode — session will not survive reload, but this tab can still navigate */
  }
  notifyAuthSessionChanged();
  void import("@/lib/warmTodayDayBundle")
    .then(({ warmTodayDayBundle }) => {
      void warmTodayDayBundle();
    })
    .catch(() => {});
}

/** Logout / 401 — wipe credentials and user caches without navigation. */
export function clearAuthSession(): void {
  if (typeof window === "undefined") return;
  const hadToken = Boolean(localStorage.getItem(AUTH_TOKEN_KEY)?.trim());
  clearAuthenticatedUserCaches();
  clearAuthCredentialStorage();
  clearAuthMeCache();
  // Returning users must not keep a "logged-in Today" from ritual/guest leftovers.
  if (hadToken) {
    markAuthSessionEnded();
  }
}

/** Flush learning outbox, clear session; caller handles navigation (prefer router.replace). */
export async function signOut(): Promise<void> {
  if (typeof window === "undefined") return;
  await flushMeaningOutbox().catch(() => undefined);
  clearAuthSession();
  notifyAuthSessionChanged();
}

/** Hard redirect logout — use signOut() + router.replace when possible. */
export async function logoutUser(redirectTo: string = "/auth?mode=login"): Promise<void> {
  await signOut();
  window.location.assign(redirectTo);
}
