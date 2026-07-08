const STORAGE_KEY = "todayflow.relationship_map.v1";
const MAX_CIRCLES = 24;

export type RelationshipCircleRecord = {
  id: string;
  label: string;
  scenarioId: string;
  pairLine?: string | null;
  theme?: string | null;
  lastSeenAt: string;
  visitCount: number;
};

function newId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `rel-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export function readRelationshipMapCircles(): RelationshipCircleRecord[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as RelationshipCircleRecord[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function writeRelationshipMapCircles(circles: RelationshipCircleRecord[]): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(circles.slice(0, MAX_CIRCLES)));
  } catch {
    /* quota */
  }
}

export function recordRelationshipMapVisit(input: {
  label: string;
  scenarioId: string;
  pairLine?: string | null;
  theme?: string | null;
}): RelationshipCircleRecord {
  const label = input.label.trim();
  const scenarioId = input.scenarioId.trim();
  if (!label || !scenarioId) {
    return {
      id: newId(),
      label: label || "Связь",
      scenarioId: scenarioId || "general",
      pairLine: input.pairLine,
      theme: input.theme,
      lastSeenAt: new Date().toISOString(),
      visitCount: 1,
    };
  }

  const key = `${label.toLowerCase()}|${scenarioId.toLowerCase()}`;
  const now = new Date().toISOString();
  const existing = readRelationshipMapCircles();
  const idx = existing.findIndex((c) => `${c.label.toLowerCase()}|${c.scenarioId.toLowerCase()}` === key);
  let record: RelationshipCircleRecord;
  if (idx >= 0) {
    record = {
      ...existing[idx],
      pairLine: input.pairLine ?? existing[idx].pairLine,
      theme: input.theme ?? existing[idx].theme,
      lastSeenAt: now,
      visitCount: existing[idx].visitCount + 1,
    };
    existing.splice(idx, 1);
    existing.unshift(record);
  } else {
    record = {
      id: newId(),
      label,
      scenarioId,
      pairLine: input.pairLine ?? null,
      theme: input.theme ?? null,
      lastSeenAt: now,
      visitCount: 1,
    };
    existing.unshift(record);
  }
  writeRelationshipMapCircles(existing);
  return record;
}

/** Circle radius by attention (visit count), capped for layout. */
export function relationshipCircleRadius(visitCount: number): number {
  return Math.min(56, 22 + Math.sqrt(Math.max(1, visitCount)) * 8);
}

/** Ring position for network layout. */
export function relationshipCirclePosition(index: number, total: number): { x: number; y: number } {
  if (total <= 1) return { x: 50, y: 50 };
  const angle = (index / total) * Math.PI * 2 - Math.PI / 2;
  const r = total <= 3 ? 0 : 28;
  return {
    x: 50 + Math.cos(angle) * r,
    y: 50 + Math.sin(angle) * r,
  };
}
