/**
 * Assemble Today's day narrative.
 * Prefer Day Map slots (guide interpretation or day_story structured fields)
 * over stacking astro/lunar/personal fact chapters.
 */

import type { MorningRitualData } from "@/components/today/todayPageUtils";
import type { TodayContractV1, TodayDayFoundationV1 } from "@/lib/todayContract";
import { isDomainLensPresent } from "@/lib/todayContract";
import { dayStoryAvoidItems, dayStoryDoItems } from "@/lib/todayContractMapper";
import type { TodayDayColorGuide } from "@/lib/todayDayColorGuide";
import { buildTodayDayMap, type TodayDayMap } from "@/lib/todayDayMap";
import type { TodaySkyCard } from "@/lib/todayDaySpine";
import type { TodayDayStoryViewModel } from "@/lib/todayDayStoryModel";
import {
  buildTodayLiteraryReading,
  pickSoftWhyLine,
} from "@/lib/todayLiteraryReading";
import { isRuUserFacingText } from "@/lib/todaySynthesisTextPolicy";

export type TodayDayNarrativeChapterId =
  | "opening"
  | "astro"
  | "lunar"
  | "personal"
  | "electional"
  | "sky"
  | "force"
  | "symbols"
  | "supports";

/** Compact glance row for Day Personal — not a chip cluster. */
export type TodayDayPersonalSignal = {
  label: string;
  value: string;
};

/** Soft checklist row for electional / horary chapter. */
export type TodayDayElectionalCheck = {
  id: string;
  status: string;
  title: string;
  story?: string | null;
};

export type TodayDayNarrativeChapter = {
  id: TodayDayNarrativeChapterId;
  kicker: string;
  paragraphs: string[];
  lead?: string | null;
  /** Visual accent for ProductNarrativeBlock. */
  accent?: "default" | "dual" | "support" | "sky";
  planetHint?: string | null;
  colorHex?: string | null;
  colorLabel?: string | null;
  dual?: { strengthen: string[]; soften: string[] } | null;
  /** Soft L3 glance signals (personal chapter only). */
  signals?: TodayDayPersonalSignal[] | null;
  /** Soft elective/horary checklist (electional chapter only). */
  checklist?: TodayDayElectionalCheck[] | null;
  collapseAfter?: number;
};

export type TodayDayNarrative = {
  theme: string | null;
  softWhy: string | null;
  chapters: TodayDayNarrativeChapter[];
  foundation: TodayDayFoundationV1 | null;
  /** Canonical Day Map when resolved — UI should prefer this over chapter dumps. */
  dayMap: TodayDayMap | null;
};

const DOMAIN_LABELS: Record<string, string> = {
  relationships: "В отношениях",
  money_work: "В работе и деньгах",
  family: "В семье и доме",
};

/** Best-effort chip color from catalog name — decorative only, not meaning. */
export function colorHexForDayName(name: string | null | undefined): string | null {
  const n = (name ?? "").trim().toLowerCase();
  if (!n) return null;
  const map: Array<[RegExp, string]> = [
    [/лазур|azure|голуб/, "#5B8FA8"],
    [/глубок.*син|deep.*blue/, "#1E3A5F"],
    [/индиго|indigo/, "#3F3D7A"],
    [/изумруд|emerald|зелён|зелен/, "#2F6B4F"],
    [/янтар|amber/, "#C9893A"],
    [/коралл|coral/, "#E07A6A"],
    [/бордов|burgundy|винн/, "#7A2E3C"],
    [/перламутр|pearl/, "#D8D2C8"],
    [/золот|gold/, "#C9A96E"],
    [/серебр|silver/, "#A8B0B8"],
    [/син|blue/, "#3D6E9C"],
    [/красн|red/, "#A83C3C"],
    [/фиолет|violet|purple/, "#6B4C8A"],
    [/розов|pink/, "#C97A9A"],
    [/оранж|orange/, "#D4783A"],
    [/бел|white|cream|слонов/, "#F4EFE6"],
    [/чёрн|черн|black/, "#2A2520"],
  ];
  for (const [re, hex] of map) {
    if (re.test(n)) return hex;
  }
  return "#8B6A3E";
}

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

