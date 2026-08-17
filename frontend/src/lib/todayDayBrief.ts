/**
 * TODAY dashboard model — Global Day only.
 * Sequence: ENERGY% + mood → Global day clock → timed transits → STRENGTHS → RISKS.
 * Global clock = Engine windows[] (not Personal Timeline).
 * No invent. Honest omit when empty. Natal/card/number stay off this screen.
 * Canon: docs/today/TODAY_PRODUCT_FLOW_V1.md
 */

import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import type { DayVisualMode } from "@/lib/dayAtmosphere";
import { DAY_MODE_LABELS_RU, DAY_VISUAL_MODES } from "@/lib/dayAtmosphere";
import { resolveCelestialMoonPhase } from "@/lib/celestialMoonPhase";
import type { TodayContractGlobalDayWindowV1, TodayContractV1 } from "@/lib/todayContract";
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
  /** Closed planet slugs for DsPlanet — omit when unknown. */
  planets: string[];
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
  /** Timed sky transits (drivers + moon) — tap opens sheet. */
  transits: TodayDayTransitRow[];
  /** Global day clock from Engine windows. Not the personal MY DAY timeline. */
  dayWindow: TodayDayWindowMark | null;
  /** 0–100 from energy_scores[primary_energy]. Omit when missing. */
  energyPct: number | null;
  strengthChips: TodayDayActionChip[];
  riskChips: TodayDayActionChip[];
};

export type TodayDayTransitRow = {
  id: string;
  title: string;
  time: string | null;
  planets: string[];
  sheetRows: TodayDaySheetRow[];
};

