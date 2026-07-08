import { getJson, getStoredAccessToken, postJson } from "@/lib/api";
import type { MeaningEventInput, MeaningEventSource, MeaningEventType, MeaningRingsResponse } from "@/lib/types";

const OUTBOX_KEY = "todayflow_meaning_outbox_v1";
const RINGS_CACHE_KEY = "todayflow_meaning_rings_cache_v1";
const MAX_BATCH = 50;
const MAX_OUTBOX = 500;
const MAX_IDEMPOTENCY_KEY_LEN = 128;

function hasAuthForMeaningApi(): boolean {
  return Boolean(getStoredAccessToken());
}

/** Backend rejects keys longer than 128 chars (Pydantic max_length). */
export function normalizeIdempotencyKey(raw: string): string {
  const trimmed = raw.trim();
  if (trimmed.length <= MAX_IDEMPOTENCY_KEY_LEN) return trimmed;
  let hash = 5381;
  for (let i = 0; i < trimmed.length; i += 1) {
    hash = ((hash << 5) + hash) ^ trimmed.charCodeAt(i);
  }
  const suffix = (hash >>> 0).toString(16).padStart(8, "0");
  const prefixBudget = MAX_IDEMPOTENCY_KEY_LEN - suffix.length - 1;
  return `${trimmed.slice(0, prefixBudget)}:${suffix}`;
}

type OutboxItem = MeaningEventInput;
type RingsCacheRecord = {
  window_days: number;
  generated_at: string;
  rings: MeaningRingsResponse["rings"];
  cached_at: string;
};

function isBrowser(): boolean {
  return typeof window !== "undefined";
}

function dedupeOutboxItems(items: OutboxItem[]): OutboxItem[] {
  const seen = new Set<string>();
  const deduped: OutboxItem[] = [];
  for (let i = items.length - 1; i >= 0; i -= 1) {
    const key = normalizeIdempotencyKey(items[i].idempotency_key);
    if (seen.has(key)) continue;
    seen.add(key);
    deduped.unshift({ ...items[i], idempotency_key: key });
  }
  return deduped;
}

function readOutbox(): OutboxItem[] {
  if (!isBrowser()) return [];
  try {
    const raw = localStorage.getItem(OUTBOX_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    const items = Array.isArray(parsed) ? (parsed as OutboxItem[]) : [];
    return dedupeOutboxItems(items);
  } catch {
    return [];
  }
}

function writeOutbox(items: OutboxItem[]): void {
  if (!isBrowser()) return;
  localStorage.setItem(OUTBOX_KEY, JSON.stringify(items.slice(-MAX_OUTBOX)));
}

export function enqueueMeaningEvent(input: {
  event_type: MeaningEventType;
  event_source: MeaningEventSource;
  quality_score?: number;
  payload?: Record<string, unknown> | null;
  local_date?: string | null;
  idempotency_key?: string;
}): string {
  const idempotencyKey = normalizeIdempotencyKey(
    input.idempotency_key?.trim() || `m-${Date.now()}-${Math.random().toString(16).slice(2, 10)}`,
  );
  const event: OutboxItem = {
    event_type: input.event_type,
    event_source: input.event_source,
    quality_score: input.quality_score ?? 1,
    payload: input.payload ?? null,
    local_date: input.local_date ?? new Date().toISOString().slice(0, 10),
    event_time: new Date().toISOString(),
    idempotency_key: idempotencyKey,
  };
  const outbox = readOutbox();
  outbox.push(event);
  writeOutbox(dedupeOutboxItems(outbox));
  return idempotencyKey;
}

export async function flushMeaningOutbox(): Promise<void> {
  if (!isBrowser() || !hasAuthForMeaningApi()) return;
  let outbox = dedupeOutboxItems(readOutbox());
  writeOutbox(outbox);
  if (!outbox.length) return;
  while (outbox.length > 0) {
    const rawChunk = outbox.slice(0, MAX_BATCH);
    const seen = new Set<string>();
    const chunk = rawChunk.filter((event) => {
      const key = normalizeIdempotencyKey(event.idempotency_key);
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    }).map((event) => ({
      ...event,
      idempotency_key: normalizeIdempotencyKey(event.idempotency_key),
    }));
    if (!chunk.length) {
      outbox = outbox.slice(rawChunk.length);
      writeOutbox(outbox);
      continue;
    }
    try {
      await postJson("/meaning/events", { events: chunk });
      outbox = outbox.slice(rawChunk.length);
      writeOutbox(outbox);
    } catch {
      // Drop the stuck head chunk so poisoned duplicates cannot block the whole outbox forever.
      outbox = dedupeOutboxItems(outbox.slice(rawChunk.length));
      writeOutbox(outbox);
      return;
    }
  }
}

export function getCachedMeaningRings(): RingsCacheRecord | null {
  if (!isBrowser()) return null;
  try {
    const raw = localStorage.getItem(RINGS_CACHE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as RingsCacheRecord;
    if (!parsed || !Array.isArray(parsed.rings)) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function clearMeaningSessionCaches(): void {
  if (!isBrowser()) return;
  localStorage.removeItem(OUTBOX_KEY);
  localStorage.removeItem(RINGS_CACHE_KEY);
}

export async function refreshMeaningRings(windowDays = 28): Promise<MeaningRingsResponse | null> {
  if (!hasAuthForMeaningApi()) return null;
  const result = await getJson<MeaningRingsResponse>(`/meaning/rings?window_days=${windowDays}`);
  if (isBrowser()) {
    const cache: RingsCacheRecord = {
      ...result,
      cached_at: new Date().toISOString(),
    };
    localStorage.setItem(RINGS_CACHE_KEY, JSON.stringify(cache));
  }
  return result;
}