/** Prioritized soft L3 lines + glance signals from day_personal (capped). */
export function collectDayPersonalLayer(
  personal: NonNullable<NonNullable<TodayContractV1["day_story"]>["day_personal"]>,
): { paragraphs: string[]; signals: TodayDayPersonalSignal[] } {
  const paras: string[] = [];
  const layerUsed: string[] = [];
  const astro = personal.personal_astrology;
  const hd = personal.human_design;
  const bazi = personal.bazi;
  const vedic = personal.vedic_personal;

  const activation = hd?.bodygraph?.activations?.[0];
  const zrPeak =
    clean(astro?.time_lords?.zodiacal_releasing?.peak_soft?.note_ru) ||
    clean(astro?.time_lords?.zodiacal_releasing_spirit?.peak_soft?.note_ru);
  const activeReturn = (astro?.planet_returns?.active ?? []).find((r) => r?.body_ru || r?.body);
  const windowReturn = (astro?.planet_returns?.highlights ?? []).find((h) => h?.in_return_window);
  const returnLine = activeReturn
    ? `Возврат ${activeReturn.body_ru || activeReturn.body}: окно активной встречи с циклом.`
    : windowReturn?.body_ru || windowReturn?.body
      ? `Возврат ${windowReturn.body_ru || windowReturn.body}: мягкое окно возврата.`
      : null;

  const softLines = [
    clean(hd?.type_authority?.summary_ru),
    clean(hd?.profile_lines_cross?.summary_ru),
    clean(hd?.variables?.summary_ru),
    clean(activation?.story_ru) || titledStory(activation?.title, activation?.story_ru),
    clean(astro?.time_lords?.summary_ru),
    zrPeak ? `ZR: ${zrPeak}` : null,
    clean(astro?.house_rulers_chains?.summary_ru),
    clean(astro?.profections?.summary_ru),
    clean(hd?.channels?.summary_ru),
    returnLine,
    clean(astro?.solar_return?.summary_ru),
    clean(astro?.lunar_return?.summary_ru),
    clean(vedic?.dasha?.summary_ru) || clean(vedic?.gochara?.summary_ru) || clean(vedic?.summary_ru),
    clean(bazi?.beats?.[0]?.story_ru) || titledStory(bazi?.beats?.[0]?.title, bazi?.beats?.[0]?.story_ru),
    clean(hd?.transit_gates?.sun?.theme_ru
      ? `HD: Солнце ${hd.transit_gates.sun.label ?? ""} — ${hd.transit_gates.sun.theme_ru}`.trim()
      : null),
    personal.name_numbers?.status === "ok" ? clean(personal.name_numbers.summary_ru) : null,
    clean(personal.summary_ru),
  ];
  for (const line of softLines) {
    pushDistinct(paras, layerUsed, line);
  }

  const signals: TodayDayPersonalSignal[] = [];
  const pushSignal = (label: string, value: string | null | undefined) => {
    const v = clean(value);
    if (!v || signals.length >= 4) return;
    if (signals.some((s) => s.label === label || s.value === v)) return;
    signals.push({ label, value: v });
  };

  if (hd?.type_authority?.type?.name_ru) {
    pushSignal(
      "HD тип",
      [
        hd.type_authority.type.name_ru,
        hd.type_authority.authority?.name_ru
          ? `авт. ${hd.type_authority.authority.name_ru}`
          : null,
      ]
        .filter(Boolean)
        .join(" · "),
    );
  }
  if (hd?.profile_lines_cross?.profile?.id) {
    pushSignal(
      "HD профиль",
      [
        hd.profile_lines_cross.profile.id,
        hd.profile_lines_cross.incarnation_cross?.label
          ? `cross ${hd.profile_lines_cross.incarnation_cross.label}`
          : null,
      ]
        .filter(Boolean)
        .join(" · "),
    );
  }
  if (hd?.variables?.pattern || hd?.variables?.digestion?.color_name_ru) {
    pushSignal(
      "HD variables",
      [
        hd.variables.pattern,
        hd.variables.digestion?.color_name_ru
          ? `пищ. ${hd.variables.digestion.color_name_ru}`
          : null,
      ]
        .filter(Boolean)
        .join(" · "),
    );
  }
  const annual = astro?.profections?.annual;
  if (annual?.house) {
    pushSignal(
      "Профекция",
      [annual.house ? `${annual.house}-й дом` : null, annual.lord_ru, annual.sign_ru]
        .filter(Boolean)
        .join(" · "),
    );
  }
  const firMajor = astro?.time_lords?.firdaria?.major?.planet_ru;
  const firSub = astro?.time_lords?.firdaria?.sub?.planet_ru;
  if (firMajor) {
    pushSignal("Firdaria", firSub ? `${firMajor} / ${firSub}` : firMajor);
  }
  const zrL1 = astro?.time_lords?.zodiacal_releasing?.level1;
  if (zrL1?.sign_ru) {
    pushSignal("ZR Fortune", [zrL1.sign_ru, zrL1.lord_ru].filter(Boolean).join(" · "));
  }
  const channel = hd?.channels?.channels?.[0];
  if (channel?.id || channel?.name_ru) {
    pushSignal(
      "HD канал",
      [channel.id, channel.name_ru, (channel.centers_ru ?? []).slice(0, 2).join(" / ")]
        .filter(Boolean)
        .join(" · "),
    );
  } else {
    const center = hd?.channels?.defined_centers?.[0];
    if (center?.name_ru) pushSignal("HD центр", center.name_ru);
  }
  const maha = vedic?.dasha?.mahadasha;
  if (maha?.lord_ru || maha?.lord) {
    pushSignal("Даша", maha.lord_ru || maha.lord || null);
  }
  const baziBeat = bazi?.beats?.[0];
  if (baziBeat?.title) pushSignal("BaZi", baziBeat.title);
  if (personal.name_numbers?.status === "ok" && personal.name_numbers.expression?.value != null) {
    pushSignal(
      "Имя",
      [
        `Expr ${personal.name_numbers.expression.value}`,
        personal.name_numbers.soul_urge?.value != null
          ? `Soul ${personal.name_numbers.soul_urge.value}`
          : null,
      ]
        .filter(Boolean)
        .join(" · "),
    );
  }

  return {
    paragraphs: paras.slice(0, 2),
    signals: signals.slice(0, 2),
  };
}

