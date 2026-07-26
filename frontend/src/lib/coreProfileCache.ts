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
 * Загружает ядро профиля.
 * Без force: может вернуть local/session cache (быстрый paint).
 * С force: сеть — GET обязан быть дешёвым (snapshot + consumption, без LLM).
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
    // Force failed — last-resort paint from any still-valid cache.
    if (force && astroId == null) {
      return readCoreProfileFromCache(null);
    }
    return null;
  }
}
