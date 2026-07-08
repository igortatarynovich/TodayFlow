/** Client-side personal year / day — same rules as Profile numerology cards. */

function parseIsoMonthDay(iso: string | null | undefined): { month: number; day: number } | null {
  if (!iso || typeof iso !== "string") return null;
  const m = iso.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (!m) return null;
  const month = Number(m[2]);
  const day = Number(m[3]);
  if (!month || !day) return null;
  return { month, day };
}

export function digitalRoot1to9(n: number): number {
  let x = Math.abs(Math.trunc(n));
  while (x > 9) {
    x = String(x)
      .split("")
      .reduce((acc, d) => acc + Number(d), 0);
  }
  return x === 0 ? 1 : x;
}

export function personalYearFromBirth(
  birthDate: string | null | undefined,
  refYear: number = new Date().getFullYear(),
): number | null {
  const parts = parseIsoMonthDay(birthDate);
  if (!parts) return null;
  return digitalRoot1to9(parts.month + parts.day + refYear);
}

export function personalDayFromBirth(
  birthDate: string | null | undefined,
  refDate: Date = new Date(),
): number | null {
  const parts = parseIsoMonthDay(birthDate);
  if (!parts) return null;
  return digitalRoot1to9(parts.month + parts.day + refDate.getFullYear() + refDate.getMonth() + 1 + refDate.getDate());
}
