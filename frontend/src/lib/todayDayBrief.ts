/**
 * TODAY dashboard model — Global Day only.
 * Sequence: ENERGY → MOON → MAIN DRIVER → STRENGTHS → RISKS.
 * No invent. Honest omit when empty. Natal/card/number stay off this screen.
 * Canon: docs/today/TODAY_PRODUCT_FLOW_V1.md
 */

import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import type { DayVisualMode } from "@/lib/dayAtmosphere";
import { DAY_MODE_LABELS_RU, DAY_VISUAL_MODES } from "@/lib/dayAtmosphere";
import { resolveCelestialMoonPhase } from "@/lib/celestialMoonPhase";
import type { TodayContractV1 } from "@/lib/todayContract";
import type { HandoffWelcomeGlass } from "@/lib/todayHandoffWelcome";
import { buildTodaySkyStripModel, inSign, type TodaySkyStripModel } from "@/lib/todaySkyToday";

export type TodayDayWhyFactor = {
  id: string;
  label: string;
  detail: string | null;
};

export type TodayDayBetterCard = {
  id: string;
  title: string;
  body: string;
  detail: string | null;
};

/** Closed Global action types — not spheres. */
export const GLOBAL_ACTION_TYPE_LABELS_RU: Record<string, string> = {
  physical_action: "Физическое действие",
  sensitive_conversation: "Тонкий разговор",
  deep_work: "Глубокая работа",
  admin_order: "Порядок",
  rest: "Отдых",
  emotional_processing: "Эмоции",
  public_visibility: "На виду",
  hard_negotiation: "Жёсткий торг",
};

export type TodayDaySheetRow = {
  label: string;
  value: string;
};

export type TodayDayMainDriver = {
  id: string;
  title: string;
  body: string | null;
  detail: string | null;
  sheetRows: TodayDaySheetRow[];
};

export type TodayDayActionChip = {
  id: string;
  label: string;
  sheetRows: TodayDaySheetRow[];
};

export type TodayDayMoonCard = {
  title: string;
  meta: string | null;
  sheetBody: string;
  sheetRows: TodayDaySheetRow[];
  context: string | null;
};

export type TodayDayBriefModel = {
  dateLabel: string;
  salutation: string;
  /** Atmosphere headline (not a separate «вайб» product label). */
  atmosphereLine: string | null;
  /** @deprecated alias — same as atmosphereLine */
  vibe: string | null;
  moodPills: string[];
  activityTags: string[];
  accents: string[];
  atmosphereNote: string | null;
  /** @deprecated alias for atmosphereNote */
  why: string | null;
  energy: string | null;
  energyCause: string | null;
  expect: string | null;
  trap: string | null;
  doItems: string[];
  avoidItems: string[];
  vibeClosing: string | null;
  /** Closed day mood id */
  visualMode: DayVisualMode | null;
  modeLabel: string | null;
  /** Lunar / sky caption under date */
  lunarCaption: string | null;
  /**
   * Continuous lunar phase for CelestialMoon (0=new … 0.5=full … 1=new).
   * From day_foundation.lunar.phase.cycle_day (preferred) or id/name.
   */
  moonPhase: number | null;
  /** «Почему так сегодня» chips */
  whyFactors: TodayDayWhyFactor[];
  /** «Сегодня лучше» grid */
  betterCards: TodayDayBetterCard[];
  /** Опора дня */
  supportLine: string | null;
  supportDetail: string | null;
  /** Personal bridge — MY DAY only, never on Global TODAY */
  personalLine: string | null;
  /** Shared sky (Moon + headline). No natal overlay on TODAY. */
  skyStrip: TodaySkyStripModel | null;
  /** Compact moon card (sign · phase · cycle). Omit if empty. */
  moonCard: TodayDayMoonCard | null;
  /** Ranked Global driver #1 */
  mainDriver: TodayDayMainDriver | null;
  strengthChips: TodayDayActionChip[];
  riskChips: TodayDayActionChip[];
};

