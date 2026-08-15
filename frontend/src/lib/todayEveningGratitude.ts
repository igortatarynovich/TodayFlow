/**
 * Evening gratitude persist — user response, never a rewrite of the saved day.
 * Canon: docs/today/TODAY_PRODUCT_FLOW_V1.md §4
 */

import { ApiError, isTransportFailure, postJson } from "@/lib/api";
import type { TodaySlotLoadFailure } from "@/lib/todaySlotAvailability";

export const EVENING_GRATITUDE_CATEGORIES = [
  { id: "people", label: "За человека рядом" },
  { id: "work", label: "За то, что получилось" },
  { id: "quiet", label: "За спокойный момент" },
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
    });
  } catch (error) {
    connectionKind = classifyPersistError(error);
  }

  const kinds = [journalKind, connectionKind];
  if (kinds.includes("no_connection")) return { ok: false, reason: "no_connection" };
  if (kinds.includes("unavailable")) return { ok: false, reason: "unavailable" };
  return { ok: true };
}