export type TodayDayWindowMark = {
  start: string;
  end: string;
  mark: number;
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
  const signChange = (contract.global_day?.drivers || []).find((row) => {
    const kind = String(row.kind || "")
      .trim()
      .toLowerCase()
      .replace(/-/g, "_");
    return kind === "moon_ingress";
  });
  pushSheetRow(sheetRows, copy.sheetSignChange, clean(signChange?.fact_ru));
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

/** Closed Global driver kinds — never print snake_case to the user. */
export const GLOBAL_DRIVER_KIND_LABELS_RU: Record<string, string> = {
  moon_ingress: "Смена знака",
  planet_ingress: "Вход планеты",
  phase_change: "Смена фазы",
  station_direct: "Станция",
  station: "Станция",
  retrograde_edge: "Ретроград",
  lunar_aspect: "Лунный аспект",
  sky_aspect: "Аспект",
  cycle_aspect: "Цикл",
  perigee: "Перигей",
  apogee: "Апогей",
};

const LUNAR_DRIVER_KINDS = new Set([
  "phase_change",
  "moon_ingress",
  "lunar_aspect",
  "perigee",
  "apogee",
]);

const PLANET_HINTS: Array<[RegExp, string]> = [
  [/лун[аеуы]|новолун|полнолун|\bmoon\b/i, "moon"],
  [/солнц|\bsun\b/i, "sun"],
  [/меркур|\bmercury\b/i, "mercury"],
  [/венер|\bvenus\b/i, "venus"],
  [/марс|\bmars\b/i, "mars"],
  [/юпитер|\bjupiter\b/i, "jupiter"],
  [/сатурн|\bsaturn\b/i, "saturn"],
  [/уран|\buranus\b/i, "uranus"],
  [/нептун|\bneptune\b/i, "neptune"],
  [/плутон|\bpluto\b/i, "pluto"],
];

export function driverKindLabel(kind: string | null | undefined): string | null {
  const key = String(kind || "")
    .trim()
    .toLowerCase()
    .replace(/-/g, "_");
  if (!key) return null;
  return GLOBAL_DRIVER_KIND_LABELS_RU[key] || null;
}

export function driverPlanets(kind: string | null | undefined, fact: string | null | undefined, id: string): string[] {
  const key = String(kind || "")
    .trim()
    .toLowerCase()
    .replace(/-/g, "_");
  const blob = `${kind || ""} ${fact || ""} ${id}`;
  const out: string[] = [];
  const seen = new Set<string>();
  const push = (slug: string) => {
    if (seen.has(slug)) return;
    seen.add(slug);
    out.push(slug);
  };
  if (LUNAR_DRIVER_KINDS.has(key)) push("moon");
  for (let i = 0; i < PLANET_HINTS.length; i += 1) {
    const pair = PLANET_HINTS[i];
    if (!pair[0].test(blob)) continue;
    push(pair[1]);
    if (out.length >= 2) break;
  }
  return out;
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
): { facts: string[]; times: string[] } {
  const windows = contract.global_day?.windows;
  const drivers = contract.global_day?.drivers;
  if (!Array.isArray(windows) || !windows.length) return { facts: [], times: [] };
  const driverIds = new Set<string>();
  const times: string[] = [];
  const seenTimes = new Set<string>();
  for (const win of windows) {
    const bucket = side === "supports" ? win.supports : win.cautions;
    if (!Array.isArray(bucket)) continue;
    if (!bucket.map((x) => String(x || "").toLowerCase().replace(/-/g, "_")).includes(actionId)) continue;
    const did = String(win.driver_id || "").trim();
    if (did) driverIds.add(did);
    const time = clean(win.time);
    if (time && !seenTimes.has(time)) {
      seenTimes.add(time);
      times.push(time);
    }
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
  return { facts: facts.slice(0, 3), times: times.slice(0, 3) };
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
    const rows: TodayDaySheetRow[] = [];
    if (related.facts.length) {
      rows.push({ label: copy.sheetDrivers, value: related.facts.join(" · ") });
    }
    if (related.times.length) {
      rows.push({ label: copy.sheetTime, value: related.times.join(" · ") });
    }
    chip.sheetRows = rows;
    out.push(chip);
    if (out.length >= max) break;
  }
  return out;
}

function actionLabelsFromList(raw: unknown): string | null {
  if (!Array.isArray(raw)) return null;
  const labels: string[] = [];
  const seen = new Set<string>();
  for (const item of raw) {
    const chip = actionChip(typeof item === "string" ? item : null);
    if (!chip || seen.has(chip.id)) continue;
    seen.add(chip.id);
    labels.push(chip.label);
  }
  return labels.length ? labels.join(" · ") : null;
}

function hhmmToMinutes(hhmm: string): number | null {
  const m = String(hhmm || "").trim().match(/^(\d{1,2}):(\d{2})$/);
  if (!m) return null;
  return Number(m[1]) * 60 + Number(m[2]);
}

/** Position of a clock on the kit 06:00–24:00 spectrum. */
function clockToMark(hhmm: string): number {
  const minutes = hhmmToMinutes(hhmm);
  if (minutes == null) return 0.5;
  const start = 6 * 60;
  const span = 18 * 60;
  return Math.min(1, Math.max(0, (minutes - start) / span));
}

export function buildEnergyPct(contract: TodayContractV1): number | null {
  const visualMode = resolveVisualMode(contract);
  const primary =
    visualMode ||
    String(contract.global_day?.primary_energy || "")
      .trim()
      .toLowerCase()
      .replace(/-/g, "_");
  const scores = contract.global_day?.energy_scores;
  if (!primary || !scores || typeof scores !== "object") return null;
  const raw = (scores as Record<string, unknown>)[primary];
  if (typeof raw !== "number" || !Number.isFinite(raw)) return null;
  return Math.round(Math.max(0, Math.min(1, raw)) * 100);
}

export function buildDayWindow(
  windows: TodayContractGlobalDayWindowV1[] | null | undefined,
): TodayDayWindowMark | null {
  if (!Array.isArray(windows) || windows.length < 2) return null;
  const timed: Array<{ time: string; intensity: number }> = [];
  for (const win of windows) {
    const time = clean(win.time);
    if (!time || hhmmToMinutes(time) == null) continue;
    timed.push({
      time,
      intensity: typeof win.intensity === "number" && Number.isFinite(win.intensity) ? win.intensity : -1,
    });
  }
  if (timed.length < 2) return null;
  timed.sort((a, b) => (hhmmToMinutes(a.time) || 0) - (hhmmToMinutes(b.time) || 0));
  let bestIdx = 0;
  let bestIntensity = -1;
  for (let i = 0; i < timed.length; i += 1) {
    if (timed[i].intensity > bestIntensity) {
      bestIntensity = timed[i].intensity;
      bestIdx = i;
    }
  }
  const peak = timed[bestIdx];
  const next = timed[bestIdx + 1];
  if (next) {
    return { start: peak.time, end: next.time, mark: clockToMark(peak.time) };
  }
  const prev = timed[bestIdx - 1];
  if (!prev) return null;
  return { start: prev.time, end: peak.time, mark: clockToMark(prev.time) };
}

function lunarWindowTime(contract: TodayContractV1): string | null {
  const drivers = contract.global_day?.drivers;
  const windows = contract.global_day?.windows;
  if (!Array.isArray(drivers) || !Array.isArray(windows)) return null;
  for (const row of drivers) {
    const key = String(row.kind || "")
      .trim()
      .toLowerCase()
      .replace(/-/g, "_");
    if (!LUNAR_DRIVER_KINDS.has(key)) continue;
    const id = String(row.id || "").trim();
    if (!id) continue;
    const hit = windows.find((win) => String(win.driver_id || "").trim() === id && clean(win.time));
    const time = hit ? clean(hit.time) : null;
    if (time) return time;
  }
  return null;
}

function buildDriverTransit(
  contract: TodayContractV1,
  row: { id?: string; kind?: string; fact_ru?: string },
  index: number,
  energyLabel: string | null,
): TodayDayTransitRow | null {
  const id = String(row.id || row.kind || "").trim();
  const title = clean(row.fact_ru) || driverKindLabel(row.kind);
  if (!title) return null;
  const planets = driverPlanets(row.kind, row.fact_ru, id);
  const matchedWindow = (contract.global_day?.windows || []).find(
    (win) => String(win.driver_id || "").trim() === id && clean(win.time),
  );
  const windowTime = matchedWindow ? clean(matchedWindow.time) : null;
  const sheetRows: TodayDaySheetRow[] = [];
  pushSheetRow(sheetRows, copy.sheetEvent, clean(row.fact_ru));
  pushSheetRow(sheetRows, copy.sheetTime, windowTime);
  pushSheetRow(
    sheetRows,
    copy.sheetWhyRanked,
    index === 0 ? copy.whyRankedDriver : copy.whyRankedAlso,
  );
  pushSheetRow(sheetRows, copy.sheetEnergyLink, energyLabel);
  pushSheetRow(sheetRows, copy.windowSupportLabel, actionLabelsFromList(matchedWindow?.supports));
  pushSheetRow(sheetRows, copy.windowCautionLabel, actionLabelsFromList(matchedWindow?.cautions));
  return { id: id || title, title, time: windowTime, planets, sheetRows };
}

function buildTransitRows(
  contract: TodayContractV1,
  moonCard: TodayDayMoonCard | null,
  energyLabel: string | null,
): TodayDayTransitRow[] {
  const out: TodayDayTransitRow[] = [];
  const seen = new Set<string>();
  if (moonCard) {
    const time = lunarWindowTime(contract);
    const sheetRows = moonCard.sheetRows.slice();
    if (time && !sheetRows.some((row) => row.label === copy.sheetTime)) {
      pushSheetRow(sheetRows, copy.sheetTime, time);
    }
    out.push({
      id: "moon",
      title: moonCard.title,
      time,
      planets: ["moon"],
      sheetRows,
    });
    seen.add(normalizeKey(moonCard.title));
  }
  const drivers = contract.global_day?.drivers;
  if (!Array.isArray(drivers)) return out;
  for (let i = 0; i < drivers.length; i += 1) {
    if (out.length >= 5) break;
    const transit = buildDriverTransit(contract, drivers[i], i, energyLabel);
    if (!transit) continue;
    const key = normalizeKey(transit.title);
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(transit);
  }
  out.sort((a, b) => {
    const am = (a.time ? hhmmToMinutes(a.time) : null) ?? Number.POSITIVE_INFINITY;
    const bm = (b.time ? hhmmToMinutes(b.time) : null) ?? Number.POSITIVE_INFINITY;
    if (am === bm) return 0;
    return am - bm;
  });
  return out;
}

function buildMainDriver(contract: TodayContractV1, energyLabel: string | null): TodayDayMainDriver | null {
  const row = contract.global_day?.drivers?.[0];
  if (!row) return null;
  const transit = buildDriverTransit(contract, row, 0, energyLabel);
  if (!transit) return null;
  const kindLabel = driverKindLabel(row.kind);
  return {
    id: transit.id,
    title: transit.title,
    body: kindLabel && kindLabel !== transit.title ? kindLabel : null,
    detail: [clean(row.fact_ru), kindLabel].filter(Boolean).join("\n\n") || transit.title,
    planets: transit.planets,
    sheetRows: transit.sheetRows,
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
  const energyLabel = visualMode ? DAY_MODE_LABELS_RU[visualMode] : null;
  const moonCard = input.loading
    ? null
    : buildMoonCard(
        input.contract,
        input.lunarHint,
        skyStrip,
        lunarCaption,
        clipCompassProse(atmosphereLine, 160) || energyLabel,
      );

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
    moonCard,
    whyFactors: buildWhyFactors(input.contract, glass),
    betterCards: buildBetterCards(input.contract),
    supportLine,
    supportDetail,
    personalLine,
    skyStrip,
    mainDriver: input.loading ? null : buildMainDriver(input.contract, energyLabel),
    transits: input.loading ? [] : buildTransitRows(input.contract, moonCard, energyLabel),
    dayWindow: input.loading ? null : buildDayWindow(input.contract.global_day?.windows),
    energyPct: input.loading ? null : buildEnergyPct(input.contract),
    strengthChips: input.loading
      ? []
      : buildActionChips(input.contract.global_day?.strength, 6, input.contract, "supports"),
    riskChips: input.loading
      ? []
      : buildActionChips(input.contract.global_day?.risk, 6, input.contract, "cautions"),
  };
}
