/**
 * P0.2.1 — Unified day synthesis: one "dish", not ingredient dumps.
 * Weaves card + number + contract narrative + profile slice into flowing RU copy.
 */

import type { TodayContractV1 } from "@/lib/todayContract";
import { getTodayTarotCardRu, type TodayTarotCardRu } from "@/components/today/todayTarotCardsRu";
import { buildTodayNarrativeV1, splitPeriodNarrative } from "@/lib/todayNarrativeFromContract";
import {
  isGenericRhythmCliche,
  isRuUserFacingText,
  polishDayHeadline,
  resolveTodayThemeHeadline,
} from "@/lib/todaySynthesisTextPolicy";

export type TodayUnifiedSynthesis = {
  eyebrow: string;
  headline: string;
  paragraphs: string[];
  eveningPrompt: string;
};

const STABILITY_MARKERS = ["устойчив", "ритм", "ровн", "последователь", "спокойн"];
const CHANGE_TAROT_IDS = new Set([13, 16, 0]); // Death, Tower, Fool — disruption / shift tone

function norm(text: string): string {
  return text.replace(/\s+/g, " ").trim();
}

function uniqueParagraphs(lines: string[], max = 4): string[] {
  const out: string[] = [];
  for (const line of lines) {
    const t = norm(line);
    if (!t || !isRuUserFacingText(t)) continue;
    const dup = out.some((x) => {
      const a = x.toLowerCase();
      const b = t.toLowerCase();
      return a === b || a.includes(b.slice(0, 40)) || b.includes(a.slice(0, 40));
    });
    if (!dup) out.push(t.endsWith(".") || t.endsWith("?") || t.endsWith("!") ? t : `${t}.`);
    if (out.length >= max) break;
  }
  return out;
}

function narrativeString(payload: Record<string, unknown> | null | undefined, key: string): string | null {
  if (!payload || typeof payload !== "object") return null;
  const v = payload[key];
  return typeof v === "string" && v.trim() ? v.trim() : null;
}

function periodSignalsStability(period: string): boolean {
  const low = period.toLowerCase();
  return STABILITY_MARKERS.some((m) => low.includes(m));
}

function tarotSignalsChange(cardId: number | null): boolean {
  if (cardId == null) return false;
  return CHANGE_TAROT_IDS.has(cardId);
}

function pickProfileTension(
  guidePayload: Record<string, unknown> | null,
  personalObservation: string | null | undefined,
): string | null {
  const candidates = [
    personalObservation,
    narrativeString(guidePayload, "personal_insight_body"),
    narrativeString(guidePayload, "personal_observation"),
    narrativeString(guidePayload, "profile_slice"),
    narrativeString(guidePayload, "life_path_note"),
  ];
  for (const c of candidates) {
    if (c && isRuUserFacingText(c)) return norm(c);
  }
  return null;
}

export function buildTarotWeaveParagraph(
  card: TodayTarotCardRu,
  cardId: number,
  periodStable: boolean,
): string {
  const name = card.nameRu;
  if (tarotSignalsChange(cardId) && periodStable) {
    return (
      `Карта дня — ${name} — может подталкивать к переменам и быстрым решениям. ` +
      "Но фокус дня скорее про устойчивый ритм: не расширяй поле внимания. " +
      "Вместо новых направлений сосредоточься на том, что уже находится перед тобой."
    );
  }
  const lead = norm(card.leadRu);
  const body = norm(card.bodyRu);
  if (lead && body && lead !== body) {
    return `${lead} ${body}`;
  }
  return lead || body;
}

export function buildNumberWeaveParagraph(numerologyValue: string, numerologyMeaning: string): string | null {
  const meaning = norm(numerologyMeaning);
  if (!isRuUserFacingText(meaning)) return null;
  if (meaning.toLowerCase().includes("число дня")) {
    return meaning;
  }
  return `Число дня ${numerologyValue} напоминает: ${meaning.replace(/\.$/, "")}.`;
}

