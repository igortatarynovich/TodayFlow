"use client";

import { clearCompactUserModelCache } from "@/lib/compactUserModelCache";
import { clearCoreProfileCache } from "@/lib/coreProfileCacheStorage";
import { ENERGY_MAP_STORAGE_PREFIX } from "@/lib/energyMapStorage";
import { GUEST_PROFILE_SESSION_KEY } from "@/lib/guestProfileDraft";
import { clearMeaningSessionCaches } from "@/lib/meaningRuntime";
import { DAY_CONTINUITY_STORAGE_PREFIX } from "@/lib/todayDayContinuity";
import { invalidateCoordinatedFetch } from "@/lib/todayFetchCoordinator";
import { clearTodayNarrativeCache } from "@/lib/todayNarrativeCache";
import { RITUAL_STORAGE_PREFIX } from "@/lib/todayRitualPersisted";

export const AUTH_TOKEN_KEY = "todayflow_token";
export const AUTH_REFRESH_TOKEN_KEY = "todayflow_refresh_token";
export const AUTH_SNAPSHOT_KEY = "todayflow_auth_snapshot_v1";
export const AUTH_LAST_VALIDATED_AT_KEY = "todayflow_last_auth_validated_at";
export const AUTH_LAST_SNAPSHOT_SAVED_AT_KEY = "todayflow_last_session_snapshot_saved_at";

const PROFILE_ATOM_VERDICT_PREFIX = "todayflow.profile_atom_verdict.v1";
const ENGAGEMENT_STORAGE_PREFIX = "todayflow.day_engagement.v1.";
const TAROT_JOURNEY_KEY = "todayflow:tarot-journey:v1";

const LOCAL_STORAGE_PREFIXES = [
  ENGAGEMENT_STORAGE_PREFIX,
  `${DAY_CONTINUITY_STORAGE_PREFIX}.`,
  ENERGY_MAP_STORAGE_PREFIX,
  PROFILE_ATOM_VERDICT_PREFIX,
  "todayflow_core_profile:",
];

const SESSION_STORAGE_PREFIXES = [
  "todayflow_core_profile:",
  "todayflow.compact_user_model.",
  "todayflow.cum_confidence_history.",
  "todayflow.today_narrative.",
  `${RITUAL_STORAGE_PREFIX}.`,
  "todayflow:tarot-question-flow:v1",
  "todayflow_guidance_compat_prefill_v1",
  "todayflow_active_jtbd_context",
  "todayflow_active_day_spine_context",
  GUEST_PROFILE_SESSION_KEY,
];

function removeStorageByPrefix(storage: Storage, prefixes: string[]): void {
  for (let i = storage.length - 1; i >= 0; i -= 1) {
    const key = storage.key(i);
    if (!key) continue;
    if (prefixes.some((prefix) => key.startsWith(prefix) || key === prefix)) {
      storage.removeItem(key);
    }
  }
}

/** User-scoped client caches — clear on login switch and logout. Locale and guest draft stay. */
export function clearAuthenticatedUserCaches(): void {
  clearCoreProfileCache();
  clearCompactUserModelCache();
  clearTodayNarrativeCache();
  clearMeaningSessionCaches();
  invalidateCoordinatedFetch("today:");
  removeStorageByPrefix(localStorage, LOCAL_STORAGE_PREFIXES);
  removeStorageByPrefix(sessionStorage, SESSION_STORAGE_PREFIXES);
  try {
    localStorage.removeItem(TAROT_JOURNEY_KEY);
  } catch {
    /* ignore */
  }
}

export function clearAuthCredentialStorage(): void {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(AUTH_REFRESH_TOKEN_KEY);
  localStorage.removeItem(AUTH_SNAPSHOT_KEY);
  localStorage.removeItem(AUTH_LAST_VALIDATED_AT_KEY);
  localStorage.removeItem(AUTH_LAST_SNAPSHOT_SAVED_AT_KEY);
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(AUTH_TOKEN_KEY);
  if (raw == null) return null;
  const trimmed = raw.trim();
  if (!trimmed) {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    return null;
  }
  if (trimmed !== raw) {
    localStorage.setItem(AUTH_TOKEN_KEY, trimmed);
  }
  return trimmed;
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(AUTH_REFRESH_TOKEN_KEY);
  if (raw == null) return null;
  const trimmed = raw.trim();
  if (!trimmed) {
    localStorage.removeItem(AUTH_REFRESH_TOKEN_KEY);
    return null;
  }
  return trimmed;
}

export function setTokenPair(accessToken: string, refreshToken?: string | null): void {
  localStorage.setItem(AUTH_TOKEN_KEY, accessToken.trim());
  if (refreshToken && refreshToken.trim()) {
    localStorage.setItem(AUTH_REFRESH_TOKEN_KEY, refreshToken.trim());
  }
}
