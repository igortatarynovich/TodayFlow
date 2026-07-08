import tarotMajorArcana from "@/data/tarotMajorArcana.json";
import { TAROT_FULL_DECK_COUNT } from "@/lib/tarotCardAssets";

export const TAROT_MAJOR_ARCANA_IDS: number[] = (tarotMajorArcana as { id: number }[])
  .map((c) => c.id)
  .sort((a, b) => a - b);

export const TAROT_DECK_INDICES: number[] = Array.from({ length: TAROT_FULL_DECK_COUNT }, (_, i) => i);

/** Случайный индекс колоды 0…77, исключая указанные (уточняющая карта и т. п.). */
export function randomTarotDeckIndexExclude(excludeIds: number[]): number {
  const ex = new Set(excludeIds.filter((x) => typeof x === "number" && Number.isFinite(x)));
  let pool = TAROT_DECK_INDICES.filter((id) => !ex.has(id));
  if (!pool.length) pool = [...TAROT_DECK_INDICES];
  return pool[Math.floor(Math.random() * pool.length)]!;
}

/** Случайный старший аркан (0…21); для полной колоды см. `randomTarotDeckIndexExclude`. */
export function randomTarotMajorArcanaId(excludeIds: number[]): number {
  const ex = new Set(excludeIds.filter((x) => typeof x === "number" && Number.isFinite(x)));
  let pool = TAROT_MAJOR_ARCANA_IDS.filter((id) => !ex.has(id));
  if (!pool.length) pool = [...TAROT_MAJOR_ARCANA_IDS];
  return pool[Math.floor(Math.random() * pool.length)]!;
}
