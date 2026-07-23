/**
 * Deduplicate parallel Today/contract fetches on the same mount key.
 * Stale-while-revalidate: callers still own UI; this only coalesces in-flight + short TTL.
 */

type Entry<T> = {
  expiresAt: number;
  data: T | null;
  inFlight: Promise<T> | null;
};

const CACHE_TTL_MS = 15_000;
const store = new Map<string, Entry<unknown>>();

export async function coordinatedFetch<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttlMs: number = CACHE_TTL_MS,
): Promise<T> {
  const now = Date.now();
  const existing = store.get(key) as Entry<T> | undefined;
  if (existing?.data != null && existing.expiresAt > now) {
    return existing.data;
  }
  if (existing?.inFlight) {
    return existing.inFlight;
  }

  const inFlight = fetcher()
    .then((data) => {
      store.set(key, { data, expiresAt: Date.now() + ttlMs, inFlight: null });
      return data;
    })
    .catch((error) => {
      const cur = store.get(key) as Entry<T> | undefined;
      if (cur?.inFlight === inFlight) {
        store.set(key, { data: cur.data, expiresAt: cur.expiresAt, inFlight: null });
      }
      throw error;
    });

  store.set(key, {
    data: existing?.data ?? null,
    expiresAt: existing?.expiresAt ?? 0,
    inFlight,
  });
  return inFlight;
}

export function invalidateCoordinatedFetch(prefix?: string): void {
  if (!prefix) {
    store.clear();
    return;
  }
  for (const key of Array.from(store.keys())) {
    if (key.startsWith(prefix)) store.delete(key);
  }
}