const KITCHEN_MECHANISM_RE =
  /профекц|секундарн\w*\s+прогресс|прогресс\.?\s*солнц|прогресс\.?\s*лун|solar\s*return|управител|нет\s+времени\/места|активных\s+личных\s+транзит|firdaria|vimshottari|\bzr\s*(?:fortune|spirit)\b|time[_\s-]?lords|\d+(?:[.,]\d+)?°|возраст\s+\d+(?:[.,]\d+)?\s*лет|дата\s+19\d{2}-\d{2}-\d{2}|дата\s+20\d{2}-\d{2}-\d{2}/i;

function clean(s: string | null | undefined): string | null {
  const t = String(s || "").trim();
  return t ? t : null;
}

function normalizeKey(s: string): string {
  return s.toLowerCase().replace(/\s+/g, " ").trim();
}

export function cleanAmbassadorWhy(s: string | null | undefined): string | null {
  const t = clean(s);
  if (!t) return null;
  if (KITCHEN_MECHANISM_RE.test(t)) return null;
  if (t.length > 320 && (t.match(/\./g) || []).length >= 4) return null;
  return t;
}

function uniqTrim(items: Array<string | null | undefined>, max: number): string[] {
  const out: string[] = [];
  const seen = new Set<string>();
  for (const raw of items) {
    const t = clean(raw);
    if (!t) continue;
    const key = normalizeKey(t);
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(t);
    if (out.length >= max) break;
  }
  return out;
}

export function clipCompassProse(s: string | null | undefined, maxChars = 180): string | null {
  const t = clean(s);
  if (!t) return null;
  if (t.length <= maxChars) return t;
  const parts = t.split(/(?<=[.!?…])\s+/).filter(Boolean);
  let out = parts[0] || t.slice(0, maxChars);
  if (parts.length > 1 && (out + " " + parts[1]).length <= maxChars + 40) {
    out = `${out} ${parts[1]}`;
  }
  if (parts.length > 2 && (out + " " + parts[2]).length <= maxChars + 24) {
    out = `${out} ${parts[2]}`;
  }
  if (out.length > maxChars + 48) {
    out = out.slice(0, maxChars).replace(/\s+\S*$/, "").trim();
  }
  return out.endsWith(".") || out.endsWith("!") || out.endsWith("?") || out.endsWith("…")
    ? out
    : `${out}…`;
}

function overlaps(a: string | null, b: string | null): boolean {
  if (!a || !b) return false;
  const aa = normalizeKey(a);
  const bb = normalizeKey(b);
  if (aa === bb) return true;
  if (aa.length >= 24 && bb.includes(aa.slice(0, Math.min(48, aa.length)))) return true;
  if (bb.length >= 24 && aa.includes(bb.slice(0, Math.min(48, bb.length)))) return true;
  return false;
}

function pickAtmosphereNote(parts: Array<string | null | undefined>): string | null {
  for (const part of parts) {
    const ok = cleanAmbassadorWhy(part);
    if (ok) return clipCompassProse(ok, 160);
  }
  return null;
}

function isDayVisualMode(value: unknown): value is DayVisualMode {
  return typeof value === "string" && (DAY_VISUAL_MODES as readonly string[]).includes(value);
}

function resolveVisualMode(contract: TodayContractV1): DayVisualMode | null {
  const fromEngine = contract.global_day?.primary_energy;
  if (isDayVisualMode(fromEngine)) return fromEngine;
  const fromAtm = contract.day_atmosphere?.visual_mode;
  if (isDayVisualMode(fromAtm)) return fromAtm;
  const fromStory = (contract.day_story as { visual_mode?: string } | undefined)?.visual_mode;
  if (isDayVisualMode(fromStory)) return fromStory;
  return null;
}

function sceneAccents(contract: TodayContractV1): string[] {
  const scenes = contract.day_story?.day_scenario?.scenes;
  if (!Array.isArray(scenes) || !scenes.length) return [];
  const pid = String(contract.day_story?.day_scenario?.primary_scene_id || "").trim();
  const byId = pid ? scenes.filter((s) => String(s.scene_id || "") === pid) : [];
  const primary =
    byId.length > 0
      ? byId
      : scenes.filter((s) => String(s.role_in_story || "").toLowerCase() === "primary");
  return uniqTrim(
    primary.map((s) => s.sphere_label_ru || s.sphere || null),
    3,
  );
}

