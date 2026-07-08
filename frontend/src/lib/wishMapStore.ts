export const WISH_MAP_STORAGE_PREFIX = "todayflow.wish_map.v1.";

export type WishAnchorRecord = {
  id: string;
  title: string;
  source: "local" | "goal";
  createdAt: string;
  lastStepDate?: string | null;
  stepCount: number;
};

export type WishGoalIn = {
  id: number;
  title: string;
  scope: string;
  completed: boolean;
  step_dates: string[];
};

function wishStorageKey(id: string): string {
  return `${WISH_MAP_STORAGE_PREFIX}${id}`;
}

export function readLocalWishAnchors(): WishAnchorRecord[] {
  if (typeof window === "undefined") return [];
  const out: WishAnchorRecord[] = [];
  try {
    for (let i = 0; i < window.localStorage.length; i += 1) {
      const key = window.localStorage.key(i);
      if (!key?.startsWith(WISH_MAP_STORAGE_PREFIX)) continue;
      const raw = window.localStorage.getItem(key);
      if (!raw) continue;
      const parsed = JSON.parse(raw) as WishAnchorRecord;
      if (parsed?.title?.trim()) out.push(parsed);
    }
  } catch {
    return [];
  }
  return out.sort((a, b) => (b.lastStepDate ?? b.createdAt).localeCompare(a.lastStepDate ?? a.createdAt));
}

export function saveLocalWishAnchor(title: string): WishAnchorRecord {
  const trimmed = title.trim();
  const id = `local-${Date.now()}`;
  const record: WishAnchorRecord = {
    id,
    title: trimmed,
    source: "local",
    createdAt: new Date().toISOString(),
    stepCount: 0,
  };
  if (typeof window !== "undefined") {
    try {
      window.localStorage.setItem(wishStorageKey(id), JSON.stringify(record));
    } catch {
      /* quota */
    }
  }
  return record;
}

export function recordWishStep(wishId: string, dateISO: string): void {
  if (typeof window === "undefined") return;
  const key = wishStorageKey(wishId);
  try {
    const raw = window.localStorage.getItem(key);
    if (!raw) return;
    const record = JSON.parse(raw) as WishAnchorRecord;
    record.stepCount = (record.stepCount ?? 0) + 1;
    record.lastStepDate = dateISO;
    window.localStorage.setItem(key, JSON.stringify(record));
  } catch {
    /* ignore */
  }
}

export function mergeWishAnchorsFromGoals(goals: WishGoalIn[]): WishAnchorRecord[] {
  const monthGoals = goals.filter((g) => (g.scope || "").toLowerCase() === "month" && !g.completed);
  const fromGoals: WishAnchorRecord[] = monthGoals.map((g) => ({
    id: `goal-${g.id}`,
    title: g.title.trim(),
    source: "goal",
    createdAt: g.step_dates[0] ? `${g.step_dates[0]}T12:00:00.000Z` : new Date().toISOString(),
    lastStepDate: g.step_dates.length ? g.step_dates.sort().at(-1) ?? null : null,
    stepCount: g.step_dates.length,
  }));
  const local = readLocalWishAnchors();
  const byTitle = new Map<string, WishAnchorRecord>();
  for (const item of [...fromGoals, ...local]) {
    const key = item.title.toLowerCase();
    const prev = byTitle.get(key);
    if (!prev || (item.stepCount ?? 0) >= (prev.stepCount ?? 0)) byTitle.set(key, item);
  }
  return Array.from(byTitle.values()).sort((a, b) =>
    (b.lastStepDate ?? b.createdAt).localeCompare(a.lastStepDate ?? a.createdAt),
  );
}

/** Stable pseudo-positions for constellation layout (0–100). */
export function wishConstellationPosition(id: string, index: number): { x: number; y: number } {
  let hash = index * 17;
  for (let i = 0; i < id.length; i += 1) hash = (hash + id.charCodeAt(i) * 31) % 997;
  return {
    x: 12 + (hash % 76),
    y: 10 + ((hash * 7) % 72),
  };
}
