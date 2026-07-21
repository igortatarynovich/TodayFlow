"use client";

import type { CoreProfile } from "@/lib/types";
import { resolveCacheUserScope } from "@/lib/cacheUserScope";

const PREFIX = "todayflow_core_profile:v2";

export const CORE_PROFILE_UPDATED_EVENT = "todayflow:core-profile-updated";

export type CoreProfileUpdatedDetail = {
  profile: CoreProfile;
  astroProfileId: number | null;
};

export function cacheKeyForCoreProfile(astroProfileId: number | null | undefined): string {
  const scope = resolveCacheUserScope();
  if (astroProfileId == null) return `${PREFIX}:${scope}:default`;
  return `${PREFIX}:${scope}:astro:${astroProfileId}`;
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

/**
 * Снимок `core_profile` внутри `GET /today` может отставать от явного `GET /account/core-profile`
 * (кэш дня на бэкенде). Выбираем более свежий объект по `generated_at` между телом ответа и sessionStorage.
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
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(cacheKeyForCoreProfile(astroProfileId ?? null));
    if (!raw) return null;
    const parsed: unknown = JSON.parse(raw);
    return isPlausibleCoreProfile(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

export function writeCoreProfileToCache(profile: CoreProfile, astroProfileId?: number | null): void {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.setItem(cacheKeyForCoreProfile(astroProfileId ?? null), JSON.stringify(profile));
  } catch {
    /* quota / private mode */
  }
}

export function clearCoreProfileCache(): void {
  if (typeof window === "undefined") return;
  try {
    for (let i = sessionStorage.length - 1; i >= 0; i -= 1) {
      const key = sessionStorage.key(i);
      // Clear v1 (legacy unscoped) and v2.
      if (key?.startsWith("todayflow_core_profile:")) {
        sessionStorage.removeItem(key);
      }
    }
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