function buildLunarCaption(
  contract: TodayContractV1,
  glassReason: string | null,
  skyStrip: TodaySkyStripModel | null,
): string | null {
  if (skyStrip?.moonLabel) return skyStrip.moonLabel;
  const lunar = contract.day_story?.day_foundation?.lunar;
  const phase = clean(lunar?.phase?.name);
  const sign =
    clean(lunar?.moon_sign?.sign_ru) ||
    clean(lunar?.moon_sign?.sign);
  if (phase && sign) return `${phase} в ${sign}`;
  if (phase) return phase;
  if (sign) return `Луна в ${sign}`;
  return glassReason ? clipCompassProse(glassReason, 72) : null;
}

export type TodayDayBriefLunarHint = {
  id?: string | null;
  name?: string | null;
  cycle_day?: number | null;
};

function formatCycleDay(cycle: number): string {
  const day = Math.max(1, Math.round(cycle));
  return `${day}-й день цикла`;
}

function pushSheetRow(rows: TodayDaySheetRow[], label: string, value: string | null | undefined) {
  const v = clean(value);
  if (!v) return;
  if (rows.some((row) => row.label === label && row.value === v)) return;
  rows.push({ label, value: v });
}

function buildMoonCard(
  contract: TodayContractV1,
  lunarHint: TodayDayBriefLunarHint | null | undefined,
  skyStrip: TodaySkyStripModel | null,
  lunarCaption: string | null,
  context: string | null,
): TodayDayMoonCard | null {
  const lunar = contract.day_story?.day_foundation?.lunar;
  const sign = clean(lunar?.moon_sign?.sign_ru) || clean(skyStrip?.moon?.sign_ru);
  const title =
    skyStrip?.moonLabel ||
    inSign("Луна", sign) ||
    lunarCaption;
  const phase =
    clean(lunar?.phase?.name) ||
    clean(lunarHint?.name);
  const cycleRaw =
    typeof lunar?.phase?.cycle_day === "number" && Number.isFinite(lunar.phase.cycle_day)
      ? lunar.phase.cycle_day
      : typeof lunarHint?.cycle_day === "number" && Number.isFinite(lunarHint.cycle_day)
        ? lunarHint.cycle_day
        : null;
  const cycle = cycleRaw != null ? formatCycleDay(cycleRaw) : null;
  const metaParts = [phase, cycle].filter((part): part is string => Boolean(part));
  const meta = metaParts.length ? metaParts.join(" · ") : null;
  if (!title && !meta) return null;
  const sheetRows: TodayDaySheetRow[] = [];
  pushSheetRow(sheetRows, copy.sheetSign, sign);
  pushSheetRow(sheetRows, copy.sheetPhase, phase);
  pushSheetRow(sheetRows, copy.sheetCycle, cycle);
  const moonContext =
    cleanAmbassadorWhy(context) ||
    cleanAmbassadorWhy(lunar?.phase?.themes) ||
    cleanAmbassadorWhy(lunar?.phase?.guidance) ||
    cleanAmbassadorWhy(lunar?.summary_ru);
  const sheetBody = [title, meta, moonContext].filter((part, i, all) => part && all.indexOf(part) === i).join("\n\n");
  return {
    title: title || "Луна",
    meta,
    sheetBody: sheetBody || title || "Луна",
    sheetRows,
    context: moonContext,
  };
}

function buildMoonPhase(
  contract: TodayContractV1,
  lunarHint?: TodayDayBriefLunarHint | null,
  glassReason?: string | null,
): number | null {
  const phase = contract.day_story?.day_foundation?.lunar?.phase;
  const cycleFromFoundation =
    typeof phase?.cycle_day === "number" && Number.isFinite(phase.cycle_day) ? phase.cycle_day : null;
  const cycleFromHint =
    typeof lunarHint?.cycle_day === "number" && Number.isFinite(lunarHint.cycle_day)
      ? lunarHint.cycle_day
      : null;
  return resolveCelestialMoonPhase({
    cycleDay: cycleFromFoundation ?? cycleFromHint,
    phaseId: phase?.id ?? lunarHint?.id ?? null,
    phaseName: phase?.name ?? lunarHint?.name ?? glassReason ?? null,
  });
}