/** Situational electional/horary chapter — only when pack was explicitly requested. */
export function collectElectionalChapter(
  personal: NonNullable<NonNullable<TodayContractV1["day_story"]>["day_personal"]>,
): TodayDayNarrativeChapter | null {
  const pack = personal.electional_horary;
  if (!pack || (!pack.summary_ru && !pack.verdict_ru && !(pack.checklist?.length))) {
    return null;
  }

  const mode = pack.mode === "horary" ? "horary" : "electional";
  const kicker = mode === "horary" ? "Хорар (soft)" : "Электив (soft)";
  const momentBits = [
    pack.moment?.date,
    pack.moment?.time,
    pack.ascendant?.sign_ru ? `ASC ${pack.ascendant.sign_ru}` : null,
    pack.moon?.sign_ru
      ? `Луна ${pack.moon.sign_ru}${pack.moon.dignity?.name_ru ? ` · ${pack.moon.dignity.name_ru}` : ""}`
      : null,
  ].filter(Boolean);
  const lead =
    clean(pack.verdict_ru) ||
    clean(pack.summary_ru) ||
    (momentBits.length ? momentBits.join(" · ") : null);

  const paragraphs: string[] = [];
  const used: string[] = [];
  if (lead) used.push(lead);
  const summary = clean(pack.summary_ru);
  if (summary && summary !== lead) {
    pushDistinct(paragraphs, used, summary);
  }
  if (pack.planetary_hour?.matched && pack.planetary_hour.ruler_planet_ru) {
    pushDistinct(
      paragraphs,
      used,
      `Планетарный час — ${pack.planetary_hour.ruler_planet_ru}${
        pack.planetary_hour.period === "night" ? " (ночь)" : pack.planetary_hour.period === "day" ? " (день)" : ""
      }.`,
    );
  }
  if (pack.nearest_lunar_aspect?.within_3h) {
    const title =
      clean(pack.nearest_lunar_aspect.title) ||
      clean(pack.nearest_lunar_aspect.aspect) ||
      "лунный аспект";
    const delta =
      typeof pack.nearest_lunar_aspect.delta_minutes === "number"
        ? ` ≈ ${Math.round(pack.nearest_lunar_aspect.delta_minutes)} мин`
        : "";
    pushDistinct(paragraphs, used, `Рядом timed-аспект: ${title}${delta}.`);
  }
  if (pack.question) {
    pushDistinct(paragraphs, used, `Вопрос: «${pack.question.slice(0, 160)}».`);
  }
  const notes = clean(pack.notes_ru);
  if (notes) pushDistinct(paragraphs, used, notes);

  const statusOrder = (s: string) =>
    ({ fail: 0, caution: 1, pass: 2, info: 3 } as Record<string, number>)[s] ?? 9;
  const checklist: TodayDayElectionalCheck[] = (pack.checklist ?? [])
    .filter((c): c is { id?: string; status?: string; title?: string; story_ru?: string } =>
      Boolean(c && (c.title || c.story_ru)),
    )
    .map((c) => ({
      id: String(c.id || c.title || "check"),
      status: String(c.status || "info"),
      title: String(c.title || "Пункт"),
      story: clean(c.story_ru),
    }))
    .sort((a, b) => statusOrder(a.status) - statusOrder(b.status))
    .slice(0, 6);

  return {
    id: "electional",
    kicker,
    lead,
    paragraphs: paragraphs.slice(0, 3),
    accent: "sky",
    planetHint: "Луна",
    checklist: checklist.length ? checklist : null,
    collapseAfter: paragraphs.length > 2 ? 1 : undefined,
  };
}

