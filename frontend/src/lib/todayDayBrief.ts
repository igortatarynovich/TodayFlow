/**
 * Block 1 day ambassador model — assemble from existing contract fields only.
 * No invent. Honest omit when empty.
 *
 * Presentation (v3.4.2 dashboard):
 *   date · lunar caption · mode hero · why factors · better cards ·
 *   support ‖ trap · personal · (detail sheet on tap)
 * Canon: TODAY_SCREEN_SCENARIO_V3 · EXPLAIN_MEANING_NOT_MECHANISM
 */

import type { DayVisualMode } from "@/lib/dayAtmosphere";
import { DAY_MODE_LABELS_RU, DAY_VISUAL_MODES } from "@/lib/dayAtmosphere";
import type { TodayContractV1 } from "@/lib/todayContract";
import type { HandoffWelcomeGlass } from "@/lib/todayHandoffWelcome";

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
  /** «Почему так сегодня» chips */
  whyFactors: TodayDayWhyFactor[];
  /** «Сегодня лучше» grid */
  betterCards: TodayDayBetterCard[];
  /** Опора дня */
  supportLine: string | null;
  supportDetail: string | null;
  /** Personal bridge */
  personalLine: string | null;
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
  const fromAtm = contract.day_atmosphere?.visual_mode;
  if (isDayVisualMode(fromAtm)) return fromAtm;
  const fromStory = (contract.day_story as { visual_mode?: string } | undefined)?.visual_mode;
  if (isDayVisualMode(fromStory)) return fromStory;
  return null;
}

function sceneAccents(contract: TodayContractV1): string[] {
  const scenes = contract.day_story?.day_scenario?.scenes;
  if (!Array.isArray(scenes) || !scenes.length) return [];
  const primary = scenes.filter((s) => String(s.role_in_story || "").toLowerCase() === "primary");
  const pool = primary.length ? primary : scenes;
  return uniqTrim(
    pool.map((s) => s.sphere_label_ru || s.sphere || null),
    3,
  );
}

function buildLunarCaption(contract: TodayContractV1, glassReason: string | null): string | null {
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
  const phase = clean(lunar?.phase?.name);
  const sign = clean(lunar?.moon_sign?.sign_ru) || clean(lunar?.moon_sign?.sign);
  if (phase || sign) {
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

export function buildTodayDayBriefModel(input: {
  contract: TodayContractV1;
  dateLabel: string;
  salutation: string;
  headline?: string | null;
  welcomeGlass?: HandoffWelcomeGlass | null;
  energyLine?: string | null;
  energyCause?: string | null;
  loading?: boolean;
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
    lunarCaption: buildLunarCaption(input.contract, glass?.reasonLine ?? null),
    whyFactors: buildWhyFactors(input.contract, glass),
    betterCards: buildBetterCards(input.contract),
    supportLine,
    supportDetail,
    personalLine,
  };
}
