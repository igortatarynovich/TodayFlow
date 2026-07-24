/**
 * Tarot personal layer — card × daily focus × Personal Model slice.
 *
 * Generic copy stays in `todayTarotCardsRu.ts`. This composer folds the card
 * into the day as the trap turn (§0.3), not as a separate “влияние карты” block.
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
  // Keep a short clause usable inside «при твоём стиле …»
  return clip(t.charAt(0).toLowerCase() + t.slice(1), 90);
}

/**
 * Compose personal tarot layer. Returns null only when card id is unknown.
 * Without focus/profile still returns card-quality copy (`personalized: false`).
 */
export function composeTarotPersonalLayer(input: {
  cardId: number;
  dailyFocusTitle?: string | null;
  dailyFocusId?: string | null;
  decisionStyle?: string | null;
  helpsFirst?: string | null;
}): TarotPersonalLayer | null {
  const card = getTodayTarotCardRu(input.cardId);
  if (!card) return null;

  const risk = clean(card.riskRu);
  const move = clean(card.focusRu);
  const lead = clean(card.leadRu);
  const body = clean(card.bodyRu);
  const dayFocus = clean(input.dailyFocusTitle);
  const style = softenStyle(input.decisionStyle ?? "");
  const help = clean(input.helpsFirst);
  const personalized = Boolean(dayFocus || style || help);

  let trapLine: string;
  if (risk && style) {
    trapLine = ensurePeriod(
      `При твоём стиле («${style}») «${card.nameRu}» легко скатывается в ${risk}`,
    );
  } else if (risk) {
    trapLine = ensurePeriod(`Ловушка «${card.nameRu}»: ${risk}`);
  } else if (style) {
    trapLine = ensurePeriod(
      `«${card.nameRu}» сегодня проверяет стиль «${style}» — ${firstSentence(body || lead).replace(/[.!?…]$/, "")}`,
    );
  } else {
    trapLine = ensurePeriod(
      firstSentence(body || lead) || `«${card.nameRu}» сегодня задаёт другой угол зрения`,
    );
  }

  const sceneBits: string[] = [];
  if (dayFocus) {
    sceneBits.push(firstSentence(dayFocus));
  } else if (lead) {
    sceneBits.push(firstSentence(lead));
  }

  // Card body as scene middle — one sentence, not a second block.
  const bodyBit = firstSentence(body);
  if (bodyBit && !sceneBits.some((b) => b.toLowerCase().includes(bodyBit.slice(0, 24).toLowerCase()))) {
    sceneBits.push(bodyBit);
  }

  sceneBits.push(trapLine);

  if (move) {
    sceneBits.push(ensurePeriod(move.charAt(0).toUpperCase() + move.slice(1)));
  } else if (help) {
    sceneBits.push(ensurePeriod(`Опора: ${clip(help, 120)}`));
  }

  const sceneBody = clip(sceneBits.join(" "), 420);
  const headline = dayFocus
    ? clip(firstSentence(dayFocus).replace(/[.!?…]$/, ""), 72)
    : clip(firstSentence(lead).replace(/[.!?…]$/, "") || card.nameRu, 72);

  return {
    cardId: input.cardId,
    cardName: card.nameRu,
    trapLine,
    sceneBody,
    headline,
    personalized,
  };
}
