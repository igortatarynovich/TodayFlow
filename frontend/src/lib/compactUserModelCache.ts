"use client";

import { getJson } from "@/lib/api";
import { resolveCacheUserScope } from "@/lib/cacheUserScope";
import type { CompactUserModel, CompactUserModelConfidenceHistory } from "@/lib/types";

const CACHE_PREFIX = "todayflow.compact_user_model.v1";
const CONFIDENCE_HISTORY_PREFIX = "todayflow.cum_confidence_history.v1";
const CACHE_TTL_MS = 5 * 60 * 1000;

type CacheEntry = {
  fetchedAtMs: number;
  localDate: string;
  scope: string;
  model: CompactUserModel;
};

function cacheKey(localDate: string): string {
  return `${CACHE_PREFIX}.${resolveCacheUserScope()}.${localDate}`;
}

function confidenceHistoryCacheKey(localDate: string, windowDays: number): string {
  return `${CONFIDENCE_HISTORY_PREFIX}.${resolveCacheUserScope()}.${localDate}.${windowDays}`;
}

export async function fetchCompactUserModelCached(options?: {
  localDate?: string;
  force?: boolean;
}): Promise<CompactUserModel | null> {
  const localDate = options?.localDate ?? new Date().toISOString().slice(0, 10);
  const force = options?.force ?? false;
  const scope = resolveCacheUserScope();

  if (!force && typeof window !== "undefined") {
    try {
      const raw = window.sessionStorage.getItem(cacheKey(localDate));
      if (raw) {
        const entry = JSON.parse(raw) as CacheEntry;
        if (
          entry?.model &&
          entry.localDate === localDate &&
          entry.scope === scope &&
          Date.now() - entry.fetchedAtMs < CACHE_TTL_MS
        ) {
          return entry.model;
        }
      }
    } catch {
      /* ignore */
    }
  }

  const qs = localDate ? `?local_date=${encodeURIComponent(localDate)}` : "";
  try {
    const model = await getJson<CompactUserModel>(`/account/compact-user-model${qs}`);
    if (model && typeof window !== "undefined") {
      const entry: CacheEntry = { fetchedAtMs: Date.now(), localDate, scope, model };
      try {
        window.sessionStorage.setItem(cacheKey(localDate), JSON.stringify(entry));
      } catch {
        /* quota */
      }
    }
    return model;
  } catch {
    return null;
  }
}

export function clearCompactUserModelCache(localDate?: string): void {
  if (typeof window === "undefined") return;
  if (localDate) {
    window.sessionStorage.removeItem(cacheKey(localDate));
    // Clear any windowDays variants for this date/scope.
    for (let i = window.sessionStorage.length - 1; i >= 0; i -= 1) {
      const key = window.sessionStorage.key(i);
      if (
        key?.startsWith(`${CONFIDENCE_HISTORY_PREFIX}.${resolveCacheUserScope()}.${localDate}.`)
      ) {
        window.sessionStorage.removeItem(key);
      }
    }
    return;
  }
  for (let i = window.sessionStorage.length - 1; i >= 0; i -= 1) {
    const key = window.sessionStorage.key(i);
    if (
      key?.startsWith("todayflow.compact_user_model.") ||
      key?.startsWith("todayflow.cum_confidence_history.")
    ) {
      window.sessionStorage.removeItem(key);
    }
  }
}

export async function fetchCompactUserModelConfidenceHistoryCached(options?: {
  localDate?: string;
  windowDays?: number;
  force?: boolean;
}): Promise<CompactUserModelConfidenceHistory | null> {
  const localDate = options?.localDate ?? new Date().toISOString().slice(0, 10);
  const windowDays = options?.windowDays ?? 90;
  const force = options?.force ?? false;
  const scope = resolveCacheUserScope();

  if (!force && typeof window !== "undefined") {
    try {
      const raw = window.sessionStorage.getItem(confidenceHistoryCacheKey(localDate, windowDays));
      if (raw) {
        const entry = JSON.parse(raw) as {
          fetchedAtMs: number;
          localDate: string;
          scope: string;
          history: CompactUserModelConfidenceHistory;
        };
        if (
          entry?.history &&
          entry.localDate === localDate &&
          entry.scope === scope &&
          Date.now() - entry.fetchedAtMs < CACHE_TTL_MS
        ) {
          return entry.history;
        }
      }
    } catch {
      /* ignore */
    }
  }

  const qs = new URLSearchParams();
  if (localDate) qs.set("local_date", localDate);
  qs.set("window_days", String(windowDays));
  try {
    const history = await getJson<CompactUserModelConfidenceHistory>(
      `/account/compact-user-model/confidence-history?${qs.toString()}`,
    );
    if (history && typeof window !== "undefined") {
      try {
        window.sessionStorage.setItem(
          confidenceHistoryCacheKey(localDate, windowDays),
          JSON.stringify({ fetchedAtMs: Date.now(), localDate, scope, history }),
        );
      } catch {
        /* quota */
      }
    }
    return history;
  } catch {
    return null;
  }
}
