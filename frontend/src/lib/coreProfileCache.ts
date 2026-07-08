"use client";

import { getJson } from "@/lib/api";
import type { CoreProfile } from "@/lib/types";
import { readCoreProfileFromCache, writeCoreProfileToCache } from "@/lib/coreProfileCacheStorage";

export {
  clearCoreProfileCache,
  publishCoreProfileUpdate,
  readCoreProfileFromCache,
  resolveCoreProfileAgainstSessionCache,
  CORE_PROFILE_UPDATED_EVENT,
  type CoreProfileUpdatedDetail,
} from "@/lib/coreProfileCacheStorage";

/**
 * Загружает ядро профиля: при отсутствии query по astro использует sessionStorage, затем сеть.
 */
export async function fetchCoreProfileCached(options?: {
  astroProfileId?: number | null;
  force?: boolean;
}): Promise<CoreProfile | null> {
  const astroId = options?.astroProfileId ?? null;
  const force = options?.force ?? false;

  if (!force && astroId == null) {
    const cached = readCoreProfileFromCache(null);
    if (cached) return cached;
  }

  const qs = astroId != null ? `?astro_profile_id=${encodeURIComponent(String(astroId))}` : "";
  try {
    const profile = await getJson<CoreProfile>(`/account/core-profile${qs}`);
    if (profile) {
      writeCoreProfileToCache(profile, astroId);
    }
    return profile;
  } catch {
    if (!force && astroId == null) {
      return readCoreProfileFromCache(null);
    }
    return null;
  }
}
