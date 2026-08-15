/**
 * Shared-sky strip model — Moon in sign every day + one headline pair.
 * Facts only. No invent.
 */

import type {
  TodayContractSkyAspectV1,
  TodayContractSkyBodyV1,
  TodayContractSkyHeadlineV1,
  TodayContractV1,
} from "@/lib/todayContract";

export type TodaySkyStripModel = {
  moon: TodayContractSkyBodyV1;
  moonLabel: string;
  headline: TodayContractSkyHeadlineV1 | null;
  headlineLabel: string | null;
  positions: TodayContractSkyBodyV1[];
  aspects: TodayContractSkyAspectV1[];
};

function clean(s: string | null | undefined): string | null {
  const t = String(s || "").trim();
  return t ? t : null;
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
): TodaySkyStripModel | null {
  const nest = contract?.sky_today;
  if (!nest) return null;
  const moon = nest.moon;
  const moonLabel = moon ? inSign(moon.body_ru, moon.sign_ru) : null;
  if (!moon || !moonLabel) return null;
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
  return {
    moon,
    moonLabel,
    headline,
    headlineLabel,
    positions: Array.isArray(nest.positions) ? nest.positions : [],
    aspects: Array.isArray(nest.aspects) ? nest.aspects : [],
  };
}
