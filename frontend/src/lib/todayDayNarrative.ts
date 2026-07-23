/**
 * Assemble Today's day as continuous narrative chapters from existing fields only.
 * Order: story → sky why → strengthen/weaken → card/number layer → supports.
 * No invented meaning — only selection, light join, and structural kickers.
 */

import type { MorningRitualData } from "@/components/today/todayPageUtils";
import type { TodayContractV1 } from "@/lib/todayContract";
import { isDomainLensPresent } from "@/lib/todayContract";
import { dayStoryAvoidItems, dayStoryDoItems } from "@/lib/todayContractMapper";
import type { TodayDayColorGuide } from "@/lib/todayDayColorGuide";
import type { TodaySkyCard } from "@/lib/todayDaySpine";
import type { TodayDayStoryViewModel } from "@/lib/todayDayStoryModel";
import {
  buildTodayLiteraryReading,
  pickSoftWhyLine,
} from "@/lib/todayLiteraryReading";
import { isRuUserFacingText } from "@/lib/todaySynthesisTextPolicy";

export type TodayDayNarrativeChapter = {
  id: "opening" | "sky" | "force" | "symbols" | "supports";
  kicker: string;
  paragraphs: string[];
};

export type TodayDayNarrative = {
  theme: string | null;
  /** Soft why line when present — for a11y/test hooks inside opening. */
  softWhy: string | null;
  chapters: TodayDayNarrativeChapter[];
};

const DOMAIN_LABELS: Record<string, string> = {
  relationships: "В отношениях",
  money_work: "В работе и деньгах",
  family: "В семье и доме",
};

function clean(text: string | null | undefined): string {
  return (text ?? "").replace(/\s+/g, " ").trim();
}

