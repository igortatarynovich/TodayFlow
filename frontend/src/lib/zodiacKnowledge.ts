import ariesManual from "../../../CONTENT/horoscopes/signs/aries.json";
import aquariusManual from "../../../CONTENT/horoscopes/signs/aquarius.json";
import cancerManual from "../../../CONTENT/horoscopes/signs/cancer.json";
import capricornManual from "../../../CONTENT/horoscopes/signs/capricorn.json";
import geminiManual from "../../../CONTENT/horoscopes/signs/gemini.json";
import leoManual from "../../../CONTENT/horoscopes/signs/leo.json";
import libraManual from "../../../CONTENT/horoscopes/signs/libra.json";
import mercuryInSignsManual from "../../../CONTENT/horoscopes/planets/mercury_in_signs.json";
import marsInSignsManual from "../../../CONTENT/horoscopes/planets/mars_in_signs.json";
import jupiterInSignsManual from "../../../CONTENT/horoscopes/planets/jupiter_in_signs.json";
import moonInSignsManual from "../../../CONTENT/horoscopes/planets/moon_in_signs.json";
import nameNumbersManual from "../../../CONTENT/horoscopes/numerology/name_numbers.json";
import neptuneInSignsManual from "../../../CONTENT/horoscopes/planets/neptune_in_signs.json";
import piscesManual from "../../../CONTENT/horoscopes/signs/pisces.json";
import plutoInSignsManual from "../../../CONTENT/horoscopes/planets/pluto_in_signs.json";
import lifePathsManual from "../../../CONTENT/horoscopes/numerology/life_paths.json";
import profileScenariosManual from "../../../CONTENT/horoscopes/scenarios/profile_scenarios.json";
import risingSignsManual from "../../../CONTENT/horoscopes/planets/rising_signs.json";
import sagittariusManual from "../../../CONTENT/horoscopes/signs/sagittarius.json";
import saturnInSignsManual from "../../../CONTENT/horoscopes/planets/saturn_in_signs.json";
import scorpioManual from "../../../CONTENT/horoscopes/signs/scorpio.json";
import sunInSignsManual from "../../../CONTENT/horoscopes/planets/sun_in_signs.json";
import taurusManual from "../../../CONTENT/horoscopes/signs/taurus.json";
import uranusInSignsManual from "../../../CONTENT/horoscopes/planets/uranus_in_signs.json";
import venusInSignsManual from "../../../CONTENT/horoscopes/planets/venus_in_signs.json";
import virgoManual from "../../../CONTENT/horoscopes/signs/virgo.json";

export type ZodiacKnowledgeEntry = {
  id: string;
  name: string;
  ruName: string;
  dates: string;
  element: string;
  modality: string;
  rulers: string[];
  themes: string[];
  stones: string[];
  portrait: string;
  strengths: string[];
  watchouts: string[];
  love: string;
  work: string;
  money: string;
  friendship: string;
  family: string;
  communication: string;
  conflict: string;
  intimacy?: string;
  likes?: string[];
  dislikes?: string[];
  hurts?: string[];
  decisions?: string;
  plusSide?: string[];
  minusSide?: string[];
  compatibilityEasy?: string[];
  compatibilityHard?: string[];
  compatibilityNote?: string;
  formula?: string;
  attraction: string;
  growth: string;
  support: string;
  career?: string;
};

export type PlanetInSignEntry = {
  signId: string;
  title: string;
  ruTitle: string;
  bullets: string[];
};

export type ProfileScenarioEntry = {
  id: string;
  title: string;
  bullets: string[];
};

export type LifePathEntry = {
  number: number;
  title: string;
  essence: string;
  strengths: string[];
  watchouts: string[];
  growth: string;
  pattern: string;
  manifestation?: string[];
  driver?: string;
  relationships?: string[];
  money_work?: string[];
  plus_side?: string[];
  minus_side?: string[];
  main_fear?: string;
  lesson?: string;
  life_theme?: string;
  relationship_strengthens?: string;
  reading?: string[];
};

export type NameNumberEntry = {
  number: number;
  expression: string;
  soul_urge: string;
  personality: string;
};

