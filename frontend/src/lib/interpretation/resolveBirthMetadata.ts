import { chineseZodiacFromIsoDate } from "@/lib/chineseZodiacFromDate";
import type { GuestProfileDraft } from "@/lib/guestProfileDraft";
import { personalDayFromBirth, personalYearFromBirth } from "@/lib/numerology/personalCycleNumbers";
import { sunSignFromIsoDate } from "@/lib/sunSignFromDate";
import {
  elementNames,
  getElement,
  getModality,
  modalityNames,
  type Element,
  type Modality,
} from "@/lib/zodiac-utils";
import { getLifePathEntry, getZodiacEntry, resolveZodiacSignId } from "@/lib/zodiacKnowledge";
import { lifePathHeroCaption } from "@/lib/visualIdentity/lifePathTitles";

const WEEKDAY_RU = ["воскресенье", "понедельник", "вторник", "среда", "четверг", "пятница", "суббота"];

const SEASON_RU: Record<string, string> = {
  winter: "зима",
  spring: "весна",
  summer: "лето",
  autumn: "осень",
};

const RULER_RU: Record<string, string> = {
  Saturn: "Сатурн",
  Uranus: "Уран",
  Jupiter: "Юпитер",
  Mars: "Марс",
  Venus: "Венера",
  Mercury: "Меркурий",
  Moon: "Луна",
  Sun: "Солнце",
  Neptune: "Нептун",
  Pluto: "Плутон",
};

export type BirthMetadata = {
  sunSignRu: string | null;
  lifePath: number | null;
  elementRu: string | null;
  element: Element | null;
  modalityRu: string | null;
  modality: Modality | null;
  rulerRu: string | null;
  chineseAnimalRu: string | null;
  chineseElementRu: string | null;
  archetypeRu: string | null;
  personalYear: number | null;
  personalDay: number | null;
  birthWeekdayRu: string | null;
  birthSeasonRu: string | null;
};

function birthSeason(month: number): string {
  if (month === 12 || month <= 2) return SEASON_RU.winter;
  if (month <= 5) return SEASON_RU.spring;
  if (month <= 8) return SEASON_RU.summer;
  return SEASON_RU.autumn;
}

export function resolveBirthMetadata(draft: GuestProfileDraft, refDate = new Date()): BirthMetadata {
  const sunSign = draft.sun_sign || sunSignFromIsoDate(draft.birth_date);
  const signId = sunSign ? resolveZodiacSignId(sunSign, null) : null;
  const signEntry = signId ? getZodiacEntry(signId) : undefined;
  const element = sunSign ? getElement(sunSign) : null;
  const modality = sunSign ? getModality(sunSign) : null;
  const chinese = chineseZodiacFromIsoDate(draft.birth_date);

  const parts = draft.birth_date.match(/^(\d{4})-(\d{2})-(\d{2})/);
  const month = parts ? Number(parts[2]) : null;
  const day = parts ? Number(parts[3]) : null;
  const weekday =
    parts && month && day ? WEEKDAY_RU[new Date(Number(parts[1]), month - 1, day).getDay()] : null;

  const ruler = signEntry?.rulers?.[0];

  return {
    sunSignRu: signEntry?.ruName ?? null,
    lifePath: draft.life_path,
    elementRu: element ? elementNames[element] : null,
    element,
    modalityRu: modality ? modalityNames[modality] : null,
    modality,
    rulerRu: ruler ? RULER_RU[ruler] ?? ruler : null,
    chineseAnimalRu: chinese?.animalRu ?? null,
    chineseElementRu: chinese?.element ?? null,
    archetypeRu:
      draft.life_path != null ? lifePathHeroCaption(draft.life_path) : null,
    personalYear: personalYearFromBirth(draft.birth_date, refDate.getFullYear()),
    personalDay: personalDayFromBirth(draft.birth_date, refDate),
    birthWeekdayRu: weekday,
    birthSeasonRu: month ? birthSeason(month) : null,
  };
}

export function resolveDomainWhyContext(draft: GuestProfileDraft, refDate = new Date()) {
  const meta = resolveBirthMetadata(draft, refDate);
  const lpEntry = getLifePathEntry(draft.life_path ?? undefined);
  return { ...meta, lifePathEntry: lpEntry };
}

export type DomainWhyContext = ReturnType<typeof resolveDomainWhyContext>;