function appendElectionalChapter(
  chapters: TodayDayNarrativeChapter[],
  contract: TodayContractV1,
): void {
  const personal = contract.day_story?.day_personal ?? null;
  if (!personal) return;
  const chapter = collectElectionalChapter(personal);
  if (!chapter) return;
  chapters.push(chapter);
}

function buildDayMapChapters(
  dayMap: TodayDayMap,
  contract: TodayContractV1,
  colorGuide: TodayDayColorGuide | null | undefined,
  used: string[],
): TodayDayNarrativeChapter[] {
  const chapters: TodayDayNarrativeChapter[] = [];
  used.push(dayMap.whatHappens);
  chapters.push({
    id: "opening",
    kicker: "Суть дня",
    lead: dayMap.whatHappens,
    paragraphs: [],
    accent: "default",
  });

  const strengthen = dayMap.whatWorks ? [dayMap.whatWorks] : [];
  const soften = [dayMap.whereConflict, dayMap.whereYouBreak].filter(
    (x): x is string => Boolean(x && x.trim()),
  );
  if (strengthen.length || soften.length) {
    chapters.push({
      id: "force",
      kicker: "День в одном взгляде",
      lead: null,
      paragraphs: [],
      accent: "dual",
      dual: { strengthen, soften },
    });
  }

  const supportParas: string[] = [];
  const supportUsed = new Set(used.map((u) => u.toLowerCase()));
  for (const hint of dayMap.avoidHints) {
    const line =
      hint.startsWith("Не ") || hint.startsWith("не ")
        ? hint
        : `Лучше не: ${hint.replace(/[.!?]+$/, "")}.`;
    if (!supportUsed.has(line.toLowerCase())) {
      supportUsed.add(line.toLowerCase());
      supportParas.push(line);
    }
  }
  const colorName = clean(colorGuide?.name) || clean(contract.day_story?.talisman?.color);
  const colorHex = colorHexForDayName(colorName);
  if (colorName) {
    const colorLine = clean(colorGuide?.benefit)
      ? `Цвет дня — ${colorName}. ${clean(colorGuide?.benefit)}`
      : `Цвет дня — ${colorName}`;
    if (!supportUsed.has(colorLine.toLowerCase())) {
      supportUsed.add(colorLine.toLowerCase());
      supportParas.push(colorLine);
    }
  }

  const holiday = contract.day_story?.day_foundation?.seasonal?.holidays?.today?.[0];
  const holidayName = clean(holiday?.name_ru);
  if (holidayName) {
    const holidayLine = `Сегодня — ${holidayName}.`;
    if (!supportUsed.has(holidayLine.toLowerCase())) {
      supportUsed.add(holidayLine.toLowerCase());
      supportParas.unshift(holidayLine);
    }
  }

  const namePack = contract.day_story?.day_personal?.name_numbers;
  if (namePack?.status === "ok" && namePack.expression?.value != null) {
    const nameLine =
      clean(namePack.summary_ru) ||
      `Числа имени: Expression ${namePack.expression.value}.`;
    if (!supportUsed.has(nameLine.toLowerCase())) {
      supportUsed.add(nameLine.toLowerCase());
      supportParas.push(nameLine);
    }
  }

  const move = dayMap.oneConcreteMove;
  if (move || supportParas.length) {
    chapters.push({
      id: "supports",
      kicker: "Твой ход",
      lead: move,
      paragraphs: supportParas,
      accent: "support",
      colorHex,
      colorLabel: colorName || null,
      collapseAfter: supportParas.length > 3 ? 2 : undefined,
    });
  }

  return chapters;
}