function ensurePeriod(text: string): string {
  const t = clean(text);
  if (!t) return "";
  return /[.!?…]$/.test(t) ? t : `${t}.`;
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

function pushDistinct(out: string[], used: string[], line: string | null | undefined): void {
  const t = clean(line);
  if (!t || !isRuUserFacingText(t)) return;
  const paragraph = ensurePeriod(t);
  if (!distinctEnough(paragraph, used)) return;
  used.push(paragraph);
  out.push(paragraph);
}

function titledStory(title: string | null | undefined, story: string | null | undefined): string {
  const body = clean(story);
  const head = clean(title);
  if (!body) return "";
  if (!head) return ensurePeriod(body);
  if (body.toLowerCase().includes(head.toLowerCase().slice(0, Math.min(12, head.length)))) {
    return ensurePeriod(body);
  }
  return ensurePeriod(`${head}. ${body}`);
}

/** Prefer mercury / personal ingresses first, then the rest — still only API story_ru. */
function collectSkyParagraphs(input: {
  morningRitualData: MorningRitualData | null | undefined;
  skyCards: TodaySkyCard[];
}): string[] {
  const celestial = input.morningRitualData?.celestial_events;
  const paragraphs: string[] = [];
  const used: string[] = [];

  const lunar = celestial?.lunar_phase;
  if (lunar?.name) {
    const lunarBody = clean(lunar.guidance) || clean(lunar.themes);
    pushDistinct(
      paragraphs,
      used,
      lunarBody
        ? `Луна сейчас — ${lunar.name}: ${lunarBody}`
        : `Луна сейчас — ${lunar.name}`,
    );
    const next = lunar.next_phase;
    if (next?.name && typeof next.in_days === "number" && next.in_days >= 0) {
      pushDistinct(
        paragraphs,
        used,
        next.in_days === 0
          ? `Ближайший переход луны — ${next.name}, уже сегодня.`
          : `Ближайший переход луны — ${next.name}, через ${next.in_days} дн.`,
      );
    }
  }

  const ingresses = celestial?.ingresses ?? [];
  const sortedIngresses = [...ingresses].sort((a, b) => {
    const score = (p: string | undefined) =>
      /меркур/i.test(p || "") ? 0 : /лун/i.test(p || "") ? 1 : 2;
    return score(a.planet_ru) - score(b.planet_ru);
  });
  for (const ingress of sortedIngresses.slice(0, 3)) {
    pushDistinct(paragraphs, used, clean(ingress.story_ru) || titledStory(
      ingress.planet_ru && ingress.sign_ru ? `${ingress.planet_ru} → ${ingress.sign_ru}` : ingress.planet_ru,
      ingress.story_ru,
    ));
  }

  for (const transit of (celestial?.personal_transits ?? []).slice(0, 2)) {
    pushDistinct(paragraphs, used, titledStory(transit.title, transit.story_ru));
  }

  for (const aspect of (celestial?.sky_aspects ?? []).slice(0, 2)) {
    pushDistinct(paragraphs, used, titledStory(aspect.title, aspect.story_ru));
  }

  for (const retro of (celestial?.retrogrades ?? []).slice(0, 2)) {
    pushDistinct(paragraphs, used, titledStory(retro.planet_ru, retro.story_ru));
  }

  // Fallback / supplement from spine sky cards (non-symbol, non-talisman duplicates).
  const skipIds = new Set(["tarot", "number", "color", "stone", "totem"]);
  for (const card of input.skyCards) {
    if (skipIds.has(card.id)) continue;
    pushDistinct(paragraphs, used, titledStory(card.title, card.story));
  }

  return paragraphs.slice(0, 8);
}

function collectForceParagraphs(
  contract: TodayContractV1,
  literary: ReturnType<typeof buildTodayLiteraryReading>,
  used: string[],
): string[] {
  const out: string[] = [];

  if (literary.lean) pushDistinct(out, used, literary.lean);
  if (literary.ease) pushDistinct(out, used, literary.ease);

  for (const id of ["relationships", "money_work", "family"] as const) {
    const lens = contract.domains[id];
    if (!isDomainLensPresent(lens)) continue;
    const label = DOMAIN_LABELS[id];
    const parts: string[] = [];
    if (clean(lens.opportunity)) parts.push(`сильнее — ${clean(lens.opportunity)}`);
    if (clean(lens.risk)) parts.push(`слабее / риск — ${clean(lens.risk)}`);
    if (clean(lens.action) && parts.length < 2) parts.push(clean(lens.action));
    if (!parts.length && clean(lens.status)) parts.push(clean(lens.status));
    if (parts.length) pushDistinct(out, used, `${label}: ${parts.join("; ")}`);
  }

  const doItems = dayStoryDoItems(contract).slice(0, 3);
  if (doItems.length) {
    pushDistinct(out, used, `Что усиливает день: ${doItems.join("; ")}`);
  }
  const avoidItems = dayStoryAvoidItems(contract).slice(0, 3);
  if (avoidItems.length) {
    pushDistinct(out, used, `Что сегодня ослабляет или лучше не дожимать: ${avoidItems.join("; ")}`);
  }

  if (literary.close) pushDistinct(out, used, literary.close);

  return out;
}

function collectSymbolParagraphs(story: TodayDayStoryViewModel, contract: TodayContractV1, used: string[]): string[] {
  const out: string[] = [];
  const tarot = story.tarotImpact;
  if (tarot) {
    const title = clean(tarot.title);
    const head = clean(tarot.headline);
    const body = clean(tarot.body);
    if (title || head || body) {
      const lead = title && head ? `Карта дня — ${title}. ${head}` : title ? `Карта дня — ${title}` : head;
      pushDistinct(out, used, lead);
      if (body) pushDistinct(out, used, body);
    }
  }

  const number = story.numberImpact;
  if (number) {
    const title = clean(number.title);
    const head = clean(number.headline);
    const body = clean(number.body);
    if (title || head || body) {
      const lead = title && head ? `Число дня — ${title}. ${head}` : title ? `Число дня — ${title}` : head;
      pushDistinct(out, used, lead);
      if (body) pushDistinct(out, used, body);
    }
  }

  pushDistinct(out, used, contract.day_story?.symbolic_note);

  return out;
}

function collectSupportParagraphs(
  contract: TodayContractV1,
  colorGuide: TodayDayColorGuide | null | undefined,
  used: string[],
): string[] {
  const out: string[] = [];
  const talisman = contract.day_story?.talisman;

  if (colorGuide) {
    const colorBits = [
      colorGuide.name ? `Цвет дня — ${colorGuide.name}` : "",
      clean(colorGuide.benefit),
      clean(colorGuide.clothing),
    ].filter(Boolean);
    if (colorBits.length) pushDistinct(out, used, colorBits.join(". "));
  } else if (talisman?.color) {
    pushDistinct(out, used, `Цвет дня — ${talisman.color}`);
  }

  if (talisman?.stone) {
    const stoneLine = talisman.note
      ? `Камень-опора — ${talisman.stone}. ${talisman.note}`
      : `Камень-опора — ${talisman.stone}`;
    pushDistinct(out, used, stoneLine);
  } else if (talisman?.note) {
    pushDistinct(out, used, talisman.note);
  }

  const practice = contract.day_story?.practice_recommendation;
  if (practice?.text) {
    const line = practice.reason
      ? `${practice.text} ${practice.reason}`
      : practice.text;
    pushDistinct(out, used, line);
  }

  return out;
}

export function buildTodayDayNarrative(input: {
  contract: TodayContractV1;
  story: TodayDayStoryViewModel;
  morningRitualData?: MorningRitualData | null;
  colorGuide?: TodayDayColorGuide | null;
}): TodayDayNarrative {
  const { contract, story } = input;
  const literary = buildTodayLiteraryReading(story, contract);
  const used: string[] = [];
  const chapters: TodayDayNarrativeChapter[] = [];

  const theme =
    clean(contract.day_story?.theme) ||
    clean(story.hero.themeShort) ||
    null;

  const openingParas: string[] = [];
  if (literary.opening) {
    // Split opening into short paragraphs for readable storytelling.
    const parts = literary.opening.split(/(?<=[.!?…])\s+/).filter(Boolean);
    if (parts.length <= 2) {
      pushDistinct(openingParas, used, literary.opening);
    } else {
      pushDistinct(openingParas, used, parts.slice(0, 2).join(" "));
      pushDistinct(openingParas, used, parts.slice(2).join(" "));
    }
  }
  const why = pickSoftWhyLine(contract, used);
  let softWhy: string | null = null;
  if (why) {
    softWhy = ensurePeriod(why);
    pushDistinct(openingParas, used, why);
  }
  if (openingParas.length) {
    chapters.push({ id: "opening", kicker: "Как звучит этот день", paragraphs: openingParas });
  }

  const skyParas = collectSkyParagraphs({
    morningRitualData: input.morningRitualData,
    skyCards: story.skyCards ?? [],
  }).filter((p) => distinctEnough(p, used));
  for (const p of skyParas) used.push(p);
  if (skyParas.length) {
    chapters.push({
      id: "sky",
      kicker: "Почему именно так — небо и переходы",
      paragraphs: skyParas,
    });
  }

  const forceParas = collectForceParagraphs(contract, literary, used);
  if (forceParas.length) {
    chapters.push({
      id: "force",
      kicker: "Что усилит и что ослабит",
      paragraphs: forceParas,
    });
  }

  const symbolParas = collectSymbolParagraphs(story, contract, used);
  if (symbolParas.length) {
    chapters.push({
      id: "symbols",
      kicker: "Слой карты и числа",
      paragraphs: symbolParas,
    });
  }

  const supportParas = collectSupportParagraphs(contract, input.colorGuide ?? story.colorGuide, used);
  if (supportParas.length) {
    chapters.push({
      id: "supports",
      kicker: "Опоры дня",
      paragraphs: supportParas,
    });
  }

  return { theme, softWhy, chapters };
}
