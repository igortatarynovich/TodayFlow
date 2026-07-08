/**
 * Today / card-of-day → partial three-card spread (anchor = first card).
 * Canon: SCREEN_CONTRACTS_V1 §6.6
 */

export function buildTarotDeepenHref(params: {
  cardId: number;
  orientation: "upright" | "reversed";
  question?: string | null;
  source?: "today" | "card_of_day";
}): string {
  const defaultQuestion =
    params.source === "today"
      ? "Как карта дня помогает увидеть мой вопрос глубже?"
      : "Что эта карта дня подсказывает, если посмотреть на ситуацию шире?";
  const search = new URLSearchParams({
    anchor: `${params.cardId}:${params.orientation}`,
    question: (params.question?.trim() || defaultQuestion).slice(0, 280),
    source: params.source || "card_of_day",
  });
  return `/tarot/spread/three_cards?${search.toString()}`;
}

export function parseTarotAnchorParam(value: string | null | undefined): {
  cardId: number;
  orientation: "upright" | "reversed";
} | null {
  if (!value?.trim()) return null;
  const [rawId, rawOrient] = value.split(":");
  const cardId = Number(rawId);
  if (!Number.isFinite(cardId)) return null;
  const orientation = rawOrient === "reversed" ? "reversed" : "upright";
  return { cardId, orientation };
}