export const ZODIAC_KNOWLEDGE: ZodiacKnowledgeEntry[] = [
  ariesManual as ZodiacKnowledgeEntry,
  taurusManual as ZodiacKnowledgeEntry,
  geminiManual as ZodiacKnowledgeEntry,
  cancerManual as ZodiacKnowledgeEntry,
  leoManual as ZodiacKnowledgeEntry,
  virgoManual as ZodiacKnowledgeEntry,
  libraManual as ZodiacKnowledgeEntry,
  scorpioManual as ZodiacKnowledgeEntry,
  sagittariusManual as ZodiacKnowledgeEntry,
  capricornManual as ZodiacKnowledgeEntry,
  aquariusManual as ZodiacKnowledgeEntry,
  piscesManual as ZodiacKnowledgeEntry,
];

export function getZodiacEntry(signId: string) {
  return ZODIAC_KNOWLEDGE.find((entry) => entry.id === signId);
}

export const SUN_IN_SIGN_KNOWLEDGE: PlanetInSignEntry[] = sunInSignsManual as PlanetInSignEntry[];
export const MERCURY_IN_SIGN_KNOWLEDGE: PlanetInSignEntry[] = mercuryInSignsManual as PlanetInSignEntry[];
export const JUPITER_IN_SIGN_KNOWLEDGE: PlanetInSignEntry[] = jupiterInSignsManual as PlanetInSignEntry[];
export const MARS_IN_SIGN_KNOWLEDGE: PlanetInSignEntry[] = marsInSignsManual as PlanetInSignEntry[];
export const MOON_IN_SIGN_KNOWLEDGE: PlanetInSignEntry[] = moonInSignsManual as PlanetInSignEntry[];
export const NEPTUNE_IN_SIGN_KNOWLEDGE: PlanetInSignEntry[] = neptuneInSignsManual as PlanetInSignEntry[];
export const PLUTO_IN_SIGN_KNOWLEDGE: PlanetInSignEntry[] = plutoInSignsManual as PlanetInSignEntry[];
export const RISING_SIGN_KNOWLEDGE: PlanetInSignEntry[] = risingSignsManual as PlanetInSignEntry[];
export const SATURN_IN_SIGN_KNOWLEDGE: PlanetInSignEntry[] = saturnInSignsManual as PlanetInSignEntry[];
export const URANUS_IN_SIGN_KNOWLEDGE: PlanetInSignEntry[] = uranusInSignsManual as PlanetInSignEntry[];
export const VENUS_IN_SIGN_KNOWLEDGE: PlanetInSignEntry[] = venusInSignsManual as PlanetInSignEntry[];
export const PROFILE_SCENARIOS: ProfileScenarioEntry[] = profileScenariosManual as ProfileScenarioEntry[];
export const LIFE_PATH_KNOWLEDGE: LifePathEntry[] = lifePathsManual as LifePathEntry[];
export const NAME_NUMBER_KNOWLEDGE: NameNumberEntry[] = nameNumbersManual as NameNumberEntry[];

export function getSunInSignEntry(signId: string) {
  return SUN_IN_SIGN_KNOWLEDGE.find((entry) => entry.signId === signId);
}

export function getMoonInSignEntry(signId: string) {
  return MOON_IN_SIGN_KNOWLEDGE.find((entry) => entry.signId === signId);
}

export function getMarsInSignEntry(signId: string) {
  return MARS_IN_SIGN_KNOWLEDGE.find((entry) => entry.signId === signId);
}

export function getJupiterInSignEntry(signId: string) {
  return JUPITER_IN_SIGN_KNOWLEDGE.find((entry) => entry.signId === signId);
}

export function getMercuryInSignEntry(signId: string) {
  return MERCURY_IN_SIGN_KNOWLEDGE.find((entry) => entry.signId === signId);
}

export function getNeptuneInSignEntry(signId: string) {
  return NEPTUNE_IN_SIGN_KNOWLEDGE.find((entry) => entry.signId === signId);
}

export function getPlutoInSignEntry(signId: string) {
  return PLUTO_IN_SIGN_KNOWLEDGE.find((entry) => entry.signId === signId);
}

export function getVenusInSignEntry(signId: string) {
  return VENUS_IN_SIGN_KNOWLEDGE.find((entry) => entry.signId === signId);
}

export function getRisingSignEntry(signId: string) {
  return RISING_SIGN_KNOWLEDGE.find((entry) => entry.signId === signId);
}

export function getSaturnInSignEntry(signId: string) {
  return SATURN_IN_SIGN_KNOWLEDGE.find((entry) => entry.signId === signId);
}

