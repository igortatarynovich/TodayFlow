/**
 * Assemble one literary Today reading from contract + story — no checklist chrome.
 * Meaning comes from backend; this only selects and lightly shapes prose.
 */

import type { TodayContractDayStoryTraceClaimV1, TodayContractV1 } from "@/lib/todayContract";
import { isDomainLensPresent } from "@/lib/todayContract";
import type { TodayDayStoryViewModel } from "@/lib/todayDayStoryModel";
import { isRuUserFacingText } from "@/lib/todaySynthesisTextPolicy";

export type TodayLiteraryReading = {
  /** Opening observation (2–5 sentences preferred). */
  opening: string;
  /**
   * Soft “почему это важно сегодня” — meaning-facing claim only.
   * Never from kitchen limitations / confidence / fingerprint.
   */
  why: string | null;
  /** Where the day leans — one short paragraph, optional. */
  lean: string | null;
  /** Where to go gently — one short paragraph, optional. */
  ease: string | null;
  /** Quiet day anchor from talisman (color/stone/note) — woven prose, not a widget. */
  anchor: string | null;
  /** One practical close, human sentence — not a command chip. */
  close: string | null;
};

/** Claim kinds safe for user-facing soft why (not kitchen). */
const MEANING_CLAIM_KINDS = new Set([
  "axis",
  "action",
  "risk",
  "domain_focus",
  "tempo",
  "observation",
]);

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

function isKitchenClaimText(text: string): boolean {
  return /учтена как|не упоминать|чек-ин|fingerprint|calculation_version|evidence_id|source_inputs/i.test(
    text,
  );
}

function meaningClaimLine(claim: TodayContractDayStoryTraceClaimV1): string {
  const kind = String(claim.kind || "observation").trim().toLowerCase();
  if (!MEANING_CLAIM_KINDS.has(kind)) return "";
  if (kind === "symbol" || kind === "mood") return "";
  const text = clean(claim.text);
  if (!text || !isRuUserFacingText(text) || isKitchenClaimText(text)) return "";
  return text;
}

/**
 * Soft why only from meaning-facing derived_claims.
 * No fallback to practice_recommendation.reason / advantage / limitations —
 * if claims are absent, the Why block disappears.
 */
export function pickSoftWhyLine(contract: TodayContractV1, used: string[] = []): string | null {
  const claims = contract.day_story?.trace?.derived_claims ?? [];
  for (const claim of claims) {
    const line = meaningClaimLine(claim);
    if (line && distinctEnough(line, used)) return firstParagraph(line, 2);
  }
  return null;
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

  const why = pickSoftWhyLine(contract, used);
  if (why) used.push(why);

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

  const talisman = dayStory?.talisman;
  const color = clean(talisman?.color);
  const stone = clean(talisman?.stone);
  const note = clean(talisman?.note);
  let anchor: string | null = null;
  if (color || stone || note) {
    const parts: string[] = [];
    if (color && stone) parts.push(`Сегодняшний якорь — ${color} и ${stone}`);
    else if (color) parts.push(`Сегодняшний якорь — оттенок «${color}»`);
    else if (stone) parts.push(`Сегодняшний якорь — ${stone}`);
    if (note && distinctEnough(note, used)) parts.push(note);
    const joined = parts.join(". ").trim();
    if (joined && distinctEnough(joined, used)) {
      anchor = firstParagraph(joined.endsWith(".") ? joined : `${joined}.`, 2);
      used.push(anchor);
    }
  }

  const closeRaw = [
    clean(dayStory?.today_move),
    clean(contract.primary_action),
  ].find((t) => t && isRuUserFacingText(t) && distinctEnough(t, used));

  const close = closeRaw ? softenCommandLead(firstParagraph(closeRaw, 1)) : null;

  return { opening, why, lean, ease, anchor, close };
}
