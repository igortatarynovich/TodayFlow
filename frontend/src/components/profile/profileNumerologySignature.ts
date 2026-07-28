import { getLifePathEntry } from "@/lib/zodiacKnowledge";
import type { CoreProfile } from "@/lib/types";

export type ProfileNumerologyCard = { key: string; label: string; value: string; hint?: string };

const PERSONAL_YEAR_HINT: Record<number, string> = {
  1: "год запуска и своего первого шага",
  2: "год союза и тонкой настройки",
  3: "год голоса и контакта",
  4: "год фундамента и режима",
  5: "год свободы и смены",
  6: "год заботы и обязательств",
  7: "год смысла и ясной дистанции",
  8: "год силы и видимого результата",
  9: "год завершения циклов",
};

/** Те же числа, что на экране «Карта»: путь, имя, суть, подача, личный год. */
export function buildNumerologySignatureCards(
  numerology: CoreProfile["numerology"] | null | undefined,
  refYear: number = new Date().getFullYear(),
): ProfileNumerologyCard[] {
  if (!numerology) return [];
  const py = personalYearFromBirth(numerology.birth_date, refYear);
  const out: ProfileNumerologyCard[] = [];

  if (numerology.life_path != null) {
    const m = numerology.is_master_life_path ? " · мастер-линия" : "";
    const essence = getLifePathEntry(numerology.life_path)?.essence?.trim();
    out.push({
      key: "lp",
      label: "Число пути",
      value: String(numerology.life_path),
      hint: essence
        ? essence.length > 110
          ? `${essence.slice(0, 107)}…`
          : essence
        : `главный сценарий жизни${m}`.trim(),
    });
  }
  if (numerology.expression != null) {
    out.push({ key: "ex", label: "Имя", value: String(numerology.expression), hint: "как ты проживаешь полное имя" });
  }
  if (numerology.soul_urge != null) {
    out.push({ key: "su", label: "Суть", value: String(numerology.soul_urge), hint: "внутренняя мотивация" });
  }
  if (numerology.personality != null) {
    out.push({ key: "pe", label: "Подача", value: String(numerology.personality), hint: "как тебя чаще встречают снаружи" });
  }
  if (py != null) {
    out.push({
      key: "py",
      label: "Личный год",
      value: String(py),
      hint: PERSONAL_YEAR_HINT[py] || `тон цикла ${refYear} по дате рождения`,
    });
  }
  return out;
}

function personalYearFromBirth(birthDate: string | null | undefined, refYear: number): number | null {
  const parts = parseIsoMonthDay(birthDate);
  if (!parts) return null;
  const sum = parts.month + parts.day + refYear;
  return digitalRoot1to9(sum);
}

function parseIsoMonthDay(iso: string | null | undefined): { month: number; day: number } | null {
  if (!iso || typeof iso !== "string") return null;
  const m = iso.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (!m) return null;
  const month = Number(m[2]);
  const day = Number(m[3]);
  if (!month || !day) return null;
  return { month, day };
}

function digitalRoot1to9(n: number): number {
  let x = Math.abs(Math.trunc(n));
  while (x > 9) {
    x = String(x)
      .split("")
      .reduce((acc, d) => acc + Number(d), 0);
  }
  return x === 0 ? 1 : x;
}
