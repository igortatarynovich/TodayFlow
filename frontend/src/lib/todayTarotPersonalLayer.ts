/**
 * Tarot personal layer — card × daily focus × Personal Model slice.
 *
 * Card meaning comes from BE (`card_base_v1`), not FE theater bank.
 * Bank supplies name only.
 */

import { getTodayTarotCardRu } from "@/components/today/todayTarotCardsRu";

export type TarotPersonalLayer = {
  cardId: number;
  cardName: string;
  /** Card-as-trap for Day Map `whereYouBreak` / soften. */
  trapLine: string;
  /** One-scene body for ritual impact (focus + trap + move). */
  sceneBody: string;
  /** Short image-line for impact headline (not the generic «Символ дня»). */
  headline: string;
  /** True when focus and/or profile slice actually shaped the copy. */
  personalized: boolean;
};

function clean(text: string | null | undefined): string {
  return (text ?? "").replace(/\s+/g, " ").trim();
}

function ensurePeriod(text: string): string {
  const t = clean(text);
  if (!t) return "";
  return /[.!?…]$/.test(t) ? t : `${t}.`;
}

function firstSentence(text: string): string {
  const t = clean(text);
  if (!t) return "";
  const part = t.split(/(?<=[.!?…])\s+/).filter(Boolean)[0] ?? t;
  return ensurePeriod(part);
}

function clip(text: string, max: number): string {
  const t = clean(text);
  if (t.length <= max) return t;
  const cut = t.slice(0, max - 1);
  const sp = cut.lastIndexOf(" ");
  return `${(sp > 40 ? cut.slice(0, sp) : cut).trim()}…`;
}

function softenStyle(style: string): string {
  const t = clean(style).replace(/[.!?…]+$/g, "");
  if (!t) return "";
  return clip(t.charAt(0).toLowerCase() + t.slice(1), 90);
}

/**
 * Compose personal tarot layer. Returns null only when card id is unknown.
 * Without focus/profile still returns a name-anchored line (`personalized: false`).
 * Does not invent card prose when `cardMeaning` is missing.
 */
export function composeTarotPersonalLayer(input: {
  cardId: number;
  /** BE card_base meaning when available. */
  cardMeaning?: string | null;
  dailyFocusTitle?: string | null;
  dailyFocusId?: string | null;
  decisionStyle?: string | null;
  helpsFirst?: string | null;
}): TarotPersonalLayer | null {
  const card = getTodayTarotCardRu(input.cardId);
  if (!card) return null;

  const meaning = clean(input.cardMeaning);
  const dayFocus = clean(input.dailyFocusTitle);
  const style = softenStyle(input.decisionStyle ?? "");
  const help = clean(input.helpsFirst);
  const personalized = Boolean(dayFocus || style || help);

  let trapLine: string;
  if (style && meaning) {
    trapLine = ensurePeriod(
      `При твоём стиле («${style}») «${card.nameRu}» звучит так: ${firstSentence(meaning).replace(/[.!?…]$/, "")}`,
    );
  } else if (style) {
    trapLine = ensurePeriod(`«${card.nameRu}» сегодня проверяет стиль «${style}»`);
  } else if (meaning) {
    trapLine = ensurePeriod(`«${card.nameRu}»: ${firstSentence(meaning).replace(/[.!?…]$/, "")}`);
  } else {
    trapLine = ensurePeriod(`«${card.nameRu}» сегодня задаёт другой угол зрения`);
  }

  const sceneBits: string[] = [];
  if (dayFocus) {
    sceneBits.push(firstSentence(dayFocus));
  } else if (meaning) {
    sceneBits.push(firstSentence(meaning));
  }

  if (
    meaning &&
    dayFocus &&
    !sceneBits.some((b) => b.toLowerCase().includes(firstSentence(meaning).slice(0, 24).toLowerCase()))
  ) {
    sceneBits.push(firstSentence(meaning));
  }

  sceneBits.push(trapLine);

  if (help) {
    sceneBits.push(ensurePeriod(`Опора: ${clip(help, 120)}`));
  }

  const sceneBody = clip(sceneBits.join(" "), 420);
  const headline = dayFocus
    ? clip(firstSentence(dayFocus).replace(/[.!?…]$/, ""), 72)
    : clip(firstSentence(meaning).replace(/[.!?…]$/, "") || card.nameRu, 72);

  return {
    cardId: input.cardId,
    cardName: card.nameRu,
    trapLine,
    sceneBody,
    headline,
    personalized,
  };
}