function buildWhyFactors(
  contract: TodayContractV1,
  glass: HandoffWelcomeGlass | null | undefined,
): TodayDayWhyFactor[] {
  const out: TodayDayWhyFactor[] = [];
  const seen = new Set<string>();

  const push = (id: string, label: string | null, detail: string | null) => {
    const lab = clean(label);
    if (!lab) return;
    const key = normalizeKey(lab);
    if (seen.has(key)) return;
    seen.add(key);
    out.push({ id, label: lab, detail: cleanAmbassadorWhy(detail) });
  };

  const lunar = contract.day_story?.day_foundation?.lunar;
  const skyMoon = contract.sky_today?.moon;
  const phase = clean(lunar?.phase?.name);
  const sign =
    clean(skyMoon?.sign_ru) ||
    clean(lunar?.moon_sign?.sign_ru) ||
    clean(lunar?.moon_sign?.sign);
  if (skyMoon && sign) {
    push(
      "lunar",
      inSign(skyMoon.body_ru || "Луна", sign) || `Луна в ${sign}`,
      clean(lunar?.phase?.themes) || clean(lunar?.phase?.guidance) || clean(lunar?.summary_ru),
    );
  } else if (phase || sign) {
    push(
      "lunar",
      phase && sign ? `${phase} · ${sign}` : phase || `Луна в ${sign}`,
      clean(lunar?.phase?.themes) || clean(lunar?.phase?.guidance) || clean(lunar?.summary_ru),
    );
  } else if (glass?.reasonLine) {
    push("lunar-glass", clipCompassProse(glass.reasonLine, 48), glass.reasonLine);
  }

  const num = contract.day_story?.day_foundation?.numerology;
  const dayNum = num?.personal_day ?? num?.universal_day;
  if (typeof dayNum === "number" && Number.isFinite(dayNum)) {
    push("number", `Число дня ${dayNum}`, clean(num?.summary_ru));
  }

  const beats = [
    ...(contract.day_story?.day_foundation?.astro?.beats || []),
    ...(contract.day_story?.day_foundation?.lunar?.beats || []),
  ];
  for (const beat of beats) {
    if (out.length >= 4) break;
    const title = clean(beat.title);
    if (!title || KITCHEN_MECHANISM_RE.test(title)) continue;
    push(`beat-${beat.id || title}`, clipCompassProse(title, 42), clean(beat.story_ru));
  }

  return out.slice(0, 4);
}

const BETTER_BUCKETS: Array<{
  id: string;
  title: string;
  spheres: string[];
  domainKeys: string[];
}> = [
  { id: "work", title: "Работа", spheres: ["work", "work_decisions", "money"], domainKeys: ["work", "money"] },
  {
    id: "people",
    title: "Люди",
    spheres: ["relationships", "communication", "home"],
    domainKeys: ["relationships"],
  },
  {
    id: "self",
    title: "Для себя",
    spheres: ["energy", "energy_body", "rest_travel", "creativity", "rest"],
    domainKeys: ["energy"],
  },
];

function buildBetterCards(contract: TodayContractV1): TodayDayBetterCard[] {
  const scenes = contract.day_story?.day_scenario?.scenes;
  const domains = contract.domains;
  const cards: TodayDayBetterCard[] = [];

  for (const bucket of BETTER_BUCKETS) {
    let body: string | null = null;
    let detail: string | null = null;

    if (Array.isArray(scenes)) {
      const match = scenes.find((s) => {
        const sp = String(s.sphere || "").toLowerCase();
        return bucket.spheres.some((b) => sp === b || sp.includes(b));
      });
      if (match) {
        body =
          clipCompassProse(match.opportunity || match.recommended_action || match.what_happens, 72) ||
          null;
        detail =
          cleanAmbassadorWhy(match.opportunity) ||
          cleanAmbassadorWhy(match.recommended_action) ||
          cleanAmbassadorWhy(match.what_happens) ||
          cleanAmbassadorWhy(match.domestic_example);
      }
    }

    if (!body && domains) {
      for (const key of bucket.domainKeys) {
        const lens = (domains as Record<string, { opportunity?: string; action?: string; status?: string }>)[key];
        if (!lens) continue;
        body = clipCompassProse(lens.opportunity || lens.action || lens.status, 72);
        detail =
          cleanAmbassadorWhy(lens.opportunity) ||
          cleanAmbassadorWhy(lens.action) ||
          cleanAmbassadorWhy(lens.status);
        if (body) break;
      }
    }

    if (body) {
      cards.push({ id: bucket.id, title: bucket.title, body, detail });
    }
  }

  return cards.slice(0, 3);
}

