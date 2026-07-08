import type { CoreProfile } from "@/lib/types";

export type ProfileNumerologyCard = { key: string; label: string; value: string; hint?: string };

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
    out.push({ key: "lp", label: "Число пути", value: String(numerology.life_path), hint: `главный сценарий${m}`.trim() });
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
      hint: `для ${refYear}, по дате рождения`,
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
