/**
 * Glance «Энергия дня» — effect + cause from interpretive_chorus (not score buckets).
 * Canon: effect = lived body/tempo; cause = one sky/number line.
 */

import type { TodayContractV1 } from "@/lib/todayContract";

export type GlanceEnergyLine = {
  /** Effect headline — «тело просит паузы» */
  effect: string;
  /** Cause subtitle — «убывающая луна снижает запас сил» */
  cause: string | null;
  /** Combined single-line for compact Glance Block */
  line: string;
};

function clean(text: string | null | undefined): string {
  return (text ?? "").replace(/\s+/g, " ").trim();
}

function firstSentence(text: string): string {
  const parts = text.split(/(?<=[.!?])\s+/).map((s) => s.trim()).filter(Boolean);
  return parts[0] || text;
}

/**
 * Prefer chorus prose over numeric energy buckets.
 * Returns null when no usable effect — Glance honest-omits the Block.
 */
export function buildGlanceEnergyFromChorus(
  contract: TodayContractV1 | null | undefined,
): GlanceEnergyLine | null {
  if (!contract?.day_story) return null;
  const chorus = contract.day_story.interpretive_chorus;
  if (!chorus) return null;

  const effect =
    clean(chorus.astrology_meaning) ||
    clean(chorus.day_number?.for_conflict) ||
    clean(chorus.day_card?.role) ||
    "";
  if (!effect || effect.length < 12) return null;

  const cause =
    clean(chorus.astrology_lead) ||
    clean(chorus.day_number?.named) ||
    clean(chorus.day_number?.tempo) ||
    null;

  const effectShort = firstSentence(effect);
  const causeShort = cause ? firstSentence(cause) : null;
  // Avoid «cause: cause» when lead duplicates meaning.
  const causeFinal =
    causeShort &&
    causeShort.toLowerCase() !== effectShort.toLowerCase() &&
    !effectShort.toLowerCase().includes(causeShort.toLowerCase().slice(0, 24))
      ? causeShort
      : null;

  return {
    effect: effectShort,
    cause: causeFinal,
    line: causeFinal ? `${effectShort} · ${causeFinal}` : effectShort,
  };
}
