/**
 * Shared-sky influence model — day weather. Personal overlay is attached by Day Brief.
 * Facts only. No invent. Not an ephemeris.
 * Clocks only from exact_time_local (orb ≠ time).
 */

import type {
  TodayContractSkyBodyV1,
  TodayContractSkyHeadlineV1,
  TodayContractV1,
} from "@/lib/todayContract";
import { formatGlanceClock } from "@/lib/todayGlanceTimeline";

export type TodaySkyStripModel = {
  moon: TodayContractSkyBodyV1 | null;
  moonLabel: string | null;
  moonDegree: string | null;
  moonWhen: string | null;
  headline: TodayContractSkyHeadlineV1 | null;
  headlineLabel: string | null;
  headlineOrb: string | null;
  headlineWhen: string | null;
  windowLabel: string | null;
  sharedStory: string | null;
  personalLine: string | null;
};

function clean(s: string | null | undefined): string | null {
  const t = String(s || "").trim();
  return t ? t : null;
}

function clock(iso: string | null | undefined): string | null {
  const raw = clean(iso);
  if (!raw) return null;
  const hhmm = formatGlanceClock(raw);
  if (!hhmm || hhmm === "—") return null;
  return hhmm;
}

function degreeBit(deg: number | null | undefined): string | null {
  if (typeof deg !== "number" || !Number.isFinite(deg)) return null;
  return `${Math.round(deg)}°`;
}

function orbBit(orb: number | null | undefined): string | null {
  if (typeof orb !== "number" || !Number.isFinite(orb)) return null;
  if (orb < 0.5) return "0°";
  return `${orb.toFixed(1)}°`;
}

export function joinSkyMeta(parts: Array<string | null | undefined>): string | null {
  const ok = parts.map((p) => clean(p)).filter((p): p is string => Boolean(p));
  return ok.length ? ok.join(" · ") : null;
}

const SIGN_PREP: Record<string, string> = {
  Овен: "Овне",
  Телец: "Тельце",
  Близнецы: "Близнецах",
  Рак: "Раке",
  Лев: "Льве",
  Дева: "Деве",
  Весы: "Весах",
  Скорпион: "Скорпионе",
  Стрелец: "Стрельце",
  Козерог: "Козероге",
  Водолей: "Водолее",
  Рыбы: "Рыбах",
};

export function inSign(bodyRu: string | null | undefined, signRu: string | null | undefined): string | null {
  const body = clean(bodyRu);
  const sign = clean(signRu);
  if (!body || !sign) return null;
  const prep = SIGN_PREP[sign] || sign;
  const prefix = prep.startsWith("Льв") ? "во" : "в";
  return `${body} ${prefix} ${prep}`;
}

export function positionLabel(row: TodayContractSkyBodyV1): string {
  const base = inSign(row.body_ru, row.sign_ru) || row.body_ru;
  const deg = typeof row.degree === "number" && Number.isFinite(row.degree) ? ` ${Math.round(row.degree)}°` : "";
  const rx = row.retrograde ? " Rx" : "";
  return `${base}${deg}${rx}`.trim();
}

export function buildTodaySkyStripModel(
  contract: TodayContractV1 | null | undefined,
  personalLine?: string | null,
): TodaySkyStripModel | null {
  const nest = contract?.sky_today;
  if (!nest) return null;
  const moon = nest.moon ?? null;
  const moonLabel = moon ? inSign(moon.body_ru, moon.sign_ru) : null;
  const headline = nest.headline ?? null;
  const headlineLabel = headline
    ? clean(headline.title_ru) ||
      (() => {
        const left = inSign(headline.planet_a_ru, headline.sign_a_ru);
        const right = inSign(headline.planet_b_ru, headline.sign_b_ru);
        const aspect = clean(headline.aspect_ru);
        if (left && right && aspect) return `${left} — ${aspect} — ${right}`;
        return null;
      })()
    : null;
  if (!moonLabel && !headlineLabel) return null;
  const window = nest.window;
  const startClock = window?.starts_at ? clock(window.starts_at) : null;
  const endClock = window?.ends_at ? clock(window.ends_at) : null;
  const windowLabel = startClock && endClock ? `${startClock}–${endClock}` : startClock || endClock;
  return {
    moon,
    moonLabel,
    moonDegree: moon ? degreeBit(moon.degree) : null,
    moonWhen: moon ? clock(moon.exact_time_local) : null,
    headline,
    headlineLabel,
    headlineOrb: headline ? orbBit(headline.orb_delta) : null,
    headlineWhen: headline ? clock(headline.exact_time_local) : null,
    windowLabel,
    sharedStory: clean(headline?.story_ru),
    personalLine: clean(personalLine),
  };
}
