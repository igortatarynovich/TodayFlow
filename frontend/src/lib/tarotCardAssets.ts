/**
 * Статические изображения колоды в `public/images/cards/tarot/`.
 * Полная колода: 22 старших аркана + 56 младших (4 масти × 14 карт, файлы 1.png…14.png).
 */

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

/** Имена как в `DATA/astrology_reference/tarot_major_arcana.json` (нижний регистр). */
const ENGLISH_MAJOR_NAME_TO_ID: Record<string, number> = {
  "the fool": 0,
  "the magician": 1,
  "the high priestess": 2,
  "the empress": 3,
  "the emperor": 4,
  "the hierophant": 5,
  "the lovers": 6,
  "the chariot": 7,
  strength: 8,
  "the hermit": 9,
  "wheel of fortune": 10,
  justice: 11,
  "the hanged one": 12,
  death: 13,
  temperance: 14,
  "the devil": 15,
  "the tower": 16,
  "the star": 17,
  "the moon": 18,
  "the sun": 19,
  judgement: 20,
  "the world": 21,
};

function normalizeTarotNameKey(raw: string | null | undefined): string | null {
  if (raw == null || typeof raw !== "string") return null;
  const t = raw.trim().toLowerCase();
  return t.length ? t : null;
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
 * Сначала id из утреннего слоя (если 0…77), затем имя старшего аркана (EN), затем стабильный индекс по дате.
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
  const k1 = normalizeTarotNameKey(args.morningTarotName);
  if (k1 && ENGLISH_MAJOR_NAME_TO_ID[k1] != null) return ENGLISH_MAJOR_NAME_TO_ID[k1]!;
  const k2 = normalizeTarotNameKey(args.cardName);
  if (k2 && ENGLISH_MAJOR_NAME_TO_ID[k2] != null) return ENGLISH_MAJOR_NAME_TO_ID[k2]!;
  return stableTarotDeckIndexFromDateISO(args.dateISO);
}

/** @deprecated Используйте `resolveDailyTarotDeckIndex` — оставлено для старых импортов. */
export function resolveDailyTarotMajorArcanaId(args: Parameters<typeof resolveDailyTarotDeckIndex>[0]): number {
  return resolveDailyTarotDeckIndex(args);
}
