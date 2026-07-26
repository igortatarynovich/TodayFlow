"use client";

import type { CoreProfile } from "@/lib/types";
import { resolveCacheUserScope } from "@/lib/cacheUserScope";

const PREFIX = "todayflow_core_profile:v3";
/** Soft TTL for stale-while-revalidate (7 days). Hash mismatch still wins. */
const CORE_PROFILE_CACHE_MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000;

export const CORE_PROFILE_UPDATED_EVENT = "todayflow:core-profile-updated";

export type CoreProfileUpdatedDetail = {
  profile: CoreProfile;
  astroProfileId: number | null;
};

type CachedEnvelope = {
  savedAt: number;
  profile: CoreProfile;
};

export function cacheKeyForCoreProfile(
  astroProfileId: number | null | undefined,
  scope = resolveCacheUserScope(),
): string {
  if (astroProfileId == null) return `${PREFIX}:${scope}:default`;
  return `${PREFIX}:${scope}:astro:${astroProfileId}`;
}

/** After login, scope may flip `u:pending` → `u:{id}`; read/write both like natal preview. */
function candidateKeys(astroProfileId?: number | null): string[] {
  const scopes = new Set<string>([resolveCacheUserScope(), "u:pending"]);
  return Array.from(scopes).map((scope) => cacheKeyForCoreProfile(astroProfileId ?? null, scope));
}

function isPlausibleCoreProfile(value: unknown): value is CoreProfile {
  if (!value || typeof value !== "object") return false;
  const o = value as Record<string, unknown>;
  return typeof o.profile_hash === "string" && typeof o.profile_version === "string";
}

function coreProfileGeneratedAtMs(profile: CoreProfile): number {
  const t = Date.parse(profile.generated_at);
  return Number.isFinite(t) ? t : 0;
}

function readEnvelope(key: string): CachedEnvelope | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(key) ?? sessionStorage.getItem(key);
    if (!raw) return null;
    const parsed: unknown = JSON.parse(raw);
    if (isPlausibleCoreProfile(parsed)) {
      // Legacy bare profile object
      return { savedAt: coreProfileGeneratedAtMs(parsed) || Date.now(), profile: parsed };
    }
    if (
      parsed &&
      typeof parsed === "object" &&
      "profile" in parsed &&
      isPlausibleCoreProfile((parsed as CachedEnvelope).profile)
    ) {
      const env = parsed as CachedEnvelope;
      const savedAt = typeof env.savedAt === "number" ? env.savedAt : Date.now();
      return { savedAt, profile: env.profile };
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * Снимок `core_profile` внутри `GET /today` может отставать от явного `GET /account/core-profile`
 * (кэш дня на бэкенде). Выбираем более свежий объект по `generated_at` между телом ответа и cache.
 */
export function resolveCoreProfileAgainstSessionCache(
  embedded: CoreProfile | null,
  astroProfileId?: number | null,
): CoreProfile | null {
  const session = readCoreProfileFromCache(astroProfileId ?? null);
  if (!embedded) return session;
  if (!session) return embedded;
  const te = coreProfileGeneratedAtMs(embedded);
  const ts = coreProfileGeneratedAtMs(session);
  if (ts > te) return session;
  if (te > ts) return embedded;
  if (embedded.profile_hash !== session.profile_hash) return session;
  return embedded;
}

export function readCoreProfileFromCache(astroProfileId?: number | null): CoreProfile | null {
  let best: CachedEnvelope | null = null;
  for (const key of candidateKeys(astroProfileId)) {
    const env = readEnvelope(key);
    if (!env) continue;
    if (Date.now() - env.savedAt > CORE_PROFILE_CACHE_MAX_AGE_MS) continue;
    if (!best || env.savedAt > best.savedAt) best = env;
  }
  return best?.profile ?? null;
}

export function writeCoreProfileToCache(profile: CoreProfile, astroProfileId?: number | null): void {
  if (typeof window === "undefined") return;
  const envelope: CachedEnvelope = { savedAt: Date.now(), profile };
  const raw = JSON.stringify(envelope);
  for (const key of candidateKeys(astroProfileId ?? null)) {
    try {
      localStorage.setItem(key, raw);
    } catch {
      /* quota / private mode — fall back to session */
      try {
        sessionStorage.setItem(key, raw);
      } catch {
        /* ignore */
      }
    }
  }
}

export function clearCoreProfileCache(): void {
  if (typeof window === "undefined") return;
  const clearFrom = (storage: Storage) => {
    for (let i = storage.length - 1; i >= 0; i -= 1) {
      const key = storage.key(i);
      // Clear current + legacy v2 keys so old Мудрец snapshots cannot stick.
      if (
        key?.startsWith("todayflow_core_profile:") ||
        key?.startsWith("todayflow_core_profile:v2")
      ) {
        storage.removeItem(key);
      }
    }
  };
  try {
    clearFrom(localStorage);
  } catch {
    /* ignore */
  }
  try {
    clearFrom(sessionStorage);
  } catch {
    /* ignore */
  }
}

/** Записывает кэш и рассылает событие для подписчиков в той же вкладке. */
export function publishCoreProfileUpdate(profile: CoreProfile, astroProfileId?: number | null): void {
  writeCoreProfileToCache(profile, astroProfileId ?? null);
  if (typeof window === "undefined") return;
  const detail: CoreProfileUpdatedDetail = { profile, astroProfileId: astroProfileId ?? null };
  window.dispatchEvent(new CustomEvent<CoreProfileUpdatedDetail>(CORE_PROFILE_UPDATED_EVENT, { detail }));
}
