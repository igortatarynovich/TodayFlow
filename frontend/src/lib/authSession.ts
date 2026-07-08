"use client";

import { clearAuthMeCache } from "@/lib/api";
import { flushMeaningOutbox } from "@/lib/meaningRuntime";
import {
  AUTH_TOKEN_KEY,
  clearAuthCredentialStorage,
  clearAuthenticatedUserCaches,
} from "@/lib/authSessionStorage";

export {
  AUTH_TOKEN_KEY,
  AUTH_SNAPSHOT_KEY,
  AUTH_LAST_VALIDATED_AT_KEY,
  AUTH_LAST_SNAPSHOT_SAVED_AT_KEY,
} from "@/lib/authSessionStorage";

export function notifyAuthSessionChanged(): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new Event("auth:update"));
}

/** After signup/login/OAuth — drop stale user caches, persist token, notify subscribers. */
export function beginAuthSession(token: string): void {
  if (typeof window === "undefined") return;
  const trimmed = token.trim();
  if (!trimmed) return;
  clearAuthenticatedUserCaches();
  clearAuthCredentialStorage();
  clearAuthMeCache();
  localStorage.setItem(AUTH_TOKEN_KEY, trimmed);
  notifyAuthSessionChanged();
}

/** Logout / 401 — wipe credentials and user caches without navigation. */
export function clearAuthSession(): void {
  if (typeof window === "undefined") return;
  clearAuthenticatedUserCaches();
  clearAuthCredentialStorage();
  clearAuthMeCache();
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