export function getUranusInSignEntry(signId: string) {
  return URANUS_IN_SIGN_KNOWLEDGE.find((entry) => entry.signId === signId);
}

export function normalizeSignId(value: string | null | undefined) {
  return String(value || "").trim().toLowerCase();
}

/**
 * Русское имя знака зодиака из подписи en («Scorpio») или ru («Скорпион»).
 * EN → берём ruName из справочника; RU или неизвестное → возвращаем как есть (без потери регистра).
 */
export function zodiacRuName(sign: string | null | undefined): string {
  if (!sign) return "";
  return getZodiacEntry(normalizeSignId(sign))?.ruName || sign;
}

const ELEMENT_RU: Record<string, string> = {
  fire: "огонь",
  earth: "земля",
  air: "воздух",
  water: "вода",
};

/** Русское имя стихии из en («earth») или ru («земля»); неизвестное — как есть. */
export function elementRuName(element: string | null | undefined): string {
  if (!element) return "";
  return ELEMENT_RU[element.trim().toLowerCase()] || element;
}

/** Порядок знаков для восстановления id по эклиптической долготе (0° = Овен). */
const ZODIAC_IDS_IN_ORDER = [
  "aries",
  "taurus",
  "gemini",
  "cancer",
  "leo",
  "virgo",
  "libra",
  "scorpio",
  "sagittarius",
  "capricorn",
  "aquarius",
  "pisces",
] as const;

/** Русские названия знаков из API/движка → канонический id (как в JSON планет в знаках). */
const RU_SIGN_TO_ID: Record<string, (typeof ZODIAC_IDS_IN_ORDER)[number]> = {
  овен: "aries",
  телец: "taurus",
  близнецы: "gemini",
  рак: "cancer",
  лев: "leo",
  дева: "virgo",
  весы: "libra",
  скорпион: "scorpio",
  стрелец: "sagittarius",
  козерог: "capricorn",
  водолей: "aquarius",
  рыбы: "pisces",
};

/**
 * Приводит подпись знака из карты (en/ru) к id aries..pisces; при отсутствии строки
 * использует долготу (как в ответе API после coalesce).
 */
export function resolveZodiacSignId(
  rawSign: string | null | undefined,
  longitude?: number | null,
): string {
  const trimmed = String(rawSign ?? "").trim();
  if (trimmed) {
    const lower = trimmed.toLowerCase();
    if (ZODIAC_KNOWLEDGE.some((z) => z.id === lower)) {
      return lower;
    }
    const fromRu = RU_SIGN_TO_ID[lower];
    if (fromRu) return fromRu;
  }
  if (longitude != null && !Number.isNaN(Number(longitude))) {
    const x = ((Number(longitude) % 360) + 360) % 360;
    const idx = Math.min(11, Math.floor(x / 30));
    return ZODIAC_IDS_IN_ORDER[idx];
  }
  return "";
}

/**
 * Эклиптическая долгота 0..360° по подписи знака (en/ru) и градусу в знаке.
 * Для визуализации колеса и куспидов, когда в payload нет готового longitude.
 */
export function eclipticLongitudeFromSignAndDegree(
  sign: string | null | undefined,
  degreeInSign: number | null | undefined,
): number | null {
  if (sign == null || String(sign).trim() === "") return null;
  if (degreeInSign == null || Number.isNaN(Number(degreeInSign))) return null;
  const id = resolveZodiacSignId(String(sign).trim(), null);
  if (!id) return null;
  const idx = ZODIAC_IDS_IN_ORDER.indexOf(id as (typeof ZODIAC_IDS_IN_ORDER)[number]);
  if (idx < 0) return null;
  const deg = ((Number(degreeInSign) % 30) + 30) % 30;
  return (idx * 30 + deg) % 360;
}

export function getProfileScenarioEntry(id: string) {
  return PROFILE_SCENARIOS.find((entry) => entry.id === id);
}

export function getLifePathEntry(number?: number | null) {
  if (!number) return undefined;
  return LIFE_PATH_KNOWLEDGE.find((entry) => entry.number === number);
}

export function getNameNumberEntry(number?: number | null) {
  if (!number) return undefined;
  return NAME_NUMBER_KNOWLEDGE.find((entry) => entry.number === number);
}
