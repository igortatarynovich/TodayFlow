"use client";

import type { NatalChartPreview } from "@/components/profile/profilePanelTypes";
import { resolveCacheUserScope } from "@/lib/cacheUserScope";

const PREFIX = "todayflow_natal_preview:v1";
/** Soft TTL — natal chart is stable until birth data changes. */
const NATAL_CACHE_MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000;

type CachedEnvelope = {
  savedAt: number;
  preview: NatalChartPreview;
};

function cacheKey(astroProfileId: number | null | undefined): string {
  const scope = resolveCacheUserScope();
  if (astroProfileId == null) return `${PREFIX}:${scope}:default`;
  return `${PREFIX}:${scope}:astro:${astroProfileId}`;
}

function isPlausiblePreview(value: unknown): value is NatalChartPreview {
  if (!value || typeof value !== "object") return false;
  const o = value as Record<string, unknown>;
  return typeof o === "object" && (o.positions != null || o.houses != null || o.ascendant != null);
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

export function readNatalPreviewFromCache(
  astroProfileId?: number | null,
): NatalChartPreview | null {
  return readEnvelope(cacheKey(astroProfileId))?.preview ?? null;
}

export function writeNatalPreviewToCache(
  preview: NatalChartPreview,
  astroProfileId?: number | null,
): void {
  if (typeof window === "undefined" || !preview) return;
  const key = cacheKey(astroProfileId);
  const envelope: CachedEnvelope = { savedAt: Date.now(), preview };
  try {
    const raw = JSON.stringify(envelope);
    sessionStorage.setItem(key, raw);
    localStorage.setItem(key, raw);
  } catch {
    /* quota */
  }
}

export function clearNatalPreviewCache(astroProfileId?: number | null): void {
  if (typeof window === "undefined") return;
  const key = cacheKey(astroProfileId);
  try {
    sessionStorage.removeItem(key);
    localStorage.removeItem(key);
  } catch {
    /* ignore */
  }
}
