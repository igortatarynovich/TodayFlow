import type { FusionResponse } from "@/components/today/todayPageUtils";

export const ENERGY_MAP_STORAGE_PREFIX = "todayflow.energy_map.v1.";

export type EnergyMapDayRecord = {
  dateISO: string;
  energyScore: number;
  focusScore?: number;
  balanceScore?: number;
  tempoLabel?: string;
  capturedAt: string;
  source: "fusion_api" | "today_fusion" | "mood_infer";
};

export function energyMapStorageKey(dateISO: string): string {
  return `${ENERGY_MAP_STORAGE_PREFIX}${dateISO}`;
}

export function normalizeEnergyMapRecord(input: unknown, dateISO: string): EnergyMapDayRecord | null {
  if (!input || typeof input !== "object") return null;
  const p = input as Record<string, unknown>;
  const energyScore = typeof p.energyScore === "number" ? p.energyScore : Number(p.energyScore);
  if (!Number.isFinite(energyScore)) return null;
  const clamped = Math.max(0, Math.min(100, Math.round(energyScore)));
  return {
    dateISO: typeof p.dateISO === "string" ? p.dateISO : dateISO,
    energyScore: clamped,
    focusScore: typeof p.focusScore === "number" ? p.focusScore : undefined,
    balanceScore: typeof p.balanceScore === "number" ? p.balanceScore : undefined,
    tempoLabel: typeof p.tempoLabel === "string" ? p.tempoLabel : undefined,
    capturedAt: typeof p.capturedAt === "string" ? p.capturedAt : new Date().toISOString(),
    source:
      p.source === "fusion_api" || p.source === "today_fusion" || p.source === "mood_infer"
        ? p.source
        : "today_fusion",
  };
}

export function loadEnergyMapRecord(dateISO: string): EnergyMapDayRecord | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(energyMapStorageKey(dateISO));
    if (!raw) return null;
    return normalizeEnergyMapRecord(JSON.parse(raw), dateISO);
  } catch {
    return null;
  }
}

export function saveEnergyMapRecord(record: EnergyMapDayRecord): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(energyMapStorageKey(record.dateISO), JSON.stringify(record));
  } catch {
    /* quota */
  }
}

export function persistEnergyMapSnapshot(
  dateISO: string,
  input: {
    energyScore: number;
    focusScore?: number;
    balanceScore?: number;
    tempoLabel?: string;
    source?: EnergyMapDayRecord["source"];
  },
): EnergyMapDayRecord {
  const record: EnergyMapDayRecord = {
    dateISO,
    energyScore: Math.max(0, Math.min(100, Math.round(input.energyScore))),
    focusScore: input.focusScore,
    balanceScore: input.balanceScore,
    tempoLabel: input.tempoLabel,
    capturedAt: new Date().toISOString(),
    source: input.source ?? "today_fusion",
  };
  saveEnergyMapRecord(record);
  return record;
}

export function persistEnergyFromFusionResponse(
  dateISO: string,
  fusion: FusionResponse,
  source: EnergyMapDayRecord["source"] = "fusion_api",
): EnergyMapDayRecord | null {
  const energy = fusion?.scores?.energy;
  if (typeof energy !== "number" || !Number.isFinite(energy)) return null;
  return persistEnergyMapSnapshot(dateISO, {
    energyScore: energy,
    focusScore: fusion.scores.focus,
    balanceScore: fusion.scores.emotional_balance,
    source,
  });
}

/** Newest first. */
export function scanEnergyMapDayRecords(): EnergyMapDayRecord[] {
  if (typeof window === "undefined") return [];
  const records: EnergyMapDayRecord[] = [];
  try {
    for (let i = 0; i < window.localStorage.length; i += 1) {
      const key = window.localStorage.key(i);
      if (!key?.startsWith(ENERGY_MAP_STORAGE_PREFIX)) continue;
      const dateISO = key.slice(ENERGY_MAP_STORAGE_PREFIX.length);
      const record = loadEnergyMapRecord(dateISO);
      if (record) records.push(record);
    }
  } catch {
    return [];
  }
  records.sort((a, b) => b.dateISO.localeCompare(a.dateISO));
  return records;
}

export function mergeEnergyMapRecords(records: EnergyMapDayRecord[]): EnergyMapDayRecord[] {
  const byDate = new Map<string, EnergyMapDayRecord>();
  for (const record of records) {
    const prev = byDate.get(record.dateISO);
    if (!prev || prev.capturedAt < record.capturedAt) {
      byDate.set(record.dateISO, record);
    }
  }
  return Array.from(byDate.values()).sort((a, b) => b.dateISO.localeCompare(a.dateISO));
}
