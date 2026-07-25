/**
 * Tarot card assets — production path uses optimized web derivatives only.
 * Masters live in assets-source/tarot/masters/ (gitignored); rebuild via:
 *   python3 scripts/build-tarot-assets.py
 */

import tarotMeta from "@/data/tarotDeckIndex.json";
import tarotWebManifest from "@/data/tarotWebManifest.json";

const WEB_BASE = "/images/cards/tarot/web";

/** Full Waite-Smith deck size. */
export const TAROT_FULL_DECK_COUNT = 78;

/** Canonical face aspect (3:5). */
export const TAROT_CARD_ASPECT_RATIO = 3 / 5;

/** Logical CSS width of a ritual reveal card (density handled via srcSet). */
export const TAROT_RITUAL_REVEAL_MAX_WIDTH_PX = 220;

/** Spine thumbnail width. */
export const TAROT_SPINE_THUMB_WIDTH_PX = 76;

/** @deprecated Prefer aspect-ratio; kept for call-site height helpers. */
export const TAROT_CARD_PIXEL_WIDTH = 576;
/** @deprecated Prefer aspect-ratio. */
export const TAROT_CARD_PIXEL_HEIGHT = 960;

export type TarotWebSizeLabel = "384x640" | "576x960" | "768x1280";

type VariantPair = {
  avif: string;
  webp: string;
  width: number;
  height: number;
};

type ManifestCard = {
  deck_index: number;
  variants: Record<string, VariantPair>;
};

type Manifest = {
  public_base: string;
  back: { variants: Record<string, VariantPair> };
  cards: ManifestCard[];
};

const manifest = tarotWebManifest as Manifest;

const CARD_BY_INDEX = new Map<number, ManifestCard>(
  (manifest.cards ?? []).map((c) => [c.deck_index, c]),
);

export function tarotCardDisplayHeightPx(widthPx: number): number {
  return Math.round(widthPx / TAROT_CARD_ASPECT_RATIO);
}

function absWeb(rel: string): string {
  return `${WEB_BASE}/${rel.replace(/^\//, "")}`;
}

function sizeOrder(): TarotWebSizeLabel[] {
  return ["384x640", "576x960", "768x1280"];
}

export function tarotCardBackSrc(preferred: TarotWebSizeLabel = "576x960"): string {
  const v = manifest.back?.variants?.[preferred] ?? manifest.back?.variants?.["576x960"];
  if (!v) return `${WEB_BASE}/back-576x960.webp`;
  return absWeb(v.webp);
}

export function tarotCardFaceSrc(
  deckIndex: number,
  preferred: TarotWebSizeLabel = "576x960",
): string | null {
  if (!Number.isFinite(deckIndex) || deckIndex < 0 || deckIndex > 77) return null;
  const card = CARD_BY_INDEX.get(deckIndex);
  const v = card?.variants?.[preferred] ?? card?.variants?.["576x960"];
  if (!v) return null;
  return absWeb(v.webp);
}

export type TarotPictureSources = {
  /** Fallback <img src> (webp mid density). */
  src: string;
  avifSrcSet: string;
  webpSrcSet: string;
  width: number;
  height: number;
};

function buildPictureSources(variants: Record<string, VariantPair> | undefined): TarotPictureSources | null {
  if (!variants) return null;
  const avifParts: string[] = [];
  const webpParts: string[] = [];
  for (const label of sizeOrder()) {
    const v = variants[label];
    if (!v) continue;
    avifParts.push(`${absWeb(v.avif)} ${v.width}w`);
    webpParts.push(`${absWeb(v.webp)} ${v.width}w`);
  }
  const mid = variants["576x960"] ?? variants["384x640"] ?? variants["768x1280"];
  if (!mid || !webpParts.length) return null;
  return {
    src: absWeb(mid.webp),
    avifSrcSet: avifParts.join(", "),
    webpSrcSet: webpParts.join(", "),
    width: mid.width,
    height: mid.height,
  };
}

export function tarotCardFacePicture(deckIndex: number): TarotPictureSources | null {
  if (!Number.isFinite(deckIndex) || deckIndex < 0 || deckIndex > 77) return null;
  return buildPictureSources(CARD_BY_INDEX.get(deckIndex)?.variants);
}

export function tarotCardBackPicture(): TarotPictureSources {
  return (
    buildPictureSources(manifest.back?.variants) ?? {
      src: `${WEB_BASE}/back-576x960.webp`,
      avifSrcSet: "",
      webpSrcSet: `${WEB_BASE}/back-576x960.webp 576w`,
      width: 576,
      height: 960,
    }
  );
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
    const en = normalizeTarotNameKey(card.name_en);
    if (en?.startsWith("the ")) {
      const short = en.slice(4);
      if (short && map[short] == null) map[short] = idx;
    }
  }
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

export function stableTarotDeckIndexFromDateISO(dateISO: string): number {
  return fnvHash32(dateISO) % TAROT_FULL_DECK_COUNT;
}

export function stableMajorArcanaIdFromDateISO(dateISO: string): number {
  return fnvHash32(dateISO) % 22;
}

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
