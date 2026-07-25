/**
 * Статические изображения колоды в `public/images/cards/tarot/`.
 * Полная колода: 22 старших аркана + 56 младших (4 масти × 14 карт, файлы 1.png…14.png).
 */

import tarotMeta from "@/data/tarotDeckIndex.json";

const TAROT_PUBLIC_BASE = "/images/cards/tarot";

const SUIT_OF = ["Suit of Wands", "Suit of Cups", "Suit of Swords", "Suit of Pentacles"] as const;

/** Всего карт в колоде Waite-Smith (как в ассетах). */
export const TAROT_FULL_DECK_COUNT = 78;

/** Натуральный размер PNG колоды (пропорции UI на вебе и в iOS). */
export const TAROT_CARD_PIXEL_WIDTH = 192;
export const TAROT_CARD_PIXEL_HEIGHT = 320;

/** Миниатюра лица в блоке «день готов» (паритет с iOS `TodayRitualFlowView` spine). */
export const TAROT_SPINE_THUMB_WIDTH_PX = 76;

/** Макс. ширина раскрытой карты в ритуале Today (лицо + рубашка в pick flow). */
export const TAROT_RITUAL_REVEAL_MAX_WIDTH_PX = 220;

/** CSS `aspect-ratio`: ширина / высота. */
export const TAROT_CARD_ASPECT_RATIO = TAROT_CARD_PIXEL_WIDTH / TAROT_CARD_PIXEL_HEIGHT;

export function tarotCardDisplayHeightPx(widthPx: number): number {
  return Math.round((widthPx * TAROT_CARD_PIXEL_HEIGHT) / TAROT_CARD_PIXEL_WIDTH);
}

/** Рубашка колоды (веб-ассет в корне `tarot/`). */
export function tarotCardBackSrc(): string {
  return `${TAROT_PUBLIC_BASE}/${encodeURIComponent("Back_web.png")}`;
}

/**
 * Лицо карты по индексу колоды 0…77: 0–21 Major Arcana, 22–77 младшие арканы
 * (жезлы, кубки, мечи, пентакли по 14 карт в порядке файлов 1…14).
 */
export function tarotCardFaceSrc(deckIndex: number): string | null {
  if (!Number.isFinite(deckIndex) || deckIndex < 0 || deckIndex > 77) return null;
  if (deckIndex <= 21) {
    return `${TAROT_PUBLIC_BASE}/${encodeURIComponent("Major Arcana")}/${deckIndex}.png`;
  }
  const n = deckIndex - 22;
  const suitIndex = Math.floor(n / 14);
  const rank = (n % 14) + 1;
  const folder = SUIT_OF[suitIndex];
  if (!folder) return null;
  return `${TAROT_PUBLIC_BASE}/${encodeURIComponent(folder)}/${rank}.png`;
}

type TarotMetaCard = {
  deck_index: number;
  id: string;
  name_ru: string;
  name_en: string;
};

function normalizeTarotNameKey(raw: string | null | undefined): string | null {
  if (raw == null || typeof raw !== "string") return null;
  const t = raw
    .trim()
    .toLowerCase()
    .replace(/ё/g, "е")
    .replace(/[«»"'`]/g, "")
    .replace(/\s+/g, " ");
  return t.length ? t : null;
}

/** name_en / name_ru / slug → deck_index 0…77 (полная колода). */
function buildTarotNameToIdMap(): Record<string, number> {
  const map: Record<string, number> = {};
  const cards = (tarotMeta as { cards: TarotMetaCard[] }).cards ?? [];
  for (const card of cards) {
    const idx = card.deck_index;
    if (!Number.isFinite(idx) || idx < 0 || idx > 77) continue;
    const keys = [card.id, card.name_en, card.name_ru]
      .map((k) => normalizeTarotNameKey(k))
      .filter((k): k is string => Boolean(k));
    for (const k of keys) {
      if (map[k] == null) map[k] = idx;
    }
    // Common major aliases without leading "the "
    const en = normalizeTarotNameKey(card.name_en);
    if (en?.startsWith("the ")) {
      const short = en.slice(4);
      if (short && map[short] == null) map[short] = idx;
    }
  }
  // Extra major aliases used in legacy reference JSON
  const extras: Record<string, number> = {
    "the hanged man": 12,
    "hanged man": 12,
    "the hanged one": 12,
    "hanged one": 12,
    "wheel of fortune": 10,
    judgment: 20,
    judgement: 20,
  };
  for (const [k, v] of Object.entries(extras)) {
    if (map[k] == null) map[k] = v;
  }
  return map;
}

const TAROT_NAME_TO_ID: Record<string, number> = buildTarotNameToIdMap();

export function resolveTarotDeckIndexByName(name: string | null | undefined): number | null {
  const key = normalizeTarotNameKey(name);
  if (!key) return null;
  const id = TAROT_NAME_TO_ID[key];
  return id != null ? id : null;
}

function fnvHash32(dateISO: string): number {
  let h = 2166136261 >>> 0;
  for (let i = 0; i < dateISO.length; i++) {
    h ^= dateISO.charCodeAt(i);
    h = Math.imul(h, 16777619) >>> 0;
  }
  return h >>> 0;
}

/** Стабильный индекс 0…77 по дате (FNV-1a 32-bit) — паритет с iOS `stableDeckIndex`. */
export function stableTarotDeckIndexFromDateISO(dateISO: string): number {
  return fnvHash32(dateISO) % TAROT_FULL_DECK_COUNT;
}

/** Стабильный старший аркан 0…21 по той же базе FNV (как iOS `stableMajorArcanaId`). */
export function stableMajorArcanaIdFromDateISO(dateISO: string): number {
  return fnvHash32(dateISO) % 22;
}

/**
 * Индекс карты в колоде 0…77 для PNG и ритуала «карта дня».
 * Сначала id из утреннего слоя (если 0…77), затем имя (EN/RU/slug, вся колода), затем стабильный индекс по дате.
 */
export function resolveDailyTarotDeckIndex(args: {
  morningTarotCardId?: string | number | null;
  morningTarotName?: string | null;
  cardName: string;
  dateISO: string;
}): number {
  const rawId = args.morningTarotCardId;
  if (rawId != null && rawId !== "") {
    const n = typeof rawId === "number" ? rawId : parseInt(String(rawId), 10);
    if (Number.isFinite(n) && n >= 0 && n <= 77) return n;
  }
  const fromMorning = resolveTarotDeckIndexByName(args.morningTarotName);
  if (fromMorning != null) return fromMorning;
  const fromCard = resolveTarotDeckIndexByName(args.cardName);
  if (fromCard != null) return fromCard;
  return stableTarotDeckIndexFromDateISO(args.dateISO);
}