function buildProfileWeaveParagraph(profileLine: string, mood: string | null): string | null {
  const low = profileLine.toLowerCase();
  if (low.includes("сужай поле") || low.includes("устал")) {
    return (
      "Твой текущий период говорит об обратном: когда ресурс ниже, поле внимания лучше сужать. " +
      "Не бери на себя всё — выбери один живой вектор и держи его ровно."
    );
  }
  if (mood && ["tired", "anxious", "low", "устал", "тревож"].some((m) => mood.includes(m) || low.includes(m))) {
    return `${profileLine} Сегодня это особенно важно учитывать — не требуй от себя темпа, который день не поддерживает.`;
  }
  return profileLine;
}

const EVENING_PROMPTS_THEMATIC = [
  "Что сегодня изменило твой взгляд на ситуацию?",
  "Что сегодня оказалось совсем не таким, как ты ожидал утром?",
  "Что сегодня стоило отпустить раньше?",
  "Что сегодня дало больше ясности — даже если план изменился?",
];

export function buildEveningPrompt({
  dateISO,
  tarotCard,
}: {
  dateISO: string;
  tarotCard: TodayTarotCardRu | undefined;
}): string {
  if (tarotCard?.eveningRu && isRuUserFacingText(tarotCard.eveningRu)) {
    return tarotCard.eveningRu.trim();
  }
  const seed = dateISO.split("-").reduce((acc, p) => acc + Number(p || 0), 0);
  return EVENING_PROMPTS_THEMATIC[Math.abs(seed) % EVENING_PROMPTS_THEMATIC.length];
}

export function buildTodayUnifiedSynthesis({
  contract,
  guidePayload,
  tarotMainId,
  numerologyValue,
  numerologyMeaning,
  personalObservation,
  mood,
  dateISO,
  eyebrow,
}: {
  contract: TodayContractV1;
  guidePayload: Record<string, unknown> | null;
  tarotMainId: number | null;
  numerologyValue: string;
  numerologyMeaning: string;
  personalObservation?: string | null;
  mood?: string | null;
  dateISO: string;
  eyebrow: string;
}): TodayUnifiedSynthesis {
  const narrative = buildTodayNarrativeV1(contract);
  const period = contract.global_context.period;
  const split = splitPeriodNarrative(period);

  let headline = resolveTodayThemeHeadline(contract);
  if (!isRuUserFacingText(headline)) {
    headline = polishDayHeadline(period, narrative.growthPoint);
  }
  if (isGenericRhythmCliche(headline)) {
    headline = polishDayHeadline(period, narrative.growthPoint);
  }

  const periodStable = periodSignalsStability(period);
  const tarotCard = tarotMainId != null ? getTodayTarotCardRu(tarotMainId) : undefined;

  const paragraphCandidates: string[] = [];

  const subline = split.subline && isRuUserFacingText(split.subline) ? norm(split.subline) : null;
  if (subline && !subline.toLowerCase().includes(headline.toLowerCase().slice(0, 24))) {
    paragraphCandidates.push(subline);
  } else if (isRuUserFacingText(narrative.growthPoint)) {
    paragraphCandidates.push(norm(narrative.growthPoint));
  }

  if (tarotCard && tarotMainId != null) {
    paragraphCandidates.push(buildTarotWeaveParagraph(tarotCard, tarotMainId, periodStable));
  }

  const numberPara = buildNumberWeaveParagraph(numerologyValue, numerologyMeaning);
  if (numberPara) paragraphCandidates.push(numberPara);

  const profileLine = pickProfileTension(guidePayload, personalObservation);
  if (profileLine) {
    const woven = buildProfileWeaveParagraph(profileLine, mood ?? null);
    if (woven) paragraphCandidates.push(woven);
  }

  const manifestations = narrative.manifestations.map((m) => m.line).filter(isRuUserFacingText);
  if (manifestations.length > 0) {
    paragraphCandidates.push(
      `В разных сферах это может проявиться так: ${manifestations[0].replace(/\.$/, "")}.`,
    );
  }

  const paragraphs = uniqueParagraphs(paragraphCandidates, 4);

  return {
    eyebrow,
    headline,
    paragraphs,
    eveningPrompt: buildEveningPrompt({ dateISO, tarotCard }),
  };
}
