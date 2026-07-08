import type { MeaningEventSource } from "@/lib/types";

export type TarotDeepenSource = "today" | "card_of_day";

export function buildTarotDeepenEventPayload(params: {
  cardId: number;
  orientation: "upright" | "reversed";
  source: TarotDeepenSource;
  spreadId?: string;
}): Record<string, unknown> {
  return {
    card_id: params.cardId,
    orientation: params.orientation,
    source: params.source,
    spread_id: params.spreadId ?? "three_cards",
  };
}

export function tarotDeepenIdempotencyKey(params: {
  cardId: number;
  source: TarotDeepenSource;
  localDate?: string | null;
}): string {
  const day = params.localDate ?? new Date().toISOString().slice(0, 10);
  return `tarot-deepen:${params.source}:${params.cardId}:${day}`;
}

export const TAROT_DEEPEN_EVENT_SOURCE: MeaningEventSource = "flow";
