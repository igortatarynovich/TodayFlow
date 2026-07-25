"use client";

import type { NatalChartPreview } from "@/components/profile/profilePanelTypes";
import { resolveCacheUserScope } from "@/lib/cacheUserScope";

const PREFIX = "todayflow_natal_preview:v2";
/** Soft TTL — natal chart is stable until birth data changes. */
const NATAL_CACHE_MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000;

type CachedEnvelope = {
  savedAt: number;
  preview: NatalChartPreview;
};

function cacheKey(astroProfileId: number | null | undefined, scope = resolveCacheUserScope()): string {
  if (astroProfileId == null) return `${PREFIX}:${scope}:default`;
  return `${PREFIX}:${scope}:astro:${astroProfileId}`;
}

function isPlausiblePreview(value: unknown): value is NatalChartPreview {
  if (!value || typeof value !== "object") return false;
  const o = value as Record<string, unknown>;
  const positions = o.positions;
  const houses = o.houses;
  const hasPositions = positions != null && typeof positions === "object";
  const hasHouses = Array.isArray(houses) ? houses.length > 0 : houses != null;
  return hasPositions || hasHouses || o.ascendant != null;
}

/** Drop bulky LLM/editorial prose so localStorage write fits quota. */
export function slimNatalPreviewForCache(preview: NatalChartPreview): NatalChartPreview {
  const { interpretations: _i, ...rest } = preview as NatalChartPreview & {
    editorial?: unknown;
    interpretations?: NatalChartPreview["interpretations"];
  };
  const slim = { ...rest } as NatalChartPreview & { editorial?: unknown };
  delete slim.editorial;
  // Keep house interpretations if compact; drop if oversized later via try/catch.
  if (_i?.houses) {
    slim.interpretations = { houses: _i.houses };
  }
  return slim;
}

function readEnvelope(key: string): CachedEnvelope | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(key) ?? localStorage.getItem(key);
    if (!raw) return null;
    const parsed: unknown = JSON.parse(raw);
    if (
      parsed &&
      typeof parsed === "object" &&
      "preview" in parsed &&
      isPlausiblePreview((parsed as CachedEnvelope).preview)
    ) {
      const env = parsed as CachedEnvelope;
      const savedAt = typeof env.savedAt === "number" ? env.savedAt : Date.now();
      if (Date.now() - savedAt > NATAL_CACHE_MAX_AGE_MS) return null;
      return { savedAt, preview: env.preview };
    }
    if (isPlausiblePreview(parsed)) {
      return { savedAt: Date.now(), preview: parsed };
    }
    return null;
  } catch {
    return null;
  }
}

function candidateKeys(astroProfileId?: number | null): string[] {
  const scopes = new Set<string>([resolveCacheUserScope(), "u:pending"]);
  return Array.from(scopes).map((scope) => cacheKey(astroProfileId, scope));
}

export function readNatalPreviewFromCache(
  astroProfileId?: number | null,
): NatalChartPreview | null {
  for (const key of candidateKeys(astroProfileId)) {
    const hit = readEnvelope(key)?.preview;
    if (hit) return hit;
  }
  // Legacy v1 keys
  const legacyPrefix = "todayflow_natal_preview:v1";
  const scope = resolveCacheUserScope();
  const legacyKeys = [
    astroProfileId == null ? `${legacyPrefix}:${scope}:default` : `${legacyPrefix}:${scope}:astro:${astroProfileId}`,
    `${legacyPrefix}:u:pending:default`,
  ];
  for (const key of legacyKeys) {
    const hit = readEnvelope(key)?.preview;
    if (hit) return hit;
  }
  return null;
}

export function writeNatalPreviewToCache(
  preview: NatalChartPreview,
  astroProfileId?: number | null,
): void {
  if (typeof window === "undefined" || !preview) return;
  const slim = slimNatalPreviewForCache(preview);
  const envelope: CachedEnvelope = { savedAt: Date.now(), preview: slim };
  const keys = candidateKeys(astroProfileId ?? (preview as { astro_profile_id?: number }).astro_profile_id);
  try {
    const raw = JSON.stringify(envelope);
    for (const key of keys) {
      sessionStorage.setItem(key, raw);
      try {
        localStorage.setItem(key, raw);
      } catch {
        /* quota — session still holds paint cache */
      }
    }
  } catch {
    /* quota */
  }
}

export function clearNatalPreviewCache(astroProfileId?: number | null): void {
  if (typeof window === "undefined") return;
  for (const key of candidateKeys(astroProfileId)) {
    try {
      sessionStorage.removeItem(key);
      localStorage.removeItem(key);
    } catch {
      /* ignore */
    }
  }
}