function firstPlanetHint(input: {
  morningRitualData: MorningRitualData | null | undefined;
  skyCards: TodaySkyCard[];
}): string | null {
  const celestial = input.morningRitualData?.celestial_events;
  const ingress = celestial?.ingresses?.[0]?.planet_ru;
  if (ingress) return ingress;
  const transit = celestial?.personal_transits?.[0]?.title;
  if (transit) return transit;
  const aspect = celestial?.sky_aspects?.[0]?.title;
  if (aspect) return aspect;
  return null;
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
    pushDistinct(
      paragraphs,
      used,
      clean(ingress.story_ru) ||
        titledStory(
          ingress.planet_ru && ingress.sign_ru
            ? `${ingress.planet_ru} → ${ingress.sign_ru}`
            : ingress.planet_ru,
          ingress.story_ru,
        ),
    );
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

  const skipIds = new Set(["tarot", "number", "color", "stone", "totem"]);
  for (const card of input.skyCards) {
    if (skipIds.has(card.id)) continue;
    pushDistinct(paragraphs, used, titledStory(card.title, card.story));
  }

  return paragraphs.slice(0, 8);
}

function collectForceDual(
  contract: TodayContractV1,
  literary: ReturnType<typeof buildTodayLiteraryReading>,
  used: string[],
): { strengthen: string[]; soften: string[]; paragraphs: string[] } {
  const strengthen: string[] = [];
  const soften: string[] = [];
  const paragraphs: string[] = [];

  if (literary.lean) pushDistinct(strengthen, used, literary.lean);
  if (literary.ease) pushDistinct(soften, used, literary.ease);

  for (const id of ["relationships", "money_work", "family"] as const) {
    const lens = contract.domains[id];
    if (!isDomainLensPresent(lens)) continue;
    const label = DOMAIN_LABELS[id];
    if (clean(lens.opportunity)) {
      pushDistinct(strengthen, used, `${label}: ${clean(lens.opportunity)}`);
    }
    if (clean(lens.risk)) {
      pushDistinct(soften, used, `${label}: ${clean(lens.risk)}`);
    }
    if (clean(lens.action) && !clean(lens.risk)) {
      pushDistinct(soften, used, `${label}: ${clean(lens.action)}`);
    }
  }

  const doItems = dayStoryDoItems(contract).slice(0, 3);
  if (doItems.length) {
    pushDistinct(strengthen, used, `Что усиливает день: ${doItems.join("; ")}`);
  }
  const avoidItems = dayStoryAvoidItems(contract).slice(0, 3);
  if (avoidItems.length) {
    pushDistinct(soften, used, `Что сегодня ослабляет или лучше не дожимать: ${avoidItems.join("; ")}`);
  }

  if (literary.close) pushDistinct(paragraphs, used, literary.close);

  paragraphs.push(...strengthen, ...soften);
  return { strengthen, soften, paragraphs };
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

/**
 * «Твой ход» — expanded supports: color why, stone note, practice reason.
 * Uses only contract + colorGuide fields — never invents sky→color links.
 */
function collectSupportChapter(
  contract: TodayContractV1,
  colorGuide: TodayDayColorGuide | null | undefined,
  used: string[],
): TodayDayNarrativeChapter | null {
  const out: string[] = [];
  const holiday = contract.day_story?.day_foundation?.seasonal?.holidays?.today?.[0];
  const holidayName = clean(holiday?.name_ru);
  if (holidayName) pushDistinct(out, used, `Сегодня — ${holidayName}.`);

  const talisman = contract.day_story?.talisman;
  const supportsStory = clean((contract.day_story as { supports_story?: string } | undefined)?.supports_story);
  if (supportsStory) pushDistinct(out, used, supportsStory);

  const colorName = clean(colorGuide?.name) || clean(talisman?.color);
  if (colorGuide) {
    if (colorName) {
      const whyParts = [clean(colorGuide.benefit), clean(talisman?.note)].filter(Boolean);
      if (whyParts.length) {
        pushDistinct(
          out,
          used,
          `Цвет дня — ${colorName}. ${whyParts.join(" ")}`,
        );
      } else {
        pushDistinct(out, used, `Цвет дня — ${colorName}`);
      }
    }
    if (clean(colorGuide.clothing)) {
      pushDistinct(out, used, `Куда ложится: ${clean(colorGuide.clothing)}`);
    }
    if (clean(colorGuide.amount)) {
      pushDistinct(out, used, clean(colorGuide.amount));
    }
    if (clean(colorGuide.avoidColor) && clean(colorGuide.avoidWhy)) {
      pushDistinct(
        out,
        used,
        `Сегодня лучше не: ${clean(colorGuide.avoidColor)} — ${clean(colorGuide.avoidWhy)}`,
      );
    }
  } else if (talisman?.color) {
    const colorLine = talisman.note
      ? `Цвет дня — ${talisman.color}. ${talisman.note}`
      : `Цвет дня — ${talisman.color}`;
    pushDistinct(out, used, colorLine);
  } else if (talisman?.note) {
    pushDistinct(out, used, talisman.note);
  }

  if (talisman?.stone) {
    // Avoid duplicating note if already used for color.
    const stoneAlreadyInColor = Boolean(talisman.note && colorGuide && out.some((p) => p.includes(talisman.note!)));
    const stoneLine =
      talisman.note && !stoneAlreadyInColor
        ? `Камень-опора — ${talisman.stone}. ${talisman.note}`
        : `Камень-опора — ${talisman.stone}`;
    pushDistinct(out, used, stoneLine);
  }

  const practice = contract.day_story?.practice_recommendation;
  if (practice?.text) {
    const line = practice.reason
      ? `${practice.text} ${practice.reason}`
      : practice.text;
    pushDistinct(out, used, line);
  }

  if (!out.length) return null;

  return {
    id: "supports",
    kicker: "Твой ход",
    lead: out[0] ?? null,
    paragraphs: out.slice(1),
    accent: "support",
    colorHex: colorHexForDayName(colorName),
    colorLabel: colorName || null,
    collapseAfter: out.length > 4 ? 3 : undefined,
  };
}

export function buildTodayDayNarrative(input: {
  contract: TodayContractV1;
  story: TodayDayStoryViewModel;
  morningRitualData?: MorningRitualData | null;
  colorGuide?: TodayDayColorGuide | null;
  guideNarrativePayload?: Record<string, unknown> | null;
}): TodayDayNarrative {
  const { contract, story } = input;
  const literary = buildTodayLiteraryReading(story, contract);
  const used: string[] = [];
  const chapters: TodayDayNarrativeChapter[] = [];

  const foundation =
    (contract.day_story?.day_foundation as TodayDayFoundationV1 | null | undefined) ?? null;
  const essenceTheme = clean(foundation?.essence?.theme);
  const essenceStory = clean(foundation?.essence?.story_ru);
  const astroSummary = clean(foundation?.astro?.summary_ru);
  const lunarSummary = clean(foundation?.lunar?.summary_ru);

  const theme =
    essenceTheme ||
    clean(contract.day_story?.theme) ||
    clean(story.hero.themeShort) ||
    null;

  const dayMap = buildTodayDayMap({
    contract,
    guideNarrativePayload: input.guideNarrativePayload,
  });

  // Day Map path: pulse/glance/move slots — not a stacked fact wall.
  // Electional stays: explicit request, not a fact dump.
  if (dayMap) {
    const chaptersMap = buildDayMapChapters(
      dayMap,
      contract,
      input.colorGuide ?? story.colorGuide,
      used,
    );
    appendElectionalChapter(chaptersMap, contract);
    return {
      theme,
      softWhy: null,
      chapters: chaptersMap,
      foundation,
      dayMap,
    };
  }

  const openingParas: string[] = [];
  if (essenceStory) {
    const parts = essenceStory.split(/(?<=[.!?…])\s+/).filter(Boolean);
    if (parts.length <= 2) {
      pushDistinct(openingParas, used, essenceStory);
    } else {
      pushDistinct(openingParas, used, parts.slice(0, 2).join(" "));
      pushDistinct(openingParas, used, parts.slice(2).join(" "));
    }
  } else if (literary.opening) {
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
    chapters.push({
      id: "opening",
      kicker: "Суть дня",
      lead: openingParas[0] ?? null,
      paragraphs: openingParas.slice(1),
      accent: "default",
    });
  }

  if (astroSummary || (foundation?.astro?.beats?.length ?? 0) > 0) {
    const paras: string[] = [];
    const layerUsed: string[] = [];
    if (astroSummary) pushDistinct(paras, layerUsed, astroSummary);
    for (const beat of (foundation?.astro?.beats ?? []).slice(0, 1)) {
      pushDistinct(paras, layerUsed, clean(beat.story_ru) || clean(beat.title));
    }
    if (paras.length) {
      for (const p of paras.slice(0, 2)) used.push(p);
      chapters.push({
        id: "astro",
        kicker: "Астрологический контекст",
        lead: paras[0] ?? null,
        paragraphs: paras.slice(1, 2),
        accent: "sky",
        planetHint:
          foundation?.astro?.beats?.find((b) =>
            /меркур|солнц|венер|марс|юпитер|сатурн/i.test(b.title || ""),
          )?.title ??
          firstPlanetHint({
            morningRitualData: input.morningRitualData,
            skyCards: story.skyCards ?? [],
          }),
      });
    }
  }

  if (lunarSummary || (foundation?.lunar?.beats?.length ?? 0) > 0) {
    const paras: string[] = [];
    const layerUsed: string[] = [];
    if (lunarSummary) pushDistinct(paras, layerUsed, lunarSummary);
    for (const beat of foundation?.lunar?.beats ?? []) {
      if (beat.kind === "phase" && lunarSummary) continue;
      pushDistinct(paras, layerUsed, clean(beat.story_ru) || clean(beat.title));
      if (paras.length >= 2) break;
    }
    if (paras.length) {
      for (const p of paras.slice(0, 2)) used.push(p);
      chapters.push({
        id: "lunar",
        kicker: "Лунный контекст",
        lead: paras[0] ?? null,
        paragraphs: paras.slice(1, 2),
        accent: "sky",
        planetHint: "Луна",
      });
    }
  }

  const personal = contract.day_story?.day_personal ?? null;
  if (personal) {
    const layer = collectDayPersonalLayer(personal);
    const capped = layer.paragraphs;
    if (capped.length || layer.signals.length) {
      for (const p of capped) used.push(p);
      chapters.push({
        id: "personal",
        kicker: "Личный слой",
        lead: capped[0] ?? null,
        paragraphs: capped.slice(1),
        accent: "sky",
        signals: layer.signals.length ? layer.signals : null,
        collapseAfter: capped.length > 2 ? 1 : undefined,
      });
    }
    appendElectionalChapter(chapters, contract);
  }

  if (!astroSummary && !lunarSummary) {
    const skyParas = collectSkyParagraphs({
      morningRitualData: input.morningRitualData,
      skyCards: story.skyCards ?? [],
    })
      .filter((p) => distinctEnough(p, used))
      .slice(0, 2);
    for (const p of skyParas) used.push(p);
    if (skyParas.length) {
      chapters.push({
        id: "sky",
        kicker: "Небо и переходы",
        lead: skyParas[0] ?? null,
        paragraphs: skyParas.slice(1),
        accent: "sky",
        planetHint: firstPlanetHint({
          morningRitualData: input.morningRitualData,
          skyCards: story.skyCards ?? [],
        }),
      });
    }
  }

  const force = collectForceDual(contract, literary, used);
  if (force.strengthen.length || force.soften.length || force.paragraphs.length) {
    const extra = force.paragraphs.filter(
      (p) => !force.strengthen.includes(p) && !force.soften.includes(p),
    );
    chapters.push({
      id: "force",
      kicker: "Сила и мягкость",
      lead: null,
      paragraphs: extra,
      accent: "dual",
      dual: {
        strengthen: force.strengthen.slice(0, 2),
        soften: force.soften.slice(0, 2),
      },
    });
  }

  const symbolParas = collectSymbolParagraphs(story, contract, used).slice(0, 2);
  if (symbolParas.length) {
    chapters.push({
      id: "symbols",
      kicker: "Слой карты и числа",
      lead: symbolParas[0] ?? null,
      paragraphs: symbolParas.slice(1),
      accent: "default",
    });
  }

  const supports = collectSupportChapter(
    contract,
    input.colorGuide ?? story.colorGuide,
    used,
  );
  if (supports) chapters.push(supports);

  return { theme, softWhy, chapters, foundation, dayMap: null };
}
