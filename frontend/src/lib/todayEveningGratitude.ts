/**
 * Evening gratitude persist — user response, never a rewrite of the saved day.
 * Canon: docs/today/TODAY_PRODUCT_FLOW_V1.md §4
 */

import { ApiError, getJson, isTransportFailure, postJson } from "@/lib/api";
import { previousDateISO } from "@/lib/todayDayContinuity";
import type { TodaySlotLoadFailure } from "@/lib/todaySlotAvailability";

export const EVENING_GRATITUDE_CATEGORIES = [
  { id: "people", label: "За человека рядом" },
  { id: "work", label: "За то, что получилось" },
  { id: "quiet", label: "За спокойный момент" },
  { id: "fresh", label: "За новый опыт" },
  { id: "self", label: "За себя" },
] as const;

export type EveningGratitudeCategoryId =
  (typeof EVENING_GRATITUDE_CATEGORIES)[number]["id"];

export type EveningGratitudeRecord = {
  dateISO: string;
  categories: string[];
  text: string;
  manifestVersion?: string | null;
  savedAt: string;
};

/** Yesterday evening close as read on D+1 TODAY. Not an outcome of a promise. */
export type EveningCloseSnapshot = {
  dateISO: string;
  eveningCompleted: boolean;
  categories: string[];
  text: string;
  morningFocus: string | null;
};

type DayConnectionPayload = {
  date?: string;
  evening_completed?: boolean;
  evening_reflection?: string | null;
  evening_observations?: {
    kind?: string;
    categories?: unknown;
    text?: unknown;
    manifest_version?: string | null;
  } | null;
  morning_focus?: string | null;
};

export function gratitudeCategoryLabels(categories: string[]): string[] {
  return EVENING_GRATITUDE_CATEGORIES.filter((row) => categories.includes(row.id)).map(
    (row) => row.label,
  );
}

export function buildGratitudeMemorySlot(snapshot: EveningCloseSnapshot | null): {
  eyebrow: string;
  body: string;
  state: "stub" | "filled";
} {
  if (!snapshot?.eveningCompleted) {
    return { eyebrow: "", body: "", state: "stub" };
  }
  const labels = gratitudeCategoryLabels(snapshot.categories);
  const text = snapshot.text.replace(/\s+/g, " ").trim();
  const focus = snapshot.morningFocus?.replace(/\s+/g, " ").trim() || "";
  const gratitudeBit = text
    ? text.length > 120
      ? `${text.slice(0, 117)}…`
      : text
    : labels.length
      ? labels.join(", ").toLowerCase()
      : "";
  if (!gratitudeBit && !focus) {
    return { eyebrow: "", body: "", state: "stub" };
  }
  const body = focus
    ? gratitudeBit
      ? `Вчера в фокусе было: «${focus.length > 80 ? `${focus.slice(0, 77)}…` : focus}». Вечер сохранён благодарностью: ${gratitudeBit}.`
      : `Вчера в фокусе было: «${focus.length > 80 ? `${focus.slice(0, 77)}…` : focus}». Вечер закрыт благодарностью.`
    : `Вчера ты отметил(а) благодарность: ${gratitudeBit}.`;
  return {
    eyebrow: "С чего продолжить",
    body,
    state: "filled",
  };
}

function snapshotFromLocal(record: EveningGratitudeRecord | null): EveningCloseSnapshot | null {
  if (!record) return null;
  if (!record.categories.length && !record.text.trim()) return null;
  return {
    dateISO: record.dateISO,
    eveningCompleted: true,
    categories: record.categories,
    text: record.text,
    morningFocus: null,
  };
}

function snapshotFromConnection(
  dateISO: string,
  payload: DayConnectionPayload | null,
): EveningCloseSnapshot | null {
  if (!payload?.evening_completed) return null;
  const obs = payload.evening_observations;
  const fromGratitude = obs && String(obs.kind || "") === "gratitude";
  const categories = fromGratitude && Array.isArray(obs.categories)
    ? obs.categories.map((id) => String(id || "").trim()).filter(Boolean)
    : [];
  const obsText = fromGratitude && typeof obs.text === "string" ? obs.text.trim() : "";
  const text = obsText || String(payload.evening_reflection || "").trim();
  const morningFocus = String(payload.morning_focus || "").trim() || null;
  if (!categories.length && !text && !morningFocus) return null;
  return {
    dateISO,
    eveningCompleted: true,
    categories,
    text,
    morningFocus,
  };
}

