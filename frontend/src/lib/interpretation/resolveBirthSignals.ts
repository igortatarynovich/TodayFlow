import type { GuestProfileDraft } from "@/lib/guestProfileDraft";
import { personalDayFromBirth, personalYearFromBirth } from "@/lib/numerology/personalCycleNumbers";
import { sunSignFromIsoDate } from "@/lib/sunSignFromDate";
import {
  getLifePathEntry,
  getSunInSignEntry,
  getZodiacEntry,
  resolveZodiacSignId,
  type LifePathEntry,
  type PlanetInSignEntry,
  type ZodiacKnowledgeEntry,
} from "@/lib/zodiacKnowledge";

export type BirthSignalContext = {
  birthDate: string;
  signId: string | null;
  sunEntry: PlanetInSignEntry | null;
  signEntry: ZodiacKnowledgeEntry | undefined;
  lpEntry: LifePathEntry | undefined;
  personalYear: number | null;
  personalDay: number | null;
};

export function resolveBirthSignals(
  draft: GuestProfileDraft,
  refDate: Date = new Date(),
): BirthSignalContext {
  const birthDate = draft.birth_date.trim();
  const sunSign = draft.sun_sign || sunSignFromIsoDate(birthDate);
  const signId = sunSign ? resolveZodiacSignId(sunSign, null) : null;

  return {
    birthDate,
    signId,
    sunEntry: signId ? getSunInSignEntry(signId) ?? null : null,
    signEntry: signId ? getZodiacEntry(signId) : undefined,
    lpEntry: getLifePathEntry(draft.life_path ?? undefined),
    personalYear: personalYearFromBirth(birthDate, refDate.getFullYear()),
    personalDay: personalDayFromBirth(birthDate, refDate),
  };
}
