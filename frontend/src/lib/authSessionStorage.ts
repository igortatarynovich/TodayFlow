"use client";

import { clearCompactUserModelCache } from "@/lib/compactUserModelCache";
import { clearCoreProfileCache } from "@/lib/coreProfileCacheStorage";
import { ENERGY_MAP_STORAGE_PREFIX } from "@/lib/energyMapStorage";
import { GUEST_PROFILE_SESSION_KEY } from "@/lib/guestProfileDraft";
import { clearMeaningSessionCaches } from "@/lib/meaningRuntime";
import { DAY_CONTINUITY_STORAGE_PREFIX } from "@/lib/todayDayContinuity";
import { clearTodayNarrativeCache } from "@/lib/todayNarrativeCache";
import { RITUAL_STORAGE_PREFIX } from "@/lib/todayRitualPersisted";

export const AUTH_TOKEN_KEY = "todayflow_token";
export const AUTH_SNAPSHOT_KEY = "todayflow_auth_snapshot_v1";
export const AUTH_LAST_VALIDATED_AT_KEY = "todayflow_last_auth_validated_at";
export const AUTH_LAST_SNAPSHOT_SAVED_AT_KEY = "todayflow_last_session_snapshot_saved_at";
/** Set on logout/401 so guest surfaces prefer Login over leftover First Today draft. */
export const AUTH_SESSION_ENDED_KEY = "todayflow_auth_session_ended_v1";

const PROFILE_ATOM_VERDICT_PREFIX = "todayflow.profile_atom_verdict.v1";
const ENGAGEMENT_STORAGE_PREFIX = "todayflow.day_engagement.v1.";
const TAROT_JOURNEY_KEY = "todayflow:tarot-journey:v1";

const LOCAL_STORAGE_PREFIXES = [
  ENGAGEMENT_STORAGE_PREFIX,
  `${DAY_CONTINUITY_STORAGE_PREFIX}.`,
  ENERGY_MAP_STORAGE_PREFIX,
  PROFILE_ATOM_VERDICT_PREFIX,
  // Ritual day extras live in localStorage (not sessionStorage).
  `${RITUAL_STORAGE_PREFIX}.`,
];

const SESSION_STORAGE_PREFIXES = [
  "todayflow_core_profile:",
  "todayflow.compact_user_model.",
  "todayflow.cum_confidence_history.",
  "todayflow.today_narrative.",
  "todayflow:tarot-question-flow:v1",
  "todayflow_guidance_compat_prefill_v1",
  "todayflow_active_jtbd_context",
  "todayflow_active_day_spine_context",
  GUEST_PROFILE_SESSION_KEY,
];

export function markAuthSessionEnded(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(AUTH_SESSION_ENDED_KEY, new Date().toISOString());
  } catch {
    /* ignore */
  }
}

export function clearAuthSessionEnded(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(AUTH_SESSION_ENDED_KEY);
  } catch {
    /* ignore */
  }
}

export function hasAuthSessionEnded(): boolean {
  if (typeof window === "undefined") return false;
  try {
    return Boolean(localStorage.getItem(AUTH_SESSION_ENDED_KEY)?.trim());
  } catch {
    return false;
  }
}

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
  localStorage.removeItem(AUTH_SNAPSHOT_KEY);
  localStorage.removeItem(AUTH_LAST_VALIDATED_AT_KEY);
  localStorage.removeItem(AUTH_LAST_SNAPSHOT_SAVED_AT_KEY);
}