/** Same-device yesterday close without a network round-trip. */
export function loadLocalYesterdayEveningClose(todayISO: string): EveningCloseSnapshot | null {
  const dateISO = String(todayISO || "").trim();
  if (!dateISO) return null;
  return snapshotFromLocal(loadEveningGratitude(previousDateISO(dateISO)));
}

/** Server yesterday close first; same-device local gratitude if the GET is empty. */
export async function loadYesterdayEveningClose(
  todayISO: string,
  options?: { authenticated?: boolean },
): Promise<EveningCloseSnapshot | null> {
  const dateISO = String(todayISO || "").trim();
  if (!dateISO) return null;
  const yesterday = previousDateISO(dateISO);
  if (options?.authenticated) {
    try {
      const payload = await getJson<DayConnectionPayload | null>(
        `/day-connection/${encodeURIComponent(yesterday)}`,
      );
      const fromServer = snapshotFromConnection(yesterday, payload);
      if (fromServer) return fromServer;
    } catch {
      /* transport / auth — fall through to local, never invent */
    }
  }
  return snapshotFromLocal(loadEveningGratitude(yesterday));
}

export function eveningGratitudeStorageKey(dateISO: string): string {
  return `todayflow_evening_gratitude_v1:${dateISO}`;
}

export function loadEveningGratitude(dateISO: string): EveningGratitudeRecord | null {
  if (typeof window === "undefined" || !dateISO) return null;
  try {
    const raw = window.localStorage.getItem(eveningGratitudeStorageKey(dateISO));
    if (!raw) return null;
    const parsed = JSON.parse(raw) as EveningGratitudeRecord;
    if (!parsed || parsed.dateISO !== dateISO) return null;
    return parsed;
  } catch {
    return null;
  }
}

function saveEveningGratitudeLocal(record: EveningGratitudeRecord): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(
    eveningGratitudeStorageKey(record.dateISO),
    JSON.stringify(record),
  );
}

function classifyPersistError(error: unknown): TodaySlotLoadFailure | "auth" {
  if (isTransportFailure(error)) return "no_connection";
  if (error instanceof ApiError && (error.status === 401 || error.status === 403)) {
    return "auth";
  }
  return "unavailable";
}

function journalContent(categories: string[], text: string): string {
  const labels = EVENING_GRATITUDE_CATEGORIES.filter((row) =>
    categories.includes(row.id),
  ).map((row) => row.label);
  const head = labels.length ? labels.join(", ") : "";
  const body = text.replace(/\s+/g, " ").trim();
  if (head && body) return `${head}\n\n${body}`.slice(0, 2000);
  return (body || head).slice(0, 2000);
}

export async function persistEveningGratitude(input: {
  dateISO: string;
  categories: string[];
  text: string;
  manifestVersion?: string | null;
  /** Snapshot of the already-shown day thesis. Does not rewrite the saved day. */
  dayFocus?: string | null;
}): Promise<{ ok: true } | { ok: false; reason: TodaySlotLoadFailure }> {
  const dateISO = String(input.dateISO || "").trim();
  const categories = Array.from(
    new Set((input.categories || []).map((id) => String(id || "").trim()).filter(Boolean)),
  );
  const text = String(input.text || "").trim();
  if (!dateISO || (!categories.length && !text)) {
    return { ok: false, reason: "unavailable" };
  }

  const record: EveningGratitudeRecord = {
    dateISO,
    categories,
    text,
    manifestVersion: input.manifestVersion ?? null,
    savedAt: new Date().toISOString(),
  };
  saveEveningGratitudeLocal(record);

  const content = journalContent(categories, text);
  const morningFocus = String(input.dayFocus || "")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 100);
  let journalKind: TodaySlotLoadFailure | "auth" | "ok" = "ok";
  try {
    await postJson("/journal/entries", {
      type: "gratitude",
      content,
      day: dateISO,
    });
  } catch (error) {
    journalKind = classifyPersistError(error);
  }

  let connectionKind: TodaySlotLoadFailure | "auth" | "ok" = "ok";
  try {
    await postJson(`/day-connection/${encodeURIComponent(dateISO)}`, {
      evening_completed: true,
      evening_reflection: content.slice(0, 500),
      evening_observations: {
        kind: "gratitude",
        categories,
        text,
        manifest_version: input.manifestVersion ?? null,
      },
      ...(morningFocus ? { morning_focus: morningFocus } : {}),
    });
  } catch (error) {
    connectionKind = classifyPersistError(error);
  }

  const kinds = [journalKind, connectionKind];
  if (kinds.includes("no_connection")) return { ok: false, reason: "no_connection" };
  if (kinds.includes("unavailable")) return { ok: false, reason: "unavailable" };
  return { ok: true };
}