function actionChip(id: string | null | undefined): TodayDayActionChip | null {
  const key = String(id || "")
    .trim()
    .toLowerCase()
    .replace(/-/g, "_");
  if (!key) return null;
  const label = GLOBAL_ACTION_TYPE_LABELS_RU[key];
  if (!label) return null;
  return { id: key, label, sheetRows: [] };
}

function relatedFactsForAction(
  contract: TodayContractV1,
  actionId: string,
  side: "supports" | "cautions",
): string[] {
  const windows = contract.global_day?.windows;
  const drivers = contract.global_day?.drivers;
  if (!Array.isArray(windows) || !windows.length) return [];
  const driverIds = new Set<string>();
  for (const win of windows) {
    const bucket = side === "supports" ? win.supports : win.cautions;
    if (!Array.isArray(bucket)) continue;
    if (!bucket.map((x) => String(x || "").toLowerCase().replace(/-/g, "_")).includes(actionId)) continue;
    const did = String(win.driver_id || "").trim();
    if (did) driverIds.add(did);
  }
  const facts: string[] = [];
  const seen = new Set<string>();
  const pushFact = (raw: string | null | undefined) => {
    const t = clean(raw);
    if (!t) return;
    const key = normalizeKey(t);
    if (seen.has(key)) return;
    seen.add(key);
    facts.push(t);
  };
  if (Array.isArray(drivers)) {
    for (const row of drivers) {
      const id = String(row.id || "").trim();
      if (id && driverIds.has(id)) pushFact(row.fact_ru);
    }
  }
  return facts.slice(0, 3);
}

function buildActionChips(
  raw: unknown,
  max: number,
  contract: TodayContractV1,
  side: "supports" | "cautions",
): TodayDayActionChip[] {
  if (!Array.isArray(raw)) return [];
  const out: TodayDayActionChip[] = [];
  const seen = new Set<string>();
  for (const item of raw) {
    const chip = actionChip(typeof item === "string" ? item : null);
    if (!chip || seen.has(chip.id)) continue;
    seen.add(chip.id);
    const related = relatedFactsForAction(contract, chip.id, side);
    if (related.length) {
      chip.sheetRows = [{ label: copy.sheetDrivers, value: related.join(" · ") }];
    }
    out.push(chip);
    if (out.length >= max) break;
  }
  return out;
}

function buildMainDriver(contract: TodayContractV1, energyLabel: string | null): TodayDayMainDriver | null {
  const row = contract.global_day?.drivers?.[0];
  if (!row) return null;
  const id = String(row.id || row.kind || "").trim();
  const title = clean(row.fact_ru) || clean(row.kind) || (id ? id : null);
  if (!title) return null;
  const kindLabel = actionChip(row.kind)?.label || clean(row.kind);
  const windowTime = (contract.global_day?.windows || []).find(
    (win) => String(win.driver_id || "").trim() === id && clean(win.time),
  )?.time;
  const sheetRows: TodayDaySheetRow[] = [];
  pushSheetRow(sheetRows, copy.sheetEvent, clean(row.fact_ru));
  pushSheetRow(sheetRows, copy.sheetTime, windowTime);
  pushSheetRow(sheetRows, copy.sheetWhyRanked, copy.whyRankedDriver);
  pushSheetRow(sheetRows, copy.sheetEnergyLink, energyLabel);
  return {
    id: id || title,
    title,
    body: kindLabel && kindLabel !== title ? kindLabel : null,
    detail: [clean(row.fact_ru), kindLabel].filter(Boolean).join("\n\n") || title,
    sheetRows,
  };
}

