/**
 * Assemble one literary Today reading from contract + story — no checklist chrome.
 * Meaning comes from backend; this only selects and lightly shapes prose.
 */

import type { TodayContractV1 } from "@/lib/todayContract";
import { isDomainLensPresent } from "@/lib/todayContract";
import type { TodayDayStoryViewModel } from "@/lib/todayDayStoryModel";
import { isRuUserFacingText } from "@/lib/todaySynthesisTextPolicy";

export type TodayLiteraryReading = {
  /** Opening observation (2–5 sentences preferred). */
  opening: string;
  /** Where the day leans — one short paragraph, optional. */
  lean: string | null;
  /** Where to go gently — one short paragraph, optional. */
  ease: string | null;
  /** One practical close, human sentence — not a command chip. */
  close: string | null;
};

function clean(text: string | null | undefined): string {
  return (text ?? "").replace(/\s+/g, " ").trim();
}

function firstParagraph(text: string, maxSentences = 4): string {
  const parts = text.split(/(?<=[.!?…])\s+/).filter(Boolean);
  if (!parts.length) return text;
  return parts.slice(0, maxSentences).join(" ").trim();
}

function distinctEnough(candidate: string, used: string[]): boolean {
  const norm = candidate.toLowerCase().replace(/[^a-zа-яё0-9]+/gi, " ").trim();
  if (norm.length < 12) return false;
  return !used.some((u) => {
    const un = u.toLowerCase().replace(/[^a-zа-яё0-9]+/gi, " ").trim();
    if (!un) return false;
    if (un.includes(norm) || norm.includes(un)) return true;
    const a = new Set(norm.split(" ").filter((w) => w.length > 3));
    const b = un.split(" ").filter((w) => w.length > 3);
    const overlap = b.filter((w) => a.has(w)).length;
    return overlap >= Math.min(4, Math.ceil(b.length * 0.55));
  });
}

/** Soften leading imperatives into observation when the whole line is a command. */
function softenCommandLead(text: string): string {
  const t = clean(text);
  if (!t) return "";
  // Keep as-is if already observational.
  if (!/^(выбери|сделай|направ|опира|держи|закрой|заверши|не\s+)/i.test(t)) return t;
  // Convert "Выбери X" → softer close without inventing new meaning.
  return t.replace(/^выбери\s+/i, "Если получится — ").replace(/^сделай\s+/i, "Имеет смысл ");
}

export function buildTodayLiteraryReading(
  story: TodayDayStoryViewModel,
  contract: TodayContractV1,
): TodayLiteraryReading {
  const used: string[] = [];
  const dayStory = contract.day_story;

  const openingCandidates = [
    clean(dayStory?.story),
    clean(story.pulse),
    clean(dayStory?.direction),
    clean(contract.global_context?.period),
  ].filter((t) => t && isRuUserFacingText(t));

  let opening = openingCandidates[0] ?? "";
  if (opening) {
    opening = firstParagraph(opening, 5);
    used.push(opening);
  }

  const peak = story.sphereFocus.cards.find((c) => c.role === "peak");
  const leanRaw = [
    clean(dayStory?.advantage),
    clean(peak?.body),
    isDomainLensPresent(contract.domains.relationships)
      ? clean(contract.domains.relationships.opportunity)
      : "",
    isDomainLensPresent(contract.domains.money_work)
      ? clean(contract.domains.money_work.opportunity)
      : "",
  ].find((t) => t && isRuUserFacingText(t) && distinctEnough(t, used));

  const lean = leanRaw ? firstParagraph(leanRaw, 2) : null;
  if (lean) used.push(lean);

  const caution = story.sphereFocus.cards.find((c) => c.role === "caution");
  const easeRaw = [
    clean(dayStory?.abstain),
    clean(caution?.releaseLine),
    clean(caution?.body),
    isDomainLensPresent(contract.domains.family) ? clean(contract.domains.family.risk) : "",
  ].find((t) => t && isRuUserFacingText(t) && distinctEnough(t, used));

  const ease = easeRaw ? firstParagraph(easeRaw, 2) : null;
  if (ease) used.push(ease);

  const closeRaw = [
    clean(dayStory?.today_move),
    clean(contract.primary_action),
  ].find((t) => t && isRuUserFacingText(t) && distinctEnough(t, used));

  const close = closeRaw ? softenCommandLead(firstParagraph(closeRaw, 1)) : null;

  return { opening, lean, ease, close };
}
