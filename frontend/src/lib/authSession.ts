"use client";

import { clearAuthMeCache } from "@/lib/api";
import { flushMeaningOutbox } from "@/lib/meaningRuntime";
import {
  AUTH_TOKEN_KEY,
  AUTH_REFRESH_TOKEN_KEY,
  clearAuthCredentialStorage,
  clearAuthenticatedUserCaches,
  getRefreshToken,
  setTokenPair,
} from "@/lib/authSessionStorage";

export {
  AUTH_TOKEN_KEY,
  AUTH_REFRESH_TOKEN_KEY,
  AUTH_SNAPSHOT_KEY,
  AUTH_LAST_VALIDATED_AT_KEY,
  AUTH_LAST_SNAPSHOT_SAVED_AT_KEY,
  getAccessToken,
  getRefreshToken,
} from "@/lib/authSessionStorage";

export type AuthTokenPair = {
  access_token?: string | null;
  refresh_token?: string | null;
  token?: string | null;
};

export function notifyAuthSessionChanged(): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new Event("auth:update"));
}

/** Normalize login/magic/OAuth/refresh payloads into access + optional refresh. */
export function extractTokenPair(payload: AuthTokenPair | string): {
  access: string;
  refresh: string | null;
} {
  if (typeof payload === "string") {
    return { access: payload.trim(), refresh: null };
  }
  const access = (payload.access_token || payload.token || "").trim();
  const refresh = (payload.refresh_token || "").trim() || null;
  return { access, refresh };
}

/** After signup/login/OAuth — drop stale user caches, persist tokens, notify subscribers. */
export function beginAuthSession(tokenOrPair: string | AuthTokenPair): void {
  if (typeof window === "undefined") return;
  const { access, refresh } = extractTokenPair(tokenOrPair);
  if (!access) return;
  clearAuthenticatedUserCaches();
  clearAuthCredentialStorage();
  clearAuthMeCache();
  setTokenPair(access, refresh);
  notifyAuthSessionChanged();
}

/** Logout / failed refresh — wipe credentials and user caches without navigation. */
export function clearAuthSession(): void {
  if (typeof window === "undefined") return;
  clearAuthenticatedUserCaches();
  clearAuthCredentialStorage();
  clearAuthMeCache();
}

/** Flush learning outbox, revoke refresh if present, clear session. */
export async function signOut(): Promise<void> {
  if (typeof window === "undefined") return;
  await flushMeaningOutbox().catch(() => undefined);
  const refresh = getRefreshToken();
  if (refresh) {
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8080";
      await fetch(`${API_BASE}/auth/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refresh }),
      });
    } catch {
      /* best-effort revoke */
    }
  }
  clearAuthSession();
  notifyAuthSessionChanged();
}

/** Hard redirect logout — use signOut() + router.replace when possible. */
export async function logoutUser(redirectTo: string = "/auth?mode=login"): Promise<void> {
  await signOut();
  window.location.assign(redirectTo);
}
