import type { ZodiacSign } from "@/lib/zodiac-utils";

/** Sun sign from ISO date — parity with iOS BirthProfileDraft.zodiacSign(for:). */
export function sunSignFromIsoDate(isoDate: string): ZodiacSign | null {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(isoDate.trim());
  if (!match) return null;
  const month = Number(match[2]);
  const day = Number(match[3]);
  if (!month || !day) return null;

  switch (true) {
    case (month === 3 && day >= 21) || (month === 4 && day < 20):
      return "Aries";
    case (month === 4 && day >= 20) || (month === 5 && day < 21):
      return "Taurus";
    case (month === 5 && day >= 21) || (month === 6 && day < 21):
      return "Gemini";
    case (month === 6 && day >= 21) || (month === 7 && day < 23):
      return "Cancer";
    case (month === 7 && day >= 23) || (month === 8 && day < 23):
      return "Leo";
    case (month === 8 && day >= 23) || (month === 9 && day < 23):
      return "Virgo";
    case (month === 9 && day >= 23) || (month === 10 && day < 23):
      return "Libra";
    case (month === 10 && day >= 23) || (month === 11 && day < 22):
      return "Scorpio";
    case (month === 11 && day >= 22) || (month === 12 && day < 22):
      return "Sagittarius";
    case (month === 12 && day >= 22) || (month === 1 && day < 20):
      return "Capricorn";
    case (month === 1 && day >= 20) || (month === 2 && day < 19):
      return "Aquarius";
    default:
      return "Pisces";
  }
}
