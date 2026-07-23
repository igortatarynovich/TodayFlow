/**
 * Ritual symbols (day number / day card) are a probabilistic layer AFTER user pick.
 * Strip mentions from any pre-ritual surface so they cannot leak via day_story prose.
 */

export type RitualRevealState = {
  numberRevealed: boolean;
  tarotRevealed: boolean;
};

const NUMBER_SENTENCE =
  /(?:^|[.!?…]\s+)(?=[^.!?…]*(?:число\s*дня|число\s+\d{1,2}|день\s*[—–-]?\s*\d{1,2}\b|\b\d{1,2}\s*:\s*ритм))[^.!?…]+[.!?…]?/giu;

const TAROT_SENTENCE =
  /(?:^|[.!?…]\s+)(?=[^.!?…]*(?:карта\s*дня|аркан|тар[оо]))[^.!?…]+[.!?…]?/giu;

function splitKeep(text: string): string[] {
  const parts = text.match(/[^.!?…]+[.!?…]?/gu);
  return parts?.map((p) => p.trim()).filter(Boolean) ?? [];
}

function sentenceMentionsNumber(s: string): boolean {
  return /число\s*дня|число\s+\d{1,2}|\bдень\s*[—–-]\s*\d{1,2}\b|\b\d{1,2}\s*:\s*ритм/i.test(s);
}

function sentenceMentionsTarot(s: string): boolean {
  return /карта\s*дня|аркан|тар[оо]/i.test(s);
}

/**
 * Remove sentences that name the day number / day card when those are unrevealed.
 * Does not invent replacement prose — drops the leaking sentence.
 */
export function redactUnrevealedRitualProse(
  text: string | null | undefined,
  reveal: RitualRevealState,
): string {
  const raw = (text ?? "").replace(/\s+/g, " ").trim();
  if (!raw) return "";
  if (reveal.numberRevealed && reveal.tarotRevealed) return raw;

  const kept = splitKeep(raw).filter((sentence) => {
    if (!reveal.numberRevealed && sentenceMentionsNumber(sentence)) return false;
    if (!reveal.tarotRevealed && sentenceMentionsTarot(sentence)) return false;
    return true;
  });

  return kept.join(" ").replace(/\s+/g, " ").trim();
}

/** Prefer a short theme line for hero before ritual; never a story dump. */
export function pickPreRitualHeroTitle(
  theme: string | null | undefined,
  fallback: string,
  reveal: RitualRevealState,
): string {
  const cleanTheme = redactUnrevealedRitualProse(theme, reveal);
  if (cleanTheme && cleanTheme.length <= 96) return cleanTheme;
  const cleanFallback = redactUnrevealedRitualProse(fallback, reveal);
  if (cleanFallback) {
    const first = splitKeep(cleanFallback)[0] ?? cleanFallback;
    return first.length <= 140 ? first : `${first.slice(0, 137)}…`;
  }
  return "Сегодняшняя линия дня";
}

export function isRitualProseClean(
  text: string | null | undefined,
  reveal: RitualRevealState,
): boolean {
  const raw = (text ?? "").trim();
  if (!raw) return true;
  return redactUnrevealedRitualProse(raw, reveal) === raw.replace(/\s+/g, " ").trim();
}

/** Test helpers — exported patterns for unit coverage. */
export const __ritualSanitizePatterns = { NUMBER_SENTENCE, TAROT_SENTENCE };