export function buildTodayDayBriefModel(input: {
  contract: TodayContractV1;
  dateLabel: string;
  salutation: string;
  headline?: string | null;
  welcomeGlass?: HandoffWelcomeGlass | null;
  energyLine?: string | null;
  energyCause?: string | null;
  loading?: boolean;
  /** Morning celestial lunar — fill-empty when day_foundation.phase is thin. */
  lunarHint?: TodayDayBriefLunarHint | null;
}): TodayDayBriefModel {
  const story = input.contract.day_story;
  const glass = input.welcomeGlass;
  const visualMode = resolveVisualMode(input.contract);

  const atmosphereLine =
    clean(input.headline) ||
    clean(story?.headline_anchor) ||
    clean(story?.theme) ||
    clean(story?.day_thesis?.label_ru) ||
    clean(story?.day_thesis?.label) ||
    clean(input.contract.global_context?.period) ||
    null;

  const essence =
    clean(story?.day_foundation?.essence?.theme) ||
    clean(story?.day_foundation?.essence?.story_ru) ||
    null;

  const expect = clipCompassProse(story?.expect, 320);

  let atmosphereNote = pickAtmosphereNote([
    glass?.reasonLine,
    essence,
    story?.day_scenario?.conflict?.why_arose,
  ]);
  if (overlaps(atmosphereNote, expect) || overlaps(atmosphereNote, atmosphereLine)) {
    atmosphereNote = null;
  }

  const doItems = uniqTrim(story?.do || [], 3).map((item) => clipCompassProse(item, 200) || item);
  const avoidItems = uniqTrim(story?.avoid || [], 2).map((item) => clipCompassProse(item, 180) || item);
  const supportLine = doItems[0] || clipCompassProse(story?.advantage, 120);
  const supportDetail =
    cleanAmbassadorWhy(story?.do?.[0]) ||
    cleanAmbassadorWhy(story?.advantage) ||
    (doItems.length > 1 ? doItems.slice(1).join(" · ") : null);

  const personalLine =
    clipCompassProse(
      cleanAmbassadorWhy(story?.day_scenario?.conflict?.why_personal) ||
        cleanAmbassadorWhy(input.contract.personal_growth?.development_point),
      180,
    ) || null;

  const skyStrip = input.loading ? null : buildTodaySkyStripModel(input.contract, null);
  const lunarCaption = input.loading
    ? null
    : buildLunarCaption(input.contract, glass?.reasonLine ?? null, skyStrip);

  return {
    dateLabel: input.dateLabel,
    salutation: input.salutation,
    atmosphereLine: input.loading ? null : atmosphereLine,
    vibe: input.loading ? null : atmosphereLine,
    moodPills: uniqTrim(glass?.moodPills || [], 2),
    activityTags: uniqTrim(glass?.activityTags || [], 3),
    accents: sceneAccents(input.contract),
    atmosphereNote,
    why: atmosphereNote,
    energy: clipCompassProse(input.energyLine, 180),
    energyCause: clipCompassProse(cleanAmbassadorWhy(input.energyCause), 160),
    expect,
    trap: clipCompassProse(story?.trap, 260),
    doItems,
    avoidItems,
    vibeClosing: null,
    visualMode,
    modeLabel: visualMode ? DAY_MODE_LABELS_RU[visualMode] : null,
    lunarCaption,
    moonPhase: input.loading
      ? null
      : buildMoonPhase(input.contract, input.lunarHint, glass?.reasonLine ?? null),
    moonCard: input.loading
      ? null
      : buildMoonCard(
          input.contract,
          input.lunarHint,
          skyStrip,
          lunarCaption,
          clipCompassProse(atmosphereLine, 160) ||
            (visualMode ? DAY_MODE_LABELS_RU[visualMode] : null),
        ),
    whyFactors: buildWhyFactors(input.contract, glass),
    betterCards: buildBetterCards(input.contract),
    supportLine,
    supportDetail,
    personalLine,
    skyStrip,
    mainDriver: input.loading
      ? null
      : buildMainDriver(input.contract, visualMode ? DAY_MODE_LABELS_RU[visualMode] : null),
    strengthChips: input.loading
      ? []
      : buildActionChips(input.contract.global_day?.strength, 6, input.contract, "supports"),
    riskChips: input.loading
      ? []
      : buildActionChips(input.contract.global_day?.risk, 6, input.contract, "cautions"),
  };
}
