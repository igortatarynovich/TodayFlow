/** Stable client-side user scope for personalized caches (never put JWT in keys). */

import { AUTH_SNAPSHOT_KEY, AUTH_TOKEN_KEY } from "@/lib/authSessionStorage";

export type CacheUserScope = string;

const GUEST_SCOPE = "guest";
const ANON_SCOPE = "anon";

/**
 * Resolve cache scope from auth snapshot /me user_id.
 * Falls back to guest/anon — never uses the raw access token.
 */
export function resolveCacheUserScope(): CacheUserScope {
  if (typeof window === "undefined") return ANON_SCOPE;
  try {
    const raw = localStorage.getItem(AUTH_SNAPSHOT_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as { profile?: { user_id?: number } | null };
      const uid = parsed?.profile?.user_id;
      if (typeof uid === "number" && Number.isFinite(uid) && uid > 0) {
        return `u:${uid}`;
      }
    }
  } catch {
    /* ignore */
  }
  try {
    if (localStorage.getItem(AUTH_TOKEN_KEY)) return "u:pending";
  } catch {
    /* ignore */
  }
  try {
    if (localStorage.getItem("todayflow_guest_session_v1")) return GUEST_SCOPE;
  } catch {
    /* ignore */
  }
  return ANON_SCOPE;
}
