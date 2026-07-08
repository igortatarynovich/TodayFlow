/**
 * Day Continuity v0 — local persistence for ship gate (Evening Close + Tomorrow).
 * Not Intent Record / PR2; enables Yesterday → Today → Tomorrow loop in experience surface.
 */

export const DAY_CONTINUITY_STORAGE_PREFIX = "todayflow.day_continuity.v1";

export type DayFocusOutcome = "done" | "partial" | "not_done";

export type DayContinuityRecord = {
  dateISO: string;
  mainFocus: string;
  outcome?: DayFocusOutcome;
  outcomeNote?: string;
  closedAt?: string;
};

export function dayContinuityStorageKey(dateISO: string): string {
  return `${DAY_CONTINUITY_STORAGE_PREFIX}.${dateISO}`;
}

export function normalizeDayContinuityRecord(input: unknown, dateISO: string): DayContinuityRecord | null {
  if (!input || typeof input !== "object") return null;
  const p = input as Record<string, unknown>;
  const mainFocus = typeof p.mainFocus === "string" ? p.mainFocus.trim() : "";
  if (!mainFocus) return null;
  const outcome =
    p.outcome === "done" || p.outcome === "partial" || p.outcome === "not_done" ? p.outcome : undefined;
  const outcomeNote = typeof p.outcomeNote === "string" ? p.outcomeNote.trim() : undefined;
  const closedAt = typeof p.closedAt === "string" ? p.closedAt : undefined;
  return {
    dateISO: typeof p.dateISO === "string" ? p.dateISO : dateISO,
    mainFocus,
    outcome,
    outcomeNote: outcomeNote || undefined,
    closedAt,
  };
}

export function loadDayContinuity(dateISO: string): DayContinuityRecord | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(dayContinuityStorageKey(dateISO));
    if (!raw) return null;
    return normalizeDayContinuityRecord(JSON.parse(raw), dateISO);
  } catch {
    return null;
  }
}

export function saveDayContinuity(record: DayContinuityRecord): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(dayContinuityStorageKey(record.dateISO), JSON.stringify(record));
  } catch {
    /* quota */
  }
}

export function previousDateISO(dateISO: string): string {
  const d = new Date(`${dateISO}T12:00:00`);
  d.setDate(d.getDate() - 1);
  return d.toISOString().slice(0, 10);
}

export function loadPreviousDayContinuity(dateISO: string): DayContinuityRecord | null {
  return loadDayContinuity(previousDateISO(dateISO));
}

export function isDayContinuityClosed(record: DayContinuityRecord | null): boolean {
  return Boolean(record?.closedAt && record.outcome);
}

export function outcomeLabelRu(outcome: DayFocusOutcome): string {
  switch (outcome) {
    case "done":
      return "Сделал";
    case "partial":
      return "Частично";
    case "not_done":
      return "Не сделал";
  }
}

export function buildTomorrowContinuityHook(): string {
  return "Завтра начнём с того, как сегодняшний результат повлиял на ваш следующий шаг.";
}

export function buildContinuityOpeningLine(prev: DayContinuityRecord): string | null {
  if (!prev.mainFocus || !prev.outcome) return null;
  const focus = prev.mainFocus.length > 120 ? `${prev.mainFocus.slice(0, 117)}…` : prev.mainFocus;
  return `Вчера главным было: «${focus}». Итог: ${outcomeLabelRu(prev.outcome).toLowerCase()}. Сегодня продолжим с того, как это повлияло на ваш следующий шаг.`;
}

export function formatDayContinuityDateRu(dateISO: string): string {
  const d = new Date(`${dateISO}T12:00:00`);
  if (Number.isNaN(d.getTime())) return dateISO;
  return d.toLocaleDateString("ru-RU", { day: "numeric", month: "long" });
}

/** All closed days newest-first from local persistence. */
export function scanClosedDayContinuityRecords(): DayContinuityRecord[] {
  if (typeof window === "undefined") return [];
  const prefix = `${DAY_CONTINUITY_STORAGE_PREFIX}.`;
  const records: DayContinuityRecord[] = [];
  try {
    for (let i = 0; i < window.localStorage.length; i += 1) {
      const key = window.localStorage.key(i);
      if (!key?.startsWith(prefix)) continue;
      const dateISO = key.slice(prefix.length);
      const raw = window.localStorage.getItem(key);
      if (!raw) continue;
      const record = normalizeDayContinuityRecord(JSON.parse(raw), dateISO);
      if (!record || !isDayContinuityClosed(record)) continue;
      records.push(record);
    }
  } catch {
    return [];
  }
  records.sort((left, right) => {
    const leftKey = left.closedAt || left.dateISO;
    const rightKey = right.closedAt || right.dateISO;
    return rightKey.localeCompare(leftKey);
  });
  return records;
}

/** Closed days newest-first from local persistence (Profile «Мои дни» v0). */
export function listClosedDayContinuityRecords(limit = 3): DayContinuityRecord[] {
  return scanClosedDayContinuityRecords().slice(0, Math.max(0, limit));
}

export function countClosedDayContinuityRecords(): number {
  return scanClosedDayContinuityRecords().length;
}
