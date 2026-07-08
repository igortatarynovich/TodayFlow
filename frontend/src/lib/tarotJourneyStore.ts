import type { TarotConcernDomain } from "@/lib/tarotQuestionFlowCanon";
import type { TarotReadingResonance } from "@/lib/buildTarotReadingStoryModel";

const STORAGE_KEY = "todayflow:tarot-journey:v1";
export const TAROT_JOURNEY_MIN_SESSIONS = 5;
const MAX_ENTRIES = 80;

export type TarotJourneyEntry = {
  id: string;
  completedAt: string;
  question: string;
  concernDomain: TarotConcernDomain | string | null;
  spreadId: string;
  spreadTitle: string;
  cardIds: number[];
  cardNames: string[];
  resonance?: TarotReadingResonance | null;
};

function newEntryId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `tj-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export function readTarotJourneyEntries(): TarotJourneyEntry[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as TarotJourneyEntry[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function writeTarotJourneyEntries(entries: TarotJourneyEntry[]): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(entries.slice(0, MAX_ENTRIES)));
  } catch {
    /* quota */
  }
}

export function appendTarotJourneyEntry(
  entry: Omit<TarotJourneyEntry, "id" | "completedAt"> & { completedAt?: string },
): TarotJourneyEntry {
  const full: TarotJourneyEntry = {
    id: newEntryId(),
    completedAt: entry.completedAt ?? new Date().toISOString(),
    question: entry.question,
    concernDomain: entry.concernDomain,
    spreadId: entry.spreadId,
    spreadTitle: entry.spreadTitle,
    cardIds: entry.cardIds,
    cardNames: entry.cardNames,
    resonance: entry.resonance ?? null,
  };
  const next = [full, ...readTarotJourneyEntries()].slice(0, MAX_ENTRIES);
  writeTarotJourneyEntries(next);
  return full;
}

export function updateTarotJourneyResonance(entryId: string, resonance: TarotReadingResonance): void {
  const entries = readTarotJourneyEntries().map((e) => (e.id === entryId ? { ...e, resonance } : e));
  writeTarotJourneyEntries(entries);
}

export function tarotJourneySessionCount(): number {
  return readTarotJourneyEntries().length;
}

export function shouldShowTarotJourney(): boolean {
  return tarotJourneySessionCount() >= TAROT_JOURNEY_MIN_SESSIONS;
}
